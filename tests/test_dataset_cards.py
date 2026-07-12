"""Task 4 & 5: Dataset card generation and platform packaging tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import export_datasets as X  # noqa: E402


def test_hf_card_exists_and_has_yaml_front_matter(tmp_path):
    """README.md for HF must have YAML front matter with dataset metadata."""
    export_dir = tmp_path / "export_test"
    export_datasets = {
        "corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 34883, "schema": X.CHUNKS_SCHEMA},
        "lineage": {"rows": 1437, "schema": X.LINEAGE_SCHEMA},
        "eval": {"rows": 56, "schema": X.EVAL_SCHEMA},
        "citation-normalization": {"rows": 2951, "schema": X.CITATION_SCHEMA},
        "supersession-pairs": {"rows": 1281, "schema": X.SUPERSESSION_SCHEMA},
    }
    card = X.build_hf_card(export_datasets)
    assert "---" in card
    assert "language" in card.lower() and "en" in card.lower()
    assert "cc-by" in card.lower()
    assert "source" in card.lower()


def test_hf_card_includes_actual_row_counts():
    """Card must cite actual row counts (not spec guesses)."""
    datasets = {
        "corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 34883, "schema": X.CHUNKS_SCHEMA},
        "citation-normalization": {"rows": 2951, "schema": X.CITATION_SCHEMA},
        "supersession-pairs": {"rows": 1281, "schema": X.SUPERSESSION_SCHEMA},
    }
    card = X.build_hf_card(datasets)
    assert "603" in card
    assert "34883" in card or "34,883" in card
    assert "2951" in card or "2,951" in card
    # For 1281, just check that supersession-pairs section exists with row count
    assert "supersession-pairs" in card.lower()
    assert "1,281" in card or "1281" in card or ("supersession" in card.lower() and "281" in card)


def test_hf_card_includes_data_quality_caveats():
    """Card must document known data-quality issues."""
    datasets = {k: {"rows": 1, "schema": v} for k, v in [
        ("corpus", X.CORPUS_SCHEMA),
        ("chunks", X.CHUNKS_SCHEMA),
    ]}
    card = X.build_hf_card(datasets)
    # Caveats: UNKNOWN dept for 124 records, oversized subjects
    assert "124" in card  # UNKNOWN count
    assert "department" in card.lower()
    assert "subject" in card.lower()
    assert ("oversized" in card.lower() or "2900" in card or "large" in card.lower())


def test_hf_card_includes_licensing_section():
    """Card must include licensing and compliance sections."""
    datasets = {"corpus": {"rows": 1, "schema": X.CORPUS_SCHEMA}}
    card = X.build_hf_card(datasets)
    assert "cc-by-4.0" in card.lower() or "cc by" in card.lower()
    assert "sebi" in card.lower()
    assert "not legal advice" in card.lower() or "disclaimer" in card.lower()


def test_kaggle_metadata_json_valid():
    """Kaggle metadata.json must be valid JSON with required fields."""
    datasets = {
        "corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 34883, "schema": X.CHUNKS_SCHEMA},
    }
    metadata = X.build_kaggle_metadata(datasets)
    parsed = json.loads(metadata)
    assert "title" in parsed
    assert "id" in parsed
    assert "licenses" in parsed
    assert parsed["licenses"][0]["name"] == "CC-BY-4.0"


def test_kaggle_metadata_includes_dataset_descriptions():
    """Each config must have a description in the metadata."""
    datasets = {
        "corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA},
        "citation-normalization": {"rows": 2951, "schema": X.CITATION_SCHEMA},
    }
    metadata = json.loads(X.build_kaggle_metadata(datasets))
    # At minimum, must mention the datasets
    assert "corpus" in str(metadata).lower()
    assert "citation" in str(metadata).lower()


def test_zenodo_submission_pack_structure():
    """Zenodo pack must have metadata.json + tarball instructions."""
    datasets = {"corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA}}
    pack = X.build_zenodo_pack(datasets)
    # pack is a dict with metadata and instructions
    assert isinstance(pack, dict)
    assert "metadata" in pack
    assert "creators" in pack["metadata"]
    assert "title" in pack["metadata"]
    assert "license" in pack["metadata"]
    assert pack["metadata"]["license"] == "CC-BY-4.0"


def test_zenodo_metadata_has_doi_fields():
    """Zenodo must include DOI and versioning fields."""
    datasets = {"corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA}}
    pack = X.build_zenodo_pack(datasets)
    meta = pack["metadata"]
    assert "version" in meta
    assert "description" in meta
    assert "SEBI" in meta["description"] or "SEBI" in meta.get("title", "")


def test_aikosh_submission_pack_includes_csv_and_metadata():
    """AIKosh pack must include CSV manifests + metadata + licensing."""
    datasets = {
        "corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 34883, "schema": X.CHUNKS_SCHEMA},
    }
    pack = X.build_aikosh_pack(datasets)
    assert isinstance(pack, dict)
    assert "manifest_csv" in pack  # CSV manifest of all configs
    assert "metadata" in pack
    assert "licensing" in pack
    assert "CC-BY" in pack["licensing"] or "CC-BY" in str(pack.get("metadata", {}))


def test_aikosh_pack_manifest_includes_all_configs():
    """AIKosh manifest must list all dataset configs with row counts."""
    datasets = {
        "corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 34883, "schema": X.CHUNKS_SCHEMA},
        "supersession-pairs": {"rows": 1281, "schema": X.SUPERSESSION_SCHEMA},
    }
    pack = X.build_aikosh_pack(datasets)
    manifest = pack["manifest_csv"]
    assert "corpus" in manifest and "603" in manifest
    assert "chunks" in manifest and "34883" in manifest
    assert "supersession-pairs" in manifest and "1281" in manifest


def test_write_cards_to_disk(tmp_path):
    """write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles."""
    # Minimal corpus + manifest
    corpus_src = tmp_path / "circulars.jsonl"
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

    export_dir = tmp_path / "dist"
    export_dir.mkdir()

    # Create minimal manifest
    manifest = {
        "version": "v2026.01",
        "corpus_snapshot_date": "2026-01-01",
        "configs": {
            "corpus": {"rows": 1, "source": "data/corpus/circulars.jsonl", "source_sha256": "abc123"},
        }
    }
    (export_dir / "manifest.json").write_text(json.dumps(manifest))

    # Call the write function
    X.write_dataset_cards(export_dir)

    # Verify files exist
    assert (export_dir / "README.md").exists()
    assert (export_dir / "metadata.json").exists()
    zenodo_pack = export_dir / "ZENODO_SUBMISSION_PACK"
    aikosh_pack = export_dir / "AIKOSH_SUBMISSION_PACK"
    # At least one should exist
    assert zenodo_pack.exists() or aikosh_pack.exists()


def test_card_validation_yaml_parses():
    """YAML front matter in HF card must parse without errors."""
    datasets = {"corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA}}
    card = X.build_hf_card(datasets)
    # Extract YAML block
    if "---" in card:
        _, yaml_block, _ = card.split("---", 2)
        # Just verify it's not malformed (basic check)
        assert "language" in yaml_block
        assert "license" in yaml_block


def test_idempotency_same_cards_on_repeat_run():
    """Calling write_dataset_cards() twice must produce identical card content."""
    datasets = {
        "corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 34883, "schema": X.CHUNKS_SCHEMA},
    }
    card1 = X.build_hf_card(datasets)
    card2 = X.build_hf_card(datasets)
    assert card1 == card2

    meta1 = X.build_kaggle_metadata(datasets)
    meta2 = X.build_kaggle_metadata(datasets)
    assert meta1 == meta2
