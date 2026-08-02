"""Unit tests for sebi_rag.measure — automated metric collection."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.measure import (  # noqa: E402
    MeasureResult,
    MeasureReport,
    ALL_METRICS,
    run_all_metrics,
    measure_parsing_latency,
    measure_supersession_precision,
    measure_temporal_accuracy,
    measure_retrieval_recall,
    measure_context_precision,
    measure_mrr,
    _git_commit,
    _bootstrap_ci,
    _mps_memory,
)


# ---------------------------------------------------------------------------
# Data class tests
# ---------------------------------------------------------------------------


class TestDataClasses:
    def test_measure_result_defaults(self):
        r = MeasureResult(metric="test", value={"x": 1})
        assert r.metric == "test"
        assert r.value == {"x": 1}
        assert r.sample_size == 0

    def test_measure_result_full(self):
        r = MeasureResult(metric="test", value={"x": 1}, sample_size=42)
        assert r.sample_size == 42

    def test_measure_report_from_results(self):
        results = [
            MeasureResult(metric="a", value={"v": 1}, sample_size=10),
            MeasureResult(metric="b", value={"v": 2}, sample_size=20),
        ]
        report = MeasureReport.from_results(
            results, git_commit="abc123", corpus_circulars=100, corpus_chunks=500, golden_n=50
        )
        assert report.git_commit == "abc123"
        assert report.corpus_circulars == 100
        assert report.corpus_chunks == 500
        assert report.golden_n == 50
        assert report.metrics == {"a": {"v": 1}, "b": {"v": 2}}

    def test_measure_report_to_json(self):
        report = MeasureReport(
            git_commit="abc123", corpus_circulars=100, corpus_chunks=500, golden_n=50,
            metrics={"m": {"v": 1}}
        )
        data = json.loads(report.to_json())
        assert data["git_commit"] == "abc123"
        assert data["metrics"]["m"]["v"] == 1


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_git_commit_in_repo(self):
        commit = _git_commit(ROOT)
        assert len(commit) == 40  # SHA-1 hex

    def test_git_commit_nonexistent_dir(self):
        commit = _git_commit("/tmp/nonexistent_dir_12345")
        assert commit == "unknown"

    def test_bootstrap_ci_empty(self):
        mean, lo, hi = _bootstrap_ci([])
        assert mean == lo == hi == 0.0

    def test_bootstrap_ci_single(self):
        mean, lo, hi = _bootstrap_ci([42.0])
        assert mean == lo == hi == 42.0

    def test_bootstrap_ci_normal(self):
        import random
        random.seed(42)
        values = [float(i) for i in range(100)]
        mean, lo, hi = _bootstrap_ci(values)
        assert 45 < mean < 55
        assert lo < mean < hi
        assert hi - lo > 0

    def test_mps_memory_no_torch(self):
        """When torch import fails, _mps_memory returns empty dict."""
        with mock.patch.dict(sys.modules, {"torch": None}):
            result = _mps_memory()
            assert result == {}

    @pytest.mark.skip(reason="torch import segfaults after full-suite MPS state depletion")
    def test_mps_memory_with_torch(self):
        """When torch+MPS available, returns memory stats dict."""
        result = _mps_memory()
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Metric: Parsing Latency
# ---------------------------------------------------------------------------


class TestParsingLatency:
    def test_missing_raw_dir(self, tmp_path):
        r = measure_parsing_latency(mock.MagicMock(), [], data_dir=str(tmp_path / "nonexistent"))
        assert r.metric == "parsing_latency"
        assert "raw directory not found" in r.value["error"]

    def test_no_pdfs(self, tmp_path):
        raw = tmp_path / "raw"
        raw.mkdir()
        r = measure_parsing_latency(mock.MagicMock(), [], data_dir=str(tmp_path))
        assert r.metric == "parsing_latency"
        assert "no PDFs found" in r.value["error"]

    def test_with_dummy_pdf(self, tmp_path, monkeypatch):
        """Test with a dummy PDF file — should not crash."""
        raw = tmp_path / "raw"
        raw.mkdir()
        # Create a minimal PDF-like file
        pdf = raw / "test.pdf"
        pdf.write_bytes(b"%PDF-1.4 dummy content for testing\n")
        # Mock extract_text to avoid pdfminer crashing on invalid PDF
        from sebi_rag import ingest_pdf
        monkeypatch.setattr(ingest_pdf, "extract_text", lambda p: "")
        r = measure_parsing_latency(mock.MagicMock(), [], data_dir=str(tmp_path))
        assert r.metric == "parsing_latency"
        assert r.value.get("sample_size", 0) == 1
        assert r.value.get("total_chars", 0) == 0
        assert r.value.get("ocr_count", 0) >= 0


# ---------------------------------------------------------------------------
# Metric: Supersession Precision
# ---------------------------------------------------------------------------


class TestSupersessionPrecision:
    def test_empty_corpus(self, tmp_path):
        corpus = tmp_path / "circulars.jsonl"
        corpus.write_text("")
        r = measure_supersession_precision(mock.MagicMock(), [], corpus_path=str(corpus), sample_n=10)
        assert r.metric == "supersession_precision"
        assert r.value["error"] == "empty corpus"

    def test_valid_edges(self, tmp_path):
        """Two circulars where A supersedes B, dates consistent, mutual reference."""
        corpus = tmp_path / "circulars.jsonl"
        records = [
            {
                "circular_number": "SEBI/HO/CIR/2024/01",
                "issue_date": "2024-01-15",
                "text": "This circular supersedes SEBI/HO/CIR/2023/01. See also SEBI/HO/CIR/2023/01 for details.",
            },
            {
                "circular_number": "SEBI/HO/CIR/2023/01",
                "issue_date": "2023-01-15",
                "text": "This circular is superseded by SEBI/HO/CIR/2024/01.",
            },
        ]
        corpus.write_text("\n".join(json.dumps(r) for r in records) + "\n")
        r = measure_supersession_precision(mock.MagicMock(), [], corpus_path=str(corpus), sample_n=10)
        assert r.metric == "supersession_precision"
        assert r.value["true_positives"] >= 1
        # At least one edge should be verified as true (mutual reference + date check)

    def test_no_supersession_mentions(self, tmp_path):
        """Circulars with no supersession text — should get zero precision edges."""
        corpus = tmp_path / "circulars.jsonl"
        records = [
            {
                "circular_number": "SEBI/HO/CIR/2024/01",
                "issue_date": "2024-01-15",
                "text": "General circular about market regulations.",
            },
        ]
        corpus.write_text("\n".join(json.dumps(r) for r in records) + "\n")
        r = measure_supersession_precision(None, [], corpus_path=str(corpus), sample_n=10)
        assert r.metric == "supersession_precision"
        # No supersession edges detected, so precision = 0 (division by 0 handled)
        assert r.value["precision"] == 0.0


# ---------------------------------------------------------------------------
# Metric: Temporal Accuracy
# ---------------------------------------------------------------------------


class TestTemporalAccuracy:
    def test_no_as_of_rows(self):
        golden = [{"query": "test", "id": "1"}]
        mock_pipeline = mock.MagicMock()
        r = measure_temporal_accuracy(mock_pipeline, golden)
        assert r.metric == "temporal_accuracy"
        assert "no as_of rows" in r.value["error"]

    def test_as_of_query_hit(self):
        golden = [
            {
                "id": "1",
                "query": "test query",
                "as_of": "2023-06-01",
                "relevant_circulars": ["CIRC-2023-01"],
                "abstain": False,
            }
        ]
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-2023-01", "CIRC-2023-02"])
        r = measure_temporal_accuracy(mock_pipeline, golden)
        assert r.metric == "temporal_accuracy"
        assert r.value["accuracy"] == 1.0
        assert r.value["correct_top3"] == 1

    def test_as_of_query_miss(self):
        golden = [
            {
                "id": "1",
                "query": "test query",
                "as_of": "2023-06-01",
                "relevant_circulars": ["CIRC-2023-01"],
                "abstain": False,
            }
        ]
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-2024-01", "CIRC-2024-02"])
        r = measure_temporal_accuracy(mock_pipeline, golden)
        assert r.value["accuracy"] == 0.0
        assert r.value["correct_top3"] == 0

    def test_as_of_abstain_skipped(self):
        golden = [
            {"id": "1", "query": "q", "as_of": "2023-06-01", "abstain": True},
        ]
        mock_pipeline = mock.MagicMock()
        r = measure_temporal_accuracy(mock_pipeline, golden)
        assert r.value["accuracy"] == 0.0
        assert r.value["total_as_of_queries"] == 0


# ---------------------------------------------------------------------------
# Metric: Retrieval Recall@10
# ---------------------------------------------------------------------------


class TestRetrievalRecall:
    def test_full_recall(self):
        golden = [
            {
                "id": "1",
                "query": "test",
                "relevant_circulars": ["CIRC-001"],
                "abstain": False,
            }
        ]
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-001", "CIRC-002"])
        r = measure_retrieval_recall(mock_pipeline, golden, k=10)
        assert r.value["recall_at_k"] == 1.0

    def test_partial_recall(self):
        golden = [
            {
                "id": "1",
                "query": "test",
                "relevant_circulars": ["CIRC-001", "CIRC-002"],
                "abstain": False,
            }
        ]
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-001", "CIRC-003"])
        r = measure_retrieval_recall(mock_pipeline, golden, k=10)
        assert r.value["recall_at_k"] == 0.5

    def test_no_relevant_skipped(self):
        golden = [
            {"id": "1", "query": "test", "relevant_circulars": [], "abstain": False},
        ]
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-001"])
        r = measure_retrieval_recall(mock_pipeline, golden, k=10)
        assert r.value["n_queries"] == 0

    def test_abstain_skipped(self):
        golden = [{"id": "1", "query": "test", "abstain": True}]
        mock_pipeline = mock.MagicMock()
        r = measure_retrieval_recall(mock_pipeline, golden)
        assert r.value["n_queries"] == 0


# ---------------------------------------------------------------------------
# Metric: Context Precision
# ---------------------------------------------------------------------------


class TestContextPrecision:
    def test_perfect_precision(self):
        golden = [
            {
                "id": "1",
                "query": "test",
                "relevant_circulars": ["CIRC-001", "CIRC-002"],
                "abstain": False,
            }
        ]
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-001", "CIRC-002", "CIRC-003"])
        r = measure_context_precision(mock_pipeline, golden, k=10)
        # 2 out of 10 top-k docs are relevant
        assert r.value["context_precision"] == 0.2

    def test_no_relevant_skipped(self):
        golden = [
            {"id": "1", "query": "test", "relevant_circulars": [], "abstain": False},
        ]
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-001"])
        r = measure_context_precision(mock_pipeline, golden, k=10)
        assert r.value["n_queries"] == 0


# ---------------------------------------------------------------------------
# Metric: MRR
# ---------------------------------------------------------------------------


class TestMRR:
    def test_first_rank(self):
        golden = [
            {
                "id": "1",
                "query": "test",
                "relevant_circulars": ["CIRC-001"],
                "abstain": False,
            }
        ]
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-001", "CIRC-002"])
        r = measure_mrr(mock_pipeline, golden)
        assert r.value["mrr"] == 1.0

    def test_second_rank(self):
        golden = [
            {
                "id": "1",
                "query": "test",
                "relevant_circulars": ["CIRC-001"],
                "abstain": False,
            }
        ]
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-002", "CIRC-001"])
        r = measure_mrr(mock_pipeline, golden)
        assert r.value["mrr"] == 0.5

    def test_not_found(self):
        golden = [
            {
                "id": "1",
                "query": "test",
                "relevant_circulars": ["CIRC-001"],
                "abstain": False,
            }
        ]
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-002", "CIRC-003"])
        r = measure_mrr(mock_pipeline, golden)
        assert r.value["mrr"] == 0.0

    def test_no_relevant_skipped(self):
        golden = [
            {"id": "1", "query": "test", "relevant_circulars": [], "abstain": False},
        ]
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-001"])
        r = measure_mrr(mock_pipeline, golden)
        assert r.value["n_queries"] == 0


# ---------------------------------------------------------------------------
# Registry and run_all_metrics
# ---------------------------------------------------------------------------


class TestRegistry:
    def test_all_metrics_keys(self):
        expected = {
            "parsing_latency",
            "supersession_precision",
            "temporal_accuracy",
            "retrieval_recall",
            "context_precision",
            "mrr",
        }
        assert set(ALL_METRICS.keys()) == expected

    def test_all_metrics_callable(self):
        for name, fn in ALL_METRICS.items():
            assert callable(fn), f"{name} is not callable"

    def test_run_all_metrics_subset(self):
        mock_pipeline = mock.MagicMock()
        mock_pipeline.query.return_value = (mock.MagicMock(), ["CIRC-001"])
        golden = [{"id": "1", "query": "q", "relevant_circulars": ["CIRC-001"], "abstain": False}]
        with tempfile.TemporaryDirectory() as td:
            results = run_all_metrics(
                mock_pipeline, golden,
                corpus_path=td,
                data_dir=td,
                metrics=["mrr", "context_precision"],
            )
    def test_run_all_metrics_empty_list_defaults_to_all(self):
        """Empty metrics list is falsy → defaults to ALL_METRICS."""
        mock_pipeline = mock.MagicMock()
        with tempfile.TemporaryDirectory() as td:
            mock_parse = mock.MagicMock(return_value=MeasureResult(metric="parsing_latency", value={}))
            ALL_METRICS["parsing_latency"] = mock_parse
            try:
                results = run_all_metrics(
                    mock_pipeline, [], data_dir=td, metrics=[]
                )
            finally:
                # Restore original
                from sebi_rag import measure as _m
                ALL_METRICS["parsing_latency"] = _m.measure_parsing_latency
            # [] is falsy, so it runs all metrics (but parsing_latency is mocked)
            assert len(results) > 0
            assert mock_parse.called


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestCLI:
    def test_unknown_metrics_exit(self):
        from scripts.bench_metrics import main as cli_main
        with mock.patch.object(sys, "argv", ["bench_metrics", "--metrics", "nonexistent"]):
            with pytest.raises(SystemExit) as exc:
                cli_main()
            assert exc.value.code == 1

    def test_available_metrics_listed(self):
        from scripts.bench_metrics import ALL_METRICS as cli_metrics
        assert set(cli_metrics.keys()) == set(ALL_METRICS.keys())

    def test_markdown_format(self):
        from scripts.bench_metrics import metrics_to_markdown
        results = [
            MeasureResult(metric="mrr", value={"mrr": 0.5}, sample_size=10),
            MeasureResult(metric="recall", value={"recall_at_k": 0.8}, sample_size=10),
        ]
        md = metrics_to_markdown(results, elapsed=5.0)
        assert "SEBI RAG" in md
        assert "mrr" in md
        assert "recall" in md
        assert "5.0s" in md
