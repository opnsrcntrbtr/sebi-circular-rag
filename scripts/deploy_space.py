"""Create/update the Gradio-SDK Hugging Face Space for the CPU demo and push
app.py, src/sebi_rag/, config.toml, requirements-spaces.txt (as
requirements.txt) and README-spaces.md (as README.md).

    .venv/bin/python scripts/deploy_space.py --repo opnsrcntrbtrian/sebi-circular-rag-demo

Excludes tests/, scripts/, data/, dist/, graphify-out/, docs/, eval/,
.venv/, uv.lock, Makefile — none of those are needed at Space runtime.
"""
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Stages a Space passes through between "upload just landed" and "hardware
# actually assigned". `hardware.current` is legitimately None in all of
# these — warning here would fire on every healthy deploy (the read-back
# happens seconds after upload_folder returns, well before a slot exists)
# and train reviewers to ignore the warning. See BUILD_ERROR incident
# 2026-09-16 in docs/status.md for why this check exists at all.
_IN_FLIGHT_STAGES = frozenset({"BUILDING", "BUILD_QUEUED", "APP_STARTING"})


def _hardware_warning(
    *, stage: str, requested: str | None, current: str | None,
    error_message: str | None,
) -> str | None:
    """Return a warning string if the just-deployed Space looks unhealthy,
    else None. Pure decision logic — no I/O — so it's unit-testable without
    a live Space or a mocked HfApi upload.
    """
    if stage == "BUILD_ERROR":
        return f"Space build failed (stage=BUILD_ERROR): {error_message}"
    if current is None and stage not in _IN_FLIGHT_STAGES:
        return (
            f"Space hardware not granted (stage={stage!r}, "
            f"requested={requested!r}, current=None) — see README-spaces.md "
            f"§ Deploying for the exit-128 / scheduling-failure runbook"
        )
    return None


def _report_runtime(api, repo_id: str, deployed_sha: str | None = None) -> None:
    """Read back the Space's runtime after a deploy and print what CI was
    previously blind to (the 2026-09-16 BUILD_ERROR sat undetected because
    nothing after upload_folder ever looked). Always non-fatal: the upload
    already succeeded, so a read-back failure must not fail the deploy.

    `deployed_sha` (the `oid` from `upload_folder`'s `CommitInfo`) guards
    against a race: `get_space_runtime` called right after `upload_folder`
    returns commonly still reflects the *previous* build (HF hasn't
    transitioned the Space into BUILDING for the new commit yet). Without
    this check, a deploy that just fixed a broken Space would reprint the
    old BUILD_ERROR it just replaced, and a deploy that just broke a
    healthy Space would report stage=RUNNING and stay silent — the exact
    inversion of what this function exists to catch. When the runtime's
    `sha` doesn't match what was just pushed, the report is for a build
    that hasn't started yet — print the info line only, suppress the
    warning (state or absence of it isn't attributable to this deploy).
    """
    try:
        runtime = api.get_space_runtime(repo_id)
        stage = runtime.stage
        requested = runtime.requested_hardware
        current = runtime.hardware
        raw = runtime.raw or {}
        error_message = raw.get("errorMessage")
        runtime_sha = raw.get("sha")
        stale = bool(deployed_sha) and bool(runtime_sha) and runtime_sha != deployed_sha
        print(
            f"runtime: stage={stage!r} hardware.requested={requested!r} "
            f"hardware.current={current!r} sha={runtime_sha!r} "
            f"deployed_sha={deployed_sha!r}"
        )
        if stale:
            print(
                "note: runtime not yet reflecting this deploy's commit "
                "(build likely still queuing) — skipping warning check"
            )
            return
        warning = _hardware_warning(
            stage=stage, requested=requested, current=current,
            error_message=error_message,
        )
        if warning:
            print(f"WARNING: {warning}")
    except Exception as exc:  # noqa: BLE001 — read-back is best-effort, never fatal
        print(f"note: could not read back Space runtime ({exc})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True, help="HF Space repo id")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--hardware", default="cpu-basic")
    args = ap.parse_args()

    from huggingface_hub import HfApi

    api = HfApi()
    try:
        api.create_repo(
            args.repo, repo_type="space", space_sdk="gradio",
            private=args.private, exist_ok=True,
        )
    except Exception as exc:  # noqa: BLE001 — repo may already exist (manual creation)
        print(f"note: create_repo call failed ({exc}); assuming Space already exists")
    try:
        api.request_space_hardware(args.repo, hardware=args.hardware)
    except Exception as exc:  # noqa: BLE001 — hardware request is best-effort
        print(f"note: could not set hardware to {args.hardware!r} ({exc}); "
              f"default free tier applies")

    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp)
        shutil.copy(ROOT / "app.py", staging / "app.py")
        shutil.copy(ROOT / "config.toml", staging / "config.toml")
        shutil.copy(ROOT / "requirements-spaces.txt", staging / "requirements.txt")
        shutil.copy(ROOT / "README-spaces.md", staging / "README.md")
        shutil.copytree(
            ROOT / "src" / "sebi_rag", staging / "src" / "sebi_rag",
            ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", "*.pyc"),
        )

        info = api.upload_folder(
            folder_path=str(staging),
            repo_id=args.repo,
            repo_type="space",
            commit_message="Deploy SEBI Circular RAG CPU demo "
                           "(app.py, src/sebi_rag, config.toml, requirements, README)",
        )
    print(f"deployed -> https://huggingface.co/spaces/{args.repo}")
    print(info)
    _report_runtime(api, args.repo, deployed_sha=getattr(info, "oid", None))


if __name__ == "__main__":
    main()
