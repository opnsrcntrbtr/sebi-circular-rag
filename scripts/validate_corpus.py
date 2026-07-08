"""Validate corpus invariants after any ingest/backfill/repair.

Checks (per docs/superpowers/plans/2026-07-08-regai-inspired-enhancements.md
section B.4): every record has a plausible circular_number (non-empty, no
whitespace, contains '/' and a digit); numbers are unique under
normalization (catches SEBI/-prefix duplicates, R4); version_lineage
contains no self-references (catches stage-6 mis-assignment fallout, R3);
issue_date is ISO or empty.

Usage: uv run python scripts/validate_corpus.py [data/corpus/circulars.jsonl]
Exit 0 = clean, 1 = violations (printed one per line).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sebi_rag.ingest_pdf import normalize_circular_number  # noqa: E402

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _plausible(n: str) -> bool:
    return bool(n) and " " not in n and "/" in n and any(ch.isdigit() for ch in n)


def validate(records: list[dict]) -> list[str]:
    violations: list[str] = []
    seen: dict[str, str] = {}
    for i, r in enumerate(records):
        n = r.get("circular_number", "")
        where = f"record {i} ({n or '<empty>'})"
        if not _plausible(n):
            violations.append(f"{where}: implausible circular_number")
            continue
        key = normalize_circular_number(n)
        if key in seen:
            violations.append(f"{where}: duplicate of {seen[key]} under normalization")
        else:
            seen[key] = n
        for ref in r.get("version_lineage", []):
            if normalize_circular_number(ref) == key:
                violations.append(f"{where}: self-reference in version_lineage")
        d = r.get("issue_date", "")
        if d and not ISO_DATE_RE.match(d):
            violations.append(f"{where}: non-ISO issue_date {d!r}")
    return violations


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/corpus/circulars.jsonl")
    records = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
               if l.strip()]
    violations = validate(records)
    for v in violations:
        print(v)
    print(f"{len(records)} records, {len(violations)} violations")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
