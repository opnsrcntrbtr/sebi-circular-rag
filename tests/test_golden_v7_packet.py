"""Offline tests for make_packet.py: external sampling, blind human packet,
CSV ingest (spec 2026-07-23 sec 7)."""
from __future__ import annotations

import csv
import html
import json
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.make_packet import ingest_packet, sample_external, write_packet  # noqa: E402
from sebi_rag.benchmark import STRATA_TARGETS_V7  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
_TASK_TYPES = list(STRATA_TARGETS_V7)  # canonical 8, in the plan's fixed order


def _row(**over):
    base = {
        "id": "v7-td-001", "query": "What does this circular cover?",
        "task_type": "title_direct", "abstain": False,
    }
    base.update(over)
    return base


def _fixture_rows() -> list[dict]:
    """~12 synthetic rows spanning all 8 task_types (Task 1 fixture pattern);
    hard_negative/far_negative rows are abstain, matching the real golden_v7
    census where every row of those two strata abstains."""
    rows = []
    for i, tt in enumerate(_TASK_TYPES):
        n = 2 if i < 4 else 1
        for j in range(n):
            rows.append(_row(
                id=f"r-{tt}-{j}", task_type=tt,
                query=f"Query {j} about {tt.replace('_', ' ')}",
                abstain=tt in {"hard_negative", "far_negative"}))
    return rows


def _fixture_pools(rows: list[dict]) -> list[dict]:
    """2-candidate pools for every non-abstain row (packet fixture shape)."""
    pools = []
    for r in rows:
        if r["abstain"]:
            continue
        rid = r["id"]
        pools.append({"id": rid, "candidates": [
            {"chunk_id": f"{rid}-docA#s#0", "doc": f"{rid}-docA", "text": "t" * 60},
            {"chunk_id": f"{rid}-docB#s#1", "doc": f"{rid}-docB", "text": "u" * 60},
        ]})
    return pools


# ---------------------------------------------------------------------------
# (a) sample_external
# ---------------------------------------------------------------------------

def test_sample_external_deterministic_100_30_over_real_golden_v7():
    """Real run shape: 100 external / 30 human, human subset of external,
    every stratum represented, reproducible for the pinned seed."""
    rows = load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")
    ext1, hum1 = sample_external(rows, 100, 30, random.Random(20260723))
    ext2, hum2 = sample_external(rows, 100, 30, random.Random(20260723))

    assert ext1 == ext2
    assert hum1 == hum2
    assert len(ext1) == 100
    assert len(hum1) == 30
    assert len(set(ext1)) == 100  # no duplicates
    assert set(hum1) <= set(ext1)

    by_id = {r["id"]: r for r in rows}
    assert {by_id[i]["task_type"] for i in ext1} == set(STRATA_TARGETS_V7)


def test_sample_external_small_fixture_respects_quota_and_subset():
    rows = _fixture_rows()
    ext, hum = sample_external(rows, 6, 2, random.Random(20260723))
    ext2, hum2 = sample_external(rows, 6, 2, random.Random(20260723))

    assert ext == ext2 and hum == hum2  # deterministic
    assert len(ext) == 6
    assert len(hum) == 2
    assert set(hum) <= set(ext)
    all_ids = {r["id"] for r in rows}
    assert set(ext) <= all_ids
    assert len(set(ext)) == 6  # no duplicates even with small n/8-strata split


def test_sample_external_all_rows_when_n_equals_total():
    rows = _fixture_rows()
    ext, hum = sample_external(rows, len(rows), 4, random.Random(20260723))
    assert set(ext) == {r["id"] for r in rows}
    assert len(hum) == 4
    assert set(hum) <= set(ext)


# ---------------------------------------------------------------------------
# (b) write_packet
# ---------------------------------------------------------------------------

def test_write_packet_no_leakage_manifest_and_csv(tmp_path):
    rows = _fixture_rows()
    pools = _fixture_pools(rows)
    # inject a special char into one candidate to prove real escaping happens
    pools[0]["candidates"][0]["text"] = "margin <script>alert(1)</script> & co"
    non_abstain_ids = [r["id"] for r in rows if not r["abstain"]]
    abstain_ids = [r["id"] for r in rows if r["abstain"]]
    ids = non_abstain_ids + abstain_ids
    human_ids = ids  # cover every row for this test
    out_dir = tmp_path / "packet_human"

    write_packet(rows, pools, ids, human_ids, out_dir)

    html_text = (out_dir / "packet.html").read_text(encoding="utf-8")

    # anti-leakage: no scores/ranks anywhere in the rendered packet
    assert "score" not in html_text.lower()
    assert "rank" not in html_text.lower()

    # every row's query text is present (HTML-escaped)
    for r in rows:
        assert html.escape(r["query"]) in html_text

    # escaping is real, not assumed: raw markup must not survive
    assert "<script>alert(1)</script>" not in html_text
    assert html.escape("margin <script>alert(1)</script> & co") in html_text

    # abstain rows get the special no-excerpt yes/no prompt, not lettered options
    assert "is this answerable from sebi circulars?" in html_text.lower()
    assert "confirm abstain" in html_text.lower()
    assert abstain_ids  # sanity: fixture actually exercises this branch

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    for r in rows:
        if r["abstain"]:
            assert r["id"] not in manifest
        else:
            assert set(manifest[r["id"]]) == {"A", "B"}
            pool = next(p for p in pools if p["id"] == r["id"])
            assert set(manifest[r["id"]].values()) == {
                c["chunk_id"] for c in pool["candidates"]}

    with (out_dir / "labels_template.csv").open(newline="", encoding="utf-8") as f:
        csv_rows = {row["id"]: row for row in csv.DictReader(f)}
    assert set(csv_rows) == set(human_ids)
    for r in rows:
        row = csv_rows[r["id"]]
        if r["abstain"]:
            assert row["choices"] == "none"
        else:
            assert row["choices"] == ""
        assert row["expected_literal"] == ""


def test_write_packet_covers_only_human_ids_not_full_external_set(tmp_path):
    rows = _fixture_rows()
    pools = _fixture_pools(rows)
    non_abstain_ids = [r["id"] for r in rows if not r["abstain"]]
    ids = non_abstain_ids  # the full "external" set
    human_ids = non_abstain_ids[:2]  # strict subset
    out_dir = tmp_path / "packet_human"

    write_packet(rows, pools, ids, human_ids, out_dir)

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert set(manifest) == set(human_ids)
    with (out_dir / "labels_template.csv").open(newline="", encoding="utf-8") as f:
        csv_ids = {row["id"] for row in csv.DictReader(f)}
    assert csv_ids == set(human_ids)


# ---------------------------------------------------------------------------
# (c) ingest_packet
# ---------------------------------------------------------------------------

def _write_manifest(path: Path, manifest: dict) -> None:
    path.write_text(json.dumps(manifest), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "choices", "expected_literal"])
        w.writeheader()
        w.writerows(rows)


def test_ingest_packet_round_trips_hand_written_csv(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, {"r1": {"A": "docA#chunk0", "B": "docB#chunk1"}})

    csv_path = tmp_path / "labels.csv"
    _write_csv(csv_path, [
        {"id": "r1", "choices": "B", "expected_literal": "margin"},
        {"id": "r2", "choices": "none", "expected_literal": ""},  # no manifest entry: abstain-protocol
    ])

    votes = ingest_packet(csv_path, manifest_path)

    assert votes == [
        {"id": "r1", "annotator": "human", "governing": ["docB#chunk1"],
         "expected_literal": "margin"},
        {"id": "r2", "annotator": "human", "governing": [],
         "expected_literal": ""},
    ]


def test_ingest_packet_multi_letter_choice_maps_to_multiple_chunk_ids(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, {
        "r1": {"A": "docA#chunk0", "B": "docB#chunk1", "C": "docC#chunk2"}})
    csv_path = tmp_path / "labels.csv"
    _write_csv(csv_path, [{"id": "r1", "choices": "A;C", "expected_literal": "x"}])

    votes = ingest_packet(csv_path, manifest_path)
    assert votes == [{"id": "r1", "annotator": "human",
                       "governing": ["docA#chunk0", "docC#chunk2"],
                       "expected_literal": "x"}]


def test_ingest_packet_unknown_letter_raises(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, {"r1": {"A": "docA#chunk0"}})
    csv_path = tmp_path / "labels.csv"
    _write_csv(csv_path, [{"id": "r1", "choices": "Z", "expected_literal": ""}])

    with pytest.raises(ValueError):
        ingest_packet(csv_path, manifest_path)


def test_ingest_packet_dispute_on_abstain_row_keeps_governing_empty(tmp_path):
    """A human who thinks an abstain row IS answerable writes free text into
    expected_literal (the plan's dispute signal); governing stays [] since no
    excerpts were ever offered for an abstain-protocol row."""
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, {})  # no rows have manifest entries
    csv_path = tmp_path / "labels.csv"
    _write_csv(csv_path, [
        {"id": "r2", "choices": "none", "expected_literal": "actually the margin circular covers this"}])

    votes = ingest_packet(csv_path, manifest_path)
    assert votes == [{"id": "r2", "annotator": "human", "governing": [],
                       "expected_literal": "actually the margin circular covers this"}]
