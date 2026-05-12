# Worked Example — *(±)*-Lappaceolides A & B

> **Trace:** [`TS-PMC12519463`](../data/traces/PMC12519463.trace.json)
> **Source:** Pallerla, Hakola, Härkönen & Siitonen, *Org. Lett.* **2025**, 27, 11149–11151. DOI [10.1021/acs.orglett.5c02445](https://doi.org/10.1021/acs.orglett.5c02445). License: CC-BY.
> **MinerU:** API `vlm`, batch `de091bba-…`. **Trace extraction:** `google/gemini-2.5-flash` (long-context).

This walkthrough shows how a single Open Access total-synthesis paper becomes one Sci-Evo trace. We chose Lappaceolides A & B not because the synthesis is the longest in the pilot (it isn't — it's only five steps including characterisation), but because every Sci-Evo design decision is exercised in a small footprint: a structured retrosynthesis tree, an explicit failed-attempt step that lists thirteen reagent combinations the authors tried, a typed `revision`, and a final kinetic-control insight that an AGI-for-Science model needs in order to *not redo the failures*.

---

## 1. Target

**Lappaceolides A and B** are dimeric monoterpenoid lactones isolated by Ragasa et al. from *Nephelium lappaceum* (rambutan). Structurally they are a *cis*-fused **dioxabicyclo[3.3.0]octane** decorated with two fused γ-butyrolactones — three contiguous stereocentres bridging the two halves of an apparently dimeric scaffold.

```
Target SMILES (canonical, RDKit):
    O=C1C[C@@]2(CO1)CO[C@@]1(CO)CC(=O)O[C@@H]21
```

The original Ragasa paper proposed a **biosynthetic origin** by oxidative homo-dimerisation of a simpler monomer, *siphonodin*. The biosynthetic pathway was a hypothesis on paper. The synthetic chemists set themselves a single quantifiable goal: *"Achieve a biomimetic total synthesis of racemic lappaceolides A and B directly from siphonodin in a single step, confirming the proposed biosynthetic pathway."*

This is the kind of problem Sci-Evo is built to capture: **the value isn't only that the molecule was made, it's the structured argument for how and why.**

---

## 2. Retrosynthetic strategy (extracted)

The trace records **two key disconnections**:

| # | Bond | Named strategy | Reasoning |
|---|---|---|---|
| 1 | C3–O of the bicyclic ether | *oxa-Michael* (retro) | Yields dimeric diol **4** |
| 2 | dimeric diol **4** → two siphonodin (**3**) | *vinylogous Michael* (retro) | Aligns with the proposed homodimerisation |

Both disconnections converge into one operational hypothesis: *if the two retro arrows are real, then in the forward direction a single **vinylogous-Michael / oxa-Michael domino** should assemble the lappaceolides directly from two equivalents of siphonodin*. That hypothesis is precisely what `retrosynthetic_strategy.rationale` records:

> *"The retrosynthetic analysis is based on Ragasa's siphonodin homodimerisation hypothesis, aiming to combine the vinylogous Michael and oxa-Michael disconnections into a single domino reaction in the forward sense."*

`is_convergent = true`; the strategy is convergent in form (two pieces joining) even though both pieces are the same molecule.

---

## 3. Execution trajectory

The five-step trace tells a tight story.

### Step 1 — Forward reaction: scalable monomer synthesis

`action: forward_reaction` &middot; valid: true &middot; yield: 78 %

> *"To synthesise siphonodin (3), dihydroxyacetone (7) will be treated with ylide 8 in a Wittig-olefination–lactonization domino reaction, expecting a good yield and scalability."*

The substrate SMILES `O=C(CO)CO` is **the canonical SMILES of dihydroxyacetone** — important because the prompt's reagent dictionary corrects the LLM's earlier (and wrong) guess of `O=C(O)CCO` (3-hydroxypropanoic acid). Conditions are recorded in `reaction`: `CH₂Cl₂`, room temperature, 24 h. The recorded outcome notes *multigram scalability*, foreshadowing why the team chose this route over alternatives.

### Step 2 — **Failed attempt**: 13 reagents, no reaction

`action: failed_attempt` &middot; **valid: false** &middot; `failure_mode: no_reaction`

This is the step the dataset is built around. The Sci-Evo schema demands that failures are first-class data, not erased from the published record. The trace dutifully encodes the entire grid the authors tried:

> *"To attempt the dimerisation of 3 at room temperature or elevated temperatures in various solvents with a range of bases and acidic additives, expecting to find conditions that promote the domino reaction."*

The `reaction.reagents` array lists thirteen tried combinations:

```
K₂CO₃, Na₂CO₃, Cs₂CO₃, TBAF, Et₃N, DBU, NaH, DABCO, NaHMDS, KOtBu,
Zn(OTf)₂, Amberlyst 15, p-TsOH
```

Outcome recorded verbatim from the paper:

> *"… gave no detectable conversion of 3 to lappaceolides (see the SI)."*

This is exactly the kind of failure record that **never appears in USPTO/ORD-style "successful reactions" datasets**. A model trained on success-only data will repeat these mistakes. A model trained including this step will recognise that, for this substrate class, the standard base- and Brønsted-acid-catalysed dimerisation is a dead end.

### Step 3 — **Revision**: borrow Lawrence's conditions

`action: revision` &middot; `revises_step_id: 2` &middot; valid: true (partial) &middot; yield: 5 %, dr 54:46

> *"To implement Lawrence-group conditions (20 mol % K₂CO₃, 1,2-DCE, 70 °C, 12 h), expecting to observe some conversion to lappaceolides."*

This is a textbook recovery step: a *citation* (the Lawrence group's prior work on (-)-angiopterlactone B with a structurally analogous Michael / oxa-Michael cascade) **is encoded as the `references` field**, and the step's `revises_step_id` points back to step 2 so a route-planner can read this trace as the data path *failed-step → cited-prior-art → recovery*. The yield is poor (5 %) and stereo-selectivity is essentially nil (54:46), but **it's the first sign of life** — the cascade does run, the kinetic regime is different from what step 2 explored.

### Step 4 — Forward reaction: optimised conditions

`action: forward_reaction` &middot; valid: true &middot; yield: 30 %, dr 3:2

> *"To conduct extensive optimisation, focusing on base and solvent, and specifically using 10.0 equiv of Cs₂CO₃ in 1,2-DCE at 85 °C for 4 h, expecting to achieve higher conversion and yield."*

Note the stoichiometry is now a structured dict — `stoichiometry: { "Cs₂CO₃": "10.0 equiv" }` — a Sci-Evo schema fix dating from the pilot bug-list (issue #2 in the bug-fix table of the technical report).

The `outcome.observation` carries the **kinetic-control insight** verbatim — *"… the yields, conversions, and diastereomeric ratios of 1 and 2 were however found to vary (8–30 %, 75–100 %, dr 3:2–2:3) from batch to batch. Reaction times longer than 4 h were found to result in lower yields, indicating that 1 and 2 are unstable at elevated temperatures under the reaction conditions."*

That single quote is the lesson a model needs: **the dimerisation is reversible at elevated temperature, so longer time is worse, not better**. Without the `evidence.text_span` anchoring this observation to the source paper it would be unverifiable. With it, the dataset is auditable.

### Step 5 — Characterisation

`action: characterization` &middot; valid: true

The standard endgame — eluent screening for chromatography, ¹H/¹³C-NMR comparison to authentic Ragasa-isolated material, single-crystal X-ray of the co-crystal of A and B. The trace records both the *purification problem* (typical EtOAc/hexane and DCM/MeOH systems failed to separate residual siphonodin from product, requiring a tertiary Et₂O–MeCN–DCM 1:1:3 system) **and** the validation that the synthetic spectra matched the natural sample.

---

## 4. Validation block

```json
"validation": {
  "characterization": ["1H NMR", "X-ray crystallography", "comparison_to_authentic"],
  "metrics": {
    "Overall Yield":        { "value": 30, "unit": "%", "interpretation": "for the dimerisation step" },
    "Longest Linear Steps": { "value": 2,  "unit": "steps", "interpretation": "from commercial DHA" },
    "Total Steps":          { "value": 2,  "unit": "steps" },
    "Failed Attempts Count":{ "value": 1,  "unit": "attempts" }
  },
  "significance": "First total synthesis of lappaceolides A and B. Provides further support for the biosynthetic hypothesis that lappaceolides are dimers of siphonodin."
}
```

---

## 5. Why this trace is useful

A model consuming this trace gets, at minimum, three actionable training signals:

1. **Strategic bond analysis.** A vinylogous-Michael / oxa-Michael **domino** is the strategic move that compresses two retro arrows into a single forward step. The pattern generalises to dimer-class natural products.
2. **A typed map of failure space** for the dimerisation: a list of thirteen common bases and Brønsted acids that *do not* drive this cascade, with `failure_mode: no_reaction`. Precisely the kind of *exclusion knowledge* a route-planner needs.
3. **A kinetic insight** — products are unstable at the operating temperature, so longer time decreases yield. The `evidence.text_span` anchors this back to verbatim paper text so a downstream auditor can confirm the model isn't hallucinating.

All of this is **machine-readable JSON conforming to a single schema**, with full provenance back to the originating MinerU `batch_id`, the OpenRouter model id used at each stage, and the OA license of the source paper.

---

## 6. Provenance footer

```yaml
trace_id:         TS-PMC12519463
schema_version:   1.0.0
license:          CC-BY-4.0
source.doi:       10.1021/acs.orglett.5c02445
source.license:   cc by
mineru.method:    MinerU API (cloud)
mineru.batch_id:  de091bba-0e1f-407c-a171-c2fdc6a2a410
extraction:       image_smiles=google/gemini-2.5-flash, trace=google/gemini-2.5-flash
validators:       RDKit canonicalisation, PubChem name lookup
human_reviewed:   false
```
