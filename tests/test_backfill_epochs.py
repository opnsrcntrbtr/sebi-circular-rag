"""Deterministic epoch assignment over the archived runs (spec A §6.3)."""
import json

from sebi_rag.autoresearch.epoch import assign_epochs, load_epoch_registry


def _r(corpus: str, ts: str) -> dict:
    return {"metadata": {"corpus_sha256": corpus, "golden_sha256": "f01d8779", "ts": ts}}


RUNS = [
    ("iv6-golden", _r("913e762c11", "2026-07-18T15:28:00+0530")),
    ("iv2-golden", _r("4083518f22", "2026-07-16T20:51:00+0530")),
    ("asof-baseline", _r("5f626dd933", "2026-08-04T13:19:00+0530")),
    ("baseline_retrieval", _r("8971de0f44", "2026-07-31T02:19:00+0530")),
    ("ft-golden", _r("4083518f22", "2026-07-16T11:41:00+0530")),
]


def test_epochs_numbered_by_earliest_observation():
    assert assign_epochs(RUNS) == {
        "4083518f": "E1",
        "913e762c": "E2",
        "8971de0f": "E3",
        "5f626dd9": "E4",
    }


def test_assignment_is_order_independent():
    assert assign_epochs(RUNS) == assign_epochs(list(reversed(RUNS)))


def test_runs_without_corpus_sha_are_ignored():
    runs = RUNS + [("pool-sweep", {"metadata": {}})]
    assert assign_epochs(runs) == assign_epochs(RUNS)


def test_registry_round_trips(tmp_path):
    path = tmp_path / "epochs.jsonl"
    path.write_text(
        json.dumps({"epoch": "E4", "corpus_sha256": "5f626dd933", "status": "open"})
        + "\n",
        encoding="utf-8",
    )
    assert load_epoch_registry(path) == {"5f626dd9": "E4"}


def test_missing_registry_is_empty(tmp_path):
    assert load_epoch_registry(tmp_path / "absent.jsonl") == {}
