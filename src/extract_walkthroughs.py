#!/usr/bin/env python3
"""
For each of the top-K traces in `_quality_report.json`, emit a one-page
"walkthrough" Markdown summary suitable for inclusion in §6 of the technical
report. Pulls the most informative bits: target name + SMILES, the
retrosynthetic strategy, the failed-attempt steps with their failure_modes,
the recovery, and the verification.

Output: docs/walkthroughs.md (concatenated; one section per trace).

Usage:
    python src/extract_walkthroughs.py --top-k 10
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUALITY_JSON = ROOT / "data" / "traces" / "_quality_report.json"
TRACES_DIR = ROOT / "data" / "traces"
OUT_PATH = ROOT / "docs" / "walkthroughs.md"


def render_one(trace: dict) -> str:
    target = trace.get("target") or {}
    rs = trace.get("retrosynthetic_strategy") or {}
    val = trace.get("validation") or {}
    src = (trace.get("_provenance") or {}).get("source") or {}

    lines: list[str] = []
    lines.append(f"## {target.get('name', '?')}")
    lines.append("")
    lines.append(
        f"**trace_id:** `{trace.get('trace_id')}` &middot; "
        f"**source:** {src.get('journal','?')} {src.get('year','')} &middot; "
        f"**DOI:** {src.get('doi_or_id','?')} &middot; "
        f"**license:** {src.get('license','?')}"
    )
    lines.append("")
    if target.get("smiles"):
        lines.append(f"**Target SMILES:** `{target['smiles']}`")
    cls = target.get("natural_product_class")
    if cls:
        lines.append(f"**Class:** {cls}")
    motiv = target.get("motivation") or ""
    if motiv:
        lines.append("")
        lines.append(f"**Motivation:** {motiv}")
    lines.append("")

    # Retrosynthetic strategy
    lines.append("**Retrosynthesis (key disconnections):**")
    discos = rs.get("key_disconnections") or []
    if discos:
        for d in discos:
            lines.append(
                f"- *{d.get('bond_description','?')}* — "
                f"{d.get('named_strategy') or 'unspecified strategy'}: "
                f"{(d.get('reasoning') or '')[:160]}"
            )
        if rs.get("rationale"):
            lines.append("")
            lines.append(f"  > {rs['rationale'][:300]}")
    else:
        lines.append("- _none extracted_")
    lines.append("")

    # Failed-attempt highlight
    steps = trace.get("execution_trace") or []
    failed = [s for s in steps if (s.get("outcome") or {}).get("valid") is False]
    revisions = [s for s in steps if s.get("action") == "revision"]
    if failed:
        lines.append(f"**Failed attempts ({len(failed)}):**")
        for s in failed[:5]:
            mode = (s.get("outcome") or {}).get("failure_mode")
            obs = ((s.get("outcome") or {}).get("observation") or "")[:200]
            decision = ((s.get("thought") or {}).get("decision") or "")[:200]
            lines.append(
                f"- step {s['step_id']}: `{mode}` — *Decision was:* {decision}"
            )
            if obs:
                lines.append(f"    *Outcome:* {obs}")
        lines.append("")
    if revisions:
        lines.append(f"**Revisions ({len(revisions)}):**")
        for s in revisions[:5]:
            decision = ((s.get("thought") or {}).get("decision") or "")[:200]
            lines.append(
                f"- step {s['step_id']} (revises step {s.get('revises_step_id')}): {decision}"
            )
        lines.append("")

    # Validation summary
    metrics = val.get("metrics") or {}
    lines.append("**Validation:**")
    chars = val.get("characterization") or []
    if chars:
        lines.append(f"- techniques: {', '.join(chars[:8])}")
    for k, v in metrics.items():
        if isinstance(v, dict):
            lines.append(
                f"- {k}: **{v.get('value')} {v.get('unit','')}** — {v.get('interpretation','')[:120]}"
            )
    if val.get("significance"):
        lines.append("")
        lines.append(f"> {val['significance'][:400]}")
    lines.append("")

    # Stats footer
    qc = trace.get("_smiles_qc") or {}
    lines.append(
        f"_stats: {len(steps)} steps, {len(failed)} failed, {len(revisions)} revisions, "
        f"SMILES {qc.get('parseable',0)}/{qc.get('total',0)} parseable._"
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-k", type=int, default=10)
    ap.add_argument("--exclude", nargs="*", default=[],
                    help="trace_ids to skip (e.g. 'TS-PMC12794845' for a known review article)")
    ap.add_argument("--out", default=str(OUT_PATH))
    args = ap.parse_args()

    qr = json.loads(QUALITY_JSON.read_text())
    cards = qr.get("top_k") or qr.get("all_cards") or []
    excluded = set(args.exclude)
    selected: list[dict] = []
    for c in cards:
        if c.get("trace_id") in excluded:
            continue
        # Drop traces where target name looks like a label, not a chemistry name
        if (c.get("target_name") or "").strip().upper() in {"REVIEW", "PERSPECTIVE", "EDITORIAL"}:
            continue
        selected.append(c)
        if len(selected) >= args.top_k:
            break

    sections: list[str] = ["# Worked Examples (Sci-Evo Total-Synthesis Traces)\n",
                           "_Auto-generated from `data/traces/*.trace.json`. "
                           "These are the top-ranked traces by composite quality "
                           "score (failed-attempt density × step count × SMILES "
                           "parseable rate × target.smiles completeness)._\n"]
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(selected, 1):
        pmcid = c.get("pmcid") or c.get("trace_id", "").replace("TS-", "")
        trace_path = TRACES_DIR / f"{pmcid}.trace.json"
        if not trace_path.exists():
            continue
        try:
            t = json.loads(trace_path.read_text())
        except Exception:
            continue
        sections.append(f"\n# {i}. {(t.get('target') or {}).get('name') or pmcid}\n")
        sections.append(render_one(t))
    out_path.write_text("\n".join(sections))
    print(f"Wrote {out_path} ({len(selected)} walkthroughs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
