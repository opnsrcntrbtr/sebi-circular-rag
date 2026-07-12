"""Metadata layer: circular_type taxonomy + validity_status derivation.

Locked decisions (2026-07-12 migration planning):
- circular_type: CIRCULAR | MASTER_CIRCULAR | CLARIFICATION | AMENDMENT |
  ADDENDUM | CORRIGENDUM — derived from the subject line, first match wins.
- validity_status: current | superseded | partially_superseded | unknown —
  computed from explicit_text supersession edges only; inferred edges
  (master-topic re-issues) never flip status.
Additive to the existing supersession_status field, never a replacement.
"""
from __future__ import annotations

import re

CIRCULAR_TYPES = ("CIRCULAR", "MASTER_CIRCULAR", "CLARIFICATION",
                  "AMENDMENT", "ADDENDUM", "CORRIGENDUM")
VALIDITY_STATUSES = ("current", "superseded", "partially_superseded", "unknown")

# Order = precedence (matches the corpus probe that locked the taxonomy):
# a "Master Circular on Amendment procedures" is a MASTER_CIRCULAR.
_TYPE_PATTERNS = (
    ("MASTER_CIRCULAR", re.compile(r"\bmaster\s+circular\b", re.I)),
    ("CORRIGENDUM", re.compile(r"\bcorrigend", re.I)),
    ("ADDENDUM", re.compile(r"\baddend", re.I)),
    ("CLARIFICATION", re.compile(r"\bclarificat", re.I)),
    ("AMENDMENT", re.compile(r"\bamendment\b", re.I)),
)

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def classify_circular_type(subject: str | None) -> str:
    s = subject or ""
    for name, pat in _TYPE_PATTERNS:
        if pat.search(s):
            return name
    return "CIRCULAR"


def derive_validity(circular_number: str, issue_date: str | None,
                    edges: list[dict]) -> str:
    """Validity of one circular from the tiered edge list (any scope: the
    function filters to explicit_text edges targeting circular_number)."""
    incoming = [e for e in edges
                if e.get("target") == circular_number
                and e.get("confidence") == "explicit_text"]
    if any(e.get("relation") == "supersedes" for e in incoming):
        return "superseded"
    if any(e.get("relation") == "amends" for e in incoming):
        return "partially_superseded"
    if not issue_date or not _ISO_DATE_RE.match(issue_date):
        return "unknown"
    return "current"
