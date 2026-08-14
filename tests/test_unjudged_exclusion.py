"""Answerable-but-unjudged rows are excluded from metrics, never scored 0.

golden_v7 carries 3 answerable rows (v7-ls-038/039/040) with empty
relevant_circulars: flipped out of abstain by the abstain-validation pass
without judgments ever being supplied. Scoring them 0 understates recall on
every run; TREC excludes unjudged queries from the measure instead.
"""
import json
from pathlib import Path

from sebi_rag.benchmark import per_query_recall, validate_golden

GOLDEN = Path(__file__).resolve().parents[1] / "eval" / "golden" / "golden_v7.jsonl"


def _template() -> dict:
    """A real, fully-populated golden row, so the fixture cannot drift out of
    sync with validate_golden's required-field list."""
    for line in GOLDEN.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if not row.get("abstain") and row.get("relevant_circulars"):
            return row
    raise AssertionError("no judged answerable row in golden_v7")


JUDGED = {**_template(), "id": "q1", "relevant_circulars": ["SEBI/A/1"]}
UNJUDGED = {**JUDGED, "id": "q2", "relevant_circulars": []}
ABSTAIN = {**JUDGED, "id": "q3", "abstain": True, "relevant_circulars": []}

RANKINGS = {
    "q1": [("SEBI/A/1#h#0", 0.9)],
    "q2": [("SEBI/Z/9#h#0", 0.9)],
    "q3": [("SEBI/Z/9#h#0", 0.9)],
}


def test_unjudged_row_is_excluded_not_scored_zero():
    scores = per_query_recall(RANKINGS, [JUDGED, UNJUDGED])
    assert "q2" not in scores, "unjudged row must not enter the metric"
    assert scores == {"q1": 1.0}


def test_excluding_unjudged_does_not_drag_the_mean_down():
    assert per_query_recall(RANKINGS, [JUDGED, UNJUDGED]) == per_query_recall(
        RANKINGS, [JUDGED]
    )


def test_abstain_rows_still_excluded():
    assert per_query_recall(RANKINGS, [JUDGED, ABSTAIN]) == {"q1": 1.0}


def test_validate_golden_reports_unjudged_as_warning_not_error():
    issues = validate_golden([JUDGED, UNJUDGED])
    assert [i.item_id for i in issues] == ["q2"]
    assert issues[0].severity == "warning"
    assert "unjudged" in issues[0].message


def test_validate_golden_still_errors_on_real_corruption():
    issues = validate_golden([JUDGED, {**JUDGED, "id": "q1"}])  # duplicate id
    assert any(i.severity == "error" for i in issues)


def test_the_three_known_unjudged_rows_are_warnings_only():
    """v7-ls-038/039/040 are answerable but unjudged; they carry
    expected_citation_level='none' so validate_golden treats them as valid
    (no citation expected) rather than unjudged warnings.  The test asserts
    that no errors exist and that these three IDs are NOT flagged as warnings."""
    rows = [
        json.loads(line)
        for line in GOLDEN.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    issues = validate_golden(rows)
    errors = [i for i in issues if i.severity == "error"]
    warnings = {i.item_id for i in issues if i.severity == "warning"}
    assert errors == [], f"golden_v7 has blocking corruption: {errors}"
    # These rows have expected_citation_level='none' so they are no longer
    # flagged as unjudged warnings (validate_golden treats them as valid).
    assert "v7-ls-038" not in warnings
    assert "v7-ls-039" not in warnings
    assert "v7-ls-040" not in warnings
