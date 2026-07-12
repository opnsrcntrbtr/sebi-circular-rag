"""Chunker (segment.hierarchical_chunk) behaviour.

Regression guard for the "5. Number of nominees:" bug: a section whose body
lives entirely in subsections must not be emitted as a standalone chunk whose
body is just the parent heading (the section ordinal then reads as a value to
extractive generators). See memory/nominee-count-chunker-bug.md.
"""
from __future__ import annotations

from sebi_rag.segment import CircularMeta, hierarchical_chunk

_META = CircularMeta(circular_number="SEBI/HO/T/P/CIR/2026/1")

# One long, blank-line-free block forces _paragraphs to split per line, exactly
# as the scraped-PDF corpus does (which is what produced the degenerate chunks).
_FILLER = "0. Preamble. " + "This clause restates prior guidance. " * 40
_TEXT = (
    _FILLER + "\n"
    "5. Number of nominees:\n"
    "5.1. Investors can provide up to 3 nominees.\n"
    "5.2. In case of multiple nominees, the account continues after the demise "
    "of the investor in the same folio without disruption.\n"
    "6. Nomination process:\n"
    "6.1. Nomination is optional for jointly held folios."
)


def _body(chunk) -> str:
    """Chunk text is 'breadcrumb-header\\nbody'; return the body."""
    return chunk.text.split("\n", 1)[1].strip() if "\n" in chunk.text else ""


def test_bare_parent_heading_not_emitted_as_standalone_chunk():
    chunks = hierarchical_chunk(_TEXT, _META)
    for c in chunks:
        assert _body(c) != "5. Number of nominees:", (
            f"degenerate heading-only chunk emitted: {c.text!r}"
        )


def test_bare_parent_heading_folds_into_first_subsection():
    chunks = hierarchical_chunk(_TEXT, _META)
    assert any(
        "Number of nominees" in c.text and "up to 3 nominees" in c.text
        for c in chunks
    ), "parent heading not folded together with its first subsection"


def test_leaf_single_line_provision_is_preserved_not_overmerged():
    # 5.2 is a leaf (its successor 6. is a sibling-level heading, not a child),
    # so it must stay in its own chunk, not get folded into section 6.
    chunks = hierarchical_chunk(_TEXT, _META)
    for c in chunks:
        if "the account continues" in c.text:
            assert "Nomination is optional" not in c.text, (
                "leaf provision 5.2 was wrongly merged into section 6"
            )
            break
    else:
        raise AssertionError("5.2 provision text missing from all chunks")
