"""Extract regulation citations from circular text (spec 2026-07-23 §3.3).

Deliberately separate from `regulations.py`: this module turns text into raw
(name, year, clause, evidence) tuples and knows nothing about which regulations
exist. Resolution to canonical reg_ids is `regulations.resolve_regulation`.

Precision is carried by the `evidence` tier, not by the relation: a circular
issued under the powers of a regulation and one that merely name-drops it both
produce a `cites` edge, distinguished by subject_line / powers_clause /
body_text.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

EVIDENCE_TIERS = ("subject_line", "powers_clause", "body_text")

# "SEBI (Name) Regulations, 2015" / "Securities and Exchange Board of India
# (Name) Regulations 2018". The name group excludes ')' so it stops at the
# closing bracket; a parenthetical containing the word "Regulations" (the real
# "Procedure for making, amending and reviewing of Regulations" entry) survives
# because the inner word is not itself bracketed.
CITATION_RE = re.compile(
    r"(?:Securities\s+and\s+Exchange\s+Board\s+of\s+India|SEBI)\s*"
    r"\(([^)]{2,120})\)\s*Regulations?[,\s]+(\d{4})",
    re.I | re.S)

POWERS_RE = re.compile(r"in\s+exercise\s+of\s+the\s+powers\s+conferred", re.I)

# SEBI PDFs render appendix tables by interleaving columns, so a circular number
# and a row marker can land inside a regulation title that wraps across lines:
#   "SEBI (Listing Obligations and Disclosure\nSEBI/HO/CFD/CMD/C\n22. Requirements)
#    Regulations, 2015"
# Such a parenthetical is a table artefact, not a regulation name. Two signals
# reject it, both absent from every one of the 42 real short names:
#   - a "/" (circular numbers; no real short name contains one)
#   - the word "Regulations" anywhere but at the very end (the sole legitimate
#     case is "...reviewing of Regulations", which ends with it)
_SPLICE_SLASH = re.compile(r"/")
_INNER_REGULATIONS = re.compile(r"\bRegulations?\b(?!\s*$)", re.I)


def _is_table_artefact(name: str) -> bool:
    return bool(_SPLICE_SLASH.search(name) or _INNER_REGULATIONS.search(name))

# A clause reference: "regulation 30", "regulation 30A", "regulation 30(2)".
CLAUSE_RE = re.compile(r"\bregulations?\s+(\d+[A-Z]{0,2}(?:\(\d+\))?)", re.I)
_YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")

# Sentence boundary: a terminator followed by whitespace. SEBI PDFs hard-wrap,
# so a bare newline is not treated as a boundary.
_SENTENCE_SPLIT = re.compile(r"(?<=[.;])\s+")


@dataclass(frozen=True)
class Citation:
    name: str
    year: int
    clause: str | None
    evidence: str


def _sentences(text: str) -> list[tuple[int, int, str]]:
    """(start, end, sentence) spans over `text`, in order."""
    spans, pos = [], 0
    for part in _SENTENCE_SPLIT.split(text):
        start = text.find(part, pos)
        if start < 0:
            continue
        spans.append((start, start + len(part), part))
        pos = start + len(part)
    return spans


def _clause_in(sentence: str) -> str | None:
    """First clause reference in a sentence, ignoring 4-digit years.

    "Regulations 2018" (the comma-less citation form) would otherwise capture
    "2018" as a clause number.
    """
    for m in CLAUSE_RE.finditer(sentence):
        cand = m.group(1)
        if _YEAR_RE.match(cand):
            continue
        return cand
    return None


def _scan(body: str, evidence: str, force_clause_none: bool = False
          ) -> list[Citation]:
    out: list[Citation] = []
    spans = _sentences(body)
    for m in CITATION_RE.finditer(body):
        name = re.sub(r"\s+", " ", m.group(1)).strip()
        if _is_table_artefact(name):
            continue
        year = int(m.group(2))
        sentence = next((s for a, b, s in spans if a <= m.start() < b), body)
        tier = evidence
        if evidence == "body_text" and POWERS_RE.search(sentence):
            tier = "powers_clause"
        clause = None if force_clause_none else _clause_in(sentence)
        out.append(Citation(name=name, year=year, clause=clause, evidence=tier))
    return out


def extract_citations(subject: str, text: str) -> list[Citation]:
    """All regulation citations in a circular, one per occurrence (not deduped).

    Subject-line citations are emitted first and always carry the
    `subject_line` tier; the subject has no clause context, so their clause is
    always None.
    """
    return _scan(subject or "", "subject_line", force_clause_none=True) + \
        _scan(text or "", "body_text")
