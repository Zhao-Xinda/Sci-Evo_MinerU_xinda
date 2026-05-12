# Worked Example — *(±)*-Lappaceolides A 与 B

> **Trace：** [`TS-PMC12519463`](../samples/PMC12519463.trace.json)
> **来源：** Pallerla, Hakola, Härkönen & Siitonen, *Org. Lett.* **2025**, 27, 11149–11151. DOI [10.1021/acs.orglett.5c02445](https://doi.org/10.1021/acs.orglett.5c02445). 许可：CC-BY。
> **MinerU：** API `vlm`，batch `de091bba-…`。**Trace 抽取：** `google/gemini-2.5-flash`（长上下文）。

本文档展示一篇 OA 全合成论文如何被处理成一条 Sci-Evo trace。我们选 Lappaceolides A 与 B 不是因为它路线最长（恰恰相反 — 含表征只有 5 步），而是因为**所有 Sci-Evo 设计决策都在这条小尺寸 trace 中得到充分展示**：结构化逆合成树 + 一个明确列出 13 种试剂组合的失败尝试 + 类型化 `revision` + 最终的动力学控制洞见 — 这正是 AGI4S 模型需要学会**不重蹈覆辙**所要的数据。

---

## 1. 目标分子

**Lappaceolides A 与 B** 是 Ragasa 等人从红毛丹（*Nephelium lappaceum*）中分离的二聚单萜内酯。结构上是 *cis* 稠合的 **dioxabicyclo[3.3.0]octane**，骨架两侧各带一个 γ-丁内酯 — 三个连续的立体中心连接了二聚的两侧。

```
Target SMILES（RDKit canonical）：
    O=C1C[C@@]2(CO1)CO[C@@]1(CO)CC(=O)O[C@@H]21
```

Ragasa 的原始论文提出了**生源假说**：lappaceolides 由更简单的单体 *siphonodin* 经氧化同型二聚而来。这一生源路径只在纸面上成立。合成化学家给自己定下了一个量化目标：*"实现 lappaceolides A 与 B 的仿生全合成（外消旋），从 siphonodin 单步合成完成，从而验证所提出的生源路径。"*

这正是 Sci-Evo 想捕获的问题：**价值不只在于这个分子合成出来了，而在于"为什么、怎么"的结构化论证。**

---

## 2. 逆合成策略（已抽出）

trace 记录了 **2 个关键 disconnection**：

| # | 键 | 命名策略 | 理由 |
|---|---|---|---|
| 1 | 双环醚的 C3–O 键 | *oxa-Michael*（反演） | 给出 dimeric diol **4** |
| 2 | dimeric diol **4** → 两分子 siphonodin（**3**） | *vinylogous Michael*（反演） | 与提出的同型二聚假说一致 |

两个 disconnection 汇成一个操作性假设：*若两个反演箭头都成立，那么在正向方向上一个单步的 **vinylogous-Michael / oxa-Michael domino** 就应该能从两份 siphonodin 直接装出 lappaceolides*。这正是 `retrosynthetic_strategy.rationale` 字段记录的：

> *"逆合成基于 Ragasa 提出的 siphonodin 同型二聚假说，把 vinylogous Michael 与 oxa-Michael 两个 disconnection 合并为一个正向 domino 反应。"*

`is_convergent = true`；尽管两个组成片段是同一分子，但策略形式上是汇聚的（两个片段汇合）。

---

## 3. 执行轨迹

5 步 trace 讲了一个紧凑的故事。

### Step 1 — Forward reaction：可放大的单体合成

`action: forward_reaction` &middot; valid: true &middot; yield: 78%

> *"为合成 siphonodin (3)，将 dihydroxyacetone (7) 与 ylide 8 通过 Wittig-olefination–lactonization domino 反应处理，期望获得高收率与可放大性。"*

substrate SMILES `O=C(CO)CO` 是 **dihydroxyacetone 的 canonical SMILES** — 重要的是，prompt 中的试剂字典纠正了 LLM 早期错误猜测的 `O=C(O)CCO`（3-羟基丙酸）。条件记录在 `reaction` 块：CH₂Cl₂、室温、24 h。outcome 注明**多克级可放大**，预示作者最终选择此路线的原因。

### Step 2 — **Failed attempt**：13 种试剂均无反应

`action: failed_attempt` &middot; **valid: false** &middot; `failure_mode: no_reaction`

这一步是数据集的核心立意。Sci-Evo schema 要求失败必须作为一等数据保留，而不是从已发表记录中抹去。trace 完整记录了作者尝试过的整个网格：

> *"在多种溶剂下、室温或加热条件下、用一系列碱与酸性添加剂尝试 3 的二聚化，期望发现能驱动该 domino 反应的条件。"*

`reaction.reagents` 数组列出了 13 种尝试：

```
K₂CO₃, Na₂CO₃, Cs₂CO₃, TBAF, Et₃N, DBU, NaH, DABCO, NaHMDS, KOtBu,
Zn(OTf)₂, Amberlyst 15, p-TsOH
```

outcome 来自论文原文 verbatim：

> *"… 未观察到 3 向 lappaceolides 的可检测转化（详见 SI）。"*

**这种失败记录在 USPTO/ORD 这类"成功反应"数据集中根本不会出现**。在仅成功数据上训练的模型只会重蹈覆辙。在含此步骤的数据上训练的模型则能识别：对这一类底物，标准碱催化与 Brønsted 酸催化的二聚化是死胡同。

### Step 3 — **Revision**：复用 Lawrence 课题组的条件

`action: revision` &middot; `revises_step_id: 2` &middot; valid: true（部分） &middot; yield: 5%、dr 54:46

> *"复用 Lawrence 课题组的条件（20 mol% K₂CO₃，1,2-DCE，70 °C，12 h），期望观察到部分转化。"*

这是教科书式的"先借再优化"：作者**引用**了 Lawrence 课题组在 (-)-angiopterlactone B 上对结构同源体系做过的 Michael / oxa-Michael 级联工作，trace 把这个引用编码进 `references`，并通过 `revises_step_id` 反指步骤 2 — 这条 trace 因此读起来就是 **失败步 → 引文先验 → 恢复** 的清晰路径。收率仅 5%、立体选择基本为零（54:46），但**首次见到反应"活了"** — 反应确实能跑，动力学条件与步骤 2 探索过的不同。

### Step 4 — Forward reaction：优化条件

`action: forward_reaction` &middot; valid: true &middot; yield: 30%、dr 3:2

> *"做大量优化，重点在碱与溶剂；最终用 10.0 当量 Cs₂CO₃，1,2-DCE，85 °C，4 h，期望提升转化率与收率。"*

注意这里的 stoichiometry 已经是结构化 dict — `stoichiometry: { "Cs₂CO₃": "10.0 equiv" }` — 这正是 pilot 阶段 bug 修复表中的第 2 项（schema bug-fix）。

`outcome.observation` 包含 verbatim 的**动力学控制洞见** — *"… 然而 1 与 2 的收率、转化、dr 在批间变化（8–30%、75–100%、dr 3:2–2:3）。反应时间长于 4 h 反而使收率下降，表明 1 与 2 在该温度下的反应条件中不稳定。"*

这一句就是模型需要学习的一课：**该二聚化在升温下可逆，所以反应时间过长反而更糟，而不是更好**。如果没有 `evidence.text_span` 把这一观察锚定到原文，模型学到的就无法核实。有了它，整个数据集是可审计的。

### Step 5 — Characterization

`action: characterization` &middot; valid: true

标准收尾 — 洗脱液筛选解决纯化难题（典型 EtOAc/hexane、DCM/MeOH 系统都无法把残留 siphonodin 与产物分开，最终需要 Et₂O–MeCN–DCM 1:1:3 三元系统）+ 用 ¹H/¹³C-NMR 与 Ragasa 分离的天然样本对比 + 共晶单晶 X-ray。trace 同时记录了**纯化难题**与**对比验证**。

---

## 4. Validation 块

```json
"validation": {
  "characterization": ["1H NMR", "X-ray crystallography", "comparison_to_authentic"],
  "metrics": {
    "Overall Yield":        { "value": 30, "unit": "%", "interpretation": "二聚化最终步" },
    "Longest Linear Steps": { "value": 2,  "unit": "steps", "interpretation": "从商业 DHA 起" },
    "Total Steps":          { "value": 2,  "unit": "steps" },
    "Failed Attempts Count":{ "value": 1,  "unit": "attempts" }
  },
  "significance": "首例 lappaceolides A 与 B 的全合成。为'lappaceolides 是 siphonodin 二聚体'的生源假说提供进一步证据。"
}
```

---

## 5. 这条 trace 的训练价值

消费这条 trace 的模型至少能拿到 3 条可训练信号：

1. **战略键分析。** vinylogous-Michael / oxa-Michael **domino** 是把两个反演箭头压缩成一个正向步骤的战略动作。这一模式可推广到二聚类天然产物。
2. **失败空间的类型化地图**：13 种常见碱与 Brønsted 酸**不能**驱动这一级联反应，标记为 `failure_mode: no_reaction`。这正是路线规划器需要的**排除性知识**。
3. **动力学洞见** — 产物在反应温度下不稳定，所以反应时间长反而收率下降。`evidence.text_span` 把这一洞见锚回论文原文，下游审计者可以确认模型不是在编造。

所有这些都是**单 schema 下的机器可读 JSON**，并通过原始 MinerU `batch_id`、各阶段 OpenRouter 模型 id、源论文的 OA 许可，完整保留 provenance。

---

## 6. Provenance 摘要

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
