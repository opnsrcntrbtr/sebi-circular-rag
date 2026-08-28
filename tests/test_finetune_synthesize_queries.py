"""Offline tests for scripts/finetune/synthesize_queries.py. The candidate
generators are pure transforms (real inputs, no network); the oMLX
transport is tested with a stubbed httpx.post, matching the pattern
established for local_adjudicate.py's own transport tests - never a live
server in this suite.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from finetune import synthesize_queries as sq  # noqa: E402
from finetune.mine_structural_pairs import MIN_CHUNK_CHARS  # noqa: E402

LONG = "x" * MIN_CHUNK_CHARS


# ---------------------------------------------------------------------------
# numeric_table_candidates
# ---------------------------------------------------------------------------

def test_numeric_table_candidates_keeps_only_numeric_dense_chunks():
    chunks_by_doc = {
        "A": [{"id": "A#1", "doc_id": "A", "section": "A/1",
              "text": "not exceeding 10% of the total amount " + LONG},
             {"id": "A#2", "doc_id": "A", "section": "A/2",
              "text": "plain text with no figures at all " + LONG}],
    }
    cands = sq.numeric_table_candidates(chunks_by_doc, minable={"A"}, seed=1)
    assert len(cands) == 1
    assert cands[0]["source_id"] == "A#1"
    assert cands[0]["positive"] == cands[0]["prompt_body"]


def test_numeric_table_candidates_skips_held_out_docs():
    chunks_by_doc = {"A": [{"id": "A#1", "doc_id": "A", "section": "A/1",
                           "text": "not exceeding 10% " + LONG}]}
    assert sq.numeric_table_candidates(chunks_by_doc, minable=set(), seed=1) == []


def test_numeric_table_candidates_strips_context_header():
    chunks_by_doc = {"A": [{"id": "A#1", "doc_id": "A", "section": "A/1",
                           "text": "A | Some subject | A/1\nnot exceeding 10% " + LONG}]}
    cands = sq.numeric_table_candidates(chunks_by_doc, minable={"A"}, seed=1)
    assert "A | Some subject" not in cands[0]["positive"]


def test_numeric_table_candidates_below_length_floor_excluded():
    chunks_by_doc = {"A": [{"id": "A#1", "doc_id": "A", "section": "A/1",
                           "text": "not exceeding 10%"}]}  # short
    assert sq.numeric_table_candidates(chunks_by_doc, minable={"A"}, seed=1) == []


# ---------------------------------------------------------------------------
# multi_hop_candidates (wraps export_datasets.build_citation_pairs)
# ---------------------------------------------------------------------------

def test_multi_hop_candidates_builds_both_passages():
    corpus = [
        {"circular_number": "SEBI/HO/CFD/2023/1", "subject": "Citing circular",
         "text": "This refers to SEBI/HO/CFD/2023/2 for details."},
        {"circular_number": "SEBI/HO/CFD/2023/2", "subject": "Cited circular subject",
         "text": "unrelated"},
    ]
    chunks_by_doc = {"SEBI/HO/CFD/2023/2": [
        {"id": "c2#1", "doc_id": "SEBI/HO/CFD/2023/2", "section": "s/1",
         "text": "the cited body text " + LONG}]}
    minable = {"SEBI/HO/CFD/2023/1", "SEBI/HO/CFD/2023/2"}
    cands = sq.multi_hop_candidates(corpus, chunks_by_doc, minable, seed=1)
    assert len(cands) == 1
    assert "Passage A (citing)" in cands[0]["prompt_body"]
    assert "Passage B (cited)" in cands[0]["prompt_body"]
    assert cands[0]["positive"] in cands[0]["prompt_body"]
    assert cands[0]["source_doc"] == "SEBI/HO/CFD/2023/1"


def test_multi_hop_candidates_skips_when_cited_doc_has_no_usable_chunks():
    corpus = [
        {"circular_number": "SEBI/HO/CFD/2023/1", "subject": "Citing",
         "text": "This refers to SEBI/HO/CFD/2023/2 for details."},
        {"circular_number": "SEBI/HO/CFD/2023/2", "subject": "Cited", "text": ""},
    ]
    minable = {"SEBI/HO/CFD/2023/1", "SEBI/HO/CFD/2023/2"}
    cands = sq.multi_hop_candidates(corpus, {}, minable, seed=1)
    assert cands == []


def test_multi_hop_candidates_skips_held_out_target():
    corpus = [
        {"circular_number": "SEBI/HO/CFD/2023/1", "subject": "Citing",
         "text": "This refers to SEBI/HO/CFD/2023/2 for details."},
        {"circular_number": "SEBI/HO/CFD/2023/2", "subject": "Cited", "text": "x"},
    ]
    chunks_by_doc = {"SEBI/HO/CFD/2023/2": [
        {"id": "c2#1", "doc_id": "SEBI/HO/CFD/2023/2", "section": "s/1", "text": LONG}]}
    cands = sq.multi_hop_candidates(corpus, chunks_by_doc, minable={"SEBI/HO/CFD/2023/1"}, seed=1)
    assert cands == []


# ---------------------------------------------------------------------------
# lineage_supersession_candidates (wraps export_datasets.build_supersession_pairs)
# ---------------------------------------------------------------------------

def test_lineage_supersession_candidates_current_is_positive():
    corpus = [
        {"circular_number": "NEW/1", "subject": "New rule", "issuing_department": "CFD"},
        {"circular_number": "OLD/1", "subject": "Old rule", "issuing_department": "CFD"},
    ]
    lineage = {"supersedes": {"NEW/1": ["OLD/1"]}, "amends": {},
              "superseded_by": {}, "amended_by": {}}
    chunks_by_doc = {
        "NEW/1": [{"id": "n#1", "doc_id": "NEW/1", "section": "s/1", "text": "new body " + LONG}],
        "OLD/1": [{"id": "o#1", "doc_id": "OLD/1", "section": "s/1", "text": "old body " + LONG}],
    }
    cands = sq.lineage_supersession_candidates(
        corpus, chunks_by_doc, lineage, minable={"NEW/1", "OLD/1"}, seed=1)
    assert len(cands) == 1
    assert cands[0]["positive"].startswith("new body")
    assert "Current passage" in cands[0]["prompt_body"]
    assert "Earlier passage" in cands[0]["prompt_body"]
    assert cands[0]["source_doc"] == "NEW/1"


def test_lineage_supersession_candidates_drops_unrelated_label():
    corpus = [
        {"circular_number": "A/1", "subject": "s1", "issuing_department": "CFD"},
        {"circular_number": "B/1", "subject": "s2", "issuing_department": "CFD"},
    ]
    lineage = {"supersedes": {}, "amends": {}, "superseded_by": {}, "amended_by": {}}
    cands = sq.lineage_supersession_candidates(
        corpus, {}, lineage, minable={"A/1", "B/1"}, seed=1)
    assert cands == []  # no supersedes/amends edge -> build_supersession_pairs
                        # only emits "unrelated" rows, which are dropped


# ---------------------------------------------------------------------------
# _extract_json_query - defensive parsing (no server-side JSON schema)
# ---------------------------------------------------------------------------

def test_extract_json_query_clean_json():
    assert sq._extract_json_query('{"query": "What is the threshold?"}') == "What is the threshold?"


def test_extract_json_query_json_wrapped_in_prose():
    text = 'Sure, here you go: {"query": "What is the deadline?"} Hope that helps!'
    assert sq._extract_json_query(text) == "What is the deadline?"


def test_extract_json_query_markdown_fenced():
    text = '```json\n{"query": "What is the cap?"}\n```'
    assert sq._extract_json_query(text) == "What is the cap?"


def test_extract_json_query_strips_thinking_block_first():
    text = '<think>reasoning about the question</think>\n{"query": "What applies here?"}'
    assert sq._extract_json_query(text) == "What applies here?"


def test_extract_json_query_regex_fallback_on_malformed_json():
    text = '{"query": "What is the limit?" some trailing garbage that breaks json.loads'
    assert sq._extract_json_query(text) == "What is the limit?"


def test_extract_json_query_returns_none_when_nothing_parseable():
    assert sq._extract_json_query("no json anywhere here") is None


def test_extract_json_query_returns_none_for_empty_query_field():
    assert sq._extract_json_query('{"query": ""}') is None


# ---------------------------------------------------------------------------
# cache_path - keyed by (source_id, model), stratum-namespaced
# ---------------------------------------------------------------------------

def test_cache_path_is_deterministic_for_same_inputs(tmp_path):
    p1 = sq.cache_path(tmp_path, "numeric_table", "A#1", "model-x")
    p2 = sq.cache_path(tmp_path, "numeric_table", "A#1", "model-x")
    assert p1 == p2


def test_cache_path_differs_by_stratum_namespace(tmp_path):
    p1 = sq.cache_path(tmp_path, "numeric_table", "A#1", "model-x")
    p2 = sq.cache_path(tmp_path, "multi_hop", "A#1", "model-x")
    assert p1.parent != p2.parent


def test_cache_path_differs_by_model():
    p1 = sq.cache_path(Path("/c"), "numeric_table", "A#1", "model-x")
    p2 = sq.cache_path(Path("/c"), "numeric_table", "A#1", "model-y")
    assert p1 != p2


# ---------------------------------------------------------------------------
# call_omlx transport - stubbed httpx, matching local_adjudicate.py's pattern
# ---------------------------------------------------------------------------

class _FakeResponse:
    def __init__(self, status_code, payload, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text or json.dumps(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            import httpx
            raise httpx.HTTPStatusError("boom", request=None, response=self)


def _ok_payload(content="hello"):
    return {"choices": [{"message": {"role": "assistant", "content": content}}]}


def test_call_omlx_sends_pinned_sampling_params(monkeypatch):
    seen = {}

    def _fake_post(url, headers, json, timeout):
        seen["json"] = json
        return _FakeResponse(200, _ok_payload())

    monkeypatch.setattr(sq.httpx, "post", _fake_post)
    monkeypatch.delenv("SYNTH_AUTH_TOKEN", raising=False)

    sq.call_omlx("prompt", "http://x", "model-x", timeout_s=10)

    assert seen["json"]["temperature"] == sq.TEMPERATURE
    assert seen["json"]["top_p"] == sq.TOP_P
    assert seen["json"]["min_p"] == sq.MIN_P
    assert seen["json"]["repetition_penalty"] == sq.REPETITION_PENALTY
    assert seen["json"]["messages"] == [{"role": "user", "content": "prompt"}]


def test_call_omlx_no_token_sends_no_auth_header(monkeypatch):
    seen = {}

    def _fake_post(url, headers, json, timeout):
        seen["headers"] = headers
        return _FakeResponse(200, _ok_payload())

    monkeypatch.setattr(sq.httpx, "post", _fake_post)
    monkeypatch.delenv("SYNTH_AUTH_TOKEN", raising=False)

    sq.call_omlx("p", "http://x", "m", timeout_s=10)
    assert "Authorization" not in seen["headers"]


def test_call_omlx_never_reads_anthropic_auth_token(monkeypatch):
    """Security-relevant: base_url is CLI-configurable here (unlike
    local_adjudicate.py's fixed local target), so falling back to a
    broader credential would risk sending it to whatever host --base-url
    happens to point at. SYNTH_AUTH_TOKEN is the only credential this
    script will ever attach, even when ANTHROPIC_AUTH_TOKEN is set."""
    seen = {}

    def _fake_post(url, headers, json, timeout):
        seen["headers"] = headers
        return _FakeResponse(200, _ok_payload())

    monkeypatch.setattr(sq.httpx, "post", _fake_post)
    monkeypatch.delenv("SYNTH_AUTH_TOKEN", raising=False)
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "should-never-be-sent")

    sq.call_omlx("p", "http://x", "m", timeout_s=10)
    assert "Authorization" not in seen["headers"]


def test_call_omlx_retries_on_5xx(monkeypatch):
    calls = {"n": 0}

    def _fake_post(url, headers, json, timeout):
        calls["n"] += 1
        if calls["n"] < 2:
            return _FakeResponse(503, {}, text="unavailable")
        return _FakeResponse(200, _ok_payload("recovered"))

    monkeypatch.setattr(sq.httpx, "post", _fake_post)
    monkeypatch.setattr(sq.time, "sleep", lambda s: None)

    out = sq.call_omlx("p", "http://x", "m", timeout_s=10)
    assert out == "recovered"
    assert calls["n"] == 2


# ---------------------------------------------------------------------------
# synthesize_stratum - resumable cache, leak filter, stratum stamping
# ---------------------------------------------------------------------------

def test_synthesize_stratum_uses_cache_when_present(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    cpath = sq.cache_path(cache_dir, "numeric_table", "A#1", "m")
    cpath.parent.mkdir(parents=True)
    cpath.write_text(json.dumps({"source_id": "A#1", "model": "m",
                                 "reply": "x", "query": "cached question"}),
                     encoding="utf-8")

    def _boom(*a, **k):
        raise AssertionError("call_omlx must not be called for a cached row")
    monkeypatch.setattr(sq, "call_omlx", _boom)

    cands = [{"source_id": "A#1", "prompt_body": "p", "positive": "pos", "source_doc": "A"}]
    rows = sq.synthesize_stratum("numeric_table", cands, target=1,
                                 base_url="http://x", model="m",
                                 cache_dir=cache_dir, timeout_s=10)
    assert rows[0]["query"] == "cached question"
    assert rows[0]["template"] == "numeric_table"


def test_synthesize_stratum_stops_at_target(tmp_path, monkeypatch):
    def _fake_call(prompt, base_url, model, timeout_s):
        return '{"query": "a question about the rule"}'
    monkeypatch.setattr(sq, "call_omlx", _fake_call)

    cands = [{"source_id": f"A#{i}", "prompt_body": "p", "positive": "pos",
             "source_doc": "A"} for i in range(10)]
    rows = sq.synthesize_stratum("numeric_table", cands, target=3,
                                 base_url="http://x", model="m",
                                 cache_dir=tmp_path / "cache", timeout_s=10)
    assert len(rows) == 3


def test_synthesize_stratum_drops_leak_filtered_and_parse_failed(tmp_path, monkeypatch):
    replies = iter([
        '{"query": "issued on 2023-07-13"}',  # metadata leak -> dropped
        'not json at all',                     # parse fail -> dropped
        '{"query": "a clean question"}',       # kept
    ])

    def _fake_call(prompt, base_url, model, timeout_s):
        return next(replies)
    monkeypatch.setattr(sq, "call_omlx", _fake_call)

    cands = [{"source_id": f"A#{i}", "prompt_body": "p", "positive": "pos",
             "source_doc": "A"} for i in range(3)]
    rows = sq.synthesize_stratum("numeric_table", cands, target=3,
                                 base_url="http://x", model="m",
                                 cache_dir=tmp_path / "cache", timeout_s=10)
    assert len(rows) == 1
    assert rows[0]["query"] == "a clean question"


def test_synthesize_stratum_never_reads_a_model_emitted_type_field(tmp_path, monkeypatch):
    """The plan's own finding: self-assigned stratum labels are unreliable.
    Even if the model emits a "type" field in its JSON, it must be ignored -
    the row's template always comes from which loop/preamble ran."""
    def _fake_call(prompt, base_url, model, timeout_s):
        return '{"query": "a clean question", "type": "multi_hop"}'
    monkeypatch.setattr(sq, "call_omlx", _fake_call)

    cands = [{"source_id": "A#1", "prompt_body": "p", "positive": "pos", "source_doc": "A"}]
    rows = sq.synthesize_stratum("numeric_table", cands, target=1,
                                 base_url="http://x", model="m",
                                 cache_dir=tmp_path / "cache", timeout_s=10)
    assert rows[0]["template"] == "numeric_table"  # not "multi_hop"
