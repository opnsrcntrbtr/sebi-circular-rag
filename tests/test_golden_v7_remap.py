"""Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.remap_doc_ids import remap  # noqa: E402


def _row(**over):
    base = {"id": "v7-td-005", "relevant_circulars": ["CIR/IMD/DF/5/2013"],
            "must_not_cite": [], "relevant_chunks": [
                {"doc": "CIR/IMD/DF/5/2013", "quote": "x" * 50}]}
    base.update(over)
    return base


def test_remaps_relevant_circulars_and_span_docs():
    rows, n = remap([_row()], {"CIR/IMD/DF/5/2013": "CIR/IMD/DF/14/2013"})
    assert rows[0]["relevant_circulars"] == ["CIR/IMD/DF/14/2013"]
    assert rows[0]["relevant_chunks"][0]["doc"] == "CIR/IMD/DF/14/2013"
    assert n == 2


def test_remaps_must_not_cite():
    rows, n = remap([_row(must_not_cite=["CIR/IMD/DF/5/2013"],
                          relevant_circulars=["OTHER/1"], relevant_chunks=[])],
                    {"CIR/IMD/DF/5/2013": "CIR/IMD/DF/14/2013"})
    assert rows[0]["must_not_cite"] == ["CIR/IMD/DF/14/2013"]
    assert n == 1


def test_unmapped_rows_untouched():
    rows, n = remap([_row(relevant_circulars=["KEEP/1"], relevant_chunks=[])],
                    {"CIR/IMD/DF/5/2013": "CIR/IMD/DF/14/2013"})
    assert rows[0]["relevant_circulars"] == ["KEEP/1"] and n == 0


def test_matching_is_normalization_insensitive():
    rows, n = remap([_row(relevant_circulars=["SEBI/CIR/IMD/DF/5/2013"],
                          relevant_chunks=[])],
                    {"CIR/IMD/DF/5/2013": "CIR/IMD/DF/14/2013"})
    assert rows[0]["relevant_circulars"] == ["CIR/IMD/DF/14/2013"] and n == 1


def test_input_rows_are_not_mutated():
    src = _row()
    remap([src], {"CIR/IMD/DF/5/2013": "CIR/IMD/DF/14/2013"})
    assert src["relevant_circulars"] == ["CIR/IMD/DF/5/2013"]
    assert src["relevant_chunks"][0]["doc"] == "CIR/IMD/DF/5/2013"
