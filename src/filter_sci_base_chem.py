#!/usr/bin/env python3
"""
Filter the organiser-provided Sci-Base sample (35k MinerU-pre-parsed papers
across 10 disciplines) down to chemistry-relevant total-synthesis-adjacent
content. Output a JSONL manifest of qualifying papers we *could* enrich the
trace dataset with on a second pass — without re-running MinerU since
Sci-Base's parquet payload IS the MinerU output already.

Heuristic:
    sci_category startswith 'Chemistry' OR contains 'Chemistry/Materials'
    AND
    title or abstract contains one of: 'total synthesis', 'asymmetric synthesis',
    'enantioselective synthesis', 'natural product synthesis', 'retrosynthesis'

Output: data/manifests/sci_base_chem.jsonl with one record per matched paper.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

import pyarrow.parquet as pq

DEFAULT_PARQUET_DIR = "/mnt/cxzx/share/bj_share/data/opendatalab/Sci-Base/paper/parquet"

KEYWORDS = re.compile(
    r"\b("
    r"total synthesis|asymmetric (total )?synthesis|enantioselective synthesis|"
    r"diastereoselective synthesis|formal synthesis|natural product synthesis|"
    r"retrosynthe|biomimetic synthesis|stereoselective total synthesis|"
    r"catalytic asymmetric"
    r")\b",
    re.IGNORECASE,
)


def is_chem_category(cat: str) -> bool:
    if not cat:
        return False
    c = cat.lower()
    return c.startswith("chemistry") or "/chemistry" in c or "chemistry/" in c


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet-dir", default=DEFAULT_PARQUET_DIR)
    ap.add_argument("--out", default="data/manifests/sci_base_chem.jsonl")
    ap.add_argument("--limit", type=int, default=0, help="0 = no limit")
    args = ap.parse_args()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    files = sorted(glob.glob(f"{args.parquet_dir}/*.parquet"))
    if not files:
        print(f"no parquet in {args.parquet_dir}", file=sys.stderr)
        return 1

    n_total = 0
    n_chem = 0
    n_ts = 0
    written = 0
    with open(args.out, "w") as fout:
        for fp in files:
            t = pq.read_table(
                fp,
                columns=["title", "abstract", "doi", "is_oa", "language", "sci_category", "sha256"],
            )
            for i in range(t.num_rows):
                n_total += 1
                cat = t["sci_category"][i].as_py() or ""
                title = t["title"][i].as_py() or ""
                abstract = t["abstract"][i].as_py() or ""
                lang = t["language"][i].as_py() or ""
                if lang and lang.lower() not in ("en", "english", ""):
                    continue
                if is_chem_category(cat):
                    n_chem += 1
                    if KEYWORDS.search(title) or KEYWORDS.search(abstract):
                        n_ts += 1
                        rec = {
                            "doi": t["doi"][i].as_py(),
                            "sha256": t["sha256"][i].as_py(),
                            "title": title,
                            "is_oa": t["is_oa"][i].as_py(),
                            "sci_category": cat,
                            "abstract": (abstract or "")[:600],
                        }
                        fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        written += 1
                        if args.limit and written >= args.limit:
                            print(
                                f"reached limit {args.limit}; total scanned={n_total}",
                                file=sys.stderr,
                            )
                            return 0
    print(
        f"scanned={n_total} chem={n_chem} total-synthesis-keyword={n_ts} written={written}\n"
        f"-> {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
