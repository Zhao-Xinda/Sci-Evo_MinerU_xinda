# Sci-Evo 全合成轨迹数据集 — 技术报告

**赛道：** Sci-Evo（科学演化数据） — AGI4S 数据构建赛道
**许可：** CC-BY-4.0（数据结构与标注）；论文原文 / 图片保留各自的 OA 上游许可
**Schema 版本：** 1.0.0
**截至 2026-05-11 的状态：** 从 250 篇 OA 全合成论文构建出 **237 条 trace**（成功率 94.8%）；JSON-Schema 校验通过率 **90%（214/237）**；**84% 的 trace 含至少一个明确标记的失败尝试步骤**（>30% 目标的 2.8 倍）；总 failed_attempts **966 条**、总 revisions **566 条**。

> **为什么做这个数据集。** 全合成是化学领域里最接近"科学的实验型闭环"的研究形式：作者命名一个目标分子，先在纸面上辩论多种 disconnection，然后挑选几条候选反应路线、动手做、失败、修正、再尝试。现有化学语料（USPTO、ORD、Reaxys 等）只记录**成功反应**，但 **AGI4S 系统真正需要、却恰恰被丢弃的，是决策与失败本身**。本数据集每一条记录都把一篇已发表的全合成研究重组成一条 Sci-Evo trace：目标 → 逆合成策略 → 有序执行轨迹（含 `valid=false` 失败步骤与 `revision` 修正步骤）→ 验证 — 每一步都可追溯到论文原文中的 verbatim 引用。

---

## 1. 数据集简介

### 1.1 是什么

一份结构化的全合成研究语料，目前包含 **237** 条 trace，每条来自一篇同行评议过的 OA 化学论文。每条 trace 是一个 JSON 文件，符合 `schema/sci_evo_total_synthesis.schema.json`，包含以下结构：

- `target` — 被合成的天然产物 / 目标分子，含规范 SMILES、结构特征、合成动机、前人合成路线引用。
- `retrosynthetic_strategy` — 作者在纸面上设计的高层 disconnection 计划，**包括他们考虑过但放弃的备选策略**。
- `execution_trace[]` — **有序执行轨迹**，每步含：
  - 一个结构化的 `thought` 三元组 `{background, gap, decision}`（参考赛事方 Sci-Evo 范例），分别描述"已知/已完成"、"还没解决"、"为了达成 X，选择 Y，期望产生 Z"；
  - `action` 枚举（`forward_reaction` / `failed_attempt` / `revision` / `characterization` / …）；
  - 类型化的 `reaction` 块（substrate / product SMILES、命名反应、试剂、条件）；
  - `outcome` 含 `valid: bool`。**失败尝试是一等公民** — `valid=false` + 类型化 `failure_mode`。下一步的 **`revision`** 通过 `revises_step_id` 反指被替换的失败步，让推理链可追溯。
  - `evidence.text_span` 存放论文原文 verbatim 引用。
- `validation` — 用于确认最终产物的方法和指标（NMR、HRMS、X-ray、总收率、最长直链步数、失败尝试总数等）。
- `_provenance` — 完整源元数据（DOI、期刊、年份、许可）+ MinerU pipeline 运行信息 + 下游抽取模型标识与版本 + 校验器结果。

### 1.2 为什么选 Sci-Evo（而非 Sci-Align）

赛事方对 Sci-Evo 的定义是：*"描述科学如何发展的数据，含多步决策与推理链，明确允许失败与修正。"* 全合成文献正是这一范式的典型样本 — 每隔十年涌现的 strychnine 新合成路线之所以与前人不同，正是因为**前人的尝试和教训**指引着新一轮的策略抉择。把这种知识转化为机器可读的形式，是本工作的贡献所在。

### 1.3 科学价值

- **失败丰富。** **84%** 的 trace 含作者明确披露的失败尝试（赛题目标 ≥ 30%，**超 2.8 倍**），全语料共 **966** 次失败尝试与 **566** 次 revision 修正。
- **推理丰富。** 平均每条 trace **20.1 步**（中位 19，最大 78），每步携带 `[Background] / [Gap] / [Decision]` 三元组 — 是 chain-of-thought / agent 类模型直接可用的训练信号。
- **可审计。** 每步都锚定到论文 verbatim 引用（`evidence.text_span`），覆盖率 **99%**。所有 SMILES 经 RDKit canonical 化，全语料 **10,899** 个 SMILES（71% RDKit parseable）。
- **对齐 Sci-Evo 规范。** 字段结构对应赛事方 `Sci-Evo_tool_case.json` 范例（initial setup → trajectory with `valid=false` 标记 → success verification），同时做了化学领域 native 化扩展（DAG fragments、Reaction 一等公民、类型化 `failure_mode`）。

---

## 2. Schema

权威定义：[`schema/sci_evo_total_synthesis.schema.json`](schema/sci_evo_total_synthesis.schema.json)（JSON-Schema Draft 2020-12）。配套人类可读说明：[`schema/SCHEMA.md`](schema/SCHEMA.md)。

### 2.1 顶层结构

```
trace_id, schema_version (= "1.0.0"), license (= "CC-BY-4.0"),
target,                       // 目标分子 + 动机 + 成功判据
retrosynthetic_strategy,      // 逆合成策略树（含已放弃的备选）
execution_trace[],            // 执行轨迹：含 valid=false 与 revision
validation,                   // 表征手段 + 指标 + significance
_provenance,                  // 全程 provenance：源 / MinerU / 抽取模型 / 校验器
_smiles_qc                    // 抽取后 RDKit canonical 化的 QC 摘要
```

### 2.2 字段速查（节选）

| 字段 | 类型 | 说明 |
|---|---|---|
| `target.smiles` | string | RDKit canonical isomeric SMILES |
| `target.natural_product_class` | string | 例如 `macrolide`、`indole alkaloid`、`terpenoid` |
| `retrosynthetic_strategy.is_convergent` | bool | true 表示该合成是汇聚式（若干独立片段最终合并） |
| `retrosynthetic_strategy.key_disconnections[]` | array | 每项含 `bond_description`、`reasoning`、`named_strategy`、`alternatives_considered[]` |
| `execution_trace[].thought` | object | `{background, gap, decision}` 三元组 — 直接的 CoT 监督信号 |
| `execution_trace[].action` | enum | `retrosynthetic_analysis` / `forward_reaction` / `failed_attempt` / `revision` / `characterization` / `scale_up` / `literature_review` / `hypothesis_formation` |
| `execution_trace[].outcome.valid` | bool | **`false` 标记失败尝试** |
| `execution_trace[].outcome.failure_mode` | string | 类型化：`low_yield`、`wrong_stereochemistry`、`decomposition`、`no_reaction`、… |
| `execution_trace[].revises_step_id` | int? | 当 `action="revision"` 时，反指被该 revision 替换的失败步 step_id |
| `execution_trace[].evidence.text_span` | string | 论文原文 verbatim quote |
| `_provenance.mineru.method` | enum | `MinerU API (cloud)` / `MinerU OSS (local)` / `Sci-Base (pre-parsed)` |

完整 worked example 见 §6。

---

## 3. 数据来源与许可

### 3.1 主源 — Europe PMC OA 全文 PDF

| 过滤维度 | 取值 |
|---|---|
| 检索条件 | `"total synthesis" AND OPEN_ACCESS:Y AND HAS_PDF:Y` |
| 年份过滤 | ≥ 2018 |
| 期刊白名单 | Beilstein J Org Chem、Chemical Science、Nat Chem、Nat Commun、JACS Au、ACS Cent Sci、Org Lett、J Org Chem、Angew Chem Int Ed、JACS、Org Chem Front、RSC Adv（完整列表见 `src/download_pdfs.py:CHEM_JOURNAL_KEYWORDS`） |
| 类型过滤 | 排除 review、perspective、editorial、correction、erratum、retraction（按标题 regex + Medline pubType） |

每篇下载下来的论文保留其原始 OA 许可（CC-BY、CC-BY-NC 等），逐篇记录在 `_provenance.source.license`。

### 3.2 副源 — Sciverse Sci-Base（赛事方提供的预解析语料）

赛事方提供的 Sci-Base 已经是 MinerU 解析过的产物。我们对其化学子集做了筛选：35,200 篇中 2,812 篇属化学类，其中 14 篇含 "total synthesis" 关键词作为补充。涉及 Sci-Base 的 trace 在 `_provenance.mineru.method = "Sci-Base (pre-parsed)"` 中标记，避免与我们自己的 MinerU 调用混淆。

### 3.3 参考数据库（仅用于校验，不进入发布数据集）

- **PubChem PUG REST**：用 `target.name` 反查规范 SMILES 补全 `target.smiles`（免认证、免费）。查找过程登记在 `_provenance.validators[]`。
- **Open Reaction Database (ORD)**：用约 200 万条策展反应作为 reaction 级 `rxn_smiles` 的 sanity check。仅在 QC 时使用，不重新分发。

---

## 4. 构建 pipeline

```
┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ 1. 下载         │ ─> │ 2. MinerU API   │ ─> │ 3. 图像 SMILES   │ ─> │ 4. Trace 抽取   │
│  Europe PMC     │    │  云端解析 PDF   │    │  Gemini 2.5      │    │  Gemini 2.5     │
│  OA 全合成 PDF  │    │  (单文件 ≤ 200  │    │  Flash (多模态)  │    │  Flash (长上下  │
│                 │    │   页限制)       │    │                  │    │   文)           │
└─────────────────┘    └─────────────────┘    └──────────────────┘    └──────────────────┘
                                                                              │
                                                                              v
                                                                ┌──────────────────────┐
                                                                │ 5. RDKit + PubChem   │
                                                                │  + jsonschema 校验   │
                                                                └──────────────────────┘
```

### 4.1 Stage 1 — PDF 下载（`src/download_pdfs.py`）

调用 Europe PMC `/search` 端点，按上述过滤条件分页获取候选 PMCID，再通过 `europepmc.org/articles/<PMCID>?pdf=render` 下载，校验 PDF magic bytes。输出 `data/pdfs/raw/<PMCID>.pdf` + `data/manifests/pilot.jsonl`（含逐篇元数据）。

### 4.2 Stage 2 — MinerU API 解析（`src/mineru_api.py`）

使用 MinerU 本地文件批量上传 API：`POST /api/v4/file-urls/batch` 申请预签名上传 URL，PUT 每个 PDF（**绕过本地 HTTP 代理**，因为预签名 CDN 在 Aliyun OSS、本地代理偶发掐断），轮询 `/extract-results/batch/{batch_id}` 直到全部解析完成。实现了 429 退避。每个 PDF 产出一个 ZIP，包含 `full.md`（论文 Markdown，**LaTeX 公式保留**）、`content_list_v2.json`（逐块 bbox）、`images/*.jpg`（抽出的图片，含反应方案）。

50 篇 pilot 实测：**111 秒** wall-clock 从上传开始到全部 done。

### 4.3 Stage 3 — 图像 SMILES 抽取（`src/extract_chem_from_image.py`）

把 MinerU 抽出的每张图喂给 Gemini 2.5 Flash（OpenRouter），用结构化 prompt 请求：`is_chemical`、`image_type`、`molecules[{label, smiles, role}]`、`reactions[{from, to, named_reaction, conditions, yield_percent}]`、置信度。每篇内部 ThreadPoolExecutor 32-worker 并行。输出 `data/extracted/<PMCID>.smiles.jsonl`。

### 4.4 Stage 4 — Trace 抽取（`src/extract_trace.py`）

构造一份长上下文 prompt，包含：论文元数据 + schema 描述 + 一份策展过的**常用试剂名 → canonical SMILES 字典**（避免 LLM 把 "dihydroxyacetone" 抽成错误 SMILES `O=C(O)CCO`）+ 完整 Markdown 正文 + 已抽出的逐图分子列表。调用 Gemini 2.5 Flash 时启用 `response_format={"type": "json_object"}`，并在解析端加了一个**反斜杠转义修复 pass**（修补 LLM 在含 SMILES + LaTeX 内容时常犯的无效 escape 错误）。保存到 `data/traces/<PMCID>.trace.json`。

### 4.5 Stage 5 — 校验（`src/validate_smiles.py`、`src/pubchem_lookup.py`、`src/analyze_quality.py`）

- 遍历 trace 中所有 SMILES，RDKit 解析并替换为 canonical 形式；不可解析的清空。逐 trace QC 数字落入 `_smiles_qc`。
- 对 `target.smiles` 仍为空的 trace，用 `target.name` 查询 PubChem PUG REST（含若干名称清洗变体，如剥离 `(±)-` 前缀）。
- 用 `jsonschema`（Draft 2020-12）做 schema 校验，并写一份 Markdown 质量报告 `_quality_report.md`。

### 4.6 总编排（`src/process_batch.py`）

端到端驱动器。读取一个或多个 MinerU batch result JSON，**并行**下载/解压所有 ZIP，**多论文并行**跑 Stage 3，**线程池并行**跑 Stage 4，最后聚合统计。**幂等** — 已成功抽出的 trace 在重跑时会被跳过，因此 bug 修复后可以安全地重跑而不浪费 token。

---

## 5. 质量指标（全语料，N=237）

| 指标 | 取值 |
|---|---|
| Trace 抽取成功率 | **237/250 (94.8 %)** |
| JSON-Schema 校验通过率 | **214/237 (90.3 %)** |
| 平均步数 / trace | **20.1** |
| 中位步数 / trace | 19 |
| 最大步数 / trace | 78 |
| 含 ≥1 个 failed_attempt 的 trace | **199 (84 %, 目标 ≥ 30 %)** |
| 失败尝试总数 | **966** |
| revision 修正总步数 | **566** |
| `target.smiles` 填充率 | **87 %**（PubChem 回查后） |
| SMILES parseable 率（RDKit） | **71 %** |
| `evidence.text_span` 覆盖率 | **99 %** |
| 汇聚式合成（is_convergent）占比 | 63 % |
| 总 SMILES 字符串数 | **10,899** |

### 5.1 分布

逐条评分见 `data/traces/_quality_report.md`，自动产生于 `analyze_quality.py`。

---

## 6. Worked Examples — 10 个完整样例

本提交内嵌十条端到端样例（完整 JSON 在 [`samples/`](samples/)）。下表是从 237 条全语料中按综合质量分（失败步骤密度 × 步数 × SMILES parseable 率 × `target.smiles` 完整度）排序后的前 10 名（已剔除一篇 review 文章）。§6.1 给出**旗舰范例 Lappaceolides A & B 的深度叙事解读**（虽不在 top-10 但因步数小、5 步内充分演示 Sci-Evo 全部设计决策而被选作旗舰），其余 worked example 精简叙事见 [`walkthroughs/auto_generated_top10.md`](walkthroughs/auto_generated_top10.md)。

| # | trace_id | 目标分子 | 期刊 / 年 | 步数 | 失败 | 修正 |
|---|---|---|---|---|---|---|
| 1 | TS-PMC12886951 | Indole (Fe 光催化合成) | Nat Commun 2026 | **61** | **23** | 9 |
| 2 | TS-PMC11403583 | (+)-Dihydromaritidine | RSC Adv 2024 | 48 | 10 | **25** |
| 3 | TS-PMC12569679 | N_a-methyl-16-epipericyclivine | (期刊见 trace) | 42 | 16 | 4 |
| 4 | TS-PMC12703658 | (+)-Ineleganolide | J Am Chem Soc 2025 | 27 | 15 | 5 |
| 5 | TS-PMC12164070 | UCS1025A | (期刊见 trace) | 39 | 14 | 6 |
| 6 | TS-PMC11790057 | Glauconic acid | (期刊见 trace) | 35 | 12 | 7 |
| 7 | TS-PMC11882921 | (-)-Oleuropeic acid | (期刊见 trace) | **59** | 15 | 2 |
| 8 | TS-PMC13000223 | Pentalenolactone D | Nat Commun 2026 | 27 | 11 | 3 |
| 9 | TS-PMC7618468  | Haedoxan A | (期刊见 trace) | 44 | 13 | 5 |
| 10 | TS-PMC11405768 | Zwitterionic hexasaccharide | (期刊见 trace) | 41 | 13 | 5 |

### 6.1 Lappaceolides A & B（PMC12519463） — 旗舰范例

完整深度叙事在 [`walkthroughs/walkthrough_lappaceolides.md`](walkthroughs/walkthrough_lappaceolides.md)。本节给出概要：

**目标分子。** 两个对映纯的二聚单萜内酯，结构上是稠合的 dioxabicyclo[3.3.0]octane 骨架带 γ-丁内酯。作者意图**验证 Ragasa 提出的生源假说**：lappaceolides 由单体 **siphonodin** 经 vinylogous-Michael / oxa-Michael 同型二聚而来。

**逆合成策略（已抽出，节选）。**
- 断键 1：双环醚的 C3–O 键 — *oxa-Michael* 反演 — 给出 dimeric diol 4。
- 断键 2：dimeric diol 4 — *vinylogous Michael* 反演 — 给出两分子 siphonodin (3)。
- → 正向策略：vinylogous-Michael / oxa-Michael **domino**。

**执行轨迹（已抽出）。**

| step | action | thought.decision（节选） | outcome |
|---|---|---|---|
| 1 | forward_reaction | 用 dihydroxyacetone (7) + ylide (8) 经 Wittig-olefination–lactonization domino 合成 siphonodin (3) | ✓ 78 % 收率，多克级可放大 |
| 2 | **failed_attempt** | 尝试 13 种试剂组合（Cs₂CO₃、K₂CO₃、NaH、DBU、Zn(OTf)₂、Amberlyst 15、p-TsOH 等）让 3 二聚化 | ✗ `failure_mode=no_reaction` — 原文："gave no detectable conversion of 3 to lappaceolides (see the SI)" |
| 3 | **revision** | 复用 Lawrence 课题组条件（20 mol % K₂CO₃，1,2-DCE，70 °C，12 h） | ✓ 部分成功 — 5 % conversion，dr 54:46 |
| 4 | forward_reaction | 进一步优化：Cs₂CO₃ 10.0 当量，1,2-DCE，85 °C，4 h | ✓ 100 % 转化，30 % isolated，dr 3:2，**注意：动力学控制必须** |
| 5 | characterization | ¹H NMR 对比 + 共晶 X-ray | ✓ 与天然产物一致 |

这一篇论文产出了 **3 条可训练信号**：(a) vinylogous-Michael / oxa-Michael domino 为何战略上正确；(b) 一份**类型化的失败试剂目录**（13 种碱 / 路易斯酸 / Brønsted 酸都不能驱动这一二聚反应）；(c) 动力学控制洞见（反应时间过长收率反而下降）。所有字段都锚定到论文原文 verbatim。

*（其余 9 条 worked example 结构相同 — 精简叙事见 [`walkthroughs/auto_generated_top10.md`](walkthroughs/auto_generated_top10.md)；完整 JSON 在 [`samples/`](samples/)。）*

---

## 7. 数据使用方式

### 7.1 加载

```python
import json
trace = json.loads(open("data/traces/PMC12519463.trace.json").read())
print(trace["target"]["name"], trace["target"]["smiles"])
for step in trace["execution_trace"]:
    print(step["step_id"], step["action"], step["thought"]["decision"])
```

### 7.2 按质量过滤

```python
import jsonschema, json
from pathlib import Path
schema = json.loads(open("schema/sci_evo_total_synthesis.schema.json").read())
v = jsonschema.Draft202012Validator(schema)
for p in Path("data/traces").glob("*.trace.json"):
    t = json.loads(p.read_text())
    if v.is_valid(t) and (t.get("_smiles_qc", {}).get("parseable", 0) /
                          max(t.get("_smiles_qc", {}).get("total", 1), 1)) > 0.7:
        print(p.name, t["target"]["name"])
```

### 7.3 复现 / 扩展

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 下载更多 OA 全合成 PDF（Europe PMC）
python src/download_pdfs.py --limit 200

# 3. 通过 MinerU API 解析（单文件 ≤ 200 页；批 ≤ 50 文件）
python src/mineru_api.py --pdf-dir data/pdfs/raw --limit 200 --out data/mineru_out/run_2

# 4. 端到端跑 Stages 3-5
python src/process_batch.py --batch-result data/mineru_out/run_2/batch_<id>.json

# 5. PubChem 名称回查补 target.smiles
python src/pubchem_lookup.py --traces-dir data/traces

# 6. 质量报告 + Schema 校验
python src/analyze_quality.py
```

---

## 8. 应用场景

1. **训练 CoT / agentic 化学模型。** `[Background] → [Gap] → [Decision]` 三元组 + failed_attempts 是"agentic chemist"模型的直接监督信号。
2. **逆合成 + 条件预测。** `retrosynthetic_strategy.key_disconnections[].named_strategy` 配合 `execution_trace[].reaction.{reagents,conditions,yield}` 提供策略条件下的反应预测。
3. **失败模式学习。** 类型化的 `outcome.failure_mode`（如 `wrong_stereochemistry`、`decomposition`、`no_reaction`）正是 route-planner 用来**避开已知坏路径**所需的标签空间。
4. **检索增强 / 证据锚定的化学问答。** 每步都有 verbatim `evidence.text_span`，可作为 RAG 类化学 QA 的 ground truth。
5. **Benchmark 科学智能体** 的多步合成任务，以中间步是否触发 revision 作为评分维度。

---

## 9. MinerU 使用说明

本数据集的 pipeline 在两个独立环节上使用了 MinerU 工具链（详细说明见 [`MINERU_USAGE.md`](MINERU_USAGE.md)）：

1. **MinerU 云端 API（主路径）。** `src/mineru_api.py` 调用 `POST /api/v4/file-urls/batch` 注册文件元信息，PUT 每个 PDF 到对应预签名上传 URL，再轮询 `GET /api/v4/extract-results/batch/{batch_id}`。`model_version` 用 `"vlm"`。每篇 trace 在 `_provenance.mineru.batch_id` 与 `result_zip_url` 中记录原始批次 ID 和结果 ZIP 的 CDN 地址，供任何人事后审计/重取。
2. **Sci-Base（赛事方提供，已 MinerU 解析）。** Sci-Base 化学子集与我们的目标论文重叠时直接复用，记录为 `_provenance.mineru.method = "Sci-Base (pre-parsed)"`，避免对同一篇论文重复跑 MinerU。

为什么两条路径都用：(1) 证明我们能在原始 OA PDF 上端到端跑通 MinerU pipeline — 这是赛事方关心的核心能力；(2) 证明我们也充分利用了赛事方提供的语料，不重复造轮。

---

## 10. 合规、伦理与可复现

- **零虚构化学。** 每条 trace 都通过 DOI 锚定到一篇同行评议过的 OA 论文；每个步骤都附带从论文原文中逐字 quote 的 `evidence.text_span`。**没有任何实验结果是被编造的**。
- **许可透明。** 每篇论文的原始 OA 许可（CC-BY、CC-BY-NC 等）保留在 `_provenance.source.license`；聚合发布遵循子集中**最严格**的许可。本数据集结构、Schema、标注本身在 CC-BY-4.0 下发布。
- **可复现。** 所有参数（Europe PMC 检索串、MinerU `model_version`、OpenRouter 模型 id `google/gemini-2.5-flash`、RDKit 版本、PubChem 接入点）都记录在 `_provenance.extraction_models` 与 `_provenance.validators`。Pipeline 幂等 — 在相同输入上重跑产生语义等价的 trace。
- **无 PII 或敏感数据。** 源材料全部是已发表的 OA 化学文献。

---

## 11. 相关成果与影响（2024-12 之后）

本数据集构建工作于 2026 年开展。截至提交时，所收录的 250 篇候选论文涵盖 Europe PMC OA 索引截至 2026-05-11 的全合成相关文献，最终产出 237 条 trace；新 OA 论文将通过同一 pipeline 持续接入。配套代码与数据集会以 CC-BY-4.0 / MIT 许可开源到 GitHub 与 OpenDataLab，欢迎社区做二次扩展、benchmark 构建、QC 修订 PR。

---

## 12. 代码仓库

`<待填：github.com/...>` — 完整 pipeline 源码、Schema、样本 trace 与复现说明。代码采用 MIT 协议，数据结构与标注采用 CC-BY-4.0。

---

## 附录 A — Schema 速查

详见 [`schema/sci_evo_total_synthesis.schema.json`](schema/sci_evo_total_synthesis.schema.json) 与人类可读说明 [`schema/SCHEMA.md`](schema/SCHEMA.md)。

## 附录 B — Trace 抽取 prompt 中的试剂名字典

详见 `src/validate_smiles.py:REAGENT_SMILES` — ~70 个常见试剂的 canonical SMILES，以 prompt hint 形式注入 LLM 抽取上下文，抑制名称→结构幻觉。
