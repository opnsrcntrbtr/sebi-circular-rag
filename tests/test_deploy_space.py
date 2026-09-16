"""scripts/deploy_space.py: post-upload runtime read-back.

Covers the observability gap from the 2026-09-16 BUILD_ERROR incident
(exit code 128, empty build log, invisible to CI — see docs/status.md and
README-spaces.md § Deploying). `_hardware_warning` is the pure decision
helper `main()` calls after `api.upload_folder(...)`; it must never raise
and must stay quiet for the normal in-flight case right after a deploy.

Loads deploy_space.py by path via importlib rather than a package import —
this module lives under scripts/, not src/sebi_rag/, so it isn't on the
test PYTHONPATH. This only stays import-safe at collection time because
`from huggingface_hub import HfApi` in deploy_space.py sits inside main(),
not at module scope; if that import is ever hoisted to the top of the
file, collecting this test starts requiring huggingface_hub to be
installed.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "deploy_space", ROOT / "scripts" / "deploy_space.py"
)
assert _spec is not None and _spec.loader is not None
deploy_space = importlib.util.module_from_spec(_spec)
sys.modules["deploy_space"] = deploy_space
_spec.loader.exec_module(deploy_space)  # noqa: S102 — loading a local script by path


def test_build_error_warns_with_message() -> None:
    msg = deploy_space._hardware_warning(
        stage="BUILD_ERROR",
        requested="zero-a10g",
        current=None,
        error_message="Job failed with exit code: 128. Reason: Error",
    )
    assert msg is not None
    assert "128" in msg


def test_in_flight_build_with_no_hardware_yet_is_quiet() -> None:
    for stage in ("BUILDING", "BUILD_QUEUED", "APP_STARTING"):
        assert deploy_space._hardware_warning(
            stage=stage, requested="zero-a10g", current=None, error_message=None,
        ) is None


def test_running_with_no_hardware_current_warns() -> None:
    msg = deploy_space._hardware_warning(
        stage="RUNNING", requested="zero-a10g", current=None, error_message=None,
    )
    assert msg is not None
    assert "zero-a10g" in msg


def test_running_with_matching_hardware_is_quiet() -> None:
    assert deploy_space._hardware_warning(
        stage="RUNNING", requested="zero-a10g", current="zero-a10g", error_message=None,
    ) is None


def test_runtime_read_back_failure_is_swallowed(capsys) -> None:
    class _ExplodingApi:
        def get_space_runtime(self, repo_id: str):
            raise RuntimeError("network down")

    # Should not raise.
    deploy_space._report_runtime(_ExplodingApi(), "opnsrcntrbtrian/sebi-circular-rag-demo")
    captured = capsys.readouterr()
    assert "network down" in captured.out or "network down" in captured.err


class _FakeRuntime:
    def __init__(self, *, stage: str, requested: str | None, current: str | None,
                 sha: str | None, error_message: str | None = None) -> None:
        self.stage = stage
        self.requested_hardware = requested
        self.hardware = current
        self.raw = {"sha": sha, "errorMessage": error_message}


def test_stale_runtime_sha_suppresses_warning(capsys) -> None:
    """The exact race this guards against: get_space_runtime called right
    after upload_folder still reflects the PREVIOUS commit's BUILD_ERROR.
    A deploy that just fixed a broken Space must not reprint the old error.
    """
    class _StaleApi:
        def get_space_runtime(self, repo_id: str):
            return _FakeRuntime(
                stage="BUILD_ERROR", requested="zero-a10g", current=None,
                sha="old-sha-from-previous-build",
                error_message="Job failed with exit code: 128. Reason: Error",
            )

    deploy_space._report_runtime(
        _StaleApi(), "opnsrcntrbtrian/sebi-circular-rag-demo",
        deployed_sha="new-sha-just-pushed",
    )
    captured = capsys.readouterr()
    assert "WARNING" not in captured.out
    assert "not yet reflecting this deploy" in captured.out


def test_matching_sha_build_error_still_warns(capsys) -> None:
    """Once the runtime's sha matches what was just pushed, a genuine
    BUILD_ERROR for *this* deploy must still surface."""
    class _MatchingApi:
        def get_space_runtime(self, repo_id: str):
            return _FakeRuntime(
                stage="BUILD_ERROR", requested="zero-a10g", current=None,
                sha="new-sha-just-pushed",
                error_message="Job failed with exit code: 128. Reason: Error",
            )

    deploy_space._report_runtime(
        _MatchingApi(), "opnsrcntrbtrian/sebi-circular-rag-demo",
        deployed_sha="new-sha-just-pushed",
    )
    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "128" in captured.out
