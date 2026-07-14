"""Master-circular identity metadata (spec 2026-07-13 §3).

Additive fields only (locked metadata rules): is_master, master_series,
master_edition, previous_edition. Series come from a maintained rule table;
unmatched subjects get None (surfaced by the coverage report, extend the
table as new series appear).
"""
from __future__ import annotations

import re
from collections import defaultdict

from sebi_rag.ingest_pdf import REF_RE, normalize_circular_number

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


# Rescission-related headings across eras: modern appendices name "rescinded"
# or "superseded" explicitly; pre-2015 master circulars instead title their
# consolidation schedule "List of Circulars & Communications" with the
# rescission stated as prose ("...shall stand rescinded") elsewhere in the
# document — each alternative below requires an explicit rescission signal,
# never a bare "list of circulars" (too broad; matches unrelated body text).
RESCISSION_HEADING = re.compile(
    r"(?:list\s+of\s+rescinded\s+circulars"
    r"|list\s+of\s+circulars?\s+(?:rescinded|superseded)"
    r"|list\s+of\s+circulars\s*(?:&|and)\s*communications"
    r"|circulars?\s+(?:rescinded|superseded)\s+(?:by|vide)\s+(?:this\s+master|"
    r"the\s+instant\s+circular)"
    r"|stand[s]?\s+rescinded"
    r"|hereby\s+rescinded)", re.I)


def consolidation_edges(rec: dict) -> list[dict]:
    """Edges for circulars listed in a master circular's rescission appendix.

    Scans the text from the first rescission-related heading onward; every
    well-formed circular reference (REF_RE) after it is a consolidation
    target. explicit_text confidence: the appendix names the number itself.
    """
    text = rec.get("text") or ""
    m = RESCISSION_HEADING.search(text)
    if not m:
        return []
    source = rec["circular_number"]
    source_key = normalize_circular_number(source)
    # Appendix tables sometimes render "SEBI" as "SE BI" (PDF kerning artifact
    # in tabular layouts), which breaks REF_RE's SEBI/HO/... match; heal only
    # within the scanned tail, not the whole document.
    tail = re.sub(r"\bSE\s+BI/", "SEBI/", text[m.start():])
    seen, edges = set(), []
    for ref in REF_RE.finditer(tail):
        n = ref.group(0)
        key = normalize_circular_number(n)
        if key == source_key or key in seen:
            continue
        seen.add(key)
        edges.append({"source": source, "target": n,
                      "relation": "consolidates",
                      "confidence": "explicit_text",
                      "evidence": "rescission_appendix"})
    return edges
