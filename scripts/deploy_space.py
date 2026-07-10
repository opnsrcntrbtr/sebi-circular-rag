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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True, help="HF Space repo id")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--hardware", default="cpu-basic")
    args = ap.parse_args()

    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(
        args.repo, repo_type="space", space_sdk="gradio",
        private=args.private, exist_ok=True,
    )
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


if __name__ == "__main__":
    main()
