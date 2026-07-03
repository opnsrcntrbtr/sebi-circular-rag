"""F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation
metrics. The question is not just citation quality but whether a reranker's
score SEPARATES answerable queries from near-domain hard negatives — the
bge-reranker-v2-m3 baseline cannot (clusters overlap ~0.34-0.47).

Retrieval pools are computed once (bge-m3 + BM25 + RRF, pool=50) and shared
across rerankers, so differences are attributable to the reranker alone (D6).

Run:  HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
      PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src \
      .venv/bin/python scripts/bench_rerankers.py [--models bge,qwen0.6b,qwen4b]
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag import eval as M  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.eval_harness import _doc, _unique, load_golden  # noqa: E402
from sebi_rag.lineage import build_lineage, demote_superseded, load_records  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402

INDEX = ROOT / "data" / "index"
CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
POOL = 50
TOP_K = 3

MODELS = {
    "bge": ("BAAI/bge-reranker-v2-m3 (baseline)", None),
    "qwen0.6b": ("Qwen3-Reranker-0.6B", "mlx-community/Qwen3-Reranker-0.6B-mxfp8"),
    "qwen4b": ("Qwen3-Reranker-4B", "mlx-community/Qwen3-Reranker-4B-mxfp8"),
}


def auroc(pos: list[float], neg: list[float]) -> float:
    """P(pos_score > neg_score); ties count half. pos = answerable top-scores,
    neg = should-abstain top-scores. Higher = better separation (1.0 perfect)."""
    if not pos or not neg:
        return float("nan")
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def best_threshold(pos: list[float], neg: list[float]) -> tuple[float, float]:
    """Threshold maximising abstention accuracy: answer if score >= thr.
    Returns (thr, accuracy over pos+neg)."""
    cands = sorted(set(pos + neg))
    best = (0.0, 0.0)
    for thr in cands + [max(cands) + 1e-6]:
        acc = (sum(p >= thr for p in pos) + sum(n < thr for n in neg)) / (
            len(pos) + len(neg)
        )
        if acc > best[1]:
            best = (thr, acc)
    return best


def evaluate(name: str, reranked_by_id: dict, golden: list[dict], lat: float) -> dict:
    pos, neg, rows = [], [], []
    for item in golden:
        reranked = reranked_by_id[item["id"]]
        top = reranked[0][1] if reranked else 0.0
        (neg if item.get("abstain") else pos).append(top)
    thr, abst_acc = best_threshold(pos, neg)
    cprec, crec, recs = [], [], []
    for item in golden:
        if item.get("abstain"):
            continue
        reranked = reranked_by_id[item["id"]]
        relevant = set(item["relevant_circulars"])
        top = reranked[0][1] if reranked else 0.0
        cited = [] if top < thr else _unique(_doc(c.id) for c, _ in reranked[:TOP_K])
        hit = len(set(cited) & relevant)
        cprec.append(hit / len(cited) if cited else 0.0)
        crec.append(hit / len(relevant) if relevant else 0.0)
    mean = lambda xs: sum(xs) / len(xs) if xs else 0.0
    return dict(
        model=name,
        auroc=auroc(pos, neg),
        best_thr=thr,
        abst_acc=abst_acc,
        cprec=mean(cprec),
        crec=mean(crec),
        pos_min=min(pos), pos_med=sorted(pos)[len(pos) // 2],
        neg_med=sorted(neg)[len(neg) // 2], neg_max=max(neg),
        s_per_query=lat,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="bge,qwen0.6b",
                    help=f"comma list from {list(MODELS)} (qwen4b is ~5x slower)")
    ap.add_argument("--golden", default=str(ROOT / "eval" / "golden" / "golden_v5.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "eval" / "bench_rerankers.json"))
    args = ap.parse_args()

    golden = load_golden(args.golden)
    lineage = build_lineage(load_records(CORPUS))
    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(INDEX, emb)
    print(f"golden={len(golden)}  chunks={len(retr.chunks)}  pool={POOL}", flush=True)

    pools = {}
    for item in golden:
        pools[item["id"]] = [c for c, _ in retr.retrieve(item["query"], top_n=POOL)]
    print("retrieval pools cached", flush=True)

    results = []
    for key in [k.strip() for k in args.models.split(",")]:
        label, mlx_id = MODELS[key]
        if mlx_id is None:
            from sebi_rag.rerank import CrossEncoderReranker

            rr = CrossEncoderReranker(device="mps")
        else:
            from sebi_rag.rerank import Qwen3MLXReranker

            rr = Qwen3MLXReranker(model_id=mlx_id)
        t0 = time.time()
        reranked_by_id = {}
        for i, item in enumerate(golden):
            out = rr.rerank(item["query"], pools[item["id"]])
            reranked_by_id[item["id"]] = demote_superseded(out, lineage)
            if (i + 1) % 10 == 0:
                print(f"  {label}: {i + 1}/{len(golden)}", flush=True)
        lat = (time.time() - t0) / len(golden)
        res = evaluate(label, reranked_by_id, golden, lat)
        results.append(res)
        # cluster detail: the items the baseline fails on
        print(f"\n== {label} ==", flush=True)
        print(f"AUROC={res['auroc']:.3f}  best_thr={res['best_thr']:.3f}  "
              f"abst_acc={res['abst_acc']:.2f}  cit_prec@3={res['cprec']:.2f}  "
              f"cit_rec@3={res['crec']:.2f}  {res['s_per_query']:.2f}s/q", flush=True)
        print(f"answerable top-scores: min={res['pos_min']:.3f} med={res['pos_med']:.3f} | "
              f"abstain top-scores: med={res['neg_med']:.3f} max={res['neg_max']:.3f}",
              flush=True)
        for item in golden:
            if item.get("abstain") and item["id"] != "abstain":
                top = reranked_by_id[item["id"]][0][1]
                print(f"  hn  {item['id']:<12} top={top:.3f}", flush=True)
        for pid in ("para-pricedata", "para-mfmaster", "para-mfborrow",
                    "para-freeze", "para-glitch"):
            it = next(i for i in golden if i["id"] == pid)
            top = reranked_by_id[pid][0][1]
            print(f"  para {pid:<14} top={top:.3f}", flush=True)

    Path(args.out).write_text(json.dumps(results, indent=2))
    print(f"\nsaved -> {args.out}", flush=True)


if __name__ == "__main__":
    main()
