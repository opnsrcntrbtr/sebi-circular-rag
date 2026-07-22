# SEBI Regulations Cross-Reference Layer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make SEBI Regulations first-class entities in the corpus and link every circular to the regulations it cites, exposing a regulation-repeal staleness signal the circular-to-circular supersession graph cannot see.

**Architecture:** Three pure-stdlib modules — `regulations.py` (identity + name resolution), `reg_citations.py` (text → raw citations), `reg_lineage.py` (edges + annotation) — plus three scripts (scrape, build, audit). Regulation text is *not* chunked or indexed in this phase. New circular fields are written to the corpus JSONL record only, never to `CircularMeta`, so the persisted index is unchanged by construction.

**Tech Stack:** Python 3.12, stdlib only for the three source modules (no torch/transformers/faiss). pytest. Existing helpers reused: `scripts/scrape_sebi.py` (`fetch`, `extract_pdf_urls`, `looks_like_pdf`), `sebi_rag.stats.clopper_pearson_ci`.

**Spec:** `docs/superpowers/specs/2026-07-23-sebi-regulations-cross-reference-design.md`

## Global Constraints

- Python 3.12 only (`pyproject.toml` pins `>=3.12,<3.13`). Use `.venv/bin/python`.
- Run all commands from the repo root: `/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG`.
- Tests need `PYTHONPATH=src`. The Makefile `ENV` var is `HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0 PYTHONPATH=src`.
- **Never add fields to `CircularMeta`** (`src/sebi_rag/segment.py:18-30`). `hierarchical_chunk()` does `meta=asdict(meta)` at line 131, so a new dataclass field propagates into all 34,883 chunk payloads and mutates the index. New fields go on the corpus JSONL record only, following the `is_master`/`master_series` precedent in `src/sebi_rag/master_meta.py:66-69`.
- **Never edit the Spaces modules** — `api_spaces.py`, `corpus_spaces.py`, `generate_spaces.py`, root `app.py`. They are the CPU-only Hugging Face demo path.
- **Do not modify `validity_status` or `supersession_status`.** The 2026-07-12 locked rule stands: validity derives from `explicit_text` circular→circular edges only.
- **Do not modify `make reindex`** or `scripts/build_index.py`.
- The three new `src/sebi_rag/` modules must import stdlib only, so every new test runs under `-m "not integration"`.
- `status` vocabulary is exactly `in_force` | `repealed` | `unknown`. `regulatory_basis_status` vocabulary is exactly `current` | `repealed_basis` | `mixed` | `unknown`. `evidence` vocabulary is exactly `subject_line` | `powers_clause` | `body_text`. `confidence` vocabulary is exactly `explicit_text` | `inferred`.
- `FUZZY_THRESHOLD = 0.8` (Jaccard over singularised, stopword-stripped tokens).
- Absence from the Updated List is never by itself proof of repeal. Only names with a `REG_SUCCESSION` entry get `status: "repealed"`; the rest get `status: "unknown"`.
- Commit after every task. Do not squash tasks together.

## Pre-staged asset

`tests/fixtures/regulation_listing.html` (41 KB) is **already committed** — a real capture of the live listing page fetched 2026-07-22. It contains exactly 42 regulation rows. Do not re-fetch it; the offline parser tests depend on this exact file.

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `src/sebi_rag/regulations.py` | Regulation identity, `reg_id` slug, alias table, name resolution, basis derivation | 1 |
| `tests/test_regulations.py` | Unit tests for the above | 1 |
| `src/sebi_rag/reg_citations.py` | Regex extraction of regulation citations from circular text | 2 |
| `tests/test_reg_citations.py` | Unit tests for the above | 2 |
| `scripts/scrape_regulations.py` | Listing parse + detail/PDF fetch → `regulations.jsonl` | 3 |
| `tests/test_scrape_regulations.py` | Offline parser tests against the staged fixture | 3 |
| `src/sebi_rag/reg_lineage.py` | Repealed stubs, edge build, corpus annotation | 4 |
| `tests/test_reg_lineage.py` | Unit tests for the above | 4 |
| `scripts/build_reg_edges.py` | Offline driver wiring 1+2+4 over the real corpus | 5 |
| `tests/test_build_reg_edges.py` | End-to-end driver test on a temp corpus | 5 |
| `scripts/audit_reg_edges.py` | Stratified precision sample + Clopper-Pearson CI | 6 |
| `tests/test_audit_reg_edges.py` | Unit tests for sampling and scoring | 6 |
| `Makefile` | `scrape-regs`, `reg-edges`, `audit-regs` targets | 5 |
| `CLAUDE.md` | Document new targets and modules | 6 |

---

### Task 1: Regulation identity and name resolution

**Files:**
- Create: `src/sebi_rag/regulations.py`
- Test: `tests/test_regulations.py`

**Interfaces:**
- Consumes: nothing (stdlib only)
- Produces:
  - `RegulationMeta` frozen dataclass
  - `reg_id(short_name: str, year: int) -> str`
  - `name_tokens(name: str) -> frozenset[str]`
  - `resolve_regulation(name: str, year: int, regulations: list[dict]) -> tuple[str | None, str]` returning `(reg_id_or_None, confidence)` where confidence is `"explicit_text"`, `"inferred"`, or `""`
  - `derive_regulatory_basis(statuses: list[str]) -> str`
  - `REGULATION_ALIASES: dict[tuple[str, int], str]`
  - `FUZZY_THRESHOLD: float`

- [ ] **Step 1: Write the failing test**

Create `tests/test_regulations.py`:

```python
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


def test_fuzzy_resolves_spelling_drift_as_inferred():
    assert resolve_regulation("Mutual Fund", 2026, REGS) == (
        "mutual-funds-2026", "inferred")
    assert resolve_regulation(
        "Substantial Acquisition of Shares and Takeover", 2011, REGS) == (
        "substantial-acquisition-of-shares-and-takeovers-2011", "inferred")
    assert resolve_regulation("Depositories Participants", 2018, REGS) == (
        "depositories-and-participants-2018", "inferred")


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


def test_regulation_meta_defaults():
    m = RegulationMeta(reg_id="x-2020", title="T", short_name="X", year=2020)
    assert m.status == "unknown"
    assert m.last_amended is None
    assert m.aliases == ()
    assert m.superseded_by_reg is None
    assert m.text == ""


def test_threshold_is_documented_constant():
    assert FUZZY_THRESHOLD == 0.8
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_regulations.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'sebi_rag.regulations'`

- [ ] **Step 3: Write the implementation**

Create `src/sebi_rag/regulations.py`:

```python
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
    ("", None) when nothing clears the threshold. Never guesses: an unresolved
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_regulations.py -q`
Expected: PASS — 13 passed

- [ ] **Step 5: Verify the module is stdlib-only**

Run: `PYTHONPATH=src .venv/bin/python -c "import sys; import sebi_rag.regulations; assert not {'torch','transformers','faiss'} & set(sys.modules), 'heavy import leaked'; print('stdlib clean')"`
Expected: `stdlib clean`

- [ ] **Step 6: Commit**

```bash
git add src/sebi_rag/regulations.py tests/test_regulations.py
git commit -m "feat(regulations): identity slug, alias table, name resolution

Three-stage resolution (exact tokens -> alias table -> Jaccard >= 0.8).
Acronyms need the table: PIT vs 'prohibition of insider trading' scores 0.0
and can never fuzzy-match. Threshold rejects the Depositories-alone decoy
(0.5) and ILDS-vs-NCS (0.6)."
```

---

### Task 2: Citation extraction

**Files:**
- Create: `src/sebi_rag/reg_citations.py`
- Test: `tests/test_reg_citations.py`

**Interfaces:**
- Consumes: nothing (stdlib only; deliberately independent of Task 1 so extraction and resolution stay separately testable)
- Produces:
  - `Citation` frozen dataclass with fields `name: str`, `year: int`, `clause: str | None`, `evidence: str`
  - `extract_citations(subject: str, text: str) -> list[Citation]` — one `Citation` per occurrence, **not** deduped; dedup happens in Task 4
  - `EVIDENCE_TIERS: tuple[str, ...]` in precedence order

- [ ] **Step 1: Write the failing test**

Create `tests/test_reg_citations.py`:

```python
"""Citation extraction from circular text (spec 2026-07-23 §3.3)."""
from sebi_rag.reg_citations import EVIDENCE_TIERS, Citation, extract_citations


def test_extracts_full_title_and_year():
    text = ("Disclosure under Securities and Exchange Board of India "
            "(Listing Obligations and Disclosure Requirements) Regulations, 2015.")
    cits = extract_citations("", text)
    assert len(cits) == 1
    assert cits[0].name == "Listing Obligations and Disclosure Requirements"
    assert cits[0].year == 2015


def test_extracts_sebi_short_form_and_acronyms():
    cits = extract_citations("", "as required by SEBI (PIT) Regulations, 2015.")
    assert [(c.name, c.year) for c in cits] == [("PIT", 2015)]


def test_year_without_comma_is_extracted():
    cits = extract_citations("", "under SEBI (Buy-back of Securities) Regulations 2018.")
    assert [(c.name, c.year) for c in cits] == [("Buy-back of Securities", 2018)]


def test_subject_line_citation_outranks_body():
    subject = "Amendment to SEBI (Mutual Funds) Regulations, 1996"
    text = "Something else entirely."
    cits = extract_citations(subject, text)
    assert cits[0].evidence == "subject_line"


def test_powers_clause_evidence_tier():
    text = ("In exercise of the powers conferred under section 11 read with "
            "SEBI (Credit Rating Agencies) Regulations, 1999, the Board directs.")
    cits = extract_citations("", text)
    assert cits[0].evidence == "powers_clause"


def test_plain_body_mention_is_body_text():
    text = "Reference is drawn to SEBI (Research Analysts) Regulations, 2014."
    cits = extract_citations("", text)
    assert cits[0].evidence == "body_text"


def test_clause_captured_when_same_sentence():
    text = ("Disclosure under Regulation 30(2) of SEBI (Listing Obligations "
            "and Disclosure Requirements) Regulations, 2015 is mandatory.")
    cits = extract_citations("", text)
    assert cits[0].clause == "30(2)"


def test_clause_not_captured_across_sentence_boundary():
    text = ("Regulation 30(2) sets the timeline. Separately, SEBI (Mutual "
            "Funds) Regulations, 2026 apply to schemes.")
    cits = extract_citations("", text)
    assert len(cits) == 1
    assert cits[0].clause is None


def test_four_digit_year_is_never_mistaken_for_a_clause():
    # "Regulations 2018" (no comma) must not yield clause="2018".
    text = "under SEBI (Buy-back of Securities) Regulations 2018, issuers shall."
    cits = extract_citations("", text)
    assert cits[0].clause is None


def test_alphanumeric_clause_is_captured():
    text = ("Under regulation 30A of SEBI (Listing Obligations and Disclosure "
            "Requirements) Regulations, 2015 the entity shall disclose.")
    cits = extract_citations("", text)
    assert cits[0].clause == "30A"


def test_multiple_distinct_regulations_in_one_document():
    text = ("Read SEBI (Mutual Funds) Regulations, 1996 together with "
            "SEBI (Alternative Investment Funds) Regulations, 2012.")
    cits = extract_citations("", text)
    assert {(c.name, c.year) for c in cits} == {
        ("Mutual Funds", 1996), ("Alternative Investment Funds", 2012)}


def test_repeated_mentions_yield_one_citation_each():
    text = ("SEBI (Mutual Funds) Regulations, 1996 applies. "
            "See SEBI (Mutual Funds) Regulations, 1996 again.")
    cits = extract_citations("", text)
    assert len(cits) == 2
    assert all(c.name == "Mutual Funds" for c in cits)


def test_parenthetical_containing_the_word_regulations_is_handled():
    # Real listing entry: "(Procedure for making, amending and reviewing of
    # Regulations) Regulations, 2025" — the word appears inside the bracket.
    text = ("per SEBI (Procedure for making, amending and reviewing of "
            "Regulations) Regulations, 2025.")
    cits = extract_citations("", text)
    assert cits[0].name == "Procedure for making, amending and reviewing of Regulations"
    assert cits[0].year == 2025


def test_no_citation_returns_empty_list():
    assert extract_citations("", "A circular with no statutory reference.") == []


def test_whitespace_in_name_is_collapsed():
    text = "SEBI (Mutual   \n Funds) Regulations, 1996 applies."
    cits = extract_citations("", text)
    assert cits[0].name == "Mutual Funds"


def test_evidence_tiers_are_in_precedence_order():
    assert EVIDENCE_TIERS == ("subject_line", "powers_clause", "body_text")


def test_citation_is_hashable():
    c = Citation(name="Mutual Funds", year=1996, clause=None, evidence="body_text")
    assert len({c, c}) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_reg_citations.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'sebi_rag.reg_citations'`

- [ ] **Step 3: Write the implementation**

Create `src/sebi_rag/reg_citations.py`:

```python
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
# (Name) Regulations 2018". The name group is non-greedy up to the closing
# bracket, so a parenthetical containing the word "Regulations" (the real
# "Procedure for making, amending and reviewing of Regulations" entry) survives.
CITATION_RE = re.compile(
    r"(?:Securities\s+and\s+Exchange\s+Board\s+of\s+India|SEBI)\s*"
    r"\(([^)]{2,120})\)\s*Regulations?[,\s]+(\d{4})",
    re.I | re.S)

POWERS_RE = re.compile(r"in\s+exercise\s+of\s+the\s+powers\s+conferred", re.I)

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_reg_citations.py -q`
Expected: PASS — 17 passed

- [ ] **Step 5: Sanity-check against the real corpus**

Run:
```bash
PYTHONPATH=src .venv/bin/python -c "
import json
from sebi_rag.reg_citations import extract_citations
n = hits = total = 0
for line in open('data/corpus/circulars.jsonl'):
    r = json.loads(line); n += 1
    c = extract_citations(r.get('subject',''), r.get('text',''))
    hits += bool(c); total += len(c)
print(f'docs={n} with_citations={hits} ({hits/n:.1%}) citations={total}')
"
```
Expected: `with_citations` is at least 500 (70.9%) — the measured baseline in the spec. A materially lower number means `CITATION_RE` regressed; do not proceed.

- [ ] **Step 6: Commit**

```bash
git add src/sebi_rag/reg_citations.py tests/test_reg_citations.py
git commit -m "feat(regulations): citation extraction with evidence tiering

One Citation per occurrence; precision carried by evidence tier
(subject_line > powers_clause > body_text) rather than by relation.
Clause captured same-sentence only, with 4-digit years excluded so the
comma-less 'Regulations 2018' form does not yield clause='2018'."
```

---

### Task 3: Regulation listing parser and scraper

**Files:**
- Create: `scripts/scrape_regulations.py`
- Test: `tests/test_scrape_regulations.py`
- Uses (do not modify): `tests/fixtures/regulation_listing.html`, `scripts/scrape_sebi.py`

**Interfaces:**
- Consumes: `scrape_sebi.fetch(url, rate) -> bytes`, `scrape_sebi.extract_pdf_urls(html, base_url) -> list[str]`, `scrape_sebi.looks_like_pdf(data) -> bool`, `regulations.reg_id`, `regulations.RegulationMeta`
- Produces:
  - `LISTING_URL: str`
  - `parse_listing(html: str) -> list[dict]` — each dict has keys `year: int`, `url: str`, `title: str`, `short_name: str`, `last_amended: str | None`
  - `parse_last_amended(title: str) -> str | None` — ISO date or None
  - `short_name_of(title: str) -> str | None`
  - `main(argv: list[str] | None = None) -> int`

- [ ] **Step 1: Write the failing test**

Create `tests/test_scrape_regulations.py`:

```python
"""Offline tests for the regulation listing parser (no network).

Fixture `regulation_listing.html` is a real capture of
https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=3&smid=0
taken 2026-07-22, containing exactly 42 in-force regulations.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scrape_regulations as S  # noqa: E402

FIXTURE = (Path(__file__).parent / "fixtures" / "regulation_listing.html"
           ).read_text(encoding="utf-8", errors="ignore")


def test_listing_parses_all_forty_two_rows():
    rows = S.parse_listing(FIXTURE)
    assert len(rows) == 42


def test_rows_carry_year_url_and_title():
    rows = S.parse_listing(FIXTURE)
    for r in rows:
        assert isinstance(r["year"], int) and 1990 <= r["year"] <= 2030
        assert r["url"].startswith("https://www.sebi.gov.in/legal/regulations/")
        assert r["url"].endswith(".html")
        assert r["title"]


def test_year_comes_from_the_issued_year_column_not_the_title():
    # FPI Regs 2019 sits in the jul-2026 folder with a 2026 amendment date;
    # its year must still be 2019.
    rows = S.parse_listing(FIXTURE)
    fpi = [r for r in rows if "Foreign Portfolio Investors" in r["title"]]
    assert fpi and fpi[0]["year"] == 2019


def test_every_row_yields_a_short_name():
    rows = S.parse_listing(FIXTURE)
    missing = [r["title"] for r in rows if not r["short_name"]]
    assert missing == []


def test_short_name_extraction():
    assert S.short_name_of(
        "Securities and Exchange Board of India (Mutual Funds) Regulations, 2026"
        " [Last amended on July 7, 2026]") == "Mutual Funds"


def test_short_name_survives_regulations_inside_the_parenthetical():
    assert S.short_name_of(
        "Securities and Exchange Board of India (Procedure for making, amending"
        " and reviewing of Regulations) Regulations, 2025"
    ) == "Procedure for making, amending and reviewing of Regulations"


def test_last_amended_standard_form():
    assert S.parse_last_amended(
        "SEBI (Mutual Funds) Regulations, 2026 [Last amended on July 7, 2026]"
    ) == "2026-07-07"


def test_last_amended_tolerates_real_source_typos():
    # All four variants occur verbatim in the live listing.
    assert S.parse_last_amended(
        "X Regulations, 2019 [Last amended on on July 07, 2026]") == "2026-07-07"
    assert S.parse_last_amended(
        "X Regulations, 2015 [Last amendment on July 08, 2026]") == "2026-07-08"
    assert S.parse_last_amended(
        "X Regulations, 2021 [amended as on January 21, 2026]") == "2026-01-21"
    assert S.parse_last_amended(
        "X Regulations, 2011 [Last amended on Last amended on December 5, 2025]"
    ) == "2025-12-05"


def test_last_amended_is_none_when_absent():
    assert S.parse_last_amended("SEBI (Stock Brokers) Regulations, 2026") is None


def test_exactly_four_fixture_rows_have_no_amendment_date():
    rows = S.parse_listing(FIXTURE)
    assert sum(r["last_amended"] is None for r in rows) == 4


def test_reg_ids_from_the_fixture_are_unique():
    from sebi_rag.regulations import reg_id
    rows = S.parse_listing(FIXTURE)
    ids = [reg_id(r["short_name"], r["year"]) for r in rows]
    assert len(set(ids)) == len(ids)


def test_empty_listing_parses_to_empty_list_not_an_error():
    assert S.parse_listing("<html><body>nothing</body></html>") == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_scrape_regulations.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'scrape_regulations'`

- [ ] **Step 3: Write the implementation**

Create `scripts/scrape_regulations.py`:

```python
"""Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).

Legality: same posture as scripts/scrape_sebi.py — SEBI robots.txt allows
/legal and /sebi_data/attachdocs; /js and /css are disallowed and are never
fetched. Self-imposed rate limit, descriptive User-Agent, checksum dedupe,
official source_url recorded.

Section sid=1 ssid=3 is "List of All SEBI Regulations (Updated)": 42 in-force
regulations on a SINGLE page with no pagination, so the doDirect POST machinery
in scrape_sebi.py is not used here. Detail pages embed the PDF through the same
`web/?file=` viewer iframe, so extract_pdf_urls() is reused unchanged.

Repealed regulations sit behind a `showHistory()` control defined in external
JS under /js, which robots.txt disallows. They are therefore NOT scraped;
reg_lineage.synthesise_repealed_stubs() derives them from corpus citations.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/scrape_regulations.py --rate 3
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from scrape_sebi import extract_pdf_urls, fetch, looks_like_pdf  # noqa: E402
from sebi_rag.regulations import RegulationMeta, reg_id  # noqa: E402

BASE = "https://www.sebi.gov.in"
LISTING_URL = (f"{BASE}/sebiweb/home/HomeAction.do"
               "?doListing=yes&sid=1&ssid=3&smid=0")

# <tr><td>2026</td><td><a href="...">Title [Last amended on ...]</a></td></tr>
ROW_RE = re.compile(
    r"<tr>\s*<td>\s*(\d{4})\s*</td>\s*<td>\s*"
    r"<a\s+href=\"(https://www\.sebi\.gov\.in/legal/regulations/[^\"]+)\""
    r"[^>]*>(.*?)</a>", re.S | re.I)

# Amendment phrases seen verbatim in the live listing, including SEBI's own
# typos: "on on", a repeated "Last amended on", "Last amendment on", lowercase,
# and "amended as on". A trailing duplicate prefix is absorbed by allowing the
# preamble to repeat.
LAST_AMENDED_RE = re.compile(
    r"(?:last\s+amend(?:ed|ment)|amended\s+as)\s+on\s+"
    r"(?:(?:last\s+amend(?:ed|ment)\s+)?on\s+)?"
    r"([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})", re.I)

SHORT_NAME_RE = re.compile(
    r"(?:Securities\s+and\s+Exchange\s+Board\s+of\s+India|SEBI)\s*"
    r"\((.+)\)\s*Regulations?", re.I | re.S)


def _text(html_fragment: str) -> str:
    s = re.sub(r"<[^>]+>", " ", html_fragment)
    s = (s.replace("&amp;", "&").replace("&nbsp;", " ")
          .replace("&#39;", "'").replace("&quot;", '"'))
    return re.sub(r"\s+", " ", s).strip()


def parse_last_amended(title: str) -> str | None:
    """ISO date of the last amendment, or None when the title carries none."""
    m = LAST_AMENDED_RE.search(title)
    if not m:
        return None
    try:
        d = dt.datetime.strptime(
            f"{m.group(1)[:3]} {int(m.group(2))}, {m.group(3)}", "%b %d, %Y").date()
    except ValueError:
        return None
    return d.isoformat()


def short_name_of(title: str) -> str | None:
    """The parenthetical short name, e.g. 'Mutual Funds'.

    Greedy up to the LAST ')' that precedes 'Regulations', so the real entry
    '(Procedure for making, amending and reviewing of Regulations) Regulations,
    2025' keeps its inner word instead of truncating at the first bracket.
    """
    m = SHORT_NAME_RE.search(title)
    if not m:
        return None
    return re.sub(r"\s+", " ", m.group(1)).strip()


def parse_listing(html: str) -> list[dict]:
    """(year, url, title, short_name, last_amended) per listing row, in order."""
    rows, seen = [], set()
    for year, url, raw_title in ROW_RE.findall(html):
        if url in seen:
            continue
        seen.add(url)
        title = _text(raw_title)
        rows.append({
            "year": int(year),
            "url": url,
            "title": title,
            "short_name": short_name_of(title) or "",
            "last_amended": parse_last_amended(title),
        })
    return rows


def _record(row: dict, pdf_url: str | None, pdf_path: str | None,
            sha: str | None, fetched: str) -> dict:
    meta = RegulationMeta(
        reg_id=reg_id(row["short_name"], row["year"]),
        title=row["title"],
        short_name=row["short_name"],
        year=row["year"],
        status="in_force",
        last_amended=row["last_amended"],
        source_url=row["url"],
        pdf_url=pdf_url,
        pdf_sha256=sha,
        pdf_path=pdf_path,
        provenance=f"SEBI Updated List, fetched {fetched}",
    )
    return asdict(meta)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rate", type=float, default=3.0)
    ap.add_argument("--out", default="data/corpus/regulations.jsonl")
    ap.add_argument("--raw", default="data/raw/regulations")
    ap.add_argument("--skip-pdfs", action="store_true",
                    help="identity only; do not download regulation PDFs")
    args = ap.parse_args(argv)

    raw_dir = Path(args.raw)
    raw_dir.mkdir(parents=True, exist_ok=True)
    fetched = dt.date.today().isoformat()

    print(f"Fetching listing (rate {args.rate}s)...", flush=True)
    rows = parse_listing(fetch(LISTING_URL, args.rate).decode("utf-8", "ignore"))
    if not rows:
        # Never truncate a good corpus file with an empty fetch.
        print("ERROR: listing returned 0 rows; leaving existing file untouched",
              flush=True)
        return 1
    print(f"Found {len(rows)} regulations.", flush=True)

    records, no_pdf = [], 0
    for i, row in enumerate(rows, 1):
        pdf_url = pdf_path = sha = None
        if not args.skip_pdfs:
            try:
                html = fetch(row["url"], args.rate).decode("utf-8", "ignore")
                urls = extract_pdf_urls(html, row["url"])
                if urls:
                    data = fetch(urls[0], args.rate)
                    if looks_like_pdf(data):
                        pdf_url = urls[0]
                        sha = hashlib.sha256(data).hexdigest()
                        dest = raw_dir / pdf_url.rsplit("/", 1)[-1]
                        dest.write_bytes(data)
                        pdf_path = str(dest)
                    else:
                        print(f"[{i}] not a PDF payload: {urls[0]}", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"[{i}] PDF fetch failed ({e}); keeping identity only",
                      flush=True)
        if pdf_url is None:
            no_pdf += 1
        records.append(_record(row, pdf_url, pdf_path, sha, fetched))
        print(f"[{i}/{len(rows)}] {records[-1]['reg_id']}", flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(records)} regulations to {out} "
          f"({no_pdf} without a PDF).", flush=True)
    print("Next: make reg-edges", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_scrape_regulations.py -q`
Expected: PASS — 12 passed

- [ ] **Step 5: Verify the offline parse produces sane reg_ids**

Run:
```bash
PYTHONPATH=src .venv/bin/python -c "
import sys; sys.path.insert(0, 'scripts')
from pathlib import Path
import scrape_regulations as S
from sebi_rag.regulations import reg_id
rows = S.parse_listing(Path('tests/fixtures/regulation_listing.html').read_text(errors='ignore'))
print(len(rows), 'rows')
for r in rows[:5]:
    print(' ', reg_id(r['short_name'], r['year']), '|', r['last_amended'])
"
```
Expected: `42 rows` followed by five well-formed slugs such as `infrastructure-investment-trusts-2014 | 2026-04-17`.

- [ ] **Step 6: Commit**

```bash
git add scripts/scrape_regulations.py tests/test_scrape_regulations.py tests/fixtures/regulation_listing.html
git commit -m "feat(regulations): listing parser + polite scraper

Single-page listing (sid=1&ssid=3), no pagination. Reuses scrape_sebi's
fetch/extract_pdf_urls/looks_like_pdf unchanged. Amendment-date regex
tolerates four verbatim source typos ('on on', repeated prefix,
'Last amendment on', 'amended as on'). Empty listing aborts rather than
truncating the corpus file."
```

---

### Task 4: Repealed stubs, edge build, corpus annotation

**Files:**
- Create: `src/sebi_rag/reg_lineage.py`
- Test: `tests/test_reg_lineage.py`

**Interfaces:**
- Consumes: `regulations.resolve_regulation`, `regulations.reg_id`, `regulations.derive_regulatory_basis`, `reg_citations.extract_citations`, `reg_citations.EVIDENCE_TIERS`
- Produces:
  - `REG_SUCCESSION: dict[str, str]`
  - `synthesise_repealed_stubs(circulars: list[dict], regulations: list[dict]) -> list[dict]` — returns **new stub records only**; caller appends
  - `build_regulation_edges(circulars: list[dict], regulations: list[dict]) -> tuple[list[dict], dict[tuple[str, int], int]]` — returns `(edges, unresolved_counts)`
  - `annotate_regulation_fields(circulars: list[dict], edges: list[dict], regulations: list[dict]) -> int` — mutates in place, returns change count, idempotent

- [ ] **Step 1: Write the failing test**

Create `tests/test_reg_lineage.py`:

```python
"""Regulation edges + corpus annotation (spec 2026-07-23 §3.3, §3.4, §3.7)."""
import pytest

from sebi_rag.reg_lineage import (REG_SUCCESSION, annotate_regulation_fields,
                                  build_regulation_edges,
                                  synthesise_repealed_stubs)

REGS = [
    {"reg_id": "mutual-funds-2026", "short_name": "Mutual Funds",
     "year": 2026, "status": "in_force"},
    {"reg_id": "listing-obligations-and-disclosure-requirements-2015",
     "short_name": "Listing Obligations and Disclosure Requirements",
     "year": 2015, "status": "in_force"},
]


def _circ(num, subject="", text=""):
    return {"circular_number": num, "subject": subject, "text": text}


def test_stub_is_created_for_a_cited_regulation_with_a_known_successor():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 1996.")]
    stubs = synthesise_repealed_stubs(circs, REGS)
    assert len(stubs) == 1
    s = stubs[0]
    assert s["reg_id"] == "mutual-funds-1996"
    assert s["status"] == "repealed"
    assert s["superseded_by_reg"] == "mutual-funds-2026"
    assert s["pdf_url"] is None and s["source_url"] is None
    assert s["text"] == ""
    assert "not on SEBI Updated List" in s["provenance"]


def test_stub_without_a_succession_entry_is_unknown_not_repealed():
    circs = [_circ("C/1", text="under SEBI (Some Vanished Thing) Regulations, 1994.")]
    stubs = synthesise_repealed_stubs(circs, REGS)
    assert len(stubs) == 1
    assert stubs[0]["status"] == "unknown"
    assert stubs[0]["superseded_by_reg"] is None


def test_stub_is_not_created_for_an_in_force_regulation():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 2026.")]
    assert synthesise_repealed_stubs(circs, REGS) == []


def test_stubs_are_deduped_across_circulars():
    circs = [_circ("C/1", text="SEBI (Mutual Funds) Regulations, 1996."),
             _circ("C/2", text="SEBI (Mutual Funds) Regulations, 1996 again.")]
    assert len(synthesise_repealed_stubs(circs, REGS)) == 1


def test_successor_gets_supersedes_reg_backlink():
    circs = [_circ("C/1", text="SEBI (Mutual Funds) Regulations, 1996.")]
    regs = [dict(r) for r in REGS]
    stubs = synthesise_repealed_stubs(circs, regs)
    regs.extend(stubs)
    succ = next(r for r in regs if r["reg_id"] == "mutual-funds-2026")
    assert "mutual-funds-1996" in succ["supersedes_reg"]


def test_edge_shape_and_vocabulary():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 2026.")]
    edges, unresolved = build_regulation_edges(circs, REGS)
    assert len(edges) == 1
    e = edges[0]
    assert e["source"] == "C/1"
    assert e["target"] == "mutual-funds-2026"
    assert e["relation"] == "cites"
    assert e["confidence"] == "explicit_text"
    assert e["evidence"] == "body_text"
    assert e["count"] == 1
    assert e["clause"] is None
    assert unresolved == {}


def test_one_edge_per_circular_regulation_pair_with_summed_count():
    circs = [_circ("C/1", text=("SEBI (Mutual Funds) Regulations, 2026 applies. "
                                "See SEBI (Mutual Funds) Regulations, 2026."))]
    edges, _ = build_regulation_edges(circs, REGS)
    assert len(edges) == 1
    assert edges[0]["count"] == 2


def test_highest_evidence_tier_wins_on_the_merged_edge():
    circs = [_circ("C/1",
                   subject="Amendment to SEBI (Mutual Funds) Regulations, 2026",
                   text="Body also cites SEBI (Mutual Funds) Regulations, 2026.")]
    edges, _ = build_regulation_edges(circs, REGS)
    assert len(edges) == 1
    assert edges[0]["evidence"] == "subject_line"
    assert edges[0]["count"] == 2


def test_clause_comes_from_the_winning_tier_occurrence():
    # Subject wins the tier and carries no clause, so the merged edge has none
    # even though a lower-tier body occurrence did.
    circs = [_circ("C/1",
                   subject="Amendment to SEBI (Mutual Funds) Regulations, 2026",
                   text=("Per Regulation 25(6) of SEBI (Mutual Funds) "
                         "Regulations, 2026 the AMC shall comply."))]
    edges, _ = build_regulation_edges(circs, REGS)
    assert edges[0]["evidence"] == "subject_line"
    assert edges[0]["clause"] is None


def test_clause_is_kept_when_the_body_occurrence_wins():
    circs = [_circ("C/1", text=("Per Regulation 25(6) of SEBI (Mutual Funds) "
                                "Regulations, 2026 the AMC shall comply."))]
    edges, _ = build_regulation_edges(circs, REGS)
    assert edges[0]["clause"] == "25(6)"


def test_fuzzy_match_is_marked_inferred():
    circs = [_circ("C/1", text="under SEBI (Mutual Fund) Regulations, 2026.")]
    edges, _ = build_regulation_edges(circs, REGS)
    assert edges[0]["confidence"] == "inferred"
    assert edges[0]["target"] == "mutual-funds-2026"


def test_unresolved_names_are_counted_not_dropped():
    circs = [_circ("C/1", text="under SEBI (Totally Unknown) Regulations, 1994.")]
    edges, unresolved = build_regulation_edges(circs, REGS)
    assert edges == []
    assert unresolved == {("Totally Unknown", 1994): 1}


def test_annotate_sets_the_three_additive_fields():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 2026.")]
    edges, _ = build_regulation_edges(circs, REGS)
    changed = annotate_regulation_fields(circs, edges, REGS)
    assert changed == 1
    assert circs[0]["regulations"] == ["mutual-funds-2026"]
    assert circs[0]["primary_regulation"] == "mutual-funds-2026"
    assert circs[0]["regulatory_basis_status"] == "current"


def test_annotate_is_idempotent():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 2026.")]
    edges, _ = build_regulation_edges(circs, REGS)
    assert annotate_regulation_fields(circs, edges, REGS) == 1
    assert annotate_regulation_fields(circs, edges, REGS) == 0


def test_annotate_orders_regulations_by_count_descending():
    circs = [_circ("C/1", text=(
        "SEBI (Listing Obligations and Disclosure Requirements) Regulations, "
        "2015 applies. SEBI (Mutual Funds) Regulations, 2026 applies. "
        "SEBI (Mutual Funds) Regulations, 2026 applies again."))]
    edges, _ = build_regulation_edges(circs, REGS)
    annotate_regulation_fields(circs, edges, REGS)
    assert circs[0]["regulations"][0] == "mutual-funds-2026"


def test_primary_regulation_prefers_evidence_tier_over_count():
    circs = [_circ("C/1",
                   subject=("Amendment to SEBI (Listing Obligations and "
                            "Disclosure Requirements) Regulations, 2015"),
                   text=("SEBI (Mutual Funds) Regulations, 2026 applies. "
                         "SEBI (Mutual Funds) Regulations, 2026 again. "
                         "SEBI (Mutual Funds) Regulations, 2026 thrice."))]
    edges, _ = build_regulation_edges(circs, REGS)
    annotate_regulation_fields(circs, edges, REGS)
    assert circs[0]["primary_regulation"] == (
        "listing-obligations-and-disclosure-requirements-2015")


def test_repealed_basis_and_mixed():
    regs = REGS + [{"reg_id": "mutual-funds-1996", "short_name": "Mutual Funds",
                    "year": 1996, "status": "repealed"}]
    dead = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 1996.")]
    edges, _ = build_regulation_edges(dead, regs)
    annotate_regulation_fields(dead, edges, regs)
    assert dead[0]["regulatory_basis_status"] == "repealed_basis"

    both = [_circ("C/2", text=("SEBI (Mutual Funds) Regulations, 1996 and "
                               "SEBI (Mutual Funds) Regulations, 2026."))]
    edges, _ = build_regulation_edges(both, regs)
    annotate_regulation_fields(both, edges, regs)
    assert both[0]["regulatory_basis_status"] == "mixed"


def test_circular_with_no_citations_gets_unknown_basis():
    circs = [_circ("C/1", text="No statutory reference here.")]
    edges, _ = build_regulation_edges(circs, REGS)
    annotate_regulation_fields(circs, edges, REGS)
    assert circs[0]["regulations"] == []
    assert circs[0]["primary_regulation"] is None
    assert circs[0]["regulatory_basis_status"] == "unknown"


def test_annotation_never_touches_validity_or_supersession():
    circs = [_circ("C/1", text="under SEBI (Mutual Funds) Regulations, 1996.")]
    circs[0].update(validity_status="current", supersession_status="in_force")
    edges, _ = build_regulation_edges(circs, REGS)
    annotate_regulation_fields(circs, edges, REGS)
    assert circs[0]["validity_status"] == "current"
    assert circs[0]["supersession_status"] == "in_force"


def test_annotation_adds_no_circular_meta_field():
    """Index-invariance guard (spec §3.1): the new fields must never be ones
    CircularMeta carries, or they would enter every chunk payload."""
    from dataclasses import fields
    from sebi_rag.segment import CircularMeta
    meta_fields = {f.name for f in fields(CircularMeta)}
    new_fields = {"regulations", "primary_regulation", "regulatory_basis_status"}
    assert meta_fields.isdisjoint(new_fields)


def test_succession_table_targets_are_distinct_from_sources():
    for src, dst in REG_SUCCESSION.items():
        assert src != dst
        assert src not in REG_SUCCESSION.get(dst, "")


@pytest.mark.parametrize("bad", [None, []])
def test_empty_inputs_do_not_raise(bad):
    edges, unresolved = build_regulation_edges(bad or [], REGS)
    assert edges == [] and unresolved == {}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_reg_lineage.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'sebi_rag.reg_lineage'`

- [ ] **Step 3: Write the implementation**

Create `src/sebi_rag/reg_lineage.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_reg_lineage.py -q`
Expected: PASS — 22 passed

- [ ] **Step 5: Run the whole offline suite to confirm nothing regressed**

Run: `make test`
Expected: PASS. The pre-existing 339 tests still pass; total is now 339 + the new ones.

- [ ] **Step 6: Commit**

```bash
git add src/sebi_rag/reg_lineage.py tests/test_reg_lineage.py
git commit -m "feat(regulations): stubs, circular->regulation edges, annotation

One cites edge per (circular, regulation); merged edge keeps the highest
evidence tier, that occurrence's clause, and the summed count. Repealed
stubs only when REG_SUCCESSION names a successor -- absence from the
Updated List is not proof of repeal. Annotation is record-only and
idempotent; a test asserts the new fields are disjoint from CircularMeta."
```

---

### Task 5: Offline driver and Makefile targets

**Files:**
- Create: `scripts/build_reg_edges.py`
- Test: `tests/test_build_reg_edges.py`
- Modify: `Makefile` (add three targets and three help lines)

**Interfaces:**
- Consumes: `reg_lineage.synthesise_repealed_stubs`, `reg_lineage.build_regulation_edges`, `reg_lineage.annotate_regulation_fields`
- Produces: `main(argv: list[str] | None = None) -> int`, `load_jsonl(path) -> list[dict]`, `write_jsonl(path, records) -> None`

- [ ] **Step 1: Write the failing test**

Create `tests/test_build_reg_edges.py`:

```python
"""End-to-end driver test on a temporary corpus (no network)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_reg_edges as B  # noqa: E402

CIRCS = [
    {"circular_number": "C/1", "subject": "", "issue_date": "2020-01-01",
     "text": "under SEBI (Mutual Funds) Regulations, 1996 the AMC shall comply.",
     "validity_status": "current"},
    {"circular_number": "C/2", "subject": "", "issue_date": "2024-01-01",
     "text": "per SEBI (Mutual Funds) Regulations, 2026 schemes shall report.",
     "validity_status": "current"},
    {"circular_number": "C/3", "subject": "", "issue_date": "2024-06-01",
     "text": "no statutory reference at all.", "validity_status": "current"},
]
REGS = [{"reg_id": "mutual-funds-2026", "title": "T", "short_name": "Mutual Funds",
         "year": 2026, "status": "in_force", "supersedes_reg": []}]


def _setup(tmp_path):
    c = tmp_path / "circulars.jsonl"
    r = tmp_path / "regulations.jsonl"
    B.write_jsonl(c, CIRCS)
    B.write_jsonl(r, REGS)
    return c, r


def test_driver_writes_edges_and_annotates(tmp_path):
    c, r = _setup(tmp_path)
    edges_out = tmp_path / "regulation_edges.jsonl"
    report = tmp_path / "unresolved.txt"
    rc = B.main(["--corpus", str(c), "--regulations", str(r),
                 "--edges", str(edges_out), "--report", str(report)])
    assert rc == 0

    edges = B.load_jsonl(edges_out)
    assert {e["source"] for e in edges} == {"C/1", "C/2"}
    assert all(e["relation"] == "cites" for e in edges)

    circs = B.load_jsonl(c)
    by_num = {x["circular_number"]: x for x in circs}
    assert by_num["C/1"]["regulatory_basis_status"] == "repealed_basis"
    assert by_num["C/2"]["regulatory_basis_status"] == "current"
    assert by_num["C/3"]["regulatory_basis_status"] == "unknown"


def test_driver_appends_repealed_stub_to_the_regulations_file(tmp_path):
    c, r = _setup(tmp_path)
    B.main(["--corpus", str(c), "--regulations", str(r),
            "--edges", str(tmp_path / "e.jsonl"),
            "--report", str(tmp_path / "u.txt")])
    regs = {x["reg_id"]: x for x in B.load_jsonl(r)}
    assert "mutual-funds-1996" in regs
    assert regs["mutual-funds-1996"]["status"] == "repealed"
    assert regs["mutual-funds-1996"]["superseded_by_reg"] == "mutual-funds-2026"
    assert "mutual-funds-1996" in regs["mutual-funds-2026"]["supersedes_reg"]


def test_driver_is_idempotent(tmp_path):
    c, r = _setup(tmp_path)
    args = ["--corpus", str(c), "--regulations", str(r),
            "--edges", str(tmp_path / "e.jsonl"),
            "--report", str(tmp_path / "u.txt")]
    B.main(args)
    first_regs = r.read_text()
    first_circs = c.read_text()
    B.main(args)
    assert r.read_text() == first_regs
    assert c.read_text() == first_circs


def test_driver_preserves_unrelated_circular_fields(tmp_path):
    c, r = _setup(tmp_path)
    B.main(["--corpus", str(c), "--regulations", str(r),
            "--edges", str(tmp_path / "e.jsonl"),
            "--report", str(tmp_path / "u.txt")])
    circs = B.load_jsonl(c)
    assert all(x["validity_status"] == "current" for x in circs)
    assert all(x["issue_date"] for x in circs)


def test_driver_writes_the_unresolved_report(tmp_path):
    c, r = _setup(tmp_path)
    B.write_jsonl(c, CIRCS + [{
        "circular_number": "C/4", "subject": "", "issue_date": "2024-01-01",
        "text": "per SEBI (Entirely Fictional Thing) Regulations, 1901.",
        "validity_status": "current"}])
    report = tmp_path / "unresolved.txt"
    B.main(["--corpus", str(c), "--regulations", str(r),
            "--edges", str(tmp_path / "e.jsonl"), "--report", str(report)])
    # A stub is minted for it, so it resolves on the second pass; the report
    # exists either way and is never a crash.
    assert report.exists()


def test_missing_regulations_file_exits_nonzero_without_writing(tmp_path):
    c = tmp_path / "circulars.jsonl"
    B.write_jsonl(c, CIRCS)
    before = c.read_text()
    rc = B.main(["--corpus", str(c), "--regulations", str(tmp_path / "nope.jsonl"),
                 "--edges", str(tmp_path / "e.jsonl"),
                 "--report", str(tmp_path / "u.txt")])
    assert rc != 0
    assert c.read_text() == before
    assert not (tmp_path / "e.jsonl").exists()


def test_load_jsonl_skips_blank_lines(tmp_path):
    p = tmp_path / "x.jsonl"
    p.write_text('{"a":1}\n\n{"a":2}\n', encoding="utf-8")
    assert B.load_jsonl(p) == [{"a": 1}, {"a": 2}]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_build_reg_edges.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'build_reg_edges'`

- [ ] **Step 3: Write the implementation**

Create `scripts/build_reg_edges.py`:

```python
"""Build circular -> regulation edges and annotate the corpus (offline).

No network, no model weights, idempotent. Ordering matters: repealed stubs are
synthesised BEFORE edges are built, because an edge may target a stub.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/build_reg_edges.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.reg_lineage import (annotate_regulation_fields,  # noqa: E402
                                  build_regulation_edges,
                                  synthesise_repealed_stubs)


def load_jsonl(path: str | Path) -> list[dict]:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def write_jsonl(path: str | Path, records: list[dict]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", default="data/corpus/circulars.jsonl")
    ap.add_argument("--regulations", default="data/corpus/regulations.jsonl")
    ap.add_argument("--edges", default="data/manifests/regulation_edges.jsonl")
    ap.add_argument("--report", default="reports/unresolved_regulations.txt")
    args = ap.parse_args(argv)

    reg_path = Path(args.regulations)
    if not reg_path.exists():
        print(f"ERROR: {reg_path} not found. Run `make scrape-regs` first.",
              file=sys.stderr)
        return 2

    circulars = load_jsonl(args.corpus)
    regulations = load_jsonl(reg_path)
    print(f"Loaded {len(circulars)} circulars, {len(regulations)} regulations.")

    stubs = synthesise_repealed_stubs(circulars, regulations)
    if stubs:
        regulations.extend(stubs)
        n_repealed = sum(s["status"] == "repealed" for s in stubs)
        print(f"Synthesised {len(stubs)} stub(s): "
              f"{n_repealed} repealed, {len(stubs) - n_repealed} unknown.")
    write_jsonl(reg_path, regulations)

    edges, unresolved = build_regulation_edges(circulars, regulations)
    write_jsonl(args.edges, edges)
    changed = annotate_regulation_fields(circulars, edges, regulations)
    write_jsonl(args.corpus, circulars)

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{c}\t{name}\t{year}" for (name, year), c
             in sorted(unresolved.items(), key=lambda kv: -kv[1])]
    report.write_text("count\tname\tyear\n" + "\n".join(lines) + "\n",
                      encoding="utf-8")

    linked = sum(1 for c in circulars if c.get("regulations"))
    basis = {}
    for c in circulars:
        k = c.get("regulatory_basis_status", "unknown")
        basis[k] = basis.get(k, 0) + 1
    print(f"\nEdges: {len(edges)} across {linked} circulars "
          f"({linked / max(len(circulars), 1):.1%} of corpus).")
    print(f"Annotated (changed): {changed}")
    print(f"regulatory_basis_status: {basis}")
    print(f"Unresolved names: {len(unresolved)} -> {report}")
    print("\nNext: make audit-regs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_build_reg_edges.py -q`
Expected: PASS — 7 passed

- [ ] **Step 5: Add the Makefile targets**

In `Makefile`, add `scrape-regs reg-edges audit-regs` to the `.PHONY` line, then add these three lines to the `help` target after the `verify-master` line:

```make
	@echo "scrape-regs    fetch SEBI regulations (Updated List, sid=1&ssid=3)"
	@echo "reg-edges      build circular->regulation edges + annotate corpus (offline)"
	@echo "audit-regs     precision audit of regulation edges (sample + CI)"
```

and add these targets at the end of the file:

```make
scrape-regs:
	$(ENV) $(PY) scripts/scrape_regulations.py --rate 3

reg-edges:
	$(ENV) $(PY) scripts/build_reg_edges.py

audit-regs:
	$(ENV) $(PY) scripts/audit_reg_edges.py
```

- [ ] **Step 6: Verify the targets are wired**

Run: `make help | grep -E "scrape-regs|reg-edges|audit-regs"`
Expected: three lines printed.

Run: `make -n reg-edges`
Expected: the echoed command ends with `scripts/build_reg_edges.py` and includes `PYTHONPATH=src`.

- [ ] **Step 7: Commit**

```bash
git add scripts/build_reg_edges.py tests/test_build_reg_edges.py Makefile
git commit -m "feat(regulations): offline edge-build driver + make targets

Stubs are synthesised before edges because an edge may target a stub.
Idempotent: re-running leaves both JSONL files byte-identical. Missing
regulations.jsonl exits 2 without writing anything."
```

---

### Task 6: Precision audit, gate, and documentation

**Files:**
- Create: `scripts/audit_reg_edges.py`
- Test: `tests/test_audit_reg_edges.py`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: `sebi_rag.stats.clopper_pearson_ci(successes, n, *, confidence=0.95) -> ProportionCI` (fields `point`, `lo`, `hi`, `n`, `successes`, `confidence`, `method`)
- Produces: `stratified_sample(edges, n, seed) -> list[dict]`, `score(labels: dict[str, bool]) -> ProportionCI`, `main(argv) -> int`

- [ ] **Step 1: Write the failing test**

Create `tests/test_audit_reg_edges.py`:

```python
"""Sampling + scoring for the regulation-edge precision audit."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_reg_edges as A  # noqa: E402

TIERS = ("subject_line", "powers_clause", "body_text")


def _edges(per_tier=40):
    out = []
    for t in TIERS:
        for i in range(per_tier):
            out.append({"source": f"C/{t}/{i}", "target": f"reg-{i}-2020",
                        "relation": "cites", "confidence": "explicit_text",
                        "evidence": t, "clause": None, "count": 1})
    return out


def test_sample_size_is_respected():
    assert len(A.stratified_sample(_edges(), 50, seed=7)) == 50


def test_sample_covers_every_evidence_tier():
    got = {e["evidence"] for e in A.stratified_sample(_edges(), 50, seed=7)}
    assert got == set(TIERS)


def test_sample_is_deterministic_for_a_fixed_seed():
    a = A.stratified_sample(_edges(), 50, seed=7)
    b = A.stratified_sample(_edges(), 50, seed=7)
    assert [e["source"] for e in a] == [e["source"] for e in b]


def test_sample_smaller_than_requested_returns_everything():
    small = _edges(per_tier=3)
    assert len(A.stratified_sample(small, 50, seed=7)) == len(small)


def test_sample_has_no_duplicates():
    s = A.stratified_sample(_edges(), 50, seed=7)
    assert len({(e["source"], e["target"]) for e in s}) == len(s)


def test_score_computes_a_clopper_pearson_interval():
    ci = A.score({"a": True, "b": True, "c": False, "d": True})
    assert ci.successes == 3 and ci.n == 4
    assert ci.method == "clopper-pearson"
    assert 0.0 <= ci.lo <= ci.point <= ci.hi <= 1.0


def test_score_with_no_labels_is_vacuous_not_an_error():
    ci = A.score({})
    assert ci.n == 0 and ci.lo == 0.0 and ci.hi == 1.0


def test_perfect_precision_lower_bound_is_below_one():
    ci = A.score({str(i): True for i in range(50)})
    assert ci.point == 1.0
    assert ci.lo < 1.0  # Clopper-Pearson is conservative by design
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_audit_reg_edges.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'audit_reg_edges'`

- [ ] **Step 3: Write the implementation**

Create `scripts/audit_reg_edges.py`:

```python
"""Precision audit for circular -> regulation edges (spec 2026-07-23 §7).

Emits a hand-labelling worksheet stratified by evidence tier, then scores a
completed worksheet with a Clopper-Pearson exact interval. Precision, not
coverage, is the gate: a regex that over-matches would score perfectly on
coverage alone.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/audit_reg_edges.py            # emit
    PYTHONPATH=src .venv/bin/python scripts/audit_reg_edges.py --score \\
        reports/reg_edge_audit.md
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.reg_citations import EVIDENCE_TIERS  # noqa: E402
from sebi_rag.stats import ProportionCI, clopper_pearson_ci  # noqa: E402

LABEL_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*\[([ xX])\]", re.M)


def stratified_sample(edges: list[dict], n: int, seed: int) -> list[dict]:
    """Up to `n` edges, spread as evenly as possible across evidence tiers.

    Tiers with fewer edges than their share give up the remainder to the others,
    so a corpus with only two populated tiers still yields a full sample.
    """
    rng = random.Random(seed)
    buckets = {t: [e for e in edges if e.get("evidence") == t]
               for t in EVIDENCE_TIERS}
    for b in buckets.values():
        rng.shuffle(b)
    out, quota = [], n
    tiers = sorted(EVIDENCE_TIERS, key=lambda t: len(buckets[t]))
    for i, t in enumerate(tiers):
        share = min(len(buckets[t]), -(-quota // (len(tiers) - i)))
        out.extend(buckets[t][:share])
        quota -= share
    return out


def score(labels: dict[str, bool]) -> ProportionCI:
    """Clopper-Pearson interval over hand-labelled edge correctness."""
    values = list(labels.values())
    return clopper_pearson_ci(sum(1 for v in values if v), len(values))


def _emit(edges: list[dict], circ_by_num: dict[str, dict],
          reg_by_id: dict[str, dict], n: int, seed: int, out: Path) -> None:
    sample = stratified_sample(edges, n, seed)
    lines = [
        "# Regulation edge precision audit",
        "",
        f"Sample: {len(sample)} of {len(edges)} edges, stratified by evidence "
        f"tier, seed={seed}.",
        "",
        "Mark `[x]` when the circular genuinely cites that regulation. "
        "Then run:",
        "",
        "    PYTHONPATH=src .venv/bin/python scripts/audit_reg_edges.py "
        f"--score {out}",
        "",
        "| edge | evidence / clause | correct |",
        "| --- | --- | --- |",
    ]
    for e in sample:
        subj = (circ_by_num.get(e["source"], {}).get("subject", "") or "")[:70]
        title = (reg_by_id.get(e["target"], {}).get("title", e["target"]))[:70]
        lines.append(
            f"| {e['source']} -> {e['target']} | {e['evidence']}"
            f"{' / ' + e['clause'] if e.get('clause') else ''} | [ ] |")
        lines.append(f"| <sub>{subj}</sub> | <sub>{title}</sub> | |")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote worksheet with {len(sample)} edges to {out}")
    print("Label each row, then re-run with --score.")


def _score_file(path: Path) -> int:
    labels = {}
    for i, m in enumerate(LABEL_RE.finditer(path.read_text(encoding="utf-8"))):
        if "->" not in m.group(1):
            continue
        labels[f"{i}:{m.group(1)}"] = m.group(3).lower() == "x"
    ci = score(labels)
    print(f"Labelled: {ci.n}   correct: {ci.successes}")
    print(f"Precision: {ci.point:.1%}  "
          f"95% CI [{ci.lo:.1%}, {ci.hi:.1%}]  ({ci.method})")
    passed = ci.n > 0 and ci.point >= 0.95
    print("GATE: " + ("PASS" if passed else "FAIL (target >= 95%)"))
    return 0 if passed else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--edges", default="data/manifests/regulation_edges.jsonl")
    ap.add_argument("--corpus", default="data/corpus/circulars.jsonl")
    ap.add_argument("--regulations", default="data/corpus/regulations.jsonl")
    ap.add_argument("--out", default="reports/reg_edge_audit.md")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260723)
    ap.add_argument("--score", metavar="WORKSHEET", default=None)
    args = ap.parse_args(argv)

    if args.score:
        return _score_file(Path(args.score))

    def _load(p):
        return [json.loads(x) for x in Path(p).read_text(
            encoding="utf-8").splitlines() if x.strip()]

    edges = _load(args.edges)
    circ = {c["circular_number"]: c for c in _load(args.corpus)}
    regs = {r["reg_id"]: r for r in _load(args.regulations)}
    _emit(edges, circ, regs, args.n, args.seed, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_audit_reg_edges.py -q`
Expected: PASS — 8 passed

- [ ] **Step 5: Capture the pre-change eval baseline**

Do this **before** running the real pipeline, so the no-op proof has something to compare against.

```bash
mkdir -p /tmp/regbaseline
cp -r eval/runs /tmp/regbaseline/runs-before
git rev-parse HEAD > /tmp/regbaseline/commit.txt
```

- [ ] **Step 6: Run the real pipeline end to end**

```bash
make scrape-regs      # ~5 min at rate 3; writes data/corpus/regulations.jsonl
make reg-edges        # offline; seconds
make audit-regs       # emits reports/reg_edge_audit.md
```

Expected from `make reg-edges`: `Edges: <N> across <M> circulars`, where `M` is at least 500 (the measured 70.9% baseline), and a `regulatory_basis_status` histogram containing all four keys.

- [ ] **Step 7: Run the gate**

Gate 1 — suite green:

```bash
make test
```
Expected: all tests pass, including the ~79 new ones.

Gate 2 — coverage. Record from the `make reg-edges` output: edge count, linked-circular count and share, and the top unresolved names from `reports/unresolved_regulations.txt`. If a high-count name is a real regulation, add it to `REGULATION_ALIASES` in `src/sebi_rag/regulations.py` (or `REG_SUCCESSION` in `reg_lineage.py` if it is repealed), re-run `make reg-edges`, and note the change.

Gate 3 — precision. Hand-label all rows in `reports/reg_edge_audit.md`, then:

```bash
PYTHONPATH=src .venv/bin/python scripts/audit_reg_edges.py --score reports/reg_edge_audit.md
```
Expected: `GATE: PASS` with precision ≥ 95%. On FAIL, extend `REGULATION_ALIASES` or raise `FUZZY_THRESHOLD`, re-run `make reg-edges`, and re-audit with a **new seed**.

Gate 4 — no-op proof:

```bash
make eval-asof
make bench-retrieval
diff -r /tmp/regbaseline/runs-before eval/runs && echo "NO-OP CONFIRMED"
```
Expected: `NO-OP CONFIRMED` (allowing for run-directory timestamps — compare the metric files, not the directory names). On any metric difference, a `CircularMeta` field leaked; move it to the record and re-run.

- [ ] **Step 8: Update CLAUDE.md**

In the Quick Start command block, add after the `make verify-master` line:

```
make scrape-regs      # Fetch SEBI regulations (Updated List, sid=1&ssid=3)
make reg-edges        # Build circular->regulation edges + annotate corpus (offline)
make audit-regs       # Precision audit of regulation edges (sample + Clopper-Pearson CI)
```

In the Architecture table, add after the `lineage.py` row:

```
| `regulations.py` | Regulation identity, alias table, name resolution |
| `reg_citations.py` | Regulation citations extracted from circular text |
| `reg_lineage.py` | Circular→regulation edges + `regulatory_basis_status` annotation |
```

And add this paragraph directly under the "⚠️ Two parallel code paths" section:

```markdown
### ⚠️ Never add fields to `CircularMeta`

`hierarchical_chunk()` does `meta=asdict(meta)` (`segment.py:131`), so a new
`CircularMeta` field lands in all 34,883 chunk payloads and mutates the
persisted index. Additive per-circular metadata goes on the corpus JSONL record
only — see `master_meta.annotate_master_fields` and
`reg_lineage.annotate_regulation_fields`.
```

- [ ] **Step 9: Write the results report**

Create `reports/2026-07-23-regulation-cross-reference-results.md` recording, with the actual numbers from Steps 6-7: regulations scraped, stubs synthesised (repealed vs unknown), edges built, linked-circular count and share, the `regulatory_basis_status` histogram, the count of circulars that are `validity_status: current` but `regulatory_basis_status: repealed_basis` (the headline signal — the spec's measured estimate was 39), audit precision with its Clopper-Pearson CI, and the no-op diff result.

- [ ] **Step 10: Commit**

```bash
git add scripts/audit_reg_edges.py tests/test_audit_reg_edges.py CLAUDE.md \
        data/corpus/regulations.jsonl data/manifests/regulation_edges.jsonl \
        reports/reg_edge_audit.md reports/unresolved_regulations.txt \
        reports/2026-07-23-regulation-cross-reference-results.md
git commit -m "feat(regulations): precision audit, gate results, docs

Stratified 50-edge audit with a Clopper-Pearson interval; coverage and
unresolved-name report; eval_asof and bench_retrieval confirmed unchanged.
CLAUDE.md gains the three make targets, the three new modules, and an
explicit warning against adding fields to CircularMeta."
```

Note: `data/corpus/circulars.jsonl` is 37 MB and is rewritten in place by `make reg-edges`. Check `git status` before committing — if the repo does not track it (see `.gitignore`), leave it out of the commit.

---

## Self-Review

**Spec coverage:**

| Spec section | Task |
|---|---|
| §3.1 index-invariance constraint | Task 4 (`test_annotation_adds_no_circular_meta_field`), Task 6 Gate 4, CLAUDE.md warning |
| §3.2 `regulations.jsonl` schema | Task 1 (`RegulationMeta`), Task 3 (`_record`) |
| §3.3 `regulation_edges.jsonl` schema | Task 4 (`build_regulation_edges`) |
| §3.4 three additive circular fields | Task 4 (`annotate_regulation_fields`) |
| §3.5 module table | Tasks 1–6, one module each |
| §3.6 alias table seed (13 rows) | Task 1 (`REGULATION_ALIASES`, all 13 plus 8 extras) |
| §3.7 `REG_SUCCESSION` (7 rows) | Task 4 (all 7, verbatim) |
| §4 data flow + Makefile targets | Tasks 3, 5 |
| §5 error handling (7 rows) | Task 3 (no-PDF, non-PDF payload, empty listing), Task 4 (unresolved, unknown-status), Task 5 (missing file, idempotency) |
| §6 testing | Tasks 1–6, ~79 tests |
| §7 gate (4 items) | Task 6 Steps 5–7 |
| §8 open question: `primary_regulation` tie-break | Task 4 (`test_primary_regulation_prefers_evidence_tier_over_count`) |
| §8 open question: fuzzy threshold | Task 1 (`FUZZY_THRESHOLD = 0.8`, decoy tests, documented in the module docstring) |

No gaps.

**Type consistency:** `reg_id` is a function in `regulations.py` and a dict *key* everywhere else — no collision, since `reg_lineage.py` imports the function by name and reads `r["reg_id"]` from dicts. `EVIDENCE_TIERS` is defined once in `reg_citations.py` and imported by both `reg_lineage.py` and `audit_reg_edges.py`. `resolve_regulation` returns `tuple[str | None, str]` in Task 1 and is unpacked as two values in Tasks 4. `build_regulation_edges` returns `tuple[list[dict], dict]` and is unpacked as two values in Tasks 4 and 5. `ProportionCI` fields used in Task 6 (`point`, `lo`, `hi`, `n`, `successes`, `method`) all exist in `src/sebi_rag/stats.py`.

**Placeholder scan:** every code step contains complete, runnable code. No TBD, no "similar to Task N", no "add error handling".

**One deliberate deviation from the spec, flagged:** the spec's §3.6 alias table lists 13 rows; Task 1 ships 21. The 8 extras (`dp`/1996, `fpi`/2014, `icdr`/2009, `ilds`/2008, `ncs`/2021, `ra`/2014, `ia`/2013, `mf`/2026) are year-variants and acronyms of regulations the spec already names elsewhere — in §3.7 `REG_SUCCESSION` or §1's citation table. Adding them costs nothing and avoids a guaranteed first-run gate failure.
