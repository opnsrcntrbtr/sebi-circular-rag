"""Offline tests for the chunk-quality-metric detectors (2026-09-15,
docs/superpowers/specs/2026-09-03-chunk-quality-metric-prereg.md).

Detector logic is deliberately independent of segment.py's own
_is_table_row_candidate/_is_table_row_filler - reusing the production
discriminator to validate itself would be circular (a chunk that dodges the
discriminator by construction would also dodge a detector built from the
same predicate, per the spec's §1).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from analysis.chunk_quality_metric import (  # noqa: E402
    compute_rates,
    is_interleaved_split,
    is_orphan_fragment,
    is_shredded_row_stub,
)

_HEADER = "SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123 | Some Subject | section"


def _chunk(body: str) -> str:
    """Mirrors chunks.jsonl's own text shape: "header\\n\\nbody"."""
    return f"{_HEADER}\n\n{body}"


# ---------------------------------------------------------------------------
# is_shredded_row_stub
# ---------------------------------------------------------------------------

def test_bare_numbered_marker_is_a_shredded_stub():
    """A lone '5.' left behind when a table row's label/value landed in a
    separate chunk from its number - the failure shape named in the spec."""
    assert is_shredded_row_stub(_chunk("5.")) is True


def test_numbered_marker_with_trailing_whitespace_is_still_a_stub():
    assert is_shredded_row_stub(_chunk("12.\n")) is True


def test_numbered_row_with_substantive_content_is_not_a_stub():
    assert is_shredded_row_stub(_chunk("5. Total income from operations")) is False


def test_ordinary_prose_paragraph_is_not_a_stub():
    assert is_shredded_row_stub(_chunk(
        "The registered intermediary shall maintain records of all "
        "transactions for a period of five years from the date of execution."
    )) is False


def test_empty_body_is_not_a_stub():
    assert is_shredded_row_stub(_chunk("")) is False


# ---------------------------------------------------------------------------
# is_orphan_fragment
# ---------------------------------------------------------------------------

def test_title_continuation_with_no_numbered_marker_is_an_orphan():
    """The TOC-wrapped-title failure shape: a label/title fragment whose
    owning numbered row landed in a different chunk."""
    assert is_orphan_fragment(_chunk(
        "Admission of Limited Liability Partnerships as Members of Stock\nExchanges"
    )) is True


def test_numbered_row_owns_its_own_marker_not_an_orphan():
    assert is_orphan_fragment(_chunk("5. Total income from operations")) is False


def test_year_prefixed_citation_fragment_is_not_an_orphan():
    """Found live in the 2026-09-16 hand-labeling sample: a leading 4-digit
    year ('2011.', '1995.') is ordinary citation/reference prose, not a
    title-continuation fragment missing its row number - the original
    \\d{1,3} marker check didn't recognize a year as 'this line already has
    its own marker', over-flagging every short year-prefixed sentence."""
    assert is_orphan_fragment(_chunk(
        "2011. approval to members of Stock"
    )) is False
    assert is_orphan_fragment(_chunk("1995. businesses.")) is False


def test_circular_preamble_boilerplate_is_not_an_orphan():
    """Found live in the same sample: every document's opening
    'CIRCULAR\\n<id> <date>\\nTo,' chunk was flagged as an orphan fragment -
    it's short and has no leading numbered-row marker, but it's ordinary
    document-header boilerplate, not shredding."""
    assert is_orphan_fragment(_chunk(
        "CIRCULAR\nSEBI/HO/MIRSD/DOP/P/CIR/2021/607 July 30, 2021\nTo,"
    )) is False
    assert is_orphan_fragment(_chunk(
        "MASTER CIRCULAR\nSEBI/HO/MIRSD/MIRSDSECFATF/P/CIR/2024/78 June 06, 2024\nTo,"
    )) is False


def test_long_ordinary_prose_is_not_an_orphan():
    assert is_orphan_fragment(_chunk(
        "The registered intermediary shall maintain records of all "
        "transactions for a period of five years from the date of execution, "
        "and shall make such records available to the Board upon request "
        "within a reasonable time as prescribed under the applicable regulations."
    )) is False


def test_empty_body_is_not_an_orphan():
    assert is_orphan_fragment(_chunk("")) is False


def test_a_shredded_stub_is_not_also_an_orphan():
    """The two detectors target different failure shapes - a bare numbered
    stub (owns a marker, no body) should not double-count as a title
    continuation (no marker, is body)."""
    assert is_orphan_fragment(_chunk("5.")) is False


# ---------------------------------------------------------------------------
# is_interleaved_split (2026-09-16, added after live hand-labeling found the
# real confirmed defect is neither of the two originally-scoped whole-chunk
# shapes)
# ---------------------------------------------------------------------------

def test_real_confirmed_example_from_sebi_ho_ddhs_cir_2021_0000000637():
    """The actual defect: a single chunk containing many numbered rows, most
    clean, but row 7's wrapped label got split by its own bare marker landing
    between the two halves ('Reserves (excluding Revaluation' / '7.' /
    'Reserve)') - chunk id SEBI/HO/DDHS/CIR/2021/0000000637#5. (Loss) for the
    period (after tax) and#10, found live in the 2026-09-16 hand-labeling
    pass. Neither is_shredded_row_stub nor is_orphan_fragment can see this:
    the chunk has substantial real content (not a bare stub) and starts with
    its own leading marker '5.' (not an orphan)."""
    body = (
        "5. (Loss) for the period (after tax) and\n"
        "Other Comprehensive Income\n"
        "(after tax)]\n"
        "6. Paid up Equity Share Capital\n"
        "Reserves (excluding Revaluation\n"
        "7.\n"
        "Reserve)\n"
        "8. Securities Premium Account\n"
        "9. Net worth\n"
        "Paid up Debt Capital/ Outstanding\n"
        "10.\n"
        "Debt\n"
        "Outstanding Redeemable\n"
        "11.\n"
        "Preference Shares\n"
        "12. Debt Equity Ratio"
    )
    assert is_interleaved_split(_chunk(body)) is True
    # Sanity: the original two detectors correctly do NOT fire on this chunk -
    # confirms the redesign was necessary, not merely additive.
    assert is_shredded_row_stub(_chunk(body)) is False
    assert is_orphan_fragment(_chunk(body)) is False


def test_clean_numbered_list_has_no_interleaved_split():
    """Every row owns its label on the same line - nothing to detect."""
    body = (
        "6. Paid up Equity Share Capital\n"
        "8. Securities Premium Account\n"
        "9. Net worth\n"
        "12. Debt Equity Ratio"
    )
    assert is_interleaved_split(_chunk(body)) is False


def test_bare_marker_between_two_complete_sentences_is_not_a_split():
    """A bare numbered heading between two SELF-CONTAINED lines (the prior
    line ends with terminal punctuation, so it isn't a dangling label half)
    is an ordinary heading, not an interleaved split."""
    body = (
        "This clause is now in force.\n"
        "7.\n"
        "5. A new sub-clause begins here."
    )
    assert is_interleaved_split(_chunk(body)) is False


def test_single_line_body_has_no_interleaved_split():
    assert is_interleaved_split(_chunk("5. Total income from operations")) is False


def test_empty_body_has_no_interleaved_split():
    assert is_interleaved_split(_chunk("")) is False


# ---------------------------------------------------------------------------
# compute_rates
# ---------------------------------------------------------------------------

def test_compute_rates_counts_all_three_detectors(tmp_path):
    chunks = tmp_path / "chunks.jsonl"
    rows = [
        {"text": _chunk("5.")},                              # shredded stub
        {"text": _chunk("Admission of Limited Liability\nPartnerships")},  # orphan
        {"text": _chunk(
            "6. Paid up Equity Share Capital\n"
            "Reserves (excluding Revaluation\n7.\nReserve)\n"
            "8. Securities Premium Account"
        )},                                                   # interleaved split
        {"text": _chunk("5. Total income from operations")},  # clean, none of the three
    ]
    chunks.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    rates = compute_rates(chunks)

    assert rates["total_chunks"] == 4
    assert rates["shredded_row_count"] == 1
    assert rates["orphan_fragment_count"] == 1
    assert rates["interleaved_split_count"] == 1
    assert rates["interleaved_split_rate"] == 0.25


# ---------------------------------------------------------------------------
# is_interleaved_split false-positive fixes, found live in the 2026-09-16
# hand-labeling pass over 117 real detector positives (raw precision 0.872,
# 15/117 false positives; these 3 patterns account for 8 of the 15 and have a
# clean, well-evidenced rule - the remaining 7 are genuinely ambiguous)
# ---------------------------------------------------------------------------

def test_currency_amount_is_not_an_interleaved_split():
    """'Rs 150.' is a rupee amount, not a row marker - found in
    'This allocation shall not be permitted since Cli-1 has a margin
    requirement of Rs\\n150.\\n299' (a page number, not a continuation)."""
    body = (
        "This allocation shall not be permitted since Cli-1 has a margin "
        "requirement of Rs\n150.\n299"
    )
    assert is_interleaved_split(_chunk(body)) is False


def test_consecutive_complete_items_are_not_an_interleaved_split():
    """Item 8 is already complete and self-numbered on its own line; item 9
    beginning normally on the next line is ordinary sequential numbering, not
    item 8's label split by item 9's marker. Found in '8. Implementation of
    GRC Order...\\n9.\\nIn case the stock broker is aggrieved by'."""
    body = (
        "8. Implementation of GRC Order. On receipt of GRC Order, if\n"
        "9.\n"
        "In case the stock broker is aggrieved by"
    )
    assert is_interleaved_split(_chunk(body)) is False


def test_date_fragment_is_not_an_interleaved_split():
    """'ending March' / '31.' / new paragraph - '31' is the day-of-month in
    a date ('March 31'), not a row marker. Found in 'calendar days from the
    end of every financial year ending March\\n31.\\n98 Master Circular for
    Mutual Funds'."""
    body = (
        "calendar days from the end of every financial year ending March\n"
        "31.\n"
        "98 Master Circular for Mutual Funds"
    )
    assert is_interleaved_split(_chunk(body)) is False


def test_real_confirmed_example_still_detected_after_the_three_fixes():
    """Regression guard: the three false-positive fixes above must not
    suppress the actual confirmed defect this detector exists to catch."""
    body = (
        "5. (Loss) for the period (after tax) and\n"
        "Other Comprehensive Income\n"
        "(after tax)]\n"
        "6. Paid up Equity Share Capital\n"
        "Reserves (excluding Revaluation\n"
        "7.\n"
        "Reserve)\n"
        "8. Securities Premium Account"
    )
    assert is_interleaved_split(_chunk(body)) is True


def test_compound_clause_number_does_not_suppress_a_real_split():
    """Found live in the recall-check pass (2026-09-16): the 'prev already
    has its own marker' exclusion (added to fix the item-8/9 false positive)
    was too broad - it also matched a compound sub-clause number like
    '42.43' (a clause reference, not a row marker) and silently suppressed a
    genuine Annexure-reference split. '42.43 Illustration...' is NOT a
    simple 'N. text' item the way '8. Implementation...' is - the '.43'
    immediately after the first period means this is clause 42, sub-point
    43, not a self-numbered list item."""
    body = (
        "42.43 Illustration on procedures to be followed in Stage-4 are "
        "provided at Annexure-\n"
        "22.\n"
        "Default of TMs to CMs"
    )
    assert is_interleaved_split(_chunk(body)) is True
