"""P2 — cross-document supersession resolution.

Classifies each circular's references as supersedes / amends / references, builds
a lineage graph across the corpus, and derives an in_force | superseded | amended
status per circular. Detection is grounded in the circular text: a reference is
treated as superseded when it appears after a supersession trigger (e.g. "this
circular supersedes ... listed below: a. <ref> b. <ref> ...").

Authoritative-text rule (handbook): we only assert a supersession that the text
states; ambiguous citations stay 'references'.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .ingest_pdf import REF_RE

SUPERSEDE_RE = re.compile(
    r"(in supersession of|supersed\w*|rescind\w*|repeal\w*|"
    r"stands? withdrawn|shall stand (?:rescinded|withdrawn|repealed))",
    re.I,
)
AMEND_RE = re.compile(r"(in (?:partial )?modification of|partial modification|amend\w*)", re.I)


def _window(text: str, pos: int, radius: int = 90) -> str:
    return text[max(0, pos - radius): pos + radius].replace("\n", " ").strip()


def detect_relations_ex(circular_number: str, text: str) -> list[dict]:
    """Like detect_relations, but returns dict records with evidence spans."""
    positions: dict[str, list[int]] = {}
    for m in REF_RE.finditer(text):
        positions.setdefault(m.group(0), []).append(m.start())
    first_sup = min((m.start() for m in SUPERSEDE_RE.finditer(text)), default=None)
    amd_pos = [m.start() for m in AMEND_RE.finditer(text)]

    out: list[dict] = []
    for ref, pos_list in positions.items():
        if ref == circular_number:
            continue
        if first_sup is not None and any(p > first_sup for p in pos_list):
            pos = next(p for p in pos_list if p > first_sup)
            out.append({"relation": "supersedes", "target": ref,
                        "evidence": _window(text, pos),
                        "extractor": "regex:SUPERSEDE_RE"})
        elif amd_pos and any(abs(p - a) < 120 for p in pos_list for a in amd_pos):
            pos = next(p for p in pos_list if any(abs(p - a) < 120 for a in amd_pos))
            out.append({"relation": "amends", "target": ref,
                        "evidence": _window(text, pos),
                        "extractor": "regex:AMEND_RE"})
        else:
            out.append({"relation": "references", "target": ref,
                        "evidence": _window(text, pos_list[0]), "extractor": "ref_only"})
    return out


def detect_relations(circular_number: str, text: str) -> list[tuple[str, str]]:
    """Return (relation, referenced_circular) for each distinct reference."""
    return [(e["relation"], e["target"])
            for e in detect_relations_ex(circular_number, text)]


@dataclass
class Lineage:
    supersedes: dict[str, list[str]] = field(default_factory=dict)   # newer -> [older]
    amends: dict[str, list[str]] = field(default_factory=dict)
    superseded_by: dict[str, list[str]] = field(default_factory=dict)  # older -> [newer]
    amended_by: dict[str, list[str]] = field(default_factory=dict)
    edges: list[dict] = field(default_factory=list)

    def status(self, circular_number: str) -> str:
        if circular_number in self.superseded_by:
            return "superseded"
        if circular_number in self.amended_by:
            return "amended"
        return "in_force"

    def explicit_superseded_by(self, circular_number: str) -> list[str]:
        return [e["source"] for e in self.edges
                if e["target"] == circular_number
                and e["relation"] == "supersedes"
                and e["confidence"] == "explicit_text"]

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps({
            "supersedes": self.supersedes, "amends": self.amends,
            "superseded_by": self.superseded_by, "amended_by": self.amended_by,
            "edges": self.edges,
        }, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "Lineage":
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            supersedes=d.get("supersedes", {}), amends=d.get("amends", {}),
            superseded_by=d.get("superseded_by", {}), amended_by=d.get("amended_by", {}),
            edges=d.get("edges", []),
        )


def mc_topic(subject: str | None) -> str | None:
    """Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None.

    Used to detect re-issues: two master circulars with the same topic are
    consecutive versions, so the newer supersedes the older.
    """
    s = (subject or "").lower()
    m = re.match(r"\s*master circular\s+(?:for|on)\s+(.+)", s)
    if not m:
        return None
    t = re.split(r"\bi\b", m.group(1))[0]          # cut at section "I."
    t = t.replace("sebi", " ")
    t = re.sub(r"[^a-z ]", " ", t)
    stop = {"the", "for", "and", "with", "of", "by", "to", "an", "a"}
    words = [w for w in t.split() if len(w) > 1 and w not in stop]
    return " ".join(words[:4]) or None


def _currency(r: dict) -> str:
    return max(r.get("issue_date", "") or "", r.get("effective_date", "") or "")


def build_lineage(records: list[dict]) -> Lineage:
    lin = Lineage()

    def add_supersede(newer: str, older: str, confidence: str = "explicit_text",
                      extractor: str = "regex:SUPERSEDE_RE", evidence: str = "") -> None:
        if newer == older:
            return
        if older not in lin.supersedes.setdefault(newer, []):
            lin.supersedes[newer].append(older)
        if newer not in lin.superseded_by.setdefault(older, []):
            lin.superseded_by[older].append(newer)
        existing = next((e for e in lin.edges if e["source"] == newer
                         and e["target"] == older and e["relation"] == "supersedes"), None)
        if existing is None:
            lin.edges.append({"source": newer, "target": older,
                              "relation": "supersedes", "confidence": confidence,
                              "extractor": extractor, "evidence": evidence})
        elif existing["confidence"] == "inferred" and confidence == "explicit_text":
            existing.update(confidence=confidence, extractor=extractor, evidence=evidence)

    # 1) explicit supersession/amendment clauses in the text
    for r in records:
        cn = r["circular_number"]
        for e in detect_relations_ex(cn, r.get("text", "")):
            if e["relation"] == "supersedes":
                add_supersede(cn, e["target"], evidence=e["evidence"])
            elif e["relation"] == "amends":
                lin.amends.setdefault(cn, []).append(e["target"])
                lin.amended_by.setdefault(e["target"], []).append(cn)
                lin.edges.append({"source": cn, "target": e["target"],
                                  "relation": "amends", "confidence": "explicit_text",
                                  "extractor": e["extractor"], "evidence": e["evidence"]})

    # 2) master-circular re-issues: within a topic, newest supersedes the rest
    groups: dict[str, list[dict]] = {}
    for r in records:
        t = mc_topic(r.get("subject"))
        if t:
            groups.setdefault(t, []).append(r)
    for rs in groups.values():
        if len(rs) < 2:
            continue
        rs.sort(key=_currency)
        newest = rs[-1]["circular_number"]
        for r in rs[:-1]:
            add_supersede(newest, r["circular_number"], confidence="inferred",
                          extractor="master_topic",
                          evidence=f"master-topic re-issue: {rs[-1].get('subject', '')!r}")

    return lin


def demote_superseded(reranked, lineage: "Lineage", penalty: float = 0.3):
    """Down-weight reranked (chunk, score) pairs from superseded circulars and
    re-sort, so an in-force successor is cited over its superseded predecessor.
    """
    out = [
        (c, s * penalty if c.doc_id in lineage.superseded_by else s)
        for c, s in reranked
    ]
    out.sort(key=lambda cs: -cs[1])
    return out


def superseded_citations(citations: list[str], lineage: Lineage) -> dict[str, list[str]]:
    """Map any cited circular that is superseded -> the circular(s) superseding it.

    Accepts chunk ids ("<circular>#...") or bare circular numbers. Lets the
    generation layer warn the user when an answer cites a superseded circular.
    """
    out: dict[str, list[str]] = {}
    for c in citations:
        cn = c.split("#", 1)[0]
        if cn in lineage.superseded_by and cn not in out:
            out[cn] = lineage.superseded_by[cn]
    return out


def load_records(corpus_path: str | Path) -> list[dict]:
    out = []
    for line in Path(corpus_path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def annotate_corpus(corpus_path: str | Path) -> dict:
    """Update each corpus record's supersession_status + superseded_by + supersedes
    from the lineage graph. Returns a summary. Idempotent."""
    corpus_path = Path(corpus_path)
    records = load_records(corpus_path)
    lin = build_lineage(records)
    changed = 0
    for r in records:
        cn = r["circular_number"]
        new_status = lin.status(cn)
        sup_by = lin.superseded_by.get(cn, [])
        supersedes = lin.supersedes.get(cn, [])
        if (r.get("supersession_status") != new_status
                or r.get("superseded_by") != sup_by
                or r.get("supersedes") != supersedes):
            changed += 1
        r["supersession_status"] = new_status
        r["superseded_by"] = sup_by
        r["supersedes"] = supersedes
    corpus_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )
    return {
        "records": len(records),
        "changed": changed,
        "supersedes_edges": sum(len(v) for v in lin.supersedes.values()),
        "superseded_in_corpus": [r["circular_number"] for r in records
                                 if lin.status(r["circular_number"]) == "superseded"],
    }
