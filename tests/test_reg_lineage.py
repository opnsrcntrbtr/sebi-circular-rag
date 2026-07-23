"""Regulation edges + corpus annotation (spec 2026-07-23 §3.3, §3.4, §3.7)."""
import pytest

from sebi_rag.reg_lineage import (REG_SUCCESSION, annotate_regulation_fields,
                                  build_regulation_edges,
                                  synthesise_repealed_stubs)

REGS = [
    {"reg_id": "mutual-funds-2026", "short_name": "Mutual Funds",
     "year": 2026, "status": "in_force"},
    {"reg_id": "listing-obligations-and-disclosure-requirements-2015",
     "short_name": "Listing Obligations and Disclosure Requirements",
     "year": 2015, "status": "in_force"},
]


def _circ(num, subject="", text=""):
    return {"circular_number": num, "subject": subject, "text": text}


def test_stub_is_created_for_a_cited_regulation_with_a_known_successor():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 1996.")]
    stubs = synthesise_repealed_stubs(circs, REGS)
    assert len(stubs) == 1
    s = stubs[0]
    assert s["reg_id"] == "mutual-funds-1996"
    assert s["status"] == "repealed"
    assert s["superseded_by_reg"] == "mutual-funds-2026"
    assert s["pdf_url"] is None and s["source_url"] is None
    assert s["text"] == ""
    assert "not on SEBI Updated List" in s["provenance"]


def test_stub_without_a_succession_entry_is_unknown_not_repealed():
    circs = [_circ("C/1", text="under SEBI (Some Vanished Thing) Regulations, 1994.")]
    stubs = synthesise_repealed_stubs(circs, REGS)
    assert len(stubs) == 1
    assert stubs[0]["status"] == "unknown"
    assert stubs[0]["superseded_by_reg"] is None


def test_stub_is_not_created_for_an_in_force_regulation():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 2026.")]
    assert synthesise_repealed_stubs(circs, REGS) == []


def test_stubs_are_deduped_across_circulars():
    circs = [_circ("C/1", text="SEBI (Mutual Funds) Regulations, 1996."),
             _circ("C/2", text="SEBI (Mutual Funds) Regulations, 1996 again.")]
    assert len(synthesise_repealed_stubs(circs, REGS)) == 1


def test_successor_gets_supersedes_reg_backlink():
    circs = [_circ("C/1", text="SEBI (Mutual Funds) Regulations, 1996.")]
    regs = [dict(r) for r in REGS]
    stubs = synthesise_repealed_stubs(circs, regs)
    regs.extend(stubs)
    succ = next(r for r in regs if r["reg_id"] == "mutual-funds-2026")
    assert "mutual-funds-1996" in succ["supersedes_reg"]


def test_edge_shape_and_vocabulary():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 2026.")]
    edges, unresolved = build_regulation_edges(circs, REGS)
    assert len(edges) == 1
    e = edges[0]
    assert e["source"] == "C/1"
    assert e["target"] == "mutual-funds-2026"
    assert e["relation"] == "cites"
    assert e["confidence"] == "explicit_text"
    assert e["evidence"] == "body_text"
    assert e["count"] == 1
    assert e["clause"] is None
    assert unresolved == {}


def test_one_edge_per_circular_regulation_pair_with_summed_count():
    circs = [_circ("C/1", text=("SEBI (Mutual Funds) Regulations, 2026 applies. "
                                "See SEBI (Mutual Funds) Regulations, 2026."))]
    edges, _ = build_regulation_edges(circs, REGS)
    assert len(edges) == 1
    assert edges[0]["count"] == 2


def test_highest_evidence_tier_wins_on_the_merged_edge():
    circs = [_circ("C/1",
                   subject="Amendment to SEBI (Mutual Funds) Regulations, 2026",
                   text="Body also cites SEBI (Mutual Funds) Regulations, 2026.")]
    edges, _ = build_regulation_edges(circs, REGS)
    assert len(edges) == 1
    assert edges[0]["evidence"] == "subject_line"
    assert edges[0]["count"] == 2


def test_clause_comes_from_the_winning_tier_occurrence():
    # Subject wins the tier and carries no clause, so the merged edge has none
    # even though a lower-tier body occurrence did.
    circs = [_circ("C/1",
                   subject="Amendment to SEBI (Mutual Funds) Regulations, 2026",
                   text=("Per Regulation 25(6) of SEBI (Mutual Funds) "
                         "Regulations, 2026 the AMC shall comply."))]
    edges, _ = build_regulation_edges(circs, REGS)
    assert edges[0]["evidence"] == "subject_line"
    assert edges[0]["clause"] is None


def test_clause_is_kept_when_the_body_occurrence_wins():
    circs = [_circ("C/1", text=("Per Regulation 25(6) of SEBI (Mutual Funds) "
                                "Regulations, 2026 the AMC shall comply."))]
    edges, _ = build_regulation_edges(circs, REGS)
    assert edges[0]["clause"] == "25(6)"


def test_partial_match_is_marked_inferred():
    circs = [_circ("C/1", text=("under SEBI (Listing Obligations and Disclosure"
                                " Requirements Framework) Regulations, 2015."))]
    edges, _ = build_regulation_edges(circs, REGS)
    assert edges[0]["confidence"] == "inferred"
    assert edges[0]["target"] == (
        "listing-obligations-and-disclosure-requirements-2015")


def test_unresolved_names_are_counted_not_dropped():
    circs = [_circ("C/1", text="under SEBI (Totally Unknown) Regulations, 1994.")]
    edges, unresolved = build_regulation_edges(circs, REGS)
    assert edges == []
    assert unresolved == {("Totally Unknown", 1994): 1}


def test_annotate_sets_the_three_additive_fields():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 2026.")]
    edges, _ = build_regulation_edges(circs, REGS)
    changed = annotate_regulation_fields(circs, edges, REGS)
    assert changed == 1
    assert circs[0]["regulations"] == ["mutual-funds-2026"]
    assert circs[0]["primary_regulation"] == "mutual-funds-2026"
    assert circs[0]["regulatory_basis_status"] == "current"


def test_annotate_is_idempotent():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 2026.")]
    edges, _ = build_regulation_edges(circs, REGS)
    assert annotate_regulation_fields(circs, edges, REGS) == 1
    assert annotate_regulation_fields(circs, edges, REGS) == 0


def test_annotate_orders_regulations_by_count_descending():
    circs = [_circ("C/1", text=(
        "SEBI (Listing Obligations and Disclosure Requirements) Regulations, "
        "2015 applies. SEBI (Mutual Funds) Regulations, 2026 applies. "
        "SEBI (Mutual Funds) Regulations, 2026 applies again."))]
    edges, _ = build_regulation_edges(circs, REGS)
    annotate_regulation_fields(circs, edges, REGS)
    assert circs[0]["regulations"][0] == "mutual-funds-2026"


def test_primary_regulation_prefers_evidence_tier_over_count():
    circs = [_circ("C/1",
                   subject=("Amendment to SEBI (Listing Obligations and "
                            "Disclosure Requirements) Regulations, 2015"),
                   text=("SEBI (Mutual Funds) Regulations, 2026 applies. "
                         "SEBI (Mutual Funds) Regulations, 2026 again. "
                         "SEBI (Mutual Funds) Regulations, 2026 thrice."))]
    edges, _ = build_regulation_edges(circs, REGS)
    annotate_regulation_fields(circs, edges, REGS)
    assert circs[0]["primary_regulation"] == (
        "listing-obligations-and-disclosure-requirements-2015")


def test_repealed_basis_and_mixed():
    regs = REGS + [{"reg_id": "mutual-funds-1996", "short_name": "Mutual Funds",
                    "year": 1996, "status": "repealed"}]
    dead = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 1996.")]
    edges, _ = build_regulation_edges(dead, regs)
    annotate_regulation_fields(dead, edges, regs)
    assert dead[0]["regulatory_basis_status"] == "repealed_basis"

    both = [_circ("C/2", text=("SEBI (Mutual Funds) Regulations, 1996 and "
                               "SEBI (Mutual Funds) Regulations, 2026."))]
    edges, _ = build_regulation_edges(both, regs)
    annotate_regulation_fields(both, edges, regs)
    assert both[0]["regulatory_basis_status"] == "mixed"


def test_circular_with_no_citations_gets_unknown_basis():
    circs = [_circ("C/1", text="No statutory reference here.")]
    edges, _ = build_regulation_edges(circs, REGS)
    annotate_regulation_fields(circs, edges, REGS)
    assert circs[0]["regulations"] == []
    assert circs[0]["primary_regulation"] is None
    assert circs[0]["regulatory_basis_status"] == "unknown"


def test_annotation_never_touches_validity_or_supersession():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 1996.")]
    circs[0].update(validity_status="current", supersession_status="in_force")
    edges, _ = build_regulation_edges(circs, REGS)
    annotate_regulation_fields(circs, edges, REGS)
    assert circs[0]["validity_status"] == "current"
    assert circs[0]["supersession_status"] == "in_force"


def test_annotation_adds_no_circular_meta_field():
    """Index-invariance guard (spec §3.1): the new fields must never be ones
    CircularMeta carries, or they would enter every chunk payload."""
    from dataclasses import fields

    from sebi_rag.segment import CircularMeta
    meta_fields = {f.name for f in fields(CircularMeta)}
    new_fields = {"regulations", "primary_regulation", "regulatory_basis_status"}
    assert meta_fields.isdisjoint(new_fields)


def test_every_alias_target_is_in_force_or_has_a_succession_entry():
    """An alias pointing at a slug that is neither a scraped in-force
    regulation nor a known-repealed one mints a phantom stub instead of
    linking. Guards the real FVCI singular/plural typo."""
    from pathlib import Path

    from sebi_rag.regulations import REGULATION_ALIASES
    corpus = Path(__file__).resolve().parents[1] / "data/corpus/regulations.jsonl"
    if not corpus.exists():
        pytest.skip("regulations.jsonl not built yet")
    import json
    in_force = {json.loads(line)["reg_id"]
                for line in corpus.read_text(encoding="utf-8").splitlines()
                if line.strip()}
    orphans = {k: v for k, v in REGULATION_ALIASES.items()
               if v not in in_force and v not in REG_SUCCESSION}
    assert orphans == {}, f"alias targets resolve to nothing: {orphans}"


def test_every_succession_source_and_target_is_well_formed():
    for src, dst in REG_SUCCESSION.items():
        assert src[-5] == "-" and src[-4:].isdigit(), src
        assert dst[-5] == "-" and dst[-4:].isdigit(), dst


def test_succession_table_targets_are_distinct_from_sources():
    for src, dst in REG_SUCCESSION.items():
        assert src != dst
        assert src not in REG_SUCCESSION.get(dst, "")


@pytest.mark.parametrize("bad", [None, []])
def test_empty_inputs_do_not_raise(bad):
    edges, unresolved = build_regulation_edges(bad or [], REGS)
    assert edges == [] and unresolved == {}


from sebi_rag.reg_lineage import build_regulatory_index

_INDEX_REGS = [
    {"reg_id": "stock-brokers-1992", "short_name": "Stock Brokers", "year": 1992,
     "status": "repealed", "superseded_by_reg": "stock-brokers-2026"},
    {"reg_id": "stock-brokers-2026", "short_name": "Stock Brokers", "year": 2026,
     "status": "in_force", "superseded_by_reg": None},
    {"reg_id": "aif-2012", "short_name": "Alternative Investment Funds", "year": 2012,
     "status": "in_force", "superseded_by_reg": None},
    {"reg_id": "orphan-2009", "short_name": "Orphan", "year": 2009,
     "status": "unknown", "superseded_by_reg": None},
    {"reg_id": "no-successor-record-1999", "short_name": "No Successor Record",
     "year": 1999, "status": "repealed", "superseded_by_reg": "missing-2030"},
]


def _icirc(num, regs, primary, basis):
    return {"circular_number": num, "regulations": regs,
            "primary_regulation": primary, "regulatory_basis_status": basis}


def test_index_happy_path_resolves_successor_object():
    circs = [_icirc("C/1", ["stock-brokers-1992"], "stock-brokers-1992",
                    "repealed_basis")]
    idx = build_regulatory_index(circs, _INDEX_REGS)
    entry = idx["C/1"]
    assert entry["regulatory_basis_status"] == "repealed_basis"
    (reg,) = entry["regulations"]
    assert reg["reg_id"] == "stock-brokers-1992"
    assert reg["short_name"] == "Stock Brokers" and reg["year"] == 1992
    assert reg["status"] == "repealed"
    assert reg["superseded_by"] == {"reg_id": "stock-brokers-2026",
                                    "short_name": "Stock Brokers", "year": 2026}


def test_index_uncited_circular_is_unknown_empty():
    circs = [_icirc("C/2", [], None, "unknown")]
    entry = build_regulatory_index(circs, _INDEX_REGS)["C/2"]
    assert entry["regulatory_basis_status"] == "unknown"
    assert entry["primary_regulation"] is None
    assert entry["regulations"] == []


def test_index_missing_basis_fields_default():
    entry = build_regulatory_index([{"circular_number": "C/3"}], _INDEX_REGS)["C/3"]
    assert entry["regulatory_basis_status"] == "unknown"
    assert entry["primary_regulation"] is None
    assert entry["regulations"] == []


def test_index_dangling_reg_id_falls_back():
    circs = [_icirc("C/4", ["ghost-2000"], "ghost-2000", "unknown")]
    (reg,) = build_regulatory_index(circs, _INDEX_REGS)["C/4"]["regulations"]
    assert reg == {"reg_id": "ghost-2000", "short_name": "ghost-2000",
                   "year": None, "status": "unknown", "superseded_by": None}


def test_index_primary_is_unknown_but_a_repealed_reg_is_present():
    # basis repealed_basis; primary points at the unknown reg, not the repealed one.
    circs = [_icirc("C/5", ["orphan-2009", "stock-brokers-1992"], "orphan-2009",
                    "repealed_basis")]
    regs = build_regulatory_index(circs, _INDEX_REGS)["C/5"]["regulations"]
    by_id = {r["reg_id"]: r for r in regs}
    assert by_id["orphan-2009"]["status"] == "unknown"
    assert by_id["stock-brokers-1992"]["status"] == "repealed"
    assert by_id["stock-brokers-1992"]["superseded_by"]["reg_id"] == "stock-brokers-2026"


def test_index_repealed_with_missing_successor_record():
    circs = [_icirc("C/6", ["no-successor-record-1999"], "no-successor-record-1999",
                    "repealed_basis")]
    (reg,) = build_regulatory_index(circs, _INDEX_REGS)["C/6"]["regulations"]
    assert reg["status"] == "repealed"
    assert reg["superseded_by"] is None
