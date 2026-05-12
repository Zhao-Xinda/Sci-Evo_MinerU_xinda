# Sci-Evo 全合成轨迹 — Schema 参考

**权威定义文件：** [`sci_evo_total_synthesis.schema.json`](sci_evo_total_synthesis.schema.json)（JSON-Schema Draft 2020-12）。
**Schema 版本：** `1.0.0`
**记录单元：** 一篇全合成论文产生一份 `<PMCID>.trace.json`。

本文档是 JSON Schema 的人类可读伴侣文档。如二者不一致，**以 JSON Schema 为准**，并请尽快修正 Schema。

---

## 设计哲学

本 Schema 用于捕获**一篇全合成论文是怎么被推理、执行、验证出来的** — 而不仅仅是分子和反应。它从赛事方 [`Sci-Evo_tool_case.json`](../other/Sci-Evo_tool_case.json) 范例继承了三个核心设计：

1. **逐步结构化的 `[Background] / [Gap] / [Decision]` 推理三元组** — 每个轨迹动作都带 thought 三元组，让在该数据上训练的模型学会模拟科学审议过程，而不只是模仿结果。
2. **`valid: false` 是一等公民** — 失败尝试不被删除；它们与成功步骤并列，带类型化 `failure_mode`，对应的恢复步骤 `revision` 通过 `revises_step_id` 指针反指。
3. **可量化 `metrics` 的 `{value, unit, interpretation}` 三元组** — 验证本身也是结构化数据。

并在此基础上做了三项化学领域 native 化扩展：

- **`Reaction` 是一等对象**，不是塞在 `parameters` 里的自由 dict — 含 `substrate_smiles`、`product_smiles`、`rxn_smiles`、`named_reaction`、`reagents`、`catalyst`、`ligand`、`solvent`、`temperature`、`time`、`stoichiometry {reagent: amount}`。
- **DAG 片段结构** — `retrosynthetic_strategy.fragments[]` 配合每步的 `fragment_id`，可以表达汇聚式合成（不仅是线性合成）。
- **类型化 `failure_mode` 枚举** — `low_yield`、`wrong_stereochemistry`、`decomposition`、`no_reaction`、`epimerization`、`reactor_clogging`、… — 给下游消费者一个明确标签空间可以学习。

---

## 顶层结构

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
  _smiles_qc:              ↘ §6             # 程序化字段
}
```

顶层必填：`trace_id`、`target`、`retrosynthetic_strategy`、`execution_trace`、`_provenance`。（`validation` 是**推荐**字段而非强制 — pilot 阶段宽松规则；部分论文没有可独立切分的 validation 章节。）

---

## §1 `target` — 被合成的目标

```yaml
target:
  name:                    str         # "(-)-strychnine"、"Lappaceolides A and B"
  smiles:                  str         # RDKit canonical isomeric SMILES
  inchi:                   str?        # 可选
  inchi_key:               str?
  natural_product_class:   str?        # "macrolide"、"indole alkaloid"、"terpenoid"
  structural_features:
    molecular_weight:      number?
    stereocenters:         int?
    ring_systems:          str?        # "fused 6-6-6 + bridged 7"
    key_motifs:            [str]?      # ["quaternary stereocenter", "vicinal diol"]
  motivation:              str         # 为什么合成这个 — 生物活性、规模需求等
  prior_syntheses:         [           # 引用的前人合成
    { lead_author, year, doi?, key_strategy }
  ]
  success_criteria:
    yield_target_percent:    number|str?
    lls_target:              int|str?
    scale_target:            str?
    stereochemistry_required: str|bool?
    free_text:               str?
```

必填：`name`、`smiles`、`motivation`、`success_criteria`。

---

## §2 `retrosynthetic_strategy` — 纸面上的策略

```yaml
retrosynthetic_strategy:
  is_convergent:        bool          # true 表示独立片段最终合并的汇聚式
  key_disconnections:   [             # 高层断键
    bond_description:   str           # "C11-C12 bond"、"macrolactonisation at C1-O17"
    named_strategy:     str?          # "NHK"、"RCM"、"Suzuki"、"Diels-Alder"
    reasoning:          str           # 为什么这样断 — 战略键、FGI、立体控制、汇聚
    alternatives_considered: [        # 纸面上考虑过但弃用的备选
      { strategy, rejected_because }
    ]
  ]
  fragments:            [             # 汇聚式子路线
    { fragment_id, smiles, role, comes_from }
  ]
  rationale:            str?          # 整体策略说明
```

必填：`is_convergent`、`key_disconnections`。

---

## §3 `execution_trace` — 时序执行轨迹

每一步是一个动作，含结构化推理 + （若适用）化学转化 + 结果。

```yaml
execution_trace[]:
  step_id:        int                 # 1, 2, 3, … （按论文顺序）
  fragment_id:    str | null          # 哪条子路线；null 表示主合并线
  action:         enum                # 见 §3.1
  thought:                            # [Background]/[Gap]/[Decision] 三元组
    background:   str                 # 截至当前已知 / 已完成
    gap:          str                 # 还需要解决的问题
    decision:     str                 # "为达成 X，选择 Y，期望 Z"
  reaction:                           # 当 action 涉及一个反应时必填（§3.2）
    ↘ §3.2
  outcome:                            # 见 §3.3
    valid:        bool                # ★ false 标记失败尝试
    yield_percent: number|null?
    ee_percent:   number|null?
    dr:           str|number?         # "10:1"、">20:1"、或数值
    regio_selectivity: str?
    failure_mode: str|null            # 当 valid=false 时必填
    observation:  str
  revises_step_id: int|null           # 当 action="revision" 时必填
  references:    [str]                # 外部引用
  evidence:                           # 强烈推荐
    text_span:    str                 # 论文原文 / SI 中的 verbatim 引用
    page:         int|null?
    section:      str|null?
    image_refs:   [str]?              # 含相关结构 / 反应图的 MinerU 图像文件名
```

### §3.1 `action` 枚举

| 值 | 用法 |
|---|---|
| `retrosynthetic_analysis` | 一个规划 / 纸面分析步（无湿实验） |
| `forward_reaction` | 一个达成 decision 目标的反应 |
| `failed_attempt` | 一个尝试过但未达到目标的反应 — 配合 `outcome.valid=false` 与类型化 `failure_mode` |
| `revision` | 替换某个失败尝试的后续步骤 — 必须设置 `revises_step_id` |
| `characterization` | NMR / MS / X-ray 等对中间体或终产物的确认 |
| `scale_up` | 对已验证反应的后期放大 |
| `literature_review` | 一个直接驱动下一步决策的文献检索 |
| `hypothesis_formation` | 纯假设形成步（少见） |

### §3.2 `reaction` 块（化学领域 native）

当 `action` ∈ {`forward_reaction`, `failed_attempt`, `scale_up`} 时必填：

```yaml
reaction:
  substrate_smiles:    [str]          # RDKit canonical
  product_smiles:      [str]
  rxn_smiles:          str|null?      # "A.B>>C"
  named_reaction:      str|null?      # "Suzuki"、"Diels-Alder"、…
  bond_formed:         str|null?      # "C-C"、"C-N"、"C=C"、…
  bond_broken:         str|null?
  reagents:            [str]?         # 自然语言列表
  catalyst:            str|null?
  ligand:              str|null?
  solvent:             str|null?      # SMILES 或名称（如 "1,2-DCE"、"THF"）
  temperature:         str|null?      # "85 °C"、"rt"
  time:                str|null?      # "4 h"
  atmosphere:          str|null?      # "Ar"、"N2"
  scale:               str|null?      # "multigram"
  stoichiometry:       { reagent: amount_str }   # ★ 是 dict/object，不是 string
```

### §3.3 `failure_mode` 推荐取值

当 `outcome.valid = false` 时，`failure_mode` 推荐取以下之一：

```
low_yield · no_reaction · wrong_regiochemistry · wrong_stereochemistry ·
epimerization · decomposition · side_product_dominant · scope_limited ·
scale_limited · incompatible_protecting_group · purification_failed ·
characterization_inconclusive · reactor_clogging · other
```

Schema **不**强制此枚举（任意 string 都接受），但下游消费者应该按上表 canonical 化。该列表在 pilot 抽取过程中持续扩张，吸收了化学专属的失败类型（例如 `reactor_clogging` 来自连续流合成文献）。

---

## §4 `validation` — 终产物验证

```yaml
validation:
  characterization: [str]             # ["1H NMR"、"X-ray"、"comparison_to_authentic"…]
  metrics:
    "Overall Yield":          { value, unit, interpretation }
    "Longest Linear Steps":   { value, unit, interpretation }
    "Total Steps":            { value, unit, interpretation }
    "Failed Attempts Count":  { value, unit, interpretation }
    # 允许追加任意指标名
  comparison_to_prior:  str?          # 与前人路线的差别
  significance:         str           # 最终评价段
```

`metrics` 是按指标名为键的自由 map；推荐 canonical key：`Overall Yield`、`Longest Linear Steps`、`Total Steps`、`ee`、`Largest Scale`、`Failed Attempts Count`。

---

## §5 `_provenance` — 完整审计链路

```yaml
_provenance:
  source:
    doi_or_id:    str
    pmcid:        str?
    title, authors, journal, year, license, pdf_url
  mineru:
    method:           "MinerU API (cloud)" | "MinerU OSS (local)" | "Sci-Base (pre-parsed)"
    model_version:    str       # 如 "vlm"
    batch_id:         str       # MinerU batch id — 直接重取句柄
    result_zip_url:   str
    parsed_at:        ISO-8601 datetime
  extraction_models:
    [{ stage: "image_smiles" | "trace_extraction" | … , name, version }]
  validators:
    [{ name: "RDKit canonicalize" | "PubChem name lookup" | … , result }]
  human_reviewed:   bool        # 默认 false；人工 QC 后置 true
  review_notes:     str?
```

---

## §6 `_smiles_qc` — 程序化 QC 摘要

由 `src/validate_smiles.py` 在 trace 抽出后追加。**不是 LLM 的输出。**

```yaml
_smiles_qc:
  total:               int          # 触及的 SMILES 字符串总数
  parseable:           int          # RDKit 解析成功
  canonicalized:       int          # canonical 化后形态发生变化
  invalid:             int
  overridden_by_name:  int          # 通过试剂字典 / PubChem 回填的次数
  invalid_examples:    [str]
  overrides:           [{ field, named_compound, was, now, reason }]
  pubchem_fills:       [{ field, name, smiles, cid }]
```

---

## 验证

```python
import jsonschema, json
schema = json.loads(open("schema/sci_evo_total_synthesis.schema.json").read())
trace  = json.loads(open("data/traces/PMC12519463.trace.json").read())
jsonschema.Draft202012Validator(schema).validate(trace)
```

Pilot 50 条 trace 全部通过 schema 校验，详见 `src/analyze_quality.py` 的报告。

---

## 软约束（推荐遵循，不在 schema 强制）

这些约束会在 `analyze_quality.py` 的报告中以提示形式呈现，不会让 Schema 校验失败：

- 当 `outcome.valid = false` 时，`outcome.failure_mode` 应被设置。
- 当 `action = "revision"` 时，`revises_step_id` 应指回某个 `outcome.valid = false` 的之前步骤。
- 当 `action ∈ {forward_reaction, failed_attempt, scale_up}` 时，`reaction` 应存在。
- `evidence.text_span` 应是论文原文的 verbatim 子串（审计脚本可校验）。

之所以 v1 不把这些做成硬规则，是为了让部分 / 不完美的 LLM 抽取仍然能通过；下游清洗者可以在 v2 schema 中升级为硬约束。
