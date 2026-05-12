#!/usr/bin/env python3
"""
Download Open-Access total-synthesis chemistry PDFs from Europe PMC.

Europe PMC aggregates OA full-text from PubMed Central, RSC, ACS Au series,
Nature OA, BJOC, etc. We filter for chemistry-relevant journals known to
publish total-synthesis work, require has-PDF + open-access flags, then
download via the PMC `?pdf=render` endpoint and verify magic bytes.

Output:
    data/pdfs/raw/<pmcid>.pdf
    data/manifests/pilot.jsonl     one line per successfully downloaded paper

Usage:
    python src/download_pdfs.py --limit 50
    python src/download_pdfs.py --limit 200 --query '"asymmetric total synthesis"'
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests

EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

# Journals known to publish total-synthesis work and that Europe PMC has full-text PDFs for.
# Match is case-insensitive substring on `journalTitle`.
CHEM_JOURNAL_KEYWORDS = [
    "Beilstein J. Org. Chem",
    "Beilstein Journal of Organic Chemistry",
    "Chemical Science",
    "Chem Sci",
    "Nat Chem",
    "Nature Chemistry",
    "Nat Commun",
    "Nature Communications",
    "Commun Chem",
    "Communications Chemistry",
    "JACS Au",
    "ACS Cent Sci",
    "Org Lett",
    "Organic Letters",
    "J Org Chem",
    "Journal of Organic Chemistry",
    "Angew Chem",
    "Angewandte Chemie",
    "JACS",
    "J Am Chem Soc",
    "Org Chem Front",
    "Organic Chemistry Frontiers",
    "RSC Adv",
    "Synthesis",
    "Synlett",
]


def search_epmc(query: str, page_size: int = 25, max_pages: int = 40):
    cursor = "*"
    for _ in range(max_pages):
        params = {
            "query": query,
            "format": "json",
            "resultType": "core",
            "pageSize": page_size,
            "cursorMark": cursor,
        }
        r = requests.get(EPMC_SEARCH, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        for hit in data.get("resultList", {}).get("result", []):
            yield hit
        nxt = data.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(0.5)


def get_journal_title(hit) -> str:
    """resultType=core nests journal info; resultType=lite has it flat."""
    if hit.get("journalTitle"):
        return hit["journalTitle"]
    j = (hit.get("journalInfo") or {}).get("journal") or {}
    return j.get("medlineAbbreviation") or j.get("isoabbreviation") or j.get("title") or ""


def is_chem_journal(hit) -> bool:
    j = get_journal_title(hit).lower()
    if not j:
        return False
    return any(k.lower() in j for k in CHEM_JOURNAL_KEYWORDS)


# Substrings (case-insensitive, in title) that mark the paper as a review,
# perspective, news, or editorial — i.e. *not* a primary research synthesis.
# Picked up after pilot run brought in 1 review article.
EXCLUDE_TITLE_PATTERNS = [
    r"\bsynthesis(?:es)?\s+toward\s+",   # "Synthesis Toward..." is sometimes used in proposals
    r"\breview\b",
    r"\bperspective\b",
    r"^perspectives?[: ]",
    r"\beditorial\b",
    r"^correction[: ]",
    r"\berratum\b",
    r"\bretraction\b",
    r"\bin memoriam\b",
    r"\bnews\s+and\s+views\b",
    r"\bhighlights?\b",
    r"\brecent advances\b",
    r"\brecent\s+progress\b",
]
import re as _re_excl
_EXCLUDE_RE = _re_excl.compile("|".join(EXCLUDE_TITLE_PATTERNS), _re_excl.IGNORECASE)


def is_excluded_pubtype(hit) -> bool:
    """Return True if title or pubType marks this as a review / non-research paper."""
    title = (hit.get("title") or "").strip()
    if title and _EXCLUDE_RE.search(title):
        return True
    # pubTypeList carries Medline-style categorisations.
    pubtypes = (hit.get("pubTypeList") or {}).get("pubType") or []
    pubtypes_str = " ".join(pt.lower() for pt in pubtypes if isinstance(pt, str))
    if any(
        kw in pubtypes_str
        for kw in [
            "review",
            "editorial",
            "letter to the editor",
            "comment",
            "correction",
            "erratum",
            "retraction",
        ]
    ):
        return True
    return False


def get_pdf_url(hit) -> str | None:
    pmcid = hit.get("pmcid")
    if pmcid:
        return f"https://europepmc.org/articles/{pmcid}?pdf=render"
    for u in (hit.get("fullTextUrlList") or {}).get("fullTextUrl", []):
        if u.get("documentStyle") == "pdf" and u.get("availability", "").lower().startswith("open"):
            return u.get("url")
    return None


def download_pdf(url: str, out_path: Path) -> tuple[bool, str]:
    try:
        with requests.get(url, stream=True, timeout=180, allow_redirects=True) as r:
            r.raise_for_status()
            with out_path.open("wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        with out_path.open("rb") as f:
            head = f.read(4)
        if head != b"%PDF":
            out_path.unlink(missing_ok=True)
            return False, "not-a-pdf"
        return True, "ok"
    except requests.RequestException as e:
        out_path.unlink(missing_ok=True)
        return False, f"http-error: {e}"


def load_seen(manifest: Path) -> set[str]:
    if not manifest.exists():
        return set()
    out = set()
    with manifest.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.add(json.loads(line)["doi"])
            except (json.JSONDecodeError, KeyError):
                continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--query",
        default='"total synthesis" AND OPEN_ACCESS:Y AND HAS_PDF:Y',
        help="Europe PMC query string",
    )
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--out", default="data/pdfs/raw")
    ap.add_argument("--manifest", default="data/manifests/pilot.jsonl")
    ap.add_argument("--year-min", type=int, default=2018, help="Skip papers older than this year")
    ap.add_argument("--sleep", type=float, default=0.7, help="Seconds between PDF downloads")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = Path(args.manifest)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    seen = load_seen(manifest)

    n_seen = n_skipped = n_failed = n_ok = 0
    with manifest.open("a") as mf:
        for hit in search_epmc(args.query):
            n_seen += 1
            if n_ok >= args.limit:
                break
            doi = hit.get("doi") or hit.get("pmcid") or hit.get("id")
            if not doi or doi in seen:
                n_skipped += 1
                continue
            try:
                year = int(hit.get("pubYear") or 0)
            except ValueError:
                year = 0
            if year and year < args.year_min:
                n_skipped += 1
                continue
            if not is_chem_journal(hit):
                n_skipped += 1
                continue
            if is_excluded_pubtype(hit):
                n_skipped += 1
                continue
            pdf_url = get_pdf_url(hit)
            if not pdf_url:
                n_skipped += 1
                continue
            stem = (hit.get("pmcid") or hit.get("id") or doi).replace("/", "_").replace(":", "_")
            out_path = out_dir / f"{stem}.pdf"
            journal = get_journal_title(hit) or "?"
            print(
                f"[{n_ok+1}/{args.limit}] {journal} ({year}) "
                f"{(hit.get('title') or '')[:90]}",
                flush=True,
            )
            ok, status = download_pdf(pdf_url, out_path)
            if not ok:
                n_failed += 1
                print(f"    FAIL: {status}", file=sys.stderr)
                continue
            rec = {
                "doi": doi,
                "pmcid": hit.get("pmcid"),
                "pmid": hit.get("pmid"),
                "title": hit.get("title"),
                "journal": journal,
                "year": year,
                "authors": hit.get("authorString"),
                "abstract": hit.get("abstractText"),
                "license": hit.get("license"),
                "is_open_access": hit.get("isOpenAccess"),
                "pdf_url": pdf_url,
                "local_path": str(out_path),
                "size_bytes": out_path.stat().st_size,
            }
            mf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            mf.flush()
            seen.add(doi)
            n_ok += 1
            time.sleep(args.sleep)

    print(
        f"\nSummary: scanned={n_seen} downloaded={n_ok} skipped={n_skipped} failed={n_failed}",
        flush=True,
    )
    return 0 if n_ok > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
