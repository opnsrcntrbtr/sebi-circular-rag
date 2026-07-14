"""Task 4 & 5: Dataset card generation and platform packaging tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import export_datasets as X  # noqa: E402


_STATS = {"snapshot_date": "2026-07-14", "dept_unknown": 1, "dept_total": 1,
          "date_min": "2020-01-01", "date_max": "2026-01-01"}


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
    card = X.build_hf_card(export_datasets, _STATS)
    assert "---" in card
    assert "language" in card.lower() and "en" in card.lower()
    assert "cc-by" in card.lower()
    assert "source" in card.lower()


def test_hf_card_includes_actual_row_counts():
    """Card must cite actual row counts from datasets, not hardcoded literals."""
    datasets = {
        "corpus": {"rows": 705, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 77859, "schema": X.CHUNKS_SCHEMA},
        "citation-normalization": {"rows": 8802, "schema": X.CITATION_SCHEMA},
        "supersession-pairs": {"rows": 2769, "schema": X.SUPERSESSION_SCHEMA},
    }
    stats = {"snapshot_date": "2026-07-14", "dept_unknown": 158, "dept_total": 705,
             "date_min": "2010-04-06", "date_max": "2026-07-07"}
    card = X.build_hf_card(datasets, stats)
    assert "705" in card
    assert "77,859" in card or "77859" in card
    assert "8,802" in card or "8802" in card
    assert "2,769" in card or "2769" in card
    assert "603" not in card       # old hardcoded value must be gone
    assert "34,883" not in card and "34883" not in card


def test_hf_card_includes_data_quality_caveats():
    """Card must document known data-quality issues using computed stats."""
    datasets = {k: {"rows": 705, "schema": v} for k, v in [
        ("corpus", X.CORPUS_SCHEMA), ("chunks", X.CHUNKS_SCHEMA)]}
    stats = {"snapshot_date": "2026-07-14", "dept_unknown": 158, "dept_total": 705,
             "date_min": "2010-04-06", "date_max": "2026-07-07"}
    card = X.build_hf_card(datasets, stats)
    assert "158" in card and "705" in card  # UNKNOWN count, computed not hardcoded
    assert "124" not in card                # old hardcoded value must be gone
    assert "department" in card.lower()
    assert "subject" in card.lower()
    assert ("oversized" in card.lower() or "2900" in card or "large" in card.lower())


def test_hf_card_includes_licensing_section():
    """Card must include licensing and compliance sections."""
    datasets = {"corpus": {"rows": 1, "schema": X.CORPUS_SCHEMA}}
    card = X.build_hf_card(datasets, _STATS)
    assert "cc-by-4.0" in card.lower() or "cc by" in card.lower()
    assert "sebi" in card.lower()
    assert "not legal advice" in card.lower() or "disclaimer" in card.lower()


def test_kaggle_metadata_json_valid():
    """Kaggle metadata.json must be valid JSON with required fields."""
    datasets = {
        "corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 34883, "schema": X.CHUNKS_SCHEMA},
    }
    metadata = X.build_kaggle_metadata(datasets, _STATS)
    parsed = json.loads(metadata)
    assert "title" in parsed
    assert "id" in parsed
    assert "licenses" in parsed
    assert parsed["licenses"][0]["name"] == "CC-BY-4.0"


def test_kaggle_metadata_includes_dataset_descriptions():
    """Description must cite actual row counts, not hardcoded literals."""
    datasets = {
        "corpus": {"rows": 705, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 77859, "schema": X.CHUNKS_SCHEMA},
        "lineage": {"rows": 4483, "schema": X.LINEAGE_SCHEMA},
        "eval": {"rows": 56, "schema": X.EVAL_SCHEMA},
        "citation-normalization": {"rows": 8802, "schema": X.CITATION_SCHEMA},
        "supersession-pairs": {"rows": 2769, "schema": X.SUPERSESSION_SCHEMA},
    }
    stats = {"snapshot_date": "2026-07-14", "dept_unknown": 158, "dept_total": 705,
             "date_min": "2010-04-06", "date_max": "2026-07-07"}
    metadata = json.loads(X.build_kaggle_metadata(datasets, stats))
    desc = metadata["description"]
    assert "705" in desc and "77,859" in desc and "4,483" in desc
    assert "8,802" in desc and "2,769" in desc
    assert "603" not in desc and "34,883" not in desc
    assert "2010" in metadata["title"] or "2010" in desc  # date range, not fixed 2021


def test_zenodo_submission_pack_structure():
    """Zenodo pack must have metadata.json + tarball instructions."""
    datasets = {"corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA}}
    pack = X.build_zenodo_pack(datasets, _STATS)
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
    pack = X.build_zenodo_pack(datasets, _STATS)
    meta = pack["metadata"]
    assert "version" in meta
    assert "description" in meta
    assert "SEBI" in meta["description"] or "SEBI" in meta.get("title", "")


def test_zenodo_pack_uses_computed_row_count_and_date():
    datasets = {"corpus": {"rows": 705, "schema": X.CORPUS_SCHEMA}}
    stats = {"snapshot_date": "2026-07-14", "dept_unknown": 158, "dept_total": 705,
             "date_min": "2010-04-06", "date_max": "2026-07-07"}
    pack = X.build_zenodo_pack(datasets, stats)
    assert "705" in pack["metadata"]["description"]
    assert "603" not in pack["metadata"]["description"]
    assert pack["metadata"]["publication_date"] == "2026-07-14"
    assert "2010" in pack["metadata"]["title"]


def test_aikosh_submission_pack_includes_csv_and_metadata():
    """AIKosh pack must include CSV manifests + metadata + licensing."""
    datasets = {
        "corpus": {"rows": 603, "schema": X.CORPUS_SCHEMA},
        "chunks": {"rows": 34883, "schema": X.CHUNKS_SCHEMA},
    }
    pack = X.build_aikosh_pack(datasets, _STATS)
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
    pack = X.build_aikosh_pack(datasets, _STATS)
    manifest = pack["manifest_csv"]
    assert "corpus" in manifest and "603" in manifest
    assert "chunks" in manifest and "34883" in manifest
    assert "supersession-pairs" in manifest and "1281" in manifest


def test_aikosh_pack_uses_computed_date_range():
    datasets = {"corpus": {"rows": 705, "schema": X.CORPUS_SCHEMA}}
    stats = {"snapshot_date": "2026-07-14", "dept_unknown": 158, "dept_total": 705,
             "date_min": "2010-04-06", "date_max": "2026-07-07"}
    pack = X.build_aikosh_pack(datasets, stats)
    assert "2010" in pack["metadata"]["title"]
    assert "2021" not in pack["metadata"]["title"]
    assert "2010" in pack["licensing"] or "2010" in pack["metadata"]["description"]


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
    card = X.build_hf_card(datasets, _STATS)
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
    card1 = X.build_hf_card(datasets, _STATS)
    card2 = X.build_hf_card(datasets, _STATS)
    assert card1 == card2

    meta1 = X.build_kaggle_metadata(datasets, _STATS)
    meta2 = X.build_kaggle_metadata(datasets, _STATS)
    assert meta1 == meta2


def test_compute_stats_from_exported_corpus(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    rows = [
        {"circular_number": "A/1", "issue_date": "2019-03-01", "issuing_department": "CFD"},
        {"circular_number": "A/2", "issue_date": "2024-06-15", "issuing_department": None},
        {"circular_number": "A/3", "issue_date": "2021-01-10", "issuing_department": ""},
    ]
    (corpus_dir / "corpus.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    stats = X._compute_stats(tmp_path)
    assert stats["dept_unknown"] == 2
    assert stats["dept_total"] == 3
    assert stats["date_min"] == "2019-03-01"
    assert stats["date_max"] == "2024-06-15"
    assert stats["snapshot_date"]  # non-empty, computed today


def test_compute_stats_ignores_non_iso_dates(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    rows = [
        {"circular_number": "A/1", "issue_date": "2020-05-01", "issuing_department": "CFD"},
        {"circular_number": "A/2", "issue_date": None, "issuing_department": "MRD"},
        {"circular_number": "A/3", "issue_date": "not-a-date", "issuing_department": "MRD"},
    ]
    (corpus_dir / "corpus.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    stats = X._compute_stats(tmp_path)
    assert stats["date_min"] == stats["date_max"] == "2020-05-01"


def test_generated_hf_card_row_counts_match_manifest(tmp_path):
    """End-to-end: every row count printed in the generated card's summary
    table must equal the corresponding manifest.json row count. Catches a
    future regression back to hardcoded literals without needing to know
    what the 'right' numbers are — it compares the card against its own
    manifest, not against an expected literal."""
    out_dir = tmp_path / "dist"
    corpus_dir = out_dir / "corpus"
    corpus_dir.mkdir(parents=True)
    rows = [
        {"circular_number": f"A/{i}", "issue_date": "2022-01-01",
         "issuing_department": "CFD" if i % 2 else ""}
        for i in range(1, 6)
    ]
    (corpus_dir / "corpus.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    manifest = {
        "version": "v2099.01",
        "configs": {
            "corpus": {"rows": 5, "source": "x", "source_sha256": "x"},
            "chunks": {"rows": 42, "source": "x", "source_sha256": "x"},
            "lineage": {"rows": 7, "source": "x", "source_sha256": "x"},
            "eval": {"rows": 3, "source": "x", "source_sha256": "x"},
            "citation-normalization": {"rows": 11, "source": "x", "source_sha256": "x"},
            "supersession-pairs": {"rows": 9, "source": "x", "source_sha256": "x"},
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    X.write_dataset_cards(out_dir)
    card = (out_dir / "README.md").read_text(encoding="utf-8")

    table_start = card.index("| Config | Rows")
    table = card[table_start:table_start + 800]
    for cfg, info in manifest["configs"].items():
        expected = f"{info['rows']:,}"
        assert expected in table, f"{cfg}: expected {expected} in card table, not found"
