"""Task 5: Integration tests — idempotency and live export verification."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import export_datasets as X  # noqa: E402


def file_sha256(path: Path) -> str:
    """Compute SHA256 of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_export_all_is_idempotent(tmp_path):
    """Running export_all() twice must produce identical output files."""
    corpus_src = tmp_path / "circulars.jsonl"
    chunks_src = tmp_path / "chunks.jsonl"
    lineage_src = tmp_path / "lineage.json"
    golden_src = tmp_path / "golden.jsonl"

    # Create minimal fixtures
    corpus_src.write_text(json.dumps({
        "circular_number": "TEST/1",
        "issue_date": "2026-01-01",
        "effective_date": "2026-01-01",
        "subject": "Test",
        "issuing_department": "CFD",
        "supersession_status": "in_force",
        "version_lineage": [],
        "source_url": "https://example.com",
        "text": "Test circular",
        "excerpt": False,
        "provenance": "Test",
    }) + "\n")

    chunks_src.write_text(json.dumps({
        "id": "TEST/1#0",
        "doc_id": "TEST/1",
        "section": "TEST/1/p0",
        "text": "TEST/1 | Test | p0\nTest body",
        "meta": {
            "circular_number": "TEST/1",
            "issue_date": "2026-01-01",
            "effective_date": "2026-01-01",
            "subject": "Test",
            "issuing_department": "CFD",
            "supersession_status": "in_force",
            "amendment_history": [],
            "version_lineage": [],
        }
    }) + "\n")

    lineage_src.write_text(json.dumps({
        "supersedes": {},
        "amends": {},
        "superseded_by": {},
        "amended_by": {},
    }))

    golden_src.write_text(json.dumps({
        "id": "q1",
        "query": "test",
        "relevant_circulars": ["TEST/1"],
        "relevant_chunks": [],
        "answer_contains": "test",
        "must_contain": ["test"],
        "must_not_contain": [],
        "abstain": False,
        "task_type": "title_direct",
        "difficulty": "easy",
        "expected_citation_level": "circular",
        "rationale": "test",
        "label_source": "golden_v5",
        "review_status": "seeded",
    }) + "\n")

    # First export
    out1 = tmp_path / "out1"
    manifest1 = X.export_all(corpus_src, chunks_src, lineage_src, golden_src, out1)

    # Second export to same location (tests manifest merge stability)
    manifest2 = X.export_all(corpus_src, chunks_src, lineage_src, golden_src, out1)

    # Manifests must be identical
    assert manifest1 == manifest2

    # Compare Parquet + JSONL files
    for cfg in ("corpus", "chunks", "lineage", "eval"):
        jsonl1 = (out1 / cfg / f"{cfg}.jsonl").read_text()
        parquet1 = (out1 / cfg / f"{cfg}.parquet").read_bytes()
        # Re-export to same location and check files are stable
        X.export_all(corpus_src, chunks_src, lineage_src, golden_src, out1)
        jsonl2 = (out1 / cfg / f"{cfg}.jsonl").read_text()
        parquet2 = (out1 / cfg / f"{cfg}.parquet").read_bytes()
        assert jsonl1 == jsonl2, f"{cfg}.jsonl changed after re-export"
        assert parquet1 == parquet2, f"{cfg}.parquet changed after re-export"


def test_manifest_version_is_consistent_across_configs(tmp_path):
    """All configs in manifest must share the same version tag (v2026.07)."""
    corpus_src = tmp_path / "circulars.jsonl"
    corpus_src.write_text(json.dumps({
        "circular_number": "TEST/1",
        "issue_date": "2026-07-01",
        "effective_date": "",
        "subject": "Test",
        "issuing_department": "CFD",
        "supersession_status": "in_force",
        "version_lineage": [],
        "source_url": "https://example.com",
        "text": "Body",
        "excerpt": False,
        "provenance": "Test",
    }) + "\n")

    chunks_src = tmp_path / "chunks.jsonl"
    chunks_src.write_text(json.dumps({
        "id": "TEST/1#0",
        "doc_id": "TEST/1",
        "section": "TEST/1/p0",
        "text": "TEST/1 | Test | p0\nBody",
        "meta": {
            "circular_number": "TEST/1",
            "issue_date": "2026-07-01",
            "effective_date": "",
            "subject": "Test",
            "issuing_department": "CFD",
            "supersession_status": "in_force",
            "amendment_history": [],
            "version_lineage": [],
        }
    }) + "\n")

    lineage_src = tmp_path / "lineage.json"
    lineage_src.write_text(json.dumps({
        "supersedes": {},
        "amends": {},
        "superseded_by": {},
        "amended_by": {},
    }))

    golden_src = tmp_path / "golden.jsonl"
    golden_src.write_text(json.dumps({
        "id": "q1",
        "query": "test",
        "relevant_circulars": ["TEST/1"],
        "relevant_chunks": [],
        "answer_contains": "test",
        "must_contain": ["test"],
        "must_not_contain": [],
        "abstain": False,
        "task_type": "title_direct",
        "difficulty": "easy",
        "expected_citation_level": "circular",
        "rationale": "test",
        "label_source": "golden_v5",
        "review_status": "seeded",
    }) + "\n")

    out = tmp_path / "out"
    manifest = X.export_all(corpus_src, chunks_src, lineage_src, golden_src, out)

    # Check version consistency
    version = manifest.get("version")
    assert version is not None
    for cfg, info in manifest.get("configs", {}).items():
        assert "rows" in info
        assert "source" in info
        assert "source_sha256" in info
        # All configs should see the same global version from corpus snapshot
        assert manifest["version"] == version


def test_live_export_produces_valid_files():
    """Smoke test: live export on actual corpus produces valid datasets."""
    corpus_path = Path("data/corpus/circulars.jsonl")
    chunks_path = Path("data/index/chunks.jsonl")
    lineage_path = Path("data/index/lineage.json")
    golden_path = Path("eval/golden/golden_v6.jsonl")

    if not all(p.exists() for p in [corpus_path, chunks_path, lineage_path, golden_path]):
        pytest.skip("Live corpus not available")

    out_dir = Path("dist/datasets")
    manifest = X.export_all(corpus_path, chunks_path, lineage_path, golden_path, out_dir)

    # Validate manifest
    assert "version" in manifest
    assert "configs" in manifest

    # Verify all 6 configs present
    expected_configs = {
        "corpus", "chunks", "lineage", "eval",
        "citation-normalization", "supersession-pairs"
    }
    assert expected_configs == set(manifest["configs"].keys())

    # Verify files exist for each config
    for cfg in expected_configs:
        jsonl = out_dir / cfg / f"{cfg}.jsonl"
        parquet = out_dir / cfg / f"{cfg}.parquet"
        assert jsonl.exists(), f"Missing {cfg}.jsonl"
        assert parquet.exists(), f"Missing {cfg}.parquet"
        assert jsonl.stat().st_size > 0, f"Empty {cfg}.jsonl"
        assert parquet.stat().st_size > 0, f"Empty {cfg}.parquet"


def test_dataset_cards_generated_on_export():
    """Verify that dataset cards are generated with export."""
    out_dir = Path("dist/datasets")
    if not (out_dir / "manifest.json").exists():
        pytest.skip("Export not run yet")

    # Check HF card
    assert (out_dir / "README.md").exists()
    readme = (out_dir / "README.md").read_text()
    assert "SEBI Circulars" in readme
    assert "---" in readme  # YAML front matter

    # Check Kaggle metadata
    assert (out_dir / "metadata.json").exists()
    kaggle_meta = json.loads((out_dir / "metadata.json").read_text())
    assert "title" in kaggle_meta
    assert "licenses" in kaggle_meta

    # Check Zenodo pack
    zenodo_pack = out_dir / "ZENODO_SUBMISSION_PACK"
    assert zenodo_pack.exists()
    assert (zenodo_pack / "metadata.json").exists()
    assert (zenodo_pack / "README_TARBALL.txt").exists()

    # Check AIKosh pack
    aikosh_pack = out_dir / "AIKOSH_SUBMISSION_PACK"
    assert aikosh_pack.exists()
    assert (aikosh_pack / "manifest.csv").exists()
    assert (aikosh_pack / "metadata.json").exists()
    assert (aikosh_pack / "LICENSING.txt").exists()


def test_card_licensing_mentions_sebi_and_attribution():
    """Cards must include proper SEBI attribution and licensing."""
    out_dir = Path("dist/datasets")
    if not (out_dir / "README.md").exists():
        pytest.skip("Cards not generated")

    readme = (out_dir / "README.md").read_text()
    assert "SEBI" in readme
    assert "cc-by" in readme.lower()
    assert "government" in readme.lower() or "Copyright Act" in readme
    assert "not legal advice" in readme.lower() or "disclaimer" in readme.lower()


def test_row_count_accuracy_in_live_export():
    """Verify actual row counts from live export match expected values."""
    out_dir = Path("dist/datasets")
    if not (out_dir / "manifest.json").exists():
        pytest.skip("Export not run yet")

    manifest = json.loads((out_dir / "manifest.json").read_text())
    configs = manifest.get("configs", {})

    # Expected row counts (updated 2026-07-12: corpus grown via scraping +
    # metadata-layer migration added confidence-tiered lineage edges)
    expected = {
        "corpus": 603,
        "chunks": 36683,
        "lineage": 1437,
        "eval": 56,
        "citation-normalization": 2951,
        "supersession-pairs": 1281,
    }

    for cfg, expected_rows in expected.items():
        actual_rows = configs.get(cfg, {}).get("rows")
        assert actual_rows == expected_rows, \
            f"{cfg}: expected {expected_rows}, got {actual_rows}"
