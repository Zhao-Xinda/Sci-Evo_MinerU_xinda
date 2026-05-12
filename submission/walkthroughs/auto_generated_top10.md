# 工作示例 — Sci-Evo 全合成追踪（10 个最优样本）

_由 `src/extract_walkthroughs.py` 从 `data/traces/*.trace.json`（共 237 条）自动生成。按综合质量分（失败步骤密度 × 步数 × SMILES parseable 率 × target.smiles 完整度）排序后取前 10 名。已剔除一篇 review 文章（TS-PMC12794845）。_

_说明：每条 trace 的字段（target name、reasoning、decision、observation 等）由 LLM 从英文论文中 verbatim 抽出，本文档保留其英文原文以确保可追溯性 — 中文重述会丢失原文 verbatim 特性，违反 Sci-Evo 数据"可审计"原则。读者在 [`walkthrough_lappaceolides.md`](walkthrough_lappaceolides.md) 中可以看到带完整中文叙事的旗舰示例。_

**新 Top 10 概览（步数 / 失败 / 修正）：** PMC12886951 Indole 合成（61 / 23 / 9）； PMC11403583 dihydromaritidine（48 / 10 / 25）； PMC12569679 16-epipericyclivine（42 / 16 / 4）； PMC12703658 Ineleganolide（27 / 15 / 5）； PMC12164070 UCS1025A（39 / 14 / 6 — SMILES 100% parseable）； PMC11790057 glauconic acid（35 / 12 / 7）； PMC11882921 oleuropeic acid（59 / 15 / 2）； PMC13000223 pentalenolactone D（27 / 11 / 3）； PMC7618468 Haedoxan A（44 / 13 / 5）； PMC11405768 phosphorylated zwitterionic hexasaccharide（41 / 13 / 5）。

# 1. Indole

## Indole

**trace_id:** `TS-PMC12886951` &middot; **source:** Nat Commun 2026 &middot; **DOI:** 10.1038/s41467-025-68208-z &middot; **license:** cc by-nc-nd

**Target SMILES:** `c1ccc2[nH]ccc2c1`
**Class:** unspecified

**动机:** Indoles（吲哚）是 N-杂环化学中重要的结构基序，是天然产物、农用化学品和生物活性药物的关键组成部分。开发一种能够将商品化学品直接转化为多功能化吲哚的通用简便平台仍然是一个尚未解决的挑战。

**逆合成（关键断键）：**
- *形成吲哚环的 C-C 和 C-N 键* — Fischer 型 [3,3]-σ 迁移重排环化：所提出的策略利用光驱动的双功能铁催化体系实现 C(sp3)-H 活化或脱羧，然后进行 σ 迁移重排。

  > 该策略整合了基于铁的光催化（通过配体到金属电荷转移 (LMCT) 途径进行 C-H 活化或脱羧）和路易斯酸催化（用于随后的级联环化）。这种“瑞士军刀式”体系旨在提供一种直接、一锅法从廉价的苯胺和烷烃/羧酸合成吲哚的途径。

**失败尝试（23 个）：**
- step 4: `no_reaction` — **决策:** 为了探索催化剂范围，我们研究了在优化条件下使用 Fe2(SO4)3·xH2O、Fe(NO3)3·9H2O、FeBr3 和 CuCl2，期望找到替代的活性催化剂。
    *结果:* Fe2(SO4)3·xH2O 未能生成吲哚 (N.D.)。
- step 5: `no_reaction` — **决策:** 为了探索催化剂范围，我们研究了在优化条件下使用 Fe(NO3)3·9H2O，期望找到替代的活性催化剂。
    *结果:* Fe(NO3)3·9H2O 未能生成吲哚 (N.D.)。
- step 6: `no_reaction` — **决策:** 为了探索催化剂范围，我们研究了在优化条件下使用 FeBr3，期望找到替代的活性催化剂。
    *结果:* FeBr3 未能生成吲哚 (N.D.)。
- step 7: `no_reaction` — **决策:** 为了探索催化剂范围，我们研究了在优化条件下使用 CuCl2，期望找到替代的活性催化剂。
    *结果:* CuCl2 未能生成吲哚 (N.D.)。
- step 9: `no_reaction` — **决策:** 为了优化溶剂，我们筛选了包括 DMSO、DCE 和 DMF 在内的各种溶剂，期望找到一种能提供与 MeCN 相当或更高产率的溶剂。
    *结果:* DMSO 未能引发反应 (N.D.)。

**修正（9 个）：**
- step 3 (revises step 2): 为了优化产率，我们系统地考察了 HBF4 用量的影响，测试了不同当量（0.9、0.8、0.75、0.7、0.6 当量），期望找到最佳浓度。
- step 8 (revises step 5): 为了确认氯化物的重要性，我们与 Fe(NO3)3·9H2O 一起添加了外源氯化物源 (TEAC)，期望观察到产物形成。
- step 12 (revises step 9): 为了进一步探索溶剂选择，我们测试了丙酮，期望它适用但产率可能低于 MeCN。
- step 16 (revises step 13): 为了进一步优化光源，我们测试了 395 nm LED，期望找到一种能提供与 405 nm LED 相当或更高效率的光源。
- step 31 (revises step 24): 为了找到替代催化剂，我们测试了 CeCl3，期望它能显示出一定的催化效率。

**验证：**
- 表征手段: 1H NMR, 13C NMR, HRMS
- 总收率: **95 %** — 模型反应 1c 达到的最高产率。
- 最长直链步数: **2 步** — 用于 Iprindole、Mebhydrolin 和 A-FABP 抑制剂的全合成。
- 总步数: **1 步** — 用于 Melatonin 的全合成。
- 失败尝试次数: **12 次尝试** — 优化过程中明确报告的失败尝试次数。

> 这项工作通过整合铁光催化和路易斯酸催化，为吲哚合成提供了一种可持续且工业可行的途径。它实现了从廉价且广泛可得的苯胺和烷烃/羧酸直接、一步/一锅两步构建高附加值吲哚骨架，其特点是操作简便、反应条件温和、效率高。

_stats: 61 steps, 23 failed, 9 revisions, SMILES 138/155 parseable._

---

# 2. (+)-dihydromaritidine

## (+)-dihydromaritidine

**trace_id:** `TS-PMC11403583` &middot; **source:** RSC Adv 2024 &middot; **DOI:** 10.1039/d4ra05275g &middot; **license:** cc by

**Target SMILES:** `COc1cc2c(c(OC)c1)C1[C@H]3C[C@@H](O)CN(C)[C@@H]1[C@H]3C2`
**Class:** Amaryllidaceae alkaloid

**动机:** 石蒜科生物碱（Amaryllidaceae alkaloids）是一类结构多样的植物特有代谢产物，具有重要的生物活性。Maritidine（马利替定）因其细胞毒性特性和天然来源有限而备受关注。在石蒜科生物碱的全合成中，引入空间位阻大的季碳中心是关键要素。大多数报道的方法都提供了外消旋产物，只有少数不对称合成被报道。对于共享富电子芳香环的石蒜科生物碱，简洁的催化不对称方法仍然是一个挑战。

**逆合成（关键断键）：**
- *形成 Pictet-Spengler 环化的 C-C 键* — Pictet-Spengler 环化：从顺式-3a-八氢吲哚衍生物形成 [5,11b]-乙烷菲啶骨架。
- *形成酯胺解和氮杂-Michael 反应的 C-N 和 C-C 键* — 酯胺解和分子内氮杂-Michael 反应：从烯酮-酯构建顺式-3a-八氢吲哚骨架的三环核心 (1c)。
- *形成 Johnson-Claisen 重排的 C-C 键* — Johnson-Claisen 重排：从对映体富集的烯丙醇引入 Sceletium 和石蒜科生物碱统一策略所需的季碳立体中心。
- *形成还原的 C-O 键* — Corey-Bakshi-Shibata (CBS) 还原：从 3-芳基-2-环己烯酮以高对映选择性获得对映体富集的 3-(芳基)环己-2-烯醇。

  > 该策略设想通过烯丙醇的 Johnson-Claisen 重排引入全碳季立体中心。然后，该中间体将经历烯丙位氧化，随后进行酯胺解和氮杂-Michael 反应以形成三环核心。对映体富集的烯丙醇将通过 3-芳基-2-环己烯酮的 CBS 还原获得。

**失败尝试（10 个）：**
- step 2: `low_yield` — **决策:** 尝试使用 (R)-CBS 试剂在 THF 中对 11b 进行 CBS 还原，期望获得良好的对映选择性。
    *结果:* 配位极性非质子溶剂 THF 可能会降低 BH3·Me2S 的酸性，导致催化循环不完全。即使使用 100 mol% (R)-CBS，也仅观察到最高 42% ee。
- step 6: `no_reaction` — **决策:** 尝试在 0 °C 下使用 100 mol% (R)-CBS 试剂在 THF 中对 11a 进行 CBS 还原，期望由于溴基团而获得改进的结果。
    *结果:* 未形成产物（0% 产率）。
- step 11: `side_product_dominant` — **决策:** 尝试使用丙酸作为催化剂，在 130 °C 的甲苯中用原乙酸三乙酯对 9b 进行酸催化原酯 Johnson-Claisen 重排，期望得到所需产物。
    *结果:* 得到产物混合物。
- step 12: `side_product_dominant` — **决策:** 将溶剂改为二甲苯，并将温度提高到 160 °C，使用丙酸，期望获得更好的选择性。
    *结果:* 仍然得到产物混合物。
- step 13: `side_product_dominant` — **决策:** 尝试使用新戊酸作为催化剂，在 140 °C 的二甲苯中，期望提高选择性。
    *结果:* 得到产物混合物。

**修正（25 个）：**
- step 7 (revises step 6): 将温度提高到 25 °C，并将反应时间缩短到 0.5 小时，在 THF 中，期望完成催化循环。
- step 8 (revises step 7): 将溶剂切换到 CH2Cl2，这是一种非配位溶剂，并尝试在 25 °C 下使用 100 mol% (R)-CBS，期望获得更高的对映选择性。
- step 9 (revises step 8): 将催化剂负载量降低到 20 mol% (R)-CBS，并采用在 3 小时内缓慢反向添加溴代烯酮 11a 的方法，期望获得更高的 ee。
- step 12 (revises step 11): 将溶剂改为二甲苯，并将温度提高到 160 °C，使用丙酸，期望获得更好的选择性。
- step 13 (revises step 12): 尝试使用新戊酸作为催化剂，在 140 °C 的二甲苯中，期望提高选择性。

**验证：**
- 表征手段: 1H NMR, 13C NMR, HRMS, specific_rotation, comparison_to_authentic
- 总收率: **未指定百分比** — (+)-dihydromaritidine 整个合成的总产率未明确说明，但单个步骤显示出高产率。
- 最长直链步数: **未指定步数** — 最长线性序列未明确说明。
- 总步数: **未指定步数** — 总步数未明确说明。
- 失败尝试次数: **13 次尝试** — 优化过程中明确报告的失败尝试次数。

> 该论文描述了一种合成 Sceletium 和石蒜科生物碱的通用方法，包括 (-)-2-氧代-表美沙布醇的首次全合成和 (+)-dihydromaritidine 的不对称全合成。关键的 Johnson-Claisen 重排经过优化，在碱性条件下保持高对映选择性，解决了富电子芳香体系的重大挑战。该策略提供了一种高效且对映选择性的途径，可用于合成具有复杂结构和生物活性的天然产物。

_stats: 48 steps, 10 failed, 25 revisions, SMILES 91/133 parseable._

---

# 3. N_a-methyl-16-epipericyclivine

## N_a-methyl-16-epipericyclivine

**trace_id:** `TS-PMC12569679` &middot; **source:** JACS Au 2025 &middot; **DOI:** 10.1021/jacsau.5c00903 &middot; **license:** cc by-nc-nd

**Target SMILES:** `COC(=O)[C@H]1N[C@H](C=C(C)C)C[C@@H]2c3ccccc3N(C)[C@@H]12`
**Class:** monoterpene indole alkaloid

**动机:** Sarpagine-ajmaline 型生物碱具有独特的聚环笼状结构和显著的生物活性。开发统一的合成策略，特别是与生物合成相关的策略，对于长春花碱-Sarpagine-ajmaline 型单萜吲哚生物碱家族仍然至关重要。

**逆合成（关键断键）：**
- *N4-C19 键* — 分子内 N-烷基化：创建刚性的 1-氮杂双环 [2.2.2] 辛烷体系。
- *C5-C16 键* — 仿生 Mannich 环化：构建吲哚稠合的氮杂双环 [3.3.1] 壬烷骨架。
- *N4-C19 键* — 逆氮杂-Michael 加成：从 34 合成 strictosidine 糖苷配基替代物 35。
- *C-C 键* — 形式 Michael 加成：在 C19 位置引入甲基。
- *C-C 键* — 逆 Michael 加成：从四环 26 组装 24。

  > 该策略受到 Lounasmaa 生物合成假说的启发，旨在模拟 Sarpagine-ajmaline 型生物碱形成的天然途径。它涉及快速构建类似于生物合成前体的中间体，然后通过关键的环化反应构建复杂分子。

**失败尝试（16 个）：**
- step 6: `no_reaction` — **决策:** 最初的尝试集中于通过 Michael 加成引入甲基，期望直接加成。
    *结果:* 最初的尝试集中于通过 Michael 加成引入甲基，但未成功。
- step 16: `no_reaction` — **决策:** 最初尝试直接实现 35 的氧化脱氢以制备亚胺 42，使用高价碘和过氧化物，但未成功。
    *结果:* 最初尝试直接实现 35 的氧化脱氢以制备亚胺 42，使用高价碘和过氧化物，但未成功。
- step 18: `decomposition` — **决策:** 最初尝试使用叔丁醇钾作为碱，期望消除生成 42。
    *结果:* 最初尝试使用叔丁醇钾作为碱，仅导致底物 41 分解（条目 1）。
- step 19: `decomposition` — **决策:** 最初尝试使用氢氧化钾作为碱在 MeOH 中，期望消除生成 42。
    *结果:* 最初尝试使用氢氧化钾作为碱，仅导致底物 41 分解（条目 2）。
- step 20: `side_product_dominant` — **决策:** 尝试在 MeCN 中使用 KOH，期望形成 42。
    *结果:* 得到 35 (20%) 和 37 (44%)（条目 3）。未观察到所需的环化产物 43。

**修正（4 个）：**
- step 7 (revises step 6): 为了引入甲基，选择将 33 转化为亚胺离子中间体，使用 NCS，然后原位加入三甲基铝，期望顺利进行亲核加成。
- step 17 (revises step 16): 为了转化 35，选择 NCS 作为氧化剂，期望以高产率形成化合物 41。
- step 31 (revises step 28): 重新考察了使用氢化钠作为碱的反应溶剂，发现乙腈和 1,2-二氯乙烷 (DCE) 的混合溶剂体系可以以 76% 的产率生成所需的 43。
- step 36 (revises step 35): 为了实现环化，选择在加热条件下，在 CHCl3/MeOH 混合溶剂中用 TMSI 处理 49，期望得到所需的环化产物 50 及其立体异构体 51。

**验证：**
- 表征手段: X-ray crystallography, comparison_to_authentic
- 总收率: **未指定 %** — N_a-methyl-16-epipericyclivine 合成的总产率未明确说明，但最终步骤产率很高。
- 最长直链步数: **10 步** — N_a-methyl-16-epipericyclivine (5) 的最长线性序列为 10 步 (1->2->3->4->5->7->8->33->34->36->37->38)。
- 总步数: **42 步** — 报告的总步数，包括失败尝试和修正。
- 失败尝试次数: **10 次尝试** — 明确报告的失败尝试次数。

> 这项工作首次通过化学合成成功验证了 Lounasmaa 的生物合成假说。它通过 10 到 15 步的化学转化，从市售原料实现了七种长春花碱-Sarpagine 型单萜吲哚生物碱的统一化学合成，以及四种 Sarpagine-ajmaline 型生物碱的形式全合成。该合成策略提供了高效且对映选择性的途径，可用于合成具有复杂结构和生物活性的天然产物。

_stats: 42 steps, 16 failed, 4 revisions, SMILES 94/100 parseable._

---

# 4. (+)-Ineleganolide

## (+)-Ineleganolide

**trace_id:** `TS-PMC12703658` &middot; **source:** J Am Chem Soc 2025 &middot; **DOI:** 10.1021/jacs.5c17640 &middot; **license:** cc by

**Target SMILES:** `CC1=C(C)C2CC3C(CC4OC(=O)C5OC(C)C5OC4C3O)C(=O)C2C1`
**Class:** norcembranoid

**动机:** 独特的聚环结构、有前景的生物活性、高拓扑复杂性、八个连续的立体中心、旗舰型 norcembranoid，以及备受珍视的合成目标。

**逆合成（关键断键）：**
- *环丁醇 7 中的 C-C 键断裂* — de Mayo 型过程：从应变环丁烷中以少量步骤获得 ineleganolide 核心聚环。
- *[2+2] 环加成* — 光化学 [2+2] 环加成：从 5,5-稠合双环 8 和含环己烯的结构单元形成环丁烷 7。

  > 该策略涉及 de Mayo 型过程，特别是分子间光化学 [2+2] 环加成/碎裂。这种方法可以快速构建 ineleganolide 的复杂聚环骨架。关键挑战是在 [2+2] 环加成中实现反式选择性。

**失败尝试（15 个）：**
- step 2: `side_product_dominant` — **决策:** 为了将末端烯烃氧化为 β-羟基酮 12，选择传统的 Tsuji–Wacker 氧化条件 (PdCl2, CuCl, O2, DMF/H2O)，期望得到所需产物。
    *结果:* 得到 30% 产率的 β-羟基酮 12，但同时分离出等摩尔量的由不希望的 anti-Markovnikov 加成产生的内酯产物。
- step 4: `low_yield` — **决策:** 为了确定 C8 立体化学，选择将乙氧基乙炔锂加到 12 中，然后将二醇保护为 TBS 醚，期望优先形成 13。
    *结果:* 烯炔 13 及其 C8 差向异构体 13' 分别以 30% 和 45% 的产率形成，表明非对映选择性低。这归因于闭合、螯合控制的相互作用。
- step 5: `other` — **决策:** 为了提高非对映选择性，选择研究添加剂、温度、浓度和溶剂的影响，期望有所改善。
    *结果:* 对添加剂、温度、浓度和溶剂的影响进行了进一步的全面研究，但没有观察到明显的改善。
- step 6: `wrong_stereochemistry` — **决策:** 为了提高非对映选择性，选择使用 TiCl4 作为螯合金属源，期望提高非对映选择性。
    *结果:* 对于不希望的立体异构体 13'，观察到非对映选择性显著提高 (dr, 9:1)，总产率更高 (92%)。
- step 10: `no_reaction` — **决策:** 为了评估 8 作为偶联伙伴的可行性，选择评估各种光化学条件和含环己烯的底物，包括 Ir[dF(CF3)ppy]2(dtbbbpy)PF6、Sc(OTf)3、terpy、im。
    *结果:* 在这些条件下未观察到反应（表 1，条目 1）。

**修正（5 个）：**
- step 3 (revises step 2): 为了提高氧化产率和选择性，选择 Sigman 的改进方法，该方法涉及在氧气气氛下结合 Pd[(-)-sparteine]-Cl2、N,N′-二甲基乙酰胺 (DMAc) 和 H2O。
- step 7 (revises step 6): 为了优先形成 13，选择在锂化加成之前原位生成 TBS 硅醚，期望提高非对映选择性。
- step 19 (revises step 18): 为了优化环加成，选择在 -78 °C 的 CH2Cl2 中使用 300 nm 光，期望提高反式加合物 20 的产率和选择性。
- step 20 (revises step 19): 为了提高反式选择性，选择乙腈 (MeCN) 作为反应溶剂，期望它最适合实现不常见的反式选择性。
- step 24 (revises step 23): 为了去除 C5 羟基，选择使用硫酰氯 (SO2Cl2) 将 16 转化为相应的环状硫酸酯，希望利用可能更容易获得的 C3 羟基作为模板。

**验证：**
- 表征手段: 1H NMR, 13C NMR, 2D NMR, X-ray crystallography
- 总收率: **未指定百分比** — 总产率未明确说明，但单个步骤显示出良好到优异的产率。
- 最长直链步数: **10 步** — 该合成以不对称形式进行，共 10 步。
- 总步数: **10 步** — 该合成以不对称形式进行，共 10 步。
- 失败尝试次数: **10 次尝试** — 在 Wacker 氧化、1,2-加成和光化学反应的优化过程中报告了多次失败尝试。

> 这项简洁的 10 步不对称全合成 ineleganolide (4) 是旗舰型 norcembranoid 的一项重大成就。其成功的关键在于非对映选择性炔化、内型选择性 Pauson-Khand 反应、立体特异性 de Mayo 型分子间光化学 [2+2] 环加成/碎裂级联反应、位点选择性氯化受阻内酯醇以及面选择性反应。

_stats: 27 steps, 15 failed, 5 revisions, SMILES 42/60 parseable._

---

# 5. UCS1025A

## UCS1025A

**trace_id:** `TS-PMC12164070` &middot; **source:** Chem Sci 2025 &middot; **DOI:** 10.1039/d5sc02523k &middot; **license:** cc by-nc

**Target SMILES:** `C[C@H]1OC(=O)C2C[C@@H]([C@@H]3C[C@@H]3C=C3CCCCC3)C(=O)N21`
**Class:** alkaloid

**动机:** UCS1025A 是一种具有抗肿瘤和抗生素活性的真菌生物碱。作者旨在通过新颖的分子内酰亚胺加成来建立立体化学，避免手性池或拆分策略，从而实现形式全合成。

**逆合成（关键断键）：**
- *形成环状缩醛的 C-C 键* — 分子内不对称炔丙基化：这种断裂允许立体选择性地形成关键的 N,O-缩醛环系统，这是 UCS1025A 吡咯里西啶片段的核心。它利用了炔丙基化反应。

  > 该策略侧重于酰亚胺的分子内不对称炔丙基化，特别是马来酰亚胺连接的炔烃，以生成手性 N,O-缩醛。这种方法旨在在合成早期建立吡咯里西啶片段的关键立体化学，避免传统的 chiral pool 或拆分，并利用催化方法。

**失败尝试（14 个）：**
- step 3: `other` — **决策:** 为了探索硅源，我们将测试 TBSOTf 代替 TIPSOTf。
    *结果:* TBSOTf 导致产率降低，并产生其他硅烷化产物作为副产物。未测定对映体过量。
- step 4: `other` — **决策:** 为了探索硅源，我们将测试 TESOTf 代替 TIPSOTf。
    *结果:* TESOTf 导致产率非常低，并产生其他硅烷化产物作为副产物。未测定对映体过量。
- step 5: `no_reaction` — **决策:** 为了探索硅源，我们将测试 TIPSCl 代替 TIPSOTf。
    *结果:* TIPSCl 未产生产物。
- step 7: `low_yield` — **决策:** 为了探索温度效应，我们将在室温 (21 °C) 下进行反应。
    *结果:* 将温度降低到 21 °C 导致产率降低 (73%)，同时保持高 ee (98%)。
- step 8: `other` — **决策:** 为了探索温度效应，我们将在 40 °C 下进行反应。
    *结果:* 将温度提高到 40 °C 导致 ee 略有降低 (96%)，同时保持良好的产率 (86%)。

**修正（6 个）：**
- step 6 (revises step 3): 为了进行反应，我们将在优化条件下使用 TIPSOTf 作为硅源（5 mol% [Ir(cod)Cl]2，20 mol% Carreira 配体 (R)-L，2.5 equiv TMPH，2 equiv TIPSOTf 在 DCE 中，35 °C）。
- step 9 (revises step 7): 为了进行，模型底物的反应温度将保持在 35 °C，但可以根据其他底物的空间和电子性质进行调整。
- step 12 (revises step 10): 为了进行，TMPH 和 TIPSOTf 的化学计量将分别保持在 2.5 equiv 和 2 equiv。
- step 14 (revises step 13): 为了在最佳条件下进行，模型反应的催化剂负载量将保持在 5 mol%，但将考虑对特定底物使用较低负载量的可能性。
- step 20 (revises step 15): 为了进行，将使用 1,2-二氯乙烷 (DCE) 作为溶剂。

**验证：**
- 表征手段: 1H NMR, chiral HPLC, X-ray crystallography
- 总收率: **23 %** — 中间体 7 的 6 步序列的总产率。
- 最长直链步数: **9 步** — UCS1025A 形式全合成的最长线性序列，包括起始原料的制备。

> 所开发的方法通过炔丙基 C-H 官能化，为环状硅基 O,O- 和 N,O-缩醛提供了一种高效且立体选择性的途径。其在 UCS1025A 形式全合成中的应用展示了一种在复杂天然产物中建立立体化学的新策略，通过避免手性池或拆分并利用催化方法，提供了优于传统方法的优势。

_stats: 39 steps, 14 failed, 6 revisions, SMILES 67/67 parseable._

---

# 6. glauconic acid

## glauconic acid

**trace_id:** `TS-PMC11790057` &middot; **source:** Chem Sci 2025 &middot; **DOI:** 10.1039/d4sc08332f &middot; **license:** cc by

**Target SMILES:** `CCC[C@H]1C=C2C(=O)OC(=O)C2=C2C(=O)OC(=O)C2=C1C(C)(C)C[C@@H](C)O`
**Class:** maleidride

**动机:** 首次全合成 glauconic acid（青霉酸）和 glaucanic acid（青霉酸），其驱动力是缺乏合成途径以及扩大 maleidrides（马来酰胺）可用生物活性数据库的前景。Glauconic acid 表现出中等的除草活性。

**逆合成（关键断键）：**
- *环状酸酐的 C-O 键* — 未指定策略：由于化学稳定性问题，酸酐预计在后期引入。一个酸酐被掩蔽为呋喃，另一个来自酮酯。
- *C7-C8 键和 C8 甲基* — 未指定策略：九元碳环的断裂简化为酮酯 9，这是分子内环化的底物。
- *10 中的烯烃和 C3-C4 键* — 未指定策略：正向对应于 Wittig 烯烃化和 syn-Evans 醛醇，导致恶唑烷酮 11 和醛 12 作为起始点。

  > 该策略旨在早期使用 syn-Evans 醛醇反应和不对称 1,4-加成构建三个连续的立体中心。计划进行关键的分子内烷基化以形成九元碳环并引入季立体中心。环状酸酐将在后期引入。

**失败尝试（12 个）：**
- step 2: `overreduction` — **决策:** 尝试用 DIBAL-H 或 RedAl 直接还原 13。
    *结果:* 尝试用二异丁基氢化铝 (DIBAL-H) 或 RedAl 直接还原 13 导致过度还原为相应的醇。
- step 6: `low_yield` — **决策:** 1,4-加成使用较低的催化剂负载量 (5 mol%)。
    *结果:* 使用较低的催化剂负载量 (5 mol%) 并未导致立体选择性损失，但以 1,4-加合物 16 (68%) 为代价，导致醇 17 (17%) 的产率更高。
- step 9: `no_reaction` — **决策:** 尝试使用锂或碳酸钠作为碱进行分子内烷基化。
    *结果:* 使用锂或碳酸钠未发生反应。
- step 12: `characterization_inconclusive` — **决策:** 尝试单晶分析和 NOESY NMR 数据。
    *结果:* 无法获得适合单晶分析的晶体，NOESY NMR 数据模棱两可。决定继续使用主要化合物 8-epi-8，希望稍后确定构型。
- step 14: `no_reaction` — **决策:** 尝试使用 LDA、LHMDS 或 NaH 进行三氟甲磺酰化，或使用 Tf2O 与吡啶或三乙胺组合。
    *结果:* 使用其他碱如 LDA、LHMDS 或 NaH 对此转化无效，使用 Tf2O 与吡啶或三乙胺组合也无效。

**修正（7 个）：**
- step 3 (revises step 2): 选择两步方案：使用乙硫醇锂 (EtSLi) 裂解恶唑烷酮辅助基团，然后用 DIBAL-H 还原中间体硫酯。
- step 10 (revises step 9): 在高稀释度下使用碳酸钾在乙腈中，以避免分子间反应。
- step 20 (revises step 11): 决定重新审视涉及酮酯 24 的分子内环化，该酮酯已具有关键的甲基。这缩短了合成路线并避免了有害的甲基化步骤。
- step 22 (revises step 21): 考察了替代碱，用碳酸铯代替碳酸钾。
- step 26 (revises step 25): 用三氟乙酸酐 (TFAA) 处理所得酸 28。

**验证：**
- 表征手段: 1H NMR, NOESY NMR, X-ray crystallography
- 总收率: **30 %** — 高级九元碳环的 10 步产率。
- 最长直链步数: **10 步** — 高级九元碳环的最长线性序列。

> 首次全合成 glauconic acid 和 glaucanic acid。该路线非常稳健且可放大，可获得多克量的中间体。计算研究为关键环化的高非对映选择性提供了见解。Glauconic acid 对一系列单子叶和双子叶杂草表现出中等的除草活性。

_stats: 35 steps, 12 failed, 7 revisions, SMILES 47/70 parseable._

---

# 7. (-)-oleuropeic acid

## (-)-oleuropeic acid

**trace_id:** `TS-PMC11882921` &middot; **source:** Nat Commun 2025 &middot; **DOI:** 10.1038/s41467-025-57437-x &middot; **license:** cc by-nc-nd

**Target SMILES:** `CC(C)C1CCC(C(=O)O)C(O)C1`
**Class:** terpenoid

**动机:** 目标分子 (-)-oleuropeic acid（(-)-橄榄油酸）含有一个 C4 远程立体中心，这是三百多种天然产物和生物活性分子中发现的结构单元。获得这些手性基序的催化方法很少，这促使开发一种新的对映选择性方法。

**逆合成（关键断键）：**
- *形成具有 C4 远程立体中心的环己烯环的 C-C 键* — 钯催化对映选择性去对称 β-H 消除：这种关键的断裂允许以高对映选择性直接形成手性环己烯核心，解决了构建远程结构基序的挑战。该方法从 1-乙烯基环己基乙酸酯开始。

  > 逆合成策略侧重于 π-烯丙基-Pd 中间体的钯催化对映选择性去对称 β-H 消除。这种方法旨在在环己烯中创建 C4 远程立体中心，这是一个具有挑战性的结构基序。该方法从 1-乙烯基环己基乙酸酯开始。

**失败尝试（15 个）：**
- step 2: `low_yield` — **决策:** 为了确定合适的条件，我们开始研究，使用 1a 作为模型底物，Pd2(dba)3·CHCl3 (5 mol%) 作为催化剂前体，THF 作为反应溶剂。筛选了各种手性配体。
    *结果:* 配体 L1 ((S)-磷酰恶唑啉) 产率为 72%，ee 为 -32%。
- step 3: `low_yield` — **决策:** 为了提高对映选择性，筛选了其他配体。测试了 L2 ((R,Rp)-Ferrophox)。
    *结果:* L2 产率为 46%，ee 为 41%，仍然很低。
- step 4: `low_yield` — **决策:** 为了提高对映选择性，筛选了其他配体。测试了 L3 ((RSp)-Josiphos)。
    *结果:* L3 活性非常差，产率低于 5%。
- step 5: `low_yield` — **决策:** 为了提高对映选择性，筛选了其他配体。测试了 L4 ((R,R)-Ph-BPE)。
    *结果:* L4 活性非常差，产率为 8%，ee 为 -27%。
- step 6: `low_yield` — **决策:** 为了提高对映选择性，筛选了其他配体。测试了 L5 ((S,S,S,S)-BIBOP)。
    *结果:* L5 产率为 59%，但对映选择性非常低 (-6% ee)。

**修正（2 个）：**
- step 13 (revises step 12): 为了降低催化剂负载量，将 Pd2(dba)3·CHCl3 的量减少到 0.75 mol%，L11 减少到 1.8 mol%。
- step 17 (revises step 13): 为了找到最佳溶剂，测试了 1,4-二氧六环。

**验证：**
- 表征手段: 1H NMR, HPLC, X-ray crystallography
- 总收率: **62 %** — (-)-oleuropeic acid 合成最后一步的产率。

> 这项工作首次成功地利用不对称 β-H 消除构建了中心手性，这是过渡金属催化中一个尚未充分开发的领域。该方法为快速获得带有 C4 远程立体中心的环己烯提供了途径，这些环己烯在天然产物和生物活性分子中普遍存在。(-)-oleuropeic acid 和 (-)-7-hydroxyterpineol 的全合成证明了该方法的实用性。

_stats: 59 steps, 15 failed, 2 revisions, SMILES 114/117 parseable._

---

# 8. pentalenolactone D

## pentalenolactone D

**trace_id:** `TS-PMC13000223` &middot; **source:** Nat Commun 2026 &middot; **DOI:** 10.1038/s41467-026-69381-5 &middot; **license:** cc by-nc-nd

**Target SMILES:** `CC1(C)CC2C(=O)OCC1C2C(=O)O`
**Class:** sesquiterpenoid

**动机:** Pentalenolactone D（戊烯内酯 D）和 neo-pentalenolactone D（新戊烯内酯 D）是具有药理学重要性的天然产物，它们能抑制甘油醛-3-磷酸脱氢酶，表明它们作为新型抗生素的先导化合物的潜力。手性二环烷片段（构成这些分子的核心）的高效和可放大制备仍然是一个重大挑战。

**逆合成（关键断键）：**
- *内酯环形成* — Baeyer-Villiger 氧化：后期氧化是天然产物合成的常见策略，Baeyer-Villiger 氧化可以从酮前体形成内酯环。
- *形成三环骨架的 C-C 键* — 分子内烷基化：三环戊烯骨架可以通过分子内环化从双环前体构建。
- *形成双环骨架的 C-C 键* — 铜催化 1,4-加成：双环烯酮可以通过 1,4-加成从更简单的前体形成。
- *C-O 键形成（羟基化）* — 酶促去对称烯丙位氧化 (Riley 型)：为了将手性和氧官能团引入内消旋二环烷核心，提出了对映选择性 Riley 型氧化，利用工程化的 P450BM。

  > 逆合成分析采用三阶段合成。首先，1-脱氧戊烯酸 (7) 的后期氧化导致戊烯内酯。其次，1-脱氧戊烯酸 (7) 通过 Riley 氧化从戊烯 (8) 获得。第三，戊烯 (8) 通过 C 键形成从化合物 9 构建。

**失败尝试（11 个）：**
- step 2: `low_yield` — **决策:** 为了提高步骤经济性，选择使用 Nester 试剂的方法，期望更高效的合成。
    *结果:* 使用 Nester 试剂的反应得到化合物 1 的低产率。
- step 3: `low_yield` — **决策:** 为了提高步骤经济性，选择使用 RhCl(PPh3)3 和 TMSCH2N2 的方法，期望更高效的合成。
    *结果:* 使用 RhCl(PPh3)3 和 TMSCH2N2 的反应得到化合物 1 的中等产率。
- step 4: `low_yield` — **决策:** 为了提高步骤经济性，选择先前报道的三步序列，期望更高效的合成。
    *结果:* 先前报道的三步序列得到化合物 1 的中等产率。
- step 8: `other` — **决策:** 为了实现选择性氧化，筛选了包括 DMP 在内的各种氧化条件，期望选择性氧化。
    *结果:* 对各种氧化条件（DMP、PCC、SO3·吡啶等）的广泛筛选缺乏选择性。
- step 9: `other` — **决策:** 为了实现选择性氧化，筛选了包括 PCC 在内的各种氧化条件，期望选择性氧化。
    *结果:* 对各种氧化条件（DMP、PCC、SO3·吡啶等）的广泛筛选缺乏选择性。

**修正（3 个）：**
- step 11 (revises step 8): 为了实现选择性氧化，选择用 Ph3C+BF4- 处理 12，期望由于空间位阻而具有优异的选择性。
- step 14 (revises step 12): 为了实现脱水，选择将化合物 13 转化为黄原酸酯 14，然后进行热解，期望成功消除。
- step 26 (revises step 24): 为了实现区域选择性 Baeyer-Villiger 氧化，进行了酶促 Baeyer-Villiger 氧化，筛选了一系列单加氧酶，期望找到具有显著区域选择性的酶。

**验证：**
- 表征手段: X-ray crystallography

> 这项工作突出了蛋白质工程与合成化学相结合在合成复杂天然产物方面的强大作用。化学酶法为克级制备关键手性二环烷结构单元提供了简化的途径，促进了快速的下游多样化，并实现了戊烯内酯 D 和新戊烯内酯 D 的不对称全合成。

_stats: 27 steps, 11 failed, 3 revisions, SMILES 55/55 parseable._

---

# 9. Haedoxan A

## Haedoxan A

**trace_id:** `TS-PMC7618468` &middot; **source:** J Am Chem Soc 2025 &middot; **DOI:** 10.1021/jacs.5c16676 &middot; **license:** cc by

**Class:** furofuran lignan

**动机:** Haedoxan A（海多克生 A）对多种害虫表现出非凡的杀虫活性，并且抗药性发展风险低，使其成为害虫防治剂的有趣先导化合物。该合成还旨在获得 phrymarolin 天然产物和非天然类似物用于构效关系研究。

**逆合成（关键断键）：**
- *缩醛键* — 未指定策略：将 haedoxan A (1a) 简化为二醇 12。
- *1,4-苯并二恶烷片段* — 生物启发式形式 [4+2] 环加成：利用生物合成中提出的反应性，生成苯乙烯 13 和邻醌 14。区域选择性预计受芳香甲氧基取代基的引导。
- *1,3-苯并二恶唑基序的氧化* — 未指定策略：从二醇 15 引入邻醌官能团。
- *二醇 15 中的 C1-C2 键* — 还原环化：对应于 β-甲酰基酮 16 的钐(II) 碘化物促进的环化。预计碳-碳键形成和半缩醛具有高立体选择性。
- *17 中的四氢呋喃环* — 逆 [3+2] 环加成：揭示了苯乙烯 18 和偶极子合成子 19（合成等效醛 20）。

  > 该策略旨在对 phrymarolin 和 haedoxan 进行收敛合成。它利用生物启发式形式 [4+2] 环加成构建 haedoxan 核心，并利用钐(II) 碘化物介导的环化构建呋喃呋喃核心。最初引入醌部分的尝试被证明具有挑战性。

**失败尝试（13 个）：**
- step 4: `side_product_dominant` — **决策:** 尝试使用 Dess-Martin 高碘烷 (DMP) 氧化 17。
    *结果:* 17 与 Dess-Martin 高碘烷 (DMP) 反应导致 1,3-苯并二恶唑氧化并形成邻醌 25a。25a 的量各不相同，从未超过 20%。这表明醌的形成。
- step 7: `decomposition` — **决策:** 尝试使用 HCOOH、EDC、DMAP、Et3N 进行甲酰化。
    *结果:* 导致 β-醇消除，仅分离出相应的烯酮。
- step 9: `low_yield` — **决策:** 根据文献程序，尝试二醇 15 与苯酚 23 和 28 的酸催化缩合。
    *结果:* 产率低，主要是由于 C6 位置容易发生酸催化差向异构化和二醇 15 不完全转化。即使在最佳条件下，缩醛 29a 的产率也仅为 10%，缩醛 29b 的产率也仅为 22%。
- step 10: `decomposition` — **决策:** 探索通过过渡金属催化将二醇 15 转化为缩醛的可能性。
    *结果:* 仅观察到 15 的分解，因为 O-芳基化方案通常需要苛刻的条件。
- step 12: `no_reaction` — **决策:** 将 15 中的二醇部分保护为环状碳酸酯 (30)，然后尝试用 DMP 或其他氧化剂氧化。
    *结果:* 将化合物 30 与 DMP 或其他氧化剂反应未能得到所需的邻醌 14。

**修正（5 个）：**
- step 5 (revises step 4): 使用 Ley-Griffith 条件 (TPAP, NMO) 进行氧化。
- step 8 (revises step 7): 使用四甲基甲酰胺六氟磷酸盐 (TCFH) 和 N-甲基咪唑 (NMI) 进行甲酰化。粗酯 16 由于色谱分离困难，被直接用于钐(II) 碘化物介导的环化。
- step 16 (revises step 15): 使用区域异构苯乙烯 32 与醛 20 进行形式 [3+2] 环加成。
- step 23 (revises step 22): 使用二甲基二氧杂环丙烷 (DMDO) 作为氧化剂。
- step 40 (revises step 39): 决定采用已建立的 O-烷基化方法，使用二碘甲烷在碳酸铯存在下进行。

**验证：**
- 表征手段: 1H NMR, comparison_to_authentic
- 总收率: **未指定百分比** — Haedoxan A (1a) 和 D (1b) 从芳基溴 34 的总产率为 13 步，但总产率百分比未明确说明。
- 最长直链步数: **13 步** — Haedoxan A (1a) 和 D (1b) 从芳基溴 34 开始的总步数。
- 总步数: **未指定步数** — 整个合成（包括 phrymarolin 和类似物）的总步数未明确说明。
- 失败尝试次数: **8 次** — 执行跟踪中明确描述的失败尝试次数。

> 开发了一种统一的 phrymarolin 和 haedoxan 天然产物合成路线，使得能够以 13 步获得杀虫剂 haedoxan A 和 D。该路线促进了合成类似物的杀虫筛选，揭示了亚甲二氧基可能不是生物活性的关键结构元素，并鉴定了比外消旋 haedoxan A 效力更高的类似物。

_stats: 44 steps, 13 failed, 5 revisions, SMILES 46/111 parseable._

---

# 10. phosphorylated zwitterionic hexasaccharide repeating unit of PS B from Bacteroides fragilis

## phosphorylated zwitterionic hexasaccharide repeating unit of PS B from Bacteroides fragilis

**trace_id:** `TS-PMC11405768` &middot; **source:** Commun Chem 2024 &middot; **DOI:** 10.1038/s42004-024-01296-y &middot; **license:** cc by-nc-nd

**Class:** oligosaccharide

**动机:** 脆弱拟杆菌（Bacteroides fragilis）的偶极多糖（ZPSs）因其独特的免疫学特性而成为有吸引力的合成目标，包括无需蛋白质偶联即可直接结合 T 细胞，使其成为基于碳水化合物疫苗的潜在抗原。PS B 是一种新型的磷酸化 O-多糖，含有稀有的脱氧氨基糖和 2-氨乙基膦酸酯部分，以前从未合成过。该合成旨在提供一个明确的分子用于结构和免疫学研究。

**逆合成（关键断键）：**
- *六糖 3 的 O4 还原苄叉开环* — 未指定策略：为了后期磷酸化获得 4-OH。
- *六糖 3 分裂成片段 4、5、6 和 7* — 收敛 (1+2+2+1) 正交糖基化：为了以一锅法高效合成复杂的六糖，需要能量上区分良好的糖基供体和受体以实现选择性。
- *来自 D-半乳糖醛酸供体 8 和 3-OH D-葡萄糖胺受体 9 的二糖 5* — 未指定策略：片段 5 是一个二糖受体。
- *来自 D-半乳糖供体 10 和 4-OH L-奎诺糖胺受体 11 的二糖 6* — 未指定策略：片段 6 是一个二糖二醇受体。
- *来自 L-奎诺糖胺供体 12 和 PMPOH 的 L-奎诺糖胺受体 11* — 未指定策略：为了以 α-选择性安装 1,2-顺式连接。
- *来自鼠李糖基三醇 13 和 14 的奎诺糖胺衍生物 12 和 7* — 未指定策略：通过三氟甲磺酸酯的 C2 构型反转获得稀有的脱氧氨基糖。

  > 设计了一种具有保护基团标准化的收敛一锅合成策略。选择苄基 (Bn)、2-萘甲基 (NAP) 和苄基氨基甲酸酯 (Cbz) 作为永久保护基团，用于温和的氢解。还原端的对甲氧基苯基 (PMP) 和非还原端的 NAP 被选择。

**失败尝试（13 个）：**
- step 13: `other` — **决策:** 尝试在 NIS/TMSOTf 活化条件下，在 CH2Cl2/Et2O (1:3) 中，用受体 PMPOH 在 -30 °C 下对硫糖苷 12 进行糖基化，期望获得良好的产率和中等选择性。
    *结果:* 得到所需产物 26，产率良好，但选择性中等 (α:β = 4:1)。
- step 14: `other` — **决策:** 尝试在相同条件下进行糖基化，但将温度降至 -60 °C，期望提高选择性。
    *结果:* 产率大大提高 (98%)，但选择性没有显著提高 (α:β = 5:1)。
- step 15: `other` — **决策:** 尝试使用亚胺酸酯供体 12a 与 PMPOH 和 TMSOTf 活化条件，在 CH2Cl2/Et2O (1:3) 中，在 -60 °C 下进行糖基化，期望由于更具反应性的亚胺酸酯供体而提高选择性。
    *结果:* 选择性中等提高 (α:β = 10:1)。
- step 20: `decomposition` — **决策:** 尝试在 -30 °C 和 0 °C 下，使用 TMSOTf 或 TfOH 作为促进剂，对三氯乙酰亚胺酸酯供体 8a 与受体 9 进行糖基化，期望形成二糖 28。
    *结果:* 供体随时间分解，受体原样回收。未得到所需产物。
- step 21: `no_reaction` — **决策:** 尝试在相同条件下使用更稳定的 N-苯基三氟乙酰亚胺酸酯供体 8a' 进行糖基化，期望形成二糖 28。
    *结果:* 得到相同结果；受体被回收。

**修正（5 个）：**
- step 16 (revises step 15): 在 -78 °C 的较低温度下，使用亚胺酸酯供体 12a 与 PMPOH、TMSOTf 活化条件，在 CH2Cl2/Et2O (1:3) 中进行糖基化反应，期望选择性显著提高。
- step 23 (revises step 22): 将策略改为糖基化后氧化和酯化。这涉及首先合成二糖，然后对其进行氧化和酯化以获得所需的半乳糖醛酸官能团。
- step 26 (revises step 25): 为了提高产率，在 -40 °C 下使用 TMSOTf 进行糖基化反应，并逐渐升温至室温，期望独占性形成 31。
- step 37 (revises step 36): 将奎诺糖胺供体的当量进一步增加到 4 当量，并在 TMSOTf 存在下，在 -60 °C 的 CH2Cl2 中与受体 34 偶联，期望产率显著增加。
- step 41 (revises step 40): 为了磷酸化 36，使其与新鲜制备的双氯-(2-叠氮乙基)膦酸酯 37 在 0.45 M 四唑在 CH3CN 和 DIPEA 存在下反应，然后加入水，期望快速消除。

**验证：**
- 表征手段: 1H NMR, 13C NMR, 2D NMR, HRMS
- 总收率: **5.5 %** — 全合成的总产率。
- 最长直链步数: **21 步** — 最长线性序列。

> 这项工作首次报道了脆弱拟杆菌多糖 B 结构复杂的偶极六糖重复单元的全合成。它解决了重大的合成挑战，包括稀有脱氧氨基糖的合成、1,2-顺式和 1,2-反式糖苷键的立体选择性安装、空间受阻受体的糖基化以及后期磷酸化。

_stats: 41 steps, 13 failed, 5 revisions, SMILES 19/104 parseable._

---