"""Sweep hybrid-retrieval pool depth (k_dense=k_sparse=top_n) on a golden set.

Turn 2 of docs/superpowers/specs/2026-08-26-retrieval-param-sweep-prereg.md.

bench_retrieval.py's --top-n only truncates the post-fusion list; k_dense and
k_sparse stay hardcoded at 50 regardless. This script calls
HybridRetriever.retrieve(k_dense=n, k_sparse=n, top_n=n) directly — the
method already supports all three as plain kwargs, so no wrapper class is
needed, just the right call.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.stats import paired_delta  # noqa: E402
from _metrics import _unique, ndcg_at_k, recall_at_k, mean_or_none, fmt  # noqa: E402


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", default=str(ROOT / "eval" / "golden" / "golden_v6.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "eval" / "runs" / "iteration_2_topk"))
    ap.add_argument("--index-dir", default=str(ROOT / "data" / "index"))
    ap.add_argument("--pool-values", default="30,40,50,60,80")
    ap.add_argument("--baseline-n", type=int, default=50)
    ap.add_argument("--adopted-k-const", type=int, default=60,
                     help="RRF k_const carried from Turn 1 (60 = baseline, Turn 1 was NULL)")
    return ap.parse_args()


def run_one_n(golden, retriever, n: int) -> dict:
    doc_recall, doc_ndcg = {}, {}
    t0 = time.perf_counter()
    for item in golden:
        if item.get("abstain"):
            continue
        qid = item["id"]
        relevant_docs = set(item.get("relevant_circulars", []))
        if not relevant_docs:
            continue
        retrieved = retriever.retrieve(item["query"], k_dense=n, k_sparse=n, top_n=n)
        ranked_doc_ids = _unique(c.doc_id for c, _ in retrieved)
        doc_recall[qid] = recall_at_k(ranked_doc_ids, relevant_docs, 10)
        doc_ndcg[qid] = ndcg_at_k(ranked_doc_ids, relevant_docs, 10)
    return {"doc_recall": doc_recall, "doc_ndcg": doc_ndcg, "elapsed_s": time.perf_counter() - t0}


def main() -> None:
    args = parse_args()
    golden_path = Path(args.golden)
    with golden_path.open() as f:
        golden = [json.loads(line) for line in f]

    candidates = sorted({int(x) for x in args.pool_values.split(",")} | {args.baseline_n})

    embedder = BGEM3Embedder()
    retriever = HybridRetriever.load(Path(args.index_dir), embedder)
    n_scorable = sum(1 for g in golden if not g.get("abstain") and g.get("relevant_circulars"))
    print(f"Loaded: {len(retriever.chunks)} chunks, {len(golden)} golden items "
          f"({n_scorable} scorable) from {golden_path.name}, k_const={args.adopted_k_const}",
          file=sys.stderr)

    runs: dict[int, dict] = {}
    for n in candidates:
        r = run_one_n(golden, retriever, n)
        runs[n] = r
        print(f"n={n:3d}  doc_recall@10={fmt(mean_or_none(r['doc_recall']))}  "
              f"doc_ndcg@10={fmt(mean_or_none(r['doc_ndcg']))}  time={r['elapsed_s']:.1f}s",
              file=sys.stderr)

    baseline = runs[args.baseline_n]
    comparisons = {}
    for n in candidates:
        if n == args.baseline_n:
            continue
        cand = runs[n]
        recall_cmp = paired_delta(baseline["doc_recall"], cand["doc_recall"])
        ndcg_cmp = paired_delta(baseline["doc_ndcg"], cand["doc_ndcg"])
        adopted = (
            (abs(recall_cmp.delta) >= 0.01 and recall_cmp.significant)
            or (abs(ndcg_cmp.delta) >= 0.01 and ndcg_cmp.significant)
        )
        comparisons[n] = {
            "recall_at_10": {"delta": recall_cmp.delta, "ci_lo": recall_cmp.ci_lo,
                              "ci_hi": recall_cmp.ci_hi, "p_value": recall_cmp.p_value,
                              "significant": recall_cmp.significant, "n": recall_cmp.n},
            "ndcg_at_10": {"delta": ndcg_cmp.delta, "ci_lo": ndcg_cmp.ci_lo,
                            "ci_hi": ndcg_cmp.ci_hi, "p_value": ndcg_cmp.p_value,
                            "significant": ndcg_cmp.significant, "n": ndcg_cmp.n},
            "adopted_per_prereg_decision_rule": adopted,
        }
        flag = "ADOPT-CANDIDATE" if adopted else "null"
        print(f"n={n:3d} vs baseline n={args.baseline_n}: "
              f"recall_at_10 Δ={recall_cmp.delta:+.4f} p={recall_cmp.p_value:.4f} sig={recall_cmp.significant} | "
              f"ndcg_at_10 Δ={ndcg_cmp.delta:+.4f} p={ndcg_cmp.p_value:.4f} sig={ndcg_cmp.significant} | {flag}",
              file=sys.stderr)

    any_adopted = any(c["adopted_per_prereg_decision_rule"] for c in comparisons.values())

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "turn": 2,
        "variable": "pool_depth_k_dense_k_sparse_top_n",
        "golden_file": str(golden_path),
        "n_golden": len(golden),
        "n_scorable": n_scorable,
        "adopted_k_const_from_turn1": args.adopted_k_const,
        "baseline_n": args.baseline_n,
        "candidates": candidates,
        "aggregate": {
            str(n): {"doc_recall_at_10": mean_or_none(runs[n]["doc_recall"]),
                      "doc_ndcg_at_10": mean_or_none(runs[n]["doc_ndcg"]),
                      "elapsed_s": runs[n]["elapsed_s"]}
            for n in candidates
        },
        "per_query": {
            str(n): {"doc_recall": runs[n]["doc_recall"], "doc_ndcg": runs[n]["doc_ndcg"]}
            for n in candidates
        },
        "paired_vs_baseline": {str(n): v for n, v in comparisons.items()},
        "any_candidate_adopted_per_decision_rule": any_adopted,
        "verdict": "ADOPT" if any_adopted else "NULL - baseline pool depth (50) carries forward unchanged",
    }
    (out_dir / "results.json").write_text(json.dumps(out, indent=2))
    print(f"\nWrote {out_dir / 'results.json'}", file=sys.stderr)
    print(f"Verdict: {out['verdict']}", file=sys.stderr)


if __name__ == "__main__":
    main()
