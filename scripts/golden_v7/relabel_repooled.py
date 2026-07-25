"""Label the 7 rows re-pooled after the assemble_pool fix (2026-07-25
remediation Task 8).

Picks, per row, the allowed pooled chunk that carries the row's
`answer_contains` provision; for multi_hop rows it additionally looks for a
supporting chunk from the pair's OTHER circular so both sides are covered.
`must_not_cite` docs are never eligible (they are the row's distractor by
construction). Rows with no governing chunk stay escalated.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from golden_v7.backfill_escalations import quote_for  # noqa: E402
from sebi_rag.benchmark import validate_golden_v7, write_jsonl  # noqa: E402
from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.ingest_pdf import normalize_circular_number as N  # noqa: E402

ANN = ROOT / "eval" / "golden" / "v7_annotations"
TARGETS = ["v7-bp-013", "v7-ls-010", "v7-mh-009", "v7-mh-012",
           "v7-mh-016", "v7-mh-018", "v7-rb-010"]


def _norm(s: str) -> str:
    return " ".join(s.split()).lower()


def _body(text: str) -> str:
    first, sep, rest = text.partition("\n")
    return rest if sep and first.count(" | ") >= 2 else text


def pick(row: dict, candidates: list[dict]) -> list[tuple[dict, str]]:
    """(candidate, quote) pairs for this row: the answer_contains carrier
    first, then for multi_hop a supporting chunk from the other circular."""
    banned = {N(d) for d in (row.get("must_not_cite") or [])}
    gold = [c for c in row.get("relevant_circulars", [])]
    allowed = [c for c in candidates if N(c["doc"]) not in banned
               and any(N(c["doc"]) == N(g) for g in gold)]
    out: list[tuple[dict, str]] = []

    lit = _norm(row.get("answer_contains", ""))
    primary = next((c for c in allowed if lit and lit in _norm(_body(c["text"]))), None)
    if not primary:
        return []
    # 140 rather than the 40-char validator floor: these spans are read by
    # human adjudicators, and a quote clipped at the floor often loses the
    # clause that makes the provision legible.
    out.append((primary, quote_for({"text": _body(primary["text"])}, row,
                                   min_chars=140)))

    if row.get("task_type") == "multi_hop":
        other = [g for g in gold if N(g) != N(primary["doc"])]
        musts = [_norm(m) for m in (row.get("must_contain") or []) if m]
        for c in allowed:
            if not any(N(c["doc"]) == N(o) for o in other):
                continue
            b = _body(c["text"])
            hit = next((m for m in musts if m in _norm(b)), None)
            if hit:
                i = _norm(b).find(hit)
                start = max(0, i - 90)
                end = min(len(b), i + len(hit) + 160)
                while start > 0 and not b[start - 1].isspace():
                    start -= 1
                while end < len(b) and not b[end].isspace():
                    end += 1
                q = b[start:end].strip()
                if len(_norm(q)) >= 40:
                    out.append((c, q))
                    break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default=str(ROOT / "eval/golden/golden_v7.jsonl"))
    ap.add_argument("--corpus", default=str(ROOT / "data/corpus/circulars.jsonl"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pools = {json.loads(l)["id"]: json.loads(l) for l in
             (ANN / "pools.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    rows = load_golden(args.golden)
    labeled, still = {}, []
    for row in rows:
        if row["id"] not in TARGETS:
            continue
        picks = pick(row, pools[row["id"]]["candidates"])
        if not picks:
            still.append(row["id"])
            continue
        row["relevant_chunks"] = [{"doc": c["doc"], "quote": q} for c, q in picks]
        labeled[row["id"]] = [c["chunk_id"] for c, _ in picks]

    issues = validate_golden_v7(rows, chunks=load_circulars(args.corpus))
    for i in issues:
        print(f"{i.item_id}: {i.message}", file=sys.stderr)
    if issues:
        print(f"{len(issues)} issues — NOT written", file=sys.stderr)
        return 1

    print(f"labeled {len(labeled)}; still escalated {len(still)}: {still}")
    for rid, cids in labeled.items():
        row = next(r for r in rows if r["id"] == rid)
        print(f"\n{rid} ({row['task_type']}) — {len(cids)} span(s)")
        for span in row["relevant_chunks"]:
            print(f"   doc={span['doc']}")
            print(f"   q  ={' '.join(span['quote'].split())[:190]}")
    if args.dry_run:
        return 0

    write_jsonl(args.golden, rows)
    with (ANN / "votes.jsonl").open("a", encoding="utf-8") as f:
        for rid, cids in labeled.items():
            row = next(r for r in rows if r["id"] == rid)
            f.write(json.dumps({
                "id": rid, "annotator": "claude", "governing": cids,
                "expected_literal": row.get("answer_contains", ""),
            }, ensure_ascii=False) + "\n")
    esc = ANN / "label_escalations.txt"
    keep = [l for l in esc.read_text(encoding="utf-8").splitlines()
            if l.strip() and l.split(":", 1)[0].strip() in set(still)]
    esc.write_text("".join(f"{l}\n" for l in keep), encoding="utf-8")
    print(f"\nvotes appended; {esc.name} now lists {len(keep)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
