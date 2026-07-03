"""Offline tests for F3 incremental indexing (ADR-001): only new/changed docs
are encoded; deletions drop rows; retrieval stays correct after a delta build."""
from __future__ import annotations

import numpy as np

from sebi_rag.embeddings import HashEmbedder
from sebi_rag.retrieve import HybridRetriever
from sebi_rag.segment import CircularMeta, hierarchical_chunk


class CountingEmbedder(HashEmbedder):
    def __init__(self) -> None:
        super().__init__()
        self.encoded = 0

    def encode(self, texts):
        self.encoded += len(texts)
        return super().encode(texts)


def _doc(num: str, body: str):
    return hierarchical_chunk(body, CircularMeta(circular_number=num,
                                                 subject=f"Subject {num}"))


def _corpus_v1():
    return (_doc("SEBI/A/1", "1. Nomination norms for demat accounts.\n\nDetails A.")
            + _doc("SEBI/B/2", "1. Block deal window rules.\n\nDetails B.")
            + _doc("SEBI/C/3", "1. Mutual fund borrowing limits.\n\nDetails C."))


def test_incremental_encodes_only_delta(tmp_path):
    emb = CountingEmbedder()
    chunks_v1 = _corpus_v1()
    r1 = HybridRetriever.build(chunks_v1, emb)
    r1.save(tmp_path)
    assert (tmp_path / "embeddings.npy").exists()
    assert (tmp_path / "manifest.json").exists()
    base = emb.encoded

    # v2: A unchanged, B changed, C deleted, D new
    chunks_v2 = (_doc("SEBI/A/1", "1. Nomination norms for demat accounts.\n\nDetails A.")
                 + _doc("SEBI/B/2", "1. REVISED block deal window rules.\n\nDetails B2.")
                 + _doc("SEBI/D/4", "1. New surveillance obligations.\n\nDetails D."))
    r2, stats = HybridRetriever.build_incremental(chunks_v2, emb, tmp_path)
    delta = emb.encoded - base

    assert stats["mode"] == "incremental"
    assert stats["docs_total"] == 3 and stats["docs_reused"] == 1
    n_changed = sum(1 for c in chunks_v2 if c.doc_id in ("SEBI/B/2", "SEBI/D/4"))
    assert stats["chunks_encoded"] == n_changed == delta  # A's chunks NOT re-encoded
    assert len(r2.chunks) == len(chunks_v2)
    assert r2.dense.index.ntotal == len(chunks_v2)  # C's rows dropped

    # reused rows are bit-identical to the originals
    a_old = [i for i, c in enumerate(chunks_v1) if c.doc_id == "SEBI/A/1"]
    a_new = [i for i, c in enumerate(r2.chunks) if c.doc_id == "SEBI/A/1"]
    assert np.array_equal(r1.vecs[a_old], r2.vecs[a_new])

    # retrieval still works and round-trips through save/load
    top = r2.retrieve("surveillance obligations", top_n=3)
    assert top and top[0][0].doc_id == "SEBI/D/4"
    r2.save(tmp_path)
    r3 = HybridRetriever.load(tmp_path, emb)
    assert len(r3.chunks) == len(chunks_v2)


def test_incremental_falls_back_to_full_without_cache(tmp_path):
    emb = CountingEmbedder()
    r, stats = HybridRetriever.build_incremental(_corpus_v1(), emb, tmp_path)
    assert stats["mode"] == "full"
    assert stats["chunks_encoded"] == len(r.chunks) == emb.encoded
