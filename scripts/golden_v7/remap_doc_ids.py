"""Rewrite golden_v7 doc references after the corpus renumbering
(2026-07-25 remediation Task 4).

Rewrites relevant_circulars, must_not_cite and every span's `doc`, matching
under normalize_circular_number so a differently-prefixed spelling still maps.
Span `quote` values are untouched — they resolve by text, not by id.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.benchmark import validate_golden_v7, write_jsonl  # noqa: E402
from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.ingest_pdf import normalize_circular_number as N  # noqa: E402

# old circular_number -> new, from the Task 3 renumber audit (all 12 accepted;
# every derived value was verified present in its own document's header).
MAPPING = {
    "SEBI/HO/MRD2/DCAP/CIR/P/2019/146": "SEBI/HO/AFD/AFD-PoD-2/CIR/P/2023/148",
    "CIR/MRD/DSA/03/2012": "3/CIR/P/2023/104",
    "SEBI/HO/MRD/MRD-POD-1/P/CIR": "SEBI/HO/MRD/MRD-POD-1/P/CIR/2023/78",
    "SEBI/HO/IMD/DF2/CIR/P/2019/65": "POD2/P/CIR/2023/48",
    "SEBI/HO/IMD/DF1/CIR/P/2020/182": "DOF1/P/CIR/2021/694",
    "PoD-2/P/CIR/2024/40": "SEBI/HO/AFD/AFD-PoD-2/P/CIR/2024/40",
    "CIR/IMD/DF/5/2013": "CIR/IMD/DF/14/2013",
    "CIR/MRD/DP/14": "CIR/MRD/DP/14/2013",
    "CIR/MRD/DP/13": "CIR/MRD/DP/13/2013",
    "CIR/4/51/2000": "SEBI/IMD/MC No.3/10554/2012",
    "CIR/MRD/DP/10": "CIR/MRD/DP/10/2012",
    "CIR/MRD/DP/41": "CIR/MRD/DP/41/2010",
}


def remap(rows: list[dict], mapping: dict[str, str]) -> tuple[list[dict], int]:
    keyed = {N(k): v for k, v in mapping.items()}
    changed = 0
    out = []
    for row in rows:
        row = json.loads(json.dumps(row))  # deep copy, rows are plain JSON
        for field in ("relevant_circulars", "must_not_cite"):
            vals = row.get(field) or []
            new_vals = []
            for v in vals:
                nv = keyed.get(N(v))
                if nv:
                    changed += 1
                    new_vals.append(nv)
                else:
                    new_vals.append(v)
            if vals:
                row[field] = new_vals
        for span in row.get("relevant_chunks") or []:
            if isinstance(span, dict):
                nv = keyed.get(N(span.get("doc", "")))
                if nv:
                    changed += 1
                    span["doc"] = nv
        out.append(row)
    return out, changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default=str(ROOT / "eval/golden/golden_v7.jsonl"))
    ap.add_argument("--corpus", default=str(ROOT / "data/corpus/circulars.jsonl"))
    args = ap.parse_args()
    rows = load_golden(args.golden)
    rows, n = remap(rows, MAPPING)
    issues = validate_golden_v7(rows, chunks=load_circulars(args.corpus))
    for i in issues:
        print(f"{i.item_id}: {i.message}", file=sys.stderr)
    if issues:
        print(f"{len(issues)} issues — NOT written", file=sys.stderr)
        return 1
    write_jsonl(args.golden, rows)
    print(f"remapped {n} references across {len(rows)} rows -> {args.golden}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
