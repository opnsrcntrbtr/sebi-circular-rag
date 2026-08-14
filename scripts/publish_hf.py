#!/usr/bin/env python3
"""Publish SEBI RAG artifacts to Hugging Face.

Covers three repos in one coordinated run:
  1. sebi-circulars (dataset) — corpus, chunks, lineage, eval, citation-normalization,
     supersession-pairs, and golden_v7 (Arrow/Parquet).
  2. sebi-circulars-index (dataset) — dense.faiss, bm25/, chunks.jsonl,
     embeddings.npy, lineage.json, manifest.json.
  3. sebi-circular-rag-demo (space) — app.py, config.toml, requirements.txt,
     README.md, src/sebi_rag/ (aligned with deploy_space.py approach).

Usage:
    python scripts/publish_hf.py              # dry-run (report only)
    python scripts/publish_hf.py --push       # actually push to HF
    python scripts/publish_hf.py --push --rebuild-index  # rebuild index first
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
SRC_SEBI_RAG = BASE_DIR / "src" / "sebi_rag"
sys.path.insert(0, str(BASE_DIR / "src"))

HF_ORG = "opnsrcntrbtrian"
DATASET_REPO = f"{HF_ORG}/sebi-circulars"
INDEX_REPO = f"{HF_ORG}/sebi-circulars-index"
SPACE_REPO = f"{HF_ORG}/sebi-circular-rag-demo"

DIST_DATASETS = BASE_DIR / "dist" / "datasets"
DATA_INDEX = BASE_DIR / "data" / "index"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log(msg: str, *, push: bool) -> None:
    prefix = "[DRY-RUN] " if not push else ""
    print(f"{prefix}{msg}")


# ---------------------------------------------------------------------------
# Step 1: Export datasets (including golden_v7 as Arrow/Parquet)
# ---------------------------------------------------------------------------


def export_golden_v7_arrow(out_dir: Path, golden_path: Path) -> dict | None:
    """Export golden_v7 as Arrow/Parquet config."""
    import pandas as pd

    rows = []
    with open(golden_path) as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    if not rows:
        return None

    config_dir = out_dir / "golden_v7"
    config_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows)
    parquet_path = config_dir / "golden_v7.parquet"
    df.to_parquet(parquet_path, index=False)

    entry = {
        "rows": len(rows),
        "source": str(golden_path),
        "source_sha256": sha256_file(golden_path),
    }

    # Update manifest
    manifest_path = out_dir / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
    else:
        manifest = {"configs": {}}

    manifest["configs"]["golden_v7"] = entry
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return entry


def step_export_datasets(push: bool) -> dict | None:
    """Run export_datasets.py then add golden_v7 Arrow config."""
    print("\n=== Step 1: Export datasets ===")

    export_script = BASE_DIR / "scripts" / "export_datasets.py"
    if not export_script.exists():
        print("[SKIP] export_datasets.py not found; skipping dataset export")
        return None

    result = subprocess.run(
        [sys.executable, str(export_script),
         "--corpus", "data/corpus/circulars.jsonl",
         "--chunks", "data/index/chunks.jsonl",
         "--lineage", "data/index/lineage.json",
         "--golden", "eval/golden/golden_v7.jsonl",
         "--out", str(DIST_DATASETS)],
        cwd=str(BASE_DIR),
    )

    if result.returncode != 0:
        print(f"[FAIL] export_datasets.py exited with code {result.returncode}")
        return None

    # Add golden_v7 as Arrow/Parquet config
    golden_path = BASE_DIR / "eval" / "golden" / "golden_v7.jsonl"
    if golden_path.exists():
        entry = export_golden_v7_arrow(DIST_DATASETS, golden_path)
        if entry:
            log(f"golden_v7 Arrow config: {entry['rows']} rows", push=push)
    else:
        log("golden_v7.jsonl not found; skipping Arrow export", push=push)

    # Show manifest summary
    manifest_path = DIST_DATASETS / "manifest.json"
    if not manifest_path.exists():
        print("[FAIL] export_datasets.py did not produce manifest.json")
        return None

    with open(manifest_path) as f:
        manifest = json.load(f)

    print("  Configs exported:")
    for cfg, info in sorted(manifest.get("configs", {}).items()):
        print(f"    {cfg:25s} rows={info.get('rows', '?')}")

    return manifest


# ---------------------------------------------------------------------------
# Step 2: Upload datasets to HF
# ---------------------------------------------------------------------------


def step_upload_datasets(push: bool) -> None:
    """Upload dist/datasets/ to HF dataset repo."""
    print("\n=== Step 2: Upload datasets ===")

    if not DIST_DATASETS.exists():
        print("[SKIP] dist/datasets/ does not exist")
        return

    from huggingface_hub import upload_folder

    log(f"Uploading {DIST_DATASETS} -> {DATASET_REPO}", push=push)

    if not push:
        files = list(DIST_DATASETS.rglob("*"))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        print(f"  Would upload {len(files)} files ({total_size / 1e6:.1f} MB)")
        return

    upload_folder(
        folder_path=DIST_DATASETS,
        repo_id=DATASET_REPO,
        repo_type="dataset",
        commit_message="Publish: sync datasets (corpus/chunks/lineage/golden_v7)",
    )
    log(f"Uploaded {DATASET_REPO}", push=push)


# ---------------------------------------------------------------------------
# Step 3.5: Rebuild index (optional)
# ---------------------------------------------------------------------------


def step_rebuild_index(push: bool, rebuild: bool) -> None:
    """Run make index to rebuild FAISS+BM25 before upload."""
    if not rebuild:
        return
    print("\n=== Step 3.5: Rebuild index ===")
    result = subprocess.run(
        ["make", "index"],
        cwd=str(BASE_DIR),
    )
    if result.returncode != 0:
        print(f"[FAIL] make index exited with code {result.returncode}")
    else:
        log("Index rebuilt successfully", push=push)


# ---------------------------------------------------------------------------
# Step 3: Upload index to HF
# ---------------------------------------------------------------------------


def step_upload_index(push: bool) -> None:
    """Upload data/index/ to HF index repo."""
    print("\n=== Step 3: Upload index ===")

    if not DATA_INDEX.exists():
        print("[SKIP] data/index/ does not exist")
        return

    from huggingface_hub import upload_folder

    log(f"Uploading {DATA_INDEX} -> {INDEX_REPO}", push=push)

    if not push:
        files = list(DATA_INDEX.rglob("*"))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        print(f"  Would upload {len(files)} files ({total_size / 1e6:.1f} MB)")
        return

    upload_folder(
        folder_path=DATA_INDEX,
        repo_id=INDEX_REPO,
        repo_type="dataset",
        commit_message="Publish: sync index (dense.faiss/bm25/chunks/lineage/embeddings)",
    )
    log(f"Uploaded {INDEX_REPO}", push=push)


# ---------------------------------------------------------------------------
# Step 4: Sync Space source code (aligned with deploy_space.py)
# ---------------------------------------------------------------------------


def step_sync_space_code(push: bool) -> None:
    """Sync Space source code using deploy_space.py approach.

    Uploads app.py, config.toml, requirements.txt, README.md, and
    src/sebi_rag/ as a folder (matching deploy_space.py behavior).
    """
    print("\n=== Step 4: Sync Space source code ===")

    from huggingface_hub import HfApi, upload_folder
    import shutil
    import tempfile

    api = HfApi()

    # Verify required files exist
    required = ["app.py", "config.toml", "requirements-spaces.txt", "README-spaces.md"]
    missing = [f for f in required if not (BASE_DIR / f).exists()]
    if missing:
        print(f"[SKIP] Missing Space files: {missing}")
        return

    log(f"Syncing Space via upload_folder (app.py, config.toml, requirements, README, src/sebi_rag/) -> {SPACE_REPO}", push=push)

    if not push:
        # Estimate size
        total = 0
        for f in ["app.py", "config.toml", "requirements-spaces.txt", "README-spaces.md"]:
            total += (BASE_DIR / f).stat().st_size
        for py in SRC_SEBI_RAG.glob("*.py"):
            total += py.stat().st_size
        print(f"  Would upload folder (~{total / 1e3:.0f} KB)")
        return

    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp)
        shutil.copy(BASE_DIR / "app.py", staging / "app.py")
        shutil.copy(BASE_DIR / "config.toml", staging / "config.toml")
        shutil.copy(BASE_DIR / "requirements-spaces.txt", staging / "requirements.txt")
        shutil.copy(BASE_DIR / "README-spaces.md", staging / "README.md")
        shutil.copytree(
            SRC_SEBI_RAG, staging / "src" / "sebi_rag",
            ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", "*.pyc"),
        )

        api.upload_folder(
            folder_path=str(staging),
            repo_id=SPACE_REPO,
            repo_type="space",
            commit_message="Publish: sync Space (app.py, src/sebi_rag/, config.toml, requirements, README)",
        )

    log(f"Synced Space -> {SPACE_REPO}", push=push)


# ---------------------------------------------------------------------------
# Verification (post-push)
# ---------------------------------------------------------------------------


def verify_push() -> None:
    """Verify all three repos were updated correctly."""
    print("\n=== Verification ===")

    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()

    # 1. Datasets repo
    try:
        manifest = json.loads(
            open(hf_hub_download(DATASET_REPO, "manifest.json", repo_type="dataset")).read()
        )
        print("\n  sebi-circulars (datasets):")
        for cfg, info in sorted(manifest.get("configs", {}).items()):
            print(f"    {cfg:25s} rows={info.get('rows', '?')}")
    except Exception as e:
        print(f"\n  [FAIL] Could not read datasets manifest: {e}")

    # 2. Index repo
    try:
        idx_manifest = json.loads(
            open(hf_hub_download(INDEX_REPO, "manifest.json", repo_type="dataset")).read()
        )
        print("\n  sebi-circulars-index (index):")
        for fname, info in sorted(idx_manifest.get("files", {}).items()):
            size = info.get("size_bytes", "?") if isinstance(info, dict) else "?"
            print(f"    {fname:25s} {size:>10}")
    except Exception as e:
        print(f"\n  [FAIL] Could not read index manifest: {e}")

    # 3. Space repo
    try:
        space_files = api.list_repo_files(SPACE_REPO, repo_type="space")
        py_count = sum(1 for f in space_files if f.startswith("src/sebi_rag/") and f.endswith(".py"))
        print(f"\n  sebi-circular-rag-demo (space): {py_count} .py files in src/sebi_rag/")
    except Exception as e:
        print(f"\n  [FAIL] Could not list Space files: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--push", action="store_true", help="Actually push to HF (default: dry-run)")
    ap.add_argument("--verify", action="store_true", help="Verify after push")
    ap.add_argument("--rebuild-index", action="store_true", help="Rebuild FAISS+BM25 index before upload")
    args = ap.parse_args(argv)

    print(f"SEBI RAG HF Publish — {'DRY-RUN' if not args.push else 'PUSH'}")
    print(f"  Datasets repo: {DATASET_REPO}")
    print(f"  Index repo:    {INDEX_REPO}")
    print(f"  Space repo:    {SPACE_REPO}\n")

    # Step 1: Export datasets
    step_export_datasets(push=args.push)

    # Step 2: Upload datasets
    step_upload_datasets(push=args.push)

    # Step 3.5: Rebuild index (optional)
    step_rebuild_index(push=args.push, rebuild=args.rebuild_index)

    # Step 3: Upload index
    step_upload_index(push=args.push)

    # Step 4: Sync Space code
    step_sync_space_code(push=args.push)

    if args.push and args.verify:
        verify_push()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
