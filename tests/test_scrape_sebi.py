"""Offline tests for the SEBI scraper parsing / pagination logic (no network)."""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scrape_sebi as S  # noqa: E402

A = "https://www.sebi.gov.in/legal/circulars/jun-2026/a_1.html"
B = "https://www.sebi.gov.in/legal/circulars/may-2025/b_2.html"
C = "https://www.sebi.gov.in/legal/circulars/jan-2024/c_3.html"


def _row(date_str, url):
    return f'<tr><td>{date_str}</td><td><a href="{url}">t</a></td></tr>'


def test_circular_href_matches_both_kinds():
    html = (f'<a href="{A}">x</a> '
            '<a href="https://www.sebi.gov.in/legal/master-circulars/jun-2026/m_9.html">m</a> '
            '<a href="https://www.sebi.gov.in/enforcement/orders/may-2026/z_1.html">skip</a>')
    urls = S.CIRCULAR_HREF.findall(html)
    assert A in urls and any("master-circulars" in u for u in urls)
    assert not any("enforcement" in u for u in urls)


def test_parse_rows_pairs_date_and_url():
    html = _row("Jun 24, 2026", A) + _row("May 01, 2025", B)
    rows = S.parse_rows(html)
    assert rows[0] == (dt.date(2026, 6, 24), A)
    assert rows[1] == (dt.date(2025, 5, 1), B)


def test_discover_applies_date_filter(monkeypatch):
    page0 = _row("Jun 24, 2026", A) + _row("May 01, 2025", B) + _row("Jan 01, 2024", C)
    monkeypatch.setattr(S, "_page",
                        lambda sid, ssid, smid, page, rate: page0.encode() if page == 0 else b"")
    monkeypatch.setattr(S.time, "sleep", lambda s: None)
    out = S.discover("circulars", 99, 0.0, date_from=dt.date(2025, 1, 1))
    assert A in out and B in out and C not in out   # 2024 filtered out


def test_discover_graceful_on_fetch_error(monkeypatch):
    page0 = _row("Jun 24, 2026", A) + _row("Jun 20, 2026", B)

    def fake_page(sid, ssid, smid, page, rate):
        if page == 0:
            return page0.encode()
        raise RuntimeError("HTTP Error 530: BLOCKED")

    monkeypatch.setattr(S, "_page", fake_page)
    monkeypatch.setattr(S.time, "sleep", lambda s: None)
    out = S.discover("circulars", 99, 0.0)
    assert A in out and B in out          # page-0 results kept, no crash


def test_discover_no_advance_guard_stops(monkeypatch):
    same = _row("Jun 24, 2026", A)
    monkeypatch.setattr(S, "_page", lambda sid, ssid, smid, page, rate: same.encode())
    monkeypatch.setattr(S.time, "sleep", lambda s: None)
    out = S.discover("circulars", 99, 0.0)
    assert out == [A]   # page 1 repeats page 0 -> stop, no infinite loop


# --- extract_pdf_urls (viewer-aware PDF extraction, 2026 SEBI migration) ---

DETAIL = "https://www.sebi.gov.in/legal/circulars/jul-2026/some-slug_102639.html"
PDF_NEW = "https://www.sebi.gov.in/sebi_data/attachdocs/jul-2026/1783423471963.pdf"
PDF_ANNEX = "https://www.sebi.gov.in/sebi_data/attachdocs/jul-2026/222.pdf"
IFRAME_LIVE = ("<iframe src='../../../web/?file=" + PDF_NEW +
               "' width='100%' style='height:600px;' title=\"t\" allowfullscreen>")


def test_extract_viewer_absolute_target():
    # Live shape as of 2026-07-09: absolute URL inside single-quoted iframe src
    assert S.extract_pdf_urls(IFRAME_LIVE, DETAIL) == [PDF_NEW]


def test_extract_viewer_relative_target():
    html = "<iframe src='../../../web/?file=/sebi_data/attachdocs/jul-2026/1783423471963.pdf'>"
    assert S.extract_pdf_urls(html, DETAIL) == [PDF_NEW]


def test_extract_viewer_urlencoded_target():
    html = ("<iframe src='../../../web/?file=https%3A%2F%2Fwww.sebi.gov.in%2Fsebi_data"
            "%2Fattachdocs%2Fjul-2026%2F1783423471963.pdf'>")
    assert S.extract_pdf_urls(html, DETAIL) == [PDF_NEW]


def test_extract_anchor_absolute_and_relative():
    html = (f'<a href="{PDF_NEW}">pdf</a> '
            '<a href="/sebi_data/attachdocs/jul-2026/222.pdf">annex</a>')
    assert S.extract_pdf_urls(html, DETAIL) == [PDF_NEW, PDF_ANNEX]


def test_extract_multi_pdf_order_and_dedupe():
    html = IFRAME_LIVE + f'<a href="{PDF_ANNEX}">a</a><a href="{PDF_NEW}">dup</a>'
    assert S.extract_pdf_urls(html, DETAIL) == [PDF_NEW, PDF_ANNEX]


def test_extract_fallback_regex_scan():
    # URL appears only in a script block, not in any src/href attribute
    html = f'<script>var u = "{PDF_NEW}";</script>'
    assert S.extract_pdf_urls(html, DETAIL) == [PDF_NEW]


def test_extract_excludes_off_origin():
    html = '<a href="https://evil.example.com/x.pdf">x</a>'
    assert S.extract_pdf_urls(html, DETAIL) == []


def test_extract_no_pdf_returns_empty():
    assert S.extract_pdf_urls("<p>nothing here</p>", DETAIL) == []


def test_pdf_url_for_returns_first_or_none(monkeypatch):
    html = IFRAME_LIVE + f'<a href="{PDF_ANNEX}">a</a>'
    monkeypatch.setattr(S, "fetch", lambda url, rate, **kw: html.encode())
    assert S.pdf_url_for(DETAIL, 0.0) == PDF_NEW
    monkeypatch.setattr(S, "fetch", lambda url, rate, **kw: b"<p>no pdf</p>")
    assert S.pdf_url_for(DETAIL, 0.0) is None
