"""Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6)."""
from sebi_rag.regulations import (FUZZY_THRESHOLD, REGULATION_ALIASES,
                                  RegulationMeta, derive_regulatory_basis,
                                  name_tokens, reg_id, resolve_regulation)

REGS = [
    {"reg_id": "mutual-funds-2026", "short_name": "Mutual Funds",
     "year": 2026, "status": "in_force"},
    {"reg_id": "mutual-funds-1996", "short_name": "Mutual Funds",
     "year": 1996, "status": "repealed"},
    {"reg_id": "listing-obligations-and-disclosure-requirements-2015",
     "short_name": "Listing Obligations and Disclosure Requirements",
     "year": 2015, "status": "in_force"},
    {"reg_id": "prohibition-of-insider-trading-2015",
     "short_name": "Prohibition of Insider Trading",
     "year": 2015, "status": "in_force"},
    {"reg_id": "depositories-and-participants-2018",
     "short_name": "Depositories and Participants",
     "year": 2018, "status": "in_force"},
    {"reg_id": "substantial-acquisition-of-shares-and-takeovers-2011",
     "short_name": "Substantial Acquisition of Shares and Takeovers",
     "year": 2011, "status": "in_force"},
    {"reg_id": "issue-and-listing-of-non-convertible-securities-2021",
     "short_name": "Issue and Listing of Non-Convertible Securities",
     "year": 2021, "status": "in_force"},
    {"reg_id": "depositories-2020", "short_name": "Depositories",
     "year": 2020, "status": "in_force"},
]


def test_reg_id_is_a_deterministic_slug():
    assert reg_id("Mutual Funds", 2026) == "mutual-funds-2026"
    assert reg_id("Issue of Capital and Disclosure Requirements", 2018) == (
        "issue-of-capital-and-disclosure-requirements-2018")


def test_reg_id_is_stable_across_punctuation_and_case_variants():
    a = reg_id("Depositories and Participants", 2018)
    b = reg_id("  DEPOSITORIES  &  PARTICIPANTS ", 2018)
    c = reg_id("Depositories, and Participants.", 2018)
    assert a == b == c == "depositories-and-participants-2018"


def test_name_tokens_singularises_and_drops_stopwords():
    assert name_tokens("Mutual Funds") == name_tokens("Mutual Fund")
    assert name_tokens("Depositories and Participants") == name_tokens(
        "Depositories Participants")
    assert "and" not in name_tokens("Depositories and Participants")


def test_exact_name_resolves_as_explicit_text():
    assert resolve_regulation("Mutual Funds", 2026, REGS) == (
        "mutual-funds-2026", "explicit_text")


def test_year_disambiguates_same_named_regulations():
    assert resolve_regulation("Mutual Funds", 1996, REGS)[0] == "mutual-funds-1996"
    assert resolve_regulation("Mutual Funds", 2026, REGS)[0] == "mutual-funds-2026"


def test_acronym_aliases_resolve_as_explicit_text():
    assert resolve_regulation("PIT", 2015, REGS) == (
        "prohibition-of-insider-trading-2015", "explicit_text")
    assert resolve_regulation("LODR", 2015, REGS)[0] == (
        "listing-obligations-and-disclosure-requirements-2015")
    assert resolve_regulation("D&P", 2018, REGS)[0] == (
        "depositories-and-participants-2018")
    assert resolve_regulation("MF", 1996, REGS)[0] == "mutual-funds-1996"
    assert resolve_regulation("MFs", 1996, REGS)[0] == "mutual-funds-1996"


def test_alias_year_matters():
    assert resolve_regulation("MF", 2026, REGS)[0] == "mutual-funds-2026"


def test_normalised_spelling_drift_resolves_as_explicit_text():
    """Singular/plural and dropped-stopword variants normalise to identical
    token sets, so they are exact matches — not threshold judgement calls —
    and carry the high-confidence tier."""
    assert resolve_regulation("Mutual Fund", 2026, REGS) == (
        "mutual-funds-2026", "explicit_text")
    assert resolve_regulation(
        "Substantial Acquisition of Shares and Takeover", 2011, REGS) == (
        "substantial-acquisition-of-shares-and-takeovers-2011", "explicit_text")
    assert resolve_regulation("Depositories Participants", 2018, REGS) == (
        "depositories-and-participants-2018", "explicit_text")


def test_genuine_partial_match_resolves_as_inferred():
    """A citation carrying a spurious extra token still resolves, but only via
    the Jaccard branch, so it is marked inferred rather than explicit_text.
    5 shared tokens over a union of 6 = 0.833, just above FUZZY_THRESHOLD."""
    assert resolve_regulation(
        "Issue and Listing of Non-Convertible Securities Market",
        2021, REGS) == (
        "issue-and-listing-of-non-convertible-securities-2021", "inferred")


def test_fuzzy_rejects_below_threshold_decoys():
    # "Depositories" alone must NOT collapse into "Depositories and
    # Participants": Jaccard 0.5 < 0.8. Both exist as separate regulations.
    assert resolve_regulation("Depositories", 2018, REGS) == (None, "")
    # Different regulations that share most tokens must stay distinct.
    assert resolve_regulation(
        "Issue and Listing of Debt Securities", 2021, REGS) == (None, "")


def test_unknown_name_is_unresolved_not_guessed():
    assert resolve_regulation("Completely Unrelated Thing", 1999, REGS) == (None, "")


def test_derive_regulatory_basis_truth_table():
    assert derive_regulatory_basis([]) == "unknown"
    assert derive_regulatory_basis(["in_force"]) == "current"
    assert derive_regulatory_basis(["in_force", "in_force"]) == "current"
    assert derive_regulatory_basis(["repealed"]) == "repealed_basis"
    assert derive_regulatory_basis(["repealed", "repealed"]) == "repealed_basis"
    assert derive_regulatory_basis(["in_force", "repealed"]) == "mixed"
    assert derive_regulatory_basis(["unknown"]) == "unknown"
    assert derive_regulatory_basis(["in_force", "unknown"]) == "current"
    assert derive_regulatory_basis(["repealed", "unknown"]) == "repealed_basis"


def test_alias_table_targets_are_well_formed_reg_ids():
    for (alias, year), target in REGULATION_ALIASES.items():
        assert isinstance(alias, str) and alias == alias.lower()
        assert isinstance(year, int)
        assert target.endswith(f"-{year}"), (alias, year, target)


def test_acronyms_ending_in_s_reach_their_own_entry():
    """PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped
    them to 'pm'/'nc'/'ild' and silently disabled all three entries."""
    from sebi_rag.regulations import _alias_keys
    assert REGULATION_ALIASES[("pms", 2020)] in _resolved("PMS", 2020)
    assert REGULATION_ALIASES[("ncs", 2021)] in _resolved("NCS", 2021)
    assert REGULATION_ALIASES[("ilds", 2008)] in _resolved("ILDS", 2008)
    # ...while a genuine plural still reaches the singular entry.
    assert "mf" in _alias_keys("MFs")


def _resolved(name, year):
    """reg_id resolved purely through the alias table, ignoring the corpus."""
    from sebi_rag.regulations import _alias_keys
    return [REGULATION_ALIASES[(k, year)] for k in _alias_keys(name)
            if (k, year) in REGULATION_ALIASES]


def test_every_alias_entry_is_reachable_from_some_spelling():
    """A table key that no _alias_keys() output can produce is dead config."""
    from sebi_rag.regulations import _alias_keys
    unreachable = [(a, y) for (a, y) in REGULATION_ALIASES
                   if a not in _alias_keys(a)]
    assert unreachable == []


def test_regulation_meta_defaults():
    m = RegulationMeta(reg_id="x-2020", title="T", short_name="X", year=2020)
    assert m.status == "unknown"
    assert m.last_amended is None
    assert m.aliases == ()
    assert m.superseded_by_reg is None
    assert m.text == ""


def test_threshold_is_documented_constant():
    assert FUZZY_THRESHOLD == 0.8
