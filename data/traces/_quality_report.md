# Sci-Evo Total-Synthesis Pilot — Quality Report

## Overall metrics

| metric | value |
|---|---|
| n_traces | 237 |
| avg_steps | 20.093 |
| median_steps | 19 |
| max_steps | 78 |
| total_failed_attempts | 966 |
| traces_with_failed_attempts | 199 |
| fraction_with_failed_attempts | 0.840 |
| total_revisions | 566 |
| target_smiles_filled_rate | 0.869 |
| smiles_total | 10899 |
| smiles_parseable | 7764 |
| smiles_parseable_rate | 0.712 |
| convergent_traces | 149 |
| evidence_coverage_avg | 0.993 |

## JSON Schema validation (Draft 2020-12)

- pass: **214/237** (90.3%)
- fail: 23

First failures:

- `PMC11186323.trace.json` (1 errors)
    - `execution_trace/18/outcome/yield_percent`: '34-85' is not of type 'number', 'null'
- `PMC11520894.trace.json` (1 errors)
    - `_provenance/source/authors`: None is not of type 'string'
- `PMC11686507.trace.json` (1 errors)
    - `execution_trace/5/outcome/yield_percent`: 'low' is not of type 'number', 'null'
- `PMC11829995.trace.json` (4 errors)
    - `target/success_criteria/yield_target_percent`: None is not of type 'number', 'string'
    - `target/success_criteria/scale_target`: None is not of type 'string'
    - `validation/metrics/Overall Yield/value`: None is not of type 'string', 'number'
- `PMC11833443.trace.json` (6 errors)
    - `execution_trace/3`: 'thought' is a required property
    - `execution_trace/4`: 'thought' is a required property
    - `execution_trace/7`: 'thought' is a required property

## Top traces selected for technical report

| rank | trace | target | journal/year | steps | failed | rev | parseable | score |
|---|---|---|---|---|---|---|---|---|
| 1 | `TS-PMC12886951` | Indole | Nat Commun 2026 | 61 | 23 | 9 | 0.89 | 124.95 |
| 2 | `TS-PMC11403583` | (+)-dihydromaritidine | RSC Adv 2024 | 48 | 10 | 25 | 0.68 | 111.92 |
| 3 | `TS-PMC12569679` | N_a-methyl-16-epipericyclivine | JACS Au 2025 | 42 | 16 | 4 | 0.94 | 99.7 |
| 4 | `TS-PMC12703658` | (+)-Ineleganolide | J Am Chem Soc 2025 | 27 | 15 | 5 | 0.70 | 93.5 |
| 5 | `TS-PMC12164070` | UCS1025A | Chem Sci 2025 | 39 | 14 | 6 | 1.00 | 92.0 |
| 6 | `TS-PMC11790057` | glauconic acid | Chem Sci 2025 | 35 | 12 | 7 | 0.67 | 89.86 |
| 7 | `TS-PMC11882921` | (-)-oleuropeic acid | Nat Commun 2025 | 59 | 15 | 2 | 0.97 | 88.37 |
| 8 | `TS-PMC13000223` | pentalenolactone D | Nat Commun 2026 | 27 | 11 | 3 | 1.00 | 87.5 |
| 9 | `TS-PMC7618468` | Haedoxan A | J Am Chem Soc 2025 | 44 | 13 | 5 | 0.41 | 86.57 |
| 10 | `TS-PMC11405768` | phosphorylated zwitterionic hexasaccharide | Commun Chem 2024 | 41 | 13 | 5 | 0.18 | 85.41 |

## Distributions

### Steps per trace

| steps | count |
|---|---|
| 2 | 4 |
| 3 | 6 |
| 4 | 1 |
| 5 | 4 |
| 6 | 8 |
| 7 | 3 |
| 8 | 4 |
| 9 | 7 |
| 10 | 8 |
| 11 | 9 |
| 12 | 9 |
| 13 | 9 |
| 14 | 9 |
| 15 | 9 |
| 16 | 6 |
| 17 | 3 |
| 18 | 13 |
| 19 | 13 |
| 20 | 11 |
| 21 | 7 |
| 22 | 8 |
| 23 | 9 |
| 24 | 11 |
| 25 | 7 |
| 26 | 9 |
| 27 | 11 |
| 28 | 2 |
| 29 | 4 |
| 31 | 1 |
| 32 | 2 |
| 33 | 3 |
| 34 | 5 |
| 35 | 3 |
| 36 | 2 |
| 38 | 1 |
| 39 | 2 |
| 41 | 2 |
| 42 | 1 |
| 44 | 2 |
| 45 | 2 |
| 47 | 1 |
| 48 | 1 |
| 53 | 1 |
| 58 | 1 |
| 59 | 1 |
| 61 | 1 |
| 78 | 1 |

### Failed attempts per trace

| failed_attempts | count |
|---|---|
| 0 | 38 |
| 1 | 34 |
| 2 | 27 |
| 3 | 33 |
| 4 | 22 |
| 5 | 16 |
| 6 | 12 |
| 7 | 15 |
| 8 | 10 |
| 9 | 5 |
| 10 | 7 |
| 11 | 5 |
| 12 | 3 |
| 13 | 5 |
| 14 | 1 |
| 15 | 2 |
| 16 | 1 |
| 23 | 1 |

### Natural-product class distribution

| class | count |
|---|---|
| unspecified | 24 |
| alkaloid | 10 |
| indole alkaloid | 9 |
| diterpenoid | 8 |
| terpenoid | 7 |
| polyketide | 5 |
| Alkaloid | 4 |
| diterpene | 4 |
| peptide | 4 |
| monoterpene indole alkaloid | 3 |
| sesquiterpenoid | 3 |
| Lycopodium alkaloid | 3 |
| meroterpenoid | 3 |
| steroidal alkaloid | 3 |
| norcembranoid | 2 |
| sactipeptide | 2 |
| macrolide | 2 |
| Daphniphyllum alkaloid | 2 |
| macrocyclic depsipeptide | 2 |
| tetraterpenoid | 2 |
| sesquiterpene | 2 |
| Terpenoid | 2 |
| isocoumarin | 2 |
| cyclopeptide | 2 |
| Amaryllidaceae alkaloid | 1 |
| maleidride | 1 |
| furofuran lignan | 1 |
| oligosaccharide | 1 |
| Stemona alkaloid | 1 |
| sphingolipid | 1 |
| vitamin | 1 |
| sesquiterpene (hydro)quinone meroterpenoid | 1 |
| cardiac glycoside | 1 |
| aryltetralin lactone cyclolignan | 1 |
| Prostaglandin | 1 |
| Monoterpene Indole Alkaloids | 1 |
| sesteterpenoid | 1 |
| ganglioside | 1 |
| diterpene alkaloid | 1 |
| sphingoid base | 1 |
| guaiane-derived sesquiterpenoid | 1 |
| d-lactone | 1 |
| polycyclic polyprenylated acylphloroglucinol | 1 |
| limonoid | 1 |
| fatty acid lactones | 1 |
| grayanane diterpenoid | 1 |
| prostaglandin | 1 |
| Cyclic Tetrapeptide | 1 |
| Diterpenoid alkaloid | 1 |
| polysaccharide | 1 |
| diketopiperazine alkaloid dimer | 1 |
| bicoumarin | 1 |
| polycyclic xanthone | 1 |
| abietane diterpenoid | 1 |
| alpha-pyrone | 1 |
| piperidine alkaloid | 1 |
| Meroterpenoid dimer | 1 |
| Aspidosperma alkaloid | 1 |
| cembranoid | 1 |
| sorbicillinoid | 1 |
| indole diterpenoid | 1 |
| Sesquiterpenoid | 1 |
| pyrroloiminoquinone | 1 |
| indolosesquiterpene alkaloid | 1 |
| polyketides | 1 |
| aromatic polyketide | 1 |
| guaianolide sesquiterpenoid lactone | 1 |
| azaphilone | 1 |
| Ganoderma meroterpenoid | 1 |
| bisindole alkaloid | 1 |
| sesterterpenoid | 1 |
| pyridinium bisretinoid | 1 |
| polycyclic polyprenylated acylphloroglucinols | 1 |
| Daphniphyllum alkaloids | 1 |
| cyclic imine toxin | 1 |
| spirocyclic ortho-cyclohexadienone | 1 |
| Marine Bromotriterpenoid Polyether | 1 |
| guaiane-derived sesquiterpene | 1 |
| cadinane sesquiterpenoid | 1 |
| aromatic polycyclic polyketide glycoside | 1 |
| saponin | 1 |
| Amaryllidaceae alkaloids | 1 |
| lipodepsipeptide | 1 |
| guaianolide sesquiterpene lactone | 1 |
| guaianolide sesquiterpene | 1 |
| Furanolide | 1 |
| carbazole alkaloid | 1 |
| homoadamantane polycyclic polyprenylated acylphloroglucinols (PPAPs) | 1 |
| terpene trilactone | 1 |
| cyclic lipopeptide | 1 |
| noncanonical cyclic peptide | 1 |
| polycyclic polyprenylated acylphloroglucinol (PPAP) | 1 |
| tropolone-peptide hybrid | 1 |
| neolignan | 1 |
| sesquiterpenoid lactone | 1 |
| cyclic bis(bibenzyl) | 1 |
| oligostilbene | 1 |
| carbasugar | 1 |
| aromatic alkaloid | 1 |
| oleanane-type triterpene saponin | 1 |
| disesquiterpenoid lactone | 1 |
| polycyclic ether | 1 |
| prenylated indole alkaloid | 1 |
| alpha-pyrone antibiotic | 1 |
| macrocyclic alkaloid | 1 |
| pyrroloiminoquinone alkaloid | 1 |
| polycyclic sesquiterpenoid alkaloid | 1 |
| monoterpenoid pyrano-[3,2-a]-carbazole alkaloid | 1 |
| Monoterpene indole alkaloid | 1 |
| marine alkaloid | 1 |
| Strychnos alkaloid | 1 |
| benzoquinone meroterpenoid | 1 |
| diamondoid | 1 |
| bisretinoid | 1 |
| nucleoside | 1 |
| phthalide | 1 |
| merosesquiterpene | 1 |
| Securinega alkaloid | 1 |
| taxane diterpenoid | 1 |
| cyclic prodiginine | 1 |
| C-glycosides | 1 |
| benzofuran-derivatized natural product | 1 |
| angucycline polyketide | 1 |
| Pyrroloazocine Alkaloids | 1 |
| diarylheptanoid | 1 |
| Ryania diterpenoid | 1 |
| peptidic siderophore | 1 |
| bis-indole alkaloid | 1 |
| sesquineolignan | 1 |
| macrolide antibiotic | 1 |
| polyhydroxylated macrolide | 1 |
| dihydronaphthyridine core | 1 |
| Veratrum alkaloid | 1 |
| cembrane diterpenoid | 1 |
| acorane-type terpenoid | 1 |
| indoline alkaloid | 1 |
| aryltetralin lignan | 1 |
| monoterpene lactones | 1 |
| Taxane | 1 |
| lycopodium alkaloid | 1 |
| indole diketopiperazine alkaloid | 1 |
| Illicium sesquiterpene | 1 |
| monoterpenoid indole alkaloid | 1 |
| hexacyclic quinazolinone alkaloid | 1 |
| Carotenoid derivative | 1 |
| isochromene derivative | 1 |
| pharmaceutically active compound | 1 |
| bis-tetrahydroisoquinoline alkaloid | 1 |
| N-acyl tyrosine | 1 |
| polyamine | 1 |
| miscellaneous | 1 |
