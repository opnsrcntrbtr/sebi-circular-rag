"""Minimal end-to-end test of the SEBI RAG pipeline.

Runs fully offline (HashEmbedder + bm25s + FAISS + RRF + LexicalReranker +
extractive stub) so Step-11 repository tests are fast and deterministic. The
heavy bge-m3 / cross-encoder path is exercised separately (Step 10).
"""
from __future__ import annotations

import pytest

from sebi_rag.embeddings import HashEmbedder
from sebi_rag.eval import mrr, ndcg_at_k, recall_at_k
from sebi_rag.lineage import Lineage, build_lineage
from sebi_rag.generate import ABSTAIN, ExtractiveStubGenerator
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.rerank import LexicalReranker
from sebi_rag.retrieve import rrf_fuse
from sebi_rag.segment import CircularMeta, hierarchical_chunk

CIRCULARS = [
    (
        CircularMeta(
            circular_number="SEBI/HO/CFD/2023/001",
            issue_date="2023-01-15",
            subject="Disclosure requirements for listed entities",
            issuing_department="CFD",
        ),
        """1. Applicability

This circular applies to all listed entities under the LODR Regulations.

2. Disclosure of material events

Listed entities shall disclose material events and price sensitive information
to the stock exchanges promptly and not later than twenty four hours.""",
    ),
    (
        CircularMeta(
            circular_number="SEBI/HO/IMD/2022/045",
            issue_date="2022-08-09",
            subject="Mutual fund expense ratio",
            issuing_department="IMD",
        ),
        """1. Scope

This circular prescribes the total expense ratio limits applicable to mutual
fund schemes and the manner of charging such expenses to unit holders.""",
    ),
    (
        CircularMeta(
            circular_number="SEBI/HO/MRD/2021/099",
            issue_date="2021-03-30",
            subject="Settlement cycle for equity",
            issuing_department="MRD",
        ),
        """1. Settlement

The settlement cycle for trades in the equity segment shall move to a T plus one
rolling settlement basis in a phased manner.""",
    ),
]


def _build_chunks():
    chunks = []
    for meta, text in CIRCULARS:
        chunks.extend(hierarchical_chunk(text, meta))
    return chunks


def _build_pipeline():
    return RAGPipeline.build(
        chunks=_build_chunks(),
        embedder=HashEmbedder(dim=512),
        reranker=LexicalReranker(),
        generator=ExtractiveStubGenerator(),
        abstain_threshold=0.05,
    )


def test_segmentation_has_stable_ids_and_metadata():
    chunks = _build_chunks()
    assert len(chunks) >= 3
    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids)), "chunk ids must be unique/stable"
    sample = chunks[0]
    assert sample.meta["circular_number"] == sample.doc_id
    assert "supersession_status" in sample.meta


def test_rrf_fusion_orders_by_reciprocal_rank():
    dense = [(2, 0.9), (1, 0.8)]
    sparse = [(1, 5.0), (3, 4.0)]
    fused = rrf_fuse([dense, sparse], k_const=60, top_n=10)
    ids = [i for i, _ in fused]
    assert ids[0] == 1  # appears high in both lists -> top after fusion
    assert set(ids) == {1, 2, 3}


def test_hybrid_retrieval_finds_relevant_circular():
    pipe = _build_pipeline()
    ans, retrieved = pipe.query(
        "What are the disclosure requirements for listed entities under LODR?"
    )
    assert any(cid.startswith("SEBI/HO/CFD/2023/001") for cid in retrieved)
    assert not ans.abstained
    assert ans.citations
    assert ans.citations[0].startswith("SEBI/HO/CFD/2023/001")


def test_abstention_on_out_of_domain_query():
    pipe = _build_pipeline()
    ans, _ = pipe.query("How do I bake chocolate chip cookies at home?")
    assert ans.abstained
    assert ans.text == ABSTAIN
    assert ans.citations == []


def test_answer_flags_superseded_citation():
    A = "SEBI/HO/W/P/CIR/2021/05"
    B = "SEBI/HO/W/P/CIR/2025/40"
    a_text = f"CIRCULAR {A}. Norms for nomination in demat accounts for investors."
    b_text = (f"CIRCULAR {B}. This circular supersedes earlier norms. In "
              f"supersession of {A}, revised nomination norms for demat accounts apply.")
    chunks = hierarchical_chunk(a_text, CircularMeta(circular_number=A))
    chunks += hierarchical_chunk(b_text, CircularMeta(circular_number=B))
    lineage = build_lineage([
        {"circular_number": A, "text": a_text},
        {"circular_number": B, "text": b_text},
    ])
    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256), reranker=LexicalReranker(),
        generator=ExtractiveStubGenerator(), abstain_threshold=0.05, lineage=lineage,
    )
    ans, _ = pipe.query("What are the nomination norms for demat accounts?")
    assert not ans.abstained
    assert A in ans.superseded and ans.superseded[A] == [B]
    assert "superseded by" in ans.text


def _repealed_basis_pipeline():
    """Offline pipeline whose single circular rests on a repealed regulation."""
    C = "SEBI/HO/W/P/CIR/2020/07"
    text = (f"CIRCULAR {C}. Registration norms for stock brokers under the "
            "erstwhile regulations.")
    chunks = hierarchical_chunk(text, CircularMeta(circular_number=C))
    lineage = build_lineage([{"circular_number": C, "text": text}])
    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256), reranker=LexicalReranker(),
        generator=ExtractiveStubGenerator(), abstain_threshold=0.05, lineage=lineage,
    )
    pipe.regulatory_index = {
        C: {"regulatory_basis_status": "repealed_basis", "primary_regulation":
            "stock-brokers-1992", "regulations": [
            {"reg_id": "stock-brokers-1992", "short_name": "Stock Brokers",
             "year": 1992, "status": "repealed", "superseded_by": {
                 "reg_id": "stock-brokers-2026", "short_name": "Stock Brokers",
                 "year": 2026}}]}}
    return pipe, C


def test_note_fires_and_disambiguates_year():
    pipe, C = _repealed_basis_pipeline()
    ans, _ = pipe.query("What are the registration norms for stock brokers?")
    assert not ans.abstained and C in ans.text
    # names BOTH years distinctly — guards the short_name-collision bug
    assert "Stock Brokers Regulations, 1992" in ans.text
    assert "Stock Brokers Regulations, 2026" in ans.text
    assert "repealed" in ans.text.lower()


def test_note_absent_when_status_not_repealed_basis():
    pipe, C = _repealed_basis_pipeline()
    pipe.regulatory_index[C]["regulatory_basis_status"] = "mixed"
    ans, _ = pipe.query("What are the registration norms for stock brokers?")
    assert "Stock Brokers Regulations, 1992" not in ans.text


def test_note_absent_when_index_is_none():
    pipe, _ = _repealed_basis_pipeline()
    pipe.regulatory_index = None
    ans, _ = pipe.query("What are the registration norms for stock brokers?")
    assert "repealed regulation" not in ans.text


def test_query_as_of_prefers_governing_circular():
    OLD = "SEBI/HO/MRD/2020/010"
    NEW = "SEBI/HO/MRD/2023/050"
    old_text = ("This circular prescribes margin rules for the equity derivatives "
               "segment. Margin collection shall be on a T plus one basis.")
    new_text = (f"CIRCULAR {NEW}. This circular supersedes {OLD}. In supersession of "
               f"{OLD}, revised margin rules for the equity derivatives segment "
               "prescribe margin collection on a T plus zero basis.")
    chunks = hierarchical_chunk(
        old_text, CircularMeta(circular_number=OLD, issue_date="2020-01-01"))
    chunks += hierarchical_chunk(
        new_text, CircularMeta(circular_number=NEW, issue_date="2023-01-01"))
    lineage = build_lineage([
        {"circular_number": OLD, "issue_date": "2020-01-01", "text": old_text},
        {"circular_number": NEW, "issue_date": "2023-01-01", "text": new_text},
    ])
    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256), reranker=LexicalReranker(),
        generator=ExtractiveStubGenerator(), abstain_threshold=0.05, lineage=lineage,
    )
    ans_old, _ = pipe.query("margin rules for the equity derivatives segment",
                            as_of="2021-06-01")
    ans_new, _ = pipe.query("margin rules for the equity derivatives segment",
                            as_of="2024-06-01")
    assert any(c.startswith(OLD) for c in ans_old.citations)
    assert any(c.startswith(NEW) for c in ans_new.citations)


def test_retrieval_metrics():
    pipe = _build_pipeline()
    _, retrieved = pipe.query(
        "disclosure of material events and price sensitive information"
    )
    relevant = {cid for cid in retrieved if cid.startswith("SEBI/HO/CFD/2023/001")}
    assert relevant, "expected at least one relevant chunk retrieved"
    assert recall_at_k(retrieved, relevant, k=len(retrieved)) == pytest.approx(1.0)
    assert mrr(retrieved, relevant) > 0.0
    assert 0.0 < ndcg_at_k(retrieved, relevant, k=10) <= 1.0


class _FixedReranker:
    """Deterministic reranker: score by doc_id lookup (test-only)."""

    def __init__(self, scores):
        self.scores = scores

    def rerank(self, query, chunks):
        out = [(c, self.scores.get(c.doc_id, 0.0)) for c in chunks]
        out.sort(key=lambda cs: -cs[1])
        return out


def test_as_of_query_not_demoted_below_abstention_floor():
    """A circular that governed on the as-of date must keep its raw rerank
    score. Bug: global demote_superseded ran first, so the then-governing
    (now-superseded) circular arrived at the as-of branch already at
    score*0.3 and fell under the abstention threshold (score_floor)."""
    OLD = "SEBI/HO/MRD/2020/010"
    NEW = "SEBI/HO/MRD/2023/050"
    old_text = ("Margin rules for the equity derivatives segment. Margin "
                "collection shall be on a T plus one basis.")
    new_text = (f"CIRCULAR {NEW}. This circular supersedes {OLD}. In "
                f"supersession of {OLD}, margin collection on a T plus zero "
                "basis.")
    chunks = hierarchical_chunk(
        old_text, CircularMeta(circular_number=OLD, issue_date="2020-01-01"))
    chunks += hierarchical_chunk(
        new_text, CircularMeta(circular_number=NEW, issue_date="2023-01-01"))
    lineage = build_lineage([
        {"circular_number": OLD, "issue_date": "2020-01-01", "text": old_text},
        {"circular_number": NEW, "issue_date": "2023-01-01", "text": new_text},
    ])
    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256),
        reranker=_FixedReranker({OLD: 0.6, NEW: 0.9}),
        generator=ExtractiveStubGenerator(),
        abstain_threshold=0.40,  # production floor — this is the point
        lineage=lineage,
    )
    # On 2021-06-01, NEW does not exist yet and OLD governs: raw score 0.6
    # must survive (demoted 0.6*0.3=0.18 would abstain via score_floor).
    ans, _ = pipe.query("margin rules equity derivatives", as_of="2021-06-01")
    assert not ans.abstained, f"abstained: {ans.abstention_reason}"
    assert ans.citations and ans.citations[0].startswith(OLD)
    # Present-day query is untouched: demotion still prefers NEW.
    ans_now, _ = pipe.query("margin rules equity derivatives")
    assert not ans_now.abstained
    assert ans_now.citations[0].startswith(NEW)


def test_supersession_note_only_for_circulars_cited_in_answer_text():
    """citations = all top_k contexts, so a demoted superseded chunk deep in
    the context window used to trigger a note contradicting the in-force
    circular the answer text actually came from (Space bug at top_k >= 8)."""
    OLD = "SEBI/HO/X/2020/01"
    NEW = "SEBI/HO/X/2024/09"
    # NEW's text must NOT mention OLD, so lineage is built directly.
    lineage = Lineage(supersedes={NEW: [OLD]}, superseded_by={OLD: [NEW]})
    chunks = hierarchical_chunk(
        "Margin rules prescribe collection on a T plus one basis.",
        CircularMeta(circular_number=OLD, issue_date="2020-01-01"))
    chunks += hierarchical_chunk(
        "Revised margin rules prescribe collection on a T plus zero basis.",
        CircularMeta(circular_number=NEW, issue_date="2024-01-01"))
    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256),
        reranker=_FixedReranker({NEW: 0.9, OLD: 0.8}),
        generator=ExtractiveStubGenerator(), abstain_threshold=0.05,
        lineage=lineage,
    )
    ans, _ = pipe.query("margin rules", top_k=2)
    assert not ans.abstained
    # OLD is in the context window -> metadata still flags it...
    assert ans.superseded == {OLD: [NEW]}
    # ...but the answer text (NEW's chunk) never references OLD, so no note.
    assert "no longer in force" not in ans.text


def test_supersession_note_kept_when_answer_text_cites_superseded():
    OLD = "SEBI/HO/X/2020/01"
    NEW = "SEBI/HO/X/2024/09"
    lineage = Lineage(supersedes={NEW: [OLD]}, superseded_by={OLD: [NEW]})
    chunks = hierarchical_chunk(
        "Margin rules prescribe collection on a T plus one basis.",
        CircularMeta(circular_number=OLD, issue_date="2020-01-01"))

    class _CitesOld:
        def generate(self, query, contexts):
            return f"Per {OLD}, margin collection is on a T plus one basis."

    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256),
        reranker=_FixedReranker({OLD: 0.8}),
        generator=_CitesOld(), abstain_threshold=0.05, lineage=lineage,
    )
    ans, _ = pipe.query("margin rules", top_k=1)
    assert not ans.abstained
    assert ans.superseded == {OLD: [NEW]}
    assert "no longer in force" in ans.text and NEW in ans.text


def test_as_of_demotes_circular_already_superseded_on_that_date():
    """Giant-family regression (golden asof-p8): OLD is superseded by two
    same-day 2026 successors A1/A2, and A1 is in turn linked (edge-only, not
    text) to a later, topically-unrelated circular LATER issued *after*
    as_of. governing_on's family() walk pulls LATER into OLD/A1/A2's
    connected component, so governing_on resolves the whole family to
    whichever of A1/A2 remains "live" once LATER is excluded by the as-of
    date filter — demoting BOTH OLD and A1 by the same uniform penalty and
    leaving their raw rerank order (OLD > A1) untouched. Per-edge timing
    instead asks, for each candidate individually, whether a direct
    successor existed by as_of: OLD has one (A1, 2026-02-06) so it is
    demoted; A1's only successor is LATER (2026-05-01, after as_of) so A1
    is NOT demoted and correctly outranks OLD."""
    OLD = "SEBI/HO/Y/2025/131"
    A1 = "SEBI/HO/Y/2026/4360"
    A2 = "SEBI/HO/Y/2026/4361"
    LATER = "SEBI/HO/Y/2026/4900"
    lineage = Lineage(
        supersedes={A1: [OLD], A2: [OLD], LATER: [A1]},
        superseded_by={OLD: [A1, A2], A1: [LATER]},
    )
    chunks = hierarchical_chunk(
        "Digital accessibility compliance guidelines for intermediaries.",
        CircularMeta(circular_number=OLD, issue_date="2025-09-25"))
    chunks += hierarchical_chunk(
        "Revised digital accessibility compliance guidelines for intermediaries A1.",
        CircularMeta(circular_number=A1, issue_date="2026-02-06"))
    chunks += hierarchical_chunk(
        "Revised digital accessibility compliance guidelines for intermediaries A2.",
        CircularMeta(circular_number=A2, issue_date="2026-02-06"))
    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256),
        reranker=_FixedReranker({OLD: 0.99, A1: 0.97, A2: 0.95}),
        generator=ExtractiveStubGenerator(), abstain_threshold=0.05,
        lineage=lineage,
    )
    # On 2026-04-01, LATER (2026-05-01) does not exist yet, but A1
    # (2026-02-06) had already superseded OLD directly: OLD must be demoted
    # below A1, which retains its raw score since its only successor
    # (LATER) postdates as_of.
    ans, _ = pipe.query("digital accessibility compliance", as_of="2026-04-01",
                        top_k=1)
    assert not ans.abstained
    assert ans.citations[0].startswith(A1), ans.citations
    # On 2025-12-01, neither A1 nor A2 exist yet: OLD governs at full score.
    ans_before, _ = pipe.query("digital accessibility compliance",
                               as_of="2025-12-01", top_k=1)
    assert ans_before.citations[0].startswith(OLD), ans_before.citations
