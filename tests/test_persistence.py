"""Index persistence round-trip (offline)."""
from __future__ import annotations

from sebi_rag.embeddings import HashEmbedder
from sebi_rag.retrieve import HybridRetriever
from sebi_rag.segment import CircularMeta, hierarchical_chunk


def _chunks():
    text = ("1. Nomination norms for demat accounts and folios.\n\n"
            "2. Price data sharing for educational purposes.\n\n"
            "3. Buyback disclosure requirements for listed entities.")
    return hierarchical_chunk(text, CircularMeta(circular_number="SEBI/HO/T/P/CIR/2024/1"))


def test_index_save_load_roundtrip(tmp_path):
    idx = tmp_path / "idx"
    r = HybridRetriever.build(_chunks(), HashEmbedder(128))
    before = [c.id for c, _ in r.retrieve("nomination demat", top_n=5)]
    assert before

    assert not HybridRetriever.index_exists(idx)
    r.save(idx)
    assert HybridRetriever.index_exists(idx)

    r2 = HybridRetriever.load(idx, HashEmbedder(128))
    after = [c.id for c, _ in r2.retrieve("nomination demat", top_n=5)]
    assert after == before
    assert len(r2.chunks) == len(r.chunks)
