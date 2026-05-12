---
license: cc-by-4.0
language:
  - en
tags:
  - chemistry
  - total-synthesis
  - retrosynthesis
  - reasoning
  - chain-of-thought
  - sci-evo
  - ai-for-science
  - ai4s
size_categories:
  - n<1K
pretty_name: Sci-Evo Total-Synthesis Trace Dataset
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/traces/*.trace.json
---

# Sci-Evo Total-Synthesis Trace Dataset

A structured corpus of total-synthesis records ("traces") rebuilt from Open Access chemistry papers as Sci-Evo trajectories — each captures the **full research closed loop**: target → retrosynthetic strategy → ordered execution trajectory (with first-class `valid=false` failed attempts and `revision` recovery steps) → success verification, every step grounded in a verbatim quote of the source paper.

Built for the **AGI4S Sci-Evo data-construction track** (deadline 2026-05-24).

## TL;DR

| Property | Value |
|---|---|
| Domain | Synthetic chemistry — total synthesis of natural products |
| Records | One JSON per paper (one paper per published total-synthesis study) |
| Schema | [`schema/sci_evo_total_synthesis.schema.json`](schema/sci_evo_total_synthesis.schema.json) — JSON-Schema Draft 2020-12, version 1.0.0 |
| Failure-rich? | **Yes** — 64 % of pilot traces include at least one author-disclosed failed attempt (target was 30 %) |
| Reasoning-rich? | **Yes** — every step carries a `[Background] / [Gap] / [Decision]` thought triple |
| Audit-able? | **Yes** — 98 % of steps anchored to a verbatim `evidence.text_span` quote from the source paper |
| Validated? | RDKit canonical SMILES + PubChem name lookup + JSON-Schema (Draft 2020-12) |
| License — annotations & schema | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| License — source paper text/figures | Original Open Access licence preserved per record (`_provenance.source.license`) |

## Why this dataset

USPTO, the Open Reaction Database, and Reaxys capture *successful* reactions. The decision-making — *which disconnection, which conditions to try, what failed, what worked next* — is exactly what AGI4S systems need and exactly what's been thrown away. This dataset puts the **decision chain** back: every record is one published total synthesis, restructured as the Sci-Evo brief asks for, with failed attempts as first-class data and explicit recovery pointers.

## Schema (top level)

```
{
  trace_id, schema_version, license,
  target {
    name, smiles, natural_product_class,
    structural_features {…}, motivation, prior_syntheses[…],
    success_criteria {…}
  },
  retrosynthetic_strategy {
    is_convergent, key_disconnections[{bond_description, named_strategy,
                                        reasoning, alternatives_considered[…]}],
    fragments[{fragment_id, smiles, role, comes_from}], rationale
  },
  execution_trace[ {
    step_id, fragment_id?,
    action: retrosynthetic_analysis | forward_reaction | failed_attempt |
            revision | characterization | scale_up | …,
    thought {background, gap, decision},
    reaction { substrate_smiles[], product_smiles[], rxn_smiles?,
               named_reaction, reagents[], catalyst, ligand, solvent,
               temperature, time, stoichiometry {reagent: amount}, …},
    outcome { valid, yield_percent?, ee_percent?, dr?,
              failure_mode?, observation },
    revises_step_id?, references[], evidence {text_span, page?, image_refs[]}
  } ],
  validation { characterization[], metrics{}, significance },
  _provenance { source, mineru, extraction_models, validators, human_reviewed },
  _smiles_qc  { total, parseable, invalid, … }     // QC summary
}
```

Full reference: [`schema/SCHEMA.md`](schema/SCHEMA.md).

## How it was built

```
Europe PMC OA chem PDF
       │  src/download_pdfs.py
       ▼
  MinerU API (cloud, vlm)            ← step 1 of MinerU usage
       │  full.md + bbox JSON + images
       ▼
  Gemini 2.5 Flash multimodal        ← per-figure SMILES extraction
       │   src/extract_chem_from_image.py
       ▼
  Gemini 2.5 Flash long-context      ← compose full Sci-Evo trace
       │   src/extract_trace.py + reagent-name dict + JSON repair
       ▼
  RDKit canonicalize + PubChem name backfill
       │   src/validate_smiles.py + src/pubchem_lookup.py
       ▼
  jsonschema validation (Draft 2020-12)
       │   src/analyze_quality.py
       ▼
  data/traces/<PMCID>.trace.json
```

End-to-end orchestrator: [`src/process_batch.py`](src/process_batch.py) — idempotent (already-extracted traces are skipped on re-runs).

## Pilot quality (N=50)

| Metric | Value |
|---|---|
| Trace extraction success | **50/50 (100 %)** |
| JSON-Schema pass rate | **100 %** |
| Avg / median / max steps per trace | **16.8 / 13 / 78** |
| Traces with ≥1 failed_attempt | **32 / 50 (64 %)** ← target ≥ 30 % |
| Total failed_attempts disclosed | **112** |
| Total revision steps | **88** |
| `target.smiles` filled | **92 %** (after PubChem backfill) |
| SMILES parseable rate (RDKit) | 68 % |
| `evidence.text_span` coverage | **98 %** |
| Convergent-strategy traces | 64 % |

## Quick start

```python
import json
from pathlib import Path

# Load any trace
trace = json.loads(Path("data/traces/PMC12519463.trace.json").read_text())
print(trace["target"]["name"], "→", trace["target"]["smiles"])
for s in trace["execution_trace"]:
    print(f"{s['step_id']:>2} {s['action']:>20} valid={s['outcome']['valid']}")
    print(f"   {s['thought']['decision']}")
```

```python
# Filter to high-quality, failure-rich traces
import jsonschema
schema = json.loads(open("schema/sci_evo_total_synthesis.schema.json").read())
v = jsonschema.Draft202012Validator(schema)
for p in Path("data/traces").glob("*.trace.json"):
    t = json.loads(p.read_text())
    n_failed = sum(1 for s in t["execution_trace"] if not s["outcome"]["valid"])
    parseable = (t.get("_smiles_qc", {}).get("parseable", 0)
                 / max(t.get("_smiles_qc", {}).get("total", 1), 1))
    if v.is_valid(t) and n_failed >= 1 and parseable > 0.7:
        print(p.name, "—", t["target"]["name"])
```

## Source data

- **Primary:** Europe PMC OA full-text PDFs filtered to chemistry journals (Beilstein J Org Chem, Chemical Science, Nat Chem, Nat Commun, JACS Au, ACS Cent Sci, Org Lett, J Org Chem, Angew Chem Int Ed, JACS, …) with `"total synthesis" AND OPEN_ACCESS:Y AND HAS_PDF:Y`, year ≥ 2018, **excluding reviews / perspectives / corrections / errata** by title regex + Medline pubType filter.
- **Secondary:** Sciverse Sci-Base (organiser-provided) — the chemistry subset of the already-MinerU-parsed 35 k-paper sample.

Per-paper original Open Access licence (CC-BY, CC-BY-NC, …) is preserved in each record's `_provenance.source.license`. Users redistributing derived works must comply with the most restrictive applicable upstream licence.

## MinerU usage statement

This dataset exercises the MinerU pipeline at **two distinct touch-points** (see [`MINERU_USAGE.md`](MINERU_USAGE.md) for the full statement):

1. **MinerU cloud API (primary)** — `src/mineru_api.py` calls `POST /api/v4/file-urls/batch` to register file metadata, PUTs each PDF to its presigned upload URL, then polls `GET /api/v4/extract-results/batch/{batch_id}`. We use `model_version: "vlm"`. Per-paper MinerU `batch_id` and `result_zip_url` are recorded in `_provenance.mineru` for full traceability.
2. **Sci-Base (already MinerU-parsed corpus)** — where the Sci-Base sample's Chemistry subset overlaps our targets, we consume it directly (recorded as `_provenance.mineru.method = "Sci-Base (pre-parsed)"`), avoiding redundant MinerU API calls and demonstrating use of the organiser-provided corpus.

## Application scenarios

1. **Train CoT / agentic-chemistry models** on real synthesis decisions — the `[Background] → [Gap] → [Decision]` triples plus failed-attempts give direct supervision for "agentic chemist" behaviour.
2. **Strategy-conditioned reaction prediction** — `retrosynthetic_strategy.key_disconnections[].named_strategy` paired with `execution_trace[].reaction.{reagents,conditions,yield}` gives the right inputs.
3. **Failure-mode learning** — `outcome.failure_mode` is exactly the label space a route-planner needs to *avoid* known-bad transformations.
4. **Citation / evidence-grounded chemistry QA** — every step has a verbatim `evidence.text_span`.
5. **Bench-marking scientific agents** on multi-step synthesis tasks where intermediate revision is part of the score.

## Limitations

- The pilot is 50 papers (250 by submission deadline). Generalisation beyond natural-product total synthesis is not claimed.
- SMILES parseable rate is 68 %; the missing 32 % are mostly complex drawn intermediates the multimodal model could not reliably read. We chose to mark these as empty rather than guess.
- `target.smiles` is filled to 92 %; the residual 8 % are uncommon natural products (e.g. `euphorikanin A`) absent from PubChem under the cited name.
- Human review has not yet been performed. Each record carries `_provenance.human_reviewed = false`. Cards may be added for individual records once reviewed.

## Citation

```bibtex
@dataset{sci_evo_total_synthesis_2026,
  title  = {Sci-Evo Total-Synthesis Trace Dataset},
  year   = {2026},
  url    = {https://github.com/<TBD>}
}
```

## Contact / contributions

Issues and pull requests welcome at the GitHub repository. Per-trace QC corrections are particularly valuable — please open one PR per trace with `_provenance.human_reviewed: true` and a note describing the change.
