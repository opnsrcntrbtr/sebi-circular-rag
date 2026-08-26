"""Sweep RRF k_const values on a golden set. No index rebuild needed.

Turn 1 of docs/superpowers/specs/2026-08-26-retrieval-param-sweep-prereg.md.
Writes per-query recall/ndcg vectors (doc-level PRIMARY, chunk-level diagnostic)
to --out/results.json, plus a paired_delta (stats.py) of each candidate k_const
against --baseline-k, so adoption follows the prereg's fixed decision rule
(>=1pp on recall_at_10 or ndcg_at_10 AND PairedResult.significant) rather than
raw deltas.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.retrieve import HybridRetriever, rrf_fuse  # noqa: E402
from sebi_rag.benchmark import resolve_chunk_spans  # noqa: E402
from sebi_rag.eval_harness import _unique  # noqa: E402
from sebi_rag.stats import paired_delta  # noqa: E402
# Shared with pool_depth_sweep.py / expansion_sweep.py / reranker_interaction_check.py
# — was duplicated inline here before, now single-sourced from _metrics.py.
from _metrics import recall_at_k, ndcg_at_k, mrr, mean_or_none  # noqa: E402,F401


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    # golden_v6 (not v7) is intentional: prereg §1 Turn 1 runs on golden_v6, n=56.
    ap.add_argument("--golden", default=str(ROOT / "eval" / "golden" / "golden_v6.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "eval" / "runs" / "iteration_1_rrf_tuning"))
    ap.add_argument("--index-dir", default=str(ROOT / "data" / "index"))
    ap.add_argument("--k-values", default="40,50,60,70,80",
                     help="comma-separated k_const candidates (baseline is added automatically)")
    ap.add_argument("--baseline-k", type=int, default=60)
    ap.add_argument("--full-grid", action="store_true",
                     help="also sweep 20-100 step 5 (superset) instead of just --k-values")
    return ap.parse_args()


def run_one_k(golden, retriever, k_const: int, expand_sparse: bool = True):
    """Retrieve+refuse at a single k_const. Returns per-query score dicts."""
    chunk_recall, chunk_ndcg, doc_recall, doc_ndcg = {}, {}, {}, {}
    t0 = time.perf_counter()
    for item in golden:
        if item.get("abstain"):
            continue
        qid = item["id"]
        query = item["query"]
        relevant_docs = set(item.get("relevant_circulars", []))
        if not relevant_docs:
            continue  # answerable-but-unjudged: excluded, matches per_query_recall convention

        dense = retriever.dense.search(query, 50)
        sparse_query = retriever.expand_query_fn(query) if (
            expand_sparse and hasattr(retriever, "expand_query_fn")
        ) else query
        sparse = retriever.sparse.search(sparse_query, 50)
        ranked = rrf_fuse([dense, sparse], k_const=k_const, top_n=50)

        ranked_chunk_ids = [retriever.chunks[i].id for i, _ in ranked]
        # Dedupe to distinct circulars BEFORE slicing top-10, matching
        # benchmark.py:run_retrieval_benchmark / per_query_recall's convention
        # (_unique(_doc(...))) — without this, multiple chunks from the same
        # circular double-count in DCG and push doc_ndcg above 1.0.
        ranked_doc_ids = _unique(retriever.chunks[i].doc_id for i, _ in ranked)

        doc_recall[qid] = recall_at_k(ranked_doc_ids, relevant_docs, 10)
        doc_ndcg[qid] = ndcg_at_k(ranked_doc_ids, relevant_docs, 10)

        gold_chunks = set(resolve_chunk_spans(item, retriever.chunks))
        if gold_chunks:
            top = ranked_chunk_ids[:10]
            chunk_recall[qid] = len(set(top) & gold_chunks) / len(gold_chunks)
            chunk_ndcg[qid] = ndcg_at_k(ranked_chunk_ids, gold_chunks, 10)
    elapsed = time.perf_counter() - t0
    return {
        "doc_recall": doc_recall, "doc_ndcg": doc_ndcg,
        "chunk_recall": chunk_recall, "chunk_ndcg": chunk_ndcg,
        "elapsed_s": elapsed,
    }


def main() -> None:
    args = parse_args()
    golden_path = Path(args.golden)
    with golden_path.open() as f:
        golden = [json.loads(line) for line in f]

    candidates = sorted({int(x) for x in args.k_values.split(",")} | {args.baseline_k})
    if args.full_grid:
        candidates = sorted(set(candidates) | set(range(20, 101, 5)))

    embedder = BGEM3Embedder()
    retriever = HybridRetriever.load(Path(args.index_dir), embedder)
    print(f"Loaded: {len(retriever.chunks)} chunks, {len(golden)} golden items "
          f"({sum(1 for g in golden if not g.get('abstain'))} scorable) from {golden_path.name}",
          file=sys.stderr)

    def fmt(x: float | None) -> str:
        return f"{x:.4f}" if x is not None else "n/a"

    runs: dict[int, dict] = {}
    for k_const in candidates:
        r = run_one_k(golden, retriever, k_const)
        runs[k_const] = r
        print(f"k={k_const:3d}  doc_recall@10={fmt(mean_or_none(r['doc_recall']))}  "
              f"doc_ndcg@10={fmt(mean_or_none(r['doc_ndcg']))}  "
              f"chunk_recall@10={fmt(mean_or_none(r['chunk_recall']))}  "
              f"chunk_ndcg@10={fmt(mean_or_none(r['chunk_ndcg']))}  time={r['elapsed_s']:.1f}s",
              file=sys.stderr)

    baseline = runs[args.baseline_k]
    comparisons = {}
    for k_const in candidates:
        if k_const == args.baseline_k:
            continue
        cand = runs[k_const]
        recall_cmp = paired_delta(baseline["doc_recall"], cand["doc_recall"])
        ndcg_cmp = paired_delta(baseline["doc_ndcg"], cand["doc_ndcg"])
        adopted = (
            (abs(recall_cmp.delta) >= 0.01 and recall_cmp.significant)
            or (abs(ndcg_cmp.delta) >= 0.01 and ndcg_cmp.significant)
        )
        comparisons[k_const] = {
            "recall_at_10": {
                "delta": recall_cmp.delta, "ci_lo": recall_cmp.ci_lo, "ci_hi": recall_cmp.ci_hi,
                "p_value": recall_cmp.p_value, "significant": recall_cmp.significant,
                "n": recall_cmp.n,
            },
            "ndcg_at_10": {
                "delta": ndcg_cmp.delta, "ci_lo": ndcg_cmp.ci_lo, "ci_hi": ndcg_cmp.ci_hi,
                "p_value": ndcg_cmp.p_value, "significant": ndcg_cmp.significant,
                "n": ndcg_cmp.n,
            },
            "adopted_per_prereg_decision_rule": adopted,
        }
        flag = "ADOPT-CANDIDATE" if adopted else "null"
        print(f"k={k_const:3d} vs baseline k={args.baseline_k}: "
              f"recall_at_10 Δ={recall_cmp.delta:+.4f} p={recall_cmp.p_value:.4f} sig={recall_cmp.significant} | "
              f"ndcg_at_10 Δ={ndcg_cmp.delta:+.4f} p={ndcg_cmp.p_value:.4f} sig={ndcg_cmp.significant} | {flag}",
              file=sys.stderr)

    best_k = max(candidates, key=lambda k: mean_or_none(runs[k]["doc_recall"]) or 0.0)
    any_adopted = any(c["adopted_per_prereg_decision_rule"] for c in comparisons.values())

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "turn": 1,
        "variable": "rrf_k_const",
        "golden_file": str(golden_path),
        "n_golden": len(golden),
        "n_scorable": sum(1 for g in golden if not g.get("abstain")),
        "baseline_k": args.baseline_k,
        "candidates": candidates,
        "aggregate": {
            str(k): {
                "doc_recall_at_10": mean_or_none(runs[k]["doc_recall"]),
                "doc_ndcg_at_10": mean_or_none(runs[k]["doc_ndcg"]),
                "chunk_recall_at_10": mean_or_none(runs[k]["chunk_recall"]),
                "chunk_ndcg_at_10": mean_or_none(runs[k]["chunk_ndcg"]),
                "elapsed_s": runs[k]["elapsed_s"],
            }
            for k in candidates
        },
        "per_query": {
            str(k): {
                "doc_recall": runs[k]["doc_recall"],
                "doc_ndcg": runs[k]["doc_ndcg"],
                "chunk_recall": runs[k]["chunk_recall"],
                "chunk_ndcg": runs[k]["chunk_ndcg"],
            }
            for k in candidates
        },
        "paired_vs_baseline": {str(k): v for k, v in comparisons.items()},
        "best_k_by_raw_doc_recall": best_k,
        "any_candidate_adopted_per_decision_rule": any_adopted,
        "verdict": "ADOPT" if any_adopted else "NULL - baseline k_const carries forward unchanged",
    }
    (out_dir / "results.json").write_text(json.dumps(out, indent=2))
    print(f"\nWrote {out_dir / 'results.json'}", file=sys.stderr)
    print(f"Verdict: {out['verdict']}", file=sys.stderr)


if __name__ == "__main__":
    main()
