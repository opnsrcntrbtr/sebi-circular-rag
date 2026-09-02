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


# --- table-row shredding fix (2026-09-01) ------------------------------------
# PDF-flattened table rows ("2. Brent Crude Oil BBL 400,000") match the same
# heading regex as a real numbered section and, without _merge_table_rows,
# each row was flushed as its own one-line chunk, destroying row<->header
# association. See memory/nominee-count-chunker-bug.md's live-defect update.
_TABLE_TEXT = (
    _FILLER + "\n"
    "9. Total income from operations 1234\n"
    "10. Brent Crude Oil BBL 400,000\n"
    "11. Canada - Toronto Stock Exchange\n"
    "12. Unique Client Code 59\n"
    "13. Age of member 47"
)


def test_flattened_table_rows_merge_into_one_chunk():
    chunks = hierarchical_chunk(_TABLE_TEXT, _META)
    rows = ["Total income from operations", "Brent Crude Oil BBL 400,000",
            "Canada - Toronto Stock Exchange", "Unique Client Code 59",
            "Age of member 47"]
    hosts = {c.id for c in chunks if any(r in c.text for r in rows)}
    assert len(hosts) == 1, (
        f"table rows scattered across {len(hosts)} chunks instead of merged "
        f"into one: {[c.text for c in chunks if c.id in hosts]!r}"
    )


def test_flattened_table_row_not_emitted_as_lone_chunk():
    chunks = hierarchical_chunk(_TABLE_TEXT, _META)
    for c in chunks:
        assert _body(c) != "10. Brent Crude Oil BBL 400,000", (
            f"table row emitted as a standalone degenerate chunk: {c.text!r}"
        )


# A genuine short-heading run broken by real prose between each heading must
# NOT be swept up by the table-row merge - only a run with nothing between
# consecutive headings is table-shaped.
_SHORT_HEADINGS_WITH_PROSE = (
    _FILLER + "\n"
    "1. Preamble:\n"
    "This circular explains conduct requirements for market participants "
    "operating in India across regulated segments under applicable law.\n"
    "2. Applicability:\n"
    "This circular applies to all registered stock brokers, depository "
    "participants, and other intermediaries under SEBI's framework.\n"
    "3. Effective date:\n"
    "This circular takes immediate effect from the date of issuance and "
    "remains applicable until further notice or amendment."
)


def test_genuine_short_heading_run_with_prose_still_splits():
    chunks = hierarchical_chunk(_SHORT_HEADINGS_WITH_PROSE, _META)
    for heading, body_snippet in (
        ("Preamble", "conduct requirements"),
        ("Applicability", "registered stock brokers"),
        ("Effective date", "immediate effect"),
    ):
        assert any(heading in c.text and body_snippet in c.text for c in chunks), (
            f"section {heading!r} lost its own prose body (wrongly merged?)"
        )
    # and no chunk should hold more than one of the three prose bodies -
    # merging headings that DO have real, separate bodies would be the
    # opposite failure mode.
    for c in chunks:
        hit = sum(s in c.text for s in
                  ("conduct requirements", "registered stock brokers",
                   "immediate effect"))
        assert hit <= 1, f"multiple sections wrongly merged into one chunk: {c.text!r}"


# A short numeric TOC/index run ("48. 119") must be absorbed with its
# neighbours, not emitted as an isolated one-line chunk.
_TOC_TEXT = _FILLER + "\n" + "\n".join(
    f"{n}. {v}" for n, v in ((46, 12), (47, 39), (48, 119), (49, 205))
)


def test_toc_numeric_run_absorbed_not_emitted_alone():
    chunks = hierarchical_chunk(_TOC_TEXT, _META)
    for c in chunks:
        assert _body(c) != "48. 119", (
            f"TOC row emitted as a standalone degenerate chunk: {c.text!r}"
        )
    assert any("48. 119" in c.text and "46. 12" in c.text for c in chunks), (
        "TOC run was not merged with its neighbouring rows"
    )


# --- gapped table rows (2026-09-02) ------------------------------------------
# Real PDF-flattened financial-statement tables (docs/status.md 2026-09-02
# scoping entry, SEBI/HO/CFD/PoD2/CIR/P/0155's LODR results-format table)
# interleave a row's own wrapped label between its number and the next row's
# number ("20. Total income from operations\nNet profit for the period\n21.
# before tax...") - the 2026-09-01 fix requires candidates to be strictly
# adjacent, so every row here still ends up a standalone chunk despite being
# genuine table rows. Tolerating up to 2 short, non-heading filler lines
# between same-depth candidates (but not more, and not real prose) closes
# this without touching the per-line candidate predicate that keeps real
# headings safe (see test_genuine_short_heading_run_with_prose_still_splits
# and test_nominee_regression_corpus_unchanged_behaviour below, unaffected).
_GAPPED_TABLE_TEXT = _FILLER + "\n" + (
    "20. Total income from operations\n"
    "Net profit for the period\n"
    "21. before tax and exceptional items\n"
    "Extraordinary items note\n"
    "Continued figures for the year\n"
    "22. after tax and exceptional items"
)


def test_gapped_table_rows_merge_across_short_fillers():
    chunks = hierarchical_chunk(_GAPPED_TABLE_TEXT, _META)
    rows = ["Total income from operations", "before tax and exceptional items",
            "after tax and exceptional items"]
    hosts = {c.id for c in chunks if any(r in c.text for r in rows)}
    assert len(hosts) == 1, (
        f"gapped table rows scattered across {len(hosts)} chunks instead of "
        f"merged into one: {[c.text for c in chunks if c.id in hosts]!r}"
    )
    for c in chunks:
        assert _body(c) != "20. Total income from operations", (
            f"table row emitted as a standalone chunk despite a mergeable gap: {c.text!r}"
        )


# A gap of 3+ filler lines is NOT tolerated - the run must break there rather
# than reach further than the design's stated limit (docs/status.md's
# 2026-09-02 entry documents this exact limitation on the real financial
# table, where the row-4->row-5 transition has 3 fillers).
_OVER_GAPPED_TABLE_TEXT = _FILLER + "\n" + (
    "30. First row label\n"
    "one gap line\n"
    "31. Second row label\n"
    "another gap line\n"
    "yet another gap line\n"
    "32. Third row label\n"
    "gap line one\n"
    "gap line two\n"
    "gap line three\n"
    "33. Fourth row label\n"
    "one gap line\n"
    "34. Fifth row label\n"
    "another gap line\n"
    "yet another gap line\n"
    "35. Sixth row label"
)


def test_table_run_does_not_bridge_a_three_line_gap():
    chunks = hierarchical_chunk(_OVER_GAPPED_TABLE_TEXT, _META)
    first_half = {c.id for c in chunks
                  if any(s in c.text for s in ("First row label", "Second row label", "Third row label"))}
    second_half = {c.id for c in chunks
                   if any(s in c.text for s in ("Fourth row label", "Fifth row label", "Sixth row label"))}
    assert len(first_half) == 1, (
        f"rows 30-32 (no gap between them) should merge into one chunk, got "
        f"{len(first_half)}: {[c.text for c in chunks if c.id in first_half]!r}"
    )
    assert len(second_half) == 1, (
        f"rows 33-35 (no gap between them) should merge into one chunk, got "
        f"{len(second_half)}: {[c.text for c in chunks if c.id in second_half]!r}"
    )
    assert first_half.isdisjoint(second_half), (
        "run bridged the 3-line gap it should not tolerate: "
        f"{[c.text for c in chunks if c.id in first_half | second_half]!r}"
    )
