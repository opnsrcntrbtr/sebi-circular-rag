"""Query-side lexical expansion (intervention #2, glossary variant).

Lay->statutory synonym injection for the BM25 leg only. Grounded in the
sparse_vocabulary_miss bucket of eval/runs/ft-traces/buckets.md.
"""
from __future__ import annotations

from sebi_rag.expand import GLOSSARY, expand_query


def test_lay_term_gains_statutory_synonym():
    out = expand_query("Can an investor block all outgoing transactions?")
    # original query preserved as prefix; statutory synonym appended
    assert out.startswith("Can an investor block all outgoing transactions?")
    assert "freeze" in out


def test_query_without_glossary_terms_is_unchanged():
    q = "What is the settlement cycle for equity trades?"
    assert expand_query(q) == q


def test_synonym_already_present_is_not_duplicated():
    out = expand_query("freeze or block the folio")
    assert out.lower().split().count("freeze") == 1


def test_multiword_synonym_splits_into_tokens():
    glossary = {"template": ("model agreement",)}
    out = expand_query("is there a template", glossary=glossary)
    assert out == "is there a template model agreement"


def test_all_five_sparse_failure_queries_expand():
    # the 5 sparse_vocabulary_miss failures from buckets.md must each gain
    # at least one statutory term
    queries = [
        "Can an investor voluntarily block all outgoing transactions from their folio?",   # para-freeze
        "Is there a template contract between a registrar to an issue and the company?",    # probe-tbl-05
        "Which circular replaced the earlier ICDR-related circulars and made them void?",   # probe-sup-01
        "How recent do the papers accompanying a broking licence application need to be?",  # probe-par-01
        "What fraction of the shares held by public investors must be kept in electronic form?",  # probe-par-02
    ]
    for q in queries:
        assert expand_query(q) != q, f"no expansion for: {q}"
