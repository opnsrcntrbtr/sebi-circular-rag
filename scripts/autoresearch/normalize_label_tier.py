"""Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.

golden_v7 carries label_source as 14 distinct prose values. This maps them to a
fixed vocabulary so metrics can be reported per tier, and leaves label_source
untouched as the provenance trail.

`label_source` records the LAST WRITER, not who reviewed a row. The audit
(reports/label_provenance_audit.md) found the 30 human-labelled rows scattered
across label_source values — 17 under `v7-draft-2026-07`, 7 under a claude
string — so human review is read from packet_human/labels_template.csv and
overrides the string.

Reporting rule (spec A §8.4): tiered reporting with NO designated primary set.

    .venv/bin/python scripts/autoresearch/normalize_label_tier.py --write
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
PACKET = ROOT / "eval" / "golden" / "v7_annotations" / "packet_human" / "labels_template.csv"

TIERS = (
    "human",
    "arbitrated",
    "model_single",
    "inherited_v5",
    "draft_seeded",
    "unknown",
)


def classify_tier(label_source: str, *, human_reviewed: bool = False) -> str:
    """Map provenance to the controlled vocabulary.

    `human_reviewed` (row appears in the human labelling packet) wins over any
    string, because the string names whoever wrote last. Otherwise: explicit
    human acts, then arbitration, then inheritance, then a plain model pass.
    """
    if human_reviewed:
        return "human"
    s = (label_source or "").strip().lower()
    if s.startswith("corrected:") or s == "external-flip":
        return "human"
    if "arbitration resolved" in s or "qwen failed to find governing" in s:
        return "arbitrated"
    if s.startswith("golden_v5"):
        return "inherited_v5"
    if s.startswith("v7-draft"):
        return "draft_seeded"
    if s.startswith("claude"):
        return "model_single"
    return "unknown"


def human_reviewed_ids(packet: Path = PACKET) -> set[str]:
    """Row ids present in the human labelling packet."""
    import csv

    if not packet.exists():
        return set()
    with packet.open(newline="", encoding="utf-8") as f:
        return {r["id"].strip() for r in csv.DictReader(f) if r.get("id", "").strip()}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", type=Path, default=GOLDEN)
    ap.add_argument("--packet", type=Path, default=PACKET)
    ap.add_argument("--write", action="store_true", help="write the file in place")
    args = ap.parse_args()

    reviewed = human_reviewed_ids(args.packet)
    rows = [
        json.loads(line)
        for line in args.golden.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    counts: collections.Counter[str] = collections.Counter()
    for row in rows:
        row["label_tier"] = classify_tier(
            row.get("label_source", ""), human_reviewed=row["id"] in reviewed
        )
        counts[row["label_tier"]] += 1

    total = len(rows)
    print(f"rows: {total}  (human packet ids: {len(reviewed)})")
    for tier in TIERS:
        n = counts.get(tier, 0)
        print(f"  {tier:<14} {n:>4}  ({100 * n / total:.1f}%)")

    if args.write:
        args.golden.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
            encoding="utf-8",
        )
        print(f"\nwrote {args.golden}")
    else:
        print("\ndry run; pass --write to apply")


if __name__ == "__main__":
    main()
