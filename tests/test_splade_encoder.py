from __future__ import annotations

import numpy as np

from sebi_rag.splade_encoder import splade_pool


def test_splade_pool_max_over_sequence_with_log_relu_and_mask():
    # batch=1, seq=2, vocab=3
    logits = np.array([[[0.0, 3.0, -5.0],
                        [2.0, 1.0,  0.0]]], dtype="float32")
    mask = np.array([[1, 1]], dtype="float32")
    out = splade_pool(logits, mask)
    # term0: max(log1p(relu(0)), log1p(relu(2))) = log1p(2)
    # term1: max(log1p(3), log1p(1)) = log1p(3)
    # term2: max(log1p(0), log1p(0)) = 0  (negative logits -> relu 0)
    expected = np.array([[np.log1p(2.0), np.log1p(3.0), 0.0]], dtype="float32")
    assert np.allclose(out, expected, atol=1e-6)


def test_splade_pool_masked_positions_excluded():
    logits = np.array([[[10.0, 0.0, 0.0],
                        [ 0.0, 9.0, 0.0]]], dtype="float32")
    mask = np.array([[1, 0]], dtype="float32")   # second token padding
    out = splade_pool(logits, mask)
    # only first token counts: term0 = log1p(10), others 0
    assert np.isclose(out[0, 0], np.log1p(10.0), atol=1e-6)
    assert out[0, 1] == 0.0 and out[0, 2] == 0.0
