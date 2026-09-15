"""Chunk-quality-metric detector (2026-09-15).

Preregistration: docs/superpowers/specs/2026-09-03-chunk-quality-metric-prereg.md

Three chunker fixes (2026-09-01/02/03-*) have shipped against
hierarchical_chunk() with ZERO production metric - each judged by
hand-inspecting one document, because golden_v7 (n=260) cannot resolve
boundary-level effects this small. This is the gap-filler: two rates computed
directly over the persisted chunks, no query/golden set involved.

**Not a cross-version comparison tool.** The prereg's original §1 assumed
chunker_version is stamped per-chunk in chunks.jsonl ("already present per
retrieve.py:243") - checked, and it is not: retrieve.py:243 stamps
chunker_version into meta.json (index-wide), not into individual chunk
records. There is also no retained historical snapshot - each `make reindex`
overwrites chunks.jsonl in place, so the 2026-09-01/02 chunker versions'
actual output no longer exists to compare against. This script therefore
reports a SINGLE current-version point measurement; comparison over time
happens by diffing two runs' saved report JSON, not within one run.

**Both rates require hand-labeled validation (spec §2) before they are
trustworthy enough to cite** - see the "not permitted" list below and
docs/status.md's dated entry for this run's precision/recall numbers.

Detector logic is deliberately independent of segment.py's own
_is_table_row_candidate/_is_table_row_filler - reusing the production
discriminator to validate itself would be circular (a chunk that dodges the
discriminator by construction would also dodge a detector built from the
same predicate).

Not permitted (spec §4):
- Reporting either rate without its precision/recall numbers.
- Retroactively scoring the three already-shipped fixes and treating that as
  proof any one was net-positive for retrieval quality - this measures chunk
  SHAPE, not downstream retrieval effect.
- Using this detector as the basis for a next interleaved-layout fix without
  a separate, explicit design decision.
- Extending the detector to fire on golden_v7 query-answer text - corpus-only
  by design.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_NUMBERED_STUB_RE = re.compile(r"^\s*\d{1,3}\.\s*$")
# {1,4} not {1,3}: widened 2026-09-16 after live hand-labeling found every
# year-prefixed sentence ("2011. approval to...") false-flagged as an orphan -
# a leading 4-digit year IS "this line already carries a numeric marker" for
# the purpose of ruling out "no marker at all", even though it isn't a table
# row number. Table row numbers in this corpus don't reach 4 digits, so this
# widening doesn't cost real shredded-stub/orphan recall.
_LEADING_NUMBER_RE = re.compile(r"^\s*\d{1,4}[.\)]")
_ORPHAN_MAX_BODY_CHARS = 120
# Document preamble/header boilerplate - found live in the same hand-labeling
# pass: every sampled document's opening "CIRCULAR\n<id> <date>\nTo," chunk
# false-flagged as an orphan (short, no leading numbered marker). This is the
# OPENING counterpart to mine_strata.py's BOILERPLATE_RE (which catches the
# closing "Yours faithfully"/"available on SEBI website" signoff shape).
_PREAMBLE_BOILERPLATE_RE = re.compile(r"^\s*(MASTER\s+)?CIRCULAR\b")


def _body(text: str) -> str:
    """Drop the structural header line, matching mine_strata.py's own _body()
    convention: chunks.jsonl's text field is "header\\n\\nbody"."""
    parts = text.split("\n", 1)
    return parts[1] if len(parts) > 1 else parts[0]


def is_shredded_row_stub(text: str) -> bool:
    """A chunk whose entire body is a bare numbered marker with no
    substantive content - e.g. a lone '5.' left behind when a table row's
    label and value landed in a different chunk from its number."""
    return bool(_NUMBERED_STUB_RE.match(_body(text).strip()))


def is_orphan_fragment(text: str) -> bool:
    """A chunk that reads as a title/label continuation - short, no leading
    numbered-row marker of its own, and no line within the chunk carries one
    either - the TOC-wrapped-title and finstat-row-label failure shapes: the
    label lands in one chunk, its owning number in another."""
    body = _body(text).strip()
    if not body or len(body) > _ORPHAN_MAX_BODY_CHARS:
        return False
    if _PREAMBLE_BOILERPLATE_RE.match(body):
        return False
    lines = [ln.strip() for ln in body.split("\n") if ln.strip()]
    if not lines:
        return False
    return not any(_LEADING_NUMBER_RE.match(ln) for ln in lines)


_TERMINAL_PUNCT = (".", ":", ";", ")")
# False-positive guards, all found live in the 2026-09-16 hand-labeling pass
# over 117 real detector positives (raw precision 0.872 before these fixes):
_CURRENCY_TAIL_RE = re.compile(r"(Rs\.?|INR|USD|₹|\$)\s*$", re.IGNORECASE)
_MONTH_TAIL_RE = re.compile(
    r"\b(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|June?|July?|Aug(ust)?|"
    r"Sep(t(ember)?)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s*$", re.IGNORECASE)
# Compound sub-clause number, e.g. "42.43" or "6.6.7" - a clause/paragraph
# reference, not a self-numbered list item. Narrower than _LEADING_NUMBER_RE
# on purpose (2026-09-16 recall-check finding): a plain "8. Implementation..."
# is a complete item on its own, but "42.43 Illustration..." is NOT - the
# digit immediately after the first period means this is clause 42's 43rd
# sub-point, and excluding it (as the original, broader prev-marker check
# did) silently suppressed genuine Annexure-reference splits.
_COMPOUND_CLAUSE_RE = re.compile(r"^\s*\d{1,3}\.\d")


def is_interleaved_split(text: str) -> bool:
    """A chunk containing at least one bare numbered-marker LINE sitting
    between two lines that look like the two halves of one wrapped label -
    the real confirmed failure shape (2026-09-16 hand-labeling): a chunk with
    many numbered rows, most clean, where one row's wrapped label got split
    by its own marker landing in the middle of it. This is a LINE-level check
    within a chunk, unlike is_shredded_row_stub/is_orphan_fragment which
    classify the chunk's body as a whole - neither of those can see a defect
    that occurs inside an otherwise-normal, content-rich chunk.

    Three exclusions, each found live and each a real false-positive pattern,
    not speculative: a currency amount ('Rs\\n150.') or a date's day-of-month
    ('ending March\\n31.') coincidentally matches the bare-marker regex, and a
    marker whose PREVIOUS line already starts with its own leading marker
    means that previous line is a complete, self-numbered item on its own -
    the next marker starts a new item, not a split of the previous one."""
    body = _body(text)
    lines = [ln.strip() for ln in body.split("\n") if ln.strip()]
    for i in range(1, len(lines) - 1):
        if not _NUMBERED_STUB_RE.match(lines[i]):
            continue
        prev_line, next_line = lines[i - 1], lines[i + 1]
        if (_LEADING_NUMBER_RE.match(prev_line)
                and not _COMPOUND_CLAUSE_RE.match(prev_line)):
            continue
        if _CURRENCY_TAIL_RE.search(prev_line) or _MONTH_TAIL_RE.search(prev_line):
            continue
        prev_incomplete = not prev_line.endswith(_TERMINAL_PUNCT)
        next_is_continuation = not _LEADING_NUMBER_RE.match(next_line)
        if prev_incomplete and next_is_continuation:
            return True
    return False


def compute_rates(chunks_path: Path) -> dict:
    """count/total_chunks for all three detectors over the persisted chunks."""
    shredded = orphan = interleaved = total = 0
    with chunks_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            total += 1
            text = json.loads(line)["text"]
            if is_shredded_row_stub(text):
                shredded += 1
            if is_orphan_fragment(text):
                orphan += 1
            if is_interleaved_split(text):
                interleaved += 1
    return {
        "total_chunks": total,
        "shredded_row_count": shredded,
        "orphan_fragment_count": orphan,
        "interleaved_split_count": interleaved,
        "shredded_row_rate": round(shredded / total, 6) if total else 0.0,
        "orphan_fragment_rate": round(orphan / total, 6) if total else 0.0,
        "interleaved_split_rate": round(interleaved / total, 6) if total else 0.0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index-dir", default=str(ROOT / "data" / "index"))
    ap.add_argument("--out", default=str(
        ROOT / "reports" / f"chunk-quality-metric-{dt.date.today().isoformat()}.json"))
    args = ap.parse_args()

    index_dir = Path(args.index_dir)
    meta = json.loads((index_dir / "meta.json").read_text(encoding="utf-8"))
    rates = compute_rates(index_dir / "chunks.jsonl")

    payload = {
        "derived_at": dt.datetime.now().isoformat(timespec="seconds"),
        "chunker_version": meta.get("chunker_version"),
        **rates,
        # Precision/recall against a hand-labeled sample are NOT computed here -
        # per the spec's §2, a corpus-wide rate is not citable without them.
        # Filled in separately once the hand-labeling round-trip (spec §2,
        # docs/status.md's 2026-09-02 scoping entry's stratified sample) completes.
        "shredded_row_precision": None,
        "shredded_row_recall": None,
        "orphan_fragment_precision": None,
        "orphan_fragment_recall": None,
        "interleaved_split_precision": None,
        "interleaved_split_recall": None,
        "directional_only": True,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"chunker_version={payload['chunker_version']} "
          f"total_chunks={rates['total_chunks']} "
          f"interleaved_split_rate={rates['interleaved_split_rate']} "
          f"shredded_row_rate={rates['shredded_row_rate']} "
          f"orphan_fragment_rate={rates['orphan_fragment_rate']}", file=sys.stderr)
    print(f"wrote {out_path} (directional_only=True until hand-labeled "
          f"precision/recall are filled in - see spec §2)", file=sys.stderr)


if __name__ == "__main__":
    main()
