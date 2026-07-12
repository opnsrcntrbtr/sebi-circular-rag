"""Push dist/datasets to the live HF Hub dataset repo (default:
opnsrcntrbtrian/sebi-circulars), matching the live repo layout exactly:
six config dirs + README.md + manifest.json + metadata.json + a provenance
copy of scripts/export_datasets.py at repo root. Platform submission packs
(AIKOSH/ZENODO) are never uploaded.

Runbook: docs/superpowers/plans/2026-07-12-hf-dataset-push-runbook.md
Regenerate first:  make export-datasets
Dry-run (default): .venv/bin/python scripts/push_datasets.py
Real push:         .venv/bin/python scripts/push_datasets.py --yes
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "datasets"
CONFIG_DIRS = ["chunks", "citation-normalization", "corpus", "eval",
               "lineage", "supersession-pairs"]
ROOT_FILES = ["README.md", "manifest.json", "metadata.json"]


def upload_plan(dist: Path) -> list[tuple[Path, str]]:
    """(local_path, path_in_repo) pairs; SystemExit if anything is missing."""
    pairs: list[tuple[Path, str]] = []
    missing: list[str] = []
    for name in ROOT_FILES:
        p = dist / name
        pairs.append((p, name)) if p.exists() else missing.append(name)
    for d in CONFIG_DIRS:
        cfg = dist / d
        expected = [cfg / f"{d}.jsonl", cfg / f"{d}.parquet"]
        for p in expected:
            if p.exists():
                pairs.append((p, f"{d}/{p.name}"))
            else:
                missing.append(str(p.relative_to(dist)))
    exporter = ROOT / "scripts" / "export_datasets.py"
    if exporter.exists():
        pairs.append((exporter, "export_datasets.py"))
    else:
        missing.append("scripts/export_datasets.py")
    if missing:
        raise SystemExit(f"refusing to push, missing artifacts: {missing} "
                         f"(run `make export-datasets` first)")
    return pairs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default="opnsrcntrbtrian/sebi-circulars")
    ap.add_argument("--dist", default=str(DIST))
    ap.add_argument("--yes", action="store_true",
                    help="actually upload; without it, print the plan and exit")
    args = ap.parse_args()

    pairs = upload_plan(Path(args.dist))
    total = sum(p.stat().st_size for p, _ in pairs)
    print(f"upload plan -> {args.repo} ({len(pairs)} files, "
          f"{total / 1e6:.1f} MB):")
    for p, rp in pairs:
        print(f"  {rp:45s} {p.stat().st_size / 1e6:8.1f} MB")
    if not args.yes:
        print("\nDRY RUN ONLY. Re-run with --yes to push.")
        return

    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo(args.repo, repo_type="dataset", exist_ok=True)
    for p, rp in pairs:
        api.upload_file(path_or_fileobj=str(p), path_in_repo=rp,
                        repo_id=args.repo, repo_type="dataset",
                        commit_message=f"Metadata layer migration v2026.07: {rp}")
    print(f"pushed {len(pairs)} files -> "
          f"https://huggingface.co/datasets/{args.repo}")


if __name__ == "__main__":
    main()