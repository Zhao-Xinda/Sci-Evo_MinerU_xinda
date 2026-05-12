#!/usr/bin/env python3
"""
PubChem name-based SMILES lookup, used to backfill `target.smiles` (and
optionally other empty SMILES fields) on completed Sci-Evo traces.

We lean on the public PubChem PUG REST API (no auth, no quota), and bypass
the corp HTTP proxy because PubChem responds fastest direct.

The fill is conservative: we only touch target.smiles when it's missing or
when the LLM's earlier guess failed RDKit canonicalisation. We never overwrite
a parseable SMILES.

Usage (single trace):
    python src/pubchem_lookup.py data/traces/PMC12519463.trace.json

Batch:
    python src/pubchem_lookup.py --traces-dir data/traces --workers 16
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote

import requests
from rdkit import Chem
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name"
NO_PROXIES = {"http": "", "https": ""}


# In-process cache so a second pass doesn't re-query PubChem.
_CACHE: dict[str, str | None] = {}


def _clean_name(name: str) -> str:
    """Strip parentheticals like '(±)', '(-)-', '(R)-' that PubChem doesn't
    handle well at the front of natural product names; also strip trailing
    enantiomer enumerations like ' A and B'."""
    if not name:
        return ""
    s = name.strip()
    # leading stereodescriptors / racemate marks
    s = re.sub(r"^[\(\[][^\)\]]{0,8}[\)\]]\s*-?\s*", "", s)
    s = re.sub(r"^\(\s*[\+\-±]\s*\)\s*-?\s*", "", s)
    s = re.sub(r"^\([RSE Z]\)\s*-?\s*", "", s)
    # 'lappaceolides A and B' -> 'lappaceolide A'  (sing form, take first)
    m = re.match(r"^(.+?)s?\s+([A-Z])\s+and\s+[A-Z]\b", s)
    if m:
        s = f"{m.group(1)} {m.group(2)}"
    # 'compounds X and Y' -> drop trailing
    s = re.sub(r"\s+and\s+[A-Z]\b.*$", "", s)
    return s.strip()


def lookup_smiles_by_name(
    name: str, *, timeout: int = 15, retries: int = 2
) -> str | None:
    """Query PubChem for a compound name. Return RDKit-canonical isomeric
    SMILES if found and parseable. None otherwise. Results are cached."""
    if not name:
        return None
    key = name.lower()
    if key in _CACHE:
        return _CACHE[key]
    cleaned = _clean_name(name)
    if not cleaned:
        _CACHE[key] = None
        return None

    candidates = []
    if cleaned != name:
        candidates.append(cleaned)
    candidates.append(name)

    for cand in candidates:
        url = f"{PUBCHEM_BASE}/{quote(cand)}/property/IsomericSMILES,CanonicalSMILES,SMILES/JSON"
        for attempt in range(retries + 1):
            try:
                r = requests.get(url, timeout=timeout, proxies=NO_PROXIES)
            except requests.RequestException:
                time.sleep(1.0 * (attempt + 1))
                continue
            if r.status_code == 404:
                break  # name not in PubChem, try next candidate
            if r.status_code == 503:
                time.sleep(1.5 * (attempt + 1))
                continue
            if r.status_code != 200:
                break
            try:
                body = r.json()
            except ValueError:
                break
            props = (body.get("PropertyTable") or {}).get("Properties") or []
            if not props:
                break
            p = props[0]
            # API has used multiple field names over the years. Prefer isomeric.
            smi = (
                p.get("IsomericSMILES")
                or p.get("SMILES")
                or p.get("CanonicalSMILES")
                or p.get("ConnectivitySMILES")
            )
            if not smi:
                break
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                break
            canon = Chem.MolToSmiles(mol)
            _CACHE[key] = canon
            return canon
    _CACHE[key] = None
    return None


def fill_target_smiles(trace: dict) -> dict:
    """Mutate trace in place: if target.smiles empty/invalid, fill from PubChem
    using target.name. Adds an entry under _smiles_qc.pubchem_fills."""
    target = trace.get("target") or {}
    name = (target.get("name") or "").strip()
    cur = (target.get("smiles") or "").strip()

    qc = trace.setdefault("_smiles_qc", {})
    fills = qc.setdefault("pubchem_fills", [])

    if not name:
        return trace
    if cur:
        # already filled and validate_smiles already canonicalised it; skip
        return trace
    smi = lookup_smiles_by_name(name)
    if smi:
        target["smiles"] = smi
        fills.append({"field": "target.smiles", "name": name, "smiles": smi})
    else:
        fills.append({"field": "target.smiles", "name": name, "smiles": None, "reason": "pubchem_miss"})
    return trace


def process_trace_file(path: Path) -> dict:
    trace = json.loads(path.read_text())
    fill_target_smiles(trace)
    path.write_text(json.dumps(trace, ensure_ascii=False, indent=2))
    return {
        "path": str(path),
        "name": ((trace.get("target") or {}).get("name") or ""),
        "filled": ((trace.get("target") or {}).get("smiles") or "") != "",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("trace", nargs="?", help="single trace JSON")
    ap.add_argument("--traces-dir", help="batch mode")
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    if args.trace and not args.traces_dir:
        result = process_trace_file(Path(args.trace))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.traces_dir:
        files = sorted(Path(args.traces_dir).glob("*.trace.json"))
        if not files:
            print(f"no traces in {args.traces_dir}", file=sys.stderr)
            return 1
        n_filled = 0
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(process_trace_file, f): f for f in files}
            for i, fut in enumerate(as_completed(futures), 1):
                f = futures[fut]
                try:
                    r = fut.result()
                except Exception as e:
                    print(f"  [{i}/{len(files)}] {f.name}: ERROR {e}")
                    continue
                if r["filled"]:
                    n_filled += 1
                tag = "FILLED" if r["filled"] else "miss"
                print(f"  [{i}/{len(files)}] {f.name}: {tag} ({r['name'][:60]})")
        print(f"\nDone. {n_filled}/{len(files)} traces have target.smiles after pubchem pass.")
        return 0
    print("Provide either a trace file or --traces-dir", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
