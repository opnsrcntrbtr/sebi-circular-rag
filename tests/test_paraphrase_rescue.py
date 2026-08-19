"""Paraphrase rescue (prereg 2026-08-19).

Contract under test:
- the rescue fires ONLY when rerank_top is below the score floor;
- it re-scores the SAME pool (no re-retrieval) with a rewritten query;
- it keeps the rescued list only if the rewrite lifts the top score to/above
  the floor, so a rescue can never lower the gate signal;
- a degenerate rewrite is rejected and the original list is preserved byte-wise;
- supersession/as-of handling is applied to the rescued list by the same path
  as the original, so a rescue cannot smuggle a superseded circular through.
"""
from __future__ import annotations

import pytest

from sebi_rag.paraphrase_rescue import (
    MAX_REWRITE_WORDS, StaticQueryRewriter, is_degenerate, query_rewriter_for,
    rescue_pool,
)
from sebi_rag.segment import Chunk
from sebi_rag.settings import Settings

FLOOR = 0.05


def _chunk(cid: str, doc: str = "D1", text: str = "body", subject: str = "Subj") -> Chunk:
    return Chunk(id=cid, doc_id=doc, section=f"{doc}/s", text=text,
                 meta={"subject": subject})


class _KeywordReranker:
    """Scores 0.9 when the query contains `hot`, else 0.01 — a stand-in for a
    cross-encoder that only recognises statutory vocabulary."""

    def __init__(self, hot: str = "intraday") -> None:
        self.hot = hot
        self.calls: list[str] = []

    def rerank(self, query: str, candidates: list[Chunk]) -> list[tuple[Chunk, float]]:
        self.calls.append(query)
        score = 0.9 if self.hot in query.lower() else 0.01
        return [(c, score) for c in candidates]


# --- is_degenerate ---------------------------------------------------------

@pytest.mark.parametrize("rewritten", [None, "", "   "])
def test_empty_rewrite_is_degenerate(rewritten):
    assert is_degenerate("original query", rewritten) is True


def test_unchanged_rewrite_is_degenerate():
    assert is_degenerate("Can a fund borrow?", "can a fund borrow?") is True


def test_overlong_rewrite_is_degenerate():
    long = " ".join(["word"] * (MAX_REWRITE_WORDS + 1))
    assert is_degenerate("q", long) is True


def test_rewrite_at_the_word_limit_is_accepted():
    at_limit = " ".join(["word"] * MAX_REWRITE_WORDS)
    assert is_degenerate("q", at_limit) is False


def test_plausible_rewrite_is_not_degenerate():
    assert is_degenerate(
        "Can an asset manager take a short-term bank loan?",
        "intraday borrowing by mutual funds to meet redemption payouts",
    ) is False


# --- rescue_pool -----------------------------------------------------------

def test_rescue_does_not_fire_when_top_score_is_at_or_above_floor():
    pool = [_chunk("c1")]
    reranked = [(pool[0], FLOOR)]
    rer = _KeywordReranker()
    out, used = rescue_pool("lay query", pool, reranked, rer,
                            StaticQueryRewriter("intraday borrowing"), FLOOR)
    assert out == reranked
    assert used is None
    assert rer.calls == []  # reranker never invoked


def test_rescue_fires_below_floor_and_keeps_the_lifted_list():
    pool = [_chunk("c1")]
    reranked = [(pool[0], 0.0296)]
    rer = _KeywordReranker()
    out, used = rescue_pool("short-term bank loan", pool, reranked, rer,
                            StaticQueryRewriter("intraday borrowing by funds"),
                            FLOOR)
    assert used == "intraday borrowing by funds"
    assert out[0][1] == pytest.approx(0.9)
    assert rer.calls == ["intraday borrowing by funds"]  # SAME pool, one pass


def test_rescue_that_fails_to_clear_the_floor_is_discarded():
    pool = [_chunk("c1")]
    reranked = [(pool[0], 0.0296)]
    # rewriter produces vocabulary the reranker still does not recognise
    rer = _KeywordReranker()
    out, used = rescue_pool("short-term bank loan", pool, reranked, rer,
                            StaticQueryRewriter("some other phrasing"), FLOOR)
    assert out == reranked  # original list preserved exactly
    assert used is None


def test_degenerate_rewrite_short_circuits_before_reranking():
    pool = [_chunk("c1")]
    reranked = [(pool[0], 0.0296)]
    rer = _KeywordReranker()
    out, used = rescue_pool("q", pool, reranked, rer,
                            StaticQueryRewriter(""), FLOOR)
    assert out == reranked
    assert used is None
    assert rer.calls == []  # no wasted rerank pass


def test_no_rewriter_is_inert():
    pool = [_chunk("c1")]
    reranked = [(pool[0], 0.0296)]
    rer = _KeywordReranker()
    out, used = rescue_pool("q", pool, reranked, rer, None, FLOOR)
    assert out == reranked
    assert used is None
    assert rer.calls == []


def test_empty_pool_is_inert():
    rer = _KeywordReranker()
    out, used = rescue_pool("q", [], [], rer,
                            StaticQueryRewriter("intraday"), FLOOR)
    assert out == []
    assert used is None


def test_rewriter_sees_the_query_and_the_pool_chunks():
    pool = [_chunk("c1", text="Intraday Borrowings"), _chunk("c2")]
    reranked = [(pool[0], 0.01), (pool[1], 0.005)]
    seen: dict = {}

    class _Recording:
        def rewrite(self, query: str, chunks: list[Chunk]) -> str | None:
            seen["query"] = query
            seen["chunks"] = chunks
            return "intraday borrowing"

    rescue_pool("lay query", pool, reranked, _KeywordReranker(), _Recording(),
                FLOOR)
    assert seen["query"] == "lay query"
    assert [c.id for c in seen["chunks"]] == ["c1", "c2"]


def test_rewriter_receives_chunks_in_reranked_order_not_pool_order():
    """PRF depends on seeing the best candidates first."""
    a, b = _chunk("c1"), _chunk("c2")
    pool = [a, b]
    reranked = [(b, 0.02), (a, 0.01)]  # b outranks a
    seen: dict = {}

    class _Recording:
        def rewrite(self, query: str, chunks: list[Chunk]) -> str | None:
            seen["ids"] = [c.id for c in chunks]
            return None

    rescue_pool("q", pool, reranked, _KeywordReranker(), _Recording(), FLOOR)
    assert seen["ids"] == ["c2", "c1"]


# --- pipeline wiring -------------------------------------------------------

class _FakeRetriever:
    def __init__(self, chunks: list[Chunk]) -> None:
        self._chunks = chunks

    def retrieve(self, query: str, top_n: int = 50) -> list[tuple[Chunk, float]]:
        return [(c, 1.0) for c in self._chunks]


class _EchoGenerator:
    def generate(self, query: str, contexts: list[Chunk]) -> str:
        return f"answer from {contexts[0].doc_id}"


def _pipeline(chunks, reranker, rewriter=None, lineage=None):
    from sebi_rag.pipeline import RAGPipeline

    return RAGPipeline(
        retriever=_FakeRetriever(chunks), reranker=reranker,
        generator=_EchoGenerator(), abstain_threshold=FLOOR,
        lineage=lineage, query_rewriter=rewriter,
    )


def test_pipeline_is_inert_without_a_rewriter():
    chunks = [_chunk("c1")]
    ans, _ = _pipeline(chunks, _KeywordReranker()).query("lay query")
    assert ans.abstained is True
    assert ans.abstention_reason == "score_floor"
    assert "rescue_query" not in ans.confidence


def test_pipeline_rescue_answers_and_records_the_rewrite():
    chunks = [_chunk("c1")]
    ans, _ = _pipeline(
        chunks, _KeywordReranker(),
        StaticQueryRewriter("intraday borrowing by mutual funds"),
    ).query("short-term bank loan")
    assert ans.abstained is False
    assert ans.confidence["rescue_query"] == "intraday borrowing by mutual funds"
    assert ans.confidence["rerank_top"] == pytest.approx(0.9)


def test_failed_rescue_leaves_the_abstention_untouched():
    chunks = [_chunk("c1")]
    ans, _ = _pipeline(
        chunks, _KeywordReranker(), StaticQueryRewriter("still lay wording"),
    ).query("short-term bank loan")
    assert ans.abstained is True
    assert ans.abstention_reason == "score_floor"
    assert "rescue_query" not in ans.confidence


def test_rescued_list_is_demoted_by_supersession_like_the_original():
    """A rescue must not lift a superseded circular past the floor.

    The rewrite scores the chunk 0.9, but its circular is superseded, so the
    0.05 penalty drops it to 0.045 — below the floor. The rescue is discarded
    and the row still abstains.
    """
    chunks = [_chunk("c1", doc="OLD")]
    pipe = _pipeline(
        chunks, _KeywordReranker(),
        StaticQueryRewriter("intraday borrowing"),
        lineage=type("L", (), {"superseded_by": {"OLD": ["NEW"]}})(),
    )
    pipe.superseded_penalty = 0.05
    ans, _ = pipe.query("short-term bank loan")
    assert ans.abstained is True
    assert "rescue_query" not in ans.confidence


def test_factory_returns_none_when_disabled():
    """Disabled must not construct the rewriter — it would load an MLX model."""
    assert query_rewriter_for(False) is None


def test_paraphrase_rescue_defaults_off_in_shipped_config():
    """The prereg keeps the flag off until §6 and §7 pass."""
    assert Settings.load().paraphrase_rescue is False


def test_rescue_survives_demotion_when_it_still_clears_the_floor():
    chunks = [_chunk("c1", doc="OLD")]
    pipe = _pipeline(
        chunks, _KeywordReranker(),
        StaticQueryRewriter("intraday borrowing"),
        lineage=type("L", (), {"superseded_by": {"OLD": ["NEW"]}})(),
    )
    pipe.superseded_penalty = 0.3  # 0.9 * 0.3 = 0.27 >= 0.05
    ans, _ = pipe.query("short-term bank loan")
    assert ans.abstained is False
    assert ans.confidence["rerank_top"] == pytest.approx(0.27)
