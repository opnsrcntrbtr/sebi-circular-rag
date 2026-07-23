"""Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6).

Regulations are consolidated living documents ("[Last amended on ...]"), not
dated issuances: no circular_number, no issue_date, one current row each. They
therefore live in their own corpus file, keyed by a deterministic `reg_id` slug.

Resolution is three-stage: exact token match, then the hand-maintained
REGULATION_ALIASES table, then Jaccard fuzzy match above FUZZY_THRESHOLD.
Acronyms need the table because they share no tokens with their titles —
"PIT" vs "prohibition of insider trading" scores 0.0 and can never fuzzy-match.
Unmatched names are returned unresolved and surfaced by the coverage report;
extend the table rather than lowering the threshold.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

STATUSES = ("in_force", "repealed", "unknown")
BASIS_STATUSES = ("current", "repealed_basis", "mixed", "unknown")

# Jaccard over singularised, stopword-stripped tokens. 0.8 admits the observed
# spelling drift ("Mutual Fund" -> "Mutual Funds" = 1.0, "Depositories
# Participants" -> "Depositories and Participants" = 1.0) while rejecting
# genuine cross-regulation confusions ("Depositories" alone = 0.5, "Issue and
# Listing of Debt Securities" vs "...Non-Convertible Securities" = 0.6).
FUZZY_THRESHOLD = 0.8

_STOPWORDS = frozenset({"and", "of", "the", "to", "for", "in", "a", "an", "on"})


@dataclass(frozen=True)
class RegulationMeta:
    reg_id: str
    title: str
    short_name: str
    year: int
    status: str = "unknown"           # in_force | repealed | unknown
    last_amended: str | None = None   # ISO date
    source_url: str | None = None
    pdf_url: str | None = None
    pdf_sha256: str | None = None
    pdf_path: str | None = None
    aliases: tuple[str, ...] = ()
    supersedes_reg: tuple[str, ...] = ()
    superseded_by_reg: str | None = None
    provenance: str = ""
    text: str = ""                    # reserved; always "" in this phase


def _slug(s: str) -> str:
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s.lower())
    return s.strip("-")


def reg_id(short_name: str, year: int) -> str:
    """Deterministic, stable identity slug. This is the edge target and join key."""
    return f"{_slug(short_name)}-{year}"


def name_tokens(name: str) -> frozenset[str]:
    """Comparison tokens: lowercased, punctuation-split, stopwords dropped,
    naively singularised (trailing 's'). Never store this form."""
    raw = re.split(r"[^a-z0-9]+", name.replace("&", " and ").lower())
    out = set()
    for t in raw:
        if not t or t in _STOPWORDS:
            continue
        out.add(t[:-1] if len(t) > 3 and t.endswith("s") else t)
    return frozenset(out)


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# Acronym citation forms observed in the corpus, with occurrence counts, keyed
# on (normalised alias, year) — "MF" 1996 and "MF" 2026 are different
# regulations, as are "ICDR" 2009 and 2018. Extend from
# reports/unresolved_regulations.txt; do not lower FUZZY_THRESHOLD instead.
REGULATION_ALIASES: dict[tuple[str, int], str] = {
    ("pit", 2015): "prohibition-of-insider-trading-2015",              # 48
    ("mf", 1996): "mutual-funds-1996",                                 # 38
    ("lodr", 2015): "listing-obligations-and-disclosure-requirements-2015",  # 34
    ("dp", 2018): "depositories-and-participants-2018",                # 33
    ("dp", 1996): "depositories-and-participants-1996",
    ("aif", 2012): "alternative-investment-funds-2012",                # 22
    ("sbeb", 2021): "share-based-employee-benefits-and-sweat-equity-2021",  # 12
    ("fpi", 2019): "foreign-portfolio-investors-2019",                 # 10
    ("fpi", 2014): "foreign-portfolio-investors-2014",
    ("icdr", 2018): "issue-of-capital-and-disclosure-requirements-2018",  # 6
    ("icdr", 2009): "issue-of-capital-and-disclosure-requirements-2009",  # 3
    ("ipef", 2009): "investor-protection-and-education-fund-2009",     # 4
    ("mf", 2026): "mutual-funds-2026",                                 # 4
    ("sast", 2011): "substantial-acquisition-of-shares-and-takeovers-2011",  # 3
    ("cra", 1999): "credit-rating-agencies-1999",                      # 3
    ("pms", 2020): "portfolio-managers-2020",                          # 2
    ("fvci", 2000): "foreign-venture-capital-investors-2000",          # 1
    ("ilds", 2008): "issue-and-listing-of-debt-securities-2008",
    ("ncs", 2021): "issue-and-listing-of-non-convertible-securities-2021",
    ("ra", 2014): "research-analysts-2014",
    ("ia", 2013): "investment-advisers-2013",
}


def _alias_key(name: str) -> str:
    """Normalised alias lookup key: alphanumerics only, lowercased, trailing
    plural 's' dropped so 'MFs' and 'MF' collide."""
    k = re.sub(r"[^a-z0-9]+", "", name.lower())
    return k[:-1] if len(k) > 2 and k.endswith("s") else k


def resolve_regulation(
    name: str, year: int, regulations: list[dict]
) -> tuple[str | None, str]:
    """Resolve a cited regulation name+year to a canonical reg_id.

    Returns (reg_id, confidence). confidence is "explicit_text" for an exact
    token match or an alias-table hit, "inferred" for a fuzzy match, and
    (None, "") when nothing clears the threshold. Never guesses: an unresolved
    name is reported, not approximated.
    """
    same_year = [r for r in regulations if r.get("year") == year]
    target = name_tokens(name)

    for r in same_year:
        if name_tokens(r["short_name"]) == target:
            return r["reg_id"], "explicit_text"

    alias_target = REGULATION_ALIASES.get((_alias_key(name), year))
    if alias_target:
        return alias_target, "explicit_text"

    best_id, best_score = None, 0.0
    for r in same_year:
        score = _jaccard(target, name_tokens(r["short_name"]))
        if score > best_score:
            best_id, best_score = r["reg_id"], score
    if best_score >= FUZZY_THRESHOLD:
        return best_id, "inferred"
    return None, ""


def derive_regulatory_basis(statuses: list[str]) -> str:
    """Regulatory-basis status of one circular from its resolved regulations.

    `unknown`-status regulations are ignored rather than treated as repealed:
    absence from the Updated List is not proof of repeal (spec §5). A circular
    resolving only to unknown-status regulations is itself `unknown`.
    """
    known = [s for s in statuses if s in ("in_force", "repealed")]
    if not known:
        return "unknown"
    has_live = "in_force" in known
    has_dead = "repealed" in known
    if has_live and has_dead:
        return "mixed"
    return "current" if has_live else "repealed_basis"
