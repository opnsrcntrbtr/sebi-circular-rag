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


def test_annotate_corpus_writes_new_metadata_fields(tmp_path):
    import json
    from sebi_rag.lineage import annotate_corpus
    new_cn = "SEBI/HO/IMD/DF2/CIR/P/2024/031"
    old_cn = "SEBI/HO/IMD/DF2/CIR/P/2021/024"
    recs = [
        {"circular_number": new_cn, "issue_date": "2024-01-01",
         "subject": "Master Circular for Mutual Funds",
         "text": f"This circular supersedes {old_cn} in full."},
        {"circular_number": old_cn, "issue_date": "2021-01-01",
         "subject": "Mutual fund norms", "text": "Old content."},
        {"circular_number": "SEBI/HO/IMD/DF2/CIR/P/2023/099", "issue_date": "",
         "subject": "Clarification on custody", "text": "No refs."},
    ]
    p = tmp_path / "c.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    summary = annotate_corpus(p)
    out = {r["circular_number"]: r
           for r in map(json.loads, p.read_text().splitlines())}
    assert out[new_cn]["circular_type"] == "MASTER_CIRCULAR"
    assert out[new_cn]["validity_status"] == "current"
    assert out[old_cn]["validity_status"] == "superseded"
    assert out[old_cn]["superseded_by_id"] == [new_cn]
    assert out["SEBI/HO/IMD/DF2/CIR/P/2023/099"]["circular_type"] == "CLARIFICATION"
    assert out["SEBI/HO/IMD/DF2/CIR/P/2023/099"]["validity_status"] == "unknown"
    edges = out[new_cn]["supersession_edges"]
    assert edges and edges[0]["target"] == old_cn and edges[0]["confidence"] == "explicit_text"
    # legacy fields still written exactly as before
    assert out[old_cn]["supersession_status"] == "superseded"
    assert out[old_cn]["superseded_by"] == [new_cn]
    assert summary["validity_counts"]["superseded"] == 1


def _lin_chain():
    # A (2019) < B (2021) < C (2023), linear supersession
    return (Lineage(
        supersedes={"B": ["A"], "C": ["B"]},
        superseded_by={"A": ["B"], "B": ["C"]},
    ), {"A": "2019-01-01", "B": "2021-01-01", "C": "2023-01-01"})


def test_governing_on_linear_chain():
    lin, dates = _lin_chain()
    assert lin.governing_on("A", "2020-06-01", dates) == "A"
    assert lin.governing_on("A", "2022-06-01", dates) == "B"
    assert lin.governing_on("A", "2024-06-01", dates) == "C"
    # entry point anywhere in the family gives the same answer
    assert lin.governing_on("C", "2020-06-01", dates) == "A"


def test_governing_on_before_family_exists():
    lin, dates = _lin_chain()
    assert lin.governing_on("A", "2018-01-01", dates) is None


def test_governing_on_unknown_dates_excluded():
    lin, dates = _lin_chain()
    dates = dict(dates, C="")  # C has no usable date
    assert lin.governing_on("A", "2024-06-01", dates) == "B"


def test_governing_on_cycle_safe():
    lin = Lineage(supersedes={"X": ["Y"], "Y": ["X"]},
                  superseded_by={"X": ["Y"], "Y": ["X"]})
    dates = {"X": "2020-01-01", "Y": "2021-01-01"}
    # both superseded within the candidate set -> deterministic max-date fallback
    assert lin.governing_on("X", "2022-01-01", dates) == "Y"


def test_governing_on_parallel_branches_max_date_wins():
    lin = Lineage(supersedes={"B1": ["A"], "B2": ["A"]},
                  superseded_by={"A": ["B1", "B2"]})
    dates = {"A": "2019-01-01", "B1": "2021-01-01", "B2": "2022-01-01"}
    assert lin.governing_on("A", "2023-01-01", dates) == "B2"


def test_detect_relations_ex_evidence_and_extractor():
    from sebi_rag.lineage import detect_relations_ex
    text = ("This circular supersedes Circular No. SEBI/HO/IMD/DF2/CIR/P/2021/024 "
            "with immediate effect.")
    rels = detect_relations_ex("SEBI/HO/IMD/DF2/CIR/P/2024/031", text)
    sup = [r for r in rels if r["relation"] == "supersedes"]
    assert sup and sup[0]["target"] == "SEBI/HO/IMD/DF2/CIR/P/2021/024"
    assert "supersedes" in sup[0]["evidence"]
    assert sup[0]["extractor"] == "regex:SUPERSEDE_RE"


def test_detect_relations_delegates_unchanged():
    from sebi_rag.lineage import detect_relations
    text = "This circular supersedes SEBI/HO/IMD/DF2/CIR/P/2021/024."
    assert ("supersedes", "SEBI/HO/IMD/DF2/CIR/P/2021/024") in detect_relations(
        "SEBI/HO/IMD/DF2/CIR/P/2024/031", text)


def test_build_lineage_edges_tiered():
    from sebi_rag.lineage import build_lineage
    new_cn = "SEBI/HO/IMD/DF2/CIR/P/2024/031"
    old_cn = "SEBI/HO/IMD/DF2/CIR/P/2021/024"
    records = [
        {"circular_number": new_cn, "issue_date": "2024-01-01",
         "subject": "Master Circular for Mutual Funds",
         "text": f"This circular supersedes {old_cn} in full."},
        {"circular_number": old_cn, "issue_date": "2021-01-01",
         "subject": "Master Circular for Mutual Funds", "text": "Old content."},
    ]
    lin = build_lineage(records)
    tiers = {(e["source"], e["target"]): e["confidence"] for e in lin.edges}
    # explicit text edge wins the tier for (new_cn, old_cn) even though the
    # master-topic rule also links them; no duplicate edge is emitted
    assert tiers[(new_cn, old_cn)] == "explicit_text"
    assert len(lin.edges) == 1


def test_build_lineage_inferred_master_topic_edge():
    from sebi_rag.lineage import build_lineage
    records = [
        {"circular_number": "MC/2", "issue_date": "2024-01-01",
         "subject": "Master Circular for Depositories", "text": "No refs here."},
        {"circular_number": "MC/1", "issue_date": "2021-01-01",
         "subject": "Master Circular for Depositories", "text": "No refs here."},
    ]
    lin = build_lineage(records)
    e = [e for e in lin.edges if e["source"] == "MC/2" and e["target"] == "MC/1"]
    assert e and e[0]["confidence"] == "inferred" and e[0]["extractor"] == "master_topic"
    assert lin.explicit_superseded_by("MC/1") == []
    assert lin.superseded_by["MC/1"] == ["MC/2"]  # legacy dicts keep both tiers


def test_lineage_save_load_roundtrips_edges(tmp_path):
    from sebi_rag.lineage import Lineage
    lin = Lineage(edges=[{"source": "A", "target": "B", "relation": "supersedes",
                          "confidence": "explicit_text",
                          "extractor": "regex:SUPERSEDE_RE", "evidence": "x"}])
    p = tmp_path / "lin.json"
    lin.save(p)
    assert Lineage.load(p).edges == lin.edges


def test_lineage_load_old_file_defaults_empty_edges(tmp_path):
    from sebi_rag.lineage import Lineage
    p = tmp_path / "old.json"
    p.write_text('{"supersedes": {}, "amends": {}, "superseded_by": {}, "amended_by": {}}',
                 encoding="utf-8")
    assert Lineage.load(p).edges == []


def test_annotate_corpus_adds_master_fields_and_consolidates_edges(tmp_path):
    import json
    from sebi_rag.lineage import annotate_corpus
    # Uses only the legacy "List of Circulars & Communications" heading
    # (Task 6), not "rescinded"/"superseded"/"repeal"/"withdrawn" wording, so
    # this text stays outside SUPERSEDE_RE's trigger vocabulary — isolating
    # the "consolidates never flips validity" claim from the codebase's
    # pre-existing (and independently correct) supersedes detector, which
    # legitimately WOULD also fire on real "rescinded"-worded appendices.
    master = {
        "circular_number": "SEBI/HO/IMD/MASTER/2024/1",
        "subject": "Master Circular for Mutual Funds",
        "issue_date": "2024-06-27",
        "text": ("Chapter 1 ... This Master Circular compiles the circulars "
                 "issued to date.\nSCHEDULE\nList of Circulars & Communications\n"
                 "1. SEBI/HO/IMD/DF2/CIR/P/2020/175 dated September 17, 2020\n"
                 "2. SEBI/HO/IMD/IMD-I/DOF5/P/CIR/2021/553 dated April 28, 2021\n"
                 + "body " * 200),
        "source_url": "https://www.sebi.gov.in/legal/master-circulars/x_1.html",
    }
    plain = {"circular_number": "SEBI/HO/IMD/DF2/CIR/P/2020/175",
             "subject": "Product labelling", "issue_date": "2020-09-17",
             "text": "body " * 200, "source_url": ""}
    p = tmp_path / "c.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in (master, plain)) + "\n")
    summary = annotate_corpus(p)
    recs = [json.loads(l) for l in p.read_text().splitlines()]
    m = next(r for r in recs if r["circular_number"] == master["circular_number"])
    q = next(r for r in recs if r["circular_number"] == plain["circular_number"])
    assert m["is_master"] is True
    assert m["master_series"] == "Mutual Funds"
    assert m["master_edition"] == 2024
    cons = [e for e in m["supersession_edges"] if e["relation"] == "consolidates"]
    assert {e["target"] for e in cons} >= {"SEBI/HO/IMD/DF2/CIR/P/2020/175"}
    assert q["is_master"] is False
    assert summary["masters"] == 1
    assert summary["consolidates_edges"] == len(cons)
    # locked rule: consolidates never flips validity
    assert q["validity_status"] in ("current", "unknown")
