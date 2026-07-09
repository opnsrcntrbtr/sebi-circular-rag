"""Create the enriched golden_v6 benchmark seed from frozen golden_v5.

This does not invent new legal labels. It preserves the 56 curated v5 items in
the richer v6 schema so future ~200-item expansion has validation rails.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.benchmark import build_golden_v6, validate_golden  # noqa: E402


def main() -> None:
    seed = ROOT / "eval" / "golden" / "golden_v5.jsonl"
    out = ROOT / "eval" / "golden" / "golden_v6.jsonl"
    rows = build_golden_v6(seed, out)
    issues = validate_golden(rows)
    if issues:
        for issue in issues:
            print(f"{issue.item_id}: {issue.message}", file=sys.stderr)
        raise SystemExit(1)
    print(f"wrote {len(rows)} rows -> {out}")


if __name__ == "__main__":
    main()
