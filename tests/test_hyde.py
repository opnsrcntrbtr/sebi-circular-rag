"""HyDE expander (Part B): query -> hypothetical statutory passage.

Offline only — generation is an injected callable; mlx_lm never loads here.
"""
from __future__ import annotations

from sebi_rag.hyde import HydeExpander


def test_prompt_contains_query_and_style_cue():
    seen: dict[str, str] = {}

    def fake(prompt: str) -> str:
        seen["prompt"] = prompt
        return "  The CRA shall not take any new clients.  "

    out = HydeExpander(fake).hypothesize(
        "can companies pull their rating assignments?"
    )
    assert "can companies pull their rating assignments?" in seen["prompt"]
    assert "SEBI circular" in seen["prompt"]
    assert out == "The CRA shall not take any new clients."


def test_generation_error_returns_empty():
    def boom(prompt: str) -> str:
        raise RuntimeError("mlx exploded")

    assert HydeExpander(boom).hypothesize("any query") == ""


def test_whitespace_output_returns_empty():
    assert HydeExpander(lambda p: "   \n ").hypothesize("any query") == ""


def test_output_truncated_to_max_chars():
    ex = HydeExpander(lambda p: "x" * 5000, max_chars=1200)
    assert len(ex.hypothesize("any query")) == 1200


# --- wiring: hyde_text as an additive third RRF leg --------------------------

from sebi_rag.embeddings import HashEmbedder  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.segment import Chunk  # noqa: E402


def _chunk(i: int, text: str) -> Chunk:
    return Chunk(id=f"DOC/{i}#s#0", doc_id=f"DOC/{i}",
                 section=f"DOC/{i}/s/p0", text=text)


_CORPUS = [
    _chunk(1, "The CRA shall not take any new clients or fresh mandates "
              "upon surrender of certificate of registration."),
    _chunk(2, "Settlement of trades occurs on a T plus one cycle."),
    _chunk(3, "Margin requirements for derivatives are specified in "
              "Annexure A of this circular."),
]


def _rank(results: list, cid: str) -> int:
    ids = [c.id for c, _ in results]
    return ids.index(cid)


def test_hyde_leg_improves_paraphrase_gap_rank():
    r = HybridRetriever.build(_CORPUS, HashEmbedder(dim=64))
    # query matches DOC/2 and DOC/3 lexically, DOC/1 not at all
    q = "settlement margin requirements for trades"
    hyde = ("Upon surrender of certificate of registration the CRA shall "
            "not take any new clients or fresh mandates.")
    without = r.retrieve(q, top_n=3)
    with_h = r.retrieve(q, top_n=3, hyde_text=hyde)
    assert _rank(with_h, "DOC/1#s#0") < _rank(without, "DOC/1#s#0"), (
        "hyde leg did not improve the paraphrase-gap chunk's rank"
    )


def test_none_and_empty_hyde_are_identical_to_baseline():
    r = HybridRetriever.build(_CORPUS, HashEmbedder(dim=64))
    q = "settlement of trades"
    base = [(c.id, s) for c, s in r.retrieve(q)]
    none_ = [(c.id, s) for c, s in r.retrieve(q, hyde_text=None)]
    empty = [(c.id, s) for c, s in r.retrieve(q, hyde_text="")]
    assert base == none_ == empty
