"""Standards-compliant TREC artifact emission (spec A §3-4)."""
import pytest

from sebi_rag.autoresearch.trecio import (
    MalformedChunkId,
    chunk_docid,
    circular_docid,
    write_docids,
    write_run_chunk,
    write_run_doc,
    write_trec_qrels,
)


def test_drops_heading_and_keeps_circular_and_ordinal():
    cid = "SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123#preamble#0"
    assert chunk_docid(cid) == "SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123#0"


def test_drops_heading_containing_spaces_and_hashes():
    cid = (
        "SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123"
        "#1. SEBI vide circular no. CIR/CFD/CMD/4/2015 dated September#1"
    )
    assert chunk_docid(cid) == "SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123#1"


def test_result_never_contains_whitespace():
    cid = "HO/43/15/12(3)2025-ISD-POD2/I/11734/2026#3. With the issuance of this#8"
    assert not any(ch.isspace() for ch in chunk_docid(cid))


def test_chunk_id_without_hash_is_returned_unchanged():
    assert chunk_docid("SEBI/HO/CFD/P/CIR/2023/123") == "SEBI/HO/CFD/P/CIR/2023/123"


def test_space_bearing_circular_id_is_percent_encoded():
    # 3 of 724 circulars are master circulars whose id carries a literal space.
    assert circular_docid("SEBI/IMD/MC No.3/10554/2012") == (
        "SEBI/IMD/MC%20No.3/10554/2012"
    )


def test_space_bearing_circular_survives_chunk_docid():
    cid = "SEBI/IMD/MC No.3/10554/2012#preamble#0"
    assert chunk_docid(cid) == "SEBI/IMD/MC%20No.3/10554/2012#0"


def test_encoding_is_applied_to_bare_circular_ids_too():
    # qrels carry bare circular ids; they must encode identically to runs,
    # or a run/qrels pair silently scores zero instead of failing.
    bare = circular_docid("SEBI/IMD/MC No.1/189241/2010")
    from_chunk = chunk_docid("SEBI/IMD/MC No.1/189241/2010#h#4").rsplit("#", 1)[0]
    assert bare == from_chunk


def test_percent_in_circular_id_raises_rather_than_encoding_ambiguously():
    with pytest.raises(MalformedChunkId, match="ambiguous"):
        circular_docid("SEBI/HO/100%/2023/1")


# -- run writers ---------------------------------------------------------

RANKINGS = {
    "q1": [
        ("SEBI/A/2023/1#preamble#0", 0.90),
        ("SEBI/B/2023/2#2. Some heading here#5", 0.80),
        ("SEBI/A/2023/1#3. Another heading#7", 0.70),
    ],
    "q2": [("SEBI/C/2023/3#intro#0", 0.60)],
}


def test_run_chunk_lines_have_exactly_six_fields(tmp_path):
    p = tmp_path / "run.chunk.trec"
    write_run_chunk(p, "unit-test", RANKINGS)
    lines = p.read_text().splitlines()
    assert len(lines) == 4
    for line in lines:
        assert len(line.split()) == 6, line


def test_run_chunk_preserves_rank_order_and_tag(tmp_path):
    p = tmp_path / "run.chunk.trec"
    write_run_chunk(p, "unit-test", RANKINGS)
    first = p.read_text().splitlines()[0].split()
    assert first[0] == "q1"
    assert first[1] == "Q0"
    assert first[2] == "SEBI/A/2023/1#0"
    assert first[3] == "1"
    assert first[5] == "unit-test"


def test_run_doc_dedupes_to_best_rank(tmp_path):
    p = tmp_path / "run.doc.trec"
    write_run_doc(p, "unit-test", RANKINGS)
    lines = [line.split() for line in p.read_text().splitlines()]
    q1 = [line for line in lines if line[0] == "q1"]
    # SEBI/A/2023/1 appears at chunk ranks 1 and 3; it must appear once, at rank 1.
    assert [line[2] for line in q1] == ["SEBI/A/2023/1", "SEBI/B/2023/2"]
    assert [line[3] for line in q1] == ["1", "2"]


def test_run_doc_lines_have_exactly_six_fields(tmp_path):
    p = tmp_path / "run.doc.trec"
    write_run_doc(p, "unit-test", RANKINGS)
    for line in p.read_text().splitlines():
        assert len(line.split()) == 6, line


def test_run_doc_encodes_space_bearing_circulars(tmp_path):
    p = tmp_path / "run.doc.trec"
    write_run_doc(p, "unit-test", {"q1": [("SEBI/IMD/MC No.3/10554/2012#h#0", 0.5)]})
    line = p.read_text().splitlines()[0].split()
    assert len(line) == 6
    assert line[2] == "SEBI/IMD/MC%20No.3/10554/2012"


def test_docids_maps_docid_back_to_full_chunk_id(tmp_path):
    p = tmp_path / "docids.tsv"
    write_docids(p, RANKINGS)
    rows = dict(line.split("\t") for line in p.read_text().splitlines())
    assert rows["SEBI/B/2023/2#5"] == "SEBI/B/2023/2#2. Some heading here#5"
    assert len(rows) == 4


# -- qrels ---------------------------------------------------------------

GOLDEN = [
    {"id": "q1", "abstain": False, "relevant_circulars": ["SEBI/A/2023/1", "SEBI/B/2023/2"]},
    {"id": "q2", "abstain": True, "relevant_circulars": []},
    {"id": "q3", "abstain": False, "relevant_circulars": ["SEBI/C/2023/3"]},
]


def test_qrels_lines_are_four_space_separated_fields(tmp_path):
    p = tmp_path / "e4.qrels"
    write_trec_qrels(p, GOLDEN)
    for line in p.read_text().splitlines():
        parts = line.split()
        assert len(parts) == 4, line
        assert parts[1] == "0"
        assert parts[3] == "1"


def test_qrels_has_no_header(tmp_path):
    p = tmp_path / "e4.qrels"
    write_trec_qrels(p, GOLDEN)
    assert p.read_text().splitlines()[0].split()[0] == "q1"


def test_qrels_expands_relevant_circulars(tmp_path):
    p = tmp_path / "e4.qrels"
    n = write_trec_qrels(p, GOLDEN)
    pairs = {(line.split()[0], line.split()[2]) for line in p.read_text().splitlines()}
    assert pairs == {
        ("q1", "SEBI/A/2023/1"),
        ("q1", "SEBI/B/2023/2"),
        ("q3", "SEBI/C/2023/3"),
    }
    assert n == 3


def test_qrels_excludes_abstain_rows(tmp_path):
    p = tmp_path / "e4.qrels"
    write_trec_qrels(p, GOLDEN)
    assert "q2" not in p.read_text()


def test_qrels_raises_when_nothing_would_be_written(tmp_path):
    with pytest.raises(ValueError, match="no qrels"):
        write_trec_qrels(tmp_path / "empty.qrels", [{"id": "q9", "abstain": True}])


def test_qrels_docids_match_run_doc_docids_exactly(tmp_path):
    """The encoding must agree across runs and qrels.

    If a run says `SEBI/IMD/MC%20No.3/...` and qrels say `SEBI/IMD/MC No.3/...`,
    the query scores zero silently instead of failing loudly.
    """
    circ = "SEBI/IMD/MC No.3/10554/2012"
    run_p, qrels_p = tmp_path / "run.doc.trec", tmp_path / "e4.qrels"
    write_run_doc(run_p, "t", {"q1": [(f"{circ}#h#0", 0.5)]})
    write_trec_qrels(qrels_p, [{"id": "q1", "abstain": False, "relevant_circulars": [circ]}])
    run_docid = run_p.read_text().split()[2]
    qrels_docid = qrels_p.read_text().split()[2]
    assert run_docid == qrels_docid == "SEBI/IMD/MC%20No.3/10554/2012"
