"""Master-circular identity metadata (spec 2026-07-13 §3).

Additive fields only (locked metadata rules): is_master, master_series,
master_edition, previous_edition. Series come from a maintained rule table;
unmatched subjects get None (surfaced by the coverage report, extend the
table as new series appear).
"""
from __future__ import annotations

import re
from collections import defaultdict

MASTER_SERIES_RULES: tuple[tuple[str, re.Pattern], ...] = tuple(
    (name, re.compile(pat, re.I)) for name, pat in (
        ("Mutual Funds", r"mutual\s+fund"),
        ("AIFs", r"alternative\s+investment\s+fund|\bAIFs?\b"),
        ("Depositories", r"depositor"),
        ("Stock Exchanges & Clearing Corporations",
         r"stock\s+exchange|clearing\s+corporation"),
        ("Stock Brokers", r"stock\s+broker"),
        ("Debenture Trustees", r"debenture\s+trustee"),
        ("REITs", r"real\s+estate\s+investment\s+trust|\bREITs?\b"),
        ("InvITs", r"infrastructure\s+investment\s+trust|\bInvITs?\b"),
        ("Portfolio Managers", r"portfolio\s+manager"),
        ("Credit Rating Agencies", r"credit\s+rating\s+agenc"),
        ("Research Analysts", r"research\s+analyst"),
        ("Investment Advisers", r"investment\s+advis"),
        ("Merchant Bankers", r"merchant\s+banker"),
        ("Custodians", r"\bcustodian"),
        ("KYC & AML", r"know\s+your\s+client|\bKYC\b|anti[- ]money\s+laundering"),
        ("Surveillance", r"\bsurveillance\b"),
        ("Online Dispute Resolution", r"online\s+dispute\s+resolution|\bODR\b"),
        ("Foreign Portfolio Investors", r"foreign\s+portfolio\s+investor|\bFPIs?\b"),
        ("Commodity Derivatives", r"commodity\s+derivative"),
        ("ESG Rating Providers", r"ESG\s+rating"),
        ("Stock Exchanges and Depositories",
         r"stock\s+exchanges?\s+and\s+depositories"),
    ))
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def master_series(subject: str | None) -> str | None:
    s = subject or ""
    for name, pat in MASTER_SERIES_RULES:
        if pat.search(s):
            return name
    return None


def annotate_master_fields(records: list[dict]) -> int:
    """Set is_master/master_series/master_edition/previous_edition in place.

    Returns the number of records whose four identity fields changed
    (idempotent: a second call on the same records returns 0).
    """
    before = [(r.get("is_master"), r.get("master_series"),
               r.get("master_edition"), r.get("previous_edition"))
              for r in records]
    by_series: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        is_master = r.get("circular_type") == "MASTER_CIRCULAR"
        series = master_series(r.get("subject")) if is_master else None
        date = r.get("issue_date") or ""
        r["is_master"] = is_master
        r["master_series"] = series
        r["master_edition"] = int(date[:4]) if is_master and _ISO.match(date) else None
        r["previous_edition"] = None
        if is_master and series and _ISO.match(date):
            by_series[series].append(r)
    for series_recs in by_series.values():
        series_recs.sort(key=lambda r: r["issue_date"])
        for prev, cur in zip(series_recs, series_recs[1:]):
            cur["previous_edition"] = prev["circular_number"]
    return sum(1 for r, b in zip(records, before)
               if (r["is_master"], r["master_series"],
                   r["master_edition"], r["previous_edition"]) != b)
