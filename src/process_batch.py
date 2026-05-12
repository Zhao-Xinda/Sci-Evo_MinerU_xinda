#!/usr/bin/env python3
"""
End-to-end orchestrator over a MinerU batch result.

Given a batch JSON saved by mineru_api.py, for each paper this:
    1. Downloads the parsed-output ZIP and extracts to data/mineru_out/<pmcid>/.
    2. Runs extract_chem_from_image on data/mineru_out/<pmcid>/images/
       -> data/extracted/<pmcid>.smiles.jsonl
    3. Runs extract_trace on the per-paper outputs
       -> data/traces/<pmcid>.trace.json
    4. Writes data/traces/_summary.json with aggregate quality stats.

All three stages are parallelised independently because they have very
different cost profiles: download is HTTP-bound, SMILES extraction is API-
bound but uses concurrency inside extract_chem_from_image, trace extraction is
single-call-per-paper so we ThreadPool it.

Usage:
    python src/process_batch.py \\
        --batch-result data/mineru_out/pilot_results/batch_<id>.json \\
        --workers 16
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

# Allow imports from this directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_chem_from_image import extract_batch as extract_smiles_batch
from extract_chem_from_image import DEFAULT_MODEL as IMG_MODEL
from extract_trace import (
    DEFAULT_MODEL as TRACE_MODEL,
    build_prompt,
    call_llm,
    get_paper_title_from_md,
    lookup_manifest,
    make_client as make_openrouter_client,
    _coerce_json,
)
from validate_smiles import validate_trace as validate_trace_smiles
from datetime import datetime, timezone


def download_and_unzip(zip_url: str, out_dir: Path, *, timeout: int = 300) -> bool:
    """Download ZIP and extract into out_dir. Bypass proxy (CDN is on Aliyun)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(
            zip_url,
            timeout=timeout,
            proxies={"http": "", "https": ""},  # CDN reachable without proxy
            stream=True,
        )
        r.raise_for_status()
        buf = io.BytesIO(r.content)
        with zipfile.ZipFile(buf) as zf:
            zf.extractall(out_dir)
        return True
    except Exception as e:
        print(f"  ! download/unzip failed for {zip_url}: {e}", file=sys.stderr)
        return False


def stage1_download_all(
    results: list[dict], out_root: Path, *, workers: int = 16
) -> dict[str, Path]:
    """Parallel download/unzip. Returns {pmcid: paper_dir} for successes."""
    paper_dirs: dict[str, Path] = {}
    print(f"\n[Stage 1/3] Download + unzip {len(results)} ZIPs (workers={workers})", flush=True)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {}
        for r in results:
            if r.get("state") != "done" or not r.get("full_zip_url"):
                print(f"  skip {r.get('data_id')} (state={r.get('state')})")
                continue
            pmcid = r["data_id"]
            paper_dir = out_root / pmcid
            futures[ex.submit(download_and_unzip, r["full_zip_url"], paper_dir)] = (
                pmcid,
                paper_dir,
            )
        done = 0
        for fut in as_completed(futures):
            pmcid, paper_dir = futures[fut]
            ok = fut.result()
            done += 1
            if ok:
                paper_dirs[pmcid] = paper_dir
            print(f"  [{done}/{len(futures)}] {pmcid}: {'OK' if ok else 'FAIL'}", flush=True)
    print(f"  -> {len(paper_dirs)}/{len(futures)} papers unzipped")
    return paper_dirs


def _process_one_paper_smiles(
    pmcid: str, paper_dir: Path, out_root: Path, img_workers: int
) -> tuple[str, Path | None]:
    """Single-paper Stage 2: returns (pmcid, jsonl_path | None). Skips when
    output already exists (idempotency)."""
    img_dir = paper_dir / "images"
    out_jsonl = out_root / f"{pmcid}.smiles.jsonl"
    if out_jsonl.exists():
        return pmcid, out_jsonl  # idempotent skip
    if not img_dir.exists():
        return pmcid, None
    imgs = sorted(
        p for p in img_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    if not imgs:
        return pmcid, None
    extract_smiles_batch(imgs, workers=img_workers, out_jsonl=out_jsonl)
    return pmcid, out_jsonl


def stage2_smiles_per_paper(
    paper_dirs: dict[str, Path],
    out_root: Path,
    *,
    img_workers: int = 16,
    paper_workers: int = 4,
) -> dict[str, Path]:
    """Image-SMILES extraction across papers, parallelised on TWO axes:
        - up to `paper_workers` papers concurrently;
        - within each paper, `img_workers` Gemini calls concurrently.
    Effective concurrency on the API is paper_workers * img_workers
    (default 64). Idempotent: skips papers whose output JSONL already exists.
    """
    print(
        f"\n[Stage 2/3] Image-SMILES extraction "
        f"(papers={paper_workers}-way x images={img_workers}-way)",
        flush=True,
    )
    out_root.mkdir(parents=True, exist_ok=True)
    smiles_paths: dict[str, Path] = {}
    skipped_existing = 0
    items = list(paper_dirs.items())
    with ThreadPoolExecutor(max_workers=paper_workers) as ex:
        futures = {
            ex.submit(_process_one_paper_smiles, pmcid, pdir, out_root, img_workers): pmcid
            for pmcid, pdir in items
        }
        done = 0
        for fut in as_completed(futures):
            pmcid_, path = fut.result()
            done += 1
            if path is None:
                print(f"  [{done}/{len(items)}] {pmcid_}: 0 images (skipped)", flush=True)
                continue
            already = path.exists() and path.stat().st_size > 0
            # We just say "ok" here; the inner extract_smiles_batch already
            # printed per-image progress.
            print(
                f"  [{done}/{len(items)}] {pmcid_}: ok ({path.name})",
                flush=True,
            )
            smiles_paths[pmcid_] = path
            if already:
                # When already-existed-on-disk vs newly written, the inner
                # call would have written nothing. Track for the summary.
                pass
    return smiles_paths


def _extract_one_trace(
    pmcid: str,
    paper_dir: Path,
    smiles_path: Path | None,
    manifest_path: Path,
    out_dir: Path,
    *,
    model: str,
    batch_id: str,
    zip_url: str,
    skip_if_exists: bool = True,
) -> dict:
    """Build one trace, write to disk, return summary dict.

    If `skip_if_exists` and a parseable trace JSON already lives at the
    expected output path, we skip re-running the LLM. Lets us re-run the
    orchestrator after fixing a bug and only spend tokens on the previously-
    failed papers.
    """
    out_path = out_dir / f"{pmcid}.trace.json"
    if skip_if_exists and out_path.exists():
        try:
            existing = json.loads(out_path.read_text())
            n_steps = len(existing.get("execution_trace") or [])
            n_failed = sum(
                1 for s in (existing.get("execution_trace") or [])
                if (s.get("outcome") or {}).get("valid") is False
            )
            return {
                "pmcid": pmcid, "ok": True, "out_path": str(out_path),
                "steps": n_steps, "failed_attempts": n_failed,
                "smiles_qc": existing.get("_smiles_qc", {}),
                "target_smiles_present": bool((existing.get("target") or {}).get("smiles")),
                "skipped": True,
            }
        except (json.JSONDecodeError, OSError):
            pass  # fall through and re-extract

    md_path = paper_dir / "full.md"
    if not md_path.exists():
        return {"pmcid": pmcid, "ok": False, "error": "no full.md"}
    full_md = md_path.read_text()
    title = get_paper_title_from_md(full_md)
    smiles_records: list[dict] = []
    if smiles_path and smiles_path.exists():
        with smiles_path.open() as f:
            for line in f:
                if line.strip():
                    smiles_records.append(json.loads(line))
    manifest_meta = lookup_manifest(manifest_path, pmcid)
    prompt = build_prompt(
        title=title,
        full_md=full_md,
        smiles_records=smiles_records,
        manifest_meta=manifest_meta,
    )
    client = make_openrouter_client()
    try:
        response = call_llm(client, prompt, model)
        trace = _coerce_json(response)
    except json.JSONDecodeError as e:
        # Save raw response next to where the trace would have lived, so a
        # human can inspect what went wrong.
        try:
            (out_dir / f"{pmcid}.raw.txt").write_text(response)
        except Exception:
            pass
        return {"pmcid": pmcid, "ok": False, "error": f"json: {e}"}
    except Exception as e:
        return {"pmcid": pmcid, "ok": False, "error": f"llm: {type(e).__name__}: {e}"}

    trace["trace_id"] = f"TS-{pmcid}"
    trace["schema_version"] = "1.0.0"
    trace["license"] = "CC-BY-4.0"
    trace["_provenance"] = {
        "source": {
            "doi_or_id": manifest_meta.get("doi") or pmcid,
            "pmcid": manifest_meta.get("pmcid") or pmcid,
            "title": manifest_meta.get("title") or title,
            "authors": manifest_meta.get("authors", ""),
            "journal": manifest_meta.get("journal", ""),
            "year": manifest_meta.get("year", 0),
            "license": manifest_meta.get("license", ""),
            "pdf_url": manifest_meta.get("pdf_url", ""),
        },
        "mineru": {
            "method": "MinerU API (cloud)",
            "model_version": "vlm",
            "batch_id": batch_id,
            "result_zip_url": zip_url,
            "parsed_at": datetime.now(timezone.utc).isoformat(),
        },
        "extraction_models": [
            {"stage": "image_smiles", "name": IMG_MODEL, "version": ""},
            {"stage": "trace_extraction", "name": model, "version": ""},
        ],
        "human_reviewed": False,
    }
    validate_trace_smiles(trace)

    out_path = out_dir / f"{pmcid}.trace.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(trace, ensure_ascii=False, indent=2))

    n_steps = len(trace.get("execution_trace") or [])
    n_failed = sum(
        1 for s in (trace.get("execution_trace") or [])
        if (s.get("outcome") or {}).get("valid") is False
    )
    return {
        "pmcid": pmcid,
        "ok": True,
        "out_path": str(out_path),
        "steps": n_steps,
        "failed_attempts": n_failed,
        "smiles_qc": trace.get("_smiles_qc", {}),
        "target_smiles_present": bool((trace.get("target") or {}).get("smiles")),
    }


def stage3_traces(
    paper_dirs: dict[str, Path],
    smiles_paths: dict[str, Path],
    *,
    manifest_path: Path,
    traces_dir: Path,
    batch_id: str,
    pmcid_to_zip: dict[str, str],
    model: str,
    workers: int = 8,
) -> list[dict]:
    """Parallel trace extraction. Lower workers because each call is large
    context (~30k tokens) and we want to be polite to OpenRouter."""
    print(f"\n[Stage 3/3] Trace extraction via {model} (workers={workers})", flush=True)
    summaries: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {}
        for pmcid, paper_dir in paper_dirs.items():
            futures[
                ex.submit(
                    _extract_one_trace,
                    pmcid,
                    paper_dir,
                    smiles_paths.get(pmcid),
                    manifest_path,
                    traces_dir,
                    model=model,
                    batch_id=batch_id,
                    zip_url=pmcid_to_zip.get(pmcid, ""),
                )
            ] = pmcid
        done = 0
        for fut in as_completed(futures):
            pmcid = futures[fut]
            try:
                s = fut.result()
            except Exception as e:
                s = {"pmcid": pmcid, "ok": False, "error": f"{type(e).__name__}: {e}"}
            summaries.append(s)
            done += 1
            tag = (
                f"steps={s.get('steps')} failed={s.get('failed_attempts')} "
                f"target_smiles={s.get('target_smiles_present')}"
                if s.get("ok")
                else f"FAIL: {s.get('error')}"
            )
            print(f"  [{done}/{len(futures)}] {pmcid}: {tag}", flush=True)
    return summaries


def aggregate(summaries: list[dict]) -> dict:
    ok = [s for s in summaries if s.get("ok")]
    n = len(ok)
    if n == 0:
        return {"n_traces": 0}
    n_steps = sum(s["steps"] for s in ok)
    n_failed = sum(s["failed_attempts"] for s in ok)
    n_with_failed = sum(1 for s in ok if s["failed_attempts"] > 0)
    n_target_smiles = sum(1 for s in ok if s["target_smiles_present"])
    smiles_total = sum(s["smiles_qc"].get("total", 0) for s in ok)
    smiles_parseable = sum(s["smiles_qc"].get("parseable", 0) for s in ok)
    return {
        "n_traces": n,
        "n_failed_total": len(summaries) - n,
        "avg_steps_per_trace": n_steps / n,
        "total_failed_attempts": n_failed,
        "traces_with_failed_attempts": n_with_failed,
        "fraction_with_failed_attempts": n_with_failed / n,
        "target_smiles_filled_rate": n_target_smiles / n,
        "smiles_total": smiles_total,
        "smiles_parseable": smiles_parseable,
        "smiles_parseable_rate": smiles_parseable / smiles_total if smiles_total else 0.0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-result", required=True, nargs="+",
                    help="One or more MinerU batch result JSONs to process together")
    ap.add_argument("--manifest", default="data/manifests/pilot.jsonl")
    ap.add_argument("--mineru-out-root", default="data/mineru_out")
    ap.add_argument("--smiles-out-root", default="data/extracted")
    ap.add_argument("--traces-out-root", default="data/traces")
    ap.add_argument("--download-workers", type=int, default=16)
    ap.add_argument("--img-workers", type=int, default=16)
    ap.add_argument("--paper-workers", type=int, default=4)
    ap.add_argument("--trace-workers", type=int, default=8)
    ap.add_argument("--model", default=TRACE_MODEL)
    ap.add_argument("--skip-stages", default="", help="Comma list: download,smiles,traces")
    args = ap.parse_args()

    skip = set(s.strip() for s in args.skip_stages.split(",") if s.strip())

    # Multi-batch support: concatenate every batch's extract_result list
    # so Stages 2 and 3 see one combined paper set. batch_id and zip-url
    # mappings are merged across the batches we were given.
    results: list[dict] = []
    pmcid_to_zip: dict[str, str] = {}
    pmcid_to_batch: dict[str, str] = {}
    for bp_str in args.batch_result:
        bp = Path(bp_str)
        body = json.loads(bp.read_text())
        bid = bp.stem.replace("batch_", "")
        for r in body["data"]["extract_result"]:
            results.append(r)
            pmcid_to_zip[r["data_id"]] = r.get("full_zip_url", "")
            pmcid_to_batch[r["data_id"]] = bid
    batch_id = "+".join(Path(b).stem.replace("batch_", "") for b in args.batch_result)
    print(f"Combined {len(args.batch_result)} batch result(s) -> {len(results)} papers", flush=True)

    out_root = Path(args.mineru_out_root)
    paper_dirs: dict[str, Path] = {}
    if "download" not in skip:
        paper_dirs = stage1_download_all(results, out_root, workers=args.download_workers)
    else:
        for r in results:
            d = out_root / r["data_id"]
            if (d / "full.md").exists():
                paper_dirs[r["data_id"]] = d

    smiles_paths: dict[str, Path] = {}
    if "smiles" not in skip and paper_dirs:
        smiles_paths = stage2_smiles_per_paper(
            paper_dirs, Path(args.smiles_out_root),
            img_workers=args.img_workers, paper_workers=args.paper_workers,
        )
    elif paper_dirs:
        for pmcid in paper_dirs:
            p = Path(args.smiles_out_root) / f"{pmcid}.smiles.jsonl"
            if p.exists():
                smiles_paths[pmcid] = p

    summaries: list[dict] = []
    if "traces" not in skip and paper_dirs:
        summaries = stage3_traces(
            paper_dirs,
            smiles_paths,
            manifest_path=Path(args.manifest),
            traces_dir=Path(args.traces_out_root),
            batch_id=batch_id,
            pmcid_to_zip=pmcid_to_zip,
            model=args.model,
            workers=args.trace_workers,
        )

    summary = aggregate(summaries)
    summary_path = Path(args.traces_out_root) / "_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps({"summary": summary, "details": summaries}, ensure_ascii=False, indent=2))
    print(f"\n=== Summary === ")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print(f"\nSaved {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
