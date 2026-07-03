"""Offline tests for the groundedness abstention gate (ADR-001 item 7)."""
from __future__ import annotations

from sebi_rag.generate import (
    ABSTAIN,
    ExtractiveStubGenerator,
    _judge_prompt_identify,
    answer_with_abstention,
    parse_excerpt_choice,
    parse_yes_no,
)
from sebi_rag.segment import Chunk


def _chunk(cid: str = "SEBI/X/1#s#0") -> Chunk:
    return Chunk(id=cid, doc_id="SEBI/X/1", section="SEBI/X/1/s/p0",
                 text="Provision text.")


class _StubJudge:
    def __init__(self, verdict: bool) -> None:
        self.verdict = verdict
        self.calls = 0

    def grounded(self, query, contexts) -> bool:
        self.calls += 1
        return self.verdict


def test_parse_yes_no():
    assert parse_yes_no("Yes") and parse_yes_no("yes.") and parse_yes_no(" YES\n")
    assert not parse_yes_no("No") and not parse_yes_no("no, it does not")
    assert parse_yes_no("maybe")  # unparseable fails open (documented)
    assert not parse_yes_no("Answer: no")


def test_parse_excerpt_choice_fails_closed():
    assert parse_excerpt_choice("2", 3) and parse_excerpt_choice("Excerpt 1.", 3)
    assert not parse_excerpt_choice("none", 3)
    assert not parse_excerpt_choice("None of the excerpts", 3)
    assert not parse_excerpt_choice("4", 3)      # out of range
    assert not parse_excerpt_choice("maybe?", 3)  # unparseable -> not grounded


def test_identify_prompt_numbers_excerpts():
    p = _judge_prompt_identify("q", [_chunk("A/1#s#0"), _chunk("B/2#s#0")])
    assert "[1] (circular SEBI/X/1)" in p and "[2] (circular SEBI/X/1)" in p
    assert "excerpt number (1-2)" in p and "none" in p


def test_judge_no_forces_abstention():
    reranked = [(_chunk(), 0.95)]
    ans = answer_with_abstention("q", reranked, ExtractiveStubGenerator(),
                                 threshold=0.4, judge=_StubJudge(False))
    assert ans.abstained and ans.text == ABSTAIN and ans.citations == []


def test_judge_yes_answers_normally():
    reranked = [(_chunk(), 0.95)]
    j = _StubJudge(True)
    ans = answer_with_abstention("q", reranked, ExtractiveStubGenerator(),
                                 threshold=0.4, judge=j)
    assert not ans.abstained and j.calls == 1


def test_score_gate_short_circuits_judge():
    reranked = [(_chunk(), 0.1)]
    j = _StubJudge(True)
    ans = answer_with_abstention("q", reranked, ExtractiveStubGenerator(),
                                 threshold=0.4, judge=j)
    assert ans.abstained and j.calls == 0  # judge never invoked below threshold


def test_subject_sim_judge_separates_by_subject():
    from sebi_rag.embeddings import HashEmbedder
    from sebi_rag.generate import SubjectSimJudge

    emb = HashEmbedder()
    on_topic = Chunk(id="A#s#0", doc_id="A", section="A/s/p0", text="x",
                     meta={"subject": "nomination norms for demat accounts"})
    off_topic = Chunk(id="B#s#0", doc_id="B", section="B/s/p0", text="x",
                      meta={"subject": "registrars share transfer agents duties"})
    j = SubjectSimJudge(emb, threshold=0.3)
    assert j.grounded("nomination norms for demat accounts", [on_topic])
    assert not j.grounded("nomination norms for demat accounts", [off_topic])
    assert not j.grounded("anything", [])  # no context -> not grounded
    # cache: second call reuses the subject vector (no error, same verdict)
    assert j.grounded("nomination norms for demat accounts", [on_topic])


def test_subject_sim_judge_two_tier_section_gate():
    from sebi_rag.embeddings import HashEmbedder
    from sebi_rag.generate import SubjectSimJudge

    emb = HashEmbedder()
    # doc subject unrelated to query; SECTION heading matches (the
    # "definition inside a master circular" case)
    c = Chunk(id="M/1#3. regulated entity definition#0", doc_id="M/1",
              section="M/1/3. regulated entity definition/p0", text="x",
              meta={"subject": "master circular for stock brokers"})
    q = "regulated entity definition"
    off = SubjectSimJudge(emb, threshold=0.5, section_threshold=None)
    two_tier = SubjectSimJudge(emb, threshold=0.5, section_threshold=0.5)
    assert not off.grounded(q, [c])         # doc subject can't see it
    assert two_tier.grounded(q, [c])        # section tier can
    assert two_tier._section_heading(c) == "3. regulated entity definition"
    assert two_tier.section_score(q, [c]) > two_tier.score(q, [c])
    # section tier requires ITS OWN bar — a weak section match doesn't pass
    strict = SubjectSimJudge(emb, threshold=0.5, section_threshold=0.999)
    assert not strict.grounded(q, [c])


def test_no_judge_preserves_legacy_behaviour():
    reranked = [(_chunk(), 0.95)]
    ans = answer_with_abstention("q", reranked, ExtractiveStubGenerator(),
                                 threshold=0.4)
    assert not ans.abstained
