"""Step 12 — end-to-end RAG integration test with the REAL stack.

bge-m3 (MPS) + bge-reranker-v2-m3 CrossEncoder (MPS) + Ollama generation.
Marked `integration` and skipped by default (slow, loads weights, needs the
Ollama server). Run with:  pytest -m integration
"""
from __future__ import annotations

import urllib.request

import pytest

from sebi_rag.embeddings import BGEM3Embedder
from sebi_rag.generate import ABSTAIN, OllamaGenerator
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.rerank import CrossEncoderReranker

from test_pipeline import CIRCULARS  # reuse the sample corpus
from sebi_rag.segment import hierarchical_chunk

pytestmark = pytest.mark.integration

OLLAMA = "http://127.0.0.1:11434"


def _ollama_up() -> bool:
    try:
        with urllib.request.urlopen(f"{OLLAMA}/api/version", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


@pytest.fixture(scope="module")
def pipeline():
    if not _ollama_up():
        pytest.skip("Ollama server not reachable on :11434")
    chunks = []
    for meta, text in CIRCULARS:
        chunks.extend(hierarchical_chunk(text, meta))
    return RAGPipeline.build(
        chunks=chunks,
        embedder=BGEM3Embedder(device="mps"),
        reranker=CrossEncoderReranker(device="mps"),
        generator=OllamaGenerator(model="llama3.1:8b"),
        abstain_threshold=0.30,
    )


def test_e2e_grounded_answer_with_citation(pipeline):
    ans, retrieved = pipeline.query(
        "Within how long must listed entities disclose material events?"
    )
    assert not ans.abstained
    assert any(c.startswith("SEBI/HO/CFD/2023/001") for c in ans.citations)
    assert ans.text and ans.text != ABSTAIN
    # answer should be grounded in the 24-hour disclosure rule
    assert "24" in ans.text or "twenty four" in ans.text.lower()


def test_e2e_abstains_out_of_domain(pipeline):
    ans, _ = pipeline.query("What is the best recipe for chocolate cookies?")
    assert ans.abstained
    assert ans.text == ABSTAIN
