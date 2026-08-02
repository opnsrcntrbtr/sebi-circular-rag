"""Sweep RRF k_const values on the golden set. No index rebuild needed."""
import json, math, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

import numpy as np  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.lineage import Lineage  # noqa: E402
from sebi_rag.retrieve import HybridRetriever, rrf_fuse  # noqa: E402
from sebi_rag.benchmark import resolve_chunk_spans  # noqa: E402


def recall_at_k(ranked_ids, relevant, k):
    if not relevant: return 0.0
    hit = len(set(ranked_ids[:k]) & relevant)
    return hit / len(relevant)


def mrr(ranked_ids, relevant):
    for i, cid in enumerate(ranked_ids):
        if cid in relevant: return 1.0 / (i + 1)
    return 0.0


def ndcg_at_k(ranked_ids, relevant, k):
    dcg = sum(1.0 / math.log2(i + 2) for i, cid in enumerate(ranked_ids[:k]) if cid in relevant)
    ideal = sum(1.0 / math.log2(i + 2) for i in range(min(k, len(relevant))))
    return dcg / ideal if ideal else 0.0


def main():
    k_const_range = list(range(20, 101, 5))
    golden_path = ROOT / "eval" / "golden" / "golden_v7.jsonl"
    golden = [json.loads(l) for l in open(golden_path)]

    embedder = BGEM3Embedder()
    retriever = HybridRetriever.load(Path("data/index"), embedder)

    print(f"Loaded: {len(retriever.chunks)} chunks, {len(golden)} golden items", file=sys.stderr)

    results = {}
    for k_const in k_const_range:
        t0 = time.perf_counter()
        chunk_recalls, chunk_mrrs, chunk_ndcgs = [], [], []
        doc_recalls, doc_mrrs, doc_ndcgs = [], [], []

        for item in golden:
            query = item["query"]
            relevant_docs = set(item.get("relevant_circulars", []))

            # Retrieve from both legs
            dense = retriever.dense.search(query, 50)
            sparse = retriever.sparse.search(retriever.expand_query_fn(query), 50) if hasattr(retriever, 'expand_query_fn') else retriever.sparse.search(query, 50)

            # Re-fuse with different k_const
            ranked = rrf_fuse([dense, sparse], k_const=k_const, top_n=50)

            # Map chunk indices to doc_ids
            ranked_chunk_ids = [retriever.chunks[i].chunk_id for i, _ in ranked]
            ranked_doc_ids = [retriever.chunks[i].doc_id for i, _ in ranked]

            # Document-level recall
            doc_recalls.append(recall_at_k(ranked_doc_ids, relevant_docs, 10))
            doc_mrrs.append(mrr(ranked_doc_ids, relevant_docs))
            doc_ndcgs.append(ndcg_at_k(ranked_doc_ids, relevant_docs, 10))

            # Chunk-level recall (using resolve_chunk_spans like eval_harness)
            gold_chunks = set(resolve_chunk_spans(item, retriever.chunks))
            if gold_chunks:
                top = ranked_chunk_ids[:10]
                chunk_recalls.append(len(set(top) & gold_chunks) / len(gold_chunks))
                chunk_mrrs.append(next((1.0 / r for r, cid in enumerate(ranked_chunk_ids, 1) if cid in gold_chunks), 0.0))
                chunk_ndcgs.append(ndcg_at_k(ranked_chunk_ids, gold_chunks, 10))

        elapsed = time.perf_counter() - t0
        avg_cr = np.mean(chunk_recalls) if chunk_recalls else 0.0
        avg_cm = np.mean(chunk_mrrs) if chunk_mrrs else 0.0
        avg_cn = np.mean(chunk_ndcgs) if chunk_ndcgs else 0.0
        avg_dr = np.mean(doc_recalls) if doc_recalls else 0.0
        avg_dm = np.mean(doc_mrrs) if doc_mrrs else 0.0
        avg_dn = np.mean(doc_ndcgs) if doc_ndcgs else 0.0
        results[k_const] = (avg_cr, avg_cm, avg_cn, avg_dr, avg_dm, avg_dn, elapsed)
        print(f"k={k_const:3d}  chunk_r@10={avg_cr:.4f}  chunk_mrr={avg_cm:.4f}  chunk_ndcg@10={avg_cn:.4f}  doc_r@10={avg_dr:.4f}  doc_mrr={avg_dm:.4f}  time={elapsed:.1f}s")

    # Find best by chunk recall
    best_k = max(results, key=lambda k: results[k][0])
    br, bm, bn, dr, dm, dn, bt = results[best_k]
    baseline_cr = 0.7160
    print(f"\nBest k_const={best_k}: chunk_recall@10={br:.4f} (+{br-baseline_cr:+.4f}), chunk_mrr={bm:.4f}, chunk_ndcg@10={bn:.4f}", file=sys.stderr)

if __name__ == "__main__":
    main()
