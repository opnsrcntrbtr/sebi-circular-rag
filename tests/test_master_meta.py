from pathlib import Path

from sebi_rag.master_meta import (annotate_master_fields, consolidation_edges,
                                  master_series)

FIXDIR = Path(__file__).parent / "fixtures"


def _master(n, subj, date):
    return {"circular_number": n, "subject": subj, "issue_date": date,
            "circular_type": "MASTER_CIRCULAR"}


def test_master_series_rule_table():
    assert master_series("Master Circular for Mutual Funds") == "Mutual Funds"
    assert master_series("Master Circular for Depositories") == "Depositories"
    assert master_series("Master Circular for Stock Brokers") == "Stock Brokers"
    assert master_series(
        "Master Circular for Alternative Investment Funds (AIFs)") == "AIFs"
    assert master_series("Master Circular on something novel") is None
    assert master_series(None) is None


def test_annotate_sets_identity_and_chains_editions():
    recs = [
        _master("MF/2023/1", "Master Circular for Mutual Funds", "2023-05-19"),
        _master("MF/2024/2", "Master Circular for Mutual Funds", "2024-06-27"),
        _master("DEP/2024/3", "Master Circular for Depositories", "2024-10-06"),
        {"circular_number": "C/1", "subject": "Nomination", "issue_date":
         "2025-01-10", "circular_type": "CIRCULAR"},
    ]
    changed = annotate_master_fields(recs)
    assert changed == 4
    assert recs[0]["is_master"] and recs[0]["master_edition"] == 2023
    assert recs[0]["previous_edition"] is None
    assert recs[1]["previous_edition"] == "MF/2023/1"     # chained by series+date
    assert recs[2]["previous_edition"] is None            # different series
    assert recs[3] == {**recs[3], "is_master": False, "master_series": None,
                       "master_edition": None, "previous_edition": None}


def test_annotate_idempotent():
    recs = [_master("MF/2023/1", "Master Circular for Mutual Funds", "2023-05-19")]
    annotate_master_fields(recs)
    assert annotate_master_fields(recs) == 0


def test_consolidation_edges_from_real_mf_appendix():
    text = (FIXDIR / "master_appendix_mf.txt").read_text(encoding="utf-8")
    rec = {"circular_number": "SEBI/HO/IMD/IMD-PoD-1/P/CIR/2024/90", "text": text}
    edges = consolidation_edges(rec)
    assert len(edges) >= 5
    e = edges[0]
    assert e["source"] == "SEBI/HO/IMD/IMD-PoD-1/P/CIR/2024/90"
    assert e["relation"] == "consolidates"
    assert e["confidence"] == "explicit_text"
    assert e["evidence"] == "rescission_appendix"
    targets = [e["target"] for e in edges]
    assert len(targets) == len(set(targets))
    assert rec["circular_number"] not in targets
    assert any("2023/152" in t for t in targets)  # real Sr.No.3 citation


def test_consolidation_edges_from_real_dep_appendix():
    text = (FIXDIR / "master_appendix_dep.txt").read_text(encoding="utf-8")
    rec = {"circular_number": "SEBI/HO/MRD/MRD-PoD-1/P/CIR/2024/168", "text": text}
    edges = consolidation_edges(rec)
    assert len(edges) >= 5
    targets = [e["target"] for e in edges]
    assert len(targets) == len(set(targets))
    assert rec["circular_number"] not in targets
    assert any("CIR/MRD/DMS/13/2010" in t for t in targets)


def test_consolidation_edges_from_real_pre2015_appendix():
    text = (FIXDIR / "master_appendix_pre2015.txt").read_text(encoding="utf-8")
    rec = {"circular_number": "CIR/MRD/DP/11/2014", "text": text}
    edges = consolidation_edges(rec)
    assert len(edges) >= 5
    targets = [e["target"] for e in edges]
    assert len(targets) == len(set(targets))
    assert rec["circular_number"] not in targets
    assert any("CIR/MRD/DP/19/2010" in t for t in targets)


def test_no_edges_without_rescission_heading():
    rec = {"circular_number": "X/1",
           "text": "This circular references SEBI/HO/MRD/2020/12 in passing. " * 20}
    assert consolidation_edges(rec) == []


def test_no_edges_for_empty_text():
    assert consolidation_edges({"circular_number": "X/1", "text": ""}) == []
