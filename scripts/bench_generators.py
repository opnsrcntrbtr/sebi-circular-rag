"""Benchmark MLX generators on the golden set: faithfulness, groundedness,
abstention, citation precision, latency. Reuses the persisted index + reranker;
only the generator changes. Larger models download on first load.

    HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
    PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src .venv/bin/python scripts/bench_generators.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.eval_harness import load_golden, run_eval  # noqa: E402
from sebi_rag.generate import MLXGenerator  # noqa: E402
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402
from sebi_rag.pipeline import RAGPipeline  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402

retr = HybridRetriever.load(ROOT / "data" / "index", BGEM3Embedder(device="mps"))
rer = CrossEncoderReranker(device="mps")
lin = build_lineage(load_records(ROOT / "data" / "corpus" / "circulars.jsonl"))
golden = load_golden(ROOT / "eval" / "golden" / "golden_v3.jsonl")
print(f"index chunks={len(retr.chunks)} golden={len(golden)}", flush=True)

MODELS = [
    "mlx-community/Qwen2.5-0.5B-Instruct-4bit",
    "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "mlx-community/Qwen2.5-3B-Instruct-4bit",
]

print("\nmodel                         faith  ground  abst  cprec  lat_s  load_s", flush=True)
for m in MODELS:
    try:
        t0 = time.time()
        gen = MLXGenerator(m)
        load_s = time.time() - t0
        pipe = RAGPipeline(retriever=retr, reranker=rer, generator=gen, lineage=lin)
        r = run_eval(pipe, golden, k=10)
        print(f"{m.split('/')[-1]:28}  {r.faithfulness:.2f}   {r.groundedness_proxy:.2f}   "
              f"{r.abstention_accuracy:.2f}  {r.citation_precision:.2f}  "
              f"{r.avg_latency_s:.2f}  {load_s:.0f}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"{m}: ERROR {e}", flush=True)
print("BENCH_DONE", flush=True)
