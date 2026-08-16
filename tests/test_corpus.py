"""corpus.load_circulars edge-case coverage.

load_circulars reads a JSONL corpus file, maps each record to CircularMeta,
and calls hierarchical_chunk on the text.  This module exercises:

- empty file / blank lines
- malformed JSON (skip vs error)
- missing required fields (circular_number, text)
- optional field defaults
- CircularMeta field mapping fidelity
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from sebi_rag.corpus import load_circulars
from sebi_rag.segment import CircularMeta


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _write_jsonl(path: Path, lines: list[str]) -> None:
    """Write *lines* (already-JSON strings) to a temp JSONL file."""
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _record(
    circular_number: str = "SEBI/HO/T/P/CIR/2026/1",
    text: str = "Some circular text with enough content.",
    **fields,
) -> dict:
    """Build a minimal corpus record with optional overrides."""
    base = {
        "circular_number": circular_number,
        "text": text,
    }
    base.update(fields)
    return base


# ---------------------------------------------------------------------------
# Empty / blank-line handling
# ---------------------------------------------------------------------------

def test_load_circulars_empty_file(tmp_path: Path) -> None:
    """An empty corpus file returns zero chunks."""
    f = tmp_path / "empty.jsonl"
    f.write_text("", encoding="utf-8")
    assert load_circulars(f) == []


def test_load_circulars_blank_lines_only(tmp_path: Path) -> None:
    """A file with only blank lines returns zero chunks."""
    f = tmp_path / "blanks.jsonl"
    f.write_text("\n\n  \n\n", encoding="utf-8")
    assert load_circulars(f) == []


# ---------------------------------------------------------------------------
# Missing required fields
# ---------------------------------------------------------------------------

def test_load_circulars_missing_text_raises(tmp_path: Path) -> None:
    """A record without 'text' raises KeyError."""
    f = tmp_path / "no_text.jsonl"
    _write_jsonl(f, [json.dumps({"circular_number": "SEBI/HO/X/2026/1"})])
    with pytest.raises(KeyError, match="text"):
        load_circulars(f)


def test_load_circulars_missing_circular_number_raises(tmp_path: Path) -> None:
    """A record without 'circular_number' raises KeyError."""
    f = tmp_path / "no_cid.jsonl"
    _write_jsonl(f, [json.dumps({"text": "some text"})])
    with pytest.raises(KeyError, match="circular_number"):
        load_circulars(f)


# ---------------------------------------------------------------------------
# Optional field defaults
# ---------------------------------------------------------------------------

def test_load_circulars_optional_fields_defaults(tmp_path: Path) -> None:
    """Missing optional fields get sensible defaults."""
    f = tmp_path / "minimal.jsonl"
    _write_jsonl(f, [json.dumps({"circular_number": "SEBI/HO/X/2026/1", "text": "x"})])
    chunks = load_circulars(f)
    assert len(chunks) == 1
    meta = chunks[0].meta
    assert meta["issue_date"] == ""
    assert meta["effective_date"] == ""
    assert meta["subject"] == ""
    assert meta["issuing_department"] == ""
    assert meta["supersession_status"] == "in_force"
    assert meta["amendment_history"] == ()
    assert meta["version_lineage"] == ()
    assert meta["circular_type"] == ""
    assert meta["validity_status"] == ""
    assert meta["superseded_by_id"] == ()


def test_load_circulars_optional_fields_preserved(tmp_path: Path) -> None:
    """Provided optional fields are passed through to CircularMeta."""
    rec = _record(
        issue_date="2026-01-15",
        effective_date="2026-02-01",
        subject="FPI norms update",
        issuing_department="Department of Market Regulation",
        supersession_status="superseded",
        amendment_history=("2025-12-01",),
        version_lineage=("SEBI/HO/X/2025/1",),
        circular_type="circular",
        validity_status="active",
        superseded_by_id=["SEBI/HO/X/2027/1"],
    )
    f = tmp_path / "full.jsonl"
    _write_jsonl(f, [json.dumps(rec)])
    chunks = load_circulars(f)
    assert len(chunks) == 1
    meta = chunks[0].meta
    assert meta["issue_date"] == "2026-01-15"
    assert meta["effective_date"] == "2026-02-01"
    assert meta["subject"] == "FPI norms update"
    assert meta["issuing_department"] == "Department of Market Regulation"
    assert meta["supersession_status"] == "superseded"
    assert meta["amendment_history"] == ("2025-12-01",)
    assert meta["version_lineage"] == ("SEBI/HO/X/2025/1",)
    assert meta["circular_type"] == "circular"
    assert meta["validity_status"] == "active"
    assert meta["superseded_by_id"] == ("SEBI/HO/X/2027/1",)


# ---------------------------------------------------------------------------
# Multiple records / chunking
# ---------------------------------------------------------------------------

def test_load_circulars_multiple_records(tmp_path: Path) -> None:
    """Multiple records produce multiple chunks."""
    recs = [
        _record(circular_number="SEBI/HO/X/2026/1", text="First circular."),
        _record(circular_number="SEBI/HO/X/2026/2", text="Second circular."),
    ]
    f = tmp_path / "multi.jsonl"
    _write_jsonl(f, [json.dumps(r) for r in recs])
    chunks = load_circulars(f)
    assert len(chunks) >= 2


def test_load_circulars_blank_line_skipped(tmp_path: Path) -> None:
    """Blank lines between records are silently skipped."""
    recs = [
        _record(circular_number="SEBI/HO/X/2026/1", text="First."),
        _record(circular_number="SEBI/HO/X/2026/2", text="Second."),
    ]
    f = tmp_path / "blanks_between.jsonl"
    f.write_text(
        json.dumps(recs[0]) + "\n\n  \n" + json.dumps(recs[1]) + "\n",
        encoding="utf-8",
    )
    chunks = load_circulars(f)
    assert len(chunks) >= 2


# ---------------------------------------------------------------------------
# Malformed JSON handling
# ---------------------------------------------------------------------------

def test_load_circulars_malformed_json_raises(tmp_path: Path) -> None:
    """Malformed JSON raises ValueError (json.loads default)."""
    f = tmp_path / "bad.jsonl"
    _write_jsonl(f, ["not valid json"])
    with pytest.raises(ValueError):
        load_circulars(f)


# ---------------------------------------------------------------------------
# Path type acceptance
# ---------------------------------------------------------------------------

def test_load_circulars_accepts_string_path(tmp_path: Path) -> None:
    """load_circulars accepts both str and Path."""
    f = tmp_path / "str.jsonl"
    _write_jsonl(f, [json.dumps(_record())])
    chunks = load_circulars(str(f))
    assert len(chunks) >= 1


def test_load_circulars_accepts_path_object(tmp_path: Path) -> None:
    """load_circulars accepts a pathlib.Path."""
    f = tmp_path / "path.jsonl"
    _write_jsonl(f, [json.dumps(_record())])
    chunks = load_circulars(f)
    assert len(chunks) >= 1
