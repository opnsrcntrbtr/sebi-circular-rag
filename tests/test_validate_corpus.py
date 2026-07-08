import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_corpus import validate  # noqa: E402


def _rec(**kw) -> dict:
    base = {"circular_number": "SEBI/HO/X/CIR/P/2024/1", "issue_date": "2024-01-05",
            "version_lineage": [], "text": "body"}
    return {**base, **kw}


def test_clean_corpus_has_no_violations():
    assert validate([_rec()]) == []


def test_flags_empty_and_malformed_numbers():
    v = validate([_rec(circular_number=""),
                  _rec(circular_number="BROKEN NUMBER 12")])
    assert len(v) == 2


def test_flags_normalized_duplicates():
    v = validate([_rec(), _rec(circular_number="HO/X/CIR/P/2024/1")])
    assert any("duplicate" in x for x in v)


def test_flags_self_reference_in_lineage():
    v = validate([_rec(version_lineage=["SEBI/HO/X/CIR/P/2024/1"])])
    assert any("self-reference" in x for x in v)


def test_flags_bad_issue_date():
    v = validate([_rec(issue_date="05-01-2024")])
    assert any("issue_date" in x for x in v)
