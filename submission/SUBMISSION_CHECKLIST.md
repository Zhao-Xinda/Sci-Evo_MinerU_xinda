# 提交清单核对

把赛题要求的每一项（含加分项）映射到本提交目录中具体文件。

## 必需项

| # | 赛题要求 | 在本提交中的位置 |
|---|---|---|
| 1 | **数据集文件**，提供互联网可访问开源链接，明确标注 **Sci-Align 或 Sci-Evo** | ✅ **https://github.com/Zhao-Xinda/Sci-Evo_MinerU_xinda** — 237 条 trace 已通过 GitHub 公开；详见 [`dataset_link.md`](dataset_link.md)；标注为 **Sci-Evo** |
| 2 | **原始数据样例**（可选但建议） | [`original_data_samples/`](original_data_samples/) — 5 篇用于构造样本 trace 的源 OA PDF |
| 3 | **完整技术报告**：含数据集简介、设计方案、结构说明（字段/来源/标注/质量评估）、≥10 条完整样例、使用方式、应用场景 | [`technical_report.md`](technical_report.md) — 12 节，覆盖全部要求；§6 含 10 个 worked example，深度叙事在 [`walkthroughs/`](walkthroughs/) |
| 4 | **数据集构建方案** — 处理/加工说明，可追溯、可解析、合规；**禁止虚构科学**；**禁止使用未授权数据** | [`technical_report.md`](technical_report.md) §4（pipeline）+ §10（合规/伦理）；每条记录的 `_provenance` 区块记录每个模型、batch_id、时间戳 |
| 5 | **MinerU 使用方式** | [`MINERU_USAGE.md`](MINERU_USAGE.md) — 调用端点、产物结构、逐 trace provenance、稳健性增强；`technical_report.md` §9 也有 |
| 6 | **相关成果或影响力**（必须 2024-12 之后） | [`technical_report.md`](technical_report.md) §11；本数据集构建于 2026 年，所收录论文涵盖 2018–2026 |

## 加分项

| 项目 | 状态 |
|---|---|
| 代码开源到 **GitHub** | ✅ **https://github.com/Zhao-Xinda/Sci-Evo_MinerU_xinda** — MIT（代码）+ CC-BY-4.0（数据集标注与 Schema），详见 [`code_repo.md`](code_repo.md) |
| **PPT / 视频** 介绍项目 | ⏳ 提交前补充 |

## 自审 — 数据集是否真正体现 Sci-Evo

> *"Sci-Evo 数据让模型模拟真实的科学探索过程，侧重推理、试错与决策。单元结构必须记录完整的科研闭环（问题→假设→方法→实验→调整），并**明确允许失败与修正**。"* — 赛题节选

| Sci-Evo 特征 | 本数据集是否体现 | 位置 |
|---|---|---|
| 闭环科研流程（目标 → 策略 → 执行 → 验证） | ✅ | 顶层结构：`target` → `retrosynthetic_strategy` → `execution_trace[]` → `validation` |
| 多步决策 / 推理链 | ✅ | 每步都含 `thought = {background, gap, decision}` 三元组 |
| 明确允许失败 | ✅ | `outcome.valid = false` 是一等公民；`failure_mode` 类型化枚举；**64 %** 的 pilot trace 含 ≥1 个 failed_attempt — 目标是 30 % |
| 明确表达失败后的修正 | ✅ | `action = "revision"` + `revises_step_id` 指针；pilot 共有 **88** 个修正步 |
| AI-Ready（清晰 schema、机器可读） | ✅ | JSON-Schema Draft 2020-12 在 [`schema/`](schema/)；pilot 100% 校验通过；人类可读说明在 `schema/SCHEMA.md` |
| 可审计 / 非虚构 | ✅ | 98 % 步骤锚定到 verbatim `evidence.text_span`；每条记录通过 DOI 反指同行评议源；每个 MinerU 产物可通过 `result_zip_url` 重取 |

## 提交前最终自检

- [x] [`dataset_link.md`](dataset_link.md) 中的公开数据集链接可访问 — GitHub 仓库已就位
- [x] [`code_repo.md`](code_repo.md) 中的 GitHub 链接可访问 — https://github.com/Zhao-Xinda/Sci-Evo_MinerU_xinda
- [ ] [`samples/`](samples/) 下 10 条样本 trace JSON 全部能解析、且通过 [`schema/sci_evo_total_synthesis.schema.json`](schema/sci_evo_total_synthesis.schema.json) 校验
- [ ] [`original_data_samples/`](original_data_samples/) 下的 PDF 都能打开并对应到正确 DOI
- [ ] 每条样本的 `_provenance` 区块中的 MinerU `batch_id` 真实有效（可通过 `result_zip_url` 复取）
- [ ] 技术报告无未填充的 `{VARS}` 占位符
- [ ] 所有许可信息都明确说明（标注与 Schema 用 CC-BY-4.0；每篇论文 OA 许可逐条保留）
