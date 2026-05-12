# Sci-Evo Total-Synthesis Trace Dataset

> Multi-step total-synthesis records restructured as **Sci-Evo** traces.
> Each record captures the published research closed loop
> **target → retrosynthetic strategy → execution trajectory → success verification**,
> with `valid=false` failed attempts and `revision` recovery steps as **first-class data**,
> every step grounded in a verbatim quote of the source paper.

Built for the **AGI4S Sci-Evo data-construction track** (deadline 2026-05-24).
Submission package: [`submission/`](submission/) (Chinese) · 12-section technical report at [`submission/technical_report.md`](submission/technical_report.md).

[![License: CC BY 4.0](https://img.shields.io/badge/dataset-CC--BY--4.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: MIT](https://img.shields.io/badge/code-MIT-green.svg)](LICENSE)
[![Schema](https://img.shields.io/badge/schema-JSON--Schema%20Draft%202020--12-orange.svg)](schema/sci_evo_total_synthesis.schema.json)

---

## TL;DR

| Property | Value |
|---|---|
| Records | **237** total-synthesis traces (one paper → one JSON) |
| Source | Open Access chemistry papers via Europe PMC (2018–2026) |
| Schema | [JSON-Schema Draft 2020-12](schema/sci_evo_total_synthesis.schema.json) — version 1.0.0 |
| Failure-rich | **84 %** of traces contain author-disclosed failed_attempts (target: ≥30 %) |
| Reasoning-rich | 20.1 steps / trace avg, each with a `[Background] / [Gap] / [Decision]` thought triple |
| Audit-able | **99 %** of steps anchored to verbatim `evidence.text_span` quotes |
| Validated | 100 % of published samples pass `jsonschema` (Draft 2020-12); RDKit canonical SMILES; PubChem name-backfilled targets |
| License — annotations & schema | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| License — original paper text/figures | Per-paper OA licence preserved in each `_provenance.source.license` |

## Why this dataset

USPTO, the Open Reaction Database, and Reaxys capture *successful* reactions. The decision-making — *which disconnection, which conditions to try, what failed, what worked next* — is exactly what AGI4S systems need and exactly what's been thrown away. This dataset puts the **decision chain** back: every record is one published total synthesis, restructured as the Sci-Evo brief asks for, with failed attempts as first-class data and explicit recovery pointers.

## Pipeline at a glance

```
Europe PMC OA PDF
       │  src/download_pdfs.py
       ▼
 MinerU API (cloud, vlm)                        ← stage 1
       │  full.md + per-block bbox JSON + figure images
       ▼
 Gemini 2.5 Flash (multimodal)                  ← stage 2: per-figure SMILES extraction
       │   src/extract_chem_from_image.py
       ▼
 Gemini 2.5 Flash (long-context)                ← stage 3: compose full Sci-Evo trace
       │   src/extract_trace.py
       │   + injected reagent-name dictionary
       │   + JSON-mode + backslash repair
       ▼
 RDKit canonicalize + PubChem name backfill     ← stage 4: validators
       │   src/validate_smiles.py + src/pubchem_lookup.py
       ▼
 jsonschema validation (Draft 2020-12)          ← stage 5: QC
       │   src/analyze_quality.py
       ▼
 data/traces/<PMCID>.trace.json                 ← the dataset
```

End-to-end orchestrator: [`src/process_batch.py`](src/process_batch.py) — idempotent (already-extracted traces are skipped on re-runs).

## Repo layout

```
.
├── README.md                                   # this file
├── DATASET_CARD.md                             # Hugging Face / OpenDataLab dataset card
├── MINERU_USAGE.md                             # dedicated MinerU usage statement
├── LICENSE                                     # MIT (code) + CC-BY-4.0 (annotations)
├── requirements.txt
│
├── docs/
│   ├── technical_report.md                     # English template (renders via render_report.py)
│   ├── technical_report.rendered.md            # numbers filled from latest _quality_report.json
│   ├── walkthroughs.md                         # auto-generated worked examples (top-10)
│   └── walkthrough_lappaceolides.md            # flagship hand-written narrative
│
├── schema/
│   ├── sci_evo_total_synthesis.schema.json     # authoritative JSON-Schema Draft 2020-12
│   └── SCHEMA.md                               # human-readable schema reference
│
├── src/
│   ├── download_pdfs.py                        # Europe PMC OA PDF download (with review filter)
│   ├── mineru_api.py                           # MinerU cloud API (batch upload + poll)
│   ├── extract_chem_from_image.py              # per-figure SMILES (multimodal LLM)
│   ├── extract_trace.py                        # full Sci-Evo trace (long-context LLM)
│   ├── validate_smiles.py                      # RDKit canonicalize + reagent name dict
│   ├── pubchem_lookup.py                       # name → SMILES backfill
│   ├── process_batch.py                        # end-to-end orchestrator (idempotent, parallel)
│   ├── analyze_quality.py                      # quality report + jsonschema validation
│   ├── extract_walkthroughs.py                 # generate worked-example narratives
│   ├── render_report.py                        # fill {VARS} in technical_report.md
│   ├── filter_sci_base_chem.py                 # Sci-Base chemistry subset filter
│   └── translate_md_zh.py                      # EN→ZH translator for the submission docs
│
├── data/
│   ├── pdfs/raw/                               # (gitignored) downloaded OA PDFs
│   ├── manifests/
│   │   ├── pilot.jsonl                         # 250 downloaded papers (DOI/title/abstract/journal)
│   │   └── sci_base_chem.jsonl                 # Sci-Base chemistry-subset candidates
│   ├── mineru_out/                             # (gitignored) MinerU per-paper outputs
│   ├── extracted/                              # (gitignored) per-image SMILES JSONL
│   └── traces/                                 # ⭐ the dataset
│       ├── PMC*.trace.json                     # 237 Sci-Evo traces
│       ├── _quality_report.md                  # quality report (markdown)
│       └── _quality_report.json                # quality report (machine-readable)
│
└── submission/                                 # competition submission package (Chinese)
    ├── README.md                               # submission overview (中文)
    ├── technical_report.md                     # 12-section technical report (中文)
    ├── MINERU_USAGE.md                         # MinerU usage statement (中文)
    ├── SUBMISSION_CHECKLIST.md                 # rubric-item mapping (中文)
    ├── dataset_link.md / code_repo.md          # public hosting pointers
    ├── schema/                                 # schema + SCHEMA.md (中文)
    ├── samples/                                # 10 schema-valid sample traces + manifest
    ├── original_data_samples/                  # 5 source OA PDFs
    └── walkthroughs/                           # flagship narrative + auto-generated top-10
```

## Quick start

```bash
git clone https://github.com/Zhao-Xinda/Sci-Evo_MinerU_xinda.git
cd Sci-Evo_MinerU_xinda
pip install -r requirements.txt

# Apply for a MinerU API token at https://mineru.net and an OpenRouter key at https://openrouter.ai
export MINERU_TOKEN=<your MinerU token>
export OPENROUTER_API_KEY=<your OpenRouter key>

# 1. Download OA total-synthesis PDFs from Europe PMC (review/perspective excluded)
python src/download_pdfs.py --limit 50

# 2. Parse via MinerU API (batches of up to 50 files)
python src/mineru_api.py --pdf-dir data/pdfs/raw --limit 50 \
    --out data/mineru_out/run_1

# 3. Stages 2-3 (image SMILES + trace extraction) end-to-end
python src/process_batch.py \
    --batch-result data/mineru_out/run_1/batch_*.json \
    --download-workers 16 --img-workers 16 --paper-workers 4 --trace-workers 8

# 4. Backfill empty target.smiles via PubChem
python src/pubchem_lookup.py --traces-dir data/traces

# 5. Quality report + JSON Schema validation
python src/analyze_quality.py

# 6. Pull current numbers into the report template
python src/render_report.py
python src/extract_walkthroughs.py --top-k 10
```

The pipeline is **idempotent** — re-running `process_batch.py` on the same MinerU batch result will skip already-extracted traces, so iterations on the schema or extraction prompt do not waste API tokens.

## Sci-Evo schema (top level)

```jsonc
{
  "trace_id":      "TS-<PMCID>",
  "schema_version": "1.0.0",
  "license":       "CC-BY-4.0",

  "target": {
    "name", "smiles", "natural_product_class",
    "structural_features": { "molecular_weight", "stereocenters", "ring_systems", "key_motifs" },
    "motivation",
    "prior_syntheses": [ { "lead_author", "year", "doi", "key_strategy" } ],
    "success_criteria": { /* free-form, recommended canonical keys */ }
  },

  "retrosynthetic_strategy": {
    "is_convergent": true,
    "key_disconnections": [
      { "bond_description", "named_strategy", "reasoning",
        "alternatives_considered": [ { "strategy", "rejected_because" } ] }
    ],
    "fragments":  [ { "fragment_id", "smiles", "role", "comes_from" } ],
    "rationale"
  },

  "execution_trace": [ {
    "step_id",
    "fragment_id":  null,
    "action":       "retrosynthetic_analysis | forward_reaction | failed_attempt | revision | characterization | scale_up | ...",
    "thought":      { "background", "gap", "decision" },
    "reaction":     { "substrate_smiles[]", "product_smiles[]", "rxn_smiles",
                      "named_reaction", "bond_formed", "bond_broken",
                      "reagents[]", "catalyst", "ligand", "solvent",
                      "temperature", "time", "atmosphere", "scale",
                      "stoichiometry": { "<reagent>": "<amount>" } },
    "outcome":      { "valid": true,
                      "yield_percent", "ee_percent", "dr", "regio_selectivity",
                      "failure_mode": null,         // typed when valid=false
                      "observation" },
    "revises_step_id":  null,                       // set when action="revision"
    "references":  [],
    "evidence":     { "text_span", "page", "section", "image_refs[]" }
  } ],

  "validation": { "characterization[]", "metrics": { /* {value, unit, interpretation} */ }, "significance" },

  "_provenance":  { "source", "mineru": { "method", "model_version", "batch_id", "result_zip_url", "parsed_at" },
                    "extraction_models[]", "validators[]", "human_reviewed" },

  "_smiles_qc":   { "total", "parseable", "invalid", "overrides[]", "pubchem_fills[]" }
}
```

Full reference: [`schema/SCHEMA.md`](schema/SCHEMA.md).

## Flagship worked example

[`docs/walkthrough_lappaceolides.md`](docs/walkthrough_lappaceolides.md) walks through the Lappaceolides A & B total synthesis (Pallerla *et al.*, *Org. Lett.* 2025) as a single Sci-Evo trace — five steps including an explicit `failed_attempt` over 13 reagent combinations and a typed `revision` recovery.

Auto-generated narratives for the top-10 traces in the pilot:
[`docs/walkthroughs.md`](docs/walkthroughs.md).

## Dataset stats (N = 237)

| Metric | Value |
|---|---|
| Trace extraction success rate | 237 / 250 = **94.8 %** |
| JSON-Schema pass rate | 214 / 237 = **90.3 %**; **10 / 10 (100 %)** for sampled traces |
| Avg / median / max steps per trace | 20.1 / 19 / 78 |
| Traces with ≥ 1 failed_attempt | **199 / 237 (84 %)** — target ≥ 30 % |
| Total failed_attempts disclosed | **966** |
| Total revision steps | **566** |
| `target.smiles` filled (after PubChem backfill) | 87 % |
| SMILES parseable rate (RDKit) | 71 % |
| `evidence.text_span` coverage | 99 % |
| Convergent-strategy traces | 63 % |
| Total SMILES extracted | 10,899 |

## License

- **Code** — [MIT](LICENSE)
- **Dataset annotations & JSON Schema** — [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
- **Original paper text / figures** — retained per upstream OA licence; per-record licence preserved in each trace's `_provenance.source.license`

## Citation

```bibtex
@dataset{sci_evo_total_synthesis_2026,
  title  = {Sci-Evo Total-Synthesis Trace Dataset},
  author = {Zhao, Xinda},
  year   = {2026},
  url    = {https://github.com/Zhao-Xinda/Sci-Evo_MinerU_xinda}
}
```

## Acknowledgements

- **MinerU** (OpenDataLab) — the document parser at the heart of the pipeline.
- **Sciverse Sci-Base** — the competition organiser's MinerU-pre-parsed chemistry sample, used as an enrichment corpus.
- **Europe PMC** — Open Access chemistry full-text PDF source.
- **PubChem** — name → SMILES backfill via PUG REST.
- **RDKit** — canonical SMILES and validity checking.
