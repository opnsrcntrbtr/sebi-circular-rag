"""Contextual chunk headers (iv9): one lay+statutory sentence per deep chunk.

Offline only — generation is an injected callable; mlx_lm never loads here.
"""
from __future__ import annotations

from sebi_rag.context_headers import (
    HeaderGenerator,
    apply_context_headers,
    in_scope,
    load_headers,
)
from sebi_rag.segment import Chunk


def test_describe_prompt_contains_inputs_and_constraints():
    seen: dict[str, str] = {}

    def fake(prompt: str) -> str:
        seen["p"] = prompt
        return " Governs winding down of a rating agency. "

    out = HeaderGenerator(fake).describe(
        "Master Circular for Credit Rating Agencies",
        "4.1.1. On and from the date of the Order",
        "not take any new clients or fresh mandates",
    )
    for frag in (
        "Master Circular for Credit Rating Agencies",
        "4.1.1. On and from the date of the Order",
        "not take any new clients or fresh mandates",
        "markdown",
    ):
        assert frag in seen["p"], f"prompt missing: {frag}"
    assert out == "Governs winding down of a rating agency."


def test_describe_cleans_markdown_and_newlines():
    g = HeaderGenerator(lambda p: "### Obligations\nof a CRA ceasing operations")
    assert g.describe("s", "g", "t") == "Obligations of a CRA ceasing operations"


def test_describe_error_or_empty_returns_empty():
    def boom(prompt: str) -> str:
        raise RuntimeError("mlx exploded")

    assert HeaderGenerator(boom).describe("s", "g", "t") == ""
    assert HeaderGenerator(lambda p: "  \n ").describe("s", "g", "t") == ""


def test_describe_truncates_to_max_chars():
    g = HeaderGenerator(lambda p: "y" * 999, max_chars=200)
    assert len(g.describe("s", "g", "t")) == 200


def _chunk(cid: str, text: str) -> Chunk:
    return Chunk(id=cid, doc_id=cid.split("#")[0], section="s", text=text)


def test_header_inserted_below_breadcrumb():
    cid = "DOC/1#4.1.1.2. not take any#0"
    c = _chunk(cid, "DOC/1 | subject | section\n4.1.1.2. body text")
    out = apply_context_headers([c], {cid: "Governs winding down."})
    assert out[0].text.splitlines() == [
        "DOC/1 | subject | section",
        "Governs winding down.",
        "4.1.1.2. body text",
    ]
    assert out[0].id == cid and len(out) == 1


def test_missing_or_empty_header_leaves_chunk_unchanged():
    c = _chunk("DOC/1#s#0", "a\nb")
    assert apply_context_headers([c], {})[0].text == "a\nb"
    assert apply_context_headers([c], {"DOC/1#s#0": "  "})[0].text == "a\nb"


def test_scope_predicate():
    assert in_scope("4.1.1. On and from the date")
    assert in_scope("12.5.2.1. rated such security")
    assert not in_scope("4.1. In order to facilitate")
    assert not in_scope("preamble")
    assert in_scope("Annexure 17")
    assert in_scope("Appendix A serial numbers")


def test_load_headers_missing_file_returns_empty(tmp_path):
    assert load_headers(tmp_path / "none.jsonl") == {}
