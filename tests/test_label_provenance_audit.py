"""Read-only cross-tab of label_source against annotation artifacts (spec A §8.2)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from autoresearch.audit_label_provenance import audit  # noqa: E402

ROWS = [
    {"id": "a", "label_source": "claude (draft adjudication)"},
    {"id": "b", "label_source": "claude (draft adjudication)"},
    {"id": "c", "label_source": "corrected: actually SEBI SAST topic"},
    {"id": "d", "label_source": "v7-draft-2026-07"},
]
ARTIFACTS = {
    "votes.jsonl": {"a", "b"},
    "packet_human": {"c"},
    "arbitration_queue.jsonl": set(),
}


def test_counts_rows_per_label_source():
    result = audit(ROWS, ARTIFACTS)
    assert result["by_source"]["claude (draft adjudication)"] == 2
    assert result["by_source"]["v7-draft-2026-07"] == 1


def test_reports_artifact_coverage_per_source():
    result = audit(ROWS, ARTIFACTS)
    assert result["coverage"]["claude (draft adjudication)"]["votes.jsonl"] == 2
    assert result["coverage"]["corrected: actually SEBI SAST topic"]["packet_human"] == 1


def test_lists_rows_no_artifact_accounts_for():
    result = audit(ROWS, ARTIFACTS)
    assert result["unaccounted"] == ["d"]


def test_empty_artifact_sets_do_not_crash():
    result = audit(ROWS, {"arbitration_queue.jsonl": set()})
    assert sorted(result["unaccounted"]) == ["a", "b", "c", "d"]
