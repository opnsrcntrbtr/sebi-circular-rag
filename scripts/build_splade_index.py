"""Build the SPLADE learned-sparse doc matrix once and persist it (iv11).

Standalone (kept out of build_index.py so the ~3.5h SPLADE encode never
entangles with routine dense/BM25 reindex). Chunk order is identical to the
dense index because both load data/corpus/circulars.jsonl via load_circulars.

    HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false PYTORCH_ENABLE_MPS_FALLBACK=1 \
    PYTHONPATH=src .venv/bin/python scripts/build_splade_index.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "PYTORCH_ENABLE_MPS_FALLBACK": "1",
             "HF_HUB_DISABLE_XET": "1", "OMP_NUM_THREADS": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag.corpus import load_circulars
from sebi_rag.splade import SpladeIndex
from sebi_rag.splade_encoder import SpladeEncoder

MODEL = "prithivida/Splade_PP_en_v1"
CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
INDEX = ROOT / "data" / "index"


def main() -> None:
    chunks = load_circulars(CORPUS)
    texts = [c.text for c in chunks]
    print(f"chunks={len(texts)}  loading {MODEL} ...", flush=True)
    encode = SpladeEncoder.load(MODEL)
    # infer vocab from a 1-row probe (avoids hardcoding 30522)
    vocab = encode(["probe"]).shape[1]
    idx = SpladeIndex(encode, vocab_size=vocab)
    t0 = time.time()
    idx.build(texts)
    nnz = idx.matrix.nnz
    print(f"encoded in {time.time() - t0:.0f}s  shape={idx.matrix.shape}  nnz={nnz}",
          flush=True)
    idx.save(INDEX, model=MODEL)
    print(f"saved -> {INDEX}/splade.npz + splade_meta.json", flush=True)


if __name__ == "__main__":
    main()
