"""Citation extraction from circular text (spec 2026-07-23 §3.3)."""
from sebi_rag.reg_citations import EVIDENCE_TIERS, Citation, extract_citations


def test_extracts_full_title_and_year():
    text = ("Disclosure under Securities and Exchange Board of India "
            "(Listing Obligations and Disclosure Requirements) Regulations, 2015.")
    cits = extract_citations("", text)
    assert len(cits) == 1
    assert cits[0].name == "Listing Obligations and Disclosure Requirements"
    assert cits[0].year == 2015


def test_extracts_sebi_short_form_and_acronyms():
    cits = extract_citations("", "as required by SEBI (PIT) Regulations, 2015.")
    assert [(c.name, c.year) for c in cits] == [("PIT", 2015)]


def test_year_without_comma_is_extracted():
    cits = extract_citations("", "under SEBI (Buy-back of Securities) Regulations 2018.")
    assert [(c.name, c.year) for c in cits] == [("Buy-back of Securities", 2018)]


def test_subject_line_citation_outranks_body():
    subject = "Amendment to SEBI (Mutual Funds) Regulations, 1996"
    text = "Something else entirely."
    cits = extract_citations(subject, text)
    assert cits[0].evidence == "subject_line"


def test_powers_clause_evidence_tier():
    text = ("In exercise of the powers conferred under section 11 read with "
            "SEBI (Credit Rating Agencies) Regulations, 1999, the Board directs.")
    cits = extract_citations("", text)
    assert cits[0].evidence == "powers_clause"


def test_plain_body_mention_is_body_text():
    text = "Reference is drawn to SEBI (Research Analysts) Regulations, 2014."
    cits = extract_citations("", text)
    assert cits[0].evidence == "body_text"


def test_clause_captured_when_same_sentence():
    text = ("Disclosure under Regulation 30(2) of SEBI (Listing Obligations "
            "and Disclosure Requirements) Regulations, 2015 is mandatory.")
    cits = extract_citations("", text)
    assert cits[0].clause == "30(2)"


def test_clause_not_captured_across_sentence_boundary():
    text = ("Regulation 30(2) sets the timeline. Separately, SEBI (Mutual "
            "Funds) Regulations, 2026 apply to schemes.")
    cits = extract_citations("", text)
    assert len(cits) == 1
    assert cits[0].clause is None


def test_four_digit_year_is_never_mistaken_for_a_clause():
    # "Regulations 2018" (no comma) must not yield clause="2018".
    text = "under SEBI (Buy-back of Securities) Regulations 2018, issuers shall."
    cits = extract_citations("", text)
    assert cits[0].clause is None


def test_alphanumeric_clause_is_captured():
    text = ("Under regulation 30A of SEBI (Listing Obligations and Disclosure "
            "Requirements) Regulations, 2015 the entity shall disclose.")
    cits = extract_citations("", text)
    assert cits[0].clause == "30A"


def test_multiple_distinct_regulations_in_one_document():
    text = ("Read SEBI (Mutual Funds) Regulations, 1996 together with "
            "SEBI (Alternative Investment Funds) Regulations, 2012.")
    cits = extract_citations("", text)
    assert {(c.name, c.year) for c in cits} == {
        ("Mutual Funds", 1996), ("Alternative Investment Funds", 2012)}


def test_repeated_mentions_yield_one_citation_each():
    text = ("SEBI (Mutual Funds) Regulations, 1996 applies. "
            "See SEBI (Mutual Funds) Regulations, 1996 again.")
    cits = extract_citations("", text)
    assert len(cits) == 2
    assert all(c.name == "Mutual Funds" for c in cits)


def test_parenthetical_containing_the_word_regulations_is_handled():
    # Real listing entry: "(Procedure for making, amending and reviewing of
    # Regulations) Regulations, 2025" — the word appears inside the bracket.
    text = ("per SEBI (Procedure for making, amending and reviewing of "
            "Regulations) Regulations, 2025.")
    cits = extract_citations("", text)
    assert cits[0].name == "Procedure for making, amending and reviewing of Regulations"
    assert cits[0].year == 2025


def test_no_citation_returns_empty_list():
    assert extract_citations("", "A circular with no statutory reference.") == []


def test_whitespace_in_name_is_collapsed():
    text = "SEBI (Mutual   \n Funds) Regulations, 1996 applies."
    cits = extract_citations("", text)
    assert cits[0].name == "Mutual Funds"


def test_evidence_tiers_are_in_precedence_order():
    assert EVIDENCE_TIERS == ("subject_line", "powers_clause", "body_text")


def test_citation_is_hashable():
    c = Citation(name="Mutual Funds", year=1996, clause=None, evidence="body_text")
    assert len({c, c}) == 1
