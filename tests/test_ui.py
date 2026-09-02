"""Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)."""
from __future__ import annotations

import json

import pytest

from sebi_rag import ui

# Output arity: chatbot, citations_md, citations_df, latency, faithfulness,
# certainty, superseded, unsupported, confidence, draft (10) +
# MAX_PREVIEWS*2 preview components (20) + loading/latency/faithfulness/
# certainty badges (4) + retrieved (1) = 35. Every yield in
# submit_query_stream must produce a tuple of this length — a mismatch here
# is exactly the arity-parity bug class the app.py-side comments warn about.
_EXPECTED_ARITY = 10 + ui.MAX_PREVIEWS * 2 + 4 + 1


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
    "citations_meta": [{"circular": "SEBI/2025/9", "status": "in_force", "superseded_by": [],
                        "chunk_id": "SEBI/2025/9#0", "preview": "Nomination text excerpt."}],
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
    out = list(ui.submit_query_stream("q", "http://x/query", "", 3, "rag", "10-01-2025", False, []))
    assert out[0][0] == [
        {"role": "user", "content": "q"},
        {"role": "assistant", "content": "**Error:** 'As of date' must be YYYY-MM-DD."},
    ]
    assert called["n"] == 0
    assert len(out[0]) == _EXPECTED_ARITY


def test_submit_query_sends_new_fields_and_returns_correct_arity(monkeypatch):
    seen = {}

    def _fake_post(url, json, headers, timeout):  # noqa: A002 - mirror httpx kwarg
        seen.update(json)
        return _Resp(_CANNED)

    monkeypatch.setattr(ui.httpx, "post", _fake_post)
    out = list(ui.submit_query_stream("q", "http://x/query", "", 5, "rag", "2025-01-10", True, []))
    assert seen["mode"] == "rag"
    assert seen["advisory"] is True
    assert seen["as_of"] == "2025-01-10"
    assert seen["top_k"] == 5
    final = out[-1]
    assert len(final) == _EXPECTED_ARITY
    assert final[0][-1] == {"role": "assistant", "content": "The nomination norms are X."}


def test_submit_query_retrieval_only_prepends_banner(monkeypatch):
    monkeypatch.setattr(ui.httpx, "post", lambda *a, **k: _Resp(_CANNED))
    out = list(ui.submit_query_stream("q", "http://x/query", "", 3, "retrieval_only", "", False, []))
    final = out[-1]
    answer = final[0][-1]["content"]
    assert answer.startswith("**Retrieval-only mode**")
    assert "The nomination norms are X." in answer


def test_submit_query_surfaces_confidence_and_retrieved(monkeypatch):
    monkeypatch.setattr(ui.httpx, "post", lambda *a, **k: _Resp(_CANNED))
    out = list(ui.submit_query_stream("q", "http://x/query", "", 3, "rag", "", False, []))
    final = out[-1]
    # confidence, draft = final[8], final[9]; retrieved is the trailing element
    confidence_json, draft_md, retrieved_json = final[8], final[9], final[-1]
    assert json.loads(confidence_json) == {"score": 0.8}
    assert draft_md == ""  # empty draft renders nothing
    assert json.loads(retrieved_json) == ["SEBI/2025/9#0"]


def test_submit_query_all_yields_share_arity(monkeypatch):
    """Every yielded tuple — loading, streaming chunks, final — must match
    the output list arity wired up in build_ui(); a short tuple silently
    misassigns every downstream component."""
    monkeypatch.setattr(ui.httpx, "post", lambda *a, **k: _Resp(_CANNED))
    out = list(ui.submit_query_stream("q", "http://x/query", "", 3, "rag", "", False, []))
    assert len(out) > 1  # at least a streaming chunk + final yield
    for tup in out:
        assert len(tup) == _EXPECTED_ARITY


def test_submit_query_preview_matches_own_circular(monkeypatch):
    """Regression guard for the zip-misalignment class of bug (app.py:389):
    a citation's preview accordion must show its own chunk's text, not a
    different citation's, when multiple circulars are cited."""
    payload = dict(_CANNED)
    payload["citations_meta"] = [
        {"circular": "A", "status": "in_force", "superseded_by": [],
         "chunk_id": "A#1", "preview": "first chunk of A"},
        {"circular": "B", "status": "in_force", "superseded_by": [],
         "chunk_id": "B#1", "preview": "first chunk of B"},
    ]
    monkeypatch.setattr(ui.httpx, "post", lambda *a, **k: _Resp(payload))
    out = list(ui.submit_query_stream("q", "http://x/query", "", 3, "rag", "", False, []))
    final = out[-1]
    preview_updates = final[10 : 10 + ui.MAX_PREVIEWS * 2]
    # accordion 0's markdown value (index 1) is circular A's text; accordion 1's is B's
    assert preview_updates[1]["value"] == "first chunk of A"
    assert preview_updates[3]["value"] == "first chunk of B"


def test_build_ui_constructs():
    demo = ui.build_ui()
    assert demo is not None


# --- _certainty_badge --------------------------------------------------------

def test_certainty_badge_high():
    assert ui._certainty_badge("high") == "🟢 High"


def test_certainty_badge_medium():
    assert ui._certainty_badge("medium") == "🟡 Medium"


def test_certainty_badge_low():
    assert ui._certainty_badge("low") == "🔴 Low"


def test_certainty_badge_unknown_defaults_white():
    assert ui._certainty_badge("unknown") == "⚪ Unknown"


# --- _build_citations_markdown -----------------------------------------------

def test_build_citations_markdown_empty():
    assert ui._build_citations_markdown([]) == "*No citations retrieved.*"


def test_build_citations_markdown_single_row():
    rows = [{"Circular": "SEBI/HO/X/2026/1", "Status": "in_force"}]
    out = ui._build_citations_markdown(rows)
    assert "| 1 | SEBI/HO/X/2026/1 " in out
    assert "| in_force |" in out


def test_build_citations_markdown_superseded_highlight():
    rows = [{"Circular": "SEBI/HO/X/2025/1", "Status": "superseded"}]
    out = ui._build_citations_markdown(rows)
    assert "⚠️" in out, "superseded rows should have warning icon"


def test_build_citations_markdown_repealed_highlight():
    rows = [{"Circular": "SEBI/HO/X/2024/1", "Status": "repealed"}]
    out = ui._build_citations_markdown(rows)
    assert "⚠️" in out, "repealed rows should have warning icon"


def test_build_citations_markdown_multiple_rows():
    rows = [
        {"Circular": "SEBI/HO/X/2026/1", "Status": "in_force"},
        {"Circular": "SEBI/HO/X/2025/1", "Status": "superseded"},
    ]
    out = ui._build_citations_markdown(rows)
    assert "| 1 | SEBI/HO/X/2026/1 " in out
    assert "| 2 | SEBI/HO/X/2025/1 ⚠️ |" in out


# --- _validate_api_url (SSRF guard) ------------------------------------------

def test_validate_api_url_allows_127():
    ui._validate_api_url("http://127.0.0.1:8000")
    ui._validate_api_url("http://localhost:8000")


def test_validate_api_url_rejects_private_10():
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://10.0.0.1:8000")


def test_validate_api_url_rejects_private_172():
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://172.16.0.1:8000")
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://172.31.255.255:8000")


def test_validate_api_url_rejects_private_192():
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://192.168.1.1:8000")


def test_validate_api_url_rejects_cloud_metadata():
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://169.254.169.254/latest/meta-data/")


def test_validate_api_url_rejects_non_http_scheme():
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("file:///etc/passwd")
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("ftp://example.com")
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("ssh://host")


def test_validate_api_url_rejects_zero_address():
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://0.0.0.0:8000")


def test_validate_api_url_rejects_multicast():
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://224.0.0.1:8000")
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://240.0.0.1:8000")


def test_validate_api_url_rejects_test_net_ranges():
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://192.0.2.1:8000")
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://198.51.100.1:8000")
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://203.0.113.1:8000")
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://198.18.0.1:8000")


def test_validate_api_url_rejects_cgnat():
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://100.64.0.1:8000")
    with pytest.raises(ValueError, match="SSRF blocked"):
        ui._validate_api_url("http://100.127.255.255:8000")


def test_validate_api_url_allows_public():
    # Unresolvable hostnames are allowed (DNS error deferred to httpx)
    ui._validate_api_url("http://example.com:8000")


def test_validate_api_url_error_is_yielded_not_raised(monkeypatch):
    """_validate_api_url runs inside submit_query_stream's try block — a
    ValueError must surface as a yielded error message, not escape as a raw
    traceback (previously it sat outside the try)."""
    called = {"n": 0}

    def _boom(*a, **k):
        called["n"] += 1
        raise AssertionError("httpx.post must not be called when the URL is SSRF-blocked")

    monkeypatch.setattr(ui.httpx, "post", _boom)
    out = list(ui.submit_query_stream("q", "http://10.0.0.1:8000/query", "", 3, "rag", "", False, []))
    assert called["n"] == 0
    final = out[-1]
    assert "Request Failed" in final[0][-1]["content"]
    assert len(final) == _EXPECTED_ARITY


# --- _to_gradio5_history / _append_message -----------------------------------

def test_to_gradio5_history_empty():
    assert ui._to_gradio5_history(None) == []
    assert ui._to_gradio5_history([]) == []


def test_to_gradio5_history_converts_pairs():
    out = ui._to_gradio5_history([["hello", "hi there"]])
    assert out == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi there"},
    ]


def test_to_gradio5_history_passthrough_dicts():
    dicts = [{"role": "user", "content": "hello"}]
    assert ui._to_gradio5_history(dicts) == dicts


def test_append_message():
    out = ui._append_message([{"role": "user", "content": "q"}], "assistant", "a")
    assert out == [
        {"role": "user", "content": "q"},
        {"role": "assistant", "content": "a"},
    ]


# --- _blank_previews / _preview_updates arity --------------------------------

def test_blank_and_preview_updates_share_arity():
    rows = [{"Circular": "SEBI/X/1", "Preview": "text"}]
    assert len(ui._blank_previews()) == len(ui._preview_updates(rows))
    assert len(ui._blank_previews()) == ui.MAX_PREVIEWS * 2
