#!/usr/bin/env python3
"""
Combine a MinerU-parsed paper directory + per-image SMILES into a Sci-Evo
total-synthesis trace conforming to schema/sci_evo_total_synthesis.schema.json.

Pipeline:
    1. Read full.md + content_list_v2.json from MinerU output.
    2. Optionally read paper.smiles.jsonl (output of extract_chem_from_image.py).
    3. Compose a schema-guided prompt and call Gemini 2.5 Flash via OpenRouter.
    4. Parse and lightly validate the returned JSON; merge in provenance.
    5. Save trace JSON.

Usage:
    python src/extract_trace.py \\
        --paper-dir /tmp/PMC12519463 \\
        --smiles-jsonl data/extracted/PMC12519463.smiles.jsonl \\
        --manifest data/manifests/pilot.jsonl \\
        --pmcid PMC12519463 \\
        --out data/traces/PMC12519463.trace.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

# Local QC module — RDKit canonicalization + reagent-name overrides.
sys_path_added = False
try:
    from validate_smiles import validate_trace as _validate_trace_smiles
except ImportError:
    # When invoked as `python src/extract_trace.py ...` the cwd may not be on
    # sys.path; add the script directory.
    import sys as _sys
    _sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    from validate_smiles import validate_trace as _validate_trace_smiles

DEFAULT_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

# Schema description embedded in the prompt. Mirrors
# schema/sci_evo_total_synthesis.schema.json but written for an LLM reader.
SCHEMA_INSTRUCTIONS = """\
Produce a single JSON object with these top-level keys:

trace_id (str)
schema_version (str = "1.0.0")
license (str = "CC-BY-4.0")

target: {
  name (str), smiles (str), inchi? (str), inchi_key? (str),
  natural_product_class (str),
  structural_features: { molecular_weight (num)?, stereocenters (int)?,
                          ring_systems (str)?, key_motifs ([str])? },
  motivation (str),
  prior_syntheses: [ {lead_author, year, doi?, key_strategy}, ... ],
  success_criteria: { yield_target_percent?, lls_target?, scale_target?,
                      stereochemistry_required?, free_text? }
}

retrosynthetic_strategy: {
  is_convergent (bool),
  key_disconnections: [ {
      bond_description (str),
      named_strategy (str)?,
      reasoning (str),
      alternatives_considered: [ {strategy, rejected_because} ]?
  }, ... ],
  fragments: [ {fragment_id, smiles, role, comes_from} ]?,
  rationale (str)?
}

execution_trace: [ {                          // chronological as published
  step_id (int >=1, unique, ordered),
  fragment_id (str | null),                   // which sub-route; null for main line
  action: one of [
      "retrosynthetic_analysis", "forward_reaction", "failed_attempt",
      "revision", "characterization", "scale_up",
      "literature_review", "hypothesis_formation"
  ],
  thought: {
      background (str),                       // What is known/completed up to this point
      gap (str),                              // What still needs to be solved
      decision (str)                          // "To <goal>, chose <tool/strategy>, expecting <outcome>."
  },
  reaction: {                                 // REQUIRED if action in {forward_reaction, failed_attempt, scale_up}
      substrate_smiles ([str]),
      product_smiles ([str]),
      rxn_smiles?,
      named_reaction?,
      bond_formed?, bond_broken?,
      reagents ([str])?, catalyst?, ligand?, solvent?, temperature?, time?,
      atmosphere?, scale?,
      stoichiometry?: { reagent_name -> amount_string }   // dict/object, e.g. {"Cs2CO3": "10.0 equiv"}
  },
  outcome: {
      valid (bool),                           // false marks a failed attempt
      yield_percent?, ee_percent?, dr?, regio_selectivity?,
      failure_mode: one of [null, "low_yield", "no_reaction",
                            "wrong_regiochemistry", "wrong_stereochemistry",
                            "epimerization", "decomposition",
                            "side_product_dominant", "scope_limited",
                            "scale_limited", "incompatible_protecting_group",
                            "purification_failed", "characterization_inconclusive",
                            "other"],         // REQUIRED when valid=false
      observation (str)
  },
  revises_step_id (int | null),               // REQUIRED when action="revision"
  references ([str])?,
  evidence: {
      text_span (str),                        // a verbatim quote from paper
      page (int)?, section (str)?,
      image_refs ([str])?                     // MinerU image filenames
  }
} ]

validation: {
  characterization: [str],                    // from {"1H NMR","13C NMR","2D NMR","HRMS","X-ray crystallography","IR","specific_rotation","comparison_to_authentic","circular_dichroism","elemental_analysis","other"}
  metrics: { <metric_name>: { value, unit, interpretation } },
                                              // include "Overall Yield", "Longest Linear Steps", "Total Steps", "Failed Attempts Count" when known
  comparison_to_prior?, significance (str)
}

(_provenance is appended programmatically afterwards — do not include it.)

Hard rules:
- Output JSON ONLY, no markdown fences, no commentary.
- Use ASCII; escape backslashes in SMILES.
- evidence.text_span MUST be a verbatim substring of the paper.
- For every step where authors describe a tried-and-failed condition or strategy
  (signal words: "did not", "failed", "no detectable", "no reaction", "decomposition",
  "epimerization", "in low yield", "could not"), emit a separate execution step with
  action="failed_attempt", outcome.valid=false, and an appropriate failure_mode.
  Then capture the recovery in a follow-up action="revision" step with revises_step_id
  pointing to that failed step.
- If you cannot determine a required field, use a short placeholder like "unspecified"
  rather than dropping the field — but only as a last resort.
"""


# JSON-valid escape characters per RFC 8259: " \ / b f n r t u
_VALID_JSON_ESC = set('"\\/bfnrtu')


def _fix_invalid_backslash_escapes(text: str) -> str:
    """Repair LLM-emitted JSON where SMILES / LaTeX backslashes are not
    properly double-escaped. RFC-8259 forbids `\\X` for X not in
    {"\\bfnrtu/}; we patch each such occurrence to `\\\\X`. Critically, we
    consume valid escape pairs (`\\\\`, `\\"`, ...) atomically so that the
    second char of a pair is not re-checked as a fresh backslash."""
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\\" and i + 1 < n:
            nxt = text[i + 1]
            if nxt in _VALID_JSON_ESC:
                # Valid escape sequence — copy both chars and advance by 2.
                out.append(ch)
                out.append(nxt)
                i += 2
            else:
                # Invalid escape — double the backslash, keep next char.
                out.append("\\\\")
                out.append(nxt)
                i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _coerce_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
    if m:
        text = m.group(1).strip()
    if not text.startswith("{"):
        l = text.find("{")
        r = text.rfind("}")
        if l != -1 and r != -1 and r > l:
            text = text[l : r + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Most common LLM mistake: unescaped backslashes inside SMILES strings.
        if "Invalid \\escape" in str(e) or "Invalid escape" in str(e):
            return json.loads(_fix_invalid_backslash_escapes(text))
        raise


def _format_reagent_hints() -> str:
    """Serialize a curated reagent-name -> SMILES dict for the LLM prompt.
    Helps the model emit correct SMILES for common reagents that are usually
    referred to by name (rather than drawn) in total-synthesis papers."""
    from validate_smiles import REAGENT_SMILES
    lines = [f"  {name}: {smi}" for name, smi in REAGENT_SMILES.items()]
    return "\n".join(lines)


def build_prompt(
    *, title: str, full_md: str, smiles_records: list[dict], manifest_meta: dict
) -> str:
    # Compact molecule list: one line per detected structure.
    mol_lines: list[str] = []
    for rec in smiles_records:
        if not rec.get("is_chemical") or rec.get("_error"):
            continue
        img_ref = Path(rec.get("_image_path", "")).name
        for mol in rec.get("molecules") or []:
            sm = (mol.get("smiles") or "").strip()
            if not sm:
                continue
            mol_lines.append(
                f"- img={img_ref} label={mol.get('label') or ''!r} role={mol.get('role','?')} smiles={sm}"
            )
        for rxn in rec.get("reactions") or []:
            mol_lines.append(
                f"- img={img_ref} reaction: from={rxn.get('from_labels')} -> to={rxn.get('to_labels')} "
                f"named={rxn.get('named_reaction')!r} cond={rxn.get('conditions')!r} yield={rxn.get('yield_percent')}"
            )
    smiles_block = "\n".join(mol_lines) if mol_lines else "(none extracted)"

    meta = f"DOI: {manifest_meta.get('doi')}\nJournal: {manifest_meta.get('journal')}\nYear: {manifest_meta.get('year')}\nTitle: {title or manifest_meta.get('title')}"

    return f"""You are extracting a structured Sci-Evo total-synthesis trace from a chemistry paper.

==== PAPER METADATA ====
{meta}

==== SCHEMA INSTRUCTIONS ====
{SCHEMA_INSTRUCTIONS}

==== COMMON REAGENT/SOLVENT NAME -> CANONICAL SMILES ====
When the paper refers to any of these compounds by name in substrate_smiles,
product_smiles, or as a reagent that needs a SMILES, USE THE SMILES BELOW
EXACTLY (do not invent a different SMILES for the same name):
{_format_reagent_hints()}

==== PAPER FULL TEXT (MinerU-parsed Markdown) ====
{full_md}

==== EXTRACTED MOLECULES & REACTIONS (from figures) ====
{smiles_block}

==== TASK ====
Read the paper. Build the Sci-Evo total-synthesis trace JSON now.
Be especially careful to:
  (a) enumerate failed attempts as their own execution_trace steps with
      outcome.valid=false and an appropriate failure_mode, then add the
      recovery as an action="revision" step pointing back via revises_step_id;
  (b) target.smiles is REQUIRED — always provide your best canonical SMILES
      for the target molecule, even for complex natural products (the molecule
      is well known if the paper names it). For SMILES inside individual
      execution_trace.reaction blocks, when truly uncertain about a complex
      drawn intermediate, leave that field as an empty string rather than
      guessing wrong;
  (c) do NOT confuse reagents/solvents with substrates: substrate_smiles is the
      molecule being transformed, NOT the reagent doing the transforming.

Output JSON ONLY.
"""


def make_client() -> OpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY env var required")
    return OpenAI(base_url=DEFAULT_BASE_URL, api_key=api_key)


def call_llm(
    client: OpenAI, prompt: str, model: str, *, max_retries: int = 2
) -> str:
    """Call the chat model. Try response_format=json_object first; if the
    provider rejects it, fall back to plain. Retry on empty responses."""
    last_err: Exception | None = None
    for attempt in range(max_retries + 1):
        kwargs = dict(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        # Many OpenRouter models accept JSON-mode; if the upstream rejects it
        # we'll retry without on the next attempt.
        if attempt == 0:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            completion = client.chat.completions.create(**kwargs)
            content = completion.choices[0].message.content or ""
            if content.strip():
                return content
            last_err = RuntimeError("empty content")
        except Exception as e:
            last_err = e
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"LLM call failed after retries: {last_err}")


def get_paper_title_from_md(md_text: str) -> str:
    for line in md_text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def lookup_manifest(manifest_path: Path, key: str) -> dict:
    """Find first manifest entry whose pmcid or doi matches key."""
    if not manifest_path.exists():
        return {}
    with manifest_path.open() as f:
        for line in f:
            r = json.loads(line)
            if r.get("pmcid") == key or r.get("doi") == key or Path(r.get("local_path", "")).stem == key:
                return r
    return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper-dir", required=True, help="MinerU output dir for one paper")
    ap.add_argument("--smiles-jsonl", help="Per-image SMILES JSONL (extract_chem_from_image output)")
    ap.add_argument("--manifest", default="data/manifests/pilot.jsonl")
    ap.add_argument("--pmcid", help="PMC ID; default = paper-dir basename")
    ap.add_argument("--mineru-batch-id", default="")
    ap.add_argument("--mineru-zip-url", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    paper_dir = Path(args.paper_dir)
    md_path = paper_dir / "full.md"
    if not md_path.exists():
        print(f"ERROR: {md_path} not found", file=sys.stderr)
        return 2
    full_md = md_path.read_text()
    title = get_paper_title_from_md(full_md)
    pmcid = args.pmcid or paper_dir.name

    smiles_records: list[dict] = []
    if args.smiles_jsonl and Path(args.smiles_jsonl).exists():
        with Path(args.smiles_jsonl).open() as f:
            for line in f:
                if line.strip():
                    smiles_records.append(json.loads(line))

    manifest_meta = lookup_manifest(Path(args.manifest), pmcid)

    prompt = build_prompt(
        title=title,
        full_md=full_md,
        smiles_records=smiles_records,
        manifest_meta=manifest_meta,
    )

    print(f"calling {args.model} with {len(prompt)} char prompt...", flush=True)
    client = make_client()
    response = call_llm(client, prompt, args.model)
    try:
        trace = _coerce_json(response)
    except json.JSONDecodeError as e:
        Path(args.out).with_suffix(".raw.txt").write_text(response)
        print(f"ERROR: JSON parse failed: {e}\n  raw saved to {Path(args.out).with_suffix('.raw.txt')}",
              file=sys.stderr)
        return 1

    # Provenance — appended programmatically.
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
            "batch_id": args.mineru_batch_id,
            "result_zip_url": args.mineru_zip_url,
            "parsed_at": datetime.now(timezone.utc).isoformat(),
        },
        "extraction_models": [
            {"stage": "image_smiles", "name": DEFAULT_MODEL, "version": ""},
            {"stage": "trace_extraction", "name": args.model, "version": ""},
        ],
        "human_reviewed": False,
    }
    # Override trace_id unconditionally — the LLM tends to invent its own
    # which makes cross-trace dedup impossible.
    trace["trace_id"] = f"TS-{pmcid}"
    trace["schema_version"] = "1.0.0"
    trace["license"] = "CC-BY-4.0"

    # SMILES QC: RDKit canonicalize + reagent-name overrides.
    _validate_trace_smiles(trace)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(trace, ensure_ascii=False, indent=2))

    # Summary
    n_steps = len(trace.get("execution_trace") or [])
    n_failed = sum(
        1
        for s in (trace.get("execution_trace") or [])
        if (s.get("outcome") or {}).get("valid") is False
    )
    n_disco = len((trace.get("retrosynthetic_strategy") or {}).get("key_disconnections") or [])
    print(
        f"Saved: {out_path}\n  steps={n_steps} failed_attempts={n_failed} disconnections={n_disco}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
