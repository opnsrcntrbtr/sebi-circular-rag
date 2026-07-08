"""Regression matrix for SEBI reference-number extraction.

One case per known format family (see docs/superpowers/plans/
2026-07-08-regai-inspired-enhancements.md section B.2). If SEBI invents a
new format, add a row here FIRST, watch it fail, then extend the parser.
"""
import pytest

from sebi_rag.ingest_pdf import REF_RE, _primary_number, parse_meta

# (format family, header text, expected primary number)
HEADER_CASES = [
    ("new-standard", "SEBI/HO/IMD/DF3/CIR/P/2017/114 May 04, 2017",
     "SEBI/HO/IMD/DF3/CIR/P/2017/114"),
    ("old-standard", "CIR/CFD/CMD/4/2015 September 9, 2015",
     "CIR/CFD/CMD/4/2015"),
    ("space-split", "SEBI/HO/DDHS/DDHS-PoD-2/ P/CIR/ 2025/104",
     "SEBI/HO/DDHS/DDHS-PoD-2/P/CIR/2025/104"),
    ("paren-split", "HO/ (79)2026-MIRSD",
     "HO/(79)2026-MIRSD"),
    ("dept-only", "AFD/P/CIR/2022/125 dated October 28, 2022",
     "AFD/P/CIR/2022/125"),
    ("dept-order-2026", "HO/(79)2026-MIRSD",
     "HO/(79)2026-MIRSD"),
    ("free-form-2026", "SEBI/HO/47/17/12(11)2025-MRD-POD3/I/11107/2026",
     "SEBI/HO/47/17/12(11)2025-MRD-POD3/I/11107/2026"),
]


@pytest.mark.parametrize("family,header,expected",
                         HEADER_CASES, ids=[c[0] for c in HEADER_CASES])
def test_primary_number_format_matrix(family, header, expected):
    assert _primary_number(header, full=header) == expected


def test_fulltext_fallback_returns_earliest_body_reference():
    # Pins stage-6 behavior (plan risk R3): with no parseable header token the
    # earliest well-formed reference in the body wins, even though it may be a
    # CITED circular rather than the document's own number. Mitigated by the
    # corpus validation script (Task 10), not by the parser.
    n = _primary_number("Gazette Notification",
                        "…in terms of CIR/MRD/DP/2/2000 read with…")
    assert n == "CIR/MRD/DP/2/2000"


def test_ref_re_matches_all_three_reference_grammars():
    text = ("cites SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123 and CIR/CFD/CMD/4/2015 "
            "and the order HO/(12)2026-MRD.")
    found = {m.group(0) for m in REF_RE.finditer(text)}
    assert found == {"SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123",
                     "CIR/CFD/CMD/4/2015", "HO/(12)2026-MRD"}


def test_parse_meta_dept_order_document_end_to_end():
    text = ("HO/(79)2026-MIRSD\n"
            "February 10, 2026\n"
            "To,\nAll Market Infrastructure Institutions\n"
            "Sub: Departmental reorganisation\n\n"
            "1. In terms of SEBI/HO/MIRSD/CIR/P/2023/50, the following applies.")
    meta = parse_meta(text)
    assert meta["circular_number"] == "HO/(79)2026-MIRSD"
    assert meta["issue_date"] == "2026-02-10"
    assert "SEBI/HO/MIRSD/CIR/P/2023/50" in meta["version_lineage"]


def test_normalize_treats_prefix_and_spacing_variants_as_same():
    from sebi_rag.ingest_pdf import normalize_circular_number as norm
    assert norm("SEBI/HO/MIRSD/CIR/P/2024/10") == norm("HO/MIRSD/CIR/P/2024/10")
    assert norm("CIR/ CFD/CMD/4/2015") == norm("CIR/CFD/CMD/4/2015")
    assert norm("cir/cfd/cmd/4/2015.") == norm("CIR/CFD/CMD/4/2015")
    # different numbers must stay different
    assert norm("CIR/CFD/CMD/4/2015") != norm("CIR/CFD/CMD/5/2015")


def test_dedup_uses_normalized_numbers(tmp_path):
    import json
    from sebi_rag.ingest_pdf import _existing_numbers, normalize_circular_number
    p = tmp_path / "c.jsonl"
    p.write_text(json.dumps({"circular_number": "SEBI/HO/X/CIR/2024/9"}) + "\n",
                 encoding="utf-8")
    assert normalize_circular_number("HO/X/CIR/2024/9") in _existing_numbers(p)


def test_parse_meta_excludes_prefix_variant_self_reference():
    text = ("HO/MIRSD/CIR/P/2024/10\nMarch 01, 2024\nTo,\nAll intermediaries\n"
            "Sub: Something\n\n"
            "1. This circular SEBI/HO/MIRSD/CIR/P/2024/10 shall come into force…")
    meta = parse_meta(text)
    assert meta["version_lineage"] == []  # own number, prefixed variant, excluded
