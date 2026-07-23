"""End-to-end driver test on a temporary corpus (no network)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_reg_edges as B  # noqa: E402

CIRCS = [
    {"circular_number": "C/1", "subject": "", "issue_date": "2020-01-01",
     "text": "under SEBI (Mutual Funds) Regulations, 1996 the AMC shall comply.",
     "validity_status": "current"},
    {"circular_number": "C/2", "subject": "", "issue_date": "2024-01-01",
     "text": "per SEBI (Mutual Funds) Regulations, 2026 schemes shall report.",
     "validity_status": "current"},
    {"circular_number": "C/3", "subject": "", "issue_date": "2024-06-01",
     "text": "no statutory reference at all.", "validity_status": "current"},
]
REGS = [{"reg_id": "mutual-funds-2026", "title": "T", "short_name": "Mutual Funds",
         "year": 2026, "status": "in_force", "supersedes_reg": []}]


def _setup(tmp_path):
    c = tmp_path / "circulars.jsonl"
    r = tmp_path / "regulations.jsonl"
    B.write_jsonl(c, CIRCS)
    B.write_jsonl(r, REGS)
    return c, r


def test_driver_writes_edges_and_annotates(tmp_path):
    c, r = _setup(tmp_path)
    edges_out = tmp_path / "regulation_edges.jsonl"
    report = tmp_path / "unresolved.txt"
    rc = B.main(["--corpus", str(c), "--regulations", str(r),
                 "--edges", str(edges_out), "--report", str(report)])
    assert rc == 0

    edges = B.load_jsonl(edges_out)
    assert {e["source"] for e in edges} == {"C/1", "C/2"}
    assert all(e["relation"] == "cites" for e in edges)

    circs = B.load_jsonl(c)
    by_num = {x["circular_number"]: x for x in circs}
    assert by_num["C/1"]["regulatory_basis_status"] == "repealed_basis"
    assert by_num["C/2"]["regulatory_basis_status"] == "current"
    assert by_num["C/3"]["regulatory_basis_status"] == "unknown"


def test_driver_appends_repealed_stub_to_the_regulations_file(tmp_path):
    c, r = _setup(tmp_path)
    B.main(["--corpus", str(c), "--regulations", str(r),
            "--edges", str(tmp_path / "e.jsonl"),
            "--report", str(tmp_path / "u.txt")])
    regs = {x["reg_id"]: x for x in B.load_jsonl(r)}
    assert "mutual-funds-1996" in regs
    assert regs["mutual-funds-1996"]["status"] == "repealed"
    assert regs["mutual-funds-1996"]["superseded_by_reg"] == "mutual-funds-2026"
    assert "mutual-funds-1996" in regs["mutual-funds-2026"]["supersedes_reg"]


def test_driver_is_idempotent(tmp_path):
    c, r = _setup(tmp_path)
    args = ["--corpus", str(c), "--regulations", str(r),
            "--edges", str(tmp_path / "e.jsonl"),
            "--report", str(tmp_path / "u.txt")]
    B.main(args)
    first_regs = r.read_text()
    first_circs = c.read_text()
    B.main(args)
    assert r.read_text() == first_regs
    assert c.read_text() == first_circs


def test_driver_preserves_unrelated_circular_fields(tmp_path):
    c, r = _setup(tmp_path)
    B.main(["--corpus", str(c), "--regulations", str(r),
            "--edges", str(tmp_path / "e.jsonl"),
            "--report", str(tmp_path / "u.txt")])
    circs = B.load_jsonl(c)
    assert all(x["validity_status"] == "current" for x in circs)
    assert all(x["issue_date"] for x in circs)


def test_driver_writes_the_unresolved_report(tmp_path):
    c, r = _setup(tmp_path)
    B.write_jsonl(c, CIRCS + [{
        "circular_number": "C/4", "subject": "", "issue_date": "2024-01-01",
        "text": "per SEBI (Entirely Fictional Thing) Regulations, 1901.",
        "validity_status": "current"}])
    report = tmp_path / "unresolved.txt"
    B.main(["--corpus", str(c), "--regulations", str(r),
            "--edges", str(tmp_path / "e.jsonl"), "--report", str(report)])
    # A stub is minted for it, so it resolves on the second pass; the report
    # exists either way and is never a crash.
    assert report.exists()


def test_missing_regulations_file_exits_nonzero_without_writing(tmp_path):
    c = tmp_path / "circulars.jsonl"
    B.write_jsonl(c, CIRCS)
    before = c.read_text()
    rc = B.main(["--corpus", str(c), "--regulations", str(tmp_path / "nope.jsonl"),
                 "--edges", str(tmp_path / "e.jsonl"),
                 "--report", str(tmp_path / "u.txt")])
    assert rc != 0
    assert c.read_text() == before
    assert not (tmp_path / "e.jsonl").exists()


def test_load_jsonl_skips_blank_lines(tmp_path):
    p = tmp_path / "x.jsonl"
    p.write_text('{"a":1}\n\n{"a":2}\n', encoding="utf-8")
    assert B.load_jsonl(p) == [{"a": 1}, {"a": 2}]
