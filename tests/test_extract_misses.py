"""Offline tests for the failure-taxonomy miss classifier (throwaway research)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "analysis"))

from extract_misses import classify_query, load_run  # noqa: E402


CHUNKS = [
    "SEBI/HO/A/1#preamble#0",
    "SEBI/HO/A/1#body#1",
    "SEBI/HO/B/2#preamble#0",
    "SEBI/HO/C/3#preamble#0",
]


def test_hit_when_relevant_doc_in_top10_docs():
    cls, rank = classify_query(CHUNKS, ["SEBI/HO/B/2"])
    assert cls == "hit"
    assert rank == 2  # docs dedupe to [A/1, B/2, C/3]; B/2 is doc-rank 2


def test_candidate_miss_when_relevant_doc_absent():
    cls, rank = classify_query(CHUNKS, ["SEBI/HO/ZZZ/9"])
    assert cls == "candidate_miss"
    assert rank == -1


def test_ranked_low_when_first_relevant_doc_after_rank10():
    ranked = [f"SEBI/HO/D{i}/{i}#p#0" for i in range(12)] + ["SEBI/HO/B/2#p#0"]
    cls, rank = classify_query(ranked, ["SEBI/HO/B/2"])
    assert cls == "ranked_low"
    assert rank == 13


def test_doc_matching_is_normalized():
    # normalize_circular_number: strips whitespace/punct, drops leading SEBI/, casefolds
    cls, _ = classify_query(CHUNKS, ["HO/B/2 "])
    assert cls == "hit"


def test_load_run_handles_chunk_ids_with_spaces(tmp_path):
    # Real chunk IDs embed section headings containing spaces.
    run = tmp_path / "run.trec"
    run.write_text(
        "q1 Q0 HO/X/1#1. For effective surveillance of the market#6 1 0.5 name\n"
        "q1 Q0 SEBI/HO/B/2#preamble#0 2 0.4 name\n",
        encoding="utf-8",
    )
    parsed = load_run(run)
    assert parsed == {
        "q1": [
            "HO/X/1#1. For effective surveillance of the market#6",
            "SEBI/HO/B/2#preamble#0",
        ]
    }
