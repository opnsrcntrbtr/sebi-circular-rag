import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.seed_v7 import carry_v6_rows  # noqa: E402


def test_carry_preserves_ids_and_adds_v7_defaults():
    v6 = [{"id": "surv", "query": "q", "relevant_circulars": ["C/1"],
           "relevant_chunks": [], "answer_contains": "a", "must_contain": ["a"],
           "must_not_contain": [], "abstain": False, "task_type": "title_direct",
           "difficulty": "medium", "expected_citation_level": "circular",
           "rationale": "r", "label_source": "golden_v5", "review_status": "seeded"}]
    out = carry_v6_rows(v6)
    assert out[0]["id"] == "surv"
    assert out[0]["as_of"] is None and out[0]["must_not_cite"] == []
    assert out[0]["review_status"] == "seeded"


def test_seed_script_writes_56_valid_rows(tmp_path):
    root = Path(__file__).resolve().parents[1]
    out = tmp_path / "golden_v7.jsonl"
    subprocess.run(
        [sys.executable, str(root / "scripts" / "golden_v7" / "seed_v7.py"),
         "--out", str(out)], check=True)
    rows = [json.loads(l) for l in out.read_text().splitlines()]
    assert len(rows) == 56
