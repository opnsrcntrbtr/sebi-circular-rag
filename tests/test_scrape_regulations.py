"""Offline tests for the regulation listing parser (no network).

Fixture `regulation_listing.html` is a real capture of
https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=3&smid=0
taken 2026-07-22, containing exactly 42 in-force regulations.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scrape_regulations as S  # noqa: E402

FIXTURE = (Path(__file__).parent / "fixtures" / "regulation_listing.html"
           ).read_text(encoding="utf-8", errors="ignore")


def test_listing_parses_all_forty_two_rows():
    rows = S.parse_listing(FIXTURE)
    assert len(rows) == 42


def test_rows_carry_year_url_and_title():
    rows = S.parse_listing(FIXTURE)
    for r in rows:
        assert isinstance(r["year"], int) and 1990 <= r["year"] <= 2030
        assert r["url"].startswith("https://www.sebi.gov.in/legal/regulations/")
        assert r["url"].endswith(".html")
        assert r["title"]


def test_year_comes_from_the_issued_year_column_not_the_title():
    # FPI Regs 2019 sits in the jul-2026 folder with a 2026 amendment date;
    # its year must still be 2019.
    rows = S.parse_listing(FIXTURE)
    fpi = [r for r in rows if "Foreign Portfolio Investors" in r["title"]]
    assert fpi and fpi[0]["year"] == 2019


def test_every_row_yields_a_short_name():
    rows = S.parse_listing(FIXTURE)
    missing = [r["title"] for r in rows if not r["short_name"]]
    assert missing == []


def test_short_name_extraction():
    assert S.short_name_of(
        "Securities and Exchange Board of India (Mutual Funds) Regulations, 2026"
        " [Last amended on July 7, 2026]") == "Mutual Funds"


def test_short_name_survives_regulations_inside_the_parenthetical():
    assert S.short_name_of(
        "Securities and Exchange Board of India (Procedure for making, amending"
        " and reviewing of Regulations) Regulations, 2025"
    ) == "Procedure for making, amending and reviewing of Regulations"


def test_short_name_without_a_sebi_prefix():
    # Made under the Securities Contracts (Regulation) Act, so the title has
    # two bracket groups and no SEBI prefix. The LAST group is the short name.
    assert S.short_name_of(
        "Securities Contracts (Regulation) (Stock Exchanges and Clearing"
        " Corporations) Regulations, 2018 [Last amended on November 22, 2025]"
    ) == "Stock Exchanges and Clearing Corporations"


def test_short_name_with_curly_braces_and_nested_parens():
    assert S.short_name_of(
        "Securities and Exchange Board of India {KYC (Know Your Client)"
        " Registration Agency} Regulations, 2011 [Last amended on February 10,"
        " 2025]") == "KYC (Know Your Client) Registration Agency"


def test_short_name_is_none_when_no_bracket_group_precedes_regulations():
    assert S.short_name_of("An Act With No Bracketed Short Name, 2018") is None


def test_last_amended_standard_form():
    assert S.parse_last_amended(
        "SEBI (Mutual Funds) Regulations, 2026 [Last amended on July 7, 2026]"
    ) == "2026-07-07"


def test_last_amended_tolerates_real_source_typos():
    # All four variants occur verbatim in the live listing.
    assert S.parse_last_amended(
        "X Regulations, 2019 [Last amended on on July 07, 2026]") == "2026-07-07"
    assert S.parse_last_amended(
        "X Regulations, 2015 [Last amendment on July 08, 2026]") == "2026-07-08"
    assert S.parse_last_amended(
        "X Regulations, 2021 [amended as on January 21, 2026]") == "2026-01-21"
    assert S.parse_last_amended(
        "X Regulations, 2011 [Last amended on Last amended on December 5, 2025]"
    ) == "2025-12-05"


def test_last_amended_is_none_when_absent():
    assert S.parse_last_amended("SEBI (Stock Brokers) Regulations, 2026") is None


def test_exactly_four_fixture_rows_have_no_amendment_date():
    rows = S.parse_listing(FIXTURE)
    assert sum(r["last_amended"] is None for r in rows) == 4


def test_reg_ids_from_the_fixture_are_unique():
    from sebi_rag.regulations import reg_id
    rows = S.parse_listing(FIXTURE)
    ids = [reg_id(r["short_name"], r["year"]) for r in rows]
    assert len(set(ids)) == len(ids)


def test_empty_listing_parses_to_empty_list_not_an_error():
    assert S.parse_listing("<html><body>nothing</body></html>") == []
