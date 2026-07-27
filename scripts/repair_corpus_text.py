"""Repair the 6 records whose body text was overwritten with one shared
circular's text (2026-07-25 remediation Task 2).

Root cause: a batch write assigned `text` and `provenance` from stale
variables while metadata came per-record from elsewhere; `ingest()` cannot
produce this shape. The correct PDFs were left on disk unreferenced.

Idempotent: re-ingests each record from its real PDF with replace=True.
Offline — every PDF is already in data/raw/.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.ingest_pdf import ingest, normalize_circular_number  # noqa: E402

# circular_number -> the orphan PDF in data/raw/ that actually contains it.
# Verified: parse_meta() on each PDF yields this number, its issue_date and
# its subject.
REPAIRS = {
    "DOF3/P/CIR/2022/39": "1648639233807.pdf",
    "DOF3/P/CIR/2022/49": "1649673908121.pdf",
    "DOF3/P/CIR/2022/82": "1655291815532.pdf",
    "DOF1/P/CIR/2022/105": "1659094793301.pdf",
    "DOF2/P/CIR/2022/161": "1669373687117.pdf",
    "PoD-1/P/CIR/2024/163": "1732618015389.pdf",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(ROOT / "data/corpus/circulars.jsonl"))
    ap.add_argument("--raw", default=str(ROOT / "data/raw"))
    args = ap.parse_args()
    corpus, raw = Path(args.corpus), Path(args.raw)

    before = {normalize_circular_number(json.loads(l)["circular_number"])
              for l in corpus.read_text(encoding="utf-8").splitlines() if l.strip()}
    drift = 0
    for num, pdf in REPAIRS.items():
        if normalize_circular_number(num) not in before:
            print(f"WARNING: {num} not in corpus — skipping", file=sys.stderr)
            continue
        rec = ingest(raw / pdf, corpus, replace=True)
        got = rec.get("circular_number", "")
        ok = normalize_circular_number(got) == normalize_circular_number(num)
        drift += 0 if ok else 1
        print(f"{'OK ' if ok else 'DRIFT'} {num}: re-ingested from {pdf} "
              f"-> {got} ({rec.get('issue_date')})")
    after = [json.loads(l) for l in corpus.read_text(encoding="utf-8").splitlines()
             if l.strip()]
    print(f"corpus now {len(after)} records")
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
