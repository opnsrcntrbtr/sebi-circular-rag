from pathlib import Path

from sebi_rag.verify_master import (diff_manifest, parse_listing, render_markdown,
                                    summarize, write_reports)

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


def _row(url="https://www.sebi.gov.in/legal/master-circulars/jun-2026/a_1.html",
         date="2026-06-10", title="Master Circular for Depositories"):
    return {"listing_date": date, "detail_url": url, "title": title}


def _rec(url, number="SEBI/HO/MRD/2026/1", date="2026-06-10", chars=5000):
    return {"source_url": url, "circular_number": number, "issue_date": date,
            "subject": "Master Circular for Depositories", "text": "x" * chars,
            "circular_type": "MASTER_CIRCULAR", "validity_status": "current"}


def test_diff_statuses():
    m = [
        _row(),                                                    # ingested_ok
        _row("https://www.sebi.gov.in/legal/master-circulars/a_2.html"),  # parse_failed
        _row("https://www.sebi.gov.in/legal/master-circulars/a_3.html"),  # fetched_not_ingested
        _row("https://www.sebi.gov.in/legal/master-circulars/a_4.html"),  # unfetchable
        _row("https://www.sebi.gov.in/legal/master-circulars/a_5.html"),  # missing
    ]
    m[2]["pdf_url"] = "https://www.sebi.gov.in/sebi_data/attachdocs/9876.pdf"
    corpus = [
        _rec(m[0]["detail_url"]),
        _rec(m[1]["detail_url"], number="SEBI/HO/MRD/2026/2", chars=100),  # degenerate
        _rec("https://www.sebi.gov.in/legal/master-circulars/old_9.html",
             number="SEBI/HO/OLD/2020/9"),                         # extra_in_corpus
    ]
    d = diff_manifest(m, corpus, raw_pdf_stems=frozenset({"9876"}),
                      exceptions={m[3]["detail_url"]: "404 on SEBI side"},
                      dist_numbers={"SEBI/HO/MRD/2026/1"})
    by_url = {x["detail_url"]: x for x in d}
    assert by_url[m[0]["detail_url"]]["status"] == "ingested_ok"
    assert by_url[m[0]["detail_url"]]["in_dist"] is True
    assert by_url[m[1]["detail_url"]]["status"] == "parse_failed"
    assert by_url[m[1]["detail_url"]]["validation"]["degenerate_text"] is True
    assert by_url[m[2]["detail_url"]]["status"] == "fetched_not_ingested"
    assert by_url[m[3]["detail_url"]]["status"] == "unfetchable"
    assert by_url[m[3]["detail_url"]]["reason"] == "404 on SEBI side"
    assert by_url[m[4]["detail_url"]]["status"] == "missing"
    assert by_url["https://www.sebi.gov.in/legal/master-circulars/old_9.html"][
        "status"] == "extra_in_corpus"


def test_summarize_and_markdown():
    m = [_row(), _row("https://www.sebi.gov.in/legal/master-circulars/a_5.html",
                      date="2024-05-01")]
    d = diff_manifest(m, [_rec(m[0]["detail_url"])])
    s = summarize(d)
    assert s["listed_total"] == 2
    assert s["status_counts"] == {"ingested_ok": 1, "missing": 1}
    assert s["coverage_pct"] == 50.0        # of retrievable (no unfetchables)
    assert s["by_year"] == {"2026": {"listed": 1, "ingested_ok": 1},
                            "2024": {"listed": 1, "ingested_ok": 0}}
    assert s["gaps"][0]["detail_url"].endswith("a_5.html")
    md = render_markdown(s)
    assert "50.0%" in md and "missing" in md


def test_coverage_pct_excludes_unfetchable():
    m = [_row(), _row("https://www.sebi.gov.in/legal/master-circulars/a_4.html")]
    d = diff_manifest(m, [_rec(m[0]["detail_url"])],
                      exceptions={m[1]["detail_url"]: "dead link"})
    assert summarize(d)["coverage_pct"] == 100.0


def test_write_reports(tmp_path):
    d = diff_manifest([_row()], [_rec(_row()["detail_url"])])
    jp, mp = write_reports(summarize(d), tmp_path)
    assert jp.name == "master_coverage.json" and mp.name == "master_coverage.md"
    import json as _json
    assert _json.loads(jp.read_text())["coverage_pct"] == 100.0
