"""Offline tests for the webis/set-encoder-base wrapper (2026-08-26 Set-Encoder
spec) — translation between this project's Reranker protocol and lightning-ir's
CrossEncoderModule.score() API, via a stubbed module; no lightning-ir / model
weights / network required. Mirrors tests/test_rerank_jina_v3.py's stub idiom."""
from __future__ import annotations

from sebi_rag.rerank import SetEncoderReranker
from sebi_rag.segment import Chunk


def _chunk(cid: str, text: str = "x") -> Chunk:
    return Chunk(id=cid, doc_id=cid.split("#")[0], section="s", text=text)


class _FakeScores:
    """Stands in for the torch.Tensor `CrossEncoderModule.score(...).scores`
    return value — only the chain SetEncoderReranker actually calls
    (.detach().to("cpu").float().tolist()) needs to work."""

    def __init__(self, values: list[float]) -> None:
        self._values = values

    def detach(self) -> "_FakeScores":
        return self

    def to(self, device: str) -> "_FakeScores":
        return self

    def float(self) -> "_FakeScores":
        return self

    def tolist(self) -> list[float]:
        return list(self._values)


class _FakeOutput:
    def __init__(self, scores: list[float]) -> None:
        self.scores = _FakeScores(scores)


class _FakeSetEncoderModule:
    """Stands in for lightning_ir.CrossEncoderModule — records the query/docs
    it was called with and returns scores positionally (unlike Jina's vendor
    API, lightning-ir's score() returns scores in input order, not pre-sorted
    with an index remap)."""

    def __init__(self, values: list[float]) -> None:
        self._values = values
        self.calls: list[tuple[str, list[str]]] = []

    def score(self, query: str, docs: list[str]):
        self.calls.append((query, list(docs)))
        return _FakeOutput(self._values)


class _StubSetEncoderReranker(SetEncoderReranker):
    """Bypass __init__ (no lightning-ir import / model download / network)."""

    def __init__(self, module: _FakeSetEncoderModule) -> None:
        self._module = module


def test_rerank_pairs_candidates_with_scores_in_input_order():
    chunks = [_chunk("a#s#0", "alpha"), _chunk("b#s#0", "beta"), _chunk("c#s#0", "gamma")]
    module = _FakeSetEncoderModule([0.2, 0.9, 0.5])
    rr = _StubSetEncoderReranker(module)

    out = rr.rerank("q", chunks)

    assert [c.id for c, _ in out] == ["b#s#0", "c#s#0", "a#s#0"]
    assert out[0][1] == 0.9 and out[-1][1] == 0.2


def test_rerank_sorts_descending():
    chunks = [_chunk("a#s#0"), _chunk("b#s#0"), _chunk("c#s#0")]
    module = _FakeSetEncoderModule([0.1, 0.2, 0.3])
    rr = _StubSetEncoderReranker(module)

    out = rr.rerank("q", chunks)

    scores = [s for _, s in out]
    assert scores == sorted(scores, reverse=True)


def test_rerank_passes_chunk_text_not_chunk_objects_to_the_module():
    chunks = [_chunk("a#s#0", "alpha text"), _chunk("b#s#0", "beta text")]
    module = _FakeSetEncoderModule([1.0, 0.0])
    rr = _StubSetEncoderReranker(module)

    rr.rerank("my query", chunks)

    assert module.calls == [("my query", ["alpha text", "beta text"])]


def test_rerank_empty_candidates_short_circuits_without_calling_the_module():
    module = _FakeSetEncoderModule([])
    rr = _StubSetEncoderReranker(module)

    assert rr.rerank("q", []) == []
    assert module.calls == []
