"""Back-conversion of archived runfiles into valid TREC artifacts (spec A §3.4)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from autoresearch.convert_legacy_runs import convert_run_dir  # noqa: E402

LEGACY = (
    "q1 Q0 SEBI/A/2023/1#preamble#0 1 0.90000000 baseline-retrieval\n"
    "q1 Q0 SEBI/B/2023/2#2. Some heading here#5 2 0.80000000 baseline-retrieval\n"
    "q1 Q0 SEBI/A/2023/1#3. Another heading#7 3 0.70000000 baseline-retrieval\n"
)


def _make_run(tmp_path: Path, text: str = LEGACY) -> Path:
    run_dir = tmp_path / "iv2-golden"
    run_dir.mkdir()
    (run_dir / "run.trec").write_text(text, encoding="utf-8")
    return run_dir


def test_emits_three_artifacts(tmp_path):
    run_dir = _make_run(tmp_path)
    result = convert_run_dir(run_dir)
    assert result["status"] == "converted"
    assert (run_dir / "run.chunk.trec").exists()
    assert (run_dir / "run.doc.trec").exists()
    assert (run_dir / "docids.tsv").exists()


def test_original_runfile_is_untouched(tmp_path):
    run_dir = _make_run(tmp_path)
    convert_run_dir(run_dir)
    assert (run_dir / "run.trec").read_text(encoding="utf-8") == LEGACY


def test_converted_chunk_run_is_valid_trec(tmp_path):
    run_dir = _make_run(tmp_path)
    convert_run_dir(run_dir)
    for line in (run_dir / "run.chunk.trec").read_text().splitlines():
        assert len(line.split()) == 6, line


def test_docids_recovers_the_space_bearing_chunk_id(tmp_path):
    run_dir = _make_run(tmp_path)
    convert_run_dir(run_dir)
    rows = dict(
        line.split("\t")
        for line in (run_dir / "docids.tsv").read_text().splitlines()
    )
    assert rows["SEBI/B/2023/2#5"] == "SEBI/B/2023/2#2. Some heading here#5"


def test_missing_runfile_is_skipped_not_failed(tmp_path):
    run_dir = tmp_path / "pool-sweep"
    run_dir.mkdir()
    (run_dir / "sweep.json").write_text("{}", encoding="utf-8")
    result = convert_run_dir(run_dir)
    assert result["status"] == "skipped"
    assert "no run.trec" in result["reason"]


def test_whitespace_in_run_tag_fails_without_writing(tmp_path):
    # A tag with a space breaks the fixed-tail assumption read_trec_run relies on.
    bad = "q1 Q0 SEBI/A/2023/1#preamble#0 1 0.90000000 bad tag\n"
    run_dir = _make_run(tmp_path, bad)
    result = convert_run_dir(run_dir)
    assert result["status"] == "failed"
    assert not (run_dir / "run.chunk.trec").exists()
