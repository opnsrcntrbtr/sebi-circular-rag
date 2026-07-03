"""Offline tests for the ADR-002 certainty architecture: abstention reasons,
confidence block, certainty bands, and the opt-in advisory draft."""
from __future__ import annotations

from sebi_rag.embeddings import HashEmbedder
from sebi_rag.generate import (
    ABSTAIN,
    ADVISORY_PREFIX,
    ExtractiveStubGenerator,
    SubjectSimJudge,
    answer_with_abstention,
)
from sebi_rag.segment import Chunk


def _chunk(subject: str = "nomination norms for demat accounts") -> Chunk:
    return Chunk(id="SEBI/X/1#s#0", doc_id="SEBI/X/1", section="SEBI/X/1/s/p0",
                 text="Provision text about nomination.", meta={"subject": subject})


GEN = ExtractiveStubGenerator()


def test_no_context_reason_when_top_k_zero():
    ans = answer_with_abstention("q", [(_chunk(), 0.99)], GEN, threshold=0.05,
                                 top_k=0)
    assert ans.abstained and ans.abstention_reason == "no_context"
    assert ans.certainty == "low" and ans.draft_answer == ""
    assert ans.confidence["rerank_top"] == 0.99  # signals populated even on abstain


def test_score_floor_reason():
    ans = answer_with_abstention("q", [(_chunk(), 0.01)], GEN, threshold=0.05)
    assert ans.abstained and ans.abstention_reason == "score_floor"


def test_subject_gate_reason_and_subject_sim_recorded():
    judge = SubjectSimJudge(HashEmbedder(), threshold=0.99)  # force gate fail
    ans = answer_with_abstention("totally unrelated query terms",
                                 [(_chunk(), 0.9)], GEN, threshold=0.05,
                                 judge=judge)
    assert ans.abstained and ans.abstention_reason == "subject_gate"
    assert ans.confidence["subject_sim"] is not None


def test_certainty_high_when_subject_sim_strong_and_faithful():
    judge = SubjectSimJudge(HashEmbedder(), threshold=0.3)
    ans = answer_with_abstention("nomination norms for demat accounts",
                                 [(_chunk(), 0.95)], GEN, threshold=0.05,
                                 judge=judge)
    assert not ans.abstained
    assert ans.confidence["subject_sim"] >= 0.65
    assert ans.certainty == "high" and ans.abstention_reason == ""


def test_certainty_capped_medium_without_gate():
    ans = answer_with_abstention("q", [(_chunk(), 0.95)], GEN, threshold=0.05)
    assert not ans.abstained and ans.certainty == "medium"


def test_advisory_draft_on_gate_failure_only_when_requested():
    judge = SubjectSimJudge(HashEmbedder(), threshold=0.99)
    plain = answer_with_abstention("unrelated", [(_chunk(), 0.9)], GEN,
                                   threshold=0.05, judge=judge)
    assert plain.draft_answer == ""
    adv = answer_with_abstention("unrelated", [(_chunk(), 0.9)], GEN,
                                 threshold=0.05, judge=judge, advisory=True)
    assert adv.abstained and adv.text == ABSTAIN          # authoritative fields untouched
    assert adv.draft_answer.startswith(ADVISORY_PREFIX)   # labelled draft present
    # advisory never produces a draft for no_context (nothing to ground it on)
    nc = answer_with_abstention("q", [], GEN, threshold=0.05, advisory=True)
    assert nc.abstention_reason == "no_context" and nc.draft_answer == ""
