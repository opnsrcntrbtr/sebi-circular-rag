"""Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).

Carries all 56 rows unchanged (ids, labels, `seeded` status — no grandfathering:
seeded behaves as draft for promotion) and adds the v7-only fields.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.benchmark import validate_golden_v7, write_jsonl  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402


def carry_v6_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        r = dict(r)
        r.setdefault("as_of", None)
        r.setdefault("must_not_cite", [])
        out.append(r)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "eval" / "golden" / "golden_v7.jsonl"))
    args = ap.parse_args()
    rows = carry_v6_rows(load_golden(ROOT / "eval" / "golden" / "golden_v6.jsonl"))
    issues = validate_golden_v7(rows)
    if issues:
        for i in issues:
            print(f"{i.item_id}: {i.message}", file=sys.stderr)
        raise SystemExit(1)
    write_jsonl(args.out, rows)
    print(f"wrote {len(rows)} rows -> {args.out}")


if __name__ == "__main__":
    main()
