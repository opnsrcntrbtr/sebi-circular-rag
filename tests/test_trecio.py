"""Standards-compliant TREC artifact emission (spec A §3-4)."""
import pytest

from sebi_rag.autoresearch.trecio import (
    MalformedChunkId,
    chunk_docid,
    circular_docid,
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
