import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.mine_strata import (  # noqa: E402
    mine_lineage_pairs, mine_numeric, mine_repealed_basis, sample_paraphrase_chunks,
    sample_title_direct,
)
from sebi_rag.segment import CircularMeta, hierarchical_chunk  # noqa: E402


def _rec(cn, date="2024-01-10", dept="ISD", **over):
    r = {"circular_number": cn, "subject": f"About {cn}", "issue_date": date,
         "issuing_department": dept, "text": "body " * 200}
    r.update(over)
    return r


def test_title_direct_stratifies_across_years():
    recs = [_rec(f"C/{y}/{i}", date=f"{y}-03-01") for y in (2022, 2023, 2024) for i in range(5)]
    got = sample_title_direct(recs, 6, random.Random(20260723))
    assert len(got) == 6
    assert len({r["issue_date"][:4] for r in got}) == 3  # all years covered


def test_paraphrase_skips_preamble_and_short_chunks():
    chunks = hierarchical_chunk(
        "intro line\n\n1. Rule:\n" + ("The registered intermediary shall maintain records. " * 20),
        CircularMeta(circular_number="C/1", subject="Records"))
    got = sample_paraphrase_chunks(chunks, 5, random.Random(20260723))
    assert got and all("preamble" not in g["chunk_id"] for g in got)


def test_numeric_miner_requires_numeric_pattern():
    chunks = hierarchical_chunk(
        "1. Fees:\n" + ("The fee shall be twenty five per cent of turnover payable "
                        "within 30 days of the end of the quarter. " * 10),
        CircularMeta(circular_number="C/2", subject="Fees"))
    assert mine_numeric(chunks, 3, random.Random(20260723))


def test_lineage_pairs_need_both_dates_and_membership():
    recs = {"OLD/1": _rec("OLD/1", "2020-06-01"), "NEW/1": _rec("NEW/1", "2023-06-01")}
    pairs = mine_lineage_pairs({"OLD/1": ["NEW/1"], "GONE/9": ["NEW/1"]}, recs, 5,
                               random.Random(20260723))
    assert len(pairs) == 1
    p = pairs[0]
    assert p["old"] == "OLD/1" and "2020-06-01" < p["as_of_mid"] < "2023-06-01"
    assert p["as_of_before"] < "2020-06-01"


def test_repealed_basis_filters_on_status():
    recs = [_rec("C/3", regulatory_basis_status="repealed_basis", regulations=[]),
            _rec("C/4", regulatory_basis_status="current")]
    got = mine_repealed_basis(recs, 5, random.Random(20260723))
    assert [g["circular_number"] for g in got] == ["C/3"]
