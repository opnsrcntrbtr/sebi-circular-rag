"""Index persistence round-trip (offline)."""
from __future__ import annotations

import json

import pytest

from sebi_rag.embeddings import HashEmbedder
from sebi_rag.retrieve import HybridRetriever
from sebi_rag.segment import CHUNKER_VERSION, CircularMeta, hierarchical_chunk


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


def test_meta_json_stamps_embed_model(tmp_path):
    """F-01/F-02 fix: save() must record which embedder produced the index."""
    idx = tmp_path / "idx"
    HybridRetriever.build(_chunks(), HashEmbedder(128)).save(idx)
    meta = json.loads((idx / "meta.json").read_text(encoding="utf-8"))
    assert meta["embed_model"] == "hash:128"


def test_meta_json_stamps_chunker_version(tmp_path):
    """F-03 fix: save() must record which segment.py version chunked the
    index, so a later chunker change (e.g. the table-row-shredding fix) is
    detectable on indices — like the HF Spaces prebuilt one — that don't get
    rebuilt automatically."""
    idx = tmp_path / "idx"
    HybridRetriever.build(_chunks(), HashEmbedder(128)).save(idx)
    meta = json.loads((idx / "meta.json").read_text(encoding="utf-8"))
    assert meta["chunker_version"] == CHUNKER_VERSION


def test_load_warns_but_still_loads_on_chunker_version_drift(tmp_path, caplog):
    """Unlike an embed_model mismatch (F-02, hard failure), stale chunking
    is drift, not embedding-space corruption — load() must still succeed,
    just warn."""
    idx = tmp_path / "idx"
    HybridRetriever.build(_chunks(), HashEmbedder(128)).save(idx)
    meta_path = idx / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["chunker_version"] = "some-old-version"
    meta_path.write_text(json.dumps(meta), encoding="utf-8")

    with caplog.at_level("WARNING"):
        r = HybridRetriever.load(idx, HashEmbedder(128))
    assert len(r.chunks) > 0
    assert "some-old-version" in caplog.text
    assert CHUNKER_VERSION in caplog.text


def test_load_refuses_mismatched_embed_model(tmp_path):
    """F-02 fix: loading an index with a different-identity embedder than the
    one it was built with must fail loudly, not silently mix embedding
    spaces — the query-time half of the corruption path finding F-01/F-02
    describe together."""
    idx = tmp_path / "idx"
    HybridRetriever.build(_chunks(), HashEmbedder(128)).save(idx)

    with pytest.raises(RuntimeError, match="hash:128.*hash:64"):
        HybridRetriever.load(idx, HashEmbedder(64))

    # same identity still loads fine
    HybridRetriever.load(idx, HashEmbedder(128))
