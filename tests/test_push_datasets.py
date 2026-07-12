"""Offline tests for the HF dataset push script (no network)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import push_datasets as P  # noqa: E402


def _fake_dist(tmp_path: Path) -> Path:
    dist = tmp_path / "datasets"
    for d in P.CONFIG_DIRS:
        (dist / d).mkdir(parents=True)
        (dist / d / f"{d}.jsonl").write_text("{}\n")
        (dist / d / f"{d}.parquet").write_bytes(b"PAR1")
    for f in P.ROOT_FILES:
        (dist / f).write_text("x")
    # platform packs that must be excluded
    (dist / "AIKOSH_SUBMISSION_PACK").mkdir()
    (dist / "AIKOSH_SUBMISSION_PACK" / "manifest.csv").write_text("x")
    (dist / "ZENODO_SUBMISSION_PACK").mkdir()
    (dist / "ZENODO_SUBMISSION_PACK" / "metadata.json").write_text("x")
    return dist


def test_upload_plan_includes_configs_and_root_files(tmp_path):
    plan = P.upload_plan(_fake_dist(tmp_path))
    repo_paths = {rp for _, rp in plan}
    assert "README.md" in repo_paths
    assert "manifest.json" in repo_paths
    assert "metadata.json" in repo_paths
    assert "corpus/corpus.jsonl" in repo_paths
    assert "corpus/corpus.parquet" in repo_paths
    assert "chunks/chunks.parquet" in repo_paths
    assert "export_datasets.py" in repo_paths  # provenance copy


def test_upload_plan_excludes_platform_packs(tmp_path):
    plan = P.upload_plan(_fake_dist(tmp_path))
    for _, rp in plan:
        assert "AIKOSH" not in rp and "ZENODO" not in rp


def test_upload_plan_fails_on_missing_config(tmp_path):
    dist = _fake_dist(tmp_path)
    (dist / "eval" / "eval.jsonl").unlink()
    import pytest
    with pytest.raises(SystemExit):
        P.upload_plan(dist)