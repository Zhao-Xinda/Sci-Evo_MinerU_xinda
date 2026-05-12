#!/usr/bin/env python3
"""
Fill template variables in docs/technical_report.md using the most recent
data/traces/_quality_report.json. Keeps the template as a check-in artefact
and produces docs/technical_report.rendered.md for submission.

Usage:
    python src/render_report.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REPORT_TEMPLATE = ROOT / "docs" / "technical_report.md"
REPORT_OUT = ROOT / "docs" / "technical_report.rendered.md"
QUALITY_JSON = ROOT / "data" / "traces" / "_quality_report.json"
MANIFEST_JSONL = ROOT / "data" / "manifests" / "pilot.jsonl"


def main() -> int:
    if not QUALITY_JSON.exists():
        print(f"missing {QUALITY_JSON}; run analyze_quality.py first")
        return 1
    qr = json.loads(QUALITY_JSON.read_text())
    overall = qr["overall"]
    sv = qr.get("schema_validation", {})

    n_input = sum(1 for _ in MANIFEST_JSONL.open()) if MANIFEST_JSONL.exists() else overall["n_traces"]

    vars_ = {
        "DATE": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "YEAR": datetime.now(timezone.utc).strftime("%Y"),
        "INDEX_DATE": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "N_TRACES": overall["n_traces"],
        "N_PAPERS": overall["n_traces"],
        "N_INPUT_PAPERS": n_input,
        "AVG_STEPS": f"{overall['avg_steps']:.1f}",
        "MEDIAN_STEPS": int(overall["median_steps"]),
        "MAX_STEPS": overall["max_steps"],
        "TOTAL_FAILED": overall["total_failed_attempts"],
        "TOTAL_REV": overall["total_revisions"],
        "N_WITH_FAIL": overall["traces_with_failed_attempts"],
        "FRAC_FAILED_PCT": f"{overall['fraction_with_failed_attempts']*100:.0f}",
        "TARGET_SMILES_PCT": f"{overall['target_smiles_filled_rate']*100:.0f}",
        "SMILES_PARSEABLE_PCT": f"{overall['smiles_parseable_rate']*100:.0f}",
        "SMILES_TOTAL": overall["smiles_total"],
        "EVIDENCE_COV_PCT": f"{overall['evidence_coverage_avg']*100:.0f}",
        "CONVERGENT_PCT": f"{overall['convergent_traces'] / overall['n_traces'] * 100:.0f}"
        if overall["n_traces"]
        else "0",
        "SCHEMA_PASS": f"{sv.get('pass_rate', 0.0)*100:.0f}"
        if "pass_rate" in sv
        else "n/a",
    }

    template = REPORT_TEMPLATE.read_text()
    rendered = template
    for k, v in vars_.items():
        rendered = rendered.replace("{" + k + "}", str(v))

    REPORT_OUT.write_text(rendered)
    print(f"Wrote {REPORT_OUT}")
    print("Filled values:")
    for k, v in vars_.items():
        print(f"  {{{k}}} = {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
