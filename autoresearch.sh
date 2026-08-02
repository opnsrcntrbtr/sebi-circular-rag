#!/usr/bin/env bash
# autoresearch.sh — SEBI Circular RAG retrieval benchmark harness.
#
# Loads the persisted FAISS+BM25 index, runs every golden_v7 query through
# HybridRetriever, computes recall@10 / MRR / nDCG@10 + latency.
# Fully offline, deterministic (fixed seeds via env), exits 0 on success.
set -euo pipefail

cd "$(dirname "$0")"

export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
export PYTORCH_ENABLE_MPS_FALLBACK=1
export HF_HUB_DISABLE_XET=1

exec python - <<'PYEOF'
"""autoresearch harness — retrieval evaluation against golden_v7."""

import json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.embeddings import BGEM3Embedder
from sebi_rag.retrieve import HybridRetriever
from sebi_rag.eval_harness import load_golden

# ---------------------------------------------------------------------------
# Load index (once)
# ---------------------------------------------------------------------------
embedder = BGEM3Embedder()
retriever = HybridRetriever.load(str(ROOT / "data" / "index"), embedder)
print(f"[harness] loaded {len(retriever.chunks)} chunks in "
      f"{embedder.dim}d", file=sys.stderr)

# ---------------------------------------------------------------------------
# Load golden set
# ---------------------------------------------------------------------------
golden_path = ROOT / "eval" / "golden" / "golden_v7.jsonl"
golden = load_golden(golden_path)
print(f"[harness] {len(golden)} golden queries", file=sys.stderr)

# ---------------------------------------------------------------------------
# Run retrieval for each query, collect metrics
# ---------------------------------------------------------------------------
K = 10

def recall_at_k(ranked_ids, relevant, k):
    if not relevant:
        return 0.0
    hit = len(set(ranked_ids[:k]) & relevant)
    return hit / len(relevant)

def mrr(ranked_ids, relevant):
    for i, cid in enumerate(ranked_ids):
        if cid in relevant:
            return 1.0 / (i + 1)
    return 0.0

def ndcg_at_k(ranked_ids, relevant, k):
    import math
    dcg = sum(1.0 / math.log2(i + 2) for i, cid in enumerate(ranked_ids[:k]) if cid in relevant)
    ideal = sum(1.0 / math.log2(i + 2) for i in range(min(k, len(relevant))))
    return dcg / ideal if ideal else 0.0

per_query = []
total_t0 = time.time()

for item in golden:
    q = item["query"]
    relevant_cids = set(item.get("relevant_circulars", []))
    if not relevant_cids:
        continue  # skip items with no ground truth

    t0 = time.time()
    results = retriever.retrieve(q, k_dense=50, k_sparse=50, top_n=50)
    elapsed = time.time() - t0

    # Extract doc_ids from retrieved chunks (strip #chunk suffix)
    ranked_docs = [c.doc_id.split("#", 1)[0] for c, _ in results]

    r = recall_at_k(ranked_docs, relevant_cids, K)
    m = mrr(ranked_docs, relevant_cids)
    n = ndcg_at_k(ranked_docs, relevant_cids, K)

    per_query.append({"id": item["id"], "recall": r, "mrr": m, "ndcg": n, "latency_s": elapsed})

total_elapsed = time.time() - total_t0

# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------
n_queries = len(per_query)
avg_recall = sum(q["recall"] for q in per_query) / n_queries if n_queries else 0.0
avg_mrr    = sum(q["mrr"] for q in per_query) / n_queries if n_queries else 0.0
avg_ndcg   = sum(q["ndcg"] for q in per_query) / n_queries if n_queries else 0.0
avg_latency = sum(q["latency_s"] for q in per_query) / n_queries if n_queries else 0.0

# Per-difficulty breakdown
diffs = {}
for q in per_query:
    # Look up difficulty from golden again (we already loaded it)
    pass

# ---------------------------------------------------------------------------
# Output METRIC lines (autoresearch harness contract)
# ---------------------------------------------------------------------------
print(f"METRIC recall_at_10={avg_recall:.6f}")
print(f"METRIC mrr={avg_mrr:.6f}")
print(f"METRIC ndcg_at_10={avg_ndcg:.6f}")
print(f"METRIC avg_latency_s={avg_latency:.4f}")
print(f"METRIC total_time_s={total_elapsed:.2f}")
print(f"METRIC n_queries={n_queries}")

# Per-difficulty metrics (re-scan golden for difficulty labels)
diff_metrics = {}
for item, q in zip(golden, per_query):
    d = item.get("difficulty", "unknown")
    if d not in diff_metrics:
        diff_metrics[d] = {"recall": [], "mrr": [], "ndcg": [], "n": 0}
    diff_metrics[d]["recall"].append(q["recall"])
    diff_metrics[d]["mrr"].append(q["mrr"])
    diff_metrics[d]["ndcg"].append(q["ndcg"])
    diff_metrics[d]["n"] += 1

for d, vals in sorted(diff_metrics.items()):
    n = vals["n"]
    if n == 0:
        continue
    print(f"METRIC recall_at_10_{d}={sum(vals['recall'])/n:.6f}")
    print(f"METRIC mrr_{d}={sum(vals['mrr'])/n:.6f}")
    print(f"METRIC ndcg_at_10_{d}={sum(vals['ndcg'])/n:.6f}")

# Per-task_type breakdown
task_metrics = {}
for item, q in zip(golden, per_query):
    t = item.get("task_type", "unknown")
    if t not in task_metrics:
        task_metrics[t] = {"recall": [], "mrr": [], "ndcg": [], "n": 0}
    task_metrics[t]["recall"].append(q["recall"])
    task_metrics[t]["mrr"].append(q["mrr"])
    task_metrics[t]["ndcg"].append(q["ndcg"])
    task_metrics[t]["n"] += 1

for t, vals in sorted(task_metrics.items()):
    n = vals["n"]
    if n == 0:
        continue
    print(f"METRIC recall_at_10_{t}={sum(vals['recall'])/n:.6f}")
    print(f"METRIC mrr_{t}={sum(vals['mrr'])/n:.6f}")
    print(f"METRIC ndcg_at_10_{t}={sum(vals['ndcg'])/n:.6f}")

# Per-citation-level breakdown
level_metrics = {}
for item, q in zip(golden, per_query):
    l = item.get("expected_citation_level", "unknown")
    if l not in level_metrics:
        level_metrics[l] = {"recall": [], "mrr": [], "ndcg": [], "n": 0}
    level_metrics[l]["recall"].append(q["recall"])
    level_metrics[l]["mrr"].append(q["mrr"])
    level_metrics[l]["ndcg"].append(q["ndcg"])
    level_metrics[l]["n"] += 1

for l, vals in sorted(level_metrics.items()):
    n = vals["n"]
    if n == 0:
        continue
    print(f"METRIC recall_at_10_{l}={sum(vals['recall'])/n:.6f}")
    print(f"METRIC mrr_{l}={sum(vals['mrr'])/n:.6f}")
    print(f"METRIC ndcg_at_10_{l}={sum(vals['ndcg'])/n:.6f}")

# Adjudicated-only subset (gate metrics)
adj = [(item, q) for item, q in zip(golden, per_query)
       if item.get("review_status") == "adjudicated"]
if adj:
    a_recall = sum(q["recall"] for _, q in adj) / len(adj)
    a_mrr = sum(q["mrr"] for _, q in adj) / len(adj)
    a_ndcg = sum(q["ndcg"] for _, q in adj) / len(adj)
    print(f"METRIC recall_at_10_adjudicated={a_recall:.6f}")
    print(f"METRIC mrr_adjudicated={a_mrr:.6f}")
    print(f"METRIC ndcg_at_10_adjudicated={a_ndcg:.6f}")
    print(f"METRIC n_adjudicated={len(adj)}")

# Per-query detail JSON (for debugging / post-processing)
detail_path = ROOT / "eval" / "runs" / f"autoresearch_{int(time.time())}.json"
detail_path.parent.mkdir(parents=True, exist_ok=True)
with open(detail_path, "w") as f:
    json.dump(per_query, f, indent=2)

print(f"[harness] wrote per-query detail to {detail_path}", file=sys.stderr)
PYEOF
