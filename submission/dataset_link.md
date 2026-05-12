# 数据集开源链接

**类型：** Sci-Evo（科学演化数据）
**标题：** Sci-Evo 全合成轨迹数据集
**许可：** CC-BY-4.0（数据结构、Schema、标注）；论文原文 OA 许可逐条保留在每条记录中
**Schema 版本：** 1.0.0

## 公开访问

**当前已开放（GitHub）：** **https://github.com/Zhao-Xinda/Sci-Evo_MinerU_xinda**
— 完整 pipeline 源码、Schema、237 条 trace 数据均已开源，可通过 `git clone` 直接获取。
trace JSON 位于 [`data/traces/`](data/traces/)，Schema 位于 [`schema/`](schema/)。

**计划镜像：**
- OpenDataLab：`https://opendatalab.com/<待上传>`
- Hugging Face：`https://huggingface.co/datasets/<待上传>`

最终提交时两个镜像 URL 会补全。提交评审期间，GitHub 仓库本身即承担"互联网可访问数据内容的开源数据集链接"的角色。

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
