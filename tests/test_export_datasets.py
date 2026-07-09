"""Offline tests for the dataset export pipeline (corpus config, Task 1)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import export_datasets as X  # noqa: E402


def _record(**over) -> dict:
    base = {
        "circular_number": "SEBI/HO/CFD/P/CIR/2023/123",
        "issue_date": "2023-07-13",
        "effective_date": "",
        "subject": "Disclosure of material events",
        "issuing_department": "CFD",
        "supersession_status": "in_force",
        "amendment_history": [],
        "version_lineage": ["CIR/CFD/CMD/4/2015"],
        "source_url": "https://www.sebi.gov.in/legal/circulars/jul-2023/x_73910.html",
        "provenance": "Parsed from PDF 1689245602256.pdf on 2026-06-30",
        "excerpt": False,
        "text": "CIRCULAR body text",
    }
    base.update(over)
    return base


def test_corpus_row_drops_provenance_and_keeps_extraction_date():
    row = X.build_corpus_rows([_record()])[0]
    assert "provenance" not in row
    assert row["extraction_date"] == "2026-06-30"


def test_corpus_row_nullifies_empty_strings():
    row = X.build_corpus_rows([_record(effective_date="", issuing_department="")])[0]
    assert row["effective_date"] is None
    assert row["issuing_department"] is None


def test_corpus_row_has_exact_schema_in_order():
    row = X.build_corpus_rows([_record()])[0]
    assert list(row) == X.CORPUS_SCHEMA
    assert "amendment_history" not in row   # empty across corpus; not exported


def test_export_corpus_refuses_invalid_source(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text(json.dumps(_record(circular_number="has space/2023")) + "\n")
    with pytest.raises(ValueError, match="violation"):
        X.export_corpus(bad, tmp_path / "out")


def test_export_corpus_writes_jsonl_parquet_manifest(tmp_path):
    src = tmp_path / "circulars.jsonl"
    recs = [_record(), _record(circular_number="SEBI/HO/MRD/P/CIR/2024/01",
                               issue_date="2024-01-05")]
    src.write_text("".join(json.dumps(r) + "\n" for r in recs))
    out = tmp_path / "out"

    manifest = X.export_corpus(src, out)

    lines = (out / "corpus" / "corpus.jsonl").read_text().splitlines()
    assert len(lines) == 2 and json.loads(lines[0])["circular_number"].endswith("/123")

    import pyarrow.parquet as pq
    table = pq.read_table(out / "corpus" / "corpus.parquet")
    assert table.num_rows == 2
    assert table.column_names == X.CORPUS_SCHEMA

    m = json.loads((out / "manifest.json").read_text())
    assert m == manifest
    assert m["version"] == "v2024.01"          # from max issue_date
    assert m["configs"]["corpus"]["rows"] == 2
    assert len(m["configs"]["corpus"]["source_sha256"]) == 64


# --- Task 2: chunks / lineage / eval configs ---

def _chunk(**over) -> dict:
    meta = {
        "circular_number": "SEBI/HO/CFD/P/CIR/2023/123",
        "issue_date": "2023-07-13",
        "effective_date": "",
        "subject": "Disclosure of material events",
        "issuing_department": "CFD",
        "supersession_status": "in_force",
        "amendment_history": [],
        "version_lineage": ["CIR/CFD/CMD/4/2015"],
    }
    base = {
        "id": "SEBI/HO/CFD/P/CIR/2023/123#preamble#0",
        "doc_id": "SEBI/HO/CFD/P/CIR/2023/123",
        "section": "SEBI/HO/CFD/P/CIR/2023/123/preamble/p0",
        "text": ("SEBI/HO/CFD/P/CIR/2023/123 | Disclosure of material events | "
                 "preamble\nCIRCULAR body text follows here."),
        "meta": meta,
    }
    base.update(over)
    return base


def test_chunk_row_splits_header_and_flattens_meta():
    row = X.build_chunk_rows([_chunk()])[0]
    assert row["chunk_id"] == "SEBI/HO/CFD/P/CIR/2023/123#preamble#0"
    assert row["context_header"] == "SEBI/HO/CFD/P/CIR/2023/123 | Disclosure of material events | preamble"
    assert row["text"] == "CIRCULAR body text follows here."
    assert row["circular_number"] == "SEBI/HO/CFD/P/CIR/2023/123"
    assert row["issuing_department"] == "CFD"
    assert row["version_lineage"] == ["CIR/CFD/CMD/4/2015"]


def test_chunk_row_has_exact_schema_no_amendment_history():
    row = X.build_chunk_rows([_chunk()])[0]
    assert list(row) == X.CHUNKS_SCHEMA
    assert "amendment_history" not in row
    assert "meta" not in row and "id" not in row


def test_build_lineage_rows_derives_forward_edges_only():
    lineage = {
        "supersedes": {"NEW/1": ["OLD/1", "OLD/2"]},
        "amends": {"NEW/1": ["OLD/3"]},
        "superseded_by": {"OLD/1": ["NEW/1"], "OLD/2": ["NEW/1"]},  # inverse; ignored
        "amended_by": {"OLD/3": ["NEW/1"]},                        # inverse; ignored
    }
    corpus_index = {"new/1": "2024-01-05"}   # normalized circular_number -> issue_date
    rows = X.build_lineage_rows(lineage, corpus_index)

    assert len(rows) == 3   # 2 supersedes + 1 amends; inverses not duplicated
    by_target = {r["target_circular"]: r for r in rows}
    assert by_target["OLD/1"]["relation"] == "supersedes"
    assert by_target["OLD/1"]["source_circular"] == "NEW/1"
    assert by_target["OLD/1"]["source_issue_date"] == "2024-01-05"
    assert by_target["OLD/1"]["target_in_corpus"] is False   # OLD/1 not in corpus_index
    assert by_target["OLD/3"]["relation"] == "amends"


def test_build_lineage_rows_flags_target_in_corpus():
    lineage = {"supersedes": {"NEW/1": ["OLD/1"]}, "amends": {},
              "superseded_by": {}, "amended_by": {}}
    corpus_index = {"new/1": "2024-01-05", "old/1": "2010-01-01"}
    rows = X.build_lineage_rows(lineage, corpus_index)
    assert rows[0]["target_in_corpus"] is True


def test_lineage_row_has_exact_schema():
    lineage = {"supersedes": {"NEW/1": ["OLD/1"]}, "amends": {},
              "superseded_by": {}, "amended_by": {}}
    rows = X.build_lineage_rows(lineage, {"new/1": "2024-01-05"})
    assert list(rows[0]) == X.LINEAGE_SCHEMA


def test_build_eval_rows_passes_through_golden_v6_records():
    golden = [{
        "id": "surv", "query": "q", "relevant_circulars": ["A/1"],
        "relevant_chunks": [], "answer_contains": "x", "must_contain": ["x"],
        "must_not_contain": [], "abstain": False, "task_type": "title_direct",
        "difficulty": "medium", "expected_citation_level": "circular",
        "rationale": "r", "label_source": "golden_v5", "review_status": "seeded",
    }]
    rows = X.build_eval_rows(golden)
    assert rows == golden
    assert list(rows[0]) == X.EVAL_SCHEMA


def test_export_eval_refuses_invalid_golden(tmp_path):
    bad = tmp_path / "golden_v6.jsonl"
    bad.write_text(json.dumps({"id": "x"}) + "\n")   # missing required fields
    with pytest.raises(ValueError, match="issue"):
        X.export_eval(bad, tmp_path / "out")


def test_full_export_writes_all_four_configs(tmp_path):
    corpus_src = tmp_path / "circulars.jsonl"
    corpus_src.write_text(json.dumps(_record()) + "\n")

    chunks_src = tmp_path / "chunks.jsonl"
    chunks_src.write_text(json.dumps(_chunk()) + "\n")

    lineage_src = tmp_path / "lineage.json"
    lineage_src.write_text(json.dumps({
        "supersedes": {"SEBI/HO/CFD/P/CIR/2023/123": ["CIR/CFD/CMD/4/2015"]},
        "amends": {}, "superseded_by": {}, "amended_by": {},
    }))

    golden_src = tmp_path / "golden_v6.jsonl"
    golden_src.write_text(json.dumps({
        "id": "surv", "query": "q", "relevant_circulars": ["A/1"],
        "relevant_chunks": [], "answer_contains": "x", "must_contain": ["x"],
        "must_not_contain": [], "abstain": False, "task_type": "title_direct",
        "difficulty": "medium", "expected_citation_level": "circular",
        "rationale": "r", "label_source": "golden_v5", "review_status": "seeded",
    }) + "\n")

    out = tmp_path / "out"
    manifest = X.export_all(corpus=corpus_src, chunks=chunks_src,
                            lineage=lineage_src, golden=golden_src, out_dir=out)

    for cfg in ("corpus", "chunks", "lineage", "eval"):
        assert (out / cfg / f"{cfg}.jsonl").exists()
        assert (out / cfg / f"{cfg}.parquet").exists()
        assert cfg in manifest["configs"]
