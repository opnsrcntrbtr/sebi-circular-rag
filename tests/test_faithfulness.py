"""Faithfulness: catch answers that cite circulars not in the retrieved context."""
from __future__ import annotations

from sebi_rag.embeddings import HashEmbedder
from sebi_rag.generate import faithfulness
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.rerank import LexicalReranker
from sebi_rag.segment import CircularMeta, hierarchical_chunk

REAL = "SEBI/HO/X/P/CIR/2023/1"
FAKE = "SEBI/HO/FAKE/P/CIR/2099/9"


def test_faithfulness_scoring():
    assert faithfulness(f"See [{REAL}] for details.", {REAL}) == (1.0, [])
    assert faithfulness(f"See [{REAL}#3] for details.", {REAL}) == (1.0, [])  # chunk id -> circular
    score, bad = faithfulness(f"Per [{FAKE}], the rule applies.", {REAL})
    assert score == 0.0 and bad == [FAKE]
    assert faithfulness("No citations here.", set()) == (1.0, [])
    assert faithfulness("[Note: not a citation]", set()) == (1.0, [])  # no '/', ignored


class _HallucinatingGenerator:
    def generate(self, query, contexts):
        return f"The applicable rule is in [{FAKE}]."


def test_pipeline_flags_hallucinated_citation():
    chunks = hierarchical_chunk("Disclosure norms for listed entities.",
                                CircularMeta(circular_number=REAL))
    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(128), reranker=LexicalReranker(),
        generator=_HallucinatingGenerator(), abstain_threshold=0.05,
    )
    ans, _ = pipe.query("What are the disclosure norms for listed entities?")
    assert not ans.abstained
    assert ans.faithfulness == 0.0
    assert FAKE in ans.unsupported_citations
    assert "treat this citation with caution" in ans.text
