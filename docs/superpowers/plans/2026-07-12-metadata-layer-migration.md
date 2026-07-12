# Metadata Layer Migration (Phase 1–2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `circular_type`, `validity_status`, `superseded_by_id`, and confidence-tiered `supersession_edges` to every corpus record and chunk, plus an as-of-date governing-circular selector, so retrieval can answer "which circular governs on date X".

**Architecture:** Additive-only migration. New module `src/sebi_rag/metadata.py` owns the type taxonomy and validity derivation (pure functions). `src/sebi_rag/lineage.py` gains confidence-tiered edge records and a `governing_on()` selector. `annotate_corpus()` writes the new fields into `data/corpus/circulars.jsonl` (local JSONL = source of truth; HF configs are regenerated exports — Phase 3, out of scope here). Existing fields (`supersession_status`, `superseded_by`, `supersedes`) are untouched.

**Tech Stack:** Python 3.12–3.13, stdlib `re`/`json`/`dataclasses`, pytest. No new dependencies.

## Global Constraints

- Additive only: never rename or change semantics of `supersession_status`, `superseded_by`, `supersedes`, or any existing `CircularMeta` field.
- `circular_type` enum: `CIRCULAR | MASTER_CIRCULAR | CLARIFICATION | AMENDMENT | ADDENDUM | CORRIGENDUM`.
- `validity_status` enum: `current | superseded | partially_superseded | unknown`.
- `validity_status` is computed from `confidence == "explicit_text"` edges only. `inferred` edges (master-topic re-issues) never flip status; they are soft metadata used by the as-of selector.
- Edge record shape (everywhere): `{"source": str, "target": str, "relation": "supersedes"|"amends", "confidence": "explicit_text"|"inferred", "extractor": str, "evidence": str}`. `source` = the newer/acting circular; `target` = the circular acted upon.
- Dates are ISO `YYYY-MM-DD` strings; comparison is lexicographic.
- Run tests with `make test` (offline suite) or `uv run pytest tests/<file> -v`.
- Model allocation: Task 1 = Fable (done in planning session). Tasks 2–6 = Sonnet 5. Task 7 = Sonnet 5 run + Fable validation checkpoint.
- API/UI exposure of `as_of` and the HF dataset re-export are explicitly out of scope (Phase 3 plan).

---

### Task 1: `metadata.py` — type classifier + validity derivation (Fable — completed in planning session)

**Files:**
- Create: `src/sebi_rag/metadata.py`
- Test: `tests/test_metadata.py`

**Interfaces:**
- Produces: `classify_circular_type(subject: str | None) -> str`; `derive_validity(circular_number: str, issue_date: str | None, edges: list[dict]) -> str`; constants `CIRCULAR_TYPES`, `VALIDITY_STATUSES`.

- [x] **Step 1: Write the failing tests**

```python
"""Metadata layer: circular_type taxonomy + validity_status derivation."""
from sebi_rag.metadata import (
    CIRCULAR_TYPES, VALIDITY_STATUSES, classify_circular_type, derive_validity,
)


def edge(source, target, relation="supersedes", confidence="explicit_text"):
    return {"source": source, "target": target, "relation": relation,
            "confidence": confidence, "extractor": "regex:SUPERSEDE_RE", "evidence": ""}


class TestClassifyCircularType:
    def test_master_circular(self):
        assert classify_circular_type("Master Circular for Mutual Funds") == "MASTER_CIRCULAR"

    def test_corrigendum(self):
        assert classify_circular_type("Corrigendum to circular on KYC norms") == "CORRIGENDUM"

    def test_addendum(self):
        assert classify_circular_type("Addendum to SEBI circular dated ...") == "ADDENDUM"

    def test_clarification(self):
        assert classify_circular_type("Clarification on REIT disclosure norms") == "CLARIFICATION"

    def test_clarificatory_stem_matches(self):
        assert classify_circular_type("Clarificatory circular on AIF norms") == "CLARIFICATION"

    def test_amendment(self):
        assert classify_circular_type("Amendment to circular on margin obligations") == "AMENDMENT"

    def test_plain_circular_default(self):
        assert classify_circular_type("Review of margin framework") == "CIRCULAR"

    def test_none_and_empty_default(self):
        assert classify_circular_type(None) == "CIRCULAR"
        assert classify_circular_type("") == "CIRCULAR"

    def test_precedence_master_beats_amendment(self):
        assert classify_circular_type(
            "Master Circular on Amendment procedures") == "MASTER_CIRCULAR"

    def test_precedence_clarification_beats_amendment(self):
        # mirrors the corpus probe ordering used to lock the taxonomy
        assert classify_circular_type(
            "Clarification on amendment to LODR circular") == "CLARIFICATION"

    def test_all_outputs_in_enum(self):
        for s in ("Master Circular on X", "Corrigendum", "Addendum", "Clarification",
                  "Amendment", "anything else", None):
            assert classify_circular_type(s) in CIRCULAR_TYPES


class TestDeriveValidity:
    CN = "SEBI/HO/IMD/DF2/CIR/P/2021/024"
    NEWER = "SEBI/HO/IMD/DF2/CIR/P/2024/031"

    def test_explicit_supersession_wins(self):
        assert derive_validity(self.CN, "2021-03-01",
                               [edge(self.NEWER, self.CN)]) == "superseded"

    def test_explicit_supersession_wins_even_without_date(self):
        assert derive_validity(self.CN, "", [edge(self.NEWER, self.CN)]) == "superseded"

    def test_explicit_amendment_is_partially_superseded(self):
        assert derive_validity(self.CN, "2021-03-01",
                               [edge(self.NEWER, self.CN, relation="amends")]
                               ) == "partially_superseded"

    def test_supersession_beats_amendment(self):
        edges = [edge(self.NEWER, self.CN, relation="amends"),
                 edge(self.NEWER, self.CN, relation="supersedes")]
        assert derive_validity(self.CN, "2021-03-01", edges) == "superseded"

    def test_inferred_supersession_stays_current(self):
        # locked decision: inferred edges are soft metadata only
        assert derive_validity(self.CN, "2021-03-01",
                               [edge(self.NEWER, self.CN, confidence="inferred")]
                               ) == "current"

    def test_missing_date_unknown(self):
        assert derive_validity(self.CN, "", []) == "unknown"
        assert derive_validity(self.CN, None, []) == "unknown"

    def test_malformed_date_unknown(self):
        assert derive_validity(self.CN, "13 July 2023", []) == "unknown"

    def test_no_edges_good_date_current(self):
        assert derive_validity(self.CN, "2021-03-01", []) == "current"

    def test_edges_for_other_circulars_ignored(self):
        assert derive_validity(self.CN, "2021-03-01",
                               [edge(self.NEWER, "SEBI/HO/OTHER/2020/001")]) == "current"

    def test_outgoing_edges_ignored(self):
        # CN superseding someone else does not change CN's own validity
        assert derive_validity(self.CN, "2021-03-01",
                               [edge(self.CN, "SEBI/HO/OTHER/2020/001")]) == "current"

    def test_all_outputs_in_enum(self):
        for args in (("", []), ("2021-03-01", []),
                     ("2021-03-01", [edge(self.NEWER, self.CN)])):
            assert derive_validity(self.CN, *args) in VALIDITY_STATUSES
```

- [x] **Step 2: Run tests to verify they fail** — `uv run pytest tests/test_metadata.py -v` → FAIL `ModuleNotFoundError: sebi_rag.metadata`

- [x] **Step 3: Implement `src/sebi_rag/metadata.py`**

```python
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
```

- [x] **Step 4: Run tests to verify they pass** — `uv run pytest tests/test_metadata.py -v` → all PASS
- [x] **Step 5: Commit** — `git add src/sebi_rag/metadata.py tests/test_metadata.py docs/superpowers/plans/2026-07-12-metadata-layer-migration.md && git commit -m "feat: metadata layer — circular_type taxonomy + validity derivation"`

---

### Task 2: Tiered supersession edges in `lineage.py` (Sonnet 5)

**Files:**
- Modify: `src/sebi_rag/lineage.py` (functions `detect_relations` L29, `Lineage` L51, `build_lineage` L102)
- Test: `tests/test_lineage.py` (append new tests; do not change the 7 existing tests)

**Interfaces:**
- Consumes: edge record shape from Global Constraints; `REF_RE` from `sebi_rag.ingest_pdf` (already imported).
- Produces: `detect_relations_ex(circular_number: str, text: str) -> list[dict]` (keys: `relation`, `target`, `evidence`, `extractor`; relation ∈ `supersedes|amends|references`); `Lineage.edges: list[dict]`; `Lineage.explicit_superseded_by(cn: str) -> list[str]`; `build_lineage` populating `edges` with `confidence` tiers; `save`/`load` round-tripping `edges` (default `[]` for old files).

- [ ] **Step 1: Write the failing tests** (append to `tests/test_lineage.py`)

```python
def test_detect_relations_ex_evidence_and_extractor():
    from sebi_rag.lineage import detect_relations_ex
    text = ("This circular supersedes Circular No. SEBI/HO/IMD/DF2/CIR/P/2021/024 "
            "with immediate effect.")
    rels = detect_relations_ex("SEBI/HO/IMD/DF2/CIR/P/2024/031", text)
    sup = [r for r in rels if r["relation"] == "supersedes"]
    assert sup and sup[0]["target"] == "SEBI/HO/IMD/DF2/CIR/P/2021/024"
    assert "supersedes" in sup[0]["evidence"]
    assert sup[0]["extractor"] == "regex:SUPERSEDE_RE"


def test_detect_relations_delegates_unchanged():
    from sebi_rag.lineage import detect_relations
    text = "This circular supersedes SEBI/HO/IMD/DF2/CIR/P/2021/024."
    assert ("supersedes", "SEBI/HO/IMD/DF2/CIR/P/2021/024") in detect_relations(
        "SEBI/HO/IMD/DF2/CIR/P/2024/031", text)


def test_build_lineage_edges_tiered():
    from sebi_rag.lineage import build_lineage
    records = [
        {"circular_number": "NEW/1", "issue_date": "2024-01-01",
         "subject": "Master Circular for Mutual Funds",
         "text": "This circular supersedes OLD/1 in full."},
        {"circular_number": "OLD/1", "issue_date": "2021-01-01",
         "subject": "Master Circular for Mutual Funds", "text": "Old content."},
    ]
    lin = build_lineage(records)
    tiers = {(e["source"], e["target"]): e["confidence"] for e in lin.edges}
    # explicit text edge wins the tier for (NEW/1, OLD/1) even though the
    # master-topic rule also links them; no duplicate edge is emitted
    assert tiers[("NEW/1", "OLD/1")] == "explicit_text"
    assert len(lin.edges) == 1


def test_build_lineage_inferred_master_topic_edge():
    from sebi_rag.lineage import build_lineage
    records = [
        {"circular_number": "MC/2", "issue_date": "2024-01-01",
         "subject": "Master Circular for Depositories", "text": "No refs here."},
        {"circular_number": "MC/1", "issue_date": "2021-01-01",
         "subject": "Master Circular for Depositories", "text": "No refs here."},
    ]
    lin = build_lineage(records)
    e = [e for e in lin.edges if e["source"] == "MC/2" and e["target"] == "MC/1"]
    assert e and e[0]["confidence"] == "inferred" and e[0]["extractor"] == "master_topic"
    assert lin.explicit_superseded_by("MC/1") == []
    assert lin.superseded_by["MC/1"] == ["MC/2"]  # legacy dicts keep both tiers


def test_lineage_save_load_roundtrips_edges(tmp_path):
    from sebi_rag.lineage import Lineage
    lin = Lineage(edges=[{"source": "A", "target": "B", "relation": "supersedes",
                          "confidence": "explicit_text",
                          "extractor": "regex:SUPERSEDE_RE", "evidence": "x"}])
    p = tmp_path / "lin.json"
    lin.save(p)
    assert Lineage.load(p).edges == lin.edges


def test_lineage_load_old_file_defaults_empty_edges(tmp_path):
    from sebi_rag.lineage import Lineage
    p = tmp_path / "old.json"
    p.write_text('{"supersedes": {}, "amends": {}, "superseded_by": {}, "amended_by": {}}',
                 encoding="utf-8")
    assert Lineage.load(p).edges == []
```

- [ ] **Step 2: Run to verify failure** — `uv run pytest tests/test_lineage.py -v` → new tests FAIL (`ImportError: detect_relations_ex`, `TypeError: unexpected keyword 'edges'`), 7 existing tests still PASS.

- [ ] **Step 3: Implement.** In `src/sebi_rag/lineage.py`:

Replace the body of `detect_relations` with a delegate and add `detect_relations_ex` above it:

```python
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
```

Add to `Lineage`: field `edges: list[dict] = field(default_factory=list)`; method

```python
    def explicit_superseded_by(self, circular_number: str) -> list[str]:
        return [e["source"] for e in self.edges
                if e["target"] == circular_number
                and e["relation"] == "supersedes"
                and e["confidence"] == "explicit_text"]
```

`save()` adds `"edges": self.edges` to the JSON dict; `load()` adds `edges=d.get("edges", [])`.

In `build_lineage`, extend `add_supersede` to carry edge metadata and dedupe (explicit beats inferred):

```python
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
```

In step 1 of `build_lineage`, switch to `detect_relations_ex` so evidence flows through; amend edges are also recorded:

```python
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
```

In step 2 (master-topic re-issues), pass the tier:

```python
        for r in rs[:-1]:
            add_supersede(newest, r["circular_number"], confidence="inferred",
                          extractor="master_topic",
                          evidence=f"master-topic re-issue: {rs[-1].get('subject', '')!r}")
```

- [ ] **Step 4: Run** — `uv run pytest tests/test_lineage.py tests/test_pipeline.py -v` → all PASS (legacy dict behaviour unchanged).
- [ ] **Step 5: Commit** — `git commit -m "feat: confidence-tiered supersession edges in lineage graph"`

---

### Task 3: `annotate_corpus` writes the four new fields (Sonnet 5)

**Files:**
- Modify: `src/sebi_rag/lineage.py:175-204` (`annotate_corpus`)
- Test: `tests/test_lineage.py` (append)

**Interfaces:**
- Consumes: `classify_circular_type`, `derive_validity` from `sebi_rag.metadata` (Task 1); `Lineage.edges`, `explicit_superseded_by` (Task 2).
- Produces: each corpus record gains `circular_type: str`, `validity_status: str`, `superseded_by_id: list[str]` (explicit tier only), `supersession_edges: list[dict]` (edges where the record is `source`). Summary dict gains `"validity_counts": dict[str, int]`.

- [ ] **Step 1: Write the failing test**

```python
def test_annotate_corpus_writes_new_metadata_fields(tmp_path):
    import json
    from sebi_rag.lineage import annotate_corpus
    recs = [
        {"circular_number": "NEW/1", "issue_date": "2024-01-01",
         "subject": "Master Circular for Mutual Funds",
         "text": "This circular supersedes OLD/1 in full."},
        {"circular_number": "OLD/1", "issue_date": "2021-01-01",
         "subject": "Mutual fund norms", "text": "Old content."},
        {"circular_number": "NODATE/1", "issue_date": "",
         "subject": "Clarification on custody", "text": "No refs."},
    ]
    p = tmp_path / "c.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    summary = annotate_corpus(p)
    out = {r["circular_number"]: r
           for r in map(json.loads, p.read_text().splitlines())}
    assert out["NEW/1"]["circular_type"] == "MASTER_CIRCULAR"
    assert out["NEW/1"]["validity_status"] == "current"
    assert out["OLD/1"]["validity_status"] == "superseded"
    assert out["OLD/1"]["superseded_by_id"] == ["NEW/1"]
    assert out["NODATE/1"]["circular_type"] == "CLARIFICATION"
    assert out["NODATE/1"]["validity_status"] == "unknown"
    edges = out["NEW/1"]["supersession_edges"]
    assert edges and edges[0]["target"] == "OLD/1" and edges[0]["confidence"] == "explicit_text"
    # legacy fields still written exactly as before
    assert out["OLD/1"]["supersession_status"] == "superseded"
    assert out["OLD/1"]["superseded_by"] == ["NEW/1"]
    assert summary["validity_counts"]["superseded"] == 1
```

- [ ] **Step 2: Run to verify failure** — `uv run pytest tests/test_lineage.py::test_annotate_corpus_writes_new_metadata_fields -v` → FAIL (KeyError `circular_type`).

- [ ] **Step 3: Implement.** In `annotate_corpus`, add `from .metadata import classify_circular_type, derive_validity` (module-level import at top of file). Inside the record loop, after the existing legacy assignments:

```python
        r["circular_type"] = classify_circular_type(r.get("subject"))
        r["validity_status"] = derive_validity(cn, r.get("issue_date"), lin.edges)
        r["superseded_by_id"] = lin.explicit_superseded_by(cn)
        r["supersession_edges"] = [e for e in lin.edges if e["source"] == cn]
```

(Include the four new fields in the `changed` comparison the same way the legacy fields are compared.) Extend the returned summary:

```python
        "validity_counts": {
            s: sum(1 for r in records if r["validity_status"] == s)
            for s in ("current", "superseded", "partially_superseded", "unknown")
        },
```

- [ ] **Step 4: Run** — `uv run pytest tests/test_lineage.py -v` → PASS.
- [ ] **Step 5: Commit** — `git commit -m "feat: annotate corpus with circular_type, validity_status, tiered edges"`

---

### Task 4: Propagate new fields into `CircularMeta` and chunk meta (Sonnet 5)

**Files:**
- Modify: `src/sebi_rag/segment.py:13-22` (`CircularMeta`), `src/sebi_rag/corpus.py:17-26` (`load_circulars`)
- Test: `tests/test_persistence.py` or new `tests/test_metadata.py` additions (put them in `tests/test_metadata.py`)

**Interfaces:**
- Consumes: corpus records with Task 3 fields.
- Produces: `CircularMeta.circular_type: str = ""`, `CircularMeta.validity_status: str = ""`, `CircularMeta.superseded_by_id: tuple[str, ...] = ()`; chunk `meta` dicts carry the three new keys (verify `hierarchical_chunk` builds `meta` via `asdict(meta)` — it does; if a field allowlist exists instead, extend it).

- [ ] **Step 1: Write the failing test** (append to `tests/test_metadata.py`)

```python
def test_chunk_meta_carries_new_fields(tmp_path):
    import json
    from sebi_rag.corpus import load_circulars
    rec = {"circular_number": "NEW/1", "issue_date": "2024-01-01",
           "subject": "Master Circular for Mutual Funds",
           "supersession_status": "in_force",
           "circular_type": "MASTER_CIRCULAR", "validity_status": "current",
           "superseded_by_id": [], "text": "Para one.\n\nPara two."}
    p = tmp_path / "c.jsonl"
    p.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    chunks = load_circulars(p)
    assert chunks
    assert chunks[0].meta["circular_type"] == "MASTER_CIRCULAR"
    assert chunks[0].meta["validity_status"] == "current"
    assert chunks[0].meta["superseded_by_id"] == ()
```

- [ ] **Step 2: Run to verify failure** — FAIL (`TypeError: unexpected keyword` or KeyError).

- [ ] **Step 3: Implement.** Append to `CircularMeta` (after `version_lineage`):

```python
    circular_type: str = ""          # metadata migration 2026-07: see metadata.py
    validity_status: str = ""        # current | superseded | partially_superseded | unknown
    superseded_by_id: tuple[str, ...] = ()  # explicit_text tier only
```

In `corpus.load_circulars`, add to the `CircularMeta(...)` call:

```python
            circular_type=r.get("circular_type", ""),
            validity_status=r.get("validity_status", ""),
            superseded_by_id=tuple(r.get("superseded_by_id", [])),
```

- [ ] **Step 4: Run** — `uv run pytest tests/test_metadata.py tests/test_persistence.py tests/test_incremental_index.py -v` → PASS.
- [ ] **Step 5: Commit** — `git commit -m "feat: propagate metadata fields into CircularMeta and chunk meta"`

---

### Task 5: As-of-date governing-circular selector (Sonnet 5 implements; Fable validates)

**Files:**
- Modify: `src/sebi_rag/lineage.py` (add two methods on `Lineage`)
- Test: `tests/test_lineage.py` (append)

**Interfaces:**
- Produces: `Lineage.family(circular_number: str) -> set[str]`; `Lineage.governing_on(circular_number: str, as_of: str, issue_dates: dict[str, str]) -> str | None`.
- Semantics (Fable spec — implement exactly): family = connected component over `supersedes` + `superseded_by` (both tiers), cycle-safe. Candidates = family members with a known `issue_date <= as_of`. Return `None` when no candidate exists (query predates the family). Governing = a candidate not superseded (either tier) by any other candidate; if several (parallel branches) or none (cycle), pick max `(issue_date, circular_number)` for determinism.

- [ ] **Step 1: Write the failing tests**

```python
def _lin_chain():
    # A (2019) < B (2021) < C (2023), linear supersession
    from sebi_rag.lineage import Lineage
    return (Lineage(
        supersedes={"B": ["A"], "C": ["B"]},
        superseded_by={"A": ["B"], "B": ["C"]},
    ), {"A": "2019-01-01", "B": "2021-01-01", "C": "2023-01-01"})


def test_governing_on_linear_chain():
    lin, dates = _lin_chain()
    assert lin.governing_on("A", "2020-06-01", dates) == "A"
    assert lin.governing_on("A", "2022-06-01", dates) == "B"
    assert lin.governing_on("A", "2024-06-01", dates) == "C"
    # entry point anywhere in the family gives the same answer
    assert lin.governing_on("C", "2020-06-01", dates) == "A"


def test_governing_on_before_family_exists():
    lin, dates = _lin_chain()
    assert lin.governing_on("A", "2018-01-01", dates) is None


def test_governing_on_unknown_dates_excluded():
    lin, dates = _lin_chain()
    dates = dict(dates, C="")  # C has no usable date
    assert lin.governing_on("A", "2024-06-01", dates) == "B"


def test_governing_on_cycle_safe():
    from sebi_rag.lineage import Lineage
    lin = Lineage(supersedes={"X": ["Y"], "Y": ["X"]},
                  superseded_by={"X": ["Y"], "Y": ["X"]})
    dates = {"X": "2020-01-01", "Y": "2021-01-01"}
    # both superseded within the candidate set -> deterministic max-date fallback
    assert lin.governing_on("X", "2022-01-01", dates) == "Y"


def test_governing_on_parallel_branches_max_date_wins():
    from sebi_rag.lineage import Lineage
    lin = Lineage(supersedes={"B1": ["A"], "B2": ["A"]},
                  superseded_by={"A": ["B1", "B2"]})
    dates = {"A": "2019-01-01", "B1": "2021-01-01", "B2": "2022-01-01"}
    assert lin.governing_on("A", "2023-01-01", dates) == "B2"
```

- [ ] **Step 2: Run to verify failure** — `AttributeError: 'Lineage' object has no attribute 'governing_on'`.

- [ ] **Step 3: Implement** (methods on `Lineage`):

```python
    def family(self, circular_number: str) -> set[str]:
        """Connected component over supersedes/superseded_by (both tiers)."""
        seen = {circular_number}
        stack = [circular_number]
        while stack:
            cn = stack.pop()
            for nb in self.supersedes.get(cn, []) + self.superseded_by.get(cn, []):
                if nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        return seen

    def governing_on(self, circular_number: str, as_of: str,
                     issue_dates: dict[str, str]) -> str | None:
        """The circular in this family that governs on date as_of (ISO), or
        None when every family member post-dates as_of."""
        cands = {cn for cn in self.family(circular_number)
                 if issue_dates.get(cn) and issue_dates[cn] <= as_of}
        if not cands:
            return None
        live = [cn for cn in cands
                if not any(s in cands for s in self.superseded_by.get(cn, []))]
        pool = live or sorted(cands)
        return max(pool, key=lambda cn: (issue_dates[cn], cn))
```

- [ ] **Step 4: Run** — `uv run pytest tests/test_lineage.py -v` → PASS.
- [ ] **Step 5: Commit** — `git commit -m "feat: as-of-date governing-circular selector on lineage graph"`

---

### Task 6: `as_of` filtering in `RAGPipeline.query` (Sonnet 5)

**Files:**
- Modify: `src/sebi_rag/pipeline.py:42-49` (`query`)
- Test: `tests/test_pipeline.py` (append)

**Interfaces:**
- Consumes: `Lineage.governing_on` (Task 5); chunk `meta["issue_date"]`.
- Produces: `RAGPipeline.query(question, pool=50, top_k=3, advisory=False, as_of: str | None = None)`. With `as_of` set and lineage present: chunks issued after `as_of` are dropped; chunks whose doc is not the governing circular on `as_of` are demoted by `superseded_penalty`; if filtering empties the pool, fall back to the unfiltered reranked list (never return zero candidates). API/UI exposure is out of scope.

- [ ] **Step 1: Write the failing test.** Reuse the existing test fixtures in `tests/test_pipeline.py` (stub embedder/reranker/generator — copy the pattern of the current lineage-demotion test in that file). Core assertion:

```python
def test_query_as_of_prefers_governing_circular(pipeline_with_lineage_factory):
    # corpus: OLD/1 (2020-01-01) superseded by NEW/1 (2023-01-01), same topic text
    pipe = pipeline_with_lineage_factory()
    ans_old, _ = pipe.query("margin rules", as_of="2021-06-01")
    ans_new, _ = pipe.query("margin rules", as_of="2024-06-01")
    assert any(c.startswith("OLD/1") for c in ans_old.citations)
    assert any(c.startswith("NEW/1") for c in ans_new.citations)
```

(If no reusable factory exists, build the two-record corpus inline exactly like the existing `demote_superseded` pipeline test does — same stub classes, plus `meta={"issue_date": ...}` on chunks.)

- [ ] **Step 2: Run to verify failure** — `TypeError: query() got an unexpected keyword argument 'as_of'`.

- [ ] **Step 3: Implement.** Change the signature to `def query(self, question, pool=50, top_k=3, advisory=False, as_of: str | None = None)` and insert after the `demote_superseded` block:

```python
        if as_of and self.lineage is not None:
            dates = {c.doc_id: (c.meta.get("issue_date") or "")
                     for c, _ in reranked}
            kept = []
            for c, s in reranked:
                d = dates.get(c.doc_id, "")
                if d and d > as_of:
                    continue  # circular did not exist on the as-of date
                gov = self.lineage.governing_on(c.doc_id, as_of, dates)
                kept.append((c, s if gov == c.doc_id else s * self.superseded_penalty))
            kept.sort(key=lambda cs: -cs[1])
            reranked = kept or reranked
```

- [ ] **Step 4: Run** — `uv run pytest tests/test_pipeline.py -v` → PASS; then `make test` → full suite PASS.
- [ ] **Step 5: Commit** — `git commit -m "feat: as-of-date retrieval filtering in RAG pipeline"`

---

### Task 7: Corpus annotation run + reindex + validation gate (Sonnet 5 runs; Fable signs off)

**Files:**
- Modify: `data/corpus/circulars.jsonl` (via `make annotate`), persisted index (via `make reindex`)
- No new code.

- [ ] **Step 1:** `make annotate` — expect summary with `records: 603` and a `validity_counts` dict; sanity: `superseded` ≲ 279 (explicit tier only, so it must be ≤ the legacy count), `unknown` ≈ 3, remainder `current`/`partially_superseded`.
- [ ] **Step 2:** Verify distribution:

```bash
python3 -c "
import json, collections
c = collections.Counter(); t = collections.Counter()
for line in open('data/corpus/circulars.jsonl'):
    r = json.loads(line); c[r['validity_status']] += 1; t[r['circular_type']] += 1
print(dict(c)); print(dict(t))"
```

Expected: types ≈ `{CIRCULAR: 516, MASTER_CIRCULAR: 44, CLARIFICATION: 23, AMENDMENT: 15, ADDENDUM: 3, CORRIGENDUM: 2}` (small drift from probe regexes acceptable); every record has all four new fields.
- [ ] **Step 3:** `make reindex`, then confirm chunk meta: `python3 -c "import json; print(json.loads(open('data/index/chunks.jsonl').readline())['meta'].keys())"` includes `circular_type`, `validity_status`, `superseded_by_id`.
- [ ] **Step 4:** `make test` → full suite PASS. Commit corpus + index: `git commit -m "chore: annotate corpus with metadata layer fields + reindex"`.
- [x] **Step 5 (Fable checkpoint — do not skip):** hand back to Fable with the distribution numbers and 15 sample records (5 MASTER_CIRCULAR, 5 explicit `superseded`, 3 `partially_superseded`, 2 `unknown`) for legal-semantics sign-off before Phase 3 (HF export). Fable also decides whether `master_topic` inferred edges get promoted to explicit after spot-check.

---

## Fable Checkpoint Verdict (2026-07-12) — SIGNED OFF

Distributions and samples approved. Decisions:

1. **`master_topic` inferred edges: NOT promoted.** Only 4 exist; 3 verified correct; the 4th (LODR master `HO/49/14/14(7)2025.../3762/2026`) is a continuously-updated master ("Issued on July 11 2023, Last updated January 30 2026") whose direction is correct via `effective_date`. Inferred stays soft, per locked decision.
2. **Dangling edges: no action.** All 398 `superseded_by_id` entries resolve to corpus records (sources are always records by construction). The 1018 dangling edge *targets* are old unscraped circulars — they can never be returned by `governing_on` (no `issue_date` → never candidates). Safe direction.
3. **Giant connected component (CRITICAL finding):** master ref-list over-tagging merges the lineage graph into one 942-node family. Raw `governing_on` over the full graph is cross-topic nonsense; it is only valid when the `issue_dates` dict is restricted to a topical candidate set — which is exactly what `RAGPipeline.query(as_of=...)` does (dates built from retrieved pool only). **Rule: never call `governing_on` with the full corpus dates dict; selector-level evaluation only on small verified families.** Precision tightening of `detect_relations_ex` (scope refs to a window after the supersession trigger instead of all-refs-after-first-trigger) is the Phase 4/5 lever to shrink the component; measure via golden as-of eval before/after.
4. **Explicit-tier precision:** ~26/275 superseded records (~9%) have >2 cross-domain superseders — over-tag suspects from master reference lists. Accepted for this milestone; quantified by P4 eval.
5. **Known dual-date limitation:** "Last updated" masters carry `issue_date` = original issue; supersession edges are timeless, so re-supersessions inside a family can mis-rank in the window between original issue and update (1 known family: LODR masters). Future refinement: edge-activation date = source's `max(issue_date, effective_date)`.
6. **Stale export golden (`test_export_integration.py` expects `chunks: 36603`, actual 36683):** confirmed pre-existing (backup corpus chunks to the same 36683); update the golden numbers as part of Task 8 export regeneration.

**P4a delivered by Fable:** `eval/golden/golden_asof_v1.jsonl` — 10 pipeline-mode + 3 selector-mode cases. All selector expectations and all retrieval-scoped pipeline expectations verified against the live lineage graph on 2026-07-12.

---

### Task 8: HF export regeneration + stale goldens (Sonnet 5) — Phase 3

**Files:**
- Modify: `tests/test_export_integration.py` (the `expected` dict in `test_row_count_accuracy_in_live_export`)
- Regenerate: `dist/datasets/` via `make benchmark-export` / `make export-datasets`

- [x] **Step 1:** Confirmed exporter whitelists columns (`CORPUS_SCHEMA`/`CHUNKS_SCHEMA`); extended both + `build_corpus_rows`/`build_chunk_rows`. TDD: 2 new tests in `test_export_datasets.py` (KeyError-confirmed fail, then pass).
- [x] **Step 2:** Ran `make export-datasets` (golden_v6 unchanged, `benchmark-export` not needed). Actuals: `corpus=603, chunks=36683, lineage=1437, eval=56, citation-normalization=2951, supersession-pairs=1281`. No parquet errors on nested `supersession_edges` (list[struct]).
- [x] **Step 3:** Updated `expected` dict in `test_row_count_accuracy_in_live_export` to actuals (chunks 36603→36683, lineage 1434→1437 — the +3 lineage rows come from this migration's new tiered edges, chunk growth is unrelated prior corpus scraping).
- [x] **Step 4:** `make test` → 195/195 PASS.
- [x] **Step 5:** Committed (`b0f7b8f`). **Did not push to HF Hub** — publishing stays user-gated.

### Task 9: As-of golden eval wiring (Sonnet 5) — Phase 4b

**Files:**
- Modify: `src/sebi_rag/eval_harness.py` (or a sibling `eval_asof.py` if the harness doesn't fit)
- Consume: `eval/golden/golden_asof_v1.jsonl` (schema: `mode: pipeline|selector`; pipeline rows have `query/as_of/expected_any/avoid`; selector rows have `entry/as_of/expected`)

- [ ] **Step 1:** Selector runner: load `data/index/lineage.json` + corpus dates; for each `mode=selector` row assert `lineage.governing_on(entry, as_of, dates) == expected` (full-corpus dates dict is correct **only** for these pre-verified rows). These 3 must pass — they are regression tests.
- [ ] **Step 2:** Pipeline runner: build the default pipeline once; for each `mode=pipeline` row call `pipe.query(query, as_of=as_of)`; score PASS when any citation startswith any `expected_any` entry AND no citation startswith an `avoid` entry. Report per-case PASS/FAIL + aggregate accuracy. **Pipeline-case failures are findings, not bugs** — report them to Fable, do not tune thresholds to force green.
- [ ] **Step 3:** Add a `make eval-asof` target mirroring existing eval targets. Commit.
- [ ] **Step 4:** Run it; hand results back to Fable for P4c accept/reject.
