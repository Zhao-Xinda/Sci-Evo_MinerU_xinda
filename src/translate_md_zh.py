#!/usr/bin/env python3
"""
Translate an English markdown file to Chinese while preserving:
  - All code blocks (```), inline code (`...`)
  - All SMILES, InChI, chemical formulas (Cs2CO3, etc.)
  - All field / variable / identifier names (target.smiles, _provenance, ...)
  - All file paths, URLs, DOIs
  - Journal abbreviations (Org. Lett., J. Am. Chem. Soc.)
  - Named-reaction names (Suzuki coupling, Diels-Alder, oxa-Michael)
  - Markdown structure (headings, lists, tables, links)

Uses Gemini 2.5 Flash via OpenRouter (multilingual, cheap).

Usage:
    OPENROUTER_API_KEY=... python src/translate_md_zh.py \
        --in submission/walkthroughs/auto_generated_top10.md \
        --out submission/walkthroughs/auto_generated_top10.md
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from openai import OpenAI

MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")
BASE_URL = "https://openrouter.ai/api/v1"

SYSTEM_PROMPT = """你是一个精确的英中翻译器，专门处理化学 / Sci-Evo 数据集文档。

【翻译指令】
将输入 markdown 中的 **所有英文叙事文本** 翻译为简体中文。这包括但不限于：
- "Motivation:" 后面的整段动机说明
- 反应路径列表的每条说明（"To form the X skeleton from..."、"To install the all-carbon quaternary..."等）
- "Decision was:" 后面的整段决策叙述（"To explore catalyst scope, we investigated..."、"Attempted CBS reduction of 11b using..."等）
- "Outcome:" 后面的整段结果观察（"failed to produce indole"、"No product was formed"、"a maximum of 42% ee was observed"等）
- 验证段每条 metric 的 interpretation（"For total synthesis of X"、"Number of explicitly reported failed attempts during optimization"、"Highest yield achieved for model reaction 1c"等）
- significance 段引用块的整段说明

**重要：英文 prose 必须翻译成中文。不要因为是化学叙事就放弃翻译。** 这些叙事是从英文论文抽出的，但**本文档是给中文评审看的提交材料**，必须可读。

【保留不译】
- 所有 ``` code fences ``` 和 `inline code`
- SMILES、InChI 字符串（不论是否在 backtick 内）
- 化学分子式：Cs2CO3、Fe(NO3)3·9H2O、p-TsOH、BH3·Me2S 等
- 试剂 / 化合物专有名称：dihydroxyacetone、siphonodin、Lappaceolides、Indole、Maritidine、UCS1025A、Pentalenolactone D 等（**保留英文**，可选地在第一次出现时加中文括注，如 "dihydroxyacetone（二羟基丙酮）"）
- 字段名 / 标识符：`target.smiles`、`retrosynthetic_strategy`、`_provenance`、`valid=false`、`failure_mode`、`step_id`、`revises_step_id` 等
- 命名反应：Suzuki coupling、Diels-Alder、oxa-Michael、vinylogous Michael、Wittig olefination、CBS reduction、Pictet-Spengler、Johnson-Claisen rearrangement 等（保留英文，可选括注）
- 文件路径、URL、DOI（如 10.1021/...、10.1039/...）
- 期刊名缩写：Org. Lett.、J. Am. Chem. Soc.、Chem. Sci.、Nat. Commun.、JACS Au、RSC Adv 等
- 作者人名（如 Pallerla、Siitonen、Ragasa）
- Markdown 结构：标题层级、列表符号、表格、链接、引用块、加粗、斜体
- 数字与单位：°C、mol %、equiv、h、min、mg、g、kDa、mmol、equiv、Tm 等
- 图片引用：`![](...)`

【关键标签翻译表】
- "Decision was:" → "决策："
- "Outcome:" → "结果："
- "Background:" → "背景："
- "Gap:" → "缺口："
- "Target SMILES:" → "目标 SMILES："
- "Class:" → "类别："
- "Motivation:" → "动机："
- "Retrosynthesis (key disconnections):" → "逆合成（关键断键）："
- "Failed attempts (N):" → "失败尝试（N 个）："
- "Revisions (N):" → "修正（N 个）："
- "Validation:" → "验证："
- "techniques:" → "表征手段："
- "Overall Yield" → "总收率"
- "Longest Linear Steps" → "最长直链步数"
- "Total Steps" → "总步数"
- "Failed Attempts Count" → "失败尝试次数"
- "stats:" → "统计："
- "steps" → "步"
- "failed" → "失败"
- "revisions" → "修正"
- "parseable" → "可解析"
- "trace_id:"、"source:"、"DOI:"、"license:" → 保留英文标签（属字段名）
- "revises step N" → "修正 step N"
- "expecting" → "期望"
- "attempted" → "尝试"

【输出】
只输出翻译后的 markdown 全文。不要加任何前后缀说明。保持完全相同的结构（行、表格、引用块、缩进、空行）。
"""


def translate(in_path: Path, out_path: Path, model: str = MODEL) -> None:
    text = in_path.read_text()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY required")
    client = OpenAI(base_url=BASE_URL, api_key=api_key)
    print(f"input: {len(text)} chars; calling {model}...", flush=True)

    # Single-shot — Gemini 2.5 Flash 1M ctx can handle 50KB easily.
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": f"Translate the following markdown to Chinese per the rules above:\n\n{text}"},
        ],
        temperature=0.0,
    )
    out = completion.choices[0].message.content or ""

    # Strip leading/trailing code-fence wrappers if the model added them.
    if out.startswith("```markdown"):
        out = out[len("```markdown"):].lstrip("\n")
    if out.startswith("```"):
        out = out[3:].lstrip("\n")
    if out.endswith("```"):
        out = out[:-3].rstrip("\n") + "\n"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out)
    print(f"wrote: {out_path} ({len(out)} chars)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    ap.add_argument("--model", default=MODEL)
    args = ap.parse_args()
    translate(Path(args.src), Path(args.dst), args.model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
