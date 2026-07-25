"""Deterministic escalation backfill from Task-5 candidate chunks
(2026-07-25 remediation Task 7)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.backfill_escalations import find_source_chunk, quote_for  # noqa: E402

_CAND = {
    "chunk_id": "SEBI/X/1#1.8. Besides the above#326",
    "doc": "SEBI/X/1",
    "subject": "Oversight",
    "text": ("1. The criteria for selection of members for annual inspection "
             "are as follows: 1.8. Besides the above, the special purpose or "
             "limited inspections shall be carried out based on any triggers "
             "like patterns found during investor complaint resolution or "
             "arbitration, complaints on specific malpractices of a broker."),
}


def _row(**over):
    base = {"id": "v7-bp-008", "relevant_circulars": ["SEBI/X/1"],
            "answer_contains": "patterns found during investor complaint resolution"}
    base.update(over)
    return base


def test_finds_the_unique_source_chunk():
    assert find_source_chunk(_row(), [_CAND])["chunk_id"] == _CAND["chunk_id"]


def test_returns_none_when_ambiguous():
    assert find_source_chunk(_row(), [_CAND, dict(_CAND, chunk_id="other#9")]) is None


def test_returns_none_when_doc_does_not_match():
    assert find_source_chunk(_row(relevant_circulars=["OTHER/2"]), [_CAND]) is None


def test_returns_none_when_answer_contains_empty():
    assert find_source_chunk(_row(answer_contains=""), [_CAND]) is None


def test_quote_is_verbatim_contains_literal_and_long_enough():
    q = quote_for(_CAND, _row())
    assert q in _CAND["text"]
    assert _row()["answer_contains"] in q
    assert len(" ".join(q.split())) >= 40


def test_quote_never_returns_the_header_line():
    cand = dict(_CAND, text="SEBI/X/1 | Oversight | s\n" + _CAND["text"])
    q = quote_for(cand, _row())
    assert not q.startswith("SEBI/X/1 |")
    assert q in cand["text"]


def test_matches_a_candidate_whose_doc_was_since_renumbered():
    """Candidate files were mined before the 2026-07-25 renumbering, so a
    candidate can still carry a doc id the corpus has since corrected. The
    row's gold doc holds the NEW number; matching must bridge the two or the
    row is stranded as unrecoverable (this hit v7-bp-003)."""
    cand = dict(_CAND, doc="CIR/MRD/DP/41")
    row = _row(relevant_circulars=["CIR/MRD/DP/41/2010"])
    assert find_source_chunk(row, [cand])["chunk_id"] == cand["chunk_id"]


def test_quote_does_not_begin_or_end_mid_word():
    cand = dict(_CAND, text="alpha beta gamma delta epsilon zeta eta theta iota")
    row = _row(answer_contains="delta")
    q = quote_for(cand, row)
    assert q in cand["text"] and "delta" in q
    assert not q.startswith(("lpha", "eta", "amma")), q
    # every token in the quote is a whole token of the source
    src = cand["text"].split()
    assert all(t in src for t in q.split()), q
