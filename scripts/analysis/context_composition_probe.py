"""What actually makes a context window large: chunk size, or chunk count?

Read-only diagnostic for the 2026-08-20 prefill finding
(corr(context_chars, latency) = 0.641 at 7B). Before preregistering a context
bound we need to know which term of `context_chars = n_contexts x mean_chunk_chars`
carries the variance — a per-chunk cap only helps if it is the size term.

Runs retrieval -> rerank -> lineage -> doc_id dedup -> top_k, i.e. exactly the
prefix of `answer_with_abstention` (generate.py:487) that fixes `contexts`, and
stops before generation. No gated metric is produced.

Usage: PYTHONPATH=src python scripts/analysis/context_composition_probe.py
"""
from __future__ import annotations

import json
import os
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

SCREEN = ROOT / "eval" / "probes" / "screen_v1.jsonl"
COST7B = ROOT / "reports" / "generator-cost-Qwen2.5-7B-Instruct-4bit.json"
GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
POOL, TOP_K = 50, 10


def main() -> None:
    from sebi_rag.api import build_default_pipeline
    from sebi_rag.eval_harness import load_golden
    from sebi_rag.generate import _grounded_prompt

    items = {it["id"]: it for it in load_golden(GOLDEN)}
    ids = [json.loads(l)["id"] for l in SCREEN.read_text().splitlines() if l.strip()]
    lat = {}
    if COST7B.exists():
        for r in json.load(open(COST7B))["rows"]:
            lat[r["id"]] = r["query_s"]
            if r["id"] not in ids:
                ids.append(r["id"])
    print(f"{len(ids)} rows ({len(lat)} with 7B latency)", file=sys.stderr)

    pipe = build_default_pipeline()
    rows, t0 = [], time.time()
    for n, rid in enumerate(sorted(ids), 1):
        it = items[rid]
        cands = pipe.retriever.retrieve(it["query"], top_n=POOL)
        reranked = pipe._apply_lineage(
            pipe.reranker.rerank(it["query"], [c for c, _ in cands]), it.get("as_of"))
        seen: dict = {}
        for chunk, score in reranked:
            prev = seen.get(chunk.doc_id)
            if prev is None or score > prev[1]:
                seen[chunk.doc_id] = (chunk, score)
        ctx = [c for c, _ in sorted(seen.values(), key=lambda cs: -cs[1])][:TOP_K]
        lens = [len(c.text) for c in ctx]
        rows.append({
            "id": rid, "task_type": it.get("task_type"),
            "n_contexts": len(ctx), "context_chars": sum(lens),
            "prompt_chars": len(_grounded_prompt(it["query"], ctx)),
            "mean_chunk_chars": round(sum(lens) / max(len(lens), 1), 1),
            "max_chunk_chars": max(lens) if lens else 0,
            "chunk_lens": lens,
            "rerank_top": round(float(reranked[0][1]) if reranked else 0.0, 4),
            "latency_7b_s": lat.get(rid),
        })
        if n % 20 == 0:
            print(f"  {n}/{len(ids)}", file=sys.stderr)

    def corr(xs, ys):
        n = len(xs)
        if n < 3:
            return None
        mx, my = sum(xs) / n, sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = sum((x - mx) ** 2 for x in xs) ** 0.5
        dy = sum((y - my) ** 2 for y in ys) ** 0.5
        return round(num / (dx * dy), 3) if dx and dy else None

    lr = [r for r in rows if r["latency_7b_s"] is not None]
    y = [r["latency_7b_s"] for r in lr]
    out = {
        "note": "read-only diagnostic; no gated metric, no floor",
        "n": len(rows), "runtime_s": round(time.time() - t0, 1),
        "n_contexts_hist": {str(k): sum(1 for r in rows if r["n_contexts"] == k)
                            for k in range(1, TOP_K + 1)},
        "corr_vs_7b_latency": {
            "n": len(lr),
            "context_chars": corr([r["context_chars"] for r in lr], y),
            "n_contexts": corr([r["n_contexts"] for r in lr], y),
            "mean_chunk_chars": corr([r["mean_chunk_chars"] for r in lr], y),
            "max_chunk_chars": corr([r["max_chunk_chars"] for r in lr], y),
        },
        "rows": rows,
    }
    dest = ROOT / "reports" / "context-composition.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
