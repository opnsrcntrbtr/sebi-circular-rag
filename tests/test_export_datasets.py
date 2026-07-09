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
