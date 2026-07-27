"""Backfill escalated golden_v7 rows from their Task-5 source candidate
(2026-07-25 remediation Task 7).

An escalation means pooling never surfaced the governing chunk. For
body_paraphrase and numeric_table rows the drafting candidate file records the
exact chunk the query was written from, and `answer_contains` was taken from
that chunk's text — so the gold chunk is recoverable deterministically, with no
re-judgment and no retrieval.

Rows that do not resolve to exactly one candidate are left escalated.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

sys.path.insert(0, str(ROOT / "scripts"))

from golden_v7.remap_doc_ids import MAPPING as RENUMBERED  # noqa: E402
from sebi_rag.benchmark import validate_golden_v7, write_jsonl  # noqa: E402
from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.ingest_pdf import normalize_circular_number as N  # noqa: E402

ANN = ROOT / "eval" / "golden" / "v7_annotations"
MIN_QUOTE_CHARS = 40


def _norm(s: str) -> str:
    return " ".join(s.split()).lower()


def _body(text: str) -> str:
    """Chunk text minus the leading "<doc> | <subject> | <section>" header."""
    first, sep, rest = text.partition("\n")
    return rest if sep and first.count(" | ") >= 2 else text


def _doc_keys(doc: str) -> set[str]:
    """Comparison keys for a candidate's doc id. The candidate files were
    mined BEFORE the 2026-07-25 renumbering, so a candidate may still carry a
    doc id that has since been corrected; accept either spelling."""
    keys = {N(doc)}
    if doc in RENUMBERED:
        keys.add(N(RENUMBERED[doc]))
    return keys


def find_source_chunk(row: dict, candidates: list[dict]) -> dict | None:
    lit = _norm(row.get("answer_contains", ""))
    if not lit:
        return None
    gold = {N(c) for c in row.get("relevant_circulars", [])}
    hits = [c for c in candidates
            if _doc_keys(c.get("doc", "")) & gold
            and lit in _norm(c.get("text", ""))]
    return hits[0] if len(hits) == 1 else None


def quote_for(candidate: dict, row: dict, min_chars: int = MIN_QUOTE_CHARS) -> str:
    """Smallest verbatim body window that contains answer_contains and clears
    min_chars after whitespace normalization."""
    body = _body(candidate["text"])
    lit = row["answer_contains"]
    i = body.find(lit)
    if i < 0:  # differs only by whitespace — fall back to the whole body
        return body.strip()
    start, end = i, i + len(lit)
    while len(" ".join(body[start:end].split())) < min_chars:
        if start > 0:
            start = max(0, start - 40)
        elif end < len(body):
            end = min(len(body), end + 40)
        else:
            break
    # Snap outward to whitespace so the quote never begins or ends mid-word
    # (these spans are read by human adjudicators).
    while start > 0 and not body[start - 1].isspace():
        start -= 1
    while end < len(body) and not body[end].isspace():
        end += 1
    return body[start:end].strip()


def _load_candidates() -> list[dict]:
    out = []
    for name in ("body_paraphrase", "numeric_table"):
        p = ANN / "candidates" / f"{name}.jsonl"
        out += [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()
                if l.strip()]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default=str(ROOT / "eval/golden/golden_v7.jsonl"))
    ap.add_argument("--corpus", default=str(ROOT / "data/corpus/circulars.jsonl"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    esc_path = ANN / "label_escalations.txt"
    esc_lines = [l for l in esc_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    escalated = {l.split(":", 1)[0].strip(): l for l in esc_lines}

    rows = load_golden(args.golden)
    cands = _load_candidates()
    filled, left = {}, {}
    for row in rows:
        rid = row["id"]
        if rid not in escalated or (row.get("relevant_chunks") or []):
            continue
        cand = find_source_chunk(row, cands)
        if not cand:
            left[rid] = escalated[rid]
            continue
        # Store the doc under its CURRENT number: candidates predate the
        # 2026-07-25 renumbering, so a stale id here would not resolve.
        doc = RENUMBERED.get(cand["doc"], cand["doc"])
        row["relevant_chunks"] = [{"doc": doc, "quote": quote_for(cand, row)}]
        filled[rid] = cand["chunk_id"]

    issues = validate_golden_v7(rows, chunks=load_circulars(args.corpus))
    for i in issues:
        print(f"{i.item_id}: {i.message}", file=sys.stderr)
    if issues:
        print(f"{len(issues)} issues — NOT written", file=sys.stderr)
        return 1

    print(f"backfilled {len(filled)} rows; {len(left)} remain escalated")
    for rid, cid in sorted(filled.items()):
        print(f"  {rid} <- {cid}")
    if args.dry_run:
        return 0

    write_jsonl(args.golden, rows)
    with (ANN / "votes.jsonl").open("a", encoding="utf-8") as f:
        for rid, cid in sorted(filled.items()):
            row = next(r for r in rows if r["id"] == rid)
            f.write(json.dumps({
                "id": rid, "annotator": "claude", "governing": [cid],
                "expected_literal": row.get("answer_contains", ""),
            }, ensure_ascii=False) + "\n")
    esc_path.write_text(
        "".join(f"{l}\n" for l in left.values()), encoding="utf-8")
    print(f"votes appended; {esc_path.name} now lists {len(left)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
