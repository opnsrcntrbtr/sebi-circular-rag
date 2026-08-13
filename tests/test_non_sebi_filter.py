"""The non-SEBI domain filter must match words, not substrings.

Shipped 2026-07-30 with no test coverage. `_is_non_sebi_domain` matched
keywords as bare substrings, so "rbi" matched inside "a-rbi-tration" and
"a-rbi-trage" - both core SEBI securities vocabulary. Any such query without
the literal word "sebi" was flagged non-SEBI and the pipeline ABSTAINED.

Caught 2026-08-13 via golden row v7-ls-015 (online dispute resolution), which
abstained with reason `non_sebi_domain` despite the governing circular being
retrieved at rank 8. 86 corpus circulars mention arbitration/arbitrage.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sebi_rag.generate import _NON_SEBI_KEYWORDS, _is_non_sebi_domain  # noqa: E402


# --- the regression: securities vocabulary containing a keyword substring ---

def test_arbitration_is_not_a_non_sebi_domain():
    assert not _is_non_sebi_domain(
        "What is the arbitration mechanism for investor disputes?")


def test_arbitrage_is_not_a_non_sebi_domain():
    assert not _is_non_sebi_domain(
        "Explain the arbitrage restrictions for mutual fund schemes")


def test_golden_v7_ls_015_query_is_not_flagged():
    """The exact query that exposed the bug."""
    assert not _is_non_sebi_domain(
        "Under the current master circular on online resolution of disputes in "
        "the Indian securities market, what common portal harnesses online "
        "conciliation and online arbitration for resolution of investor disputes?")


# --- the filter must still do its job -------------------------------------

def test_genuine_rbi_query_is_still_flagged():
    assert _is_non_sebi_domain("What did RBI say about overseas direct investment?")


def test_genuine_gst_query_is_still_flagged():
    assert _is_non_sebi_domain("What are the e-invoicing rules from the GST council?")


def test_genuine_pfrda_query_is_still_flagged():
    assert _is_non_sebi_domain("How does PFRDA regulate the national pension system?")


def test_multiword_keyword_still_matches():
    assert _is_non_sebi_domain(
        "Rules under the foreign exchange management act for inbound investment")


def test_sebi_mention_short_circuits():
    """Guard against false positives on cross-domain SEBI questions."""
    assert not _is_non_sebi_domain(
        "SEBI's online resolution mechanism under the RBI framework")


def test_every_short_keyword_is_word_bounded():
    """Any single-token keyword <= 5 chars is a substring hazard. Embedding it
    inside a longer word must not trigger the filter."""
    short = [k for k in _NON_SEBI_KEYWORDS if len(k) <= 5 and " " not in k]
    assert short, "expected some short keywords to guard"
    for kw in short:
        probe = f"discussion of x{kw}y provisions for listed entities"
        assert not _is_non_sebi_domain(probe), (
            f"{kw!r} matched inside a longer word")
