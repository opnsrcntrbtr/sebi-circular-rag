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


# --- governing-clause folding (probe-par-03 / CRA sub-clause class) ---------
# Same per-line splitting trigger as _TEXT: one blank-line-free block.
_CRA_TEXT = (
    _FILLER + "\n"
    "4.1.1. On and from the date of the Order of winding down or surrender "
    "of certificate of registration, the CRA shall:\n"
    "4.1.1.1. not onboard any new clients or accept fresh rating mandates;\n"
    "4.1.1.2. permit companies to withdraw ongoing rating assignments "
    "without levy of any charge;\n"
    "4.1.2. All other obligations of the CRA shall continue as specified."
)


def test_sibling_list_item_carries_governing_clause():
    # 4.1.1.2 is the SECOND child: the carry mechanism only rescues the first,
    # so this chunk historically lost the "winding down" context entirely.
    chunks = hierarchical_chunk(_CRA_TEXT, _META)
    for c in chunks:
        if "withdraw ongoing rating assignments" in c.text:
            assert "winding down" in c.text, (
                f"governing clause missing from sibling chunk: {c.text!r}"
            )
            break
    else:
        raise AssertionError("4.1.1.2 provision text missing from all chunks")


def test_governing_clause_not_duplicated():
    chunks = hierarchical_chunk(_CRA_TEXT, _META)
    for c in chunks:
        assert c.text.count("On and from the date of the Order") <= 1, (
            f"governing clause duplicated: {c.text!r}"
        )


def test_nominee_regression_corpus_unchanged_behaviour():
    # the original nominee-bug guarantees still hold with folding active
    chunks = hierarchical_chunk(_TEXT, _META)
    for c in chunks:
        assert _body(c) != "5. Number of nominees:"
    assert any(
        "Number of nominees" in c.text and "up to 3 nominees" in c.text
        for c in chunks
    )


# --- wrapped-line governing-clause absorption (probe-par-03 residual) --------
# SEBI PDFs hard-wrap clause text; in a blank-line-free block each physical
# line arrives as its own paragraph, so only line 1 was recorded as the head.
_WRAPPED_CRA_TEXT = (
    _FILLER + "\n"
    "4.1.1. On and from the date of the Order, or the date of submission of "
    "request for\n"
    "surrender of certificate of registration to SEBI, as applicable,\n"
    "the concerned CRA shall –\n"
    "4.1.1.1. disclose prominently on its website the fact of winding down;\n"
    "4.1.1.2. permit companies to withdraw ongoing rating assignments "
    "without levy of any charge;\n"
    "4.1.2. All other obligations of the CRA shall continue as specified."
)


def test_wrapped_governing_clause_folds_full_text_into_sibling():
    # Head line 1 ends at "request for"; the discriminative tokens
    # ("surrender", "certificate") live on wrap line 2. The sibling chunk
    # 4.1.1.2 must carry them via the folded prefix.
    chunks = hierarchical_chunk(_WRAPPED_CRA_TEXT, _META)
    for c in chunks:
        if "withdraw ongoing rating assignments" in c.text:
            assert "surrender of certificate" in c.text, (
                f"wrapped clause text missing from sibling chunk: {c.text!r}"
            )
            break
    else:
        raise AssertionError("4.1.1.2 provision text missing from all chunks")


def test_terminator_head_absorbs_nothing():
    # A head already ending in a clause terminator (":") must not absorb the
    # following body line into the governing clause.
    text = (
        _FILLER + "\n"
        "5. Number of nominees:\n"
        "This provision applies to all folios opened after the effective "
        "date.\n"
        "5.1. Investors can provide up to 3 nominees."
    )
    chunks = hierarchical_chunk(text, _META)
    for c in chunks:
        if "up to 3 nominees" in c.text:
            assert "applies to all folios" not in c.text, (
                f"terminated head wrongly absorbed body text: {c.text!r}"
            )
            break
    else:
        raise AssertionError("5.1 provision text missing from all chunks")


def test_absorption_respects_300_char_cap():
    # A long unterminated head plus a long continuation must never yield a
    # folded governing-clause line over 300 chars.
    head_line = "7.1.1. " + ("alpha bravo charlie delta echo " * 9).strip()
    continuation = ("wrapped continuation tokens " * 12).strip()
    text = (
        _FILLER + "\n"
        f"{head_line}\n"
        f"{continuation}\n"
        "7.1.1.1. first child provision;\n"
        "7.1.1.2. second child provision about margin obligations;"
    )
    chunks = hierarchical_chunk(text, _META)
    for c in chunks:
        if "second child provision" in c.text:
            gov_lines = [
                l for l in c.text.splitlines() if l.startswith("7.1.1. ")
            ]
            assert gov_lines, "governing clause not folded into child chunk"
            assert all(len(l) <= 300 for l in gov_lines), (
                f"folded clause exceeds 300-char cap: {gov_lines!r}"
            )
            break
    else:
        raise AssertionError("7.1.1.2 provision text missing from all chunks")
