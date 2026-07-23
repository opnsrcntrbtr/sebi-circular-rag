"""Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).

Three responsibilities, in dependency order:
  1. synthesise_repealed_stubs — cited regulations absent from the Updated List
     become stub records. Absence alone is NOT proof of repeal, so only names
     with a REG_SUCCESSION entry get status "repealed"; the rest are "unknown".
  2. build_regulation_edges  — one edge per (circular, regulation) pair.
  3. annotate_regulation_fields — three additive fields on the corpus RECORD.

Critical: the additive fields are never added to CircularMeta. hierarchical_chunk
does `meta=asdict(meta)`, so a new dataclass field would enter every chunk payload
and mutate the persisted index. This mirrors master_meta.annotate_master_fields,
which sets is_master/master_series on records only.
"""
from __future__ import annotations

from collections import defaultdict

from .reg_citations import EVIDENCE_TIERS, extract_citations
from .regulations import derive_regulatory_basis, reg_id, resolve_regulation

# Curated repeal chains: maintainer assertions, not text extractions. Populates
# supersedes_reg / superseded_by_reg on the regulation records; produces NO rows
# in regulation_edges.jsonl, which holds circular->regulation edges only.
# Extend from reports/unresolved_regulations.txt.
REG_SUCCESSION: dict[str, str] = {
    "mutual-funds-1996": "mutual-funds-2026",
    "stock-brokers-1992": "stock-brokers-2026",
    "depositories-and-participants-1996": "depositories-and-participants-2018",
    "registrars-to-an-issue-and-share-transfer-agents-1993":
        "registrars-to-an-issue-and-share-transfer-agents-2025",
    "issue-and-listing-of-debt-securities-2008":
        "issue-and-listing-of-non-convertible-securities-2021",
    "issue-of-capital-and-disclosure-requirements-2009":
        "issue-of-capital-and-disclosure-requirements-2018",
    "foreign-portfolio-investors-2014": "foreign-portfolio-investors-2019",
    # Added from the unknown-stub report after the first full run. Each is a
    # documented repeal-and-replace, not an inference from absence.
    "venture-capital-funds-1996": "alternative-investment-funds-2012",
    "portfolio-managers-1993": "portfolio-managers-2020",
    "share-based-employee-benefits-2014":
        "share-based-employee-benefits-and-sweat-equity-2021",
    "substantial-acquisition-of-shares-and-takeovers-1997":
        "substantial-acquisition-of-shares-and-takeovers-2011",
    "issue-and-listing-of-non-convertible-redeemable-preference-shares-2013":
        "issue-and-listing-of-non-convertible-securities-2021",
    "stock-brokers-and-sub-brokers-1992": "stock-brokers-2026",
    "procedure-for-holding-enquiry-by-enquiry-officer-and-imposing-penalty-2002":
        "intermediaries-2008",
}

_TIER_RANK = {t: i for i, t in enumerate(EVIDENCE_TIERS)}


def _cited(circulars: list[dict]):
    """Yield (circular, Citation) for every citation occurrence in the corpus."""
    for c in circulars or []:
        for cit in extract_citations(c.get("subject", ""), c.get("text", "")):
            yield c, cit


def synthesise_repealed_stubs(circulars: list[dict],
                              regulations: list[dict]) -> list[dict]:
    """Stub records for cited regulations absent from the Updated List.

    Returns NEW records only; the caller appends them to `regulations`. Also
    sets the `supersedes_reg` backlink on the successor record in place.
    """
    known = {r["reg_id"] for r in regulations}
    by_id = {r["reg_id"]: r for r in regulations}
    stubs: dict[str, dict] = {}

    for _, cit in _cited(circulars):
        target, _conf = resolve_regulation(cit.name, cit.year, regulations)
        if target and target in known:
            continue
        # Unresolvable against the in-force set: mint a stub keyed on the
        # citation's own wording, so repeated spellings collapse to one record.
        candidate = target or reg_id(cit.name, cit.year)
        if candidate in known or candidate in stubs:
            continue
        successor = REG_SUCCESSION.get(candidate)
        stubs[candidate] = {
            "reg_id": candidate,
            "title": f"SEBI ({cit.name}) Regulations, {cit.year}",
            "short_name": cit.name,
            "year": cit.year,
            "status": "repealed" if successor else "unknown",
            "last_amended": None,
            "source_url": None,
            "pdf_url": None,
            "pdf_sha256": None,
            "pdf_path": None,
            "aliases": [],
            "supersedes_reg": [],
            "superseded_by_reg": successor,
            "provenance": ("Inferred from corpus citations; "
                           "not on SEBI Updated List"),
            "text": "",
        }
        if successor and successor in by_id:
            back = list(by_id[successor].get("supersedes_reg") or [])
            if candidate not in back:
                back.append(candidate)
                by_id[successor]["supersedes_reg"] = back
    return list(stubs.values())


def build_regulation_edges(
    circulars: list[dict], regulations: list[dict]
) -> tuple[list[dict], dict[tuple[str, int], int]]:
    """One `cites` edge per (circular, regulation) pair.

    The merged edge carries the highest-precedence evidence tier observed, the
    clause from that same winning occurrence, and the total occurrence count.
    Unresolved (name, year) pairs are returned with counts, never dropped.
    """
    merged: dict[tuple[str, str], dict] = {}
    unresolved: dict[tuple[str, int], int] = defaultdict(int)

    for c in circulars or []:
        source = c["circular_number"]
        for cit in extract_citations(c.get("subject", ""), c.get("text", "")):
            target, confidence = resolve_regulation(
                cit.name, cit.year, regulations)
            if not target:
                unresolved[(cit.name, cit.year)] += 1
                continue
            key = (source, target)
            edge = merged.get(key)
            if edge is None:
                merged[key] = {
                    "source": source, "target": target, "relation": "cites",
                    "confidence": confidence, "evidence": cit.evidence,
                    "clause": cit.clause, "count": 1,
                }
                continue
            edge["count"] += 1
            if _TIER_RANK[cit.evidence] < _TIER_RANK[edge["evidence"]]:
                edge["evidence"] = cit.evidence
                edge["clause"] = cit.clause
                edge["confidence"] = confidence
    return list(merged.values()), dict(unresolved)


def annotate_regulation_fields(circulars: list[dict], edges: list[dict],
                               regulations: list[dict]) -> int:
    """Set regulations / primary_regulation / regulatory_basis_status in place.

    Returns the number of records whose three fields changed (idempotent: a
    second call on the same inputs returns 0). Never touches validity_status or
    supersession_status — the 2026-07-12 locked rule stands.
    """
    status_by_id = {r["reg_id"]: r.get("status", "unknown") for r in regulations}
    by_source: dict[str, list[dict]] = defaultdict(list)
    for e in edges:
        by_source[e["source"]].append(e)

    changed = 0
    for c in circulars or []:
        before = (c.get("regulations"), c.get("primary_regulation"),
                  c.get("regulatory_basis_status"))
        mine = by_source.get(c["circular_number"], [])
        ordered = sorted(mine, key=lambda e: (-e["count"], e["target"]))
        reg_ids = [e["target"] for e in ordered]
        primary = min(
            mine,
            key=lambda e: (_TIER_RANK[e["evidence"]], -e["count"], e["target"]),
            default=None)
        c["regulations"] = reg_ids
        c["primary_regulation"] = primary["target"] if primary else None
        c["regulatory_basis_status"] = derive_regulatory_basis(
            [status_by_id.get(i, "unknown") for i in reg_ids])
        after = (c["regulations"], c["primary_regulation"],
                 c["regulatory_basis_status"])
        changed += after != before
    return changed


def build_regulatory_index(circulars: list[dict],
                           regulations: list[dict]) -> dict[str, dict]:
    """Per-circular regulatory-basis lookup for the query/citation layer.

    Read-only join of already-annotated corpus fields with regulations.jsonl.
    Every circular gets an entry. Never recomputes regulatory_basis_status and
    never touches validity_status/supersession_status.
    """
    by_id = {r["reg_id"]: r for r in regulations}

    def _ref(reg_id: str) -> dict:
        rec = by_id.get(reg_id)
        if rec is None:  # dangling reg_id: present on circular, absent from listing
            return {"reg_id": reg_id, "short_name": reg_id, "year": None,
                    "status": "unknown", "superseded_by": None}
        status = rec.get("status", "unknown")
        superseded_by = None
        if status == "repealed":
            succ = by_id.get(rec.get("superseded_by_reg"))
            if succ is not None:
                superseded_by = {"reg_id": succ["reg_id"],
                                 "short_name": succ.get("short_name", succ["reg_id"]),
                                 "year": succ.get("year")}
        return {"reg_id": reg_id, "short_name": rec.get("short_name", reg_id),
                "year": rec.get("year"), "status": status,
                "superseded_by": superseded_by}

    index: dict[str, dict] = {}
    for c in circulars or []:
        reg_ids = c.get("regulations") or []
        index[c["circular_number"]] = {
            "regulatory_basis_status": c.get("regulatory_basis_status") or "unknown",
            "primary_regulation": c.get("primary_regulation"),
            "regulations": [_ref(rid) for rid in reg_ids],
        }
    return index
