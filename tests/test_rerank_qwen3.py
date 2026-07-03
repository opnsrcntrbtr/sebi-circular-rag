"""Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and
rerank ordering via a stubbed scorer; no mlx / model weights required."""
from __future__ import annotations

from sebi_rag.rerank import Qwen3MLXReranker, qwen3_rerank_prompt
from sebi_rag.segment import Chunk


def test_prompt_format_matches_model_card():
    p = qwen3_rerank_prompt("q1", "d1")
    assert p.startswith("<|im_start|>system\nJudge whether the Document")
    assert '"yes" or "no"' in p
    assert "<Instruct>: " in p and "<Query>: q1\n<Document>: d1" in p
    assert p.endswith("<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n")


class _StubQwen(Qwen3MLXReranker):
    """Bypass __init__ (no mlx); score by keyword overlap to test ordering."""

    def __init__(self, max_doc_chars: int = 10) -> None:
        self.max_doc_chars = max_doc_chars

    def _score(self, query: str, doc: str) -> float:
        assert len(doc) <= self.max_doc_chars  # truncation applied by caller
        return sum(w in doc for w in query.split()) / (len(query.split()) or 1)


def test_rerank_orders_by_score_and_truncates():
    chunks = [
        Chunk(id="a#s#0", doc_id="a", section="a/s/p0", text="alpha beta"),
        Chunk(id="b#s#0", doc_id="b", section="b/s/p0", text="alpha xxxx"),
        Chunk(id="c#s#0", doc_id="c", section="c/s/p0", text="zzzz yyyy"),
    ]
    rr = _StubQwen(max_doc_chars=10)
    out = rr.rerank("alpha beta", chunks)
    assert [c.id for c, _ in out] == ["a#s#0", "b#s#0", "c#s#0"]
    assert out[0][1] == 1.0 and out[2][1] == 0.0
    assert all(0.0 <= s <= 1.0 for _, s in out)
