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
    X.write_dataset_cards(out_dir)
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

    # Expected row counts (updated 2026-07-17: first re-annotation since the
    # 2026-07-15 supersede-classification fix (f2c20b6) — trigger-word matches
    # now count regardless of ref position, adding +86 lineage edges and
    # +81 supersession pairs over the 2026-07-14 pins)
    #
    # Updated 2026-07-25 by the corpus remediation. Two repairs moved these:
    #   (a) 5 records had their body text overwritten with one shared
    #       circular's text; re-ingested from their real PDFs.
    #   (b) 12 records carried a stale circular_number — either truncated
    #       ("CIR/MRD/DP/41") or taken from a circular they merely CITED.
    # chunks   77859 -> 77841: the 5 repaired records' true text is shorter.
    # lineage   4569 -> 4574 (+5) and citation-normalization 8802 -> 8812
    #       (+10): the repaired records now contribute their real citations.
    # supersession-pairs 2850 -> 2760 (-90): FALSE POSITIVES REMOVED, not lost
    #       data. A record misnamed after a circular it cited was inheriting
    #       that circular's supersession claims. Verified: the entire delta is
    #       attributable to those 12 records (every other record: 0 change);
    #       records with a wrong cited number went 4->0, 9->0, 8->0, while
    #       truncated numbers now resolve correctly (0->1).
    #
    # Updated 2026-07-31: corpus grew by +14 circulars (+582 chunks, +0 lineage,
    # +87 citation-normalization, +9 supersession-pairs) from orphan PDF ingest
    # (11 normal + 2 OCR + 1 unparseable master). supersession-pairs unchanged.
    #
    # Updated 2026-08-18: corpus grew by +2 circulars (+45 chunks) — the two
    # 2026-08-14 DDHS circulars (HO/17/11/(2)2026, HO/17/11/17(5)2026) ingested
    # after the 2026-08-14 expansion. lineage/eval/citation-normalization/
    # supersession-pairs unchanged (new circulars carry no reg citations).
    #
    # Updated 2026-08-28: bounded historical scrape for the bge-m3 SEBI
    # fine-tuning intervention (Phase -1, .claude/plans/deep-analyse-and-
    # research-bright-dawn.md) — corpus grew by +760 circulars (+9,381
    # chunks), targeting the previously-thin 2010-2021 window via --from/--to
    # (see docs/status.md 2026-08-28 entry for the per-batch breakdown and
    # the frozen snapshot id). eval unchanged (golden_v7 deliberately not
    # re-derived, stays the intervention's fixed measurement target).
    #
    # Updated 2026-09-01: table-row-shredding chunker fix (Workstream B of the
    # same intervention's post-hoc verdict, segment.py's _merge_table_rows) —
    # chunks 87959 -> 85131 (-2,828). PDF-flattened table rows that matched
    # the heading regex were merging into fewer, larger chunks instead of one
    # chunk per row; corpus/lineage/eval/citation-normalization/
    # supersession-pairs are untouched (chunk boundaries only, no document- or
    # citation-level change). See memory/nominee-count-chunker-bug.md.
    #
    # Updated 2026-09-02: gapped-table-row fix (docs/status.md's 2026-09-02
    # scoping + fix entries, segment.py's _merge_table_rows gap tolerance) —
    # chunks 85131 -> 84188 (-943). Table/TOC rows separated by up to 2 short
    # filler lines (a row's own wrapped label, or the lead-in to the next)
    # now merge across that gap instead of each staying a standalone chunk;
    # corpus/lineage/eval/citation-normalization/supersession-pairs untouched
    # (chunk boundaries only, same as the 2026-09-01 entry above).
    #
    # Updated 2026-09-03: TOC long-title-row fix (docs/status.md's 2026-09-03
    # entry, segment.py's _is_toc_row_candidate + _toc_region_indices) —
    # chunks 84188 -> 83752 (-436). TOC rows whose trailing "title + page
    # number" text exceeds the table-cell-sized 60-char cap now merge too, but
    # only inside a bounded window after a literal "TABLE OF CONTENTS" marker
    # paragraph; corpus/lineage/eval/citation-normalization/supersession-pairs
    # untouched (chunk boundaries only, same as the two entries above).
    expected = {
        "corpus": 1490,
        "chunks": 83752,
        "lineage": 4752,
        "eval": 56,
        "citation-normalization": 9926,
        "supersession-pairs": 8781,
    }

    # Report every drift in one run: a re-annotation usually moves several
    # counts at once, and failing on only the first turns one fix into N.
    drift = {cfg: (exp, configs.get(cfg, {}).get("rows"))
             for cfg, exp in expected.items()
             if configs.get(cfg, {}).get("rows") != exp}
    assert not drift, "row-count drift (expected, actual): " + repr(drift)
