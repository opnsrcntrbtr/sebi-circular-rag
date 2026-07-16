"""Pool-width sweep (intervention #3): answer-level rescue rate vs reranker
latency at retriever pool 50/100/150 (throwaway research script).

The TREC runfiles record fused (pre-rerank) order, so this script reranks
inline and classifies at the answer level on the RERANKED ordering — the
question is whether widening the pool lets the cross-encoder rescue answer
chunks into the top-10.

Run:  HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
      PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/analysis/sweep_pool.py
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
for k, v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(k, v)

from extract_misses import classify_answer, classify_query  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402


def _load_items(path: Path) -> list[dict]:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    return [r for r in rows if not r.get("abstain")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pools", default="50,100,150")
    ap.add_argument("--out", default=str(ROOT / "eval" / "runs" / "pool-sweep"))
    args = ap.parse_args()
    pools = [int(p) for p in args.pools.split(",")]

    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(ROOT / "data" / "index", emb)
    rer = CrossEncoderReranker(device="mps")
    items = _load_items(ROOT / "eval" / "golden" / "golden_v6.jsonl")
    items += _load_items(ROOT / "eval" / "probes" / "probes_v1.jsonl")
    print(f"items={len(items)} pools={pools}", flush=True)

    report: dict[str, dict] = {}
    for pool in pools:
        lats: list[float] = []
        counts = {"hit": 0, "ranked_low": 0, "candidate_miss": 0}
        failures: list[dict] = []
        for item in items:
            t0 = time.time()
            cands = retr.retrieve(item["query"], top_n=pool)
            reranked = rer.rerank(item["query"], [c for c, _ in cands])
            lats.append(time.time() - t0)
            ids = [c.id for c, _ in reranked]
            texts = {c.id: c.text for c, _ in reranked}
            must = item.get("must_contain", [])
            if must:
                cls, rank = classify_answer(ids, texts, must)
            else:
                cls, rank = classify_query(ids, item["relevant_circulars"])
            counts[cls] += 1
            if cls != "hit":
                failures.append({"id": item["id"], "class": cls, "rank": rank})
        p95 = (statistics.quantiles(lats, n=20)[18] if len(lats) >= 20
               else max(lats))
        report[str(pool)] = {
            "answer_level": counts,
            "failures": failures,
            "latency_mean_s": round(statistics.mean(lats), 3),
            "latency_p95_s": round(p95, 3),
        }
        print(f"pool={pool} {counts} mean={report[str(pool)]['latency_mean_s']}s "
              f"p95={report[str(pool)]['latency_p95_s']}s", flush=True)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "sweep.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out / "sweep.json")}, indent=2))


if __name__ == "__main__":
    main()
