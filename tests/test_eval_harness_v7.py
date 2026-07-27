"""Offline harness tests for v7 metrics: as_of passthrough, must_not_cite,
chunk-level recall/MRR, and the adjudicated-subset gate sub-report."""
from sebi_rag.embeddings import HashEmbedder
from sebi_rag.eval_harness import run_eval
from sebi_rag.generate import ExtractiveStubGenerator
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.rerank import LexicalReranker
from sebi_rag.segment import CircularMeta, hierarchical_chunk

_DOC = "SEBI/HO/T/2024/1"
_TEXT = (
    "1. Applicability:\nThis circular applies to all registered stock brokers "
    "and depository participants dealing in the equity derivatives segment.\n\n"
    "2. Margin requirements:\nThe upfront margin shall be collected at the rate "
    "of twenty per cent of the transaction value in all cases without exception."
)


def _pipeline():
    chunks = hierarchical_chunk(
        _TEXT, CircularMeta(circular_number=_DOC, subject="Margin requirements"))
    return RAGPipeline.build(chunks, HashEmbedder(), LexicalReranker(),
                             ExtractiveStubGenerator(), abstain_threshold=0.0)


def _row(**over):
    base = {"id": "v7-nt-001", "query": "upfront margin rate for stock brokers",
            "relevant_circulars": [_DOC],
            "relevant_chunks": [{"doc": _DOC,
                                 "quote": "upfront margin shall be collected at the rate of twenty per cent"}],
            "answer_contains": "twenty", "must_contain": [], "must_not_contain": [],
            "abstain": False, "task_type": "numeric_table", "difficulty": "hard",
            "review_status": "draft"}
    base.update(over)
    return base


def test_chunk_metrics_computed_for_span_rows():
    report = run_eval(_pipeline(), [_row()], k=10)
    assert report.chunk_labeled_n == 1
    assert report.chunk_recall_at_k == 1.0
    assert report.chunk_mrr > 0.0


def test_rows_without_spans_do_not_dilute_chunk_metrics():
    report = run_eval(_pipeline(), [_row(), _row(id="v7-td-001", relevant_chunks=[])], k=10)
    assert report.chunk_labeled_n == 1


def test_as_of_is_passed_to_pipeline():
    calls = {}
    class _Spy:
        retriever = _pipeline().retriever
        def query(self, q, as_of=None, **kw):
            calls["as_of"] = as_of
            return _pipeline().query(q)
    run_eval(_Spy(), [_row(as_of="2023-05-01", task_type="lineage_supersession",
                           must_not_cite=[])], k=10)
    assert calls["as_of"] == "2023-05-01"


def test_must_not_cite_violation_counted():
    report = run_eval(_pipeline(), [_row(task_type="lineage_supersession",
                                         must_not_cite=[_DOC])], k=10)
    assert report.must_not_cite_violation_rate == 1.0


def test_gate_subreport_covers_only_adjudicated():
    rows = [_row(), _row(id="v7-nt-002", review_status="adjudicated")]
    report = run_eval(_pipeline(), rows, k=10)
    assert report.gate is not None and report.gate["n"] == 1
    assert 0.0 <= report.gate["recall_at_k"] <= 1.0


def test_gate_is_none_when_nothing_adjudicated():
    assert run_eval(_pipeline(), [_row()], k=10).gate is None
