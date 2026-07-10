"""Publish the locally built data/index artifacts to a HF dataset repo so the
CPU Space can HybridRetriever.load() them instead of re-encoding 36k chunks.

Build the index first on this machine (fast on MPS):
    make reindex

Then:
    .venv/bin/python scripts/upload_spaces_index.py \
        --repo opnsrcntrbtrian/sebi-circulars-index [--private]

Finally set spaces.index_repo in config.toml to the same repo id.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "data" / "index"
REQUIRED = ["dense.faiss", "chunks.jsonl", "meta.json", "lineage.json"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True, help="HF dataset repo id")
    ap.add_argument("--index-dir", default=str(INDEX_DIR))
    ap.add_argument("--private", action="store_true")
    args = ap.parse_args()

    d = Path(args.index_dir)
    missing = [f for f in REQUIRED if not (d / f).exists()]
    if missing:
        raise SystemExit(f"{d} is missing {missing}; run `make reindex` first")

    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(args.repo, repo_type="dataset", private=args.private,
                    exist_ok=True)
    info = api.upload_folder(
        folder_path=str(d),
        repo_id=args.repo,
        repo_type="dataset",
        commit_message="Publish prebuilt FAISS/BM25 index + lineage for the "
                       "HF Spaces demo",
    )
    print(f"uploaded {d} -> {info.repo_url if hasattr(info, 'repo_url') else args.repo}")
    print(f"now set   [spaces] index_repo = \"{args.repo}\"   in config.toml")


if __name__ == "__main__":
    main()
