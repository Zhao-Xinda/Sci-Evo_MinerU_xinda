# MinerU 使用专项说明

本文档描述 **MinerU** 工具链在 Sci-Evo 全合成轨迹数据集构建中的具体使用方式，满足赛题"数据集构建过程中必须至少使用一项 MinerU 工具链"的要求。

本提交在两个独立环节上使用了 MinerU 工具链：

---

## 1. MinerU 云端 API — 主数据抽取路径

**代码：** [`src/mineru_api.py`](src/mineru_api.py)
**端点：** `https://mineru.net/api/v4/`
**鉴权：** Bearer token（为本提交申请）
**模型版本：** `"vlm"`

### 调用流程

| 阶段 | HTTP 请求 | 作用 |
|---|---|---|
| 1. 注册 | `POST /api/v4/file-urls/batch` | 一次提交 ≤ 50 个文件的元数据；返回 `batch_id` 和每个文件对应的预签名上传 URL |
| 2. 上传 | `PUT <presigned_url>` （按文档要求**不**带 `Content-Type`） | 直接把 PDF 字节流推到 Aliyun OSS 的预签名地址。我们**绕过本地 HTTP 代理** — 测试中本地代理偶发掐断 OSS 连接 |
| 3. 轮询 | `GET /api/v4/extract-results/batch/{batch_id}` | 每 ~10 秒轮询一次，直到所有文件进入 `state="done"` 或 `"failed"` |
| 4. 拉取 | `GET <full_zip_url>` | 从 MinerU CDN 拉取每篇文件的输出 ZIP |

### MinerU 的产物（每篇论文）

输出 ZIP 包含：

- `full.md` — 整篇论文的 Markdown，**LaTeX 公式被完整保留**（如 `$\mathrm{Pd(OAc)_2}$`），保留了章节结构，图片以 `![](images/<sha>.jpg)` 内联。
- `content_list_v2.json` — 块级结构化布局：每个文本块、图片、表格、公式都标注了 `type`、`page_idx`、像素 `bbox`。
- `*_origin.pdf` — 一份源 PDF 的副本，便于追溯。
- `images/*.jpg` — PDF 中的每个图、scheme、结构、谱图都被抽出为独立文件（典型论文 10–50 张图）。
- `layout.json`、`*_model.json` — 模型与布局中间件。

这种产物正是下游 LLM 需要的形式：干净的 Markdown 文本 + 逐图文件清单。**没有 MinerU 我们必须自己 OCR PDF，且会丢失 LaTeX 公式精度** — 在化学语料里这是不可接受的，因为像 `\mathrm{Cs_2CO_3 \ (10 \ equiv)}$` 这样的反应条件直接携带语义。

### 我们如何下游使用 MinerU 输出

下游 pipeline 同时消费两类 MinerU 产物：

1. **`full.md`** 与 JSON Schema 描述、试剂名字典等一起喂给 OpenRouter 上的 Gemini 2.5 Flash，由 LLM 组装出完整的 Sci-Evo trace。
2. **`images/*.jpg`** 逐图喂给 Gemini 2.5 Flash 多模态版，抽取每张图里的 SMILES 与反应角色。所抽分子列表被回填到上面的 LLM prompt 中，让最终 trace 同时含规范化学结构与 verbatim 文本。

### Provenance 记录

每条 trace 都记录其 MinerU pipeline 调用的全部信息：

```yaml
_provenance.mineru:
  method:           "MinerU API (cloud)"
  model_version:    "vlm"
  batch_id:         "<UUID>"          # 直接重取的句柄
  result_zip_url:   "https://cdn-mineru.openxlab.org.cn/pdf/.../<UUID>.zip"
  parsed_at:        "<ISO 8601>"
```

任何人都可以通过 `result_zip_url` 重新拉取原始 MinerU 输出，使得整条数据**端到端可审计**。

### Pilot 实测性能

50 篇 pilot — 一次提交全部 50 PDF — 从上传开始到全部 done 的 wall-clock：**111 秒**。状态轨迹（实时记录）：

```
[   0s] {'pending': 27, 'done': 4, 'waiting-file': 7, 'running': 12}
[  11s] {'pending': 4, 'done': 5, 'running': 41}
[  21s] {'done': 18, 'running': 32}
[  32s] {'done': 27, 'running': 23}
[  44s] {'done': 30, 'running': 20}
[  55s] {'done': 33, 'running': 17}
[  67s] {'done': 35, 'running': 15}
[  77s] {'done': 40, 'running': 10}
[  88s] {'done': 43, 'running':  7}
[  99s] {'done': 49, 'running':  1}
[ 111s] {'done': 50}
```

### 工程稳健性增强

- **上传绕过代理。** 公司 HTTPS 代理偶发掐断到 `mineru.oss-cn-shanghai.aliyuncs.com` 的连接。`upload_one()` 用 `proxies={"http": "", "https": ""}` 直连，最多 5 次指数退避重试。
- **429 退避。** `/file-urls/batch` 端点有按分钟的速率限制。`apply_upload_urls()` 在 429 时按 `30s × 重试次数` 退避（最多 6 次）。
- **轮询 + 超时。** `poll_until_done()` 间隔 10 秒轮询，30 分钟硬超时，并实时打印状态映射（见上面 pilot 实测的状态轨迹）。

---

## 2. Sci-Base（赛事方提供，已 MinerU 预解析的语料）

**来源：** `/mnt/cxzx/share/bj_share/data/opendatalab/Sci-Base/`（Sciverse Sci-Base 样本，35,200 篇覆盖 10 大学科，已由赛事方用 MinerU 解析）。
**代码：** [`src/filter_sci_base_chem.py`](src/filter_sci_base_chem.py)。

### 我们如何使用

我们筛选 Sci-Base parquet 中的化学子集（`sci_category` 以 `Chemistry` 开头或包含 `/Chemistry`），并把标题或摘要含全合成关键词的论文挑出来，写入候选清单 [`data/manifests/sci_base_chem.jsonl`](data/manifests/sci_base_chem.jsonl)。

走 Sci-Base 而非自调 MinerU API 的 trace，会被记录为 `_provenance.mineru.method = "Sci-Base (pre-parsed)"`，使数据血统不混淆。

### 为什么两条路径都用

- (1) 证明我们能在**原始 OA 论文**上端到端跑通 MinerU pipeline — 这是赛事方最关心的能力维度；
- (2) 证明我们在**赛事方提供的语料**上也充分利用，不浪费已有的 MinerU 输出。

---

## 3. 我们没有用的部分

- **MinerU 开源版（本地）。** 我们考虑过但未在本地部署 — 开发环境无 GPU。在该约束下云端 API 是更合适的选择。
- **MinerU Skills / 在线版。** 不在本批量 pipeline 工作流的范围内。

---

## 4. 复现本 MinerU 使用方式

```bash
export MINERU_TOKEN=<在 mineru.net 申请的 token>

# A. 把目录下的至多 50 篇 PDF 一次提交
python src/mineru_api.py --pdf-dir data/pdfs/raw --limit 50 \
    --out data/mineru_out/pilot_results

# B. 提交一份自定义清单（一行一个路径）
python src/mineru_api.py --pdf-list /tmp/list.txt --limit 200 \
    --out data/mineru_out/scale_results

# C. 单文件调试
python src/mineru_api.py --pdf data/pdfs/raw/PMC12519463.pdf
```

总编排 [`src/process_batch.py`](src/process_batch.py) 消费 A 或 B 产生的 `batch_<id>.json`，下载并解压每篇产物，再串联到图像 SMILES 抽取 + Sci-Evo trace 抽取：

```bash
python src/process_batch.py \
    --batch-result data/mineru_out/pilot_results/batch_<id>.json \
    --download-workers 16 --img-workers 16 --paper-workers 4 --trace-workers 8
```

重跑安全 — 已抽出的 trace 会被跳过。
