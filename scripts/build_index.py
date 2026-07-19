"""Build the dense+sparse index once and persist it (run after corpus changes).

    HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
    PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src .venv/bin/python scripts/build_index.py

This is the slow step (bge-m3 encodes every chunk on MPS). Afterwards the API and
calibration reload the index in <1s instead of re-encoding.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {
    "TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(k, v)

from sebi_rag.context_headers import apply_context_headers, load_headers  # noqa: E402
from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402

CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
INDEX = ROOT / "data" / "index"

FULL = "--full" in sys.argv  # force re-encode of every document

chunks = load_circulars(CORPUS)
# iv9: merge contextual headers (no-op when the sidecar is absent)
chunks = apply_context_headers(
    chunks, load_headers(ROOT / "data" / "corpus" / "context_headers.jsonl")
)
print(f"chunks={len(chunks)}  building index...", flush=True)
t0 = time.time()
emb = BGEM3Embedder(device="mps")
if FULL:
    retriever = HybridRetriever.build(chunks, emb)
    stats = {"mode": "full (--full)", "chunks_encoded": len(chunks)}
else:
    retriever, stats = HybridRetriever.build_incremental(chunks, emb, INDEX)
print(f"built in {time.time() - t0:.0f}s  {stats}", flush=True)
retriever.save(INDEX)
build_lineage(load_records(CORPUS)).save(INDEX / "lineage.json")
print(f"saved index + lineage -> {INDEX}", flush=True)
