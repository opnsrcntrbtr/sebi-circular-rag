import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_corpus import validate  # noqa: E402


def _rec(**kw) -> dict:
    base = {"circular_number": "SEBI/HO/X/CIR/P/2024/1", "issue_date": "2024-01-05",
            "version_lineage": []}
    rec = {**base, **kw}
    # Distinct per-record text unless a test sets it explicitly: two records
    # sharing one body is itself a violation (see the duplicate-text tests).
    rec.setdefault("text", f"body of {rec['circular_number']}")
    return rec


def test_clean_corpus_has_no_violations():
    assert validate([_rec()]) == []


def test_flags_empty_and_malformed_numbers():
    v = validate([_rec(circular_number=""),
                  _rec(circular_number="BROKEN NUMBER 12")])
    assert len(v) == 2


def test_flags_normalized_duplicates():
    v = validate([_rec(), _rec(circular_number="HO/X/CIR/P/2024/1")])
    assert any("duplicate of" in x for x in v)


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


# --- 2026-07-25 remediation Task 1: text-integrity invariants -------------
# Guards the two bug classes that shipped undetected: records sharing one
# body text, and records whose stored circular_number cannot be derived
# from their own text.

_TEXT_A = (
    "CIRCULAR\nAFD/P/CIR/2022/125\nSeptember 26, 2022\nTo,\n"
    "All Foreign Portfolio Investors\nDear Sir / Madam,\n"
    "Subject: Modification in the Operational Guidelines\n\n"
    "1. This is the body of circular one.\n"
)
_TEXT_B = (
    "CIRCULAR\nDOF3/P/CIR/2022/82\nJune 15, 2022\nTo,\nAll Mutual Funds\n"
    "Dear Sir / Madam,\nSubject: Nomination for Mutual Fund Unit Holders\n\n"
    "1. This is the body of circular two.\n"
)


def test_real_corpus_shaped_records_pass():
    recs = [_rec(circular_number="AFD/P/CIR/2022/125", text=_TEXT_A),
            _rec(circular_number="DOF3/P/CIR/2022/82", text=_TEXT_B)]
    assert validate(recs) == []


def test_duplicate_text_across_records_flagged():
    recs = [_rec(circular_number="AFD/P/CIR/2022/125", text=_TEXT_A),
            _rec(circular_number="DOF3/P/CIR/2022/82", text=_TEXT_A)]
    assert any("duplicate text" in v for v in validate(recs))


def test_number_not_derivable_from_own_text_flagged():
    # stored number belongs to a circular this text merely cites
    recs = [_rec(circular_number="SEBI/HO/MRD2/DCAP/CIR/P/2019/146", text=_TEXT_A)]
    assert any("not derivable" in v for v in validate(recs))


def test_empty_text_is_not_a_duplicate_cluster():
    recs = [_rec(circular_number="AFD/P/CIR/2022/125", text=""),
            _rec(circular_number="DOF3/P/CIR/2022/82", text="")]
    assert not any("duplicate text" in v for v in validate(recs))
