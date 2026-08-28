"""Offline tests for scripts/finetune/train_lora.py's pure pieces. The
actual LoRA-apply + train + save cycle needs a real bge-m3 load and was
verified empirically via a throwaway smoke test before this script was
written (see its module docstring) - not re-run here, matching the
offline-first convention (HashEmbedder) used across this test suite.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from finetune.train_lora import (  # noqa: E402
    build_dataset,
    check_trainable_ratio,
    load_pairs,
)


def _row(q="query", pos="positive", n_negs=5, template="t", doc="D"):
    return {"query": q, "positive": pos,
           "neg": [f"neg{i}" for i in range(n_negs)],
           "template": template, "source_doc": doc}


# ---------------------------------------------------------------------------
# load_pairs
# ---------------------------------------------------------------------------

def test_load_pairs_reads_jsonl(tmp_path):
    path = tmp_path / "pairs.jsonl"
    path.write_text(json.dumps(_row()) + "\n", encoding="utf-8")
    rows = load_pairs([path], n_negatives=4)
    assert len(rows) == 1
    assert rows[0]["query"] == "query"


def test_load_pairs_merges_multiple_files(tmp_path):
    p1 = tmp_path / "a.jsonl"
    p2 = tmp_path / "b.jsonl"
    p1.write_text(json.dumps(_row(q="a")) + "\n", encoding="utf-8")
    p2.write_text(json.dumps(_row(q="b")) + "\n", encoding="utf-8")
    rows = load_pairs([p1, p2], n_negatives=4)
    assert {r["query"] for r in rows} == {"a", "b"}


def test_load_pairs_skips_rows_with_too_few_negatives(tmp_path):
    """Defensive: mine_structural_pairs.py already guarantees >=5 negatives
    per row, but a hand-edited or foreign pairs file might not - such a row
    must be skipped, never silently truncated/padded."""
    path = tmp_path / "pairs.jsonl"
    path.write_text(json.dumps(_row(n_negs=2)) + "\n", encoding="utf-8")
    assert load_pairs([path], n_negatives=4) == []


def test_load_pairs_skips_blank_lines(tmp_path):
    path = tmp_path / "pairs.jsonl"
    path.write_text(json.dumps(_row()) + "\n\n  \n", encoding="utf-8")
    assert len(load_pairs([path], n_negatives=4)) == 1


# ---------------------------------------------------------------------------
# build_dataset - column order is significant (MNRL reads roles
# positionally: anchor, positive, then negative_1..negative_n)
# ---------------------------------------------------------------------------

def test_build_dataset_column_order_is_anchor_positive_then_negatives():
    rows = [_row(q="q1", pos="p1"), _row(q="q2", pos="p2")]
    ds = build_dataset(rows, n_negatives=4)
    assert ds.column_names == ["anchor", "positive",
                               "negative_1", "negative_2",
                               "negative_3", "negative_4"]


def test_build_dataset_content_matches_input_rows():
    rows = [_row(q="query text", pos="positive text")]
    ds = build_dataset(rows, n_negatives=2)
    assert ds[0]["anchor"] == "query text"
    assert ds[0]["positive"] == "positive text"
    assert ds[0]["negative_1"] == "neg0"
    assert ds[0]["negative_2"] == "neg1"


def test_build_dataset_respects_n_negatives_truncation():
    """Only the first n_negatives of a row's (up to 5) mined negatives are
    used - the plan's Phase 2 spec is explicitly 1 positive + 4 hard
    negatives, the 5th mined negative is buffer, never silently included."""
    rows = [_row(n_negs=5)]
    ds = build_dataset(rows, n_negatives=4)
    assert "negative_5" not in ds.column_names
    assert ds[0]["negative_4"] == "neg3"


def test_build_dataset_empty_rows_produces_empty_dataset():
    ds = build_dataset([], n_negatives=4)
    assert len(ds) == 0
    assert ds.column_names == ["anchor", "positive",
                               "negative_1", "negative_2",
                               "negative_3", "negative_4"]


# ---------------------------------------------------------------------------
# check_trainable_ratio - the two failure modes apply_lora guards against
# ---------------------------------------------------------------------------

def test_check_trainable_ratio_passes_for_realistic_lora_fraction():
    # measured on the real model in the pre-write smoke test: 7.1M / 567.8M
    check_trainable_ratio(trainable=7_110_656, total=567_754_752,
                         target_modules=["query", "key", "value", "dense"], r=16)


def test_check_trainable_ratio_raises_on_zero_trainable():
    """The classic PEFT footgun: a target_modules list that matches nothing
    in the model's architecture applies zero adapters and fails SILENTLY
    (no exception from add_adapter itself) unless the caller checks."""
    try:
        check_trainable_ratio(trainable=0, total=567_754_752,
                             target_modules=["wrong_name"], r=16)
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert "zero trainable" in str(e)


def test_check_trainable_ratio_raises_when_too_broad():
    """Trainable params exceeding 10% of the full model means the
    "LoRA" adapter isn't parameter-efficient anymore - it's a full
    fine-tune in disguise, losing the overfitting protection that's the
    whole reason LoRA was chosen over full FT for this intervention."""
    try:
        check_trainable_ratio(trainable=100_000_000, total=567_754_752,
                             target_modules=["everything"], r=16)
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert "too broad" in str(e)


def test_check_trainable_ratio_boundary_at_exactly_10_percent_passes():
    check_trainable_ratio(trainable=10_000_000, total=100_000_000,
                         target_modules=["x"], r=16, max_fraction=0.1)
