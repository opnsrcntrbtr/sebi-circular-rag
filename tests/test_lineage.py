"""P2 lineage / supersession resolution tests."""
from __future__ import annotations

from pathlib import Path

from sebi_rag.lineage import (
    Lineage,
    build_lineage,
    demote_superseded,
    detect_relations,
    load_records,
    superseded_citations,
)
from sebi_rag.segment import Chunk

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"

A = "SEBI/HO/X/P/CIR/2020/01"
B = "SEBI/HO/X/P/CIR/2024/99"


def test_supersession_detected_from_text():
    records = [
        {"circular_number": A, "text": f"CIRCULAR {A} dated Jan 1, 2020. Norms."},
        {"circular_number": B, "text": (
            f"CIRCULAR {B} dated Feb 2, 2024. This circular supersedes earlier "
            f"circulars. In supersession of {A} dated Jan 1, 2020, the following "
            "norms apply.")},
    ]
    lin = build_lineage(records)
    assert lin.supersedes.get(B) == [A]
    assert lin.superseded_by.get(A) == [B]
    assert lin.status(A) == "superseded"
    assert lin.status(B) == "in_force"


def test_superseded_citations_flagged_for_retrieval():
    records = [
        {"circular_number": A, "text": f"CIRCULAR {A}. Original norms."},
        {"circular_number": B, "text": (
            f"CIRCULAR {B}. This circular supersedes. In supersession of {A}, "
            "revised norms apply.")},
    ]
    lin = build_lineage(records)
    # an answer citing a chunk of the superseded circular A
    flagged = superseded_citations([f"{A}#sec#0", f"{B}#sec#1"], lin)
    assert flagged == {A: [B]}


def test_lineage_save_load_roundtrip(tmp_path):
    records = [
        {"circular_number": A, "text": f"CIRCULAR {A}. Norms."},
        {"circular_number": B, "text": f"CIRCULAR {B}. In supersession of {A}, norms."},
    ]
    lin = build_lineage(records)
    p = tmp_path / "lineage.json"
    lin.save(p)
    loaded = Lineage.load(p)
    assert loaded.superseded_by == lin.superseded_by
    assert loaded.supersedes == lin.supersedes
    assert loaded.status(A) == "superseded"


def test_master_circular_reissue_supersession():
    records = [
        {"circular_number": "OLD/2025/1", "issue_date": "2025-01-01",
         "subject": "Master Circular for Stock Brokers", "text": "norms"},
        {"circular_number": "NEW/2026/1", "issue_date": "2026-01-01",
         "subject": "Master Circular for Stock Brokers", "text": "revised norms"},
        {"circular_number": "OTHER/2025/2", "issue_date": "2025-06-01",
         "subject": "Master Circular for Mutual Funds", "text": "mf norms"},
    ]
    lin = build_lineage(records)
    assert lin.status("OLD/2025/1") == "superseded"
    assert lin.superseded_by["OLD/2025/1"] == ["NEW/2026/1"]
    assert lin.status("NEW/2026/1") == "in_force"
    assert lin.status("OTHER/2025/2") == "in_force"   # singleton topic, untouched


def test_demote_superseded_puts_in_force_on_top():
    lin = Lineage(superseded_by={"OLD": ["NEW"]})
    old = Chunk(id="OLD#1", doc_id="OLD", section="", text="x")
    new = Chunk(id="NEW#1", doc_id="NEW", section="", text="y")
    # superseded OLD scored higher pre-demotion
    out = demote_superseded([(old, 0.9), (new, 0.8)], lin, penalty=0.3)
    assert out[0][0].doc_id == "NEW"   # in-force successor now ranks first
    assert out[1][0].doc_id == "OLD"


def test_plain_citation_is_not_supersession():
    rels = detect_relations(
        "SEBI/HO/Y/P/CIR/2024/10",
        "SEBI vide circular SEBI/HO/Z/P/CIR/2022/05 dated Jan 1, 2022 prescribed norms.",
    )
    assert ("references", "SEBI/HO/Z/P/CIR/2022/05") in rels
    assert all(rel != "supersedes" for rel, _ in rels)


def test_real_corpus_oiae_supersedes_listed_circulars():
    lin = build_lineage(load_records(CORPUS))
    oiae = "SEBI/HO/OIAE/OIAE_IAD-3/P/CIR/2026/12676"
    assert oiae in lin.supersedes
    # a circular explicitly listed as superseded by the OIAE consolidation
    assert "SEBI/HO/MIRSD/POD-1/P/CIR/2024/81" in lin.supersedes[oiae]
    # the price-data circular only cites prior circulars -> no supersession
    mrd = "HO/47/17/12(11)2025-MRD-POD3/I/11107/2026"
    assert mrd not in lin.supersedes
