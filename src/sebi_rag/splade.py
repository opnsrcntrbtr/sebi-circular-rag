"""SPLADE learned-sparse retrieval leg (iv11).

Non-destructive, opt-in third RRF leg. A dependency-injected encoder maps
texts to sparse term-weight vectors (scipy CSR over the model vocabulary);
search is a sparse dot-product returning the same (idx, score) tuple shape
that rrf_fuse already consumes for the dense and BM25 legs. The encoder is
injected so tests run offline with a fake; the real Splade_PP encoder is
built by SpladeEncoder.load() (see splade_encoder.py).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import numpy as np
from scipy.sparse import csr_matrix, load_npz, save_npz


class SpladeIndex:
    def __init__(
        self, encode: Callable[[list[str]], csr_matrix], vocab_size: int
    ) -> None:
        self._encode = encode
        self.vocab_size = vocab_size
        self.matrix: csr_matrix | None = None

    def build(self, texts: list[str]) -> None:
        self.matrix = self._encode(texts).tocsr()

    def search(self, query: str, k: int) -> list[tuple[int, float]]:
        if self.matrix is None:
            raise RuntimeError("SpladeIndex.search called before build/load")
        q = self._encode([query]).tocsr()          # (1, vocab)
        scores = np.asarray((self.matrix @ q.T).todense()).ravel()  # (n,)
        k = min(k, scores.shape[0])
        # top-k by score, descending; ties broken by ascending index
        top = np.argsort(-scores, kind="stable")[:k]
        return [(int(i), float(scores[i])) for i in top]

    def save(self, path: str | Path, model: str) -> None:
        if self.matrix is None:
            raise RuntimeError("SpladeIndex.save called before build")
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        save_npz(str(d / "splade.npz"), self.matrix)
        (d / "splade_meta.json").write_text(
            json.dumps({"n": int(self.matrix.shape[0]),
                        "vocab_size": int(self.vocab_size),
                        "model": model}),
            encoding="utf-8",
        )

    @classmethod
    def load(
        cls,
        path: str | Path,
        encode: Callable[[list[str]], csr_matrix],
        expected_n: int,
    ) -> "SpladeIndex":
        d = Path(path)
        meta = json.loads((d / "splade_meta.json").read_text(encoding="utf-8"))
        matrix = load_npz(str(d / "splade.npz")).tocsr()
        if matrix.shape[0] != expected_n:
            raise ValueError(
                f"SPLADE row count {matrix.shape[0]} != expected {expected_n}"
            )
        obj = cls(encode, vocab_size=int(meta["vocab_size"]))
        obj.matrix = matrix
        return obj
