"""Classify golden/probe queries against a TREC runfile (throwaway research).

Classes: hit (relevant doc within top-10 deduped docs), ranked_low (relevant
doc in candidates but first appears after doc-rank 10), candidate_miss
(relevant doc absent from the top-50 candidate set entirely).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.ingest_pdf import normalize_circular_number  # noqa: E402


def _doc(chunk_id: str) -> str:
    return chunk_id.split("#", 1)[0]


def classify_query(
    ranked_chunk_ids: list[str], relevant_circulars: list[str]
) -> tuple[str, int]:
    relevant = {normalize_circular_number(c) for c in relevant_circulars}
    docs: list[str] = []
    seen: set[str] = set()
    for cid in ranked_chunk_ids:
        d = normalize_circular_number(_doc(cid))
        if d not in seen:
            seen.add(d)
            docs.append(d)
    for rank, d in enumerate(docs, start=1):
        if d in relevant:
            return ("hit" if rank <= 10 else "ranked_low"), rank
    return "candidate_miss", -1


def _ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def classify_answer(
    ranked_chunk_ids: list[str],
    chunk_texts: dict[str, str],
    must_contain: list[str],
) -> tuple[str, int]:
    """Answer-level classification: a candidate chunk qualifies if it contains
    any must_contain needle (whitespace-normalized). Spec's 'gold chunk in
    top-k' criterion — stricter than doc-level."""
    needles = [_ws(m) for m in must_contain if m.strip()]
    for rank, cid in enumerate(ranked_chunk_ids, start=1):
        text = _ws(chunk_texts.get(cid, ""))
        if any(n in text for n in needles):
            return ("hit" if rank <= 10 else "ranked_low"), rank
    return "candidate_miss", -1


def load_run(path: Path) -> dict[str, list[str]]:
    """Chunk IDs embed section headings containing spaces, so parse TREC
    fields positionally: qid, Q0 at the front; rank, score, run name at the
    end; everything between is the chunk id."""
    run: dict[str, list[tuple[int, str]]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        fields = line.split(" ")
        qid, cid, rank = fields[0], " ".join(fields[2:-3]), int(fields[-3])
        run.setdefault(qid, []).append((rank, cid))
    return {q: [c for _, c in sorted(v)] for q, v in run.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--golden", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", required=True, help="label: golden_v6 | probes_v1")
    ap.add_argument("--chunks", default=str(ROOT / "data" / "index" / "chunks.jsonl"),
                    help="chunk texts for answer-level classification")
    args = ap.parse_args()

    run = load_run(Path(args.run))
    needed = {cid for cids in run.values() for cid in cids}
    chunk_texts: dict[str, str] = {}
    with Path(args.chunks).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            if c["id"] in needed:
                chunk_texts[c["id"]] = c["text"]
    rows = [
        json.loads(line)
        for line in Path(args.golden).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    failures, hits, skipped = [], 0, 0
    for row in rows:
        if row.get("abstain"):
            skipped += 1
            continue
        ranked = run.get(row["id"], [])
        cls, rank = classify_query(ranked, row["relevant_circulars"])
        must = row.get("must_contain", [])
        if must:
            a_cls, a_rank = classify_answer(ranked, chunk_texts, must)
        else:  # no needle -> answer level falls back to doc level
            a_cls, a_rank = cls, rank
        if cls == "hit" and a_cls == "hit":
            hits += 1
            continue
        failures.append({
            "id": row["id"],
            "query": row["query"],
            "class": cls,
            "first_relevant_rank": rank,
            "answer_class": a_cls,
            "first_answer_rank": a_rank,
            "relevant_circulars": row["relevant_circulars"],
            "must_contain": must,
            "task_type": row.get("task_type", ""),
            "source": args.source,
        })
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in failures:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({
        "answerable": len(rows) - skipped, "hits": hits,
        "doc_candidate_miss": sum(1 for r in failures if r["class"] == "candidate_miss"),
        "doc_ranked_low": sum(1 for r in failures if r["class"] == "ranked_low"),
        "answer_candidate_miss": sum(1 for r in failures if r["answer_class"] == "candidate_miss"),
        "answer_ranked_low": sum(1 for r in failures if r["answer_class"] == "ranked_low"),
        "out": str(out),
    }, indent=2))


if __name__ == "__main__":
    main()
