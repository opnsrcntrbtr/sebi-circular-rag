"""P0 prep: price a larger MLX generator before committing to the R0 upgrade.

Answers the two empirical questions gating R0
(docs/research-roadmap-2026-08-19.md R0, "Costs to measure before committing"):

  1. Does bug B3 (dual-model-on-MPS segfault) fire when an N-billion-parameter
     MLX generator is co-resident with bge-m3 and bge-reranker-v2-m3 on MPS
     in 48 GB? Process completion IS the check — B3 manifests as a segfault.
  2. What is warm query latency against `timeout_s` (30 s), and what does that
     imply for a full 260-row gate re-derivation?

Measures the production path via build_default_pipeline(), overriding only the
generator model. Reports nothing about answer quality — that is R0's own
preregistered experiment, not this.

Usage: PYTHONPATH=src SEBI_RAG_MLX_MODEL=<model> python scripts/analysis/generator_cost_probe.py
"""
from __future__ import annotations

import json
import os
import resource
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

for _k, _v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(_k, _v)

N_ROWS = 20
WARMUP = 2
POOL, TOP_K = 50, 10


def rss_gb() -> float:
    # macOS reports ru_maxrss in bytes
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 3)


def main() -> None:
    from sebi_rag.api import build_default_pipeline
    from sebi_rag.eval_harness import load_golden
    from sebi_rag.settings import Settings

    s = Settings.load()
    model = os.environ.get("SEBI_RAG_MLX_MODEL", s.mlx_model)
    print(f"model={model} timeout_s={s.timeout_s}", file=sys.stderr)

    t0 = time.time()
    pipe = build_default_pipeline()
    load_s = time.time() - t0
    print(f"pipeline loaded in {load_s:.1f}s  rss={rss_gb():.2f} GB", file=sys.stderr)

    rows = [r for r in load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")
            if not r.get("abstain") and not r.get("as_of")][:N_ROWS + WARMUP]

    recs = []
    for n, item in enumerate(rows):
        q = item["query"]
        t = time.time()
        cand = pipe.retriever.retrieve(q, top_n=POOL)
        t_ret = time.time() - t
        t = time.time()
        pipe.reranker.rerank(q, [c for c, _ in cand])
        t_rer = time.time() - t
        t = time.time()
        ans, _ = pipe.query(q, pool=POOL, top_k=TOP_K)
        t_q = time.time() - t
        if n < WARMUP:
            print(f"  warmup {n+1}: {t_q:.2f}s", file=sys.stderr)
            continue
        recs.append({"id": item["id"], "retrieve_s": t_ret, "rerank_s": t_rer,
                     "query_s": t_q, "gen_s": max(t_q - t_ret - t_rer, 0.0),
                     "abstained": bool(ans.abstained), "chars": len(ans.text)})
        print(f"  {len(recs):2d}/{N_ROWS}  query={t_q:6.2f}s  gen~{recs[-1]['gen_s']:6.2f}s",
              file=sys.stderr)

    q = sorted(r["query_s"] for r in recs)
    pct = lambda p: q[min(int(len(q) * p), len(q) - 1)]  # noqa: E731
    gen = [r["gen_s"] for r in recs]

    out = {
        "model": model,
        "n": len(recs),
        "pipeline_load_s": round(load_s, 1),
        "peak_rss_gb": round(rss_gb(), 2),
        "b3_segfault": False,          # reaching this line IS the answer
        "query_s": {"p50": round(statistics.median(q), 2),
                    "p95": round(pct(0.95), 2),
                    "mean": round(statistics.mean(q), 2),
                    "max": round(max(q), 2)},
        "gen_s": {"p50": round(statistics.median(gen), 2),
                  "mean": round(statistics.mean(gen), 2)},
        "retrieve_s_mean": round(statistics.mean(r["retrieve_s"] for r in recs), 3),
        "rerank_s_mean": round(statistics.mean(r["rerank_s"] for r in recs), 3),
        "timeout_s": s.timeout_s,
        "over_timeout": sum(1 for x in q if x > s.timeout_s),
        "implied_gate_260_min": round(statistics.mean(q) * 260 / 60, 1),
        "rows": recs,
    }
    dest = ROOT / "reports" / f"generator-cost-{model.split('/')[-1]}.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("model", "n", "pipeline_load_s", "peak_rss_gb", "b3_segfault",
                       "query_s", "gen_s", "retrieve_s_mean", "rerank_s_mean",
                       "timeout_s", "over_timeout", "implied_gate_260_min")}, indent=2))


if __name__ == "__main__":
    main()
