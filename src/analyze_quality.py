#!/usr/bin/env python3
"""
Quality analysis over completed Sci-Evo traces.

Produces:
    - Overall metrics (counts, distributions, pass-rates).
    - Per-trace scoring (we want a "richness" + "data quality" composite).
    - Top-K traces selected for the technical-report samples (default 10),
      filtered to those that demonstrate the dataset's strengths:
        * complete failure-modes + revisions
        * non-trivial step count
        * target.smiles filled
        * high SMILES-parseable rate
        * Open Reaction Database cross-checkable named reactions
    - JSON Schema validation pass-rate (jsonschema, draft 2020-12).
    - A markdown report at data/traces/_quality_report.md.

Usage:
    python src/analyze_quality.py --traces-dir data/traces \\
        --schema schema/sci_evo_total_synthesis.schema.json --top-k 10
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


def _safe_get(d: dict, *path, default=None):
    cur: Any = d
    for k in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur is not None else default


def score_trace(t: dict) -> dict:
    """Return a per-trace quality scorecard dict."""
    steps = t.get("execution_trace") or []
    n_steps = len(steps)
    n_failed = sum(1 for s in steps if _safe_get(s, "outcome", "valid") is False)
    n_revisions = sum(1 for s in steps if s.get("action") == "revision")
    n_named = sum(1 for s in steps if _safe_get(s, "reaction", "named_reaction"))
    n_with_evidence = sum(
        1 for s in steps if _safe_get(s, "evidence", "text_span")
    )

    qc = t.get("_smiles_qc") or {}
    smi_total = qc.get("total", 0)
    smi_parseable = qc.get("parseable", 0)
    parseable_rate = (smi_parseable / smi_total) if smi_total else 0.0

    target = t.get("target") or {}
    has_target_smiles = bool(target.get("smiles"))
    target_class = target.get("natural_product_class") or ""

    rs = t.get("retrosynthetic_strategy") or {}
    n_disco = len(rs.get("key_disconnections") or [])
    is_convergent = bool(rs.get("is_convergent"))
    n_fragments = len(rs.get("fragments") or [])

    val = t.get("validation") or {}
    n_chars = len(val.get("characterization") or [])
    n_metrics = len(val.get("metrics") or {})

    # Composite score: more failed-attempts is GOOD (data is richer in
    # decision data when authors disclose what didn't work).
    score = (
        min(n_steps, 30) * 1.0       # cap step credit at 30 to avoid favoring run-ons
        + n_failed * 3.0             # failed attempts are the signal
        + n_revisions * 1.5
        + n_disco * 1.0
        + n_named * 0.5
        + (1.0 if has_target_smiles else 0.0) * 4.0
        + parseable_rate * 5.0
        + (1.0 if is_convergent else 0.0) * 1.0
        + n_fragments * 0.3
        + n_metrics * 0.5
    )

    return {
        "trace_id": t.get("trace_id"),
        "pmcid": _safe_get(t, "_provenance", "source", "pmcid"),
        "title": _safe_get(t, "_provenance", "source", "title", default=""),
        "journal": _safe_get(t, "_provenance", "source", "journal", default=""),
        "year": _safe_get(t, "_provenance", "source", "year", default=0),
        "target_name": target.get("name", ""),
        "target_class": target_class,
        "steps": n_steps,
        "failed_attempts": n_failed,
        "revisions": n_revisions,
        "named_reactions": n_named,
        "evidence_coverage": n_with_evidence / n_steps if n_steps else 0.0,
        "smiles_total": smi_total,
        "smiles_parseable": smi_parseable,
        "smiles_parseable_rate": parseable_rate,
        "has_target_smiles": has_target_smiles,
        "key_disconnections": n_disco,
        "is_convergent": is_convergent,
        "fragments": n_fragments,
        "characterization_methods": n_chars,
        "validation_metrics": n_metrics,
        "score": round(score, 2),
    }


def validate_schema(traces: list[tuple[Path, dict]], schema_path: Path) -> dict:
    """Use jsonschema to validate; return summary + per-trace errors."""
    try:
        import jsonschema
    except ImportError:
        return {"error": "jsonschema not installed; run `pip install jsonschema`"}

    schema = json.loads(schema_path.read_text())
    validator = jsonschema.Draft202012Validator(schema)
    n_pass = 0
    error_examples: list[dict] = []
    for path, t in traces:
        errors = list(validator.iter_errors(t))
        if not errors:
            n_pass += 1
        elif len(error_examples) < 10:
            error_examples.append(
                {
                    "trace": path.name,
                    "n_errors": len(errors),
                    "first_errors": [
                        {
                            "path": list(e.absolute_path),
                            "message": e.message[:200],
                        }
                        for e in errors[:3]
                    ],
                }
            )
    return {
        "n_total": len(traces),
        "n_pass": n_pass,
        "n_fail": len(traces) - n_pass,
        "pass_rate": n_pass / len(traces) if traces else 0.0,
        "error_examples": error_examples,
    }


def render_markdown(
    overall: dict,
    schema_report: dict,
    cards: list[dict],
    top: list[dict],
) -> str:
    md = []
    md.append("# Sci-Evo Total-Synthesis Pilot — Quality Report\n")
    md.append("## Overall metrics\n")
    md.append("| metric | value |")
    md.append("|---|---|")
    for k, v in overall.items():
        if isinstance(v, float):
            md.append(f"| {k} | {v:.3f} |")
        else:
            md.append(f"| {k} | {v} |")
    md.append("")

    md.append("## JSON Schema validation (Draft 2020-12)\n")
    if "error" in schema_report:
        md.append(f"_skipped_: {schema_report['error']}\n")
    else:
        md.append(
            f"- pass: **{schema_report['n_pass']}/{schema_report['n_total']}** "
            f"({schema_report['pass_rate']*100:.1f}%)"
        )
        md.append(f"- fail: {schema_report['n_fail']}\n")
        if schema_report.get("error_examples"):
            md.append("First failures:\n")
            for ex in schema_report["error_examples"][:5]:
                md.append(f"- `{ex['trace']}` ({ex['n_errors']} errors)")
                for e in ex["first_errors"]:
                    md.append(
                        f"    - `{'/'.join(str(p) for p in e['path'])}`: {e['message']}"
                    )
        md.append("")

    md.append("## Top traces selected for technical report\n")
    md.append("| rank | trace | target | journal/year | steps | failed | rev | parseable | score |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for i, c in enumerate(top, 1):
        target = (c["target_name"] or "?")[:42]
        journal = f"{c['journal']} {c['year']}".strip()
        md.append(
            f"| {i} | `{c['trace_id']}` | {target} | {journal} | "
            f"{c['steps']} | {c['failed_attempts']} | {c['revisions']} | "
            f"{c['smiles_parseable_rate']:.2f} | {c['score']} |"
        )
    md.append("")

    md.append("## Distributions\n")
    step_dist = Counter(c["steps"] for c in cards)
    md.append("### Steps per trace\n")
    md.append("| steps | count |")
    md.append("|---|---|")
    for s in sorted(step_dist):
        md.append(f"| {s} | {step_dist[s]} |")
    md.append("")

    fail_dist = Counter(c["failed_attempts"] for c in cards)
    md.append("### Failed attempts per trace\n")
    md.append("| failed_attempts | count |")
    md.append("|---|---|")
    for s in sorted(fail_dist):
        md.append(f"| {s} | {fail_dist[s]} |")
    md.append("")

    cls_dist = Counter(c["target_class"] or "(unspecified)" for c in cards)
    md.append("### Natural-product class distribution\n")
    md.append("| class | count |")
    md.append("|---|---|")
    for k, v in cls_dist.most_common():
        md.append(f"| {k} | {v} |")
    md.append("")

    return "\n".join(md)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces-dir", default="data/traces")
    ap.add_argument(
        "--schema",
        default="schema/sci_evo_total_synthesis.schema.json",
    )
    ap.add_argument("--top-k", type=int, default=10)
    ap.add_argument(
        "--output-md",
        default="data/traces/_quality_report.md",
    )
    ap.add_argument(
        "--output-json",
        default="data/traces/_quality_report.json",
    )
    args = ap.parse_args()

    paths = sorted(Path(args.traces_dir).glob("*.trace.json"))
    if not paths:
        print(f"no traces in {args.traces_dir}")
        return 1

    cards: list[dict] = []
    loaded: list[tuple[Path, dict]] = []
    for p in paths:
        try:
            t = json.loads(p.read_text())
        except Exception as e:
            print(f"  load err {p.name}: {e}")
            continue
        loaded.append((p, t))
        cards.append(score_trace(t))

    n = len(cards)
    overall = {
        "n_traces": n,
        "avg_steps": statistics.mean(c["steps"] for c in cards) if n else 0.0,
        "median_steps": statistics.median(c["steps"] for c in cards) if n else 0.0,
        "max_steps": max(c["steps"] for c in cards) if n else 0,
        "total_failed_attempts": sum(c["failed_attempts"] for c in cards),
        "traces_with_failed_attempts": sum(1 for c in cards if c["failed_attempts"] > 0),
        "fraction_with_failed_attempts": (
            sum(1 for c in cards if c["failed_attempts"] > 0) / n if n else 0.0
        ),
        "total_revisions": sum(c["revisions"] for c in cards),
        "target_smiles_filled_rate": (
            sum(1 for c in cards if c["has_target_smiles"]) / n if n else 0.0
        ),
        "smiles_total": sum(c["smiles_total"] for c in cards),
        "smiles_parseable": sum(c["smiles_parseable"] for c in cards),
        "smiles_parseable_rate": (
            sum(c["smiles_parseable"] for c in cards)
            / sum(c["smiles_total"] for c in cards)
            if sum(c["smiles_total"] for c in cards)
            else 0.0
        ),
        "convergent_traces": sum(1 for c in cards if c["is_convergent"]),
        "evidence_coverage_avg": (
            statistics.mean(c["evidence_coverage"] for c in cards) if n else 0.0
        ),
    }

    schema_report = validate_schema(loaded, Path(args.schema))

    cards.sort(key=lambda c: c["score"], reverse=True)
    top = cards[: args.top_k]

    payload = {"overall": overall, "schema_validation": schema_report,
               "top_k": top, "all_cards": cards}
    Path(args.output_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    Path(args.output_md).write_text(render_markdown(overall, schema_report, cards, top))

    print("=== Overall ===")
    for k, v in overall.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.3f}")
        else:
            print(f"  {k}: {v}")
    if "error" not in schema_report:
        print(f"\n=== Schema validation === pass {schema_report['n_pass']}/{schema_report['n_total']} ({schema_report['pass_rate']*100:.1f}%)")
    print(f"\n=== Top {args.top_k} traces ===")
    for i, c in enumerate(top, 1):
        print(
            f"  {i:>2}. [{c['score']:>5.1f}] {c['trace_id']:>20} "
            f"{c['target_name'][:35]:<35}  steps={c['steps']:>2} "
            f"failed={c['failed_attempts']:>2} rev={c['revisions']:>2} "
            f"parseable={c['smiles_parseable_rate']:.2f}"
        )
    print(f"\nSaved {args.output_md}")
    print(f"Saved {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
