"""Reranker interaction check: does the turns-1-3 winning fusion/pool config
change which reranker (bge-reranker-v2-m3 vs jina-reranker-v3-mlx) wins?

Turn 4 of docs/superpowers/specs/2026-08-26-retrieval-param-sweep-prereg.md.
NOT a re-derivation of ADR-004 (already run 2026-08-24 on golden_v7). Turns
1-3 were all null, so the "config" here is unchanged current-prod defaults —
this is an independent replication of ADR-004's comparison on a different
(smaller, golden_v6) set, not a new config being tested.
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
from sebi_rag.rerank import CrossEncoderReranker, JinaMLXReranker  # noqa: E402
from sebi_rag.stats import paired_delta  # noqa: E402
from _metrics import _unique, ndcg_at_k, recall_at_k, mean_or_none, fmt  # noqa: E402


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", default=str(ROOT / "eval" / "golden" / "golden_v6.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "eval" / "runs" / "iteration_4_reranker"))
    ap.add_argument("--index-dir", default=str(ROOT / "data" / "index"))
    ap.add_argument("--pool-n", type=int, default=50)
    return ap.parse_args()


def run_arm(golden, retriever, reranker, pool_n: int) -> dict:
    doc_recall, doc_ndcg = {}, {}
    t0 = time.perf_counter()
    for item in golden:
        if item.get("abstain"):
            continue
        qid = item["id"]
        relevant_docs = set(item.get("relevant_circulars", []))
        if not relevant_docs:
            continue
        pool = retriever.retrieve(item["query"], top_n=pool_n)
        reranked = reranker.rerank(item["query"], [c for c, _ in pool])
        ranked_doc_ids = _unique(c.doc_id for c, _ in reranked)
        doc_recall[qid] = recall_at_k(ranked_doc_ids, relevant_docs, 10)
        doc_ndcg[qid] = ndcg_at_k(ranked_doc_ids, relevant_docs, 10)
    return {"doc_recall": doc_recall, "doc_ndcg": doc_ndcg, "elapsed_s": time.perf_counter() - t0}


def main() -> None:
    args = parse_args()
    golden_path = Path(args.golden)
    with golden_path.open() as f:
        golden = [json.loads(line) for line in f]

    embedder = BGEM3Embedder()
    retriever = HybridRetriever.load(Path(args.index_dir), embedder)
    n_scorable = sum(1 for g in golden if not g.get("abstain") and g.get("relevant_circulars"))
    print(f"Loaded: {len(retriever.chunks)} chunks, {n_scorable} scorable golden items "
          f"from {golden_path.name}", file=sys.stderr)

    print("Running bge-reranker-v2-m3 (control, current citation-scoring reranker)...",
          file=sys.stderr)
    bge = CrossEncoderReranker()
    runs = {"bge": run_arm(golden, retriever, bge, args.pool_n)}
    del bge

    print("Running jina-reranker-v3-mlx (prod pool-ordering reranker, ADR-004)...",
          file=sys.stderr)
    jina = JinaMLXReranker()
    runs["jina"] = run_arm(golden, retriever, jina, args.pool_n)

    for name, r in runs.items():
        print(f"{name:6s} doc_recall@10={fmt(mean_or_none(r['doc_recall']))}  "
              f"doc_ndcg@10={fmt(mean_or_none(r['doc_ndcg']))}  time={r['elapsed_s']:.1f}s",
              file=sys.stderr)

    recall_cmp = paired_delta(runs["bge"]["doc_recall"], runs["jina"]["doc_recall"])
    ndcg_cmp = paired_delta(runs["bge"]["doc_ndcg"], runs["jina"]["doc_ndcg"])
    jina_wins = (
        (recall_cmp.delta > 0 and abs(recall_cmp.delta) >= 0.01 and recall_cmp.significant)
        or (ndcg_cmp.delta > 0 and abs(ndcg_cmp.delta) >= 0.01 and ndcg_cmp.significant)
    )
    bge_wins = (
        (recall_cmp.delta < 0 and abs(recall_cmp.delta) >= 0.01 and recall_cmp.significant)
        or (ndcg_cmp.delta < 0 and abs(ndcg_cmp.delta) >= 0.01 and ndcg_cmp.significant)
    )
    print(f"jina vs bge: recall_at_10 Δ={recall_cmp.delta:+.4f} p={recall_cmp.p_value:.4f} "
          f"sig={recall_cmp.significant} | ndcg_at_10 Δ={ndcg_cmp.delta:+.4f} "
          f"p={ndcg_cmp.p_value:.4f} sig={ndcg_cmp.significant}", file=sys.stderr)

    if bge_wins:
        verdict = ("FLAG - bge wins significantly at this config; ADR-004's reranker choice may "
                    "need re-review (out of scope for this loop, not acted on here)")
    elif jina_wins:
        verdict = "CONFIRMED - jina still wins significantly; ADR-004 choice holds"
    else:
        verdict = "NULL - no significant difference on golden_v6; ADR-004 choice (jina) unchanged"
    print(f"Verdict: {verdict}", file=sys.stderr)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "turn": 4,
        "variable": "reranker_interaction_check",
        "note": "not a re-derivation of ADR-004; config unchanged from current prod since turns 1-3 were null",
        "golden_file": str(golden_path),
        "n_scorable": n_scorable,
        "aggregate": {
            name: {"doc_recall_at_10": mean_or_none(r["doc_recall"]),
                    "doc_ndcg_at_10": mean_or_none(r["doc_ndcg"]),
                    "elapsed_s": r["elapsed_s"]}
            for name, r in runs.items()
        },
        "per_query": {
            name: {"doc_recall": r["doc_recall"], "doc_ndcg": r["doc_ndcg"]}
            for name, r in runs.items()
        },
        "jina_vs_bge": {
            "recall_at_10": {"delta": recall_cmp.delta, "ci_lo": recall_cmp.ci_lo,
                              "ci_hi": recall_cmp.ci_hi, "p_value": recall_cmp.p_value,
                              "significant": recall_cmp.significant, "n": recall_cmp.n},
            "ndcg_at_10": {"delta": ndcg_cmp.delta, "ci_lo": ndcg_cmp.ci_lo,
                            "ci_hi": ndcg_cmp.ci_hi, "p_value": ndcg_cmp.p_value,
                            "significant": ndcg_cmp.significant, "n": ndcg_cmp.n},
        },
        "verdict": verdict,
    }
    (out_dir / "results.json").write_text(json.dumps(out, indent=2))
    print(f"\nWrote {out_dir / 'results.json'}", file=sys.stderr)


if __name__ == "__main__":
    main()
