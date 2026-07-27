"""Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)."""
from sebi_rag.benchmark import (
    STRATA_TARGETS_V7, validate_golden_v7,
)


def _row(**over):
    base = {
        "id": "v7-ls-001", "query": "What replaced the 2020 margin circular?",
        "relevant_circulars": ["SEBI/HO/NEW/2024/1"],
        "relevant_chunks": [{"doc": "SEBI/HO/NEW/2024/1",
                             "quote": "the margin requirements specified herein shall apply to all"}],
        "answer_contains": "margin", "must_contain": ["margin"],
        "must_not_contain": [], "must_not_cite": ["SEBI/HO/OLD/2020/9"],
        "abstain": False, "as_of": None, "task_type": "lineage_supersession",
        "difficulty": "hard", "expected_citation_level": "chunk",
        "rationale": "test", "label_source": "v7-miner-lineage",
        "review_status": "draft",
    }
    base.update(over)
    return base


def test_strata_targets_sum_to_260():
    assert sum(STRATA_TARGETS_V7.values()) == 260
    assert STRATA_TARGETS_V7["lineage_supersession"] == 40


def test_valid_row_passes():
    assert validate_golden_v7([_row()]) == []


def test_bad_v7_id_flagged():
    issues = validate_golden_v7([_row(id="v7-xx-1")])
    assert any("id" in i.message for i in issues)


def test_carried_ids_exempt_from_v7_pattern():
    row = _row(id="surv", must_not_cite=[], task_type="title_direct",
               label_source="golden_v5", review_status="seeded")
    assert validate_golden_v7([row]) == []


def test_short_quote_flagged():
    row = _row(relevant_chunks=[{"doc": "SEBI/HO/NEW/2024/1", "quote": "too short"}])
    issues = validate_golden_v7([row])
    assert any("quote" in i.message for i in issues)


def test_quote_doc_must_be_relevant_circular():
    row = _row(relevant_chunks=[{"doc": "SEBI/HO/OTHER/2021/5",
                                 "quote": "x" * 50}])
    issues = validate_golden_v7([row])
    assert any("doc" in i.message for i in issues)


def test_as_of_only_on_lineage_rows_and_iso():
    issues = validate_golden_v7([_row(task_type="title_direct",
                                      must_not_cite=[], as_of="2023-05-01")])
    assert any("as_of" in i.message for i in issues)
    issues = validate_golden_v7([_row(as_of="01/05/2023")])
    assert any("as_of" in i.message for i in issues)


def test_must_not_cite_only_on_lineage_rows():
    issues = validate_golden_v7([_row(task_type="title_direct")])
    assert any("must_not_cite" in i.message for i in issues)


def test_abstain_row_needs_no_labels():
    row = _row(id="v7-hn-001", task_type="hard_negative", abstain=True,
               relevant_circulars=[], relevant_chunks=[], must_contain=[],
               must_not_cite=[], as_of=None, expected_citation_level="none")
    assert validate_golden_v7([row]) == []


def test_census_enforced_at_full_size():
    rows = [_row(id=f"v7-ls-{i:03d}") for i in range(260)]
    issues = validate_golden_v7(rows)
    assert any("census" in i.message for i in issues)


def test_far_negative_exempt_from_hard_floor():
    rows = [_row(id=f"v7-ls-{i:03d}", task_type="lineage_supersession")
            for i in range(STRATA_TARGETS_V7["lineage_supersession"])]
    rows += [_row(id=f"v7-td-{i:03d}", task_type="title_direct", difficulty="hard",
                  must_not_cite=[], as_of=None)
             for i in range(STRATA_TARGETS_V7["title_direct"])]
    rows += [_row(id=f"v7-bp-{i:03d}", task_type="body_paraphrase", difficulty="hard",
                  must_not_cite=[], as_of=None)
             for i in range(STRATA_TARGETS_V7["body_paraphrase"])]
    rows += [_row(id=f"v7-nt-{i:03d}", task_type="numeric_table", difficulty="hard",
                  must_not_cite=[], as_of=None)
             for i in range(STRATA_TARGETS_V7["numeric_table"])]
    rows += [_row(id=f"v7-mh-{i:03d}", task_type="multi_hop", difficulty="hard",
                  must_not_cite=[], as_of=None)
             for i in range(STRATA_TARGETS_V7["multi_hop"])]
    rows += [_row(id=f"v7-rb-{i:03d}", task_type="repealed_basis", difficulty="hard",
                  must_not_cite=[], as_of=None)
             for i in range(STRATA_TARGETS_V7["repealed_basis"])]
    rows += [_row(id=f"v7-hn-{i:03d}", task_type="hard_negative", difficulty="hard",
                  must_not_cite=[], as_of=None, abstain=True, relevant_circulars=[],
                  relevant_chunks=[], must_contain=[], expected_citation_level="none")
             for i in range(STRATA_TARGETS_V7["hard_negative"])]
    rows += [_row(id=f"v7-fn-{i:03d}", task_type="far_negative", difficulty="easy",
                  must_not_cite=[], as_of=None, abstain=True, relevant_circulars=[],
                  relevant_chunks=[], must_contain=[], expected_citation_level="none")
             for i in range(STRATA_TARGETS_V7["far_negative"])]
    issues = validate_golden_v7(rows)
    assert not any("far_negative under 20% hard" in i.message for i in issues)
