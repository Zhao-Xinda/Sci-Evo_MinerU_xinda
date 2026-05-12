# 数据集开源链接

**类型：** Sci-Evo（科学演化数据）
**标题：** Sci-Evo 全合成轨迹数据集
**许可：** CC-BY-4.0（数据结构、Schema、标注）；论文原文 OA 许可逐条保留在每条记录中
**Schema 版本：** 1.0.0

## 公开访问

数据集将在以下平台发布：

- **主镜像 — OpenDataLab：** `https://opendatalab.com/<上传后填写>`
- **副镜像 — Hugging Face：** `https://huggingface.co/datasets/<上传后填写>`

最终提交时两个 URL 会替换为生效的链接。

## Dataset Card

数据集卡片（描述结构、来源、MinerU 使用、质量指标、应用场景）见 [`../DATASET_CARD.md`](../DATASET_CARD.md)，发布时会同时作为两个镜像的 `README.md`。

## 下载内容

发布产物含：

```
sci_evo_total_synthesis_traces/
├── data/
│   └── traces/
│       ├── PMC*.trace.json        # 一条记录一个 JSON
│       └── _quality_report.{md,json}
├── schema/
│   ├── sci_evo_total_synthesis.schema.json
│   └── SCHEMA.md
├── docs/
│   ├── technical_report.md
│   └── walkthroughs.md
├── DATASET_CARD.md
├── LICENSE
└── README.md
```

## 版本

发布版本会在源仓库（见 [`code_repo.md`](code_repo.md)）以 git tag 形式标记。每个发布包顶层都会带 `_release` 块，记录构建该包的代码 commit hash。

## 评审期临时样本访问

为了让评委在最终上传完成前就能查阅，本提交直接内嵌了 10 条代表性 trace JSON（见 [`samples/`](samples/)），选样标准记录在 [`samples/manifest.json`](samples/manifest.json)。
