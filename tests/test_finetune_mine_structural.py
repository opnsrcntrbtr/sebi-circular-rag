"""Offline tests for scripts/finetune/mine_structural_pairs.py's pure
transforms. Hard-negative mining (mine_hard_negatives) needs a real
embedder/FAISS index so it is exercised via a fake retriever object here,
not the production BGEM3Embedder - matches the offline-first convention
(HashEmbedder) used across the rest of this test suite.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from finetune.mine_structural_pairs import (  # noqa: E402
    MIN_CHUNK_CHARS,
    _is_signoff_boilerplate,
    _leaks_metadata,
    _split_heading,
    _strip_context_header,
    load_minable_docs,
    mine_citation_context,
    mine_hard_negatives,
    mine_heading_section,
    mine_lineage_pairs,
    mine_subject_body,
)

LONG = "x" * MIN_CHUNK_CHARS  # pad text past the degenerate-chunk floor


# ---------------------------------------------------------------------------
# metadata leakage / heading detection
# ---------------------------------------------------------------------------

def test_leaks_metadata_catches_iso_date():
    assert _leaks_metadata("issued on 2023-07-13")


def test_leaks_metadata_catches_circular_number_formats():
    assert _leaks_metadata("see SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123")
    assert _leaks_metadata("per HO/43/15/12(3)2025-ISD-POD2/I/11734/2026")


def test_leaks_metadata_false_on_clean_text():
    assert not _leaks_metadata("nomination norms for demat accounts")


def test_split_heading_finds_numbered_clause_and_strips_it():
    text = "2. Applicability\nThis circular applies to all listed entities."
    result = _split_heading(text)
    assert result == ("2. Applicability",
                      "This circular applies to all listed entities.")


def test_split_heading_none_when_no_numbered_line():
    assert _split_heading("plain preamble text with no clause number") is None


# ---------------------------------------------------------------------------
# context-header stripping (segment.py:130's F1/ADR-001 enrichment)
# ---------------------------------------------------------------------------

def test_strip_context_header_removes_doc_id_subject_section_prefix():
    text = "SEBI/HO/CFD/2023/123 | Disclosure of material events | preamble\nActual body text starts here."
    assert _strip_context_header(text, "SEBI/HO/CFD/2023/123") == "Actual body text starts here."


def test_strip_context_header_is_noop_when_first_line_is_not_the_header():
    text = "2. Applicability\nThis circular applies to all listed entities."
    assert _strip_context_header(text, "SEBI/HO/CFD/2023/123") == text


def test_strip_context_header_is_noop_for_a_different_docs_header():
    """Guards against accidentally stripping a citation to a DIFFERENT
    circular that happens to also use the ' | ' separator."""
    text = "SEBI/HO/CFD/2023/999 | Some other subject | s1\nbody"
    assert _strip_context_header(text, "SEBI/HO/CFD/2023/123") == text


def test_mine_subject_body_positive_excludes_the_context_header():
    """The systematic defect this fix targets: a positive that still
    carries "{doc_id} | {subject} | {section}" restates the query
    (subject) right next to itself, teaching a string-match shortcut
    instead of genuine semantic retrieval."""
    corpus = [{"circular_number": "A", "subject": "Nomination norms"}]
    chunks_by_doc = {"A": [
        {"doc_id": "A", "section": "A/1",
         "text": "A | Nomination norms | A/1\n" + LONG + " real body content"},
    ]}
    rows = mine_subject_body(corpus, chunks_by_doc, minable={"A"})
    assert len(rows) == 1
    assert "Nomination norms" not in rows[0]["positive"]
    assert "A |" not in rows[0]["positive"]


def test_mine_subject_body_drops_chunk_that_is_all_header_no_body():
    """A chunk whose real body is short falls below MIN_CHUNK_CHARS only
    AFTER the header is stripped - the header bulk must not count toward
    the length floor."""
    corpus = [{"circular_number": "A", "subject": "Nomination norms"}]
    chunks_by_doc = {"A": [
        {"doc_id": "A", "section": "A/1",
         "text": "A | Nomination norms | A/1\n" + "x" * (MIN_CHUNK_CHARS - 10)},
    ]}
    assert mine_subject_body(corpus, chunks_by_doc, minable={"A"}) == []


def test_is_signoff_boilerplate_matches_common_sign_off_openers():
    assert _is_signoff_boilerplate("Yours faithfully,\nAshok Nimbekar\nGeneral Manager")
    assert _is_signoff_boilerplate("Deputy General Manager\nDepartment of Debt")
    assert _is_signoff_boilerplate("Email id: someone@sebi.gov.in")


def test_is_signoff_boilerplate_does_not_flag_substantive_text_mentioning_a_title():
    """A passage that merely MENTIONS a manager's title mid-paragraph is
    substantive text, not a signature block, and must not be rejected -
    only text that OPENS with a sign-off marker is boilerplate."""
    assert not _is_signoff_boilerplate(
        "The compliance officer shall report to the General Manager within "
        "seven days of any material event under this circular.")


def test_mine_subject_body_excludes_signoff_boilerplate_chunk():
    corpus = [{"circular_number": "A", "subject": "Nomination norms"}]
    chunks_by_doc = {"A": [
        {"doc_id": "A", "section": "A/1",
         "text": "A | Nomination norms | A/1\nYours faithfully,\n" + LONG},
    ]}
    assert mine_subject_body(corpus, chunks_by_doc, minable={"A"}) == []


def test_mine_heading_section_strips_header_before_detecting_heading():
    chunks_by_doc = {"A": [
        {"doc_id": "A", "section": "A/1",
         "text": "A | Some subject | A/1\n2. Applicability\n" + LONG + " applies"},
    ]}
    rows = mine_heading_section(chunks_by_doc, minable={"A"})
    assert len(rows) == 1
    assert rows[0]["query"] == "2. Applicability"
    assert "A | Some subject" not in rows[0]["positive"]


# ---------------------------------------------------------------------------
# holdout / minable universe
# ---------------------------------------------------------------------------

def test_load_minable_docs_excludes_holdout_slice(tmp_path):
    corpus = [{"circular_number": "A"}, {"circular_number": "B"},
              {"circular_number": "C"}]
    holdout_path = tmp_path / "holdout.json"
    import json
    holdout_path.write_text(json.dumps({"holdout_docs": ["B"]}), encoding="utf-8")
    assert load_minable_docs(corpus, holdout_path) == {"A", "C"}


# ---------------------------------------------------------------------------
# template 1: subject_body
# ---------------------------------------------------------------------------

def test_mine_subject_body_pairs_subject_with_own_chunks():
    corpus = [{"circular_number": "A", "subject": "Nomination norms"}]
    chunks_by_doc = {"A": [
        {"doc_id": "A", "section": "A/1", "text": LONG + " body one"},
        {"doc_id": "A", "section": "A/preamble", "text": LONG + " preamble text"},
    ]}
    rows = mine_subject_body(corpus, chunks_by_doc, minable={"A"}, max_per_doc=5)
    assert len(rows) == 1  # preamble chunk excluded
    assert rows[0]["query"] == "Nomination norms"
    assert rows[0]["template"] == "subject_body"
    assert rows[0]["source_doc"] == "A"


def test_mine_subject_body_skips_held_out_doc():
    corpus = [{"circular_number": "A", "subject": "Nomination norms"}]
    chunks_by_doc = {"A": [{"doc_id": "A", "section": "A/1", "text": LONG}]}
    assert mine_subject_body(corpus, chunks_by_doc, minable=set()) == []


def test_mine_subject_body_skips_metadata_leaking_subject():
    corpus = [{"circular_number": "A", "subject": "circular dated 2023-07-13"}]
    chunks_by_doc = {"A": [{"doc_id": "A", "section": "A/1", "text": LONG}]}
    assert mine_subject_body(corpus, chunks_by_doc, minable={"A"}) == []


def test_mine_subject_body_caps_volume_per_doc():
    corpus = [{"circular_number": "A", "subject": "Nomination norms"}]
    chunks_by_doc = {"A": [
        {"doc_id": "A", "section": f"A/{i}", "text": LONG + f" body {i}"}
        for i in range(10)
    ]}
    rows = mine_subject_body(corpus, chunks_by_doc, minable={"A"}, max_per_doc=3)
    assert len(rows) == 3


# ---------------------------------------------------------------------------
# template 2: heading_section
# ---------------------------------------------------------------------------

def test_mine_heading_section_pairs_heading_with_rest_of_chunk():
    chunks_by_doc = {"A": [
        {"doc_id": "A", "section": "A/1",
         "text": "2. Applicability\n" + LONG + " applies to all entities"},
    ]}
    rows = mine_heading_section(chunks_by_doc, minable={"A"})
    assert len(rows) == 1
    assert rows[0]["query"] == "2. Applicability"
    assert "2. Applicability" not in rows[0]["positive"]
    assert rows[0]["template"] == "heading_section"


def test_mine_heading_section_skips_chunks_without_a_heading():
    chunks_by_doc = {"A": [{"doc_id": "A", "section": "A/preamble", "text": LONG}]}
    assert mine_heading_section(chunks_by_doc, minable={"A"}) == []


def test_mine_heading_section_skips_held_out_doc():
    chunks_by_doc = {"A": [
        {"doc_id": "A", "section": "A/1", "text": "2. Applicability\n" + LONG}]}
    assert mine_heading_section(chunks_by_doc, minable=set()) == []


# ---------------------------------------------------------------------------
# template 3: citation_context (wraps export_datasets.build_citation_pairs)
# ---------------------------------------------------------------------------

def test_mine_citation_context_resolves_cited_doc_and_pairs_with_subject():
    # REF_RE (ingest_pdf.py) only matches real circular-number shapes -
    # "SEBI/HO/.../YYYY/N" is the _NEW pattern; a loosely-shaped fixture
    # (e.g. "SEBI/A/2023/2") silently matches nothing and the test would
    # pass for the wrong reason (an accidentally-empty result).
    corpus = [
        {"circular_number": "SEBI/HO/CFD/2023/1", "subject": "Citing circular",
         "text": "This refers to SEBI/HO/CFD/2023/2 for details."},
        {"circular_number": "SEBI/HO/CFD/2023/2", "subject": "Cited circular subject",
         "text": "unrelated body"},
    ]
    rows = mine_citation_context(
        corpus, minable={"SEBI/HO/CFD/2023/1", "SEBI/HO/CFD/2023/2"})
    assert len(rows) == 1
    assert rows[0]["positive"] == "Cited circular subject"
    assert rows[0]["source_doc"] == "SEBI/HO/CFD/2023/1"


def test_mine_citation_context_drops_pair_when_cited_doc_held_out():
    corpus = [
        {"circular_number": "SEBI/HO/CFD/2023/1", "subject": "Citing circular",
         "text": "This refers to SEBI/HO/CFD/2023/2 for details."},
        {"circular_number": "SEBI/HO/CFD/2023/2", "subject": "Cited circular subject",
         "text": "unrelated body"},
    ]
    # target held out (absent from minable) -> pair must be dropped
    rows = mine_citation_context(corpus, minable={"SEBI/HO/CFD/2023/1"})
    assert rows == []


# ---------------------------------------------------------------------------
# template 4: lineage_pair (wraps export_datasets.build_supersession_pairs)
# ---------------------------------------------------------------------------

def test_mine_lineage_pairs_keeps_supersedes_drops_unrelated():
    corpus = [
        {"circular_number": "NEW/1", "subject": "New rule", "issuing_department": "CFD"},
        {"circular_number": "OLD/1", "subject": "Old rule", "issuing_department": "CFD"},
    ]
    lineage = {"supersedes": {"NEW/1": ["OLD/1"]}, "amends": {},
              "superseded_by": {}, "amended_by": {}}
    rows = mine_lineage_pairs(corpus, lineage, minable={"NEW/1", "OLD/1"})
    assert len(rows) == 1
    assert rows[0]["query"] == "New rule"
    assert rows[0]["positive"] == "Old rule"
    assert rows[0]["template"] == "lineage_pair"


def test_mine_lineage_pairs_skips_pair_with_holdout_endpoint():
    corpus = [
        {"circular_number": "NEW/1", "subject": "New rule", "issuing_department": "CFD"},
        {"circular_number": "OLD/1", "subject": "Old rule", "issuing_department": "CFD"},
    ]
    lineage = {"supersedes": {"NEW/1": ["OLD/1"]}, "amends": {},
              "superseded_by": {}, "amended_by": {}}
    rows = mine_lineage_pairs(corpus, lineage, minable={"NEW/1"})  # OLD/1 held out
    assert rows == []


# ---------------------------------------------------------------------------
# hard-negative mining: fake retriever, deterministic FAISS-like behavior
# ---------------------------------------------------------------------------

@dataclass
class _FakeChunk:
    doc_id: str
    text: str


class _FakeDenseIndex:
    """Deterministic stand-in for faiss.IndexFlatIP.search: returns a fixed
    ranking + scores independent of the query vector, so tests can assert
    exact margin/window behavior without a real embedder."""

    def __init__(self, ranking: list[tuple[int, float]]):
        self._idx = np.array([[i for i, _ in ranking]])
        self._scores = np.array([[s for _, s in ranking]])
        self.ntotal = len(ranking)

    def search(self, q_vecs, k):
        n = q_vecs.shape[0]
        return (np.repeat(self._scores, n, axis=0)[:, :k],
               np.repeat(self._idx, n, axis=0)[:, :k])


class _FakeDense:
    def __init__(self, index):
        self.index = index


class _FakeRetriever:
    def __init__(self, chunks, ranking):
        self.chunks = chunks
        self.dense = _FakeDense(_FakeDenseIndex(ranking))


class _FakeEmbedder:
    """Deterministic unit vectors keyed by text hash - cosine of a text with
    itself is always 1.0, letting tests control positive_scores precisely
    via the ranking's own declared scores instead of real semantics."""

    def encode(self, texts):
        # Every row identical unit vector: dot products are then driven
        # entirely by the FakeDenseIndex's declared scores, not by these
        # vectors - mine_hard_negatives only uses embed() for positive_score
        # (query . positive) and for the FAISS call's query vectors.
        return np.ones((len(texts), 4), dtype="float32") / 2.0


def test_mine_hard_negatives_excludes_own_document():
    chunks = [_FakeChunk("SAME", "self text"), _FakeChunk("OTHER", "neg text")]
    ranking = [(0, 0.9), (1, 0.5)]  # rank0 = same-doc (must be excluded)
    retriever = _FakeRetriever(chunks, ranking)
    rows = [{"query": "q", "positive": "p", "template": "t", "source_doc": "SAME"}]
    # only 1 valid negative exists -> can't reach n_neg=5, row is dropped
    out = mine_hard_negatives(rows, retriever, _FakeEmbedder(),
                              k=2, rank_lo=0, rank_hi=1, n_neg=1)
    assert len(out) == 1
    assert out[0]["neg"] == ["neg text"]


def test_mine_hard_negatives_applies_margin_filter():
    """A candidate scoring above 95% of the positive's own score is a
    likely false negative and must be rejected, even if it's otherwise a
    valid, different-document candidate in the rank window."""
    chunks = [_FakeChunk("OTHER1", "too close to positive"),
              _FakeChunk("OTHER2", "safely below margin")]
    # FakeEmbedder makes positive_score = 1.0 (identical unit vectors) ->
    # threshold = 0.95. Candidate 0 scores 0.99 (above threshold, rejected);
    # candidate 1 scores 0.40 (kept).
    ranking = [(0, 0.99), (1, 0.40)]
    retriever = _FakeRetriever(chunks, ranking)
    rows = [{"query": "q", "positive": "p", "template": "t", "source_doc": "SRC"}]
    out = mine_hard_negatives(rows, retriever, _FakeEmbedder(),
                              k=2, rank_lo=0, rank_hi=1, n_neg=1)
    assert len(out) == 1
    assert out[0]["neg"] == ["safely below margin"]


def test_mine_hard_negatives_respects_rank_window():
    chunks = [_FakeChunk("A", "rank0 too close to top"),
              _FakeChunk("B", "rank1 in window"),
              _FakeChunk("C", "rank2 outside window")]
    ranking = [(0, 0.30), (1, 0.20), (2, 0.10)]
    retriever = _FakeRetriever(chunks, ranking)
    rows = [{"query": "q", "positive": "p", "template": "t", "source_doc": "SRC"}]
    # window = rank 1 only (rank_lo=1, rank_hi=1) -> only candidate B qualifies
    out = mine_hard_negatives(rows, retriever, _FakeEmbedder(),
                              k=3, rank_lo=1, rank_hi=1, n_neg=1)
    assert len(out) == 1
    assert out[0]["neg"] == ["rank1 in window"]


def test_mine_hard_negatives_drops_rows_with_too_few_negatives():
    chunks = [_FakeChunk("OTHER", "only one candidate")]
    ranking = [(0, 0.2)]
    retriever = _FakeRetriever(chunks, ranking)
    rows = [{"query": "q", "positive": "p", "template": "t", "source_doc": "SRC"}]
    out = mine_hard_negatives(rows, retriever, _FakeEmbedder(),
                              k=1, rank_lo=0, rank_hi=0, n_neg=5)
    assert out == []  # only 1 candidate exists, need 5 -> dropped, not padded


def test_mine_hard_negatives_empty_rows_returns_empty():
    assert mine_hard_negatives([], _FakeRetriever([], []), _FakeEmbedder()) == []
