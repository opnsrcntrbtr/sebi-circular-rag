#!/usr/bin/env bash
set -euo pipefail

# -- Autoresearch benchmark harness for SEBI RAG --------------------------
# Builds a HashEmbedder index (deterministic, no model/network), then runs
# retrieval benchmark on golden_v7.jsonl. Emits METRIC lines for recall@10,
# MRR, nDCG@10 at circular (doc) level.
#
# Deterministic: fixed corpus, fixed golden set, no network, no model weights.

cd "$(dirname "$0")"
export PYTHONPATH="src:${PYTHONPATH:-}"
export TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1

exec python -u - <<'PYEOF'
"""Deterministic retrieval benchmark for autoresearch."""
import json, time, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.embeddings import HashEmbedder
from sebi_rag.retrieve import HybridRetriever
from sebi_rag.corpus import load_circulars
from sebi_rag.eval import recall_at_k, mrr as calc_mrr, ndcg_at_k
from sebi_rag.segment import Chunk

# -- Paths ---------------------------------------------------------------
CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
INDEX = ROOT / "data" / "index_ar"  # autoresearch index (isolated)
GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"

# -- Build index with HashEmbedder (deterministic, no model) -------------
print("Building HashEmbedder index ...", flush=True)
t0 = time.time()

chunks = load_circulars(CORPUS)
print(f" chunks={len(chunks)}", flush=True)

emb = HashEmbedder(dim=256)
retriever = HybridRetriever.build(chunks, emb)
retriever.save(INDEX)
print(f" built in {time.time()-t0:.1f}s", flush=True)

# -- Load golden set -----------------------------------------------------
print("Loading golden set ...", flush=True)
golden = []
with GOLDEN.open() as f:
    for line in f:
        item = json.loads(line)
        if not item.get("abstain", False):
            golden.append(item)
print(f" active queries={len(golden)}", flush=True)

# -- Benchmark: retrieve + evaluate --------------------------------------
print(f"\n{'id':<12} {'recall@10':>9} {'mrr':>7} {'ndcg@10':>8}", flush=True)

k = 10
recall_scores, mrr_scores, ndcg_scores = [], [], []

for item in golden:
    qid = item["id"]
    query = item["query"]
    relevant_circulars = set(item.get("relevant_circulars", []))

    # Retrieve top-k chunks
    results = retriever.retrieve(query, k_dense=50, k_sparse=50, top_n=k)
    # Extract doc (circular) IDs from ranked chunks
    ranked_docs = [c.id.split("#", 1)[0] for c, _ in results[:k]]

    # Circular-level recall: any chunk from a relevant circular counts
    circ_recall = recall_at_k(ranked_docs, relevant_circulars, k)

    # MRR at circular level
    circ_mrr = calc_mrr(ranked_docs, relevant_circulars)

    # nDCG@10 at circular level
    circ_ndcg = ndcg_at_k(ranked_docs, relevant_circulars, k)

    recall_scores.append(circ_recall)
    mrr_scores.append(circ_mrr)
    ndcg_scores.append(circ_ndcg)

    print(f"{qid:<12} {circ_recall:>9.4f} {circ_mrr:>7.4f} {circ_ndcg:>8.4f}", flush=True)

# -- Aggregate metrics ---------------------------------------------------
avg_recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0.0
avg_mrr = sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0.0
avg_ndcg = sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0

print(f"\n{'='*40}", flush=True)
print(f"AVG recall@10={avg_recall:.4f}", flush=True)
print(f"AVG mrr={avg_mrr:.4f}", flush=True)
print(f"AVG ndcg@10={avg_ndcg:.4f}", flush=True)
print(f"n_queries={len(golden)}", flush=True)

# Emit METRIC lines for autoresearch
print(f"METRIC recall@10={avg_recall:.4f}", flush=True)
print(f"METRIC mrr={avg_mrr:.4f}", flush=True)
print(f"METRIC ndcg@10={avg_ndcg:.4f}", flush=True)
print(f"METRIC n_queries={len(golden)}", flush=True)

PYEOF
