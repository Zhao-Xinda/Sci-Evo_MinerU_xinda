# MinerU Usage Statement

This document describes exactly how the **MinerU** toolchain is exercised in the construction of the Sci-Evo Total-Synthesis Trace Dataset, satisfying the competition's requirement that *"the dataset must use at least one MinerU toolchain component"*.

We use **two distinct MinerU components** in this submission:

---

## 1. MinerU Cloud API — primary data-extraction path

**Code:** [`src/mineru_api.py`](src/mineru_api.py).
**Endpoint:** `https://mineru.net/api/v4/`
**Auth:** Bearer token (registered for this submission).
**Model version:** `"vlm"`

### What we call

| Stage | HTTP request | What it does |
|---|---|---|
| 1. Register | `POST /api/v4/file-urls/batch` | Submit metadata for up to 50 files at once; receive `batch_id` and one presigned upload URL per file |
| 2. Upload | `PUT <presigned_url>` (no `Content-Type` per docs) | Stream PDF bytes directly to the Aliyun OSS upload URL. We bypass the local HTTP proxy because the proxy was occasionally killing OSS connections in our test environment. |
| 3. Poll | `GET /api/v4/extract-results/batch/{batch_id}` | Poll once per ~10 s until all files are in `state="done"` or `"failed"` |
| 4. Fetch | `GET <full_zip_url>` | Pull the per-file output ZIP from the MinerU CDN |

### What MinerU produces (per paper)

The output ZIP contains:

- `full.md` — the entire paper as Markdown, with **LaTeX-preserved formulas** (e.g. `$\mathrm{Pd(OAc)_2}$`), section structure, and image links inlined as `![](images/<sha>.jpg)`.
- `content_list_v2.json` — block-level structured layout: each text block, image, table, and equation tagged with `type`, `page_idx`, and pixel `bbox`.
- `*_origin.pdf` — a copy of the source PDF, preserved for traceability.
- `images/*.jpg` — every figure / scheme / structure / spectrum extracted from the PDF as a discrete file (typical paper: 10–50 images).
- `layout.json`, `*_model.json` — model and layout intermediates.

This output is exactly what an LLM downstream needs: clean Markdown text + a per-figure file list. **Without MinerU, we would have to OCR the PDF ourselves and lose the LaTeX-formulae fidelity** — a deal-breaker for a chemistry corpus where reaction conditions like `\mathrm{Cs_2CO_3 \ (10 \ equiv)}$` carry meaning.

### How we use the MinerU output downstream

The downstream pipeline consumes both kinds of MinerU output:

1. **`full.md`** is fed (along with the JSON Schema description and a curated reagent dictionary) to Gemini 2.5 Flash via OpenRouter, which composes the full Sci-Evo trace.
2. **`images/*.jpg`** are sent one-by-one to Gemini 2.5 Flash multimodal to extract per-figure SMILES and reaction roles. The resulting molecule list is appended to the prompt above so the trace has structured chemistry alongside the verbatim text.

### Provenance recording

Every trace records its MinerU pipeline run:

```yaml
_provenance.mineru:
  method:           "MinerU API (cloud)"
  model_version:    "vlm"
  batch_id:         "<UUID>"          # direct re-fetch handle
  result_zip_url:   "https://cdn-mineru.openxlab.org.cn/pdf/.../<UUID>.zip"
  parsed_at:        "<ISO 8601>"
```

Anyone can re-fetch the original MinerU output by hitting the recorded `result_zip_url`, ensuring the dataset is **end-to-end auditable**.

### Pilot performance

50-paper pilot — submission of all 50 PDFs in one batch — wall-clock from upload-start to all-done: **111 seconds**. State trajectory captured live:

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

### Robustness fixes implemented

- **Proxy bypass on upload.** The corporate HTTPS proxy occasionally drops connections to `mineru.oss-cn-shanghai.aliyuncs.com`. `upload_one()` PUTs with `proxies={"http": "", "https": ""}` and retries up to 5× with exponential back-off.
- **429 backoff on apply_url.** The `/file-urls/batch` endpoint enforces a per-minute rate limit. `apply_upload_urls()` retries on 429 with `30s × attempt` back-off (up to 6 retries).
- **State polling with timeout.** `poll_until_done()` sleeps 10 s between polls, fails-fast after 30 minutes, and prints the live state map (visible in the pilot timing block above).

---

## 2. Sci-Base (organiser-provided, MinerU-pre-parsed corpus)

**Source:** `/mnt/cxzx/share/bj_share/data/opendatalab/Sci-Base/` (Sciverse Sci-Base sample, 35 200 papers across 10 disciplines, MinerU-parsed by the organiser).
**Code:** [`src/filter_sci_base_chem.py`](src/filter_sci_base_chem.py).

### How we use it

We filter the Sci-Base parquet for the chemistry subset (`sci_category` starts with `Chemistry` or contains `/Chemistry`) and surface candidates whose title or abstract matches our total-synthesis keyword set. The filtered manifest is at [`data/manifests/sci_base_chem.jsonl`](data/manifests/sci_base_chem.jsonl).

For traces sourced via Sci-Base rather than our own MinerU API call, `_provenance.mineru.method = "Sci-Base (pre-parsed)"` is recorded, so the data lineage is unambiguous.

### Why both touch-points

- (1) demonstrates we can run the MinerU pipeline **end-to-end on raw OA papers** — the failure mode the organisers care about most;
- (2) demonstrates we leverage the **organiser-provided** corpus where it's the most efficient choice and avoids redundant MinerU API calls.

---

## 3. What we did *not* use

- **MinerU OSS (local).** We considered but did not deploy the MinerU open-source project locally because no GPU was available in our development environment. The cloud API was the right choice given the constraint.
- **MinerU Skills / online use.** Out of scope for this batch-pipeline workflow.

---

## 4. Reproducing this MinerU usage

```bash
export MINERU_TOKEN=<your token from mineru.net>

# A. submit one batch of up to 50 PDFs from a directory
python src/mineru_api.py --pdf-dir data/pdfs/raw --limit 50 \
    --out data/mineru_out/pilot_results

# B. submit a custom selection (one path per line)
python src/mineru_api.py --pdf-list /tmp/list.txt --limit 200 \
    --out data/mineru_out/scale_results

# C. run a single PDF for debugging
python src/mineru_api.py --pdf data/pdfs/raw/PMC12519463.pdf
```

The orchestrator [`src/process_batch.py`](src/process_batch.py) consumes a `batch_<id>.json` produced by step A or B, downloads and unzips every per-paper output, and wires them through to image-SMILES extraction + Sci-Evo trace extraction:

```bash
python src/process_batch.py \
    --batch-result data/mineru_out/pilot_results/batch_<id>.json \
    --download-workers 16 --img-workers 32 --trace-workers 8
```

Re-running is safe — already-extracted traces are skipped.
