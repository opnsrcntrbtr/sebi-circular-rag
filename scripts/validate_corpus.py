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
from sebi_rag.ingest_pdf import normalize_circular_number, parse_meta  # noqa: E402

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PROV_RE = re.compile(r"Parsed from PDF (\S+\.pdf)", re.I)

# 2011-era master circulars ("SEBI/IMD/MC No.2/836/2011") authentically
# contain a space in "MC No." — not a parsing defect. Stored numbers keep
# the document's own spelling, so this known legacy shape is carved out
# rather than rewritten or the whitespace check dropped generally.
_LEGACY_MC_NO_RE = re.compile(r"\bMC No\.\s*\d+\b", re.I)


def _plausible(n: str) -> bool:
    if not n or "/" not in n or not any(ch.isdigit() for ch in n):
        return False
    if " " in n:
        return bool(_LEGACY_MC_NO_RE.search(n))
    return True


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
        # A record's own number must be derivable from its own text. Catches
        # both the R3 last-resort fallback picking up a CITED number and a
        # record whose text was overwritten with another circular's body.
        derived = parse_meta(r.get("text", "")).get("circular_number", "")
        if derived and normalize_circular_number(derived) != key:
            violations.append(
                f"{where}: circular_number not derivable from own text "
                f"(text yields {derived!r})")
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
    # Two records may never share one body text (catches the shared-text
    # backfill bug: metadata written per-record, text from a stale variable).
    by_text: dict[str, str] = {}
    for i, r in enumerate(records):
        t = " ".join((r.get("text") or "").split())
        if not t:
            continue
        n = r.get("circular_number", "") or "<empty>"
        if t in by_text:
            violations.append(
                f"record {i} ({n}): duplicate text — identical body to "
                f"{by_text[t]}")
        else:
            by_text[t] = n
    return violations


def validate_deep(records: list[dict], raw_dir: Path) -> list[str]:
    """Every record's text must match the PDF its provenance names.

    Slow (re-extracts every PDF) — opt in with --deep after any
    ingest/backfill/repair.
    """
    from sebi_rag.ingest_pdf import extract_text

    violations: list[str] = []
    for i, r in enumerate(records):
        n = r.get("circular_number", "") or "<empty>"
        m = PROV_RE.search(r.get("provenance", ""))
        if not m:
            violations.append(f"record {i} ({n}): provenance names no PDF")
            continue
        pdf = raw_dir / m.group(1)
        if not pdf.exists():
            violations.append(f"record {i} ({n}): provenance PDF missing: {m.group(1)}")
            continue
        try:
            got = " ".join(extract_text(pdf).split())
        except Exception as exc:  # noqa: BLE001
            violations.append(f"record {i} ({n}): PDF extract failed: {exc}")
            continue
        if got != " ".join((r.get("text") or "").split()):
            violations.append(
                f"record {i} ({n}): text does not match provenance PDF {m.group(1)}")
    return violations


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--deep"]
    deep = "--deep" in sys.argv[1:]
    path = Path(args[0] if args else "data/corpus/circulars.jsonl")
    records = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
               if l.strip()]
    violations = validate(records)
    if deep:
        violations += validate_deep(records, path.parents[1] / "raw")
    for v in violations:
        print(v)
    print(f"{len(records)} records, {len(violations)} violations"
          f"{' (deep)' if deep else ''}")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
