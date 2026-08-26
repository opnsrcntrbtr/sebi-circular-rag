"""Compare query-expansion arms (current prod / no-expand / HyDE) on a golden set.

Turn 3 of docs/superpowers/specs/2026-08-26-retrieval-param-sweep-prereg.md.

SPLADE is deliberately excluded from this run: no persisted SPLADE sidecar
exists under data/index/ (iv11's sidecar, per docs/status.md 2026-08-12, took
~3.7h to build and was not kept) and rebuilding it just for a confirmatory arm
that already has a recorded, larger-n verdict (iv11: +2.9pp nDCG@10, p=0.032,
1.36x latency, on the full corpus) is disproportionate to what a quick
golden_v6 pass would add. Recorded as a scope decision, not a null result.
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
    ap.add_argument("--out", default=str(ROOT / "eval" / "runs" / "iteration_3_query_expansion"))
    ap.add_argument("--index-dir", default=str(ROOT / "data" / "index"))
    ap.add_argument("--k-const", type=int, default=60)
    ap.add_argument("--pool-n", type=int, default=50)
    return ap.parse_args()


def run_arm(golden, retriever, *, expand_sparse: bool, hyde_text_fn=None) -> dict:
    doc_recall, doc_ndcg = {}, {}
    t0 = time.perf_counter()
    for item in golden:
        if item.get("abstain"):
            continue
        qid = item["id"]
        relevant_docs = set(item.get("relevant_circulars", []))
        if not relevant_docs:
            continue
        kw: dict[str, object] = {"expand_sparse": expand_sparse}
        if hyde_text_fn is not None:
            kw["hyde_text"] = hyde_text_fn(item["query"]) or None
        retrieved = retriever.retrieve(item["query"], **kw)
        ranked_doc_ids = _unique(c.doc_id for c, _ in retrieved)
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

    runs = {}
    print("Running baseline (current prod: expand_sparse=True, no hyde/splade)...", file=sys.stderr)
    runs["baseline_expand_true"] = run_arm(golden, retriever, expand_sparse=True)

    print("Running no-expand (expand_sparse=False, iv2 control arm)...", file=sys.stderr)
    runs["no_expand"] = run_arm(golden, retriever, expand_sparse=False)

    print("Running HyDE (loading HydeExpander.load(), local MLX model)...", file=sys.stderr)
    from sebi_rag.hyde import HydeExpander
    expander = HydeExpander.load()
    runs["hyde"] = run_arm(golden, retriever, expand_sparse=True,
                             hyde_text_fn=expander.hypothesize)

    print("SPLADE arm SKIPPED — no persisted sidecar, ~3.7h rebuild cost "
          "disproportionate; iv11's recorded verdict (+2.9pp nDCG@10, p=0.032) stands.",
          file=sys.stderr)

    for name, r in runs.items():
        print(f"{name:20s} doc_recall@10={fmt(mean_or_none(r['doc_recall']))}  "
              f"doc_ndcg@10={fmt(mean_or_none(r['doc_ndcg']))}  time={r['elapsed_s']:.1f}s",
              file=sys.stderr)

    baseline = runs["baseline_expand_true"]
    comparisons = {}
    for name in ("no_expand", "hyde"):
        cand = runs[name]
        recall_cmp = paired_delta(baseline["doc_recall"], cand["doc_recall"])
        ndcg_cmp = paired_delta(baseline["doc_ndcg"], cand["doc_ndcg"])
        adopted = (
            (abs(recall_cmp.delta) >= 0.01 and recall_cmp.significant)
            or (abs(ndcg_cmp.delta) >= 0.01 and ndcg_cmp.significant)
        )
        comparisons[name] = {
            "recall_at_10": {"delta": recall_cmp.delta, "ci_lo": recall_cmp.ci_lo,
                              "ci_hi": recall_cmp.ci_hi, "p_value": recall_cmp.p_value,
                              "significant": recall_cmp.significant, "n": recall_cmp.n},
            "ndcg_at_10": {"delta": ndcg_cmp.delta, "ci_lo": ndcg_cmp.ci_lo,
                            "ci_hi": ndcg_cmp.ci_hi, "p_value": ndcg_cmp.p_value,
                            "significant": ndcg_cmp.significant, "n": ndcg_cmp.n},
            "adopted_per_prereg_decision_rule": adopted,
        }
        flag = "ADOPT-CANDIDATE" if adopted else "null"
        print(f"{name} vs baseline: recall_at_10 Δ={recall_cmp.delta:+.4f} p={recall_cmp.p_value:.4f} "
              f"sig={recall_cmp.significant} | ndcg_at_10 Δ={ndcg_cmp.delta:+.4f} "
              f"p={ndcg_cmp.p_value:.4f} sig={ndcg_cmp.significant} | {flag}", file=sys.stderr)

    any_adopted = any(c["adopted_per_prereg_decision_rule"] for c in comparisons.values())

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "turn": 3,
        "variable": "query_expansion",
        "golden_file": str(golden_path),
        "n_scorable": n_scorable,
        "arms_run": list(runs.keys()),
        "splade_skipped_reason": "no persisted sidecar; ~3.7h rebuild cost; iv11 verdict already recorded",
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
        "paired_vs_baseline": comparisons,
        "any_candidate_adopted_per_decision_rule": any_adopted,
        "verdict": "ADOPT" if any_adopted else "NULL - current prod expansion (expand_sparse=True, no hyde/splade) carries forward unchanged",
    }
    (out_dir / "results.json").write_text(json.dumps(out, indent=2))
    print(f"\nWrote {out_dir / 'results.json'}", file=sys.stderr)
    print(f"Verdict: {out['verdict']}", file=sys.stderr)


if __name__ == "__main__":
    main()
