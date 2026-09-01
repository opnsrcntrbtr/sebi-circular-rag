"""Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen)
external annotation leg that replaces the quota-blocked Gemini leg as
primary. The blind protocol itself lives in gemini_adjudicate.py and is
already covered there; these tests pin what is NEW here: the "qwen"
annotator identity, model provenance in cache entries, OpenAI
chat-completions response extraction, thinking-block stripping, the
pilot comparison path, and the transport (auth-optional, retry-on-5xx,
OpenAI request body) since the 2026-08-28 swap off the Anthropic-proxy
transport onto oMLX's /v1/chat/completions directly.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7 import local_adjudicate  # noqa: E402
from golden_v7.local_adjudicate import (  # noqa: E402
    ANNOTATOR,
    _extract_text,
    _post_local,
    _strip_thinking,
    pilot,
)
from golden_v7.gemini_adjudicate import adjudicate  # noqa: E402


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
# (a) annotator identity + model provenance (via the shared adjudicate())
# ---------------------------------------------------------------------------

def test_adjudicate_with_qwen_annotator_and_model_stamps_both(tmp_path):
    """Vote records must say annotator "qwen" (never reuse "gemini" - the
    agreement report is a permanent artifact and its provenance must be
    honest), and cache entries must record the local model id, not the
    gemini module's default."""
    rows = [_row(id="r1")]
    pools = [_pool("r1", n=2)]
    cache_dir = tmp_path / "qwen"

    votes = adjudicate(rows, pools, ["r1"], lambda p: "A\nEXPECTED: x",
                       cache_dir=cache_dir, annotator=ANNOTATOR,
                       model="Qwen3.6-35B-A3B-MLX-4bit")
    assert votes[0]["annotator"] == "qwen"
    cached = json.loads((cache_dir / "r1.json").read_text())
    assert cached["model"] == "Qwen3.6-35B-A3B-MLX-4bit"


def test_adjudicate_default_annotator_stays_gemini(tmp_path):
    """Back-compat guard: the gemini leg (on hold, not removed) must keep
    producing annotator "gemini" without changes at its call sites."""
    votes = adjudicate([_row(id="r1")], [_pool("r1", n=2)], ["r1"],
                       lambda p: "A\nEXPECTED: x", cache_dir=tmp_path / "g")
    assert votes[0]["annotator"] == "gemini"


# ---------------------------------------------------------------------------
# (b) OpenAI chat-completions response extraction + thinking-strip
# ---------------------------------------------------------------------------

def test_extract_text_reads_first_choice_message_content():
    payload = {"choices": [
        {"message": {"role": "assistant",
                     "content": "B, C\nEXPECTED: twenty per cent"}},
    ]}
    assert _extract_text(payload) == "B, C\nEXPECTED: twenty per cent"


def test_extract_text_empty_choices_returns_empty_string():
    assert _extract_text({"choices": []}) == ""
    assert _extract_text({}) == ""


def test_strip_thinking_removes_inline_think_tags():
    """Qwen-family models may emit <think>...</think> as inline text rather
    than as separate content blocks, depending on the server's template.
    The strict parser reads the FIRST non-blank line as the letter choice,
    so unstripped reasoning would fail-closed every single row."""
    reply = "<think>\nA discusses fees... B carries the provision.\n</think>\nB\nEXPECTED: fee cap"
    assert _strip_thinking(reply) == "B\nEXPECTED: fee cap"


def test_strip_thinking_leaves_plain_replies_untouched():
    assert _strip_thinking("NONE\nEXPECTED:") == "NONE\nEXPECTED:"


# ---------------------------------------------------------------------------
# (c) transport: OpenAI request body, optional auth, retry-on-5xx
#     (2026-08-28 swap off the Anthropic-proxy transport onto oMLX's
#     /v1/chat/completions directly - skip_api_key_verification means an
#     unset token must NOT raise, unlike the old hard RuntimeError)
# ---------------------------------------------------------------------------

class _FakeResponse:
    def __init__(self, status_code: int, payload: dict, text: str = ""):
        self.status_code = status_code
        self._payload = payload
        self.text = text or json.dumps(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("boom", request=None, response=self)


def _ok_payload(text="A\nEXPECTED: x"):
    return {"choices": [{"message": {"role": "assistant", "content": text}}]}


def test_post_local_sends_openai_body_to_chat_completions(monkeypatch):
    seen = {}

    def _fake_post(url, headers, json, timeout):  # noqa: A002 - mirror httpx kwarg
        seen["url"] = url
        seen["headers"] = headers
        seen["json"] = json
        return _FakeResponse(200, _ok_payload())

    monkeypatch.setattr(local_adjudicate.httpx, "post", _fake_post)
    monkeypatch.setattr(local_adjudicate, "_current_model", lambda: "Qwen3.8-27B-oQ4e-mtp")
    monkeypatch.delenv("GOLDEN_LOCAL_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)

    out = _post_local("prompt text")

    assert out == "A\nEXPECTED: x"
    assert seen["url"] == "http://127.0.0.1:8001/v1/chat/completions"
    assert seen["json"]["model"] == "Qwen3.8-27B-oQ4e-mtp"
    assert seen["json"]["messages"] == [{"role": "user", "content": "prompt text"}]


def test_post_local_without_token_succeeds_and_sends_no_auth_header(monkeypatch):
    """oMLX's skip_api_key_verification is on: an unset token is not an
    error, it just means no Authorization header goes out."""
    seen = {}

    def _fake_post(url, headers, json, timeout):
        seen["headers"] = headers
        return _FakeResponse(200, _ok_payload())

    monkeypatch.setattr(local_adjudicate.httpx, "post", _fake_post)
    monkeypatch.delenv("GOLDEN_LOCAL_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)

    out = _post_local("prompt text")

    assert out == "A\nEXPECTED: x"
    assert "Authorization" not in seen["headers"]


def test_post_local_with_token_sends_bearer_header(monkeypatch):
    seen = {}

    def _fake_post(url, headers, json, timeout):
        seen["headers"] = headers
        return _FakeResponse(200, _ok_payload())

    monkeypatch.setattr(local_adjudicate.httpx, "post", _fake_post)
    monkeypatch.setenv("GOLDEN_LOCAL_AUTH_TOKEN", "tok-123")

    _post_local("prompt text")

    assert seen["headers"]["Authorization"] == "Bearer tok-123"


def test_post_local_retries_on_5xx_then_succeeds(monkeypatch):
    calls = {"n": 0}

    def _fake_post(url, headers, json, timeout):
        calls["n"] += 1
        if calls["n"] < 2:
            return _FakeResponse(503, {}, text="service unavailable")
        return _FakeResponse(200, _ok_payload("B\nEXPECTED: y"))

    monkeypatch.setattr(local_adjudicate.httpx, "post", _fake_post)
    monkeypatch.setattr(local_adjudicate.time, "sleep", lambda s: None)
    monkeypatch.delenv("GOLDEN_LOCAL_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)

    out = _post_local("prompt text")

    assert out == "B\nEXPECTED: y"
    assert calls["n"] == 2


def test_post_local_strips_thinking_from_openai_content(monkeypatch):
    def _fake_post(url, headers, json, timeout):
        return _FakeResponse(200, _ok_payload(
            "<think>reasoning here</think>\nC\nEXPECTED: z"))

    monkeypatch.setattr(local_adjudicate.httpx, "post", _fake_post)
    monkeypatch.delenv("GOLDEN_LOCAL_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)

    assert _post_local("prompt text") == "C\nEXPECTED: z"


# ---------------------------------------------------------------------------
# (d) pilot - measured agreement before the full run, no votes.jsonl writes
# ---------------------------------------------------------------------------

def test_pilot_compares_against_claude_and_never_writes_votes(tmp_path):
    rows = [_row(id="r1"), _row(id="r2", task_type="numeric_table"),
            _row(id="r3", task_type="hard_negative", abstain=True)]
    pools = [_pool("r1", n=2), _pool("r2", n=2)]
    claude_votes = {"r1": ["r1-doc0#s#0"], "r2": ["r2-doc1#s#1"]}
    cache_dir = tmp_path / "qwen"

    # deterministic fake: always picks letter A
    results = pilot(rows, pools, ["r1", "r2", "r3"], claude_votes,
                    lambda p: "A\nEXPECTED: x", n=2, cache_dir=cache_dir)

    assert len(results) == 2                      # abstain row r3 not eligible
    assert {r["id"] for r in results} == {"r1", "r2"}
    for r in results:
        assert set(r) >= {"id", "task_type", "claude", "qwen", "match"}
        assert isinstance(r["match"], bool)
    # nothing outside the cache dir was touched
    assert list(tmp_path.iterdir()) == [cache_dir]


def test_pilot_prefers_distinct_strata_first(tmp_path):
    """Five pilot rows from five strata measure more than five from one -
    the gemini probe caught its protocol bug precisely because it sampled
    across strata."""
    rows = [_row(id=f"r{i}", task_type="title_direct") for i in range(3)]
    rows += [_row(id="r3", task_type="numeric_table"),
             _row(id="r4", task_type="body_paraphrase")]
    pools = [_pool(r["id"], n=1) for r in rows]
    claude_votes = {r["id"]: ["x"] for r in rows}

    results = pilot(rows, pools, [r["id"] for r in rows], claude_votes,
                    lambda p: "A\nEXPECTED: x", n=3, cache_dir=tmp_path / "q")
    picked_types = [r["task_type"] for r in results]
    assert len(set(picked_types)) == 3            # one per stratum, not r0/r1/r2
