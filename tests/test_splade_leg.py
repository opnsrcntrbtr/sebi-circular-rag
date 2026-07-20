from __future__ import annotations

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from sebi_rag.retrieve import HybridRetriever
from sebi_rag.segment import Chunk
from sebi_rag.splade import SpladeIndex


class _StubDense:
    """Returns a fixed dense ranking regardless of query."""
    def __init__(self, ranking): self._r = ranking
    def search(self, query, k): return self._r[:k]


class _StubSparse:
    def __init__(self, ranking): self._r = ranking
    def search(self, query, k): return self._r[:k]


def _chunks(n):
    return [Chunk(id=f"D/{i}#0", doc_id="D", section="0", text=f"t{i}",
                  meta={}) for i in range(n)]


def _fake_encode(rows):
    def encode(texts):
        return csr_matrix(np.array([rows[t] for t in texts], dtype="float32"))
    return encode


def test_splade_leg_changes_fused_order_when_on():
    chunks = _chunks(2)
    # Base legs tie doc0 and doc1 (each is r0 in one leg, r1 in the other),
    # so off-fusion orders them by insertion (doc1 first). SPLADE then breaks
    # the tie strongly toward doc0.
    dense = _StubDense([(1, 0.9), (0, 0.8)])
    sparse = _StubSparse([(0, 5.0), (1, 4.0)])
    splade = SpladeIndex(_fake_encode({
        "t0": [1.0, 0.0], "t1": [0.0, 1.0], "q": [1.0, 0.0],
    }), vocab_size=2)
    splade.build(["t0", "t1"])
    r = HybridRetriever(chunks=chunks, dense=dense, sparse=sparse, splade=splade)

    off = [c.id for c, _ in r.retrieve("q", use_splade=False)]
    on = [c.id for c, _ in r.retrieve("q", use_splade=True)]
    # With splade on, doc0 gains a strong third-leg vote and must rank higher
    # than it does with splade off.
    assert on.index("D/0#0") < off.index("D/0#0")


def test_flag_off_is_unchanged_and_ignores_splade():
    chunks = _chunks(2)
    dense = _StubDense([(0, 0.9), (1, 0.8)])
    sparse = _StubSparse([(0, 5.0), (1, 4.0)])
    r = HybridRetriever(chunks=chunks, dense=dense, sparse=sparse, splade=None)
    out = [c.id for c, _ in r.retrieve("q", use_splade=False)]
    assert out == ["D/0#0", "D/1#0"]


def test_use_splade_without_index_raises():
    chunks = _chunks(1)
    r = HybridRetriever(chunks=chunks, dense=_StubDense([(0, 1.0)]),
                        sparse=_StubSparse([(0, 1.0)]), splade=None)
    with pytest.raises(RuntimeError, match="use_splade=True but no SPLADE index"):
        r.retrieve("q", use_splade=True)
