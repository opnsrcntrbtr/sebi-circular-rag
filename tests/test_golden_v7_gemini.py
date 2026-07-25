"""Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply
parsing, and cached adjudication (spec 2026-07-23 sec 7; plan Task 10)."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.gemini_adjudicate import (  # noqa: E402
    _parse_error_ids,
    _replace_annotator_votes,
    _should_retry,
    adjudicate,
    build_prompt,
    parse_reply,
)

ROOT = Path(__file__).resolve().parents[1]


def _row(**over):
    base = {"id": "v7-td-001", "query": "What does this circular cover?",
            "task_type": "title_direct", "abstain": False}
    base.update(over)
    return base


def _pool(row_id: str, n: int = 3) -> dict:
    return {"id": row_id, "candidates": [
        {"chunk_id": f"{row_id}-doc{i}#s#{i}", "doc": f"{row_id}-doc{i}",
         "text": f"excerpt body text number {i} about margin rules " * 2}
        for i in range(n)]}


# ---------------------------------------------------------------------------
# (a) build_prompt
# ---------------------------------------------------------------------------

def test_governing_prompt_carries_the_spec_sec6_strictness_bar():
    """The claude annotator (Task 8) judged under an explicit bar: a chunk is
    governing iff its text contains the provision that answers the query,
    and "topical relatedness is NOT enough". The gemini prompt originally
    said only "the governing provision", so the two annotators were answering
    materially different questions - a 5-row probe on 2026-07-26 measured 0/5
    exact-set agreement, with gemini returning a strict superset of claude's
    pick on 3 of 5. Agreement is only evidence when both raters were asked
    the same question, so the bar must appear in the prompt itself."""
    prompt = build_prompt(_row(), _pool("v7-td-001", n=2))
    lowered = prompt.lower()
    assert "topical relatedness is not enough" in lowered
    assert "operative provision" in lowered


def test_governing_prompt_does_not_leak_how_many_chunks_usually_govern():
    """Guard against the tempting-but-circular fix: claude's labels are
    mostly single-chunk, so telling gemini "usually exactly one governs"
    would raise agreement by feeding claude's own answer distribution back
    into the supposedly independent leg. The prompt ports the DEFINITION
    only - anything about cardinality is leakage, not calibration."""
    lowered = build_prompt(_row(), _pool("v7-td-001", n=2)).lower()
    for leak in ("usually one", "usually exactly one", "typically one",
                 "select one", "only one excerpt"):
        assert leak not in lowered


def test_should_retry_only_on_transient_statuses():
    for status in (429, 500, 502, 503, 504):
        assert _should_retry(status), status
    for status in (200, 400, 401, 403, 404):
        assert not _should_retry(status), status


def test_build_prompt_contains_every_letter_and_excerpt_no_scores_or_ranks():
    row = _row()
    pool = _pool(row["id"], n=3)
    prompt = build_prompt(row, pool)

    for letter in ("A", "B", "C"):
        assert f"{letter}." in prompt
    for cand in pool["candidates"]:
        assert cand["text"] in prompt
        assert cand["doc"] in prompt

    # anti-leakage: no scores/ranks/system-favoritism hints (Task 9 bar)
    assert "score" not in prompt.lower()
    assert "rank" not in prompt.lower()
    assert row["query"] in prompt


def test_build_prompt_abstain_row_has_no_excerpts_and_uses_yes_no_protocol():
    row = _row(id="v7-hn-001", task_type="hard_negative", abstain=True)
    prompt = build_prompt(row, None)

    assert "answerable from sebi circulars" in prompt.lower()
    assert "yes or no" in prompt.lower()
    # no lettered options anywhere - nothing was offered to choose from
    assert "A." not in prompt
    assert "score" not in prompt.lower()
    assert "rank" not in prompt.lower()


def test_abstain_prompt_tells_model_to_blank_expected_on_no():
    """Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as
    "confirms abstain" and a non-blank one as "disputes it" (mirroring
    Task 9's human protocol) - but nothing forced the MODEL to actually
    leave it blank when answering NO. A NO reply with non-blank filler text
    after EXPECTED (e.g. "N/A") would silently parse as a dispute of a
    correct abstain answer. The prompt itself must instruct the model to
    leave EXPECTED blank on NO; this asserts that instruction is present in
    the rendered prompt text, and that the parser's behavior on a reply
    that ignores it is exactly the failure mode the instruction exists to
    prevent (documenting why the instruction is load-bearing, not
    decorative)."""
    row = _row(id="v7-hn-001", task_type="hard_negative", abstain=True)
    prompt = build_prompt(row, None)
    assert "if your answer is no, leave expected blank" in prompt.lower()

    # the failure mode itself, if a model ignores the instruction above:
    # NO + non-blank filler after EXPECTED still parses as a dispute, not
    # a confirm - this is exactly why the instruction must be present.
    assert parse_reply("NO\nEXPECTED: N/A", []) == ([], "N/A")


def test_build_prompt_zero_candidate_pool_also_uses_yes_no_protocol():
    """A non-abstain row whose pool happens to have zero candidates can't
    offer any lettered choice either, so it degrades to the same abstain-
    style yes/no framing as a true abstain row."""
    row = _row(id="v7-td-002")
    pool = {"id": "v7-td-002", "candidates": []}
    prompt = build_prompt(row, pool)
    assert "yes or no" in prompt.lower()
    assert "A." not in prompt


def test_build_prompt_shuffle_is_deterministic_per_row_id():
    row = _row()
    pool = _pool(row["id"], n=4)
    assert build_prompt(row, pool) == build_prompt(row, pool)


# ---------------------------------------------------------------------------
# (b) parse_reply
# ---------------------------------------------------------------------------

def test_parse_reply_letters_and_expected():
    assert parse_reply("B, C\nEXPECTED: twenty per cent", ["A", "B", "C"]) == (
        ["B", "C"], "twenty per cent")


def test_parse_reply_none_means_no_governing_excerpt():
    assert parse_reply("NONE", ["A", "B", "C"]) == ([], "")


def test_parse_reply_garbage_is_unparseable():
    assert parse_reply("not sure what you mean by that", ["A", "B", "C"]) == ([], "")


def test_parse_reply_unknown_letter_fails_the_whole_reply_closed():
    """Decision #3: a valid letter alongside an unrecognized one invalidates
    the WHOLE reply rather than silently dropping just the bad one."""
    assert parse_reply("B, Z\nEXPECTED: x", ["A", "B", "C"]) == ([], "")


def test_parse_reply_single_letter_no_expected_line():
    assert parse_reply("A", ["A", "B", "C"]) == (["A"], "")


def test_parse_reply_empty_letters_dispatches_to_yes_no_protocol():
    """letters=[] is how adjudicate signals an abstain/zero-candidate row;
    parse_reply must switch protocols rather than treat every YES/NO answer
    as an unrecognized 'letter'."""
    assert parse_reply("YES\nEXPECTED: margin rules for brokers", []) == (
        [], "margin rules for brokers")
    assert parse_reply("NO\nEXPECTED:", []) == ([], "")
    assert parse_reply("gibberish", []) == ([], "")


# ---------------------------------------------------------------------------
# (c) adjudicate
# ---------------------------------------------------------------------------

def test_adjudicate_writes_votes_and_caches_then_zero_post_calls_on_rerun(tmp_path):
    rows = [_row(id="r1"), _row(id="r2", task_type="hard_negative", abstain=True)]
    pool_r1 = _pool("r1", n=2)
    pools = [pool_r1]
    ids = ["r1", "r2"]
    cache_dir = tmp_path / "gemini"

    # replicate the same shuffle adjudicate() must use, to know which real
    # chunk_id letter "B" refers to for r1 (precise mapping check, not just
    # "some valid chunk id" - a wrong mapping here would be a silent
    # correctness bug since the label would point at the wrong provision).
    shuffled = list(pool_r1["candidates"])
    random.Random("r1").shuffle(shuffled)
    letter_b_chunk = shuffled[1]["chunk_id"]

    replies = iter(["B\nEXPECTED: margin", "NO\nEXPECTED:"])
    calls = []

    def fake_post(prompt: str) -> str:
        calls.append(prompt)
        return next(replies)

    votes = adjudicate(rows, pools, ids, fake_post, cache_dir=cache_dir)

    assert len(calls) == 2
    v1 = next(v for v in votes if v["id"] == "r1")
    v2 = next(v for v in votes if v["id"] == "r2")
    assert v1 == {"id": "r1", "annotator": "gemini",
                  "governing": [letter_b_chunk], "expected_literal": "margin"}
    assert v2 == {"id": "r2", "annotator": "gemini",
                  "governing": [], "expected_literal": ""}

    assert (cache_dir / "r1.json").exists()
    assert (cache_dir / "r2.json").exists()
    cached_r1 = json.loads((cache_dir / "r1.json").read_text(encoding="utf-8"))
    cached_r2 = json.loads((cache_dir / "r2.json").read_text(encoding="utf-8"))
    assert cached_r1["parse_error"] is False
    assert cached_r2["parse_error"] is False  # well-formed "NO" is not an error

    # rerun: identical votes reconstructed from cache, zero new post() calls
    votes2 = adjudicate(rows, pools, ids, fake_post, cache_dir=cache_dir)
    assert len(calls) == 2  # unchanged
    assert votes2 == votes


def test_adjudicate_marks_parse_error_in_cache_for_garbage_reply(tmp_path):
    rows = [_row(id="r1")]
    pools = [_pool("r1", n=2)]
    cache_dir = tmp_path / "gemini"

    votes = adjudicate(rows, pools, ["r1"], lambda p: "garbled nonsense",
                        cache_dir=cache_dir)

    assert votes == [{"id": "r1", "annotator": "gemini", "governing": [],
                       "expected_literal": ""}]
    cached = json.loads((cache_dir / "r1.json").read_text(encoding="utf-8"))
    assert cached["parse_error"] is True


def test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply(tmp_path):
    """A garbled reply to an abstain-protocol (YES/NO) prompt is distinct
    from a well-formed 'NO' with a blank EXPECTED - both yield the same
    governing=[]/expected_literal="" vote record, but only the garbled one
    should be flagged parse_error in the cache for later human repair."""
    rows = [_row(id="r2", task_type="hard_negative", abstain=True)]
    cache_dir = tmp_path / "gemini"

    votes = adjudicate(rows, [], ["r2"], lambda p: "maybe? unclear",
                        cache_dir=cache_dir)

    assert votes == [{"id": "r2", "annotator": "gemini", "governing": [],
                       "expected_literal": ""}]
    cached = json.loads((cache_dir / "r2.json").read_text(encoding="utf-8"))
    assert cached["parse_error"] is True


def test_adjudicate_abstain_row_dispute_keeps_governing_empty(tmp_path):
    """A Gemini reply that disputes an abstain row (says YES, it IS
    answerable) writes free text into expected_literal - governing stays []
    since no excerpts were ever offered for an abstain-protocol row.
    Mirrors Task 9's human-abstain-protocol semantics exactly."""
    rows = [_row(id="r2", task_type="hard_negative", abstain=True)]
    cache_dir = tmp_path / "gemini"

    votes = adjudicate(
        rows, [], ["r2"],
        lambda p: "YES\nEXPECTED: actually the margin circular covers this",
        cache_dir=cache_dir)

    assert votes == [{"id": "r2", "annotator": "gemini", "governing": [],
                       "expected_literal": "actually the margin circular covers this"}]


def test_adjudicate_creates_cache_dir_if_missing(tmp_path):
    cache_dir = tmp_path / "does" / "not" / "exist" / "yet"
    rows = [_row(id="r2", task_type="hard_negative", abstain=True)]
    adjudicate(rows, [], ["r2"], lambda p: "NO\nEXPECTED:", cache_dir=cache_dir)
    assert cache_dir.is_dir()


# ---------------------------------------------------------------------------
# (d) _parse_error_ids (reviewer Important #2: surfacing parse errors that
# would otherwise be invisible outside the cache directory - this matters
# most for abstain rows, where a parse-error vote is byte-identical to a
# legitimate confirm-abstain vote and claude has no baseline to catch it).
# ---------------------------------------------------------------------------

def test_parse_error_ids_finds_only_the_flagged_rows(tmp_path):
    rows = [_row(id="r1"), _row(id="r2", task_type="hard_negative", abstain=True)]
    pools = [_pool("r1", n=2)]
    cache_dir = tmp_path / "gemini"

    def fake_post(prompt: str) -> str:
        # r1 gets a well-formed reply, r2 gets garbage -> only r2 should
        # be flagged.
        return "A\nEXPECTED: fine" if "Excerpts" in prompt else "unintelligible"

    adjudicate(rows, pools, ["r1", "r2"], fake_post, cache_dir=cache_dir)

    assert _parse_error_ids(["r1", "r2"], cache_dir) == ["r2"]


def test_parse_error_ids_empty_when_nothing_flagged(tmp_path):
    rows = [_row(id="r1")]
    pools = [_pool("r1", n=2)]
    cache_dir = tmp_path / "gemini"
    adjudicate(rows, pools, ["r1"], lambda p: "A\nEXPECTED: fine",
               cache_dir=cache_dir)

    assert _parse_error_ids(["r1"], cache_dir) == []


def test_parse_error_ids_skips_ids_with_no_cache_file(tmp_path):
    """Defensive: an id that was never adjudicated (no cache file at all)
    is not reported as a parse error - it's a different situation entirely
    and _parse_error_ids must not raise on it."""
    cache_dir = tmp_path / "gemini"
    cache_dir.mkdir(parents=True)
    assert _parse_error_ids(["never-ran"], cache_dir) == []


# ---------------------------------------------------------------------------
# (e) _replace_annotator_votes (votes.jsonl rerun-idempotency helper)
# ---------------------------------------------------------------------------

def test_replace_annotator_votes_drops_old_gemini_keeps_others_untouched():
    existing = [
        {"id": "a", "annotator": "claude", "governing": ["x"], "expected_literal": ""},
        {"id": "b", "annotator": "gemini", "governing": ["stale"], "expected_literal": "old"},
        {"id": "c", "annotator": "human", "governing": [], "expected_literal": ""},
    ]
    fresh = [{"id": "b", "annotator": "gemini", "governing": ["new"],
               "expected_literal": "new"},
              {"id": "d", "annotator": "gemini", "governing": [],
               "expected_literal": ""}]

    merged = _replace_annotator_votes(existing, fresh, "gemini")

    assert merged == [existing[0], existing[2], fresh[0], fresh[1]]


def test_replace_annotator_votes_on_empty_existing_just_returns_fresh():
    fresh = [{"id": "b", "annotator": "gemini", "governing": [], "expected_literal": ""}]
    assert _replace_annotator_votes([], fresh, "gemini") == fresh
