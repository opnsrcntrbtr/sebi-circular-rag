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
    out = app_module.run_query_spaces("what are the norms?", 3, "rag", "not-a-date")
    assert out[0].startswith("**Error:**") and "YYYY-MM-DD" in out[0]
