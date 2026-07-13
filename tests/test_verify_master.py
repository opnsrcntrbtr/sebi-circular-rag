from pathlib import Path

from sebi_rag.verify_master import parse_listing

FIXTURE = Path(__file__).parent / "fixtures" / "master_listing_page0.html"


def test_parse_listing_extracts_rows_from_real_page():
    rows = parse_listing(FIXTURE.read_text(encoding="utf-8", errors="ignore"))
    assert len(rows) >= 20
    first = rows[0]
    assert set(first) == {"listing_date", "detail_url", "title"}
    assert first["detail_url"].startswith(
        "https://www.sebi.gov.in/legal/master-circulars/")
    assert "master circular" in first["title"].lower()
    assert first["listing_date"] and len(first["listing_date"]) == 10


def test_parse_listing_dedupes_and_ignores_non_master_links():
    html = (
        '<tr><td>Jun 10, 2026</td><td><a href='
        '"https://www.sebi.gov.in/legal/master-circulars/jun-2026/x_100.html">'
        'Master Circular for Depositories</a></td></tr>'
        '<tr><td>Jun 10, 2026</td><td><a href='
        '"https://www.sebi.gov.in/legal/master-circulars/jun-2026/x_100.html">'
        'Master Circular for Depositories</a></td></tr>'
        '<a href="https://www.sebi.gov.in/legal/circulars/jun-2026/y_1.html">c</a>'
    )
    rows = parse_listing(html)
    assert len(rows) == 1
    assert rows[0] == {
        "listing_date": "2026-06-10",
        "detail_url": "https://www.sebi.gov.in/legal/master-circulars/jun-2026/x_100.html",
        "title": "Master Circular for Depositories",
    }


def test_parse_listing_empty_html():
    assert parse_listing("") == []
