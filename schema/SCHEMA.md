# Sci-Evo Total-Synthesis Trace — Schema Reference

**Authoritative file:** [`sci_evo_total_synthesis.schema.json`](sci_evo_total_synthesis.schema.json) (JSON-Schema Draft 2020-12).
**Schema version:** `1.0.0`
**Records:** one `<PMCID>.trace.json` per published total-synthesis paper.

This document is a human-readable companion to the JSON Schema. The JSON Schema is the source of truth; if the two disagree, fix the JSON.

---

## Why this shape

The schema is designed to capture **how a published total synthesis was reasoned about, executed, and verified** — not just the molecules and reactions. It draws three concrete design choices from the organiser's reference [`Sci-Evo_tool_case.json`](../other/Sci-Evo_tool_case.json):

1. **Structured `[Background] / [Gap] / [Decision]` reasoning per step** — every action in the trajectory carries a thought triple, so a model trained on this data can mimic scientific deliberation, not just outcomes.
2. **`valid: false` is a first-class marker** — failed attempts are not deleted; they sit alongside successful steps with a typed `failure_mode` and the recovery is a `revision` step that points back via `revises_step_id`.
3. **Quantifiable `metrics` per `{value, unit, interpretation}` triple** — verification is itself structured data.

…and adds three chemistry-specific extensions on top:

- **`Reaction` is first-class**, not a free-form `parameters` blob — `substrate_smiles`, `product_smiles`, `rxn_smiles`, `named_reaction`, `reagents`, `catalyst`, `ligand`, `solvent`, `temperature`, `time`, `stoichiometry {reagent: amount}`.
- **DAG fragment structure** — `retrosynthetic_strategy.fragments[]` plus per-step `fragment_id` makes convergent (not just linear) syntheses representable.
- **Typed `failure_mode` enum** — `low_yield`, `wrong_stereochemistry`, `decomposition`, `no_reaction`, `epimerization`, `reactor_clogging`, … — gives downstream consumers a label space to learn over.

---

## Top-level shape

```
{
  trace_id:         "TS-<PMCID>"            # required
  schema_version:   "1.0.0"
  license:          "CC-BY-4.0"
  target:                  ↘ §1
  retrosynthetic_strategy: ↘ §2             # required
  execution_trace:         ↘ §3 (array)     # required
  validation:              ↘ §4
  _provenance:             ↘ §5             # required
  _smiles_qc:              ↘ §6             # programmatic
}
```

Required top-level keys: `trace_id`, `target`, `retrosynthetic_strategy`, `execution_trace`, `_provenance`. (`validation` is *recommended* but not enforced — pilot-stage relaxation; some papers don't have a separable validation section.)

---

## §1 `target` — what is being synthesised

```yaml
target:
  name:                    str         # "(-)-strychnine", "Lappaceolides A and B"
  smiles:                  str         # RDKit-canonical isomeric SMILES
  inchi:                   str?        # optional
  inchi_key:               str?
  natural_product_class:   str?        # "macrolide", "indole alkaloid", "terpenoid"
  structural_features:
    molecular_weight:      number?
    stereocenters:         int?
    ring_systems:          str?        # "fused 6-6-6 + bridged 7"
    key_motifs:            [str]?      # ["quaternary stereocenter", "vicinal diol"]
  motivation:              str         # WHY synthesise this — bio activity, scale, ...
  prior_syntheses:         [           # optional list of earlier syntheses cited
    { lead_author, year, doi?, key_strategy }
  ]
  success_criteria:
    yield_target_percent:    number|str?
    lls_target:              int|str?
    scale_target:            str?
    stereochemistry_required: str|bool?
    free_text:               str?
```

Required: `name`, `smiles`, `motivation`, `success_criteria`.

---

## §2 `retrosynthetic_strategy` — the on-paper plan

```yaml
retrosynthetic_strategy:
  is_convergent:        bool          # true if independent fragments are joined
  key_disconnections:   [             # the high-level cuts the authors made
    bond_description:   str           # "C11-C12 bond", "macrolactonisation at C1-O17"
    named_strategy:     str?          # "NHK", "RCM", "Suzuki", "Diels-Alder"
    reasoning:          str           # WHY this cut — strategic bond, FGI, stereo, convergence
    alternatives_considered: [        # paths considered on paper but rejected
      { strategy, rejected_because }
    ]
  ]
  fragments:            [             # convergent sub-routes
    { fragment_id, smiles, role, comes_from }
  ]
  rationale:            str?          # free-text overall strategy
```

Required: `is_convergent`, `key_disconnections`.

---

## §3 `execution_trace` — the chronological trajectory

Each step is a single action with structured reasoning + (where applicable) a chemical transformation + an outcome.

```yaml
execution_trace[]:
  step_id:        int                 # 1, 2, 3, …  (chronological as published)
  fragment_id:    str | null          # which sub-route; null = main convergent line
  action:         enum                # see §3.1
  thought:                            # the [Background]/[Gap]/[Decision] triple
    background:   str                 # what is known/completed up to this point
    gap:          str                 # what still needs to be solved
    decision:     str                 # "To <goal>, chose <tool>, expecting <outcome>."
  reaction:                           # required iff action involves a reaction (§3.2)
    ↘ §3.2
  outcome:                            # see §3.3
    valid:        bool                # ★ false marks a FAILED ATTEMPT
    yield_percent: number|null?
    ee_percent:   number|null?
    dr:           str|number?         # "10:1", ">20:1", or numeric
    regio_selectivity: str?
    failure_mode: str|null            # required when valid=false
    observation:  str
  revises_step_id: int|null           # required when action="revision"
  references:    [str]                # external citations
  evidence:                           # always recommended
    text_span:    str                 # verbatim quote from paper main text or SI
    page:         int|null?
    section:      str|null?
    image_refs:   [str]?              # MinerU image filenames showing structures
```

### §3.1 `action` enum

| Value | When |
|---|---|
| `retrosynthetic_analysis` | A planning / on-paper analysis step (no wet experiment) |
| `forward_reaction` | A reaction that achieved its decision goal |
| `failed_attempt` | A reaction tried but did not achieve its decision goal — paired with `outcome.valid=false` and a typed `failure_mode` |
| `revision` | A subsequent step that replaces a failed attempt — must set `revises_step_id` |
| `characterization` | NMR / MS / X-ray confirmation of an intermediate or final product |
| `scale_up` | A late-stage scale-up of an already-validated reaction |
| `literature_review` | A literature lookup that drove the next decision |
| `hypothesis_formation` | A pure hypothesis-formation step (rare) |

### §3.2 `reaction` block (chemistry-native)

Required when `action` is one of `forward_reaction`, `failed_attempt`, `scale_up`.

```yaml
reaction:
  substrate_smiles:    [str]          # RDKit-canonical
  product_smiles:      [str]
  rxn_smiles:          str|null?      # "A.B>>C"
  named_reaction:      str|null?      # "Suzuki", "Diels-Alder", …
  bond_formed:         str|null?      # "C-C", "C-N", "C=C", …
  bond_broken:         str|null?
  reagents:            [str]?         # natural-language list
  catalyst:            str|null?
  ligand:              str|null?
  solvent:             str|null?      # SMILES OR name (e.g. "1,2-DCE", "THF")
  temperature:         str|null?      # "85 °C", "rt"
  time:                str|null?      # "4 h"
  atmosphere:          str|null?      # "Ar", "N2"
  scale:               str|null?      # "multigram"
  stoichiometry:       { reagent: amount_str }   # ★ object/dict, not string
```

### §3.3 `failure_mode` recommended values

When `outcome.valid = false`, set `failure_mode` to one of:

```
low_yield · no_reaction · wrong_regiochemistry · wrong_stereochemistry ·
epimerization · decomposition · side_product_dominant · scope_limited ·
scale_limited · incompatible_protecting_group · purification_failed ·
characterization_inconclusive · reactor_clogging · other
```

The schema does **not** enforce this list strictly — any string is accepted — but downstream consumers should canonicalise to it. The list grew during pilot extraction to absorb chemistry-specific failure types (e.g. `reactor_clogging` from continuous-flow synthesis literature).

---

## §4 `validation` — final-product confirmation

```yaml
validation:
  characterization: [str]             # ["1H NMR", "X-ray", "comparison_to_authentic", …]
  metrics:
    "Overall Yield":          { value, unit, interpretation }
    "Longest Linear Steps":   { value, unit, interpretation }
    "Total Steps":            { value, unit, interpretation }
    "Failed Attempts Count":  { value, unit, interpretation }
    # additional metric_name -> {value, unit, interpretation} entries allowed
  comparison_to_prior:  str?          # how this synthesis differs from earlier routes
  significance:         str           # final-verdict paragraph
```

`metrics` is a free-form map keyed by metric name; recommended canonical keys are `Overall Yield`, `Longest Linear Steps`, `Total Steps`, `ee`, `Largest Scale`, `Failed Attempts Count`.

---

## §5 `_provenance` — full audit trail

```yaml
_provenance:
  source:
    doi_or_id:    str
    pmcid:        str?
    title, authors, journal, year, license, pdf_url
  mineru:
    method:           "MinerU API (cloud)" | "MinerU OSS (local)" | "Sci-Base (pre-parsed)"
    model_version:    str       # e.g. "vlm"
    batch_id:         str       # MinerU batch id — direct re-fetch handle
    result_zip_url:   str
    parsed_at:        ISO-8601 datetime
  extraction_models:
    [{ stage: "image_smiles" | "trace_extraction" | … , name, version }]
  validators:
    [{ name: "RDKit canonicalize" | "PubChem name lookup" | … , result }]
  human_reviewed:   bool        # default false; set true after human QC pass
  review_notes:     str?
```

---

## §6 `_smiles_qc` — automatic QC summary

Programmatically appended by `src/validate_smiles.py` after every trace extraction. **Not part of the LLM's emitted content.**

```yaml
_smiles_qc:
  total:               int          # total SMILES strings touched
  parseable:           int          # parsed cleanly by RDKit
  canonicalized:       int          # changed shape after canonicalisation
  invalid:             int
  overridden_by_name:  int          # number of fills via the reagent dict / PubChem
  invalid_examples:    [str]
  overrides:           [{ field, named_compound, was, now, reason }]
  pubchem_fills:       [{ field, name, smiles, cid }]
```

---

## Validation

```python
import jsonschema, json
schema = json.loads(open("schema/sci_evo_total_synthesis.schema.json").read())
trace  = json.loads(open("data/traces/PMC12519463.trace.json").read())
jsonschema.Draft202012Validator(schema).validate(trace)
```

The pilot dataset (50 traces, 50/50 schema pass) is validated as part of `src/analyze_quality.py`.

---

## Soft invariants (recommended, not schema-enforced)

These are caught by the `analyze_quality.py` reporter and surfaced in `_quality_report.md`:

- When `outcome.valid = false`, `outcome.failure_mode` SHOULD be set.
- When `action = "revision"`, `revises_step_id` SHOULD point back to a prior step with `outcome.valid = false`.
- When `action ∈ {forward_reaction, failed_attempt, scale_up}`, `reaction` SHOULD be present.
- `evidence.text_span` SHOULD be a verbatim substring of the source paper (audit script can verify).

These are intentionally not hard schema rules in v1 so partial / imperfect LLM extractions still validate; downstream cleaners can elevate them to enforced invariants in a v2 schema.
