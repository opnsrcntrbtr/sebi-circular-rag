"""FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata."""
from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

from sebi_rag.api import CORPUS, create_app
from sebi_rag.corpus import load_circulars
from sebi_rag.embeddings import HashEmbedder
from sebi_rag.generate import ExtractiveStubGenerator
from sebi_rag.lineage import build_lineage, load_records
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.rerank import LexicalReranker
from sebi_rag.segment import CircularMeta, hierarchical_chunk


def _offline_pipeline() -> RAGPipeline:
    chunks = load_circulars(CORPUS)
    lineage = build_lineage(load_records(CORPUS))
    return RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(512), reranker=LexicalReranker(),
        generator=ExtractiveStubGenerator(), abstain_threshold=0.30, lineage=lineage,
    )


def _tiny_pipeline() -> RAGPipeline:
    A, B = "SEBI/HO/Z/P/CIR/2021/1", "SEBI/HO/Z/P/CIR/2025/9"
    chunks = hierarchical_chunk("Nomination norms for demat accounts.",
                                CircularMeta(circular_number=A))
    chunks += hierarchical_chunk(
        f"This circular supersedes. In supersession of {A}, revised nomination norms.",
        CircularMeta(circular_number=B))
    lineage = build_lineage([
        {"circular_number": A, "text": "nomination norms"},
        {"circular_number": B, "text": f"supersedes. In supersession of {A}."},
    ])
    return RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(128), reranker=LexicalReranker(),
        generator=ExtractiveStubGenerator(), abstain_threshold=0.05, lineage=lineage)


class _SlowGenerator:
    def generate(self, query, contexts):
        time.sleep(0.3)
        return "slow answer"


def _slow_pipeline() -> RAGPipeline:
    chunks = hierarchical_chunk("Nomination norms for demat accounts.",
                                CircularMeta(circular_number="SEBI/HO/Z/P/CIR/2024/1"))
    return RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(64), reranker=LexicalReranker(),
        generator=_SlowGenerator(), abstain_threshold=0.05,
        lineage=build_lineage([{"circular_number": "SEBI/HO/Z/P/CIR/2024/1", "text": "x"}]))


client = TestClient(create_app(_offline_pipeline))


def test_health():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["circulars"] >= 4
    assert body["chunks"] > body["circulars"]


def test_query_grounded_with_metadata_and_latency():
    r = client.post("/query", json={
        "question": "norms for sharing and usage of stock exchange price data for educational purposes"})
    assert r.status_code == 200
    body = r.json()
    assert body["abstained"] is False
    assert body["latency_ms"] >= 0.0
    assert body["citations_meta"]
    for m in body["citations_meta"]:
        assert m["circular"] and m["status"] in {"in_force", "superseded", "amended", "unknown"}


def test_query_abstains_out_of_domain():
    r = client.post("/query", json={"question": "best recipe for chocolate chip cookies"})
    body = r.json()
    assert body["abstained"] is True
    assert body["certainty"] == "low" and body["abstention_reason"]  # ADR-002


def test_top_k_zero_rejected_422():
    # ADR-002: top_k=0 previously caused a silent no-context abstention
    r = client.post("/query", json={"question": "nomination norms", "top_k": 0})
    assert r.status_code == 422


def test_response_carries_certainty_fields():
    body = client.post("/query", json={
        "question": "norms for sharing and usage of stock exchange price data "
                    "for educational purposes"}).json()
    assert body["certainty"] in {"high", "medium", "low"}
    assert "rerank_top" in body["confidence"] and "margin" in body["confidence"]
    assert body["draft_answer"] == ""  # advisory not requested


def test_auth_required_when_key_set(monkeypatch):
    monkeypatch.setenv("SEBI_RAG_API_KEY", "s3cret")
    c = TestClient(create_app(_tiny_pipeline))
    assert c.post("/query", json={"question": "nomination demat"}).status_code == 401
    ok = c.post("/query", json={"question": "nomination demat"},
                headers={"X-API-Key": "s3cret"})
    assert ok.status_code == 200


def test_rate_limit(monkeypatch):
    monkeypatch.setenv("SEBI_RAG_RATE_PER_MIN", "2")
    monkeypatch.delenv("SEBI_RAG_API_KEY", raising=False)
    c = TestClient(create_app(_tiny_pipeline))
    assert c.post("/query", json={"question": "nomination"}).status_code == 200
    assert c.post("/query", json={"question": "nomination"}).status_code == 200
    assert c.post("/query", json={"question": "nomination"}).status_code == 429


def test_query_exceeds_time_budget_returns_504(monkeypatch):
    monkeypatch.delenv("SEBI_RAG_API_KEY", raising=False)
    monkeypatch.setenv("SEBI_RAG_TIMEOUT_S", "0.05")
    c = TestClient(create_app(_slow_pipeline))
    assert c.post("/query", json={"question": "nomination"}).status_code == 504


def test_citation_meta_reports_superseded(monkeypatch):
    monkeypatch.delenv("SEBI_RAG_API_KEY", raising=False)
    c = TestClient(create_app(_tiny_pipeline))
    body = c.post("/query", json={"question": "nomination demat accounts"}).json()
    statuses = {m["circular"]: m["status"] for m in body["citations_meta"]}
    # the older superseded circular, if cited, is reported as superseded
    if "SEBI/HO/Z/P/CIR/2021/1" in statuses:
        assert statuses["SEBI/HO/Z/P/CIR/2021/1"] == "superseded"


def test_ready_triggers_pipeline() -> None:
    """/ready should trigger pipeline build and return ready=true."""
    c = TestClient(create_app(_offline_pipeline))
    resp = c.get("/ready")
    assert resp.status_code == 200
    assert resp.json() == {"ready": True}


class _CannedGenerator:
    def generate(self, query, contexts):
        return "CANNED-LLM-ANSWER"


def _distinct_pipeline() -> RAGPipeline:
    chunks = hierarchical_chunk("Nomination norms for demat accounts.",
                                CircularMeta(circular_number="SEBI/HO/Z/P/CIR/2024/7"))
    return RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(128), reranker=LexicalReranker(),
        generator=_CannedGenerator(), abstain_threshold=0.05,
        lineage=build_lineage([{"circular_number": "SEBI/HO/Z/P/CIR/2024/7",
                                "text": "nomination norms"}]))


_distinct_client = TestClient(create_app(_distinct_pipeline))


def test_mode_defaults_to_rag():
    r = _distinct_client.post("/query", json={"question": "nomination norms"})
    assert r.status_code == 200
    assert r.json()["answer"] == "CANNED-LLM-ANSWER"


def test_mode_retrieval_only_swaps_generator():
    r = _distinct_client.post(
        "/query", json={"question": "nomination norms", "mode": "retrieval_only"})
    assert r.status_code == 200
    body = r.json()
    # ExtractiveStubGenerator returns the top context text, never the canned LLM string
    assert body["answer"] != "CANNED-LLM-ANSWER"
    assert "nomination" in body["answer"].lower()


def test_mode_invalid_rejected_422():
    r = _distinct_client.post(
        "/query", json={"question": "nomination norms", "mode": "bogus"})
    assert r.status_code == 422


def test_mode_retrieval_only_shares_retrieval():
    q = {"question": "nomination norms"}
    rag = _distinct_client.post("/query", json={**q, "mode": "rag"}).json()
    ret = _distinct_client.post("/query", json={**q, "mode": "retrieval_only"}).json()
    assert rag["citations"] == ret["citations"]  # same retriever/reranker/lineage


def test_compute_kwargs_cpu_disables_fp16():
    from sebi_rag.api import _compute_kwargs
    from sebi_rag.settings import Settings
    s = Settings(corpus_path="c", index_dir="i",
                 device="cpu", use_fp16=True, encode_batch_size=16)
    assert _compute_kwargs(s) == {"device": "cpu", "use_fp16": False, "batch_size": 16}


def test_compute_kwargs_mps_keeps_fp16():
    from sebi_rag.api import _compute_kwargs
    from sebi_rag.settings import Settings
    s = Settings(corpus_path="c", index_dir="i",
                 device="mps", use_fp16=True, encode_batch_size=8)
    assert _compute_kwargs(s) == {"device": "mps", "use_fp16": True, "batch_size": 8}


def test_embedder_reranker_accept_compute_kwargs():
    import inspect
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.rerank import CrossEncoderReranker
    for cls in (BGEM3Embedder, CrossEncoderReranker):
        params = set(inspect.signature(cls.__init__).parameters)
        assert {"device", "use_fp16", "batch_size"} <= params


@pytest.mark.integration
def test_bge_fp16_encode_is_normalized():
    from sebi_rag.embeddings import BGEM3Embedder
    emb = BGEM3Embedder(device="mps", use_fp16=True, batch_size=4)
    v = emb.encode(["nomination norms for demat accounts", "unrelated text"])
    assert v.shape == (2, 1024)
    import numpy as np
    assert np.allclose(np.linalg.norm(v, axis=1), 1.0, atol=1e-3)


from sebi_rag.api import _citation_meta

_API_INDEX = {
    "SEBI/HO/Z/P/CIR/2021/1": {
        "regulatory_basis_status": "repealed_basis",
        "primary_regulation": "stock-brokers-1992",
        "regulations": [{
            "reg_id": "stock-brokers-1992", "short_name": "Stock Brokers",
            "year": 1992, "status": "repealed",
            "superseded_by": {"reg_id": "stock-brokers-2026",
                              "short_name": "Stock Brokers", "year": 2026}}]},
}


def test_citation_meta_fills_regulatory_fields():
    out = _citation_meta(["SEBI/HO/Z/P/CIR/2021/1#0"], None, _API_INDEX)
    assert len(out) == 1
    m = out[0]
    assert m.regulatory_basis_status == "repealed_basis"
    assert len(m.regulations) == 1
    assert m.regulations[0].year == 1992
    assert m.regulations[0].superseded_by.year == 2026


def test_citation_meta_defaults_when_index_none():
    out = _citation_meta(["SEBI/HO/Z/P/CIR/2021/1"], None, None)
    assert out[0].regulatory_basis_status == "unknown"
    assert out[0].regulations == []


def test_citation_meta_defaults_when_circular_absent_from_index():
    out = _citation_meta(["SEBI/HO/NOT/IN/INDEX/9"], None, _API_INDEX)
    assert out[0].regulatory_basis_status == "unknown"
    assert out[0].regulations == []
