# 提交说明 — Sci-Evo 全合成轨迹数据集

**赛道：** Sci-Evo（科学演化数据） — AGI4S 数据构建赛道
**提交截止：** 2026-05-24
**许可：** CC-BY-4.0（数据结构与标注）；每篇论文原始 OA 协议在每条记录中保留

**🔗 代码仓库（GitHub）：** **https://github.com/Zhao-Xinda/Sci-Evo_MinerU_xinda**
（含完整 pipeline 源码、237 条 trace 数据、Schema、技术报告；MIT 代码协议 + CC-BY-4.0 数据协议）

---

## 本提交目录内容

| 路径 | 用途 |
|---|---|
| [`README.md`](README.md) | 本说明 |
| [`technical_report.md`](technical_report.md) | 12 节完整技术报告（已用当前 pilot 数据填充） |
| [`MINERU_USAGE.md`](MINERU_USAGE.md) | MinerU 使用专项说明（HTTP 端点、输出字段、每条 trace 的 provenance） |
| [`schema/`](schema/) | JSON Schema（Draft 2020-12）+ 人类可读的 schema 参考 |
| [`samples/`](samples/) | 10 条代表性完整 trace JSON + 选样清单 `manifest.json` |
| [`original_data_samples/`](original_data_samples/) | 5 篇用作样本的源 OA PDF |
| [`walkthroughs/`](walkthroughs/) | 旗舰范例 + 自动生成的 9 条 worked-example 叙事 |
| [`code_repo.md`](code_repo.md) | 代码仓库（GitHub）位置与复现说明 |
| [`dataset_link.md`](dataset_link.md) | 数据集开源地址（OpenDataLab / Hugging Face） |
| [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) | 把赛题每条要求映射到本目录中具体文件的核对清单 |

---

## 头牌指标（全语料，N=237）

- **237/250 (94.8%)** trace 抽取成功率
- **214/237 (90.3%)** JSON-Schema 校验通过率
- **84%（199/237）** 的 trace 含至少一个作者公开披露的 *failed_attempt*（赛题目标 ≥ 30%，**超 2.8 倍**）
- 总计 **966** 个失败尝试 + **566** 个 revision 修正步骤
- **87%** 记录的 `target.smiles` 已填充（PubChem 名称回查后）
- **99%** 步骤含 verbatim 论文原文 quote（`evidence.text_span`）
- 平均每条 trace **20.1 步**（中位 19，最大 78），总计 **10,899** 个 SMILES
- 一篇论文 → 一条 Sci-Evo trace，schema 校验通过、SMILES RDKit canonical、MinerU/抽取链路完整 provenance 记录

---

## 5 分钟读懂本提交

1. 先粗读 [`technical_report.md`](technical_report.md) §1–§3（理念、schema、数据来源）。
2. 打开 [`samples/PMC12519463.trace.json`](samples/PMC12519463.trace.json) 对照阅读 [`walkthroughs/walkthrough_lappaceolides.md`](walkthroughs/walkthrough_lappaceolides.md) — 这是旗舰范例，5 步 trace 内充分演示了 Sci-Evo 的所有设计决策。
3. 看一两条更大的样本 — 如 [`samples/PMC13014231.trace.json`](samples/PMC13014231.trace.json)（生物素 Biotin，27 步含 6 个失败尝试 + 11 个修正，JACS Au 连续流合成）；[`samples/PMC13000223.trace.json`](samples/PMC13000223.trace.json)（pentalenolactone D，11 个失败尝试）。
4. 翻 [`MINERU_USAGE.md`](MINERU_USAGE.md) 了解 MinerU 集成全过程。

---

## 复现

完整 pipeline 在公开代码仓库（参见 [`code_repo.md`](code_repo.md)）。最简单的端到端冒烟流程：

```bash
git clone https://github.com/Zhao-Xinda/Sci-Evo_MinerU_xinda.git
cd Sci-Evo_MinerU_xinda
cd Sci-Evo_MinerU_xinda
pip install -r requirements.txt
export MINERU_TOKEN=<token>          # 用于云端解析
export OPENROUTER_API_KEY=<key>      # 用于 SMILES + trace 抽取
python src/download_pdfs.py --limit 5
python src/mineru_api.py --pdf-dir data/pdfs/raw --limit 5 \
    --out data/mineru_out/test
python src/process_batch.py \
    --batch-result data/mineru_out/test/batch_*.json
python src/pubchem_lookup.py --traces-dir data/traces
python src/analyze_quality.py
```

幂等 — 在相同输入上重跑会跳过已抽出的 trace。

---

## 合规

- **零虚构化学**：每条记录都通过 DOI 锚定到某篇同行评议的开放获取论文；每个步骤都附带从论文中逐字 quote 的文本。**没有任何实验结果是被编造的**。
- **许可透明**：每篇论文的原 OA 许可保留在 `_provenance.source.license`。聚合后遵循子集中最严格的许可。
- **可复现**：所有模型标识（MinerU `vlm`、OpenRouter `google/gemini-2.5-flash`、RDKit、PubChem）和每个 pipeline 参数都记录在 `_provenance` 中。

## 联系方式

问题、修订或 PR — 请到 GitHub 仓库（链接见 [`code_repo.md`](code_repo.md)）开 issue。
