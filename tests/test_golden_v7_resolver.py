"""Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud."""
from sebi_rag.benchmark import (
    chunks_by_doc, qrels_rows, resolve_chunk_spans, validate_golden_v7,
)
from sebi_rag.segment import CircularMeta, hierarchical_chunk

_TEXT = (
    "1. Applicability:\nThis circular applies to all registered stock brokers "
    "and depository participants dealing in the equity derivatives segment.\n\n"
    "2. Margin requirements:\nThe upfront margin shall be collected at the rate "
    "of twenty per cent of the transaction value in all cases without exception."
)


def _chunks(doc="SEBI/HO/T/2024/1"):
    return hierarchical_chunk(_TEXT, CircularMeta(circular_number=doc, subject="Margins"))


def _row(quote, doc="SEBI/HO/T/2024/1"):
    return {"id": "v7-nt-001", "relevant_circulars": [doc],
            "relevant_chunks": [{"doc": doc, "quote": quote}], "abstain": False}


def test_resolves_normalized_whitespace_quote():
    chunks = _chunks()
    quote = "upfront  margin shall be collected at the\nrate of twenty per cent"
    ids = resolve_chunk_spans(_row(quote), chunks_by_doc(chunks))
    assert ids and all(i in {c.id for c in chunks} for i in ids)


def test_unresolvable_quote_returns_empty():
    ids = resolve_chunk_spans(
        _row("this text appears nowhere in the corpus at all, honestly"),
        chunks_by_doc(_chunks()))
    assert ids == []


def test_legacy_string_entries_pass_through():
    row = {"id": "x", "relevant_chunks": ["SEBI/HO/T/2024/1#preamble#0"]}
    assert resolve_chunk_spans(row, {}) == ["SEBI/HO/T/2024/1#preamble#0"]


def test_validator_flags_unresolvable_quote_when_chunks_given():
    row = _row("this text appears nowhere in the corpus at all, honestly")
    row.update({"query": "q", "answer_contains": "", "must_contain": [],
                "must_not_contain": [], "task_type": "numeric_table",
                "difficulty": "hard", "expected_citation_level": "chunk",
                "rationale": "t", "label_source": "t", "review_status": "draft"})
    issues = validate_golden_v7([row], chunks=_chunks())
    assert any("resolve" in i.message for i in issues)


def test_qrels_span_rows_get_grade_2():
    chunks = _chunks()
    golden = [{"id": "q1", "abstain": False,
               "relevant_circulars": ["SEBI/HO/T/2024/1"],
               "relevant_chunks": [{"doc": "SEBI/HO/T/2024/1",
                                    "quote": "upfront margin shall be collected at the rate of twenty per cent"}]}]
    rows = qrels_rows(golden, chunks)
    assert rows and all(score == 2 for _, _, score in rows)
