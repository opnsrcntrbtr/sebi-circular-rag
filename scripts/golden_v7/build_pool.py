"""Candidate pools for chunk-label judging (spec §6). TREC-style pooling:
union of system legs + gold-doc literal chunks, capped, deduped.

Real run (writes pools.jsonl):
    make golden-v7-pool          # needs the persisted index + MPS models
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag.benchmark import _norm_ws  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402


def assemble_pool(row, retriever, reranker, cap: int = 20,
                  gold_literal_cap: int = 6):
    """TREC-style pool: gold-doc literal matches lead, then round-robin over
    [reranked, dense, raw-BM25] top-15 legs until `cap`, deduped by chunk id.

    `gold_literal_cap` bounds the literal-match step, and those matches are
    reranked rather than taken in document order. Without both, a common
    must_contain literal ("broker") matches hundreds of chunks in a master
    circular and fills the entire cap with the document's opening pages —
    preamble and table-of-contents stubs — starving the ranked legs entirely.
    Measured 2026-07-25: this saturated 92 of 207 pools and caused 24 of 25
    labelling escalations.
    """
    gold_docs = set(row.get("relevant_circulars", []))
    literals = [_norm_ws(m) for m in row.get("must_contain", []) if m]
    q = row["query"]

    pool, seen = [], set()

    def add(c, limit=None):
        if c.id not in seen and len(pool) < (cap if limit is None else limit):
            seen.add(c.id)
            pool.append(c)

    literal_hits = [c for c in retriever.chunks
                    if c.doc_id in gold_docs and literals
                    and any(lit in _norm_ws(c.text) for lit in literals)]
    if literal_hits:
        for c in [c for c, _ in reranker.rerank(q, literal_hits)]:
            add(c, limit=min(gold_literal_cap, cap))
    rrf = retriever.retrieve(q, top_n=50)
    reranked = [c for c, _ in reranker.rerank(q, [c for c, _ in rrf])[:15]]
    dense = [retriever.chunks[i] for i, _ in retriever.dense.search(q, 15)]
    bm25 = [retriever.chunks[i] for i, _ in retriever.sparse.search(q, 15)]  # raw query: no expand_query
    legs = [reranked, dense, bm25]
    i = 0
    while len(pool) < cap and any(legs):
        leg = legs[i % 3]
        if leg:
            add(leg.pop(0))
        i += 1
    return pool


def main() -> None:
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.rerank import CrossEncoderReranker
    from sebi_rag.retrieve import HybridRetriever
    from sebi_rag.settings import Settings

    s = Settings.load()
    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(s.index_dir, emb)
    rer = CrossEncoderReranker(device="mps")
    golden = load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")
    out = ROOT / "eval" / "golden" / "v7_annotations" / "pools.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in golden:
            if row.get("abstain"):
                continue
            pool = assemble_pool(row, retr, rer)
            f.write(json.dumps({"id": row["id"], "candidates": [
                {"chunk_id": c.id, "doc": c.doc_id, "text": c.text}
                for c in pool]}, ensure_ascii=False) + "\n")
            print(row["id"], len(pool), file=sys.stderr)
    print(f"wrote pools -> {out}")


if __name__ == "__main__":
    main()
