"""Regression coverage for the ZeroGPU-hardware workaround in app.py.

Background: the Space (opnsrcntrbtrian/sebi-circular-rag-demo) was created on
`zero-a10g` hardware and cannot be downgraded to cpu-basic without a PRO
subscription (HF `request_space_hardware` returns 402). ZeroGPU Spaces refuse
to start ("No @spaces.GPU function detected") unless at least one function is
decorated with `@spaces.GPU`. app.py adds an undecorated, never-called
`warm_up_gpu` purely to satisfy that startup check; actual pipeline code
never runs inside a `@spaces.GPU` function, so it executes on the CPU host
process ZeroGPU allocates outside GPU-decorated calls, exactly as before.

These tests run fully offline: the real `spaces` package (HF's ZeroGPU SDK)
is not a project dependency (see pyproject.toml) and is not installed
locally, so a stub is injected into sys.modules before app.py is imported.
"""
from __future__ import annotations

import importlib
import re
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")


@pytest.fixture()
def stub_spaces_module(monkeypatch):
    """Inject a fake `spaces` module so app.py's `import spaces` succeeds
    offline, and record every function passed to `spaces.GPU`."""
    decorated = []

    def _GPU(fn):
        decorated.append(fn.__name__)
        return fn

    fake = types.ModuleType("spaces")
    fake.GPU = _GPU
    monkeypatch.setitem(sys.modules, "spaces", fake)
    return decorated


@pytest.fixture()
def app_module(stub_spaces_module, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT))
    sys.modules.pop("app", None)
    mod = importlib.import_module("app")
    yield mod
    sys.modules.pop("app", None)


def test_app_imports_spaces_and_declares_gpu_function():
    """Static guard: if `import spaces` or the `@spaces.GPU` decorator is
    ever removed, the deployed Space (fixed on zero-a10g hardware) goes back
    to crashing on startup with 'No @spaces.GPU function detected'."""
    assert re.search(r"^import spaces\s*$", APP_SOURCE, re.MULTILINE)
    assert re.search(r"@spaces\.GPU\s*\ndef \w+\(", APP_SOURCE)


def test_warm_up_gpu_is_decorated_on_import(app_module, stub_spaces_module):
    assert "warm_up_gpu" in stub_spaces_module
    assert callable(app_module.warm_up_gpu)


def test_warm_up_gpu_is_never_called():
    """It must stay dead code: calling it would request a real ZeroGPU
    allocation (and burn the account's daily GPU quota) for a function that
    exists solely to satisfy the startup check, not to do any work."""
    call_sites = re.findall(r"(?<!def )warm_up_gpu\s*\(", APP_SOURCE)
    # The only occurrence of `warm_up_gpu(` in the file must be its `def`.
    assert call_sites == [], f"warm_up_gpu is invoked at: {call_sites}"


def test_pipeline_query_path_has_no_gpu_decorator(app_module):
    """The functions actually on the request path (get_pipeline,
    run_query_spaces) must stay undecorated, confirming the real RAG logic
    runs outside any @spaces.GPU-gated call and therefore on CPU."""
    import inspect

    for fn in (app_module.get_pipeline, app_module.run_query_spaces):
        src = inspect.getsource(fn)
        assert "@spaces.GPU" not in src


def test_readme_hardware_hint_is_present_but_non_authoritative():
    """`hardware:` in README-spaces.md is not a documented Spaces config key
    (only `suggested_hardware` is, and even that doesn't auto-assign — see
    https://huggingface.co/docs/hub/spaces-config-reference). It is a
    human-readable hint only; it does NOT change the already-provisioned
    zero-a10g hardware. This test guards against the comment/claim drifting
    out of sync with that reality."""
    readme = (ROOT / "README-spaces.md").read_text(encoding="utf-8")
    assert "hardware: cpu-basic" in readme
