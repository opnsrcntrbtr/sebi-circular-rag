"""Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.

splade_pool is the canonical SPLADE representation (Formal et al.):
    w_j = max_{i in seq}  log(1 + relu(logits_{i,j}))  * mask_i
kept as a pure function so the math is unit-tested without loading a model.
SpladeEncoder.load returns an encode callable for SpladeIndex; it is thin
model plumbing and follows the untested-factory pattern of HydeExpander.load.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.sparse import csr_matrix


def splade_pool(logits: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    """(batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights."""
    activated = np.log1p(np.maximum(logits, 0.0))           # log(1 + relu(x))
    masked = activated * attention_mask[:, :, None]         # zero padding rows
    return masked.max(axis=1)                               # max over sequence


class SpladeEncoder:
    @staticmethod
    def load(
        model: str = "prithivida/Splade_PP_en_v1",
        device: str = "mps",
        batch_size: int = 32,
    ) -> Callable[[list[str]], csr_matrix]:
        import torch
        from transformers import AutoModelForMaskedLM, AutoTokenizer

        tok = AutoTokenizer.from_pretrained(model)
        mdl = AutoModelForMaskedLM.from_pretrained(model).to(device).eval()

        def encode(texts: list[str]) -> csr_matrix:
            from scipy.sparse import vstack

            rows: list[csr_matrix] = []
            for start in range(0, len(texts), batch_size):
                batch = texts[start: start + batch_size]
                enc = tok(batch, padding=True, truncation=True,
                          max_length=512, return_tensors="pt").to(device)
                with torch.no_grad():
                    logits = mdl(**enc).logits            # (b, seq, vocab)
                weights = splade_pool(
                    logits.float().cpu().numpy(),
                    enc["attention_mask"].cpu().numpy().astype("float32"),
                )
                rows.append(csr_matrix(weights))
            return (vstack(rows).tocsr() if rows
                    else csr_matrix((0, mdl.config.vocab_size)))

        return encode
