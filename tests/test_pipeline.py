"""Minimal end-to-end test of the SEBI RAG pipeline.

Runs fully offline (HashEmbedder + bm25s + FAISS + RRF + LexicalReranker +
extractive stub) so Step-11 repository tests are fast and deterministic. The
heavy bge-m3 / cross-encoder path is exercised separately (Step 10).
"""
from __future__ import annotations

import pytest

from sebi_rag.embeddings import HashEmbedder
from sebi_rag.eval import mrr, ndcg_at_k, recall_at_k
from sebi_rag.lineage import build_lineage
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
