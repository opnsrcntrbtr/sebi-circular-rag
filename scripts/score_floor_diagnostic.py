"""Score-floor false-abstention diagnostics (hybrid-gate-prereg 2026-08-13, §10b).

Re-runs the 19 score_floor rows against the current index (rebuilt
2026-08-17, 730 circulars / 78,630 chunks) and classifies each:

- NOW_PASSES    relevant doc in fusion pool AND top CE score >= 0.42
- CE_MISMATCH   relevant doc in fusion pool but top CE score < 0.42
- RECALL_DEEP   not in top-50 pool, but reachable at dense k=200
- RECALL_ABSENT in index, unreachable even at dense k=200
- DOC_MISSING   relevant circular absent from the index entirely

Usage: PYTHONPATH=src python scripts/score_floor_diagnostic.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

for _k, _v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(_k, _v)

from sebi_rag.embeddings import BGEM3Embedder
from sebi_rag.eval_harness import load_golden
from sebi_rag.expand import expand_query
from sebi_rag.rerank import CrossEncoderReranker
from sebi_rag.retrieve import HybridRetriever
from sebi_rag.settings import Settings

SCORE_FLOOR_IDS = [
    "v7-nt-004", "v7-bp-039", "para-parrva", "para-mfmaster", "para-freeze",
    "v7-td-005", "v7-nt-016", "v7-ls-013", "v7-rb-009", "v7-ls-031",
    "v7-bp-024", "v7-td-009", "v7-bp-034", "v7-bp-013", "hn-takeover",
    "v7-bp-015", "para-glitch", "para-mfborrow", "para-pricedata",
]

GATE = 0.42  # subject_sim floor (generate.py), per spec §3 arm table


def main() -> None:
    s = Settings.load()
    print(f"loading index from {s.index_dir} ...", file=sys.stderr)
    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(s.index_dir, emb)
    reranker = CrossEncoderReranker(device="mps")
    golden = load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")
    rows = {r["id"]: r for r in golden}

    index_docs = {c.doc_id for c in retr.chunks}
    print(f"index: {len(retr.chunks)} chunks, {len(index_docs)} docs", file=sys.stderr)

    out = []
    for rid in SCORE_FLOOR_IDS:
        r = rows[rid]
        q = r["query"]
        docs = set(r.get("relevant_circulars") or [])

        fused = retr.retrieve(q, top_n=50)
        f_rank = next((i + 1 for i, (c, _) in enumerate(fused) if c.doc_id in docs), None)
        dense = retr.dense.search(q, 50)
        d_rank = next((i + 1 for i, (idx, _) in enumerate(dense) if retr.chunks[idx].doc_id in docs), None)
        sparse = retr.sparse.search(expand_query(q), 50)
        s_rank = next((i + 1 for i, (idx, _) in enumerate(sparse) if retr.chunks[idx].doc_id in docs), None)
        dense200 = retr.dense.search(q, 200)
        d200_rank = next((i + 1 for i, (idx, _) in enumerate(dense200) if retr.chunks[idx].doc_id in docs), None)

        reranked = reranker.rerank(q, [c for c, _ in fused])
        ce_top = reranked[0][1] if reranked else None
        ce_rel = max((sc for c, sc in reranked if c.doc_id in docs), default=None)

        in_index = bool(docs & index_docs)
        if f_rank is not None:
            cls = "NOW_PASSES" if (ce_top is not None and ce_top >= GATE) else "CE_MISMATCH"
        elif d200_rank is not None:
            cls = "RECALL_DEEP"
        elif in_index:
            cls = "RECALL_ABSENT"
        else:
            cls = "DOC_MISSING"

        out.append({
            "id": rid,
            "query": q[:80],
            "relevant": sorted(docs),
            "in_index": in_index,
            "fusion_rank_50": f_rank,
            "dense_rank_50": d_rank,
            "sparse_rank_50": s_rank,
            "dense_rank_200": d200_rank,
            "ce_top": round(ce_top, 4) if ce_top is not None else None,
            "ce_relevant_best": round(ce_rel, 4) if ce_rel is not None else None,
            "class": cls,
        })

    report = {
        "gate": GATE,
        "index_dir": str(s.index_dir),
        "n_chunks": len(retr.chunks),
        "rows": out,
    }
    dest = ROOT / "reports" / "score-floor-diagnostic-2026-08-18.json"
    dest.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
