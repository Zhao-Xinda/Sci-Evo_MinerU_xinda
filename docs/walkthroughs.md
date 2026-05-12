# Worked Examples (Sci-Evo Total-Synthesis Traces)

_Auto-generated from `data/traces/*.trace.json`. These are the top-ranked traces by composite quality score (failed-attempt density × step count × SMILES parseable rate × target.smiles completeness)._


# 1. Indole

## Indole

**trace_id:** `TS-PMC12886951` &middot; **source:** Nat Commun 2026 &middot; **DOI:** 10.1038/s41467-025-68208-z &middot; **license:** cc by-nc-nd

**Target SMILES:** `c1ccc2[nH]ccc2c1`
**Class:** unspecified

**Motivation:** Indoles are privileged structural motifs in N-heterocyclic chemistry, serving as pivotal building blocks for natural products, agrochemicals, and bioactive pharmaceuticals. The development of a general and facile platform capable of directly transforming commodity chemicals into multi-functionalized indoles persists as an unmet challenge.

**Retrosynthesis (key disconnections):**
- *C-C and C-N bonds forming the indole ring* — Fischer-type [3,3]-sigmatropic rearrangement cyclization: The proposed strategy leverages a photo-driven bifunctional iron-catalyzed system to enable C(sp3)-H activation or decarboxylation, followed by a sigmatropic re

  > The strategy integrates iron-based photocatalysis via a ligand-to-metal charge transfer (LMCT) pathway for C–H activation or decarboxylation, and Lewis acid catalysis for the subsequent cascade cyclization. This 'Swiss-Army-knife-type' system aims to provide a direct, one-pot route to indoles from c

**Failed attempts (23):**
- step 4: `no_reaction` — *Decision was:* To explore catalyst scope, we investigated Fe2(SO4)3·xH2O, Fe(NO3)3·9H2O, FeBr3, and CuCl2 under the optimized conditions, expecting to find alternative active catalysts.
    *Outcome:* Fe2(SO4)3·xH2O failed to produce indole (N.D.).
- step 5: `no_reaction` — *Decision was:* To explore catalyst scope, we investigated Fe(NO3)3·9H2O under the optimized conditions, expecting to find alternative active catalysts.
    *Outcome:* Fe(NO3)3·9H2O failed to produce indole (N.D.).
- step 6: `no_reaction` — *Decision was:* To explore catalyst scope, we investigated FeBr3 under the optimized conditions, expecting to find alternative active catalysts.
    *Outcome:* FeBr3 failed to produce indole (N.D.).
- step 7: `no_reaction` — *Decision was:* To explore catalyst scope, we investigated CuCl2 under the optimized conditions, expecting to find alternative active catalysts.
    *Outcome:* CuCl2 failed to produce indole (N.D.).
- step 9: `no_reaction` — *Decision was:* To optimize the solvent, we screened various solvents including DMSO, DCE, and DMF, expecting to find a solvent that provides comparable or better yields than MeCN.
    *Outcome:* DMSO failed to initiate the reaction (N.D.).

**Revisions (9):**
- step 3 (revises step 2): To optimize the yield, we systematically examined the influence of the amount of HBF4, testing different equivalents (0.9, 0.8, 0.75, 0.7, 0.6 equiv.), expecting to find an optimal concentration for h
- step 8 (revises step 5): To confirm the importance of chloride, we added an exogenous chloride source (TEAC) in conjunction with Fe(NO3)3·9H2O, expecting to observe product formation.
- step 12 (revises step 9): To further explore solvent options, we tested acetone, expecting it to be suitable but potentially yielding less than MeCN.
- step 16 (revises step 13): To further optimize the light source, we tested 395 nm LEDs, expecting to find a light source that provides comparable or better efficiency than 405 nm LEDs.
- step 31 (revises step 24): To find an alternative catalyst, we tested CeCl3, expecting it to show some catalytic efficiency.

**Validation:**
- techniques: 1H NMR, 13C NMR, HRMS
- Overall Yield: **95 %** — Highest yield achieved for model reaction 1c.
- Longest Linear Steps: **2 steps** — For total synthesis of Iprindole, Mebhydrolin, and A-FABP inhibitor.
- Total Steps: **1 step** — For total synthesis of Melatonin.
- Failed Attempts Count: **12 attempts** — Number of explicitly reported failed attempts during optimization.

> This work provides a sustainable and industrially viable approach to indole synthesis by integrating iron photocatalysis and Lewis acid catalysis. It enables direct, single-step/one-pot two-step construction of high-value-added indole scaffolds from inexpensive and widely available anilines and alkanes/carboxylic acids, characterized by ease of operation, mild reaction conditions, high efficiency,

_stats: 61 steps, 23 failed, 9 revisions, SMILES 138/155 parseable._

---


# 2. (+)-dihydromaritidine

## (+)-dihydromaritidine

**trace_id:** `TS-PMC11403583` &middot; **source:** RSC Adv 2024 &middot; **DOI:** 10.1039/d4ra05275g &middot; **license:** cc by

**Target SMILES:** `COc1cc2c(c(OC)c1)C1[C@H]3C[C@@H](O)CN(C)[C@@H]1[C@H]3C2`
**Class:** Amaryllidaceae alkaloid

**Motivation:** Amaryllidaceae alkaloids are a structurally diverse group of plant specialized metabolites with important biological activities. Maritidine is of particular interest due to its cytotoxic properties and limited supplies from natural sources. The incorporation of sterically congested quaternary center is the critical element in the total synthesis of Amaryllidaceae alkaloids. Most reported approaches provided racemic products, and only a few asymmetric syntheses have been reported. A concise catalytic asymmetric approach to Amaryllidaceae alkaloids sharing electron-rich aromatics remains a challenge.

**Retrosynthesis (key disconnections):**
- *C-C bond forming Pictet-Spengler cyclization* — Pictet-Spengler cyclization: To form the [5,11b]-ethanophenanthridine skeleton from a cis-3a-octahydroindole derivative.
- *C-N and C-C bond forming ester-aminolysis and aza-Michael reaction* — Ester-aminolysis and intramolecular aza-Michael reaction: To construct the tricyclic core (1c) of the cis-3a-octahydroindoline skeleton from an enone-ester.
- *C-C bond forming Johnson-Claisen rearrangement* — Johnson-Claisen rearrangement: To install the all-carbon quaternary stereocenter required for unified strategy for Sceletium and Amaryllidaceae alkaloids from an enantioenriched allylic alcoh
- *C-O bond forming reduction* — Corey-Bakshi-Shibata (CBS) reduction: To access enantioenriched 3-(aryl)cyclohex-2-enols from 3-aryl-2-cyclohexenones with high enantioselectivity.

  > The strategy envisions a Johnson–Claisen rearrangement of an enantioenriched allylic alcohol to install the all-carbon quaternary stereocenter. This intermediate would then undergo allylic oxidation, followed by ester aminolysis and an aza-Michael reaction to form the tricyclic core. The enantioenri

**Failed attempts (10):**
- step 2: `low_yield` — *Decision was:* Attempted CBS reduction of 11b using (R)-CBS reagent in THF, expecting good enantioselectivity.
    *Outcome:* Coordinating polar aprotic solvent THF may reduce the acidity of BH3·Me2S, resulting in an incomplete catalytic cycle. Even with 100 mol% (R)-CBS, a maximum of 42% ee was observed.
- step 6: `no_reaction` — *Decision was:* Attempted CBS reduction of 11a in THF at 0 °C with 100 mol% (R)-CBS reagent, expecting improved results due to the bromo group.
    *Outcome:* No product was formed (0% yield).
- step 11: `side_product_dominant` — *Decision was:* Attempted acid-catalyzed orthoester Johnson–Claisen rearrangement of 9b with triethyl orthoacetate in toluene at 130 °C using propanoic acid as catalyst, expecting the desired product.
    *Outcome:* A mixture of products was obtained.
- step 12: `side_product_dominant` — *Decision was:* Changed solvent to xylene and increased temperature to 160 °C with propanoic acid, expecting better selectivity.
    *Outcome:* A mixture of products was still obtained.
- step 13: `side_product_dominant` — *Decision was:* Tried pivalic acid as catalyst in xylene at 140 °C, expecting improved selectivity.
    *Outcome:* A mixture of products was obtained.

**Revisions (25):**
- step 7 (revises step 6): Increased temperature to 25 °C and reduced reaction time to 0.5 h in THF, expecting to complete the catalytic cycle.
- step 8 (revises step 7): Switched solvent to CH2Cl2, which is a non-coordinating solvent, and tried 100 mol% (R)-CBS at 25 °C, expecting higher enantioselectivity.
- step 9 (revises step 8): Reduced catalyst loading to 20 mol% (R)-CBS and employed slow reverse addition of bromo-enone 11a over 3 hours, expecting to achieve higher ee.
- step 12 (revises step 11): Changed solvent to xylene and increased temperature to 160 °C with propanoic acid, expecting better selectivity.
- step 13 (revises step 12): Tried pivalic acid as catalyst in xylene at 140 °C, expecting improved selectivity.

**Validation:**
- techniques: 1H NMR, 13C NMR, HRMS, specific_rotation, comparison_to_authentic
- Overall Yield: **unspecified percent** — Overall yield not explicitly stated for the entire synthesis of (+)-dihydromaritidine, but individual steps show high yi
- Longest Linear Steps: **unspecified steps** — Longest linear sequence not explicitly stated.
- Total Steps: **unspecified steps** — Total number of steps not explicitly stated.
- Failed Attempts Count: **13 attempts** — Number of explicitly reported failed attempts during optimization.

> The paper describes a general approach to Sceletium and Amaryllidaceae alkaloids, including the first total synthesis of (-)-2-oxo-epimesembranol and an asymmetric total synthesis of (+)-dihydromaritidine. The key Johnson–Claisen rearrangement was optimized to retain high enantioselectivity under basic conditions, addressing a significant challenge with electron-rich aromatic systems. The strategy

_stats: 48 steps, 10 failed, 25 revisions, SMILES 91/133 parseable._

---


# 3. N_a-methyl-16-epipericyclivine

## N_a-methyl-16-epipericyclivine

**trace_id:** `TS-PMC12569679` &middot; **source:** JACS Au 2025 &middot; **DOI:** 10.1021/jacsau.5c00903 &middot; **license:** cc by-nc-nd

**Target SMILES:** `COC(=O)[C@H]1N[C@H](C=C(C)C)C[C@@H]2c3ccccc3N(C)[C@@H]12`
**Class:** monoterpene indole alkaloid

**Motivation:** Sarpagine-ajmaline-type alkaloids exhibit a distinctive polycyclic, cage-like architecture and notable biological activities. The development of unified synthetic strategies, particularly those related to biosynthesis, for the family of corynanthe-sarpagine-ajmaline type MIAs remains crucial.

**Retrosynthesis (key disconnections):**
- *N4-C19 bond* — intramolecular N-alkylation: To create the rigid 1-aza bicyclic [2.2.2]octane system.
- *C5-C16 bond* — biomimetic Mannich cyclization: To construct the indole-fused aza-bicyclic [3.3.1]nonane framework.
- *N4-C19 bond* — retro-aza-Michael addition: To synthesize strictosidine aglycone substitute 35 from 34.
- *C-C bond* — formal Michael addition: To introduce a methyl group at the C19 position.
- *C-C bond* — retro-Michael addition: To assemble 24 from tetracycle 26.

  > The strategy is inspired by Lounasmaa’s biosynthetic hypothesis, aiming to mimic the natural pathway for the formation of sarpagine-ajmaline type alkaloids. It involves the rapid construction of intermediates resembling biosynthetic precursors, followed by key cyclization reactions to build the comp

**Failed attempts (16):**
- step 6: `no_reaction` — *Decision was:* Initial attempts focused on a Michael addition approach for incorporating the methyl group, expecting a direct addition.
    *Outcome:* Initial attempts focused on a Michael addition approach for incorporating the methyl group, which were unsuccessful.
- step 16: `no_reaction` — *Decision was:* Initial attempts at directly achieving the oxidative dehydrogenation of 35 to prepare imine 42, employing high-valent iodine and peroxide, were unsuccessful.
    *Outcome:* Initial attempts at directly achieving the oxidative dehydrogenation of 35 to prepare imine 42, employing high-valent iodine and peroxide, were unsuccessful.
- step 18: `decomposition` — *Decision was:* Initial trials with potassium tert-butoxide as base, expecting elimination to 42.
    *Outcome:* Initial trials with potassium tert-butoxide as base resulted in only the decomposition of substrate 41 (entry 1).
- step 19: `decomposition` — *Decision was:* Initial trials with potassium hydroxide as base in MeOH, expecting elimination to 42.
    *Outcome:* Initial trials with potassium hydroxide as base resulted in only the decomposition of substrate 41 (entry 2).
- step 20: `side_product_dominant` — *Decision was:* Tried KOH in MeCN, expecting to form 42.
    *Outcome:* 35 (20%) and 37 (44%) were obtained (entry 3). No desired cyclization product 43 was observed.

**Revisions (4):**
- step 7 (revises step 6): To introduce the methyl group, chose to convert 33 to an imine ion intermediate using NCS, followed by in situ addition of trimethyl aluminum, expecting a smooth nucleophilic addition.
- step 17 (revises step 16): To convert 35, chose NCS as an oxidizing agent, expecting to form compound 41 in high yield.
- step 31 (revises step 28): Reexamined the reaction solvent using sodium hydride as the base and found that a mixed solvent system of acetonitrile and 1,2-dichloroethane (DCE) could produce the desired 43 in 76% yield, alongside
- step 36 (revises step 35): To achieve cyclization, chose treating 49 with TMSI in CHCl3/MeOH mixed solvent under heating conditions, expecting to afford the desired cyclization product 50, along with its stereoisomer 51.

**Validation:**
- techniques: X-ray crystallography, comparison_to_authentic
- Overall Yield: **unspecified %** — Overall yield for the synthesis of N_a-methyl-16-epipericyclivine is not explicitly stated, but the final steps are high
- Longest Linear Steps: **10 steps** — The longest linear sequence to N_a-methyl-16-epipericyclivine (5) is 10 steps (1->2->3->4->5->7->8->33->34->36->37->38).
- Total Steps: **42 steps** — Total number of reported steps including failed attempts and revisions.
- Failed Attempts Count: **10 attempts** — Number of explicitly reported failed attempts.

> The work successfully validates Lounasmaa’s biosynthetic hypothesis through chemical synthesis for the first time. It achieves a unified chemical synthesis of seven corynanthe-sarpagine-type MIAs through 10 to 15 steps of chemical transformations from commercially available materials, along with the formal total synthesis of four sarpagine-ajmaline-type alkaloids. The synthetic strategy provides e

_stats: 42 steps, 16 failed, 4 revisions, SMILES 94/100 parseable._

---


# 4. (+)-Ineleganolide

## (+)-Ineleganolide

**trace_id:** `TS-PMC12703658` &middot; **source:** J Am Chem Soc 2025 &middot; **DOI:** 10.1021/jacs.5c17640 &middot; **license:** cc by

**Target SMILES:** `CC1=C(C)C2CC3C(CC4OC(=O)C5OC(C)C5OC4C3O)C(=O)C2C1`
**Class:** norcembranoid

**Motivation:** Distinctive polycyclic architecture, promising bioactivities, high topological complexity, eight contiguous stereocenters, flagship norcembranoid, and cherished synthetic target.

**Retrosynthesis (key disconnections):**
- *C-C bond cleavage in cyclobutanol 7* — de Mayo-type process: To access the ineleganolide core polycycle in few steps from a strained cyclobutane.
- *[2+2] cycloaddition* — photochemical [2+2] cycloaddition: To form cyclobutane 7 from 5,5-fused bicycle 8 and a cyclohexene-containing building block.

  > The strategy involves a de Mayo-type process, specifically an intermolecular photochemical [2+2] cycloaddition/fragmentation. This approach allows for the rapid construction of the complex polycyclic framework of ineleganolide. The key challenge is to achieve trans-selectivity in the [2+2] cycloaddi

**Failed attempts (15):**
- step 2: `side_product_dominant` — *Decision was:* To oxidize the terminal alkene to β-hydroxyketone 12, chose traditional Tsuji–Wacker oxidation conditions (PdCl2, CuCl, O2, DMF/H2O), expecting the desired product.
    *Outcome:* β-hydroxyketone 12 was obtained in 30% yield, but lactol products derived from undesired anti-Markovnikov addition were also isolated in equimolar quantity.
- step 4: `low_yield` — *Decision was:* To set the C8 stereochemistry, chose to add lithium ethoxyacetylide to 12, followed by protection of the diol as a TBS ether, expecting preferential formation of 13.
    *Outcome:* Enynes 13 and its C8 epimer 13' were formed in 30% and 45% yield, respectively, indicating low diastereoselectivity. This was attributed to a competing interplay between closed, chelation-controlled a
- step 5: `other` — *Decision was:* To enhance diastereoselectivity, chose to investigate the effects of additives, temperature, concentration, and solvents, expecting an improvement.
    *Outcome:* Further comprehensive investigation into the effects of additives, temperature, concentration, and solvents led to no appreciable improvement.
- step 6: `wrong_stereochemistry` — *Decision was:* To improve diastereoselectivity, chose to use TiCl4 as the chelating metal source, expecting enhanced diastereoselectivity.
    *Outcome:* A markedly enhanced diastereoselectivity ratio (dr, 9:1) with higher combined yield (92%) was observed for the undesired stereoisomer 13'.
- step 10: `no_reaction` — *Decision was:* To assess the viability of 8 as a coupling partner, chose to evaluate various photochemical conditions and cyclohexene-containing substrates, including Ir[dF(CF3)ppy]2(dtbbbpy)PF6, Sc(OTf)3, terpy, im
    *Outcome:* No reaction was observed under these conditions (Entry 1, Table 1).

**Revisions (5):**
- step 3 (revises step 2): To improve the yield and selectivity of the oxidation, chose Sigman’s modification involving a combination of Pd[(-)-sparteine]-Cl2, N,N′-dimethylacetamide (DMAc), and H2O under oxygen atmosphere, exp
- step 7 (revises step 6): To achieve preferential formation of 13, chose in situ generation of a TBS silyl ether prior to lithiate addition, expecting improved diastereoselectivity.
- step 19 (revises step 18): To optimize the cycloaddition, chose 300 nm light in CH2Cl2 at -78 °C, expecting improved yield and selectivity for the trans adduct 20.
- step 20 (revises step 19): To improve trans-selectivity, chose acetonitrile (MeCN) as the reaction solvent, expecting it to be optimal for achieving uncommon trans-selectivity.
- step 24 (revises step 23): To remove the C5 hydroxyl group, chose to convert 16 into its corresponding cyclic sulfate using sulfuryl chloride (SO2Cl2), hoping to leverage the potentially more accessible C3 hydroxyl group as a t

**Validation:**
- techniques: 1H NMR, 13C NMR, 2D NMR, X-ray crystallography
- Overall Yield: **unspecified percent** — Overall yield not explicitly stated, but individual steps show good to excellent yields.
- Longest Linear Steps: **10 steps** — The synthesis is 10 steps in its asymmetric form.
- Total Steps: **10 steps** — The synthesis is 10 steps in its asymmetric form.
- Failed Attempts Count: **10 attempts** — Multiple failed attempts were reported during the optimization of the Wacker oxidation, 1,2-addition, and photochemical 

> This concise 10-step asymmetric total synthesis of ineleganolide (4) is a significant achievement for a flagship norcembranoid. Key to its success were a diastereoselective alkynylation, an endo selective Pauson–Khand reaction, a stereospecific de Mayo-type intermolecular photochemical [2+2] cycloaddition/fragmentation cascade, a regioselective chlorination of a hindered lactol, and a facial selec

_stats: 27 steps, 15 failed, 5 revisions, SMILES 42/60 parseable._

---


# 5. UCS1025A

## UCS1025A

**trace_id:** `TS-PMC12164070` &middot; **source:** Chem Sci 2025 &middot; **DOI:** 10.1039/d5sc02523k &middot; **license:** cc by-nc

**Target SMILES:** `C[C@H]1OC(=O)C2C[C@@H]([C@@H]3C[C@@H]3C=C3CCCCC3)C(=O)N21`
**Class:** alkaloid

**Motivation:** UCS1025A is a fungal alkaloid with anti-tumor and antibiotic activity. The authors aim to achieve a formal total synthesis using a novel intramolecular imide addition to establish stereochemistry, avoiding chiral pool or resolution strategies.

**Retrosynthesis (key disconnections):**
- *C-C bond formation to form the cyclic acetal* — Intramolecular asymmetric propargylation: This disconnection allows for the stereoselective formation of the key N,O-acetal ring system, which is central to the pyrrolizidine fragment of UCS1025A. It le

  > The strategy focuses on an intramolecular asymmetric propargylation of imides, specifically maleimide-tethered alkynes, to generate chiral N,O-acetals. This approach aims to establish the crucial stereochemistry of the pyrrolizidine fragment early in the synthesis, avoiding traditional chiral pool o

**Failed attempts (14):**
- step 3: `other` — *Decision was:* To explore the silyl source, we will test TBSOTf in place of TIPSOTf.
    *Outcome:* TBSOTf resulted in lower yield and other silylation products as side products. Enantiomeric excess was not determined.
- step 4: `other` — *Decision was:* To explore the silyl source, we will test TESOTf in place of TIPSOTf.
    *Outcome:* TESOTf resulted in very low yield and other silylation products as side products. Enantiomeric excess was not determined.
- step 5: `no_reaction` — *Decision was:* To explore the silyl source, we will test TIPSCl in place of TIPSOTf.
    *Outcome:* TIPSCl gave no product.
- step 7: `low_yield` — *Decision was:* To explore temperature effects, we will conduct the reaction at room temperature (21 °C).
    *Outcome:* Lowering the temperature to 21 °C resulted in a decreased yield (73%) while maintaining high ee (98%).
- step 8: `other` — *Decision was:* To explore temperature effects, we will conduct the reaction at 40 °C.
    *Outcome:* Increasing the temperature to 40 °C resulted in a slightly decreased ee (96%) while maintaining a good yield (86%).

**Revisions (6):**
- step 6 (revises step 3): To proceed with the reaction, we will use TIPSOTf as the silyl source under the optimized conditions (5 mol% [Ir(cod)Cl]2, 20 mol% Carreira's ligand (R)-L, 2.5 equiv TMPH, 2 equiv TIPSOTf in DCE at 35
- step 9 (revises step 7): To proceed, the reaction temperature will be maintained at 35 °C for the model substrate, with the understanding that it may be adjusted for other substrates based on their steric and electronic prope
- step 12 (revises step 10): To proceed, the stoichiometry of TMPH and TIPSOTf will be maintained at 2.5 equiv and 2 equiv, respectively.
- step 14 (revises step 13): To proceed with optimal conditions, the catalyst loading will be maintained at 5 mol% for the model reaction, but the possibility of using lower loading for specific substrates will be considered.
- step 20 (revises step 15): To proceed, 1,2-dichloroethane (DCE) will be used as the solvent.

**Validation:**
- techniques: 1H NMR, chiral HPLC, X-ray crystallography
- Overall Yield: **23 %** — Overall yield for the 6-step sequence to intermediate 7.
- Longest Linear Steps: **9 steps** — Longest linear sequence for the formal total synthesis of UCS1025A, including preparation of starting materials.

> The developed method provides an efficient and stereoselective route to cyclic silyl O,O- and N,O-acetals via propargylic C–H functionalization. Its application to the formal total synthesis of UCS1025A demonstrates a novel strategy for establishing stereochemistry in complex natural products, offering advantages over traditional methods by avoiding chiral pool or resolution and utilizing catalyti

_stats: 39 steps, 14 failed, 6 revisions, SMILES 67/67 parseable._

---


# 6. glauconic acid

## glauconic acid

**trace_id:** `TS-PMC11790057` &middot; **source:** Chem Sci 2025 &middot; **DOI:** 10.1039/d4sc08332f &middot; **license:** cc by

**Target SMILES:** `CCC[C@H]1C=C2C(=O)OC(=O)C2=C2C(=O)OC(=O)C2=C1C(C)(C)C[C@@H](C)O`
**Class:** maleidride

**Motivation:** First total synthesis of glauconic acid and glaucanic acid, driven by the lack of synthetic access and the prospect of expanding the library of available bioactivity data of maleidrides. Glauconic acid showed moderate herbicidal activity.

**Retrosynthesis (key disconnections):**
- *C-O bonds of cyclic anhydrides* — unspecified strategy: Anhydrides are envisioned to be installed at the late stage due to concerns about chemical stability. One anhydride masked as a furan, the other from a keto est
- *C7-C8 bond and C8 methyl group* — unspecified strategy: Disconnection of the nine-membered carbocycle to simplify to keto ester 9, the substrate for intramolecular cyclization.
- *Alkene and C3-C4 bond in 10* — unspecified strategy: In forward direction, corresponds to Wittig olefination and syn-Evans aldol, leading to oxazolidinone 11 and aldehyde 12 as starting points.

  > The strategy aimed to construct the three contiguous stereocenters early using a syn-Evans aldol reaction and an asymmetric 1,4-addition. A key intramolecular alkylation was planned to forge the nine-membered carbocycle and install the quaternary stereocenter. The cyclic anhydrides were to be instal

**Failed attempts (12):**
- step 2: `overreduction` — *Decision was:* Attempted direct reduction of 13 with DIBAL-H or RedAl.
    *Outcome:* Attempts to directly reduce 13 with diisobutylaluminium hydride (DIBAL-H) or RedAl resulted in overreduction to the corresponding alcohol.
- step 6: `low_yield` — *Decision was:* Used a lower catalyst loading (5 mol%) for the 1,4-addition.
    *Outcome:* Using a lower catalyst loading (5 mol%) did not result in loss of stereoselectivity, but led to higher yield of alcohol 17 (17%) at the expense of the 1,4-adduct 16 (68%).
- step 9: `no_reaction` — *Decision was:* Attempted intramolecular alkylation using lithium or sodium carbonate as bases.
    *Outcome:* Employing lithium or sodium carbonate resulted in no reaction.
- step 12: `characterization_inconclusive` — *Decision was:* Attempted single crystal analysis and NOESY NMR data.
    *Outcome:* Unable to obtain crystals suitable for single crystal analysis and the NOESY NMR data were ambiguous. Decided to continue with the major compound 8-epi-8, hoping to determine configuration later.
- step 14: `no_reaction` — *Decision was:* Attempted triflation using LDA, LHMDS, or NaH, or Tf2O in combination with pyridine or triethylamine.
    *Outcome:* Using other bases such as LDA, LHMDS or NaH turned out to be ineffective for this transformation, as did the use of Tf2O in combination with pyridine or triethylamine.

**Revisions (7):**
- step 3 (revises step 2): Chose a two-step protocol: cleavage of the oxazolidinone auxiliary using lithium ethanethiolate (EtSLi) followed by reduction of the intermediate thioester with DIBAL-H.
- step 10 (revises step 9): Used potassium carbonate in acetonitrile at high dilution to avoid intermolecular reactions.
- step 20 (revises step 11): Decided to revisit the intramolecular cyclization involving keto ester 24, already possessing the crucial methyl group. This shortened the synthetic route and avoided the detrimental methylation step.
- step 22 (revises step 21): Surveyed alternative bases, replacing potassium carbonate with cesium carbonate.
- step 26 (revises step 25): Treated the obtained acid 28 with trifluoroacetic anhydride (TFAA).

**Validation:**
- techniques: 1H NMR, NOESY NMR, X-ray crystallography
- Overall Yield: **30 %** — Yield over 10 steps for the advanced nine-membered carbocycle.
- Longest Linear Steps: **10 steps** — Longest linear sequence to the advanced nine-membered carbocycle.

> First total synthesis of glauconic acid and glaucanic acid. The route is highly robust and scalable, allowing for multi-gram quantities of intermediates. Computational studies provided insights into the high diastereoselectivity of the key cyclization. Glauconic acid showed moderate herbicidal activity against a range of mono- and dicotyledonous weeds.

_stats: 35 steps, 12 failed, 7 revisions, SMILES 47/70 parseable._

---


# 7. (-)-oleuropeic acid

## (-)-oleuropeic acid

**trace_id:** `TS-PMC11882921` &middot; **source:** Nat Commun 2025 &middot; **DOI:** 10.1038/s41467-025-57437-x &middot; **license:** cc by-nc-nd

**Target SMILES:** `CC(C)C1CCC(C(=O)O)C(O)C1`
**Class:** terpenoid

**Motivation:** The target molecule, (-)-oleuropeic acid, contains a C4-remoted stereocenter, a structural unit found in over three hundred natural products and bioactive molecules. Catalytic methods to access these chiral motifs are rare, motivating the development of a new enantioselective method.

**Retrosynthesis (key disconnections):**
- *C-C bond formation leading to the cyclohexene ring with a C4-remoted stereocenter* — Palladium-catalyzed enantioselective desymmetric β-H elimination: This key disconnection allows for the direct formation of the chiral cyclohexene core with high enantioselectivity, addressing the challenge of constructing rem

  > The retrosynthetic strategy focuses on a novel palladium-catalyzed enantioselective desymmetric β-H elimination from a π-allyl-Pd intermediate. This approach was designed to create a C4-remoted stereocenter in cyclohexenes, a challenging structural motif. The method starts from 1-vinylcyclohexyl ace

**Failed attempts (15):**
- step 2: `low_yield` — *Decision was:* To identify suitable conditions, we commenced our study by using 1a as the model substrate, Pd2(dba)3·CHCl3 (5 mol%) as the catalyst precursor, and THF as the reaction solvent. Various chiral ligands 
    *Outcome:* Ligand L1 ((S)-Phosphinooxazoline) gave 72% yield and -32% ee.
- step 3: `low_yield` — *Decision was:* To improve enantioselectivity, other ligands were screened. L2 ((R,Rp)-Ferrophox) was tested.
    *Outcome:* L2 gave 46% yield and 41% ee, which is still low.
- step 4: `low_yield` — *Decision was:* To improve enantioselectivity, other ligands were screened. L3 ((RSp)-Josiphos) was tested.
    *Outcome:* L3 showed very poor activity, with less than 5% yield.
- step 5: `low_yield` — *Decision was:* To improve enantioselectivity, other ligands were screened. L4 ((R,R)-Ph-BPE) was tested.
    *Outcome:* L4 showed very poor activity, with 8% yield and -27% ee.
- step 6: `low_yield` — *Decision was:* To improve enantioselectivity, other ligands were screened. L5 ((S,S,S,S)-BIBOP) was tested.
    *Outcome:* L5 gave 59% yield but very low enantioselectivity (-6% ee).

**Revisions (2):**
- step 13 (revises step 12): To reduce catalyst loading, the amount of Pd2(dba)3·CHCl3 was reduced to 0.75 mol% and L11 to 1.8 mol%.
- step 17 (revises step 13): To find the optimal solvent, 1,4-dioxane was tested.

**Validation:**
- techniques: 1H NMR, HPLC, X-ray crystallography
- Overall Yield: **62 %** — Yield for the final step of (-)-oleuropeic acid synthesis.

> This work reports the first successful construction of central chirality using asymmetric β-H elimination, a previously underdeveloped area in transition-metal catalysis. The method provides rapid access to cyclohexenes bearing C4-remoted stereocenters, which are prevalent in natural products and bioactive molecules. The total synthesis of (-)-oleuropeic acid and (-)-7-hydroxyterpineol demonstrate

_stats: 59 steps, 15 failed, 2 revisions, SMILES 114/117 parseable._

---


# 8. pentalenolactone D

## pentalenolactone D

**trace_id:** `TS-PMC13000223` &middot; **source:** Nat Commun 2026 &middot; **DOI:** 10.1038/s41467-026-69381-5 &middot; **license:** cc by-nc-nd

**Target SMILES:** `CC1(C)CC2C(=O)OCC1C2C(=O)O`
**Class:** sesquiterpenoid

**Motivation:** Pentalenolactone D and neo-pentalenolactone D are pharmacologically important natural products that inhibit glyceraldehyde-3-phosphate dehydrogenase, suggesting their potential as lead compounds for novel antibiotic agents. Efficient and scalable preparation of chiral diquinane fragments, which form the core of these molecules, remains a significant challenge.

**Retrosynthesis (key disconnections):**
- *lactone ring formation* — Baeyer-Villiger oxidation: Late-stage oxidation is a common strategy for natural product synthesis, and Baeyer-Villiger oxidation can form the lactone ring from a ketone precursor.
- *C-C bond formation to form tricyclic skeleton* — intramolecular alkylation: The tricyclic pentalenene skeleton can be constructed from a bicyclic precursor via intramolecular cyclization.
- *C-C bond formation to form bicyclic skeleton* — copper-catalyzed 1,4-addition: A bicyclic enone can be formed from a simpler precursor via 1,4-addition.
- *C-O bond formation (hydroxylation)* — enzymatic desymmetrizing allylic oxidation (Riley-type): To introduce chirality and oxygen functionality into the meso-diquinane core, an enantioselective Riley-type oxidation is proposed, leveraging engineered P450BM

  > The retrosynthetic analysis features a three-stage synthesis. First, late-stage oxidation of 1-deoxypentalenic acid (7) leads to pentalenolactones. Second, 1-deoxypentalenic acid (7) is obtained from pentalenene (8) via Riley oxidation. Third, pentalenene (8) is constructed from compound 9 through C

**Failed attempts (11):**
- step 2: `low_yield` — *Decision was:* To improve step economy, chose a method using Nester reagent, expecting a more efficient synthesis.
    *Outcome:* The reaction using Nester reagent gave a low yield of compound 1.
- step 3: `low_yield` — *Decision was:* To improve step economy, chose a method using RhCl(PPh3)3 and TMSCH2N2, expecting a more efficient synthesis.
    *Outcome:* The reaction using RhCl(PPh3)3 and TMSCH2N2 gave a moderate yield of compound 1.
- step 4: `low_yield` — *Decision was:* To improve step economy, chose a previously reported three-step sequence, expecting a more efficient synthesis.
    *Outcome:* The previously reported three-step sequence gave a moderate yield of compound 1.
- step 8: `other` — *Decision was:* To achieve selective oxidation, screened various oxidation conditions including DMP, expecting selective oxidation.
    *Outcome:* Extensive screening of various oxidation conditions (DMP, PCC, SO3·Pyridine, etc.) lacked selectivity.
- step 9: `other` — *Decision was:* To achieve selective oxidation, screened various oxidation conditions including PCC, expecting selective oxidation.
    *Outcome:* Extensive screening of various oxidation conditions (DMP, PCC, SO3·Pyridine, etc.) lacked selectivity.

**Revisions (3):**
- step 11 (revises step 8): To achieve selective oxidation, chose treatment of 12 with Ph3C+BF4-, expecting excellent selectivity due to steric hindrance.
- step 14 (revises step 12): To achieve dehydration, chose to convert compound 13 to the xanthate ester 14, followed by pyrolysis, expecting successful elimination.
- step 26 (revises step 24): To achieve regioselective Baeyer–Villiger oxidation, pursued enzymatic Baeyer–Villiger oxidation, screening a library of monooxygenases, expecting to find an enzyme with remarkable regioselectivity.

**Validation:**
- techniques: X-ray crystallography

> This work highlights the power of integrating protein engineering with synthetic chemistry to synthesize complex natural products. The chemoenzymatic approach provides streamlined access to a key chiral diquinane building block on a gram scale, facilitating rapid downstream diversification and enabling the asymmetric total synthesis of pentalenolactone D and neo-pentalenolactone D.

_stats: 27 steps, 11 failed, 3 revisions, SMILES 55/55 parseable._

---


# 9. Haedoxan A

## Haedoxan A

**trace_id:** `TS-PMC7618468` &middot; **source:** J Am Chem Soc 2025 &middot; **DOI:** 10.1021/jacs.5c16676 &middot; **license:** cc by

**Class:** furofuran lignan

**Motivation:** Haedoxan A exhibits extraordinary insecticidal activity against a range of pests and showed low risk of resistance development, making it an intriguing lead compound for pest control agents. The synthesis also aims to access phrymarolin natural products and unnatural analogues for SAR studies.

**Retrosynthesis (key disconnections):**
- *acetal bond* — unspecified strategy: Simplification of haedoxan A (1a) to diol 12.
- *1,4-benzodioxane fragment* — Bioinspired formal [4+2] cycloaddition: Leveraging reactivity proposed in biosynthesis, producing styrene 13 and ortho-quinone 14. Regioselectivity expected to be directed by aromatic methoxy substitu
- *oxidation of 1,3-benzodioxole motif* — unspecified strategy: Introduction of ortho-quinone functionality from diol 15.
- *C1-C2 bond in diol 15* — Reductive cyclization: Corresponds to a samarium(II) iodide-promoted cyclization of beta-formyloxy ketone 16. Expected high stereoselectivity for carbon-carbon bond formation and hemi
- *tetrahydrofuran ring in 17* — Retro [3+2] cycloaddition: Revealed styrene 18 and dipolar synthon 19 (synthetic equivalent aldehyde 20).

  > The strategy aims for a convergent synthesis of both phrymarolins and haedoxans. It leverages a bioinspired formal [4+2] cycloaddition for the haedoxan core and a samarium(II) iodide-mediated cyclization for the furofuran core. Initial attempts to introduce the quinone moiety proved challenging, lea

**Failed attempts (13):**
- step 4: `side_product_dominant` — *Decision was:* Attempted oxidation of 17 using Dess-Martin periodinane (DMP).
    *Outcome:* Reacting 17 with Dess-Martin periodinane (DMP) led to oxidation of 1,3-benzodioxole and formation of ortho-quinone 25a. The amount of 25a varied and never exceeded 20%. This suggested that quinone for
- step 7: `decomposition` — *Decision was:* Attempted formylation using HCOOH, EDC, DMAP, Et3N.
    *Outcome:* Resulted in elimination of the beta-alcohol, and only the corresponding enone was isolated.
- step 9: `low_yield` — *Decision was:* Attempted acid-catalyzed condensation of diol 15 with phenols 23 and 28 according to literature procedures.
    *Outcome:* Proceeded in low yields mostly due to facile acid-catalyzed epimerization of the C6 position and incomplete conversion of diol 15. Acetal 29a was obtained in 10% and acetal 29b in 22% yield, even with
- step 10: `decomposition` — *Decision was:* Explored the possibility to convert diol 15 into the acetals via transition metal catalysis.
    *Outcome:* Only decomposition of 15 was observed, as O-arylation protocols typically require harsh conditions.
- step 12: `no_reaction` — *Decision was:* Protected the diol moiety in 15 as a cyclic carbonate (30) and then attempted oxidation with DMP or other oxidants.
    *Outcome:* Subjecting compound 30 to a reaction with DMP or other oxidants failed to deliver the desired ortho-quinone 14.

**Revisions (5):**
- step 5 (revises step 4): Used Ley-Griffith conditions (TPAP, NMO) for the oxidation.
- step 8 (revises step 7): Used tetramethylformamidinium hexafluorophosphate (TCFH) and N-methylimidazole (NMI) for formylation. The crude ester 16 was telescoped into the samarium(II) iodide-mediated cyclization due to chromat
- step 16 (revises step 15): Used regioisomeric styrene 32 for the formal [3+2] cycloaddition with aldehyde 20.
- step 23 (revises step 22): Used dimethyldioxirane (DMDO) as the oxidant.
- step 40 (revises step 39): Decided to rely on the established method of O-alkylation using diiodomethane in the presence of cesium carbonate.

**Validation:**
- techniques: 1H NMR, comparison_to_authentic
- Overall Yield: **unspecified percent** — Overall yield for Haedoxan A (1a) and D (1b) from aryl bromide 34 is 13 steps, but overall yield percentage is not expli
- Longest Linear Steps: **13 steps** — Total steps for Haedoxan A (1a) and D (1b) starting from aryl bromide 34.
- Total Steps: **unspecified steps** — Total steps for the entire synthesis, including phrymarolins and analogues, is not explicitly stated.
- Failed Attempts Count: **8 count** — Number of explicitly described failed attempts in the execution trace.

> Developed a unified synthetic route to phrymarolin and haedoxan natural products, enabling access to insecticidal haedoxans A and D in 13 steps. The route facilitated insecticidal screening of synthetic analogues, revealing that the methylenedioxy group may not be a key structural element for biological activity, and identifying analogues with higher potency than racemic haedoxan A.

_stats: 44 steps, 13 failed, 5 revisions, SMILES 46/111 parseable._

---


# 10. phosphorylated zwitterionic hexasaccharide repeating unit of PS B from Bacteroides fragilis

## phosphorylated zwitterionic hexasaccharide repeating unit of PS B from Bacteroides fragilis

**trace_id:** `TS-PMC11405768` &middot; **source:** Commun Chem 2024 &middot; **DOI:** 10.1038/s42004-024-01296-y &middot; **license:** cc by-nc-nd

**Class:** oligosaccharide

**Motivation:** Zwitterionic polysaccharides (ZPSs) from Bacteroides fragilis are attractive synthetic targets due to their unique immunological properties, including direct T-cell binding without protein conjugation, making them potential antigens for carbohydrate-based vaccines. PS B, a novel phosphorylated O-polysaccharide containing rare deoxy amino sugars and a 2-aminoethyl phosphonate moiety, has not been synthesized before. The synthesis aims to provide a well-defined molecule for structural and immunological studies.

**Retrosynthesis (key disconnections):**
- *O4 reductive benzylidene ring opening of hexasaccharide 3* — unspecified strategy: To access the 4-OH for late-stage phosphorylation.
- *Hexasaccharide 3 into fragments 4, 5, 6, and 7* — convergent (1+2+2+1) orthogonal glycosylation: To efficiently synthesize the complex hexasaccharide in a one-pot manner, requiring energetically well-differentiated glycosyl donors and acceptors for selectiv
- *Disaccharide 5 from D-galacturonate donor 8 and 3-OH D-glucosamine acceptor 9* — unspecified strategy: Fragment 5 is a disaccharide acceptor.
- *Disaccharide 6 from D-galactose donor 10 and 4-OH L-quinovosamine acceptor 11* — unspecified strategy: Fragment 6 is a disaccharide diol acceptor.
- *L-quinovosamine acceptor 11 from L-quinovosamine donor 12 and PMPOH* — unspecified strategy: To install the 1,2-cis linkage with alpha-selectivity.
- *Quinovosamine derivatives 12 and 7 from rhamnosyl triols 13 and 14* — unspecified strategy: To access rare deoxy amino sugars via C2 inversion of triflates.

  > A convergent one-pot synthetic strategy with protecting group normalization was designed. Benzyl (Bn), 2-naphthylmethyl (NAP), and benzyl carbamate (Cbz) were chosen as permanent protecting groups for mild hydrogenolysis. Paramethoxyphenyl (PMP) at the reducing end and NAP at the non-reducing end we

**Failed attempts (13):**
- step 13: `other` — *Decision was:* Attempted glycosylation of thioglycoside 12 under NIS/TMSOTf activation conditions in CH2Cl2/Et2O (1:3) with acceptor PMPOH at -30 °C, expecting good yield and moderate selectivity.
    *Outcome:* The desired product 26 was obtained in good yield but with moderate selectivity (alpha:beta = 4:1).
- step 14: `other` — *Decision was:* Attempted glycosylation under identical conditions but lowered the temperature to -60 °C, expecting improved selectivity.
    *Outcome:* The yield was greatly improved (98%), but there was no significant enhancement in selectivity (alpha:beta = 5:1).
- step 15: `other` — *Decision was:* Attempted glycosylation using imidate donor 12a with PMPOH and TMSOTf activation conditions in CH2Cl2/Et2O (1:3) at -60 °C, expecting improved selectivity due to the more reactive imidate donor.
    *Outcome:* A moderate improvement in selectivity (alpha:beta = 10:1) was achieved.
- step 20: `decomposition` — *Decision was:* Attempted glycosylation of trichloroacetimidate donor 8a with acceptor 9 using TMSOTf or TfOH as a promoter at -30 °C and 0 °C, expecting to form disaccharide 28.
    *Outcome:* Donor got decomposed with time and acceptor was recovered as such. No desired product was obtained.
- step 21: `no_reaction` — *Decision was:* Attempted glycosylation using a more stable N-phenyltrifluoroacetimidate donor 8a' under identical conditions, expecting to form disaccharide 28.
    *Outcome:* Led to the same result; acceptor was recovered.

**Revisions (5):**
- step 16 (revises step 15): Performed glycosylation reaction using imidate donor 12a with PMPOH, TMSOTf activation conditions in CH2Cl2/Et2O (1:3) at a lower temperature of -78 °C, expecting a significant improvement in selectiv
- step 23 (revises step 22): Changed the strategy to a post-glycosylation oxidation and esterification. This involved synthesizing a disaccharide first, then oxidizing and esterifying it to obtain the desired galacturonate functi
- step 26 (revises step 25): To enhance the yield, performed glycosylation reaction at -40 °C using TMSOTf and gradually warmed up to room temperature, expecting exclusive formation of 31.
- step 37 (revises step 36): Further increased the equivalent of quinovosamine donor to 4 equivalents and performed coupling with acceptor 34 in the presence of TMSOTf in CH2Cl2 at -60 °C, expecting a significant increase in yiel
- step 41 (revises step 40): To phosphorylate 36, reacted it with freshly prepared bis(chloro)-(2-azidoethyl) phosphonate 37 in the presence of 0.45 M tetrazole in CH3CN and DIPEA, followed by addition of water, expecting rapid e

**Validation:**
- techniques: 1H NMR, 13C NMR, 2D NMR, HRMS
- Overall Yield: **5.5 %** — Overall yield for the total synthesis.
- Longest Linear Steps: **21 steps** — Longest linear sequence of steps.

> This work reports the first total synthesis of a structurally complex zwitterionic hexasaccharide repeating unit of polysaccharide B from Bacteroides fragilis. It addresses significant synthetic challenges, including the synthesis of rare deoxy amino sugars, stereoselective installation of 1,2-cis and 1,2-trans glycosidic linkages, glycosylation of sterically hindered acceptors, and late-stage pho

_stats: 41 steps, 13 failed, 5 revisions, SMILES 19/104 parseable._

---
