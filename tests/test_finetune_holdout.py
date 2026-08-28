"""Offline tests for scripts/finetune/holdout_split.py - the contamination
boundary every Phase 0 mining script asserts against. See the module
docstring for why a slice (not the whole 159) is held out, and why rows are
classified held_out/in_corpus/mixed rather than pooled into one number.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from finetune.holdout_split import (  # noqa: E402
    build,
    classify_rows,
    gold_circulars,
    split_holdout,
)


def _row(rid: str, relevant: list[str]) -> dict:
    return {"id": rid, "relevant_circulars": relevant}


def test_gold_circulars_dedupes_and_sorts_across_rows():
    golden = [_row("r1", ["B", "A"]), _row("r2", ["A", "C"]), _row("r3", [])]
    assert gold_circulars(golden) == ["A", "B", "C"]


def test_split_holdout_is_deterministic_for_same_seed():
    circulars = [f"CIR/{i}" for i in range(159)]
    h1, m1 = split_holdout(circulars, fraction=0.30, seed=42)
    h2, m2 = split_holdout(circulars, fraction=0.30, seed=42)
    assert h1 == h2 and m1 == m2


def test_split_holdout_rounds_and_partitions_exhaustively():
    circulars = [f"CIR/{i}" for i in range(159)]
    holdout, minable = split_holdout(circulars, fraction=0.30, seed=42)
    assert len(holdout) == round(159 * 0.30) == 48
    assert len(minable) == 159 - 48
    assert set(holdout) & set(minable) == set()
    assert set(holdout) | set(minable) == set(circulars)


def test_split_holdout_different_seed_gives_different_slice():
    circulars = [f"CIR/{i}" for i in range(159)]
    h1, _ = split_holdout(circulars, seed=42)
    h2, _ = split_holdout(circulars, seed=7)
    assert h1 != h2


def test_classify_rows_single_doc_held_out():
    holdout = {"A"}
    golden = [_row("r1", ["A"])]
    result = classify_rows(golden, holdout)
    assert result == {"held_out": ["r1"], "in_corpus": [], "mixed": []}


def test_classify_rows_single_doc_in_corpus():
    holdout = {"A"}
    golden = [_row("r1", ["B"])]
    result = classify_rows(golden, holdout)
    assert result == {"held_out": [], "in_corpus": ["r1"], "mixed": []}


def test_classify_rows_multi_doc_straddling_is_mixed():
    """A multi_hop or lineage_supersession row citing both a held-out and a
    minable circular is neither a clean generalization test nor a clean
    in-corpus test - it must land in its own bucket, never pooled into
    either headline number."""
    holdout = {"A"}
    golden = [_row("r1", ["A", "B"])]
    result = classify_rows(golden, holdout)
    assert result == {"held_out": [], "in_corpus": [], "mixed": ["r1"]}


def test_classify_rows_multi_doc_all_held_out_counts_as_held_out():
    holdout = {"A", "B"}
    golden = [_row("r1", ["A", "B"])]
    result = classify_rows(golden, holdout)
    assert result["held_out"] == ["r1"]


def test_classify_rows_excludes_rows_with_no_relevant_circulars():
    """Pure-abstention rows have no gold document to be contaminated by or
    generalize to - they belong in none of the three buckets."""
    holdout = {"A"}
    golden = [_row("r1", [])]
    result = classify_rows(golden, holdout)
    assert result == {"held_out": [], "in_corpus": [], "mixed": []}


def test_build_end_to_end_partitions_are_disjoint_and_row_split_sums(tmp_path):
    golden_path = tmp_path / "golden.jsonl"
    import json
    rows = [_row(f"r{i}", [f"CIR/{i % 20}"]) for i in range(50)]
    golden_path.write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    result = build(golden_path, fraction=0.30, seed=42)

    holdout = set(result["holdout_docs"])
    minable = set(result["minable_gold_docs"])
    assert holdout & minable == set()
    assert result["gold_circulars_total"] == 20
    total_classified = sum(result["row_split_counts"].values())
    assert total_classified == 50  # every row has exactly one gold doc here
