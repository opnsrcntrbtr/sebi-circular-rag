"""The eval stack's generator choice must be one shared decision.

`derive_thresholds.py` sets the floors and `eval_json.py` measures against
them. If they build different generators the gate keeps reporting numbers that
no longer mean anything - the same silent failure `golden_v7.score` exists to
prevent for scoring semantics.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.generate import ExtractiveStubGenerator, eval_generator_for  # noqa: E402


def test_stub_is_the_default_kind():
    assert isinstance(eval_generator_for("stub"), ExtractiveStubGenerator)


def test_mlx_kind_builds_the_production_generator():
    """Uses an injected loader so the test stays offline."""
    sentinel = object()
    got = eval_generator_for("mlx", mlx_model="some/model",
                             mlx_loader=lambda m: (sentinel, m))
    assert got == (sentinel, "some/model")


def test_unknown_kind_raises_rather_than_defaulting():
    """Silently falling back to the stub would derive floors under semantics
    the caller did not ask for."""
    try:
        eval_generator_for("magic")
    except ValueError as e:
        assert "magic" in str(e)
    else:
        raise AssertionError("expected ValueError on unknown generator kind")


# --- coupling: both eval entry points must route through the factory --------

_SCRIPTS = (ROOT / "scripts" / "eval_json.py",
            ROOT / "scripts" / "golden_v7" / "derive_thresholds.py")


def test_eval_scripts_do_not_construct_a_generator_directly():
    for p in _SCRIPTS:
        src = p.read_text(encoding="utf-8")
        assert not re.search(r"generator=ExtractiveStubGenerator\(\)", src), (
            f"{p.name} hardcodes the stub instead of using eval_generator_for")


def test_eval_scripts_use_the_shared_factory():
    """Must assert the factory is CALLED, not merely imported.

    Verified 2026-08-12 by red-green: an earlier version of this test checked
    only that the name appeared somewhere in the file, so reverting the call
    site to `generator=ExtractiveStubGenerator()` left the import behind and
    this test still passed while the script bypassed the shared decision.
    """
    for p in _SCRIPTS:
        src = p.read_text(encoding="utf-8")
        assert re.search(r"generator=eval_generator_for\(", src), (
            f"{p.name} does not call eval_generator_for at the generator= site")


def test_both_eval_scripts_read_the_same_setting():
    """A factory both call is not enough - they must pass the same setting,
    or the floors and the measurements still diverge."""
    for p in _SCRIPTS:
        src = p.read_text(encoding="utf-8")
        assert "s.eval_generator" in src, f"{p.name} does not read s.eval_generator"
