"""P4b: as-of golden evaluation runner tests (offline)."""
from __future__ import annotations

import pytest

from pathlib import Path

from sebi_rag.embeddings import HashEmbedder
from sebi_rag.eval_asof import load_golden_asof, run_pipeline_cases, run_selector_cases, summarize
from sebi_rag.generate import ExtractiveStubGenerator
from sebi_rag.lineage import Lineage
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.rerank import LexicalReranker
from sebi_rag.segment import CircularMeta, hierarchical_chunk

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_ASOF = ROOT / "eval" / "golden" / "golden_asof_v1.jsonl"


def test_load_golden_asof_has_both_modes():
    cases = load_golden_asof(GOLDEN_ASOF)
    modes = {c["mode"] for c in cases}
    assert modes == {"pipeline", "selector"}
    assert len(cases) == 13


def _lin_chain():
    return (Lineage(
        supersedes={"B": ["A"], "C": ["B"]},
        superseded_by={"A": ["B"], "B": ["C"]},
    ), {"A": "2019-01-01", "B": "2021-01-01", "C": "2023-01-01"})


def test_run_selector_cases_pass_and_fail():
    lin, dates = _lin_chain()
    cases = [
        {"id": "s1", "mode": "selector", "entry": "A", "as_of": "2022-06-01", "expected": "B"},
        {"id": "s2", "mode": "selector", "entry": "A", "as_of": "2022-06-01", "expected": "C"},  # wrong on purpose
        {"id": "p1", "mode": "pipeline", "query": "irrelevant", "as_of": "x",
         "expected_any": ["Z"]},  # must be skipped by selector runner
    ]
    results = run_selector_cases(lin, dates, cases)
    assert {r.id for r in results} == {"s1", "s2"}
    by_id = {r.id: r for r in results}
    assert by_id["s1"].passed is True
    assert by_id["s2"].passed is False


def test_run_pipeline_cases_pass_and_avoid():
    OLD, NEW = "SEBI/HO/MRD/2020/010", "SEBI/HO/MRD/2023/050"
    old_text = "This circular prescribes margin rules. T plus one basis."
    new_text = (f"CIRCULAR {NEW}. This circular supersedes {OLD}. In supersession of "
               f"{OLD}, revised margin rules apply on a T plus zero basis.")
    chunks = hierarchical_chunk(old_text, CircularMeta(circular_number=OLD, issue_date="2020-01-01"))
    chunks += hierarchical_chunk(new_text, CircularMeta(circular_number=NEW, issue_date="2023-01-01"))
    from sebi_rag.lineage import build_lineage
    lineage = build_lineage([
        {"circular_number": OLD, "issue_date": "2020-01-01", "text": old_text},
        {"circular_number": NEW, "issue_date": "2023-01-01", "text": new_text},
    ])
    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256), reranker=LexicalReranker(),
        generator=ExtractiveStubGenerator(), abstain_threshold=0.05, lineage=lineage,
    )
    cases = [
        {"id": "p-old", "mode": "pipeline", "query": "margin rules", "as_of": "2021-06-01",
         "expected_any": [OLD], "avoid": [NEW]},
        {"id": "p-new", "mode": "pipeline", "query": "margin rules", "as_of": "2024-06-01",
         "expected_any": [NEW], "avoid": []},
        {"id": "s-skip", "mode": "selector", "entry": "A", "as_of": "x", "expected": "B"},
    ]
    results = run_pipeline_cases(pipe, cases)
    assert {r.id for r in results} == {"p-old", "p-new"}
    by_id = {r.id: r for r in results}
    assert by_id["p-old"].passed is True
    assert by_id["p-new"].passed is True


def test_summarize_reports_accuracy_and_failures():
    from sebi_rag.eval_asof import AsofCaseResult
    results = [
        AsofCaseResult(id="a", mode="selector", passed=True, detail=""),
        AsofCaseResult(id="b", mode="pipeline", passed=False, detail=""),
    ]
    summary = summarize(results)
    assert summary["n"] == 2
    assert summary["passed"] == 1
    assert summary["accuracy"] == 0.5
    assert summary["failures"] == ["b"]


def test_summarize_reports_a_clopper_pearson_interval():
    from sebi_rag.eval_asof import AsofCaseResult
    results = [
        AsofCaseResult(id=f"p{i}", mode="pipeline", passed=True, detail="")
        for i in range(9)
    ] + [AsofCaseResult(id="p9", mode="pipeline", passed=False, detail="")]
    summary = summarize(results)
    assert summary["accuracy"] == 0.9
    assert summary["ci_lo"] == pytest.approx(0.554984, abs=1e-5)
    assert summary["ci_hi"] == pytest.approx(0.997471, abs=1e-5)
    assert summary["ci_method"] == "clopper-pearson"


def test_summarize_all_pass_pins_upper_bound():
    from sebi_rag.eval_asof import AsofCaseResult
    results = [
        AsofCaseResult(id=f"s{i}", mode="selector", passed=True, detail="")
        for i in range(3)
    ]
    summary = summarize(results)
    assert summary["ci_hi"] == 1.0
    assert summary["ci_lo"] < 1.0


def test_summarize_handles_an_empty_mode():
    summary = summarize([])
    assert summary["n"] == 0
    assert summary["accuracy"] == 0.0
    assert (summary["ci_lo"], summary["ci_hi"]) == (0.0, 1.0)
