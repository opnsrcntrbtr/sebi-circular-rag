"""Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.

The pipeline depends only on the Embedder protocol, so unit tests run offline
with HashEmbedder while production uses BGEM3Embedder (validated, Step 10).
"""
from __future__ import annotations

import hashlib
import re
from typing import Protocol, runtime_checkable

import numpy as np

_TOK = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _TOK.findall(text.lower())


@runtime_checkable
class Embedder(Protocol):
    dim: int

    def encode(self, texts: list[str]) -> np.ndarray:  # (n, dim), L2-normalized
        ...


class HashEmbedder:
    """Deterministic hashed bag-of-words embedding. No model, no network.

    Stable across processes (hashlib, not Python hash). Good enough that text
    sharing vocabulary lands near each other in cosine space — sufficient to
    exercise dense retrieval wiring in tests.
    """

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def encode(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype="float32")
        for i, t in enumerate(texts):
            for tok in _tokens(t):
                h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
                out[i, h % self.dim] += 1.0
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return out / norms


class BGEM3Embedder:
    """Production dense embedder: BAAI/bge-m3 on Apple Silicon MPS (Step 10)."""

    def __init__(self, model_path: str = "BAAI/bge-m3", device: str = "mps",
                 use_fp16: bool = False, batch_size: int = 32) -> None:
        from FlagEmbedding import BGEM3FlagModel
        from huggingface_hub import snapshot_download

        # Pre-fetch without the 2.3 GB onnx variant we never use (Step 10).
        if "/" in model_path and not model_path.startswith(("/", ".", "~")):
            model_path = snapshot_download(
                model_path,
                ignore_patterns=["onnx/*", "imgs/*", "*.onnx", "*.onnx_data"],
            )
        self._m = BGEM3FlagModel(model_path, use_fp16=use_fp16, devices=device)
        self._batch_size = batch_size
        self.dim = 1024

    def encode(self, texts: list[str]) -> np.ndarray:
        out = self._m.encode(texts, return_dense=True,
                             batch_size=self._batch_size)["dense_vecs"]
        v = np.asarray(out, dtype="float32")
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return v / norms
