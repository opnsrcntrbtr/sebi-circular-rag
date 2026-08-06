"""Controlled-vocabulary label_tier over golden_v7 (spec A §8.3)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from autoresearch.normalize_label_tier import TIERS, classify_tier  # noqa: E402

GOLDEN = Path(__file__).resolve().parents[1] / "eval" / "golden" / "golden_v7.jsonl"


def test_human_corrections_are_human():
    assert classify_tier("corrected: actually SEBI SAST topic") == "human"
    assert classify_tier("corrected: actually SEBI topic") == "human"


def test_external_flip_is_human():
    assert classify_tier("external-flip") == "human"


def test_human_reviewed_outranks_the_last_writer_string():
    """label_source records the LAST WRITER, not who reviewed the row.

    17 of the 30 packet_human rows carry label_source 'v7-draft-2026-07' and 7
    carry a claude string. Classifying on the string alone would bury them.
    """
    assert classify_tier("v7-draft-2026-07", human_reviewed=True) == "human"
    assert classify_tier("claude (draft adjudication)", human_reviewed=True) == "human"
    assert classify_tier("golden_v5", human_reviewed=True) == "human"


def test_arbitration_resolved_is_arbitrated():
    assert classify_tier("claude (arbitration resolved: title_direct)") == "arbitrated"
    assert classify_tier("claude (qwen failed to find governing)") == "arbitrated"


def test_single_claude_pass_is_model_single():
    assert classify_tier("claude (draft adjudication)") == "model_single"
    assert classify_tier("claude (abstain validation)") == "model_single"


def test_v5_inheritance_is_flagged():
    assert classify_tier("golden_v5") == "inherited_v5"
    assert classify_tier("golden_v5 (promoted golden_v5)") == "inherited_v5"


def test_seeded_draft_is_draft_seeded():
    assert classify_tier("v7-draft-2026-07") == "draft_seeded"


def test_unrecognised_value_is_unknown_not_an_error():
    assert classify_tier("something nobody wrote down") == "unknown"


def test_every_tier_is_in_the_vocabulary():
    for src in [
        "corrected: actually SEBI SAST topic",
        "claude (arbitration resolved: title_direct)",
        "claude (draft adjudication)",
        "golden_v5",
        "v7-draft-2026-07",
        "mystery",
    ]:
        assert classify_tier(src) in TIERS


def test_every_golden_row_carries_a_valid_tier():
    rows = [
        json.loads(line)
        for line in GOLDEN.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 260
    for row in rows:
        assert row["label_tier"] in TIERS
        assert row["label_source"], "free-text provenance must be preserved"


def test_no_row_is_classified_unknown():
    rows = [
        json.loads(line)
        for line in GOLDEN.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    unknown = [r["id"] for r in rows if r["label_tier"] == "unknown"]
    assert unknown == [], f"unclassified rows are a mapping gap: {unknown}"


def test_agreement_apply_preserves_label_tier():
    """`make golden-v7-agree` rewrites golden_v7.jsonl via apply() +
    write_jsonl. If apply() rebuilt rows from a fixed key list instead of
    copying, every tier would be silently erased on the next agreement run.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "golden_v7"))
    from agreement import apply

    rows = [
        {"id": "r1", "label_tier": "human", "label_source": "corrected: x",
         "relevant_chunks": [], "review_status": "adjudicated"},
        {"id": "r2", "label_tier": "model_single", "label_source": "claude (draft)",
         "relevant_chunks": [], "review_status": "adjudicated"},
    ]
    out = apply(rows, {"r1": ("promote", None)})
    assert [r["label_tier"] for r in out] == ["human", "model_single"]
