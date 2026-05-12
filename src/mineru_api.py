#!/usr/bin/env python3
"""
MinerU cloud API client — local-file batch upload + result polling.

Flow (per readme.txt 159-207):
    1) POST /api/v4/file-urls/batch  -> presigned upload URLs + batch_id
    2) PUT each PDF to its presigned URL  (no Content-Type header)
    3) System auto-submits parse tasks once upload is detected
    4) Poll GET /api/v4/extract-results/batch/{batch_id} for results

Usage:
    python src/mineru_api.py --pdf path/to/file.pdf
    python src/mineru_api.py --pdf-dir data/pdfs/raw --limit 50

Environment:
    MINERU_TOKEN must be set, or pass --token.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

API_BASE = "https://mineru.net/api/v4"
APPLY_URL = f"{API_BASE}/file-urls/batch"
RESULT_URL_TPL = f"{API_BASE}/extract-results/batch/{{batch_id}}"


def apply_upload_urls(
    token: str, files: list[dict], model_version: str = "vlm",
    *, max_retries: int = 6,
) -> dict:
    """POST file metadata, get presigned upload URLs + batch_id.

    Handles 429 (rate-limit) with exponential backoff, since the apply endpoint
    has a per-minute rate limit even though there's no published number.
    """
    last_err: Exception | None = None
    for attempt in range(max_retries):
        r = requests.post(
            APPLY_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json={"files": files, "model_version": model_version},
            timeout=60,
        )
        if r.status_code == 429:
            wait = 30 * (attempt + 1)
            print(f"  apply_upload_urls 429 — backing off {wait}s (attempt {attempt+1}/{max_retries})", flush=True)
            time.sleep(wait)
            last_err = RuntimeError(f"429 Too Many Requests")
            continue
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            last_err = e
            time.sleep(5 * (attempt + 1))
            continue
        body = r.json()
        if body.get("code") != 0:
            raise RuntimeError(f"apply upload urls failed: {body}")
        return body["data"]
    raise RuntimeError(f"apply_upload_urls exhausted retries: {last_err}")


def upload_one(
    presigned_url: str,
    local_path: Path,
    *,
    max_retries: int = 5,
    use_proxy: bool = False,
) -> bool:
    """PUT bytes to presigned URL — no Content-Type header per docs.

    Defaults to bypassing HTTP(S) proxies because the dev proxy occasionally
    closes connections to Aliyun OSS mid-upload (the presigned host).
    """
    proxies = None if not use_proxy else None  # None == use env proxies
    if not use_proxy:
        proxies = {"http": "", "https": ""}  # bypass env proxies
    last_err = None
    for attempt in range(max_retries):
        try:
            with local_path.open("rb") as f:
                r = requests.put(
                    presigned_url, data=f, timeout=300, proxies=proxies
                )
            if r.status_code == 200:
                return True
            last_err = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            last_err = f"{type(e).__name__}: {e}"
        time.sleep(2 * (attempt + 1))
    print(f"  upload {local_path.name} FAIL after {max_retries} retries: {last_err}", flush=True)
    return False


def fetch_batch_results(token: str, batch_id: str) -> dict:
    """GET parse results for a batch_id."""
    r = requests.get(
        RESULT_URL_TPL.format(batch_id=batch_id),
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def poll_until_done(
    token: str, batch_id: str, *, interval_s: int = 10, max_wait_s: int = 1800
) -> dict:
    """Poll batch_id until all files reach done/failed state, or timeout."""
    t0 = time.time()
    while True:
        body = fetch_batch_results(token, batch_id)
        if body.get("code") != 0:
            raise RuntimeError(f"fetch results failed: {body}")
        extract_results = (body.get("data") or {}).get("extract_result") or []
        states = [r.get("state") for r in extract_results]
        n_done = sum(1 for s in states if s in ("done", "failed"))
        elapsed = int(time.time() - t0)
        print(
            f"  [{elapsed:4d}s] states: "
            f"{ {s: states.count(s) for s in set(states)} }",
            flush=True,
        )
        if extract_results and n_done == len(extract_results):
            return body
        if time.time() - t0 > max_wait_s:
            raise TimeoutError(f"batch {batch_id} did not finish in {max_wait_s}s")
        time.sleep(interval_s)


def parse_one_pdf(token: str, pdf_path: Path, model_version: str = "vlm") -> dict:
    """Convenience: full single-file flow → returns final result dict."""
    print(f"[1/4] Apply upload URL for {pdf_path.name}")
    apply = apply_upload_urls(
        token, [{"name": pdf_path.name, "data_id": pdf_path.stem}], model_version
    )
    batch_id = apply["batch_id"]
    urls = apply["file_urls"]
    print(f"  batch_id={batch_id}")

    print(f"[2/4] PUT {pdf_path} -> presigned URL")
    ok = upload_one(urls[0], pdf_path)
    if not ok:
        raise RuntimeError("upload failed")
    print("  upload OK")

    print(f"[3/4] Poll batch {batch_id} for parse completion")
    final = poll_until_done(token, batch_id)

    print(f"[4/4] Done")
    return final


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", help="Single PDF path")
    ap.add_argument("--pdf-dir", help="Directory of PDFs")
    ap.add_argument("--pdf-list", help="File listing one PDF path per line")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--token", default=os.environ.get("MINERU_TOKEN"))
    ap.add_argument("--model-version", default="vlm")
    ap.add_argument("--out", default="data/mineru_out/raw_results")
    args = ap.parse_args()

    if not args.token:
        print("ERROR: --token or MINERU_TOKEN env required", file=sys.stderr)
        return 2
    if not args.pdf and not args.pdf_dir and not args.pdf_list:
        print("ERROR: --pdf, --pdf-dir, or --pdf-list required", file=sys.stderr)
        return 2

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.pdf:
        pdf_path = Path(args.pdf)
        result = parse_one_pdf(args.token, pdf_path, args.model_version)
        out_file = out_dir / f"{pdf_path.stem}.result.json"
        out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"\nSaved: {out_file}")
        # Print compact summary
        for r in (result.get("data") or {}).get("extract_result", []):
            print(f"  state={r.get('state')} url={r.get('full_zip_url') or r.get('err_msg')}")
        return 0

    if args.pdf_list:
        with open(args.pdf_list) as f:
            pdfs = [Path(line.strip()) for line in f if line.strip()]
        pdfs = pdfs[: args.limit]
        if not pdfs:
            print(f"no PDFs listed in {args.pdf_list}", file=sys.stderr)
            return 1
    else:
        pdfs = sorted(Path(args.pdf_dir).glob("*.pdf"))[: args.limit]
        if not pdfs:
            print(f"no PDFs in {args.pdf_dir}", file=sys.stderr)
            return 1
    print(f"Submitting {len(pdfs)} PDFs in batches of 50 (API limit)")
    BATCH = 50
    all_results = []
    for i in range(0, len(pdfs), BATCH):
        chunk = pdfs[i : i + BATCH]
        files_meta = [{"name": p.name, "data_id": p.stem} for p in chunk]
        apply = apply_upload_urls(args.token, files_meta, args.model_version)
        batch_id = apply["batch_id"]
        urls = apply["file_urls"]
        for j, (p, u) in enumerate(zip(chunk, urls), 1):
            ok = upload_one(u, p)
            print(f"  [{j}/{len(chunk)}] upload {p.name}: {'OK' if ok else 'FAIL'}", flush=True)
        final = poll_until_done(args.token, batch_id, max_wait_s=3600)
        out_file = out_dir / f"batch_{batch_id}.json"
        out_file.write_text(json.dumps(final, ensure_ascii=False, indent=2))
        all_results.append({"batch_id": batch_id, "file": str(out_file)})
    print(f"\nDone. {len(all_results)} batches saved to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
