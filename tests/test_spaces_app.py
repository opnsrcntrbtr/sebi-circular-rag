"""HF Spaces demo (root app.py): citations table + preview accordion logic.

Fully offline, no Gradio launch, no network. `spaces` (the ZeroGPU package) is
stubbed before import since it isn't installed outside an actual Space.

This file exists because app.py had zero test coverage before it (see
tests/test_ui.py, which covers the different src/sebi_rag/ui.py module) — six
consecutive commits (065a67a..84ea79e) tried to fix the citation preview by
pushing to the live Space and eyeballing it. These tests pin the exact
defects those commits kept reintroducing: a chunks_map capped at 5 entries,
a doc_id/chunk_id key mismatch, HTML nested in a markdown table cell, and
unescaped `|`/`\\`/newlines corrupting table rows.
"""
from __future__ import annotations

import sys
import types

import pytest


@pytest.fixture(scope="module", autouse=True)
def _stub_spaces_package():
    """app.py does `import spaces` (ZeroGPU) at module scope; stub it."""
    if "spaces" not in sys.modules:
        stub = types.ModuleType("spaces")
        stub.GPU = lambda f=None, **_kw: (f if f is not None else (lambda g: g))
        sys.modules["spaces"] = stub
    yield


@pytest.fixture(scope="module")
def app_module():
    sys.path.insert(0, "src")
    import app  # noqa: PLC0415 — deliberate late import, root-level Spaces entrypoint

    return app


# ---------------------------------------------------------------------------
# _build_citations_markdown: table structure, no Preview column, no HTML/pipe
# corruption regardless of what a caller passes for Circular text.
# ---------------------------------------------------------------------------


def test_empty_rows_returns_placeholder(app_module):
    assert app_module._build_citations_markdown([]) == "*No citations retrieved.*"


def test_table_has_no_preview_column(app_module):
    rows = [{"Circular": "SEBI/HO/X/2024/1", "Status": "in_force", "Superseded By": "-"}]
    md = app_module._build_citations_markdown(rows)
    header = md.splitlines()[0]
    assert "Preview" not in header
    assert header.count("|") == 5  # | # | Circular | Status | Superseded By |


def test_superseded_row_gets_warning_icon(app_module):
    rows = [{"Circular": "SEBI/HO/X/2024/1", "Status": "superseded", "Superseded By": "SEBI/HO/X/2026/2"}]
    md = app_module._build_citations_markdown(rows)
    assert "⚠️" in md


def test_in_force_row_has_no_warning_icon(app_module):
    rows = [{"Circular": "SEBI/HO/X/2024/1", "Status": "in_force", "Superseded By": "-"}]
    md = app_module._build_citations_markdown(rows)
    data_row = md.splitlines()[-1]
    assert "⚠️" not in data_row


def test_pipe_in_circular_id_does_not_break_table_row_count(app_module):
    # Regression: unescaped '|' inside a cell silently adds table columns.
    # `\|` still contains a literal '|' character (that's how markdown escapes
    # it), so count only pipes NOT preceded by a backslash.
    import re

    unescaped_pipe = re.compile(r"(?<!\\)\|")
    rows = [{"Circular": "SEBI|HO|X/2024/1", "Status": "in_force", "Superseded By": "-"}]
    md = app_module._build_citations_markdown(rows)
    header_cols = len(unescaped_pipe.findall(md.splitlines()[0]))
    data_cols = len(unescaped_pipe.findall(md.splitlines()[-1]))
    assert header_cols == data_cols


def test_backslash_in_circular_id_escaped_before_pipe(app_module):
    # Regression (b34454b): escape order matters — backslash must be escaped
    # first or the pipe-escaping backslash itself gets re-escaped.
    rows = [{"Circular": r"SEBI\HO\X", "Status": "in_force", "Superseded By": "-"}]
    md = app_module._build_citations_markdown(rows)
    row = md.splitlines()[-1]
    assert row.count("|") == 5


def test_multiple_rows_numbered_in_order(app_module):
    rows = [
        {"Circular": "A", "Status": "in_force", "Superseded By": "-"},
        {"Circular": "B", "Status": "in_force", "Superseded By": "-"},
    ]
    md = app_module._build_citations_markdown(rows)
    data_lines = md.splitlines()[2:]
    assert data_lines[0].startswith("| 1 |")
    assert data_lines[1].startswith("| 2 |")


# ---------------------------------------------------------------------------
# _truncate_preview
# ---------------------------------------------------------------------------


def test_truncate_preview_under_limit_unchanged(app_module):
    assert app_module._truncate_preview("short text") == "short text"


def test_truncate_preview_over_limit_gets_ellipsis(app_module):
    text = "x" * 900
    out = app_module._truncate_preview(text, limit=800)
    assert len(out) == 801  # 800 chars + ellipsis
    assert out.endswith("…")


# ---------------------------------------------------------------------------
# _preview_updates / _blank_previews: the accordion pool wiring.
# ---------------------------------------------------------------------------


def test_blank_and_preview_updates_have_equal_length(app_module):
    # Guards the exact class of bug that would break every `yield` in
    # run_query_stream: output tuple arity must match the Gradio outputs list
    # regardless of which branch fires.
    blank = app_module._blank_previews()
    filled = app_module._preview_updates(
        [{"id": "c1", "Circular": "SEBI/HO/X/2024/1"}], {"c1": "some text"}
    )
    assert len(blank) == len(filled) == 2 * app_module.MAX_PREVIEWS


def test_preview_updates_found_chunk_shows_real_text(app_module):
    rows = [{"id": "c1", "Circular": "SEBI/HO/X/2024/1"}]
    chunk_text = {"c1": "7. Information to be captured in nomination form."}
    updates = app_module._preview_updates(rows, chunk_text)
    # updates = [accordion_0, markdown_0, accordion_1, markdown_1, ...]
    assert updates[0]["visible"] is True
    assert "SEBI/HO/X/2024/1" in updates[0]["label"]
    assert updates[1]["value"] == "7. Information to be captured in nomination form."


def test_preview_updates_missing_chunk_id_falls_back_not_raises(app_module):
    # Regression: the original chunks_map.get(..., "*Preview unavailable.*")
    # fallback existed, but a 5-entry cap meant it fired almost always. Here
    # we assert the fallback path itself is still correct and never raises.
    rows = [{"id": "does-not-exist", "Circular": "SEBI/HO/X/2024/1"}]
    updates = app_module._preview_updates(rows, {})
    assert updates[1]["value"] == "*Preview unavailable.*"


def test_preview_updates_truncates_long_chunk_text(app_module):
    rows = [{"id": "c1", "Circular": "SEBI/HO/X/2024/1"}]
    chunk_text = {"c1": "y" * 1000}
    updates = app_module._preview_updates(rows, chunk_text)
    assert len(updates[1]["value"]) == 801
    assert updates[1]["value"].endswith("…")


def test_preview_updates_rows_beyond_max_previews_are_dropped(app_module):
    rows = [
        {"id": f"c{i}", "Circular": f"CIRCULAR/{i}"}
        for i in range(app_module.MAX_PREVIEWS + 5)
    ]
    chunk_text = {f"c{i}": f"text {i}" for i in range(len(rows))}
    updates = app_module._preview_updates(rows, chunk_text)
    assert len(updates) == 2 * app_module.MAX_PREVIEWS
    # last visible slot corresponds to row MAX_PREVIEWS - 1, not one of the
    # extra rows beyond the pool
    last_label = updates[2 * (app_module.MAX_PREVIEWS - 1)]["label"]
    assert f"CIRCULAR/{app_module.MAX_PREVIEWS - 1}" in last_label


def test_blank_previews_all_hidden_and_empty(app_module):
    updates = app_module._blank_previews()
    accordions = updates[0::2]
    markdowns = updates[1::2]
    assert all(u["visible"] is False for u in accordions)
    assert all(u["value"] == "" for u in markdowns)


def test_get_chunk_text_builds_once_and_caches(app_module):
    from sebi_rag.segment import Chunk

    class _FakeRetriever:
        chunks = [
            Chunk(id="c1", doc_id="D1", section="s", text="text one"),
            Chunk(id="c2", doc_id="D1", section="s", text="text two"),
        ]

    class _FakePipeline:
        retriever = _FakeRetriever()

    app_module._chunk_text.clear()
    result = app_module._get_chunk_text(_FakePipeline())
    assert result == {"c1": "text one", "c2": "text two"}

    # Second call with an empty retriever must return the cached map, not an
    # empty one — this is what removes the O(78.5k) per-query rebuild.
    class _EmptyPipeline:
        retriever = types.SimpleNamespace(chunks=[])

    result2 = app_module._get_chunk_text(_EmptyPipeline())
    assert result2 == {"c1": "text one", "c2": "text two"}

    app_module._chunk_text.clear()  # don't leak state into other tests


# ---------------------------------------------------------------------------
# _cycle_messages_until_done — the cycling-status-message mechanism behind
# the loading indicator. get_pipeline()/pipeline.query() are single blocking
# calls with no progress callback, so this runs the blocking work on a
# worker thread and yields cycling messages every `interval`s until it
# resolves. Fully offline: no real pipeline, just concurrent.futures.Future.
# ---------------------------------------------------------------------------


def test_cycle_messages_stops_immediately_on_already_done_future(app_module):
    import concurrent.futures

    future: concurrent.futures.Future = concurrent.futures.Future()
    future.set_result("done")
    messages = list(app_module._cycle_messages_until_done(future, ["a", "b"], interval=0.05))
    assert messages == []  # already resolved — no cycling needed


def test_cycle_messages_cycles_while_future_pending(app_module):
    import concurrent.futures
    import time

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(time.sleep, 0.17)
        messages = list(
            app_module._cycle_messages_until_done(future, ["a", "b"], interval=0.05)
        )
    # ~0.17s / 0.05s interval => at least 2 cycles observed before it resolved
    assert len(messages) >= 2
    # cycles through the list in order, wrapping around
    assert messages == ["a", "b", "a"][: len(messages)]


def test_cycle_messages_propagates_exception_from_future(app_module):
    import concurrent.futures

    future: concurrent.futures.Future = concurrent.futures.Future()
    future.set_exception(ValueError("boom"))
    with pytest.raises(ValueError, match="boom"):
        list(app_module._cycle_messages_until_done(future, ["a"], interval=0.05))


# ---------------------------------------------------------------------------
# _format_latency / _faithfulness_badge — human-readable metadata formatting.
# Regression: the UI previously showed raw "21621 ms" / unexplained "1.00".
# ---------------------------------------------------------------------------


def test_format_latency_under_1000ms_shows_milliseconds(app_module):
    assert app_module._format_latency(850) == "850ms"
    assert app_module._format_latency(0) == "0ms"


def test_format_latency_1000ms_and_over_shows_seconds(app_module):
    assert app_module._format_latency(1000) == "1.0s"
    assert app_module._format_latency(21621) == "21.6s"


def test_faithfulness_badge_tiers(app_module):
    assert app_module._faithfulness_badge(1.0).startswith("✅")
    assert app_module._faithfulness_badge(0.9).startswith("✅")
    assert app_module._faithfulness_badge(0.8).startswith("⚠️")
    assert app_module._faithfulness_badge(0.7).startswith("⚠️")
    assert app_module._faithfulness_badge(0.5).startswith("❌")
    assert "0.85" in app_module._faithfulness_badge(0.85)


# ---------------------------------------------------------------------------
# _hidden_meta / _loading_meta / _visible_meta — the metadata badge row.
# These were the dead-component bug: loading_text/latency_badge/
# faithfulness_badge/certainty_badge were declared, permanently
# visible=False, and never appeared in any yield tuple or outputs list.
# Length parity across all three mirrors the _blank_previews/_preview_updates
# guard for the exact same class of arity-mismatch bug.
# ---------------------------------------------------------------------------


def test_meta_helpers_return_four_tuples(app_module):
    assert len(app_module._hidden_meta()) == 4
    assert len(app_module._loading_meta("loading…")) == 4
    assert len(app_module._visible_meta(1000, 0.9, "🟢 High")) == 4


def test_hidden_meta_all_hidden(app_module):
    updates = app_module._hidden_meta()
    assert all(u["visible"] is False for u in updates)


def test_loading_meta_shows_message_badges_still_hidden(app_module):
    loading, latency, faithfulness, certainty = app_module._loading_meta("⏳ Building…")
    assert loading["visible"] is True
    assert loading["value"] == "⏳ Building…"
    assert latency["visible"] is False
    assert faithfulness["visible"] is False
    assert certainty["visible"] is False


def test_visible_meta_shows_formatted_badges_loading_hidden(app_module):
    loading, latency, faithfulness, certainty = app_module._visible_meta(
        21621, 1.0, "🟢 High"
    )
    assert loading["visible"] is False
    assert latency["visible"] is True
    assert latency["value"] == "⏱️ 21.6s"
    assert faithfulness["visible"] is True
    assert "1.00" in faithfulness["value"]
    assert certainty["visible"] is True
    assert certainty["value"] == "🟢 High"

