"""HF Spaces path: corpus_spaces loader mapping + HybridGenerator fallback.

Fully offline: HF rows are stubbed via monkeypatch; no `datasets`,
`gradio_client` or `transformers` import is exercised.
"""
from __future__ import annotations

import pytest

from sebi_rag import corpus_spaces
from sebi_rag.segment import Chunk
from sebi_rag.settings import Settings, SpacesSettings

CORPUS_ROWS = [
    {
        "circular_number": "SEBI/HO/X/2024/1",
        "issue_date": "2024-03-01",
        "subject": "Old norms",
        "issuing_department": "X",
        "supersession_status": "superseded",
        "version_lineage": [],
        "text": "1. Applicability\nThis circular applies to all brokers.",
        "source_url": "https://example.org/1",
    },
    {
        "circular_number": "SEBI/HO/X/2026/2",
        "issue_date": "2026-01-15",
        "subject": "New norms",
        "issuing_department": "X",
        "supersession_status": "in_force",
        "version_lineage": [],
        "text": "1. Applicability\nThis circular supersedes SEBI/HO/X/2024/1.",
        "source_url": "https://example.org/2",
    },
]

CHUNK_ROWS = [
    {
        "chunk_id": "SEBI/HO/X/2024/1#1. Applicability#0",
        "doc_id": "SEBI/HO/X/2024/1",
        "circular_number": "SEBI/HO/X/2024/1",
        "section": "SEBI/HO/X/2024/1/1. Applicability/p0",
        "context_header": "SEBI/HO/X/2024/1 | Old norms | 1. Applicability",
        "text": "This circular applies to all brokers.",
        "subject": "Old norms",
        "issue_date": "2024-03-01",
        "supersession_status": "superseded",
        "version_lineage": [],
    },
    {
        "chunk_id": "SEBI/HO/X/2026/2#1. Applicability#0",
        "doc_id": "SEBI/HO/X/2026/2",
        "circular_number": "SEBI/HO/X/2026/2",
        "section": "SEBI/HO/X/2026/2/1. Applicability/p0",
        "context_header": "SEBI/HO/X/2026/2 | New norms | 1. Applicability",
        "text": "This circular supersedes SEBI/HO/X/2024/1.",
        "subject": "New norms",
        "issue_date": "2026-01-15",
        "supersession_status": "in_force",
        "version_lineage": [],
    },
]


@pytest.fixture()
def settings() -> Settings:
    import dataclasses
    return dataclasses.replace(
        Settings("c.jsonl", "idx"), spaces=SpacesSettings(recent_years=(2025, 2026))
    )


@pytest.fixture(autouse=True)
def _stub_rows(monkeypatch):
    monkeypatch.setattr(
        corpus_spaces, "load_hf_rows",
        lambda s, cfg: CHUNK_ROWS if cfg == "chunks" else CORPUS_ROWS,
    )


def test_chunks_config_refuses_header_and_maps_fields(settings):
    out = corpus_spaces.load_circulars_from_hf(settings, "chunks", "full")
    assert [type(c) for c in out] == [Chunk, Chunk]
    c = out[0]
    assert c.id == "SEBI/HO/X/2024/1#1. Applicability#0"
    assert c.doc_id == "SEBI/HO/X/2024/1"
    assert c.text.startswith("SEBI/HO/X/2024/1 | Old norms | 1. Applicability\n")
    assert c.text.endswith("applies to all brokers.")
    assert c.meta["subject"] == "Old norms"          # SubjectSimJudge depends on this
    assert c.meta["supersession_status"] == "superseded"


def test_corpus_config_rechunks_like_local_ingestion(settings):
    out = corpus_spaces.load_circulars_from_hf(settings, "corpus", "full")
    docs = {c.doc_id for c in out}
    assert docs == {"SEBI/HO/X/2024/1", "SEBI/HO/X/2026/2"}
    # hierarchical_chunk enrichment: header line prepended
    assert any(c.text.startswith("SEBI/HO/X/2024/1 | Old norms") for c in out)


def test_recent_subset_filters_by_issue_year(settings):
    for cfg in ("chunks", "corpus"):
        out = corpus_spaces.load_circulars_from_hf(settings, cfg, "recent")
        assert {c.doc_id for c in out} == {"SEBI/HO/X/2026/2"}
    recs = corpus_spaces.load_corpus_records_from_hf(settings, "recent")
    assert [r["circular_number"] for r in recs] == ["SEBI/HO/X/2026/2"]


def test_corpus_records_feed_build_lineage(settings):
    from sebi_rag.lineage import build_lineage

    recs = corpus_spaces.load_corpus_records_from_hf(settings, "full")
    lin = build_lineage(recs)
    assert lin.status("SEBI/HO/X/2024/1") == "superseded"
    assert lin.superseded_by["SEBI/HO/X/2024/1"] == ["SEBI/HO/X/2026/2"]


def test_invalid_arguments_raise(settings):
    with pytest.raises(ValueError):
        corpus_spaces.load_circulars_from_hf(settings, "bogus", "full")
    with pytest.raises(ValueError):
        corpus_spaces.load_circulars_from_hf(settings, "chunks", "bogus")


# --- HybridGenerator fallback behavior (no models, no network) --------------

_CTX = [Chunk(id="A/1#s#0", doc_id="A/1", section="A/1/s/p0", text="body")]


class _Boom:
    calls = 0

    def generate(self, query, contexts):
        _Boom.calls += 1
        raise TimeoutError("external space stalled")


class _Canned:
    def generate(self, query, contexts):
        return "fallback answer [A/1]"


def _hybrid(external_space: str):
    from sebi_rag.generate_spaces import HybridGenerator

    sp = SpacesSettings(external_space=external_space)
    return HybridGenerator(sp, external=_Boom(), fallback=_Canned())


def test_hybrid_falls_back_on_external_failure():
    _Boom.calls = 0
    g = _hybrid("someuser/some-llm-space")
    assert g.generate("q", _CTX) == "fallback answer [A/1]"
    assert _Boom.calls == 1  # external was tried first


def test_hybrid_skips_external_when_unconfigured():
    _Boom.calls = 0
    g = _hybrid("")
    assert g.generate("q", _CTX) == "fallback answer [A/1]"
    assert _Boom.calls == 0  # empty external_space -> straight to fallback


def test_generators_implement_generator_protocol():
    from sebi_rag.generate import Generator
    from sebi_rag.generate_spaces import (
        ExternalSpaceGenerator, HFGenerator, HybridGenerator,
    )

    sp = SpacesSettings()
    for g in (ExternalSpaceGenerator(sp), HFGenerator(sp), HybridGenerator(sp)):
        assert callable(getattr(g, "generate", None))
        # Generator is a non-runtime Protocol; signature parity is what matters:
        # generate(query: str, contexts: list[Chunk]) -> str, ABSTAIN on empty.
    assert HFGenerator(sp).generate("q", []) == "I don't know based on the available evidence."
