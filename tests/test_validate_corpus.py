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


def test_allows_legacy_mc_no_format():
    """2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the
    document's own authentic wording includes a space in "MC No.", which is
    not a parsing defect. Stored numbers keep the document's own spelling
    (never rewritten to satisfy this validator), so the check must special-
    case this known legacy pattern rather than reject all whitespace."""
    v = validate([_rec(circular_number="SEBI/IMD/MC No.2/836/2011")])
    assert v == []


def test_still_flags_other_whitespace_as_implausible():
    v = validate([_rec(circular_number="SEBI/HO/X CIR/P/2024/1")])
    assert any("implausible" in x for x in v)
