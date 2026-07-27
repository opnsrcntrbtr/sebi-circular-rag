"""Dry-run audit of every circular_number renumber.py would change, with the
document's own header alongside, so each change gets a human verdict before
the corpus is rewritten (2026-07-25 remediation Task 3).

Read-only. Run AFTER Task 2 — on the unrepaired corpus the 5 shared-text
records all resolve to PoD-1/P/CIR/2024/163 (a 5-way collision).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.ingest_pdf import (  # noqa: E402
    _header, normalize_circular_number, parse_meta,
)


def main() -> int:
    corpus = ROOT / "data/corpus/circulars.jsonl"
    recs = [json.loads(l) for l in corpus.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    changes = []
    for i, r in enumerate(recs, 1):
        m = parse_meta(r.get("text", ""))
        new = m.get("circular_number", "")
        old = r.get("circular_number", "")
        if new and new != old:
            changes.append((i, old, new, r.get("issue_date", ""),
                            m.get("issue_date", ""), _header(r.get("text", ""))))
    print(f"{len(changes)} of {len(recs)} records would be renumbered\n")
    for i, old, new, od, nd, head in changes:
        print(f"line {i}")
        print(f"  old: {old}")
        print(f"  new: {new}")
        if od != nd:
            print(f"  issue_date: {od} -> {nd}")
        print(f"  header: {' '.join(head.split())[:160]}")
        print()
    # collision check: the rewrite must keep numbers unique
    final: dict[str, list[int]] = {}
    for i, r in enumerate(recs, 1):
        m = parse_meta(r.get("text", ""))
        n = m.get("circular_number", "") or r.get("circular_number", "")
        final.setdefault(normalize_circular_number(n), []).append(i)
    dupes = {k: v for k, v in final.items() if len(v) > 1}
    print(f"post-renumber collisions: {len(dupes)}")
    for k, v in dupes.items():
        print(f"  {k}: lines {v}")
    return 1 if dupes else 0


if __name__ == "__main__":
    raise SystemExit(main())
