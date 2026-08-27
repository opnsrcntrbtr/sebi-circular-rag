"""As-of date plumbing in the Spaces UI (app.py)."""
from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def app_module(monkeypatch):
    fake = types.ModuleType("spaces")
    fake.GPU = lambda fn: fn
    monkeypatch.setitem(sys.modules, "spaces", fake)
    monkeypatch.syspath_prepend(str(ROOT))
    sys.modules.pop("app", None)
    return importlib.import_module("app")


def test_parse_as_of_accepts_iso_and_empty(app_module):
    assert app_module._parse_as_of("2025-01-10") == "2025-01-10"
    assert app_module._parse_as_of("  2025-01-10  ") == "2025-01-10"
    assert app_module._parse_as_of("") is None
    assert app_module._parse_as_of("   ") is None


def test_parse_as_of_rejects_garbage(app_module):
    with pytest.raises(ValueError):
        app_module._parse_as_of("January 10, 2025")
    with pytest.raises(ValueError):
        app_module._parse_as_of("2025-13-45")


def test_run_query_rejects_bad_as_of_before_building_pipeline(app_module):
    # Must error out on the date BEFORE get_pipeline() (no index download).
    out = list(app_module.run_query_stream("what are the norms?", 3, "rag", "not-a-date", []))
    assert out[0][0][-1] == {"role": "assistant", "content": "**Error:** 'As of date' must be YYYY-MM-DD (e.g. 2025-01-10)."}


def _expected_output_count(app_module) -> int:
    """8 fixed fields + 2 per preview accordion + 4 meta badges.

    Matches the flat list built in build_ui() (chatbot, citations_md,
    citations_df, latency_out, faithfulness_out, certainty_out,
    superseded_out, unsupported_out, *preview_components, loading_text,
    latency_badge, faithfulness_badge, certainty_badge).
    """
    return 8 + 2 * app_module.MAX_PREVIEWS + 4


def test_run_query_yield_arity_matches_outputs_list_pipeline_free_paths(app_module):
    # Regression guard for the exact bug class that made loading_text/
    # latency_badge/faithfulness_badge/certainty_badge dead components: a
    # yield tuple whose length silently drifts from build_ui()'s outputs=
    # list. These two paths never touch get_pipeline(), so they're cheap to
    # check directly without mocking the whole RAG pipeline.
    expected = _expected_output_count(app_module)

    empty_out = list(app_module.run_query_stream("", 3, "rag", "", []))
    assert len(empty_out[0]) == expected

    bad_date_out = list(app_module.run_query_stream("q", 3, "rag", "not-a-date", []))
    assert len(bad_date_out[0]) == expected


def test_as_of_widget_is_date_only_string_typed_datetime(app_module):
    # Regression guard: gr.DateTime defaults to type="timestamp" (a float),
    # which _parse_as_of's date.fromisoformat() cannot parse — this must stay
    # type="string" or the calendar picker silently breaks every as-of query.
    # include_time=False keeps it date-only (no meaning for an as-of date).
    import gradio as gr

    as_of_components = [
        c for c in app_module.demo.blocks.values()
        if isinstance(c, gr.DateTime) and c.label == "As of date (optional)"
    ]
    assert len(as_of_components) == 1
    as_of = as_of_components[0]
    assert as_of.type == "string"
    assert as_of.include_time is False
