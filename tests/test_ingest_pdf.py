"""Validate the local PDF ingestion path with a synthetic circular PDF."""
from __future__ import annotations

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from sebi_rag.ingest_pdf import ingest, parse_meta


def _make_pdf(path):
    c = canvas.Canvas(str(path), pagesize=A4)
    lines = [
        "CIRCULAR",
        "SEBI/HO/TEST/PoD-9/P/CIR/2024/077          March 5, 2024",
        "To, All Listed Entities",
        "Sub: Test circular on illustrative disclosure norms for listed entities",
        "1. This circular refers to Master Circular "
        "SEBI/HO/TEST/PoD2/CIR/P/2024/050 dated January 2, 2024.",
        "2. Listed entities shall comply with the disclosure timelines herein.",
    ]
    y = 800
    for ln in lines:
        c.drawString(40, y, ln)
        y -= 22
    c.save()


def test_ingest_extracts_metadata_and_lineage(tmp_path):
    pdf = tmp_path / "test_circular.pdf"
    _make_pdf(pdf)
    corpus = tmp_path / "corpus.jsonl"

    rec = ingest(pdf, corpus, source_url="https://example.test/circular")
    assert rec["circular_number"] == "SEBI/HO/TEST/PoD-9/P/CIR/2024/077"
    assert rec["issue_date"] == "2024-03-05"
    assert "illustrative disclosure" in rec["subject"].lower()
    assert rec["issuing_department"] == "TEST"
    assert "SEBI/HO/TEST/PoD2/CIR/P/2024/050" in rec["version_lineage"]
    assert rec["source_url"] == "https://example.test/circular"
    assert rec["provenance"].startswith("Parsed from PDF test_circular.pdf")

    # written once; re-ingest is a no-op (dedupe by circular number)
    assert corpus.read_text(encoding="utf-8").strip().count("\n") == 0  # 1 line
    rec2 = ingest(pdf, corpus)
    assert rec2.get("_skipped") == "duplicate"


def test_parse_meta_handles_old_format():
    text = "CIRCULAR CIR/CFD/CMD/4/2015 dated September 9, 2015\nSub: Old format."
    meta = parse_meta(text)
    assert meta["circular_number"] == "CIR/CFD/CMD/4/2015"
    assert meta["issue_date"] == "2015-09-09"


def test_parse_meta_handles_en_dash_in_place_of_slash():
    """A PDF kerning artifact can render the number's own '/' as a typographic
    en-dash with stray spacing (e.g. "IMD-I –PoD1" for "IMD-I/PoD1"). If
    the own-number strategies fail to match, _primary_number's last-resort
    fallback grabs the first CITED reference instead, silently colliding the
    document's stored circular_number with an unrelated circular it cites."""
    text = ("CIRCULAR\nSEBI/HO/IMD/IMD-I –PoD1/P/CIR/2023/125 July 20, 2023\n"
           "To\nAll Mutual Funds\nSub: New category of Mutual Fund schemes.")
    meta = parse_meta(text)
    assert meta["circular_number"] == "SEBI/HO/IMD/IMD-I/PoD1/P/CIR/2023/125"
    assert meta["issue_date"] == "2023-07-20"


def test_parse_meta_handles_2011_mc_number_format():
    """2011-era master circulars use "SEBI/<DEPT>/MC No.<n>/<serial>/<year>",
    matching neither the new SEBI/HO/... nor old CIR/... reference formats."""
    text = ("Deputy General Manager\nInvestment Management Department\n"
           "SEBI/IMD/MC No.2/836/2011\nJanuary 07, 2011\n"
           "All Mutual Funds, Asset Management Companies (AMCs)\nDear Sir/ Madam,\n"
           "Sub: Master Circular for Mutual Funds")
    meta = parse_meta(text)
    assert meta["circular_number"] == "SEBI/IMD/MC No.2/836/2011"
    assert meta["issue_date"] == "2011-01-07"


def test_parse_meta_handles_space_before_year_slash():
    """Old-format PDFs (e.g. CIR/MRD/DP/ 11 /2012) split the number with a
    space BEFORE the year's slash, not just after a slash. Losing the year
    here silently collides two different master circulars under the same
    stored circular_number (e.g. CIR/MRD/DP/11/2012 vs CIR/MRD/DP/11/2014)."""
    text = ("MASTER CIRCULAR\nCIR/MRD/DP/ 11 /2012 April 13, 2012\nTo,\n"
           "All Stock Exchanges\nSub: Master Circular for Stock Exchange / Cash Market")
    meta = parse_meta(text)
    assert meta["circular_number"] == "CIR/MRD/DP/11/2012"
    assert meta["issue_date"] == "2012-04-13"
