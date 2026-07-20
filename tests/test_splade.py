from __future__ import annotations

import json

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from sebi_rag.splade import SpladeIndex

VOCAB = 6


def _fake_encode(rows: dict[str, list[float]]):
    """Return an encode fn mapping known texts to known dense weight rows."""
    def encode(texts: list[str]) -> csr_matrix:
        dense = np.array([rows[t] for t in texts], dtype="float32")
        return csr_matrix(dense)
    return encode


def test_search_ranks_by_sparse_dot_product():
    # doc0 shares terms 0,1 with the query; doc1 shares term 5 only; doc2 none.
    docs = {
        "doc0": [2.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        "doc1": [0.0, 0.0, 0.0, 0.0, 0.0, 3.0],
        "doc2": [0.0, 0.0, 4.0, 0.0, 0.0, 0.0],
    }
    query = {"q": [1.0, 1.0, 0.0, 0.0, 0.0, 1.0]}
    idx = SpladeIndex(_fake_encode({**docs, **query}), vocab_size=VOCAB)
    idx.build(["doc0", "doc1", "doc2"])
    out = idx.search("q", k=2)
    assert [i for i, _ in out] == [0, 1]           # doc0 score 3.0, doc1 score 3.0 -> tie broken by idx
    assert out[0][1] == 3.0 and out[1][1] == 3.0


def test_save_load_roundtrip_and_guard(tmp_path):
    docs = {
        "a": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "b": [0.0, 2.0, 0.0, 0.0, 0.0, 0.0],
    }
    idx = SpladeIndex(_fake_encode(docs), vocab_size=VOCAB)
    idx.build(["a", "b"])
    idx.save(tmp_path, model="fake/model")

    # meta records the true row count and vocab
    meta = json.loads((tmp_path / "splade_meta.json").read_text())
    assert meta["n"] == 2 and meta["vocab_size"] == VOCAB and meta["model"] == "fake/model"

    # load with matching expected_n succeeds and preserves scores
    reloaded = SpladeIndex.load(tmp_path, _fake_encode({**docs, "b": [0.0, 2.0, 0.0, 0.0, 0.0, 0.0]}), expected_n=2)
    assert reloaded.matrix.shape == (2, VOCAB)

    # load with wrong expected_n raises, not silently mis-fuses
    with pytest.raises(ValueError, match="row count 2 != expected 77859"):
        SpladeIndex.load(tmp_path, _fake_encode(docs), expected_n=77859)
