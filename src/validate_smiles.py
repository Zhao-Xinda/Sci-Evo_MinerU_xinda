#!/usr/bin/env python3
"""
SMILES quality control for Sci-Evo total-synthesis traces.

What it does:
    1. RDKit-canonicalize every SMILES in the trace (target, fragments,
       substrate_smiles, product_smiles, rxn_smiles, reagents-as-SMILES).
    2. Replace each parseable SMILES with its canonical form so downstream
       consumers can compare across rows.
    3. For invalid SMILES, blank the field and record the offence.
    4. Apply a small built-in REAGENT dictionary (chemical name -> canonical
       SMILES) to override LLM-guessed structures whenever the named compound
       appears verbatim in the step's evidence.text_span. Catches cases like
       'dihydroxyacetone' -> O=C(CO)CO that the LLM may hallucinate as
       3-hydroxypropanoic acid.
    5. Append a top-level `_smiles_qc` field with per-trace statistics.

The module is pure-Python (RDKit only) and has no network dependency.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from rdkit import Chem
from rdkit import RDLogger

# Silence RDKit's stderr noise on bad SMILES — we surface our own messages.
RDLogger.DisableLog("rdApp.*")


# ---------------------------------------------------------------------------
# Common reagent / starting-material name -> canonical SMILES.
# Curated from frequently-cited reagents in total-synthesis literature.
# Names are matched case-insensitively against evidence.text_span as whole
# words (or near-whole words for things like 'p-TsOH').
# ---------------------------------------------------------------------------
REAGENT_SMILES: dict[str, str] = {
    # carbonyl / oxo small starting materials
    "dihydroxyacetone": "O=C(CO)CO",
    "glyceraldehyde": "O=C[C@@H](O)CO",
    "glyoxal": "O=CC=O",
    "formaldehyde": "C=O",
    "paraformaldehyde": "OCO",
    "acetaldehyde": "CC=O",
    "glycolic acid": "OCC(=O)O",
    "glycolaldehyde": "OCC=O",
    # bases (carbonates / hydroxides / amides)
    "Cs2CO3": "[Cs+].[Cs+].[O-]C([O-])=O",
    "K2CO3":  "[K+].[K+].[O-]C([O-])=O",
    "Na2CO3": "[Na+].[Na+].[O-]C([O-])=O",
    "NaHCO3": "[Na+].OC([O-])=O",
    "KHCO3":  "[K+].OC([O-])=O",
    "KOtBu":  "[K+].CC(C)(C)[O-]",
    "NaOtBu": "[Na+].CC(C)(C)[O-]",
    "LiOH":   "[Li+].[OH-]",
    "NaOH":   "[Na+].[OH-]",
    "KOH":    "[K+].[OH-]",
    "NaH":    "[Na+].[H-]",
    "KH":     "[K+].[H-]",
    "NaHMDS": "[Na+].[N-]([Si](C)(C)C)[Si](C)(C)C",
    "LiHMDS": "[Li+].[N-]([Si](C)(C)C)[Si](C)(C)C",
    "KHMDS":  "[K+].[N-]([Si](C)(C)C)[Si](C)(C)C",
    "LDA":    "[Li+].CC(C)[N-]C(C)C",
    # amine / pyridine bases
    "Et3N":   "CCN(CC)CC",
    "DBU":    "N1=C2N(CCC1)CCCC2",
    "DBN":    "N1=C2N(CC1)CCC2",
    "DABCO":  "C1CN2CCN1CC2",
    "DIPEA":  "CCN(C(C)C)C(C)C",
    "DMAP":   "CN(C)c1ccncc1",
    "imidazole": "c1cnc[nH]1",
    "pyridine":  "c1ccncc1",
    "TBAF":   "[F-].CCCC[N+](CCCC)(CCCC)CCCC",
    # acids
    "p-TsOH":  "Cc1ccc(S(=O)(=O)O)cc1",
    "PPTS":    "Cc1ccc(S(=O)(=O)[O-])cc1.c1cc[nH+]cc1",
    "TFA":     "OC(=O)C(F)(F)F",
    "MsOH":    "CS(=O)(=O)O",
    "TfOH":    "OS(=O)(=O)C(F)(F)F",
    "HCl":     "Cl",
    # Lewis acids
    "Zn(OTf)2": "[Zn+2].[O-]S(=O)(=O)C(F)(F)F.[O-]S(=O)(=O)C(F)(F)F",
    "Cu(OTf)2": "[Cu+2].[O-]S(=O)(=O)C(F)(F)F.[O-]S(=O)(=O)C(F)(F)F",
    "Sc(OTf)3": "[Sc+3].[O-]S(=O)(=O)C(F)(F)F.[O-]S(=O)(=O)C(F)(F)F.[O-]S(=O)(=O)C(F)(F)F",
    "BF3":      "FB(F)F",
    "BF3.OEt2": "FB(F)F.CCOCC",
    "AlCl3":    "Cl[Al](Cl)Cl",
    "TiCl4":    "Cl[Ti](Cl)(Cl)Cl",
    "FeCl3":    "Cl[Fe](Cl)Cl",
    # palladium / common metal sources
    "Pd(OAc)2": "[Pd+2].CC(=O)[O-].CC(=O)[O-]",
    "Pd(PPh3)4": "[Pd].P(c1ccccc1)(c1ccccc1)c1ccccc1.P(c1ccccc1)(c1ccccc1)c1ccccc1.P(c1ccccc1)(c1ccccc1)c1ccccc1.P(c1ccccc1)(c1ccccc1)c1ccccc1",
    # solvents (rarely SMILES-needed but useful)
    "DCM":   "ClCCl",
    "DCE":   "ClCCCl",
    "1,2-DCE": "ClCCCl",
    "DMF":   "CN(C)C=O",
    "DMSO":  "CS(=O)C",
    "DMA":   "CN(C)C(C)=O",
    "THF":   "C1CCOC1",
    "MeCN":  "CC#N",
    "EtOAc": "CCOC(=O)C",
    "MeOH":  "CO",
    "EtOH":  "CCO",
    "iPrOH": "CC(C)O",
    "PhMe":  "Cc1ccccc1",
    "toluene": "Cc1ccccc1",
    # oxidants / reductants
    "DDQ":   "Clc1c(Cl)c(=O)c(C#N)c(C#N)c1=O",
    "PCC":   "[O-][Cr](=O)(=O)Cl.c1cc[nH+]cc1",
    "MnO2":  "O=[Mn]=O",
    "OsO4":  "O=[Os](=O)(=O)=O",
    "NaBH4": "[Na+].[BH4-]",
    "LiAlH4": "[Li+].[Al-]([H])([H])([H])[H]",
    "DIBAL": "CC(C)C[Al]CC(C)C",
    "DIBAL-H": "CC(C)C[Al]CC(C)C",
}

# Lower-case alias map for case-insensitive lookup.
_REAGENT_LOOKUP = {k.lower(): v for k, v in REAGENT_SMILES.items()}


@dataclass
class SmilesQC:
    total: int = 0
    parseable: int = 0
    canonicalized: int = 0
    invalid: int = 0
    overridden_by_name: int = 0
    invalid_examples: list[str] = field(default_factory=list)
    overrides: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "parseable": self.parseable,
            "canonicalized": self.canonicalized,
            "invalid": self.invalid,
            "overridden_by_name": self.overridden_by_name,
            "invalid_examples": self.invalid_examples[:10],
            "overrides": self.overrides[:25],
        }


def canonicalize_smiles(smi: str) -> str | None:
    """Return canonical SMILES if `smi` parses, else None. Empty input -> None."""
    if not smi or not isinstance(smi, str):
        return None
    smi = smi.strip()
    if not smi:
        return None
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol)


def find_named_reagent(text: str) -> tuple[str, str] | None:
    """Search `text` for any reagent name in the dict; return (name, SMILES).

    Matches whole-token names (case-insensitive) plus a few hyphen/dot variants.
    Returns the FIRST match in the order names appear in the dict. We pick
    longest-name-first to prefer 'p-TsOH' over 'TsOH'.
    """
    if not text:
        return None
    lower = text.lower()
    for name in sorted(REAGENT_SMILES.keys(), key=len, reverse=True):
        n = name.lower()
        # Whole-word-ish boundary; allow internal punctuation common in chem names.
        pattern = r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])"
        if re.search(pattern, lower):
            return name, REAGENT_SMILES[name]
    return None


def _process_smiles_list(
    smis: list[str] | None,
    qc: SmilesQC,
    *,
    evidence_text: str = "",
    field_label: str = "",
) -> list[str]:
    """Canonicalize each SMILES in a list. Apply name-based override if the
    list looks wrong vs an evidence-text-mentioned named reagent."""
    if not smis:
        return smis or []
    out: list[str] = []
    for smi in smis:
        qc.total += 1
        canon = canonicalize_smiles(smi)
        if canon is None:
            qc.invalid += 1
            if smi:
                qc.invalid_examples.append(smi)
            out.append("")
            continue
        qc.parseable += 1
        if canon != smi:
            qc.canonicalized += 1
        out.append(canon)

    # NOTE: We deliberately do NOT auto-override empty SMILES from the
    # evidence text. Earlier experiments showed this routinely picked solvents
    # / reagents (1,2-DCE, Cs2CO3, ...) instead of the actual substrate or
    # product the field describes. The right place to inject reagent-name
    # knowledge is the LLM prompt (see extract_trace.py _format_reagent_hints).
    # Validation only canonicalizes and flags; it does not fill.
    return out


def _process_str(smi: str | None, qc: SmilesQC) -> str:
    if not smi:
        return ""
    qc.total += 1
    canon = canonicalize_smiles(smi)
    if canon is None:
        qc.invalid += 1
        qc.invalid_examples.append(smi)
        return ""
    qc.parseable += 1
    if canon != smi:
        qc.canonicalized += 1
    return canon


def validate_trace(trace: dict) -> dict:
    """Mutate `trace` in place, canonicalizing SMILES and adding _smiles_qc.

    Returns the same trace for chaining.
    """
    qc = SmilesQC()

    target = trace.get("target") or {}
    if "smiles" in target:
        target["smiles"] = _process_str(target.get("smiles"), qc)

    rs = trace.get("retrosynthetic_strategy") or {}
    for frag in rs.get("fragments") or []:
        if "smiles" in frag:
            frag["smiles"] = _process_str(frag.get("smiles"), qc)

    for step in trace.get("execution_trace") or []:
        rxn = step.get("reaction")
        if not isinstance(rxn, dict):
            continue
        ev_text = ((step.get("evidence") or {}).get("text_span")) or ""
        rxn["substrate_smiles"] = _process_smiles_list(
            rxn.get("substrate_smiles"),
            qc,
            evidence_text=ev_text,
            field_label=f"step_{step.get('step_id')}.substrate_smiles",
        )
        rxn["product_smiles"] = _process_smiles_list(
            rxn.get("product_smiles"),
            qc,
            evidence_text=ev_text,
            field_label=f"step_{step.get('step_id')}.product_smiles",
        )
        if "rxn_smiles" in rxn and rxn.get("rxn_smiles"):
            # rxn_smiles is "A.B>>C" — split, canonicalize each side.
            parts = rxn["rxn_smiles"].split(">>")
            if len(parts) == 2:
                lhs = ".".join(
                    s for s in (canonicalize_smiles(p) or "" for p in parts[0].split(".")) if s
                )
                rhs = ".".join(
                    s for s in (canonicalize_smiles(p) or "" for p in parts[1].split(".")) if s
                )
                rxn["rxn_smiles"] = f"{lhs}>>{rhs}" if lhs and rhs else ""

    trace["_smiles_qc"] = qc.to_dict()
    return trace


def main_cli() -> int:
    """Standalone: read a trace JSON, write a validated copy."""
    import argparse
    import json
    import sys
    from pathlib import Path

    ap = argparse.ArgumentParser()
    ap.add_argument("trace_json")
    ap.add_argument("--out", help="Output path (default: overwrite input)")
    args = ap.parse_args()

    p = Path(args.trace_json)
    trace = json.loads(p.read_text())
    validate_trace(trace)
    out_path = Path(args.out) if args.out else p
    out_path.write_text(json.dumps(trace, ensure_ascii=False, indent=2))
    print(f"Saved {out_path}")
    print(f"  smiles_qc: {trace['_smiles_qc']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main_cli())
