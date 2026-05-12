#!/usr/bin/env python3
"""
Extract chemical structures + reaction roles from MinerU-emitted images
using a multimodal LLM (Gemini 2.5 Flash via OpenRouter by default).

For each image we ask the model to classify it (single molecule / reaction
scheme / unrelated figure / spectrum) and return structured chemistry:
  - SMILES of every drawn structure with role & name/label
  - reaction conditions (reagents, solvent, temp, time, yield)
  - named reaction if applicable

Usage:
    python src/extract_chem_from_image.py \
        --img-dir data/mineru_out/<paper>/images \
        --out data/extracted/<paper>.smiles.jsonl

    python src/extract_chem_from_image.py \
        --img-glob 'data/mineru_out/**/images/*.jpg' \
        --workers 32

Environment:
    OPENROUTER_API_KEY   required
    OPENROUTER_MODEL     default 'google/gemini-2.5-flash'
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from openai import OpenAI

DEFAULT_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

PROMPT = """\
You are a chemistry information-extraction tool. The image below is taken from a chemistry
paper (likely a total-synthesis paper). Inspect it carefully and return JSON ONLY (no prose,
no markdown fences) matching this schema exactly:

{
  "is_chemical": <bool: true if image contains chemical structures or reactions>,
  "image_type": "single_molecule" | "reaction_scheme" | "retrosynthesis" |
                "spectrum" | "table_or_text" | "other",
  "molecules": [
    {
      "label": <str|null: the bold compound number/letter shown next to the structure, e.g. "1", "5a", "7-Boc">,
      "smiles": <str: canonical SMILES; include stereo if drawn (@/@@,/,\\); empty string if unparseable>,
      "role": "starting_material" | "reactant" | "intermediate" | "product" |
              "catalyst" | "ligand" | "reagent" | "byproduct" | "target" | "unspecified",
      "stereochem_note": <str|null: free-text describing wedge/dash/cis/trans/ee if drawn>
    }
  ],
  "reactions": [
    {
      "from_labels": [<str>],   // labels of substrates as they appear in image
      "to_labels":   [<str>],   // labels of products
      "named_reaction": <str|null: e.g. "Suzuki coupling", "Diels-Alder">,
      "conditions": <str|null: reagents, solvent, temperature, time as written above the arrow>,
      "yield_percent": <number|null>,
      "ee_percent": <number|null>,
      "dr": <str|null: e.g. "10:1">,
      "notes": <str|null: any caveat or footnote text near the arrow>
    }
  ],
  "scheme_caption_text": <str|null: any caption/title text in the image>,
  "confidence": <number 0..1: your confidence in the extraction>
}

Rules:
- If the image is not chemical (page header, journal logo, spectrum, photograph), set
  is_chemical=false, image_type accordingly, and leave molecules/reactions empty arrays.
- SMILES must be valid; if a structure is too small/blurred to read, output empty string for smiles.
- Use ASCII only. No commentary outside the JSON.
"""


def encode_image_data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        mime = "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def make_client(api_key: str | None = None, base_url: str = DEFAULT_BASE_URL) -> OpenAI:
    api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY env var or --api-key required")
    return OpenAI(base_url=base_url, api_key=api_key)


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S)


def _coerce_json(text: str) -> dict:
    """Strip markdown fences if any and parse."""
    text = text.strip()
    m = _JSON_FENCE_RE.search(text)
    if m:
        text = m.group(1).strip()
    # try to locate first { and last }
    if not text.startswith("{"):
        l = text.find("{")
        r = text.rfind("}")
        if l != -1 and r != -1 and r > l:
            text = text[l : r + 1]
    return json.loads(text)


def extract_one(
    client: OpenAI,
    image_path: Path,
    *,
    model: str = DEFAULT_MODEL,
    max_retries: int = 3,
) -> dict:
    data_uri = encode_image_data_uri(image_path)
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": PROMPT},
                            {"type": "image_url", "image_url": {"url": data_uri}},
                        ],
                    }
                ],
                temperature=0.0,
            )
            content = completion.choices[0].message.content or ""
            data = _coerce_json(content)
            data["_image_path"] = str(image_path)
            data["_model"] = model
            return data
        except json.JSONDecodeError as e:
            last_err = e
            time.sleep(0.5 * (attempt + 1))
        except Exception as e:
            last_err = e
            time.sleep(1.0 * (attempt + 1))
    return {
        "_image_path": str(image_path),
        "_model": model,
        "_error": f"{type(last_err).__name__}: {last_err}",
        "is_chemical": False,
        "molecules": [],
        "reactions": [],
    }


def extract_batch(
    image_paths: list[Path],
    *,
    model: str = DEFAULT_MODEL,
    workers: int = 32,
    out_jsonl: Path | None = None,
) -> list[dict]:
    client = make_client()
    results: list[dict] = []
    out_fh = open(out_jsonl, "w") if out_jsonl else None
    try:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {ex.submit(extract_one, client, p, model=model): p for p in image_paths}
            for i, fut in enumerate(as_completed(futures), 1):
                p = futures[fut]
                try:
                    r = fut.result()
                except Exception as e:
                    r = {
                        "_image_path": str(p),
                        "_error": f"{type(e).__name__}: {e}",
                        "is_chemical": False,
                        "molecules": [],
                        "reactions": [],
                    }
                results.append(r)
                if out_fh:
                    out_fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                    out_fh.flush()
                if i % 25 == 0 or i == len(image_paths):
                    n_chem = sum(
                        1 for x in results if x.get("is_chemical") and not x.get("_error")
                    )
                    print(f"  [{i}/{len(image_paths)}] chemical={n_chem}", flush=True)
    finally:
        if out_fh:
            out_fh.close()
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--img-dir", help="Directory containing images")
    ap.add_argument("--img-glob", help="Glob pattern (e.g. 'data/**/images/*.jpg')")
    ap.add_argument("--out", default="data/extracted/smiles.jsonl")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--limit", type=int, default=0, help="0 = no limit")
    args = ap.parse_args()

    if not args.img_dir and not args.img_glob:
        print("ERROR: --img-dir or --img-glob required", file=sys.stderr)
        return 2

    if args.img_dir:
        d = Path(args.img_dir)
        paths = sorted([p for p in d.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}])
    else:
        from glob import glob
        paths = [Path(p) for p in sorted(glob(args.img_glob, recursive=True))]
    if args.limit:
        paths = paths[: args.limit]
    if not paths:
        print("no images found", file=sys.stderr)
        return 1
    print(f"extracting from {len(paths)} images, model={args.model}, workers={args.workers}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    extract_batch(paths, model=args.model, workers=args.workers, out_jsonl=out_path)

    # Summary
    n_total = n_chem = n_mol = n_rxn = 0
    with out_path.open() as f:
        for line in f:
            r = json.loads(line)
            n_total += 1
            if r.get("is_chemical") and not r.get("_error"):
                n_chem += 1
                n_mol += len(r.get("molecules") or [])
                n_rxn += len(r.get("reactions") or [])
    print(
        f"\nDone. images={n_total} chemical={n_chem} molecules={n_mol} reactions={n_rxn}\n"
        f"Output: {out_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
