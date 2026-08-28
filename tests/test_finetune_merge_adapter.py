"""Offline tests for scripts/finetune/merge_adapter.py's pure pieces. The
actual PeftModel merge + save cycle needs a real bge-m3 load and the real
trained adapter and was verified empirically via a throwaway smoke test
before this script was written (see its module docstring: a non-trivial
0.75 L2 embedding-distance shift after merge, ~2.18 GB output matching the
base model's own scale, and an exact-match reload round-trip) - not re-run
here, matching the offline-first convention used across this test suite.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from finetune.merge_adapter import sha256_dir  # noqa: E402


def test_sha256_dir_hashes_every_file_relative_to_root(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"hello")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_bytes(b"world")

    manifest = sha256_dir(tmp_path)

    assert set(manifest) == {"a.txt", "sub/b.txt"}
    # exact sha256 of the real content - pinned so a hashing-logic
    # regression (e.g. accidentally hashing the path instead of the
    # content) is caught, not just "some hash landed in the right key"
    import hashlib
    assert manifest["a.txt"] == hashlib.sha256(b"hello").hexdigest()
    assert manifest["sub/b.txt"] == hashlib.sha256(b"world").hexdigest()


def test_sha256_dir_empty_directory_returns_empty_manifest(tmp_path):
    assert sha256_dir(tmp_path) == {}


def test_sha256_dir_ignores_subdirectories_themselves_only_files(tmp_path):
    (tmp_path / "empty_subdir").mkdir()
    (tmp_path / "file.txt").write_bytes(b"content")
    manifest = sha256_dir(tmp_path)
    assert list(manifest) == ["file.txt"]
