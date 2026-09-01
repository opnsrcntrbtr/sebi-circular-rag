"""Build the dense+sparse index once and persist it (run after corpus changes).

    HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
    PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src .venv/bin/python scripts/build_index.py

This is the slow step (bge-m3 encodes every chunk on MPS). Afterwards the API and
calibration reload the index in <1s instead of re-encoding.
"""
from __future__ import annotations

import argparse
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

from sebi_rag.api import _embed_kwargs  # noqa: E402
from sebi_rag.context_headers import apply_context_headers, load_headers  # noqa: E402
from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.settings import Settings  # noqa: E402

CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
INDEX = ROOT / "data" / "index"

ap = argparse.ArgumentParser()
ap.add_argument("--full", action="store_true", help="force re-encode of every document")
ap.add_argument("--context-headers",
                default=str(ROOT / "data" / "corpus" / "context_headers.jsonl"),
                help="path to context headers sidecar")
# Build an experiment arm beside the production index instead of over it.
# The iv9/iv10 header arms are throwaway indexes; overwriting data/index in
# place would leave the production stack in the treatment state on any
# mid-build failure, recoverable only by another full re-encode.
ap.add_argument("--out", default=None,
                help="index output directory (default: data/index)")
args, _ = ap.parse_known_args()

OUT = Path(args.out) if args.out else INDEX

chunks = load_circulars(CORPUS)
# iv9: merge contextual headers (no-op when the sidecar is absent)
chunks = apply_context_headers(
    chunks, load_headers(args.context_headers)
)
print(f"chunks={len(chunks)}  building index...", flush=True)
t0 = time.time()
emb = BGEM3Embedder(**_embed_kwargs(Settings.load()))
if args.full:
    retriever = HybridRetriever.build(chunks, emb)
    stats = {"mode": "full (--full)", "chunks_encoded": len(chunks)}
else:
    retriever, stats = HybridRetriever.build_incremental(chunks, emb, INDEX)
print(f"built in {time.time() - t0:.0f}s  {stats}", flush=True)
OUT.mkdir(parents=True, exist_ok=True)
retriever.save(OUT)
build_lineage(load_records(CORPUS)).save(OUT / "lineage.json")
print(f"saved index + lineage -> {OUT}", flush=True)
