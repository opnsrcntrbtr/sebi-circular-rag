"""Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)."""
from __future__ import annotations

import json

import pytest

from sebi_rag import ui


def test_parse_as_of_empty_is_none():
    assert ui._parse_as_of("") is None
    assert ui._parse_as_of("   ") is None


def test_parse_as_of_valid_iso():
    assert ui._parse_as_of("2025-01-10") == "2025-01-10"


def test_parse_as_of_malformed_raises_valueerror():
    with pytest.raises(ValueError):
        ui._parse_as_of("10-01-2025")


class _Resp:
    status_code = 200

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


_CANNED = {
    "answer": "The nomination norms are X.",
    "citations_meta": [{"circular": "SEBI/2025/9", "status": "in_force", "superseded_by": []}],
    "latency_ms": 12.5,
    "faithfulness": 0.91,
    "certainty": "high",
    "abstained": False,
    "abstention_reason": "",
    "superseded": {},
    "unsupported_citations": [],
    "confidence": {"score": 0.8},
    "draft_answer": "",
    "retrieved": ["SEBI/2025/9#0"],
}


def test_submit_query_malformed_as_of_short_circuits(monkeypatch):
    called = {"n": 0}

    def _boom(*a, **k):
        called["n"] += 1
        raise AssertionError("httpx.post must not be called on bad as_of")

    monkeypatch.setattr(ui.httpx, "post", _boom)
    out = ui.submit_query("q", "http://x/query", "", 3, "rag", "10-01-2025", False)
    assert out[0].startswith("**Error:**")
    assert called["n"] == 0
    assert len(out) == 10


def test_submit_query_sends_new_fields_and_returns_ten(monkeypatch):
    seen = {}

    def _fake_post(url, json, headers, timeout):  # noqa: A002 - mirror httpx kwarg
        seen.update(json)
        return _Resp(_CANNED)

    monkeypatch.setattr(ui.httpx, "post", _fake_post)
    out = ui.submit_query("q", "http://x/query", "", 5, "rag", "2025-01-10", True)
    assert seen["mode"] == "rag"
    assert seen["advisory"] is True
    assert seen["as_of"] == "2025-01-10"
    assert seen["top_k"] == 5
    assert len(out) == 10
    assert out[0] == "The nomination norms are X."  # no banner in rag mode


def test_submit_query_retrieval_only_prepends_banner(monkeypatch):
    monkeypatch.setattr(ui.httpx, "post", lambda *a, **k: _Resp(_CANNED))
    out = ui.submit_query("q", "http://x/query", "", 3, "retrieval_only", "", False)
    assert out[0].startswith("**Retrieval-only mode**")
    assert "The nomination norms are X." in out[0]


def test_submit_query_surfaces_confidence_and_retrieved(monkeypatch):
    monkeypatch.setattr(ui.httpx, "post", lambda *a, **k: _Resp(_CANNED))
    out = ui.submit_query("q", "http://x/query", "", 3, "rag", "", False)
    confidence_json, draft_md, retrieved_json = out[7], out[8], out[9]
    assert json.loads(confidence_json) == {"score": 0.8}
    assert draft_md == ""  # empty draft renders nothing
    assert json.loads(retrieved_json) == ["SEBI/2025/9#0"]


def test_build_ui_constructs():
    demo = ui.build_ui()
    assert demo is not None
