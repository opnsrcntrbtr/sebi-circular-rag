"""Offline tests for the jina-reranker-v3-mlx wrapper (ADR-004) — translation
between this project's Reranker protocol and the vendor's raw-string API, via
a stubbed backend; no mlx / model weights / network required."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from sebi_rag.rerank import JinaMLXReranker, retrieval_reranker_for
from sebi_rag.segment import Chunk

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _chunk(cid: str, text: str = "x") -> Chunk:
    return Chunk(id=cid, doc_id=cid.split("#")[0], section="s", text=text)


class _FakeJinaBackend:
    """Stands in for the vendor's MLXReranker.rerank() — same return shape
    (list of dicts with 'index' into the ORIGINAL input list and
    'relevance_score'), deliberately returned out of index order to prove the
    wrapper maps back by index rather than assuming order is preserved."""

    def __init__(self, scores: dict[int, float]):
        self._scores = scores
        self.calls: list[tuple[str, list[str]]] = []

    def rerank(self, query, documents, top_n=None, return_embeddings=False):
        self.calls.append((query, list(documents)))
        items = [{"document": documents[i], "relevance_score": s, "index": i}
                 for i, s in self._scores.items()]
        items.sort(key=lambda it: -it["relevance_score"])  # vendor returns pre-sorted
        return items


class _StubJinaMLXReranker(JinaMLXReranker):
    """Bypass __init__ (no snapshot_download / mlx / network)."""

    def __init__(self, backend: _FakeJinaBackend) -> None:
        self._reranker = backend


def test_rerank_maps_vendor_results_back_to_chunks_by_index():
    chunks = [_chunk("a#s#0", "alpha"), _chunk("b#s#0", "beta"), _chunk("c#s#0", "gamma")]
    # Deliberately non-monotonic in position: middle chunk scores highest.
    backend = _FakeJinaBackend({0: 0.2, 1: 0.9, 2: 0.5})
    rr = _StubJinaMLXReranker(backend)

    out = rr.rerank("q", chunks)

    assert [c.id for c, _ in out] == ["b#s#0", "c#s#0", "a#s#0"]
    assert out[0][1] == 0.9 and out[-1][1] == 0.2


def test_rerank_passes_chunk_text_not_chunk_objects_to_the_backend():
    chunks = [_chunk("a#s#0", "alpha text"), _chunk("b#s#0", "beta text")]
    backend = _FakeJinaBackend({0: 1.0, 1: 0.0})
    rr = _StubJinaMLXReranker(backend)

    rr.rerank("my query", chunks)

    assert backend.calls == [("my query", ["alpha text", "beta text"])]


def test_rerank_empty_candidates_short_circuits_without_calling_the_backend():
    backend = _FakeJinaBackend({})
    rr = _StubJinaMLXReranker(backend)

    assert rr.rerank("q", []) == []
    assert backend.calls == []


# --- retrieval_reranker_for: ADR-004's single retrieval-reranker decision ----
# Mirrors citation_scorer_for's shape exactly: the SAME seam every pipeline
# builder routes through, so eval and production can never disagree about
# which reranker orders the pool. Never affects citation scoring — R1 showed
# that role fails independently of retrieval-reranking quality, which is why
# citation_scorer_for is always built against the bge instance directly.

def test_retrieval_reranker_for_defaults_to_bge():
    bge = object()
    assert retrieval_reranker_for("bge", bge) is bge


def test_retrieval_reranker_for_selects_jina_via_injected_loader():
    bge = object()
    sentinel = object()
    got = retrieval_reranker_for("jina", bge, jina_loader=lambda: sentinel)
    assert got is sentinel


def test_retrieval_reranker_for_does_not_load_jina_when_bge_selected():
    bge = object()
    called = []
    got = retrieval_reranker_for("bge", bge, jina_loader=lambda: called.append(1))
    assert got is bge and not called, "must not load a model just to discard it"


def test_retrieval_reranker_for_rejects_an_unknown_model():
    try:
        retrieval_reranker_for("magic", object())
    except ValueError as e:
        assert "magic" in str(e)
    else:
        raise AssertionError("expected ValueError on unknown reranker model")


# --- coupling: eval_json.py must measure whatever production actually runs --
# It builds its own RAGPipeline directly (to reuse the persisted index rather
# than re-embedding — see its own comment), so it does NOT automatically pick
# up api.py's wiring. Without this, eval_json.py would silently keep measuring
# bge-reranker-v2-m3 even after production switched to Jina (ADR-004) — a
# worse failure than not testing a new candidate: it measures a configuration
# production no longer serves. derive_thresholds.py is deliberately EXCLUDED:
# it fixes the floor-derivation baseline on bge-reranker-v2-m3 on purpose, so
# a floor comparison against it keeps meaning something.

def test_eval_json_routes_the_retrieval_reranker_through_the_shared_factory():
    src = (ROOT / "scripts" / "eval_json.py").read_text(encoding="utf-8")
    assert "retrieval_reranker_for(" in src, \
        "eval_json.py does not route through the shared reranker seam"
    assert not re.search(r"reranker=rer\b", src), \
        "eval_json.py hardcodes rer directly as pipeline.reranker"


def test_eval_asof_routes_the_retrieval_reranker_through_the_shared_factory():
    """Same bug, same fix, second script: eval_asof.py also builds its own
    RAGPipeline directly and had CrossEncoderReranker hardcoded — caught
    2026-08-24 when a post-adoption eval-asof run's own metadata still said
    reranker: BAAI/bge-reranker-v2-m3 after reranker_model=jina shipped, i.e.
    the "13/13 unchanged" claim had silently never tested Jina at all."""
    src = (ROOT / "scripts" / "eval_asof.py").read_text(encoding="utf-8")
    assert "retrieval_reranker_for(" in src, \
        "eval_asof.py does not route through the shared reranker seam"
    assert not re.search(r"reranker=rer\b", src), \
        "eval_asof.py hardcodes rer directly as pipeline.reranker"
