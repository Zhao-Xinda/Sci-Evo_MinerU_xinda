# 代码仓库

**仓库地址：** `https://github.com/<待填>` （仓库公开后填写完整 URL — 代码本地已就绪可直接推）

**许可：**
- Pipeline 源代码：**MIT**
- 数据集标注与 JSON Schema：**CC-BY-4.0**

## 仓库结构

```
minerU-1/
├── README.md                                  # 项目概述
├── DATASET_CARD.md                            # Hugging Face / OpenDataLab 风格的数据卡
├── MINERU_USAGE.md                            # MinerU 使用专项说明
├── LICENSE                                    # MIT（代码）+ CC-BY-4.0（标注）
├── requirements.txt
├── docs/
│   ├── technical_report.md                    # 提交版技术报告（模板）
│   ├── technical_report.rendered.md           # 由 render_report.py 用实际指标填充
│   ├── walkthroughs.md                        # 自动生成的 worked example
│   └── walkthrough_lappaceolides.md           # 旗舰范例（手写润色版）
├── schema/
│   ├── sci_evo_total_synthesis.schema.json    # 权威 JSON Schema（Draft 2020-12）
│   └── SCHEMA.md                              # 人类可读 schema 参考
├── src/
│   ├── download_pdfs.py                       # Europe PMC OA PDF 下载（含 review 过滤）
│   ├── mineru_api.py                          # MinerU 云端 API 客户端（批量上传 + 轮询）
│   ├── extract_chem_from_image.py             # 多模态 Gemini 2.5 Flash 抽 SMILES
│   ├── extract_trace.py                       # 长上下文 Gemini 2.5 Flash 组装 Sci-Evo trace
│   ├── validate_smiles.py                     # RDKit canonical 化 + 试剂字典
│   ├── pubchem_lookup.py                      # 名称→SMILES 回查（PubChem PUG REST）
│   ├── process_batch.py                       # 端到端总编排（幂等）
│   ├── analyze_quality.py                     # 质量报告 + JSON Schema 校验
│   ├── extract_walkthroughs.py                # 自动生成 worked example 叙事
│   ├── render_report.py                       # 把 {VARS} 填进 technical_report.md
│   └── filter_sci_base_chem.py                # Sci-Base 化学子集筛选
├── data/
│   ├── pdfs/                                  # 原始 PDF（gitignored；可由 manifest 复现）
│   ├── manifests/                             # 已下载论文的 JSONL 清单
│   ├── mineru_out/                            # MinerU 逐篇产物（gitignored）
│   ├── extracted/                             # 逐图 SMILES JSONL
│   └── traces/                                # *** 数据集本体 ***
└── other/                                     # 赛事方提供的 Sci-Evo 范例（不属于本数据集）
```

## 快速复现

```bash
git clone https://github.com/<待填>
cd minerU-1
pip install -r requirements.txt
export MINERU_TOKEN=<token>
export OPENROUTER_API_KEY=<key>

python src/download_pdfs.py --limit 50            # OA 全合成 PDF
python src/mineru_api.py --pdf-dir data/pdfs/raw --limit 50 \
    --out data/mineru_out/run_1
python src/process_batch.py \
    --batch-result data/mineru_out/run_1/batch_*.json
python src/pubchem_lookup.py --traces-dir data/traces
python src/analyze_quality.py
python src/render_report.py
python src/extract_walkthroughs.py
```

整个 pipeline **幂等** — 重跑 `process_batch.py` 时已成功的 trace 会被跳过，所以 schema 或 prompt 调整后可以放心重跑，不会浪费已经花掉的 API token。

## 本提交对应的分支 / commit

本提交对应代码仓库 `main` 分支的 commit `<待填>`。发布数据集时 `_release.commit_hash` 字段会记录精确 commit。
