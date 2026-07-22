# SEBI Regulations Cross-Reference Layer — Design

**Date:** 2026-07-23
**Status:** Approved for planning
**Source:** https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=3&smid=0

## 1. Problem

The corpus holds 705 circulars (531 `CIRCULAR`, 130 `MASTER_CIRCULAR`, 44 other).
Supersession is tracked circular-to-circular only. Regulations — the statutory
instruments circulars are issued under — are absent, so three things are
currently impossible:

1. Answering "which circulars operate under the LODR Regulations" at all.
2. Detecting that a circular is stale because its *regulation* was repealed,
   not because a later circular superseded it.
3. Anchoring `master_series` to an authoritative entity list rather than to 21
   hand-written subject regexes (29 of 130 master circulars match none).

### Measured justification

Against `data/corpus/circulars.jsonl` (705 records, measured 2026-07-22):

| Signal | Count | Share |
|---|---|---|
| Circulars naming ≥1 regulation by title | 500 | 70.9% |
| Circulars citing a clause ("regulation 30(2)") | 514 | 72.9% |
| Distinct regulation titles cited (raw, unnormalised) | 173 | — |
| `master_series` values mapping ~1:1 to a regulation | 16 of 18 | — |
| `current` circulars citing ≥1 regulation | 236 | — |
| …of those, citing **only** regulations absent from the in-force list | 39 | 16.5% |

The 39 are the headline: `validity_status` today derives solely from
`explicit_text` circular→circular edges, so a circular reads as `current` while
the regulation it was issued under has been repealed. The most-cited regulation
in the entire corpus — SEBI (Mutual Funds) Regulations, **1996**, 634 mentions —
was replaced by the 2026 edition. Stock Brokers 1992 → 2026, D&P 1996 → 2018 and
RTA 1993 → 2025 follow the same pattern.

### Source characterisation

The listing (`sid=1&ssid=3&smid=0`) returns **42 in-force regulations on a single
page with no pagination** — unlike circulars, which need the `doDirect` POST
pagination in `scripts/scrape_sebi.py`. Detail pages embed the PDF with the same
`<iframe src='../../../web/?file=…/sebi_data/attachdocs/<mon-yyyy>/<stem>.pdf'>`
viewer that `extract_pdf_urls()` already resolves, so the fetch layer is reused
unchanged. PDFs are larger than circulars (FPI Regs 2019 = 847 KB vs ~100 KB
typical); 42 documents ≈ 30–60 MB total.

Each regulation is a **consolidated living document** ("[Last amended on July 07,
2026]"), not a dated issuance. It therefore has no `circular_number`, no
`issue_date`, and exactly one current row per regulation — a different identity
model from circulars, which is why regulations get their own corpus file rather
than sharing `circulars.jsonl`.

## 2. Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | **Linking layer only.** Regulation text is not chunked, embedded, or indexed in this phase. | Keeps FAISS/BM25/reranker/abstention untouched, so the 0.956 recall baseline and the 10/10 as-of result need no re-gate. Indexing is a separate spec. |
| D2 | **Repealed regulations become stub records** synthesised from corpus citations, with no text and a hand-maintained successor table. | `showHistory()` lives in external JS under `/js`, which SEBI's robots.txt disallows and this project honours. Stubs recover the repeal signal without scraping a disallowed path. |
| D3 | **New additive field `regulatory_basis_status`;** `validity_status` is not modified. | The 2026-07-12 locked metadata rule ("validity from `explicit_text` circular edges only") stands. Additive means no eval movement. |
| D4 | **Document-level edges; clause captured as an unvalidated string.** | Full staleness and topic-linking value now; the clause string becomes verifiable when regulation text is indexed, without re-parsing 705 documents. |
| D5 | **Explicit acronym table + fuzzy matching for spelling drift.** | Acronyms have near-zero token overlap with their titles and are structurally unfuzzy-matchable — `PIT` (48 citations) and `LODR` (34) would fail or mis-match. Same "extend the table, surfaced by a coverage report" loop as `MASTER_SERIES_RULES`. |
| D6 | **Gate = edge-precision audit + no-op proof.** | Recall@k cannot gate a change that does not touch retrieval. |

### Non-goals

Explicitly out of scope for this spec, deferred to Phase 2:

- Chunking, embedding, or indexing regulation text.
- Any change to `/query` request or response, `src/sebi_rag/ui.py`, or the
  Spaces modules (`api_spaces.py`, `corpus_spaces.py`, `generate_spaces.py`,
  root `app.py`).
- Re-anchoring `MASTER_SERIES_RULES` to the regulation entity list.
- Validating clause numbers against regulation text.

## 3. Architecture

### 3.1 Index-invariance constraint

`hierarchical_chunk()` sets `meta=asdict(meta)` on every chunk
(`src/sebi_rag/segment.py:131`), so any field added to `CircularMeta` propagates
into all 34,883 chunk payloads and mutates the persisted index.

**The three new circular fields are therefore written to the corpus JSONL record
only, never to `CircularMeta`.** This follows the established precedent:
`is_master`, `master_series`, `master_edition` and `previous_edition` are all set
on the record by `annotate_master_fields()` (`src/sebi_rag/master_meta.py:66-69`)
and are absent from the `CircularMeta` dataclass. Honouring it makes the
index-invariance half of the gate true by construction, not by inspection.

### 3.2 `data/corpus/regulations.jsonl`

One record per regulation:

```json
{
  "reg_id": "mutual-funds-2026",
  "title": "Securities and Exchange Board of India (Mutual Funds) Regulations, 2026",
  "short_name": "Mutual Funds",
  "year": 2026,
  "status": "in_force",
  "last_amended": "2026-07-07",
  "source_url": "https://www.sebi.gov.in/legal/regulations/jul-2026/…_1234.html",
  "pdf_url": "https://www.sebi.gov.in/sebi_data/attachdocs/jul-2026/1784270676009.pdf",
  "pdf_sha256": "…",
  "pdf_path": "data/raw/regulations/1784270676009.pdf",
  "aliases": ["MF", "MFs", "Mutual Fund"],
  "supersedes_reg": ["mutual-funds-1996"],
  "superseded_by_reg": null,
  "provenance": "SEBI Updated List, fetched 2026-07-23",
  "text": ""
}
```

- `reg_id` — deterministic slug: `slugify(short_name) + "-" + year`. Stable
  across re-scrapes; it is the edge target and the join key.
- `status` — `in_force` | `repealed` | `unknown`.
- `text` — reserved, always `""` in this phase.
- Repealed stubs use the identical shape with `status: "repealed"`, null
  `source_url`/`pdf_url`/`pdf_sha256`/`pdf_path`, and
  `provenance: "Inferred from corpus citations; not on SEBI Updated List"`.

### 3.3 `data/manifests/regulation_edges.jsonl`

Reuses the tiered-edge vocabulary already established by `consolidation_edges()`
(`src/sebi_rag/master_meta.py:121-124`):

```json
{
  "source": "SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123",
  "target": "listing-obligations-and-disclosure-requirements-2015",
  "relation": "cites",
  "confidence": "explicit_text",
  "evidence": "subject_line",
  "clause": "30",
  "count": 12
}
```

- `relation` — `cites` only. A bare mention does not license a stronger claim
  such as `issued_under`; precision is carried by `evidence` instead.
- `confidence` — `explicit_text` when the regulation title was matched exactly or
  via the alias table; `inferred` when resolved by fuzzy match.
- `evidence` — precedence order `subject_line` > `powers_clause` > `body_text`.
  `powers_clause` means the citation falls within a sentence matching
  `/in exercise of the powers conferred/i`.
- `clause` — nullable. Populated only when a `regulation <n>` reference and the
  regulation title occur in the **same sentence**. Never validated in this phase.
- `count` — occurrences of that regulation in that circular, used for tie-breaks.

One edge per (circular, regulation) pair. Where a circular cites the same
regulation several times, the edge carries the highest-precedence `evidence` tier
observed, the `clause` from that same highest-tier occurrence (null if that
occurrence had none, even when a lower-tier occurrence did), and `count` as the
total across all occurrences.

### 3.4 Additive circular record fields

| Field | Type | Meaning |
|---|---|---|
| `regulations` | `list[str]` | Resolved `reg_id`s, ordered by `count` descending |
| `primary_regulation` | `str \| null` | Highest `evidence` tier, tie-broken by `count`, then by `reg_id` for determinism |
| `regulatory_basis_status` | `str` | `current` \| `repealed_basis` \| `mixed` \| `unknown` |

`regulatory_basis_status` derivation:

- no resolved regulations → `unknown`
- all resolved regulations `in_force` → `current`
- all resolved regulations `repealed` → `repealed_basis`
- otherwise → `mixed`

### 3.5 Modules

| File | Purpose | Depends on |
|---|---|---|
| `src/sebi_rag/regulations.py` | `RegulationMeta` dataclass, `reg_id()` slug, `REGULATION_ALIASES`, `resolve_regulation()`, `derive_regulatory_basis()` | stdlib only |
| `src/sebi_rag/reg_citations.py` | `CITATION_RE`, `Citation`, `extract_citations(subject, text)` | stdlib only |
| `src/sebi_rag/reg_lineage.py` | `REG_SUCCESSION`, `synthesise_repealed_stubs()`, `build_regulation_edges()`, `annotate_regulation_fields()` | `regulations`, `reg_citations` |
| `scripts/scrape_regulations.py` | Listing → detail → PDF → `regulations.jsonl` | `scrape_sebi.fetch/extract_pdf_urls/looks_like_pdf` |
| `scripts/build_reg_edges.py` | Offline: corpus + regulations → edges + annotations | `reg_lineage` |
| `scripts/audit_reg_edges.py` | Stratified sample → precision worksheet + CI | `stats.clopper_pearson_ci` |

Three source modules rather than one because extraction (text → raw citation),
resolution (raw name → canonical entity) and graph construction are separately
testable with disjoint test surfaces — mirroring the existing `metadata.py` /
`master_meta.py` / `lineage.py` split. None of them import `torch`,
`transformers`, `faiss` or any model, so the whole layer stays inside the
`not integration` test suite.

`scripts/scrape_regulations.py` imports its HTTP primitives from
`scripts/scrape_sebi.py` unchanged; no edit to `scrape_sebi.py` is required.
Listing discovery is a single GET — the `doDirect` pagination path is not used.

### 3.6 Alias table seed

Observed acronym citation forms with counts, to seed `REGULATION_ALIASES`:

| Alias | Count | Canonical `reg_id` |
|---|---|---|
| `PIT` | 48 | `prohibition-of-insider-trading-2015` |
| `MF` (1996) | 38 | `mutual-funds-1996` (repealed stub) |
| `LODR` | 34 | `listing-obligations-and-disclosure-requirements-2015` |
| `D&P` | 33 | `depositories-and-participants-2018` |
| `AIF` | 22 | `alternative-investment-funds-2012` |
| `SBEB` | 12 | `share-based-employee-benefits-and-sweat-equity-2021` |
| `FPI` | 10 | `foreign-portfolio-investors-2019` |
| `ICDR` | 6 | `issue-of-capital-and-disclosure-requirements-2018` |
| `IPEF` | 4 | `investor-protection-and-education-fund-2009` |
| `SAST` | 3 | `substantial-acquisition-of-shares-and-takeovers-2011` |
| `CRA` | 3 | `credit-rating-agencies-1999` |
| `PMS` | 2 | `portfolio-managers-2020` |
| `FVCI` | 1 | `foreign-venture-capital-investors-2000` |

Aliases are keyed on `(alias, year)`, not alias alone — `MF 1996` and `MF 2026`
are different regulations, as are `ICDR 2009` and `ICDR 2018`.

Fuzzy matching handles the residual spelling drift (`Mutual Fund` singular,
`Takeover` vs `Takeovers`, `Depositories Participants` with the conjunction
dropped). The acceptance threshold is set empirically during implementation
against the observed 173 variants and recorded in the module docstring; it is not
fixed here.

### 3.7 `REG_SUCCESSION` table

Hand-maintained repeal chains, one entry per superseded regulation, seeded from
the measured unmatched set:

```
mutual-funds-1996                    -> mutual-funds-2026
stock-brokers-1992                   -> stock-brokers-2026
depositories-and-participants-1996   -> depositories-and-participants-2018
registrars-to-an-issue-and-share-transfer-agents-1993
                                     -> registrars-to-an-issue-and-share-transfer-agents-2025
issue-and-listing-of-debt-securities-2008
                                     -> issue-and-listing-of-non-convertible-securities-2021
issue-of-capital-and-disclosure-requirements-2009
                                     -> issue-of-capital-and-disclosure-requirements-2018
foreign-portfolio-investors-2014     -> foreign-portfolio-investors-2019
```

The table populates `supersedes_reg` and `superseded_by_reg` on the regulation
records; it produces no rows in `regulation_edges.jsonl`, which holds
circular→regulation edges only. Entries are maintainer assertions, not text
extractions, and the module docstring must say so. The table is extended from the
unresolved-name report; a stub with no successor entry is valid and simply has
`superseded_by_reg: null`.

## 4. Data flow

```
scripts/scrape_regulations.py
    GET listing (sid=1&ssid=3&smid=0)      -> 42 rows (title, url, last-amended)
    GET each detail page                   -> pdf_url via extract_pdf_urls()
    GET each pdf                           -> data/raw/regulations/*.pdf + .sha256
                                           -> data/corpus/regulations.jsonl

scripts/build_reg_edges.py                 (offline, idempotent, no network)
    load circulars.jsonl + regulations.jsonl
    reg_citations.extract_citations()      -> raw (name, year, clause, evidence)
    regulations.resolve_regulation()       -> reg_id | unresolved
    reg_lineage.synthesise_repealed_stubs()-> appends stubs to regulations.jsonl
    reg_lineage.build_regulation_edges()   -> data/manifests/regulation_edges.jsonl
    reg_lineage.annotate_regulation_fields()-> rewrites circulars.jsonl in place
                                           -> reports/unresolved_regulations.txt

scripts/audit_reg_edges.py
    stratified sample by evidence tier     -> reports/reg_edge_audit.md
```

Ordering: stubs must be synthesised before edges are built, because an edge may
target a stub. `build_reg_edges.py` is independent of `annotate`/`index` and does
not participate in `make reindex`.

Makefile targets — `reindex` is **unmodified**:

```make
scrape-regs:
	$(ENV) $(PY) scripts/scrape_regulations.py --rate 3
reg-edges:
	$(ENV) $(PY) scripts/build_reg_edges.py
audit-regs:
	$(ENV) $(PY) scripts/audit_reg_edges.py
```

## 5. Error handling

| Condition | Behaviour |
|---|---|
| Detail page yields no PDF | Record kept with null PDF fields; listing identity is sufficient. Run continues. |
| PDF URL returns an HTML error body | Rejected by `looks_like_pdf()`; record kept with null PDF fields; logged. |
| Listing returns 0 rows | Abort before writing, leaving `regulations.jsonl` untouched — never truncate a good file with an empty fetch. |
| Cited name resolves below fuzzy threshold | Left unresolved, appended to `reports/unresolved_regulations.txt` with its count. Never silently dropped. |
| `regulations.jsonl` missing | `build_reg_edges.py` exits with a clear message and a non-zero code; writes nothing. |
| `annotate_regulation_fields()` called twice | Returns 0 on the second call — same idempotency contract as `annotate_master_fields()`. |
| Regulation cited that is neither in-force nor in `REG_SUCCESSION` | Stub created with `status: "unknown"` and `superseded_by_reg: null`. A circular citing only such regulations gets `regulatory_basis_status: "unknown"`, never `repealed_basis`. |

The last row matters: absence from the Updated List is not by itself proof of
repeal, because the list is fetched at one point in time and the citation may be
a typo or an Act rather than a regulation. Only names with a `REG_SUCCESSION`
entry are marked `repealed`; the rest are `unknown`. This makes
`repealed_basis` a curated, defensible claim rather than an inference from
absence.

## 6. Testing

All offline (`not integration`) — no network, no model weights.

`tests/test_regulations.py`
- `reg_id()` slug is deterministic and stable for punctuation and case variants
- alias resolution: `PIT`/2015, `LODR`/2015, `D&P`/2018, `MF`/1996 vs `MF`/2026
- fuzzy accepts `Mutual Fund`→`mutual-funds-2026`, `Takeover`→`…-takeovers-2011`
- fuzzy rejects a below-threshold decoy (no false canonical assignment)
- `derive_regulatory_basis()` truth table: all four outcomes including `mixed`

`tests/test_reg_citations.py`
- title + year extraction from a realistic circular preamble
- clause captured when same-sentence; **not** captured when the clause number is
  in a different sentence from the title
- evidence tiering: `subject_line`, `powers_clause`, `body_text`
- multiple distinct regulations in one document produce distinct citations
- `count` aggregation across repeated mentions

`tests/test_reg_lineage.py`
- stub synthesis creates `mutual-funds-1996` with `superseded_by_reg: mutual-funds-2026`
- a cited name with no `REG_SUCCESSION` entry yields status `unknown`, not `repealed`
- edge dedupe: one edge per (circular, regulation), highest evidence tier wins
- `annotate_regulation_fields()` returns a change count, then 0 on re-run
- `primary_regulation` tie-break: evidence tier, then count, then `reg_id`
- annotated records do **not** gain any `CircularMeta` field (index-invariance)
- saved-HTML listing fixture parses to 42 rows with titles and last-amended dates
- missing `regulations.jsonl` produces a clean error, not a traceback

One `@pytest.mark.integration` test fetches the live listing and asserts ≥40 rows
with resolvable detail URLs.

## 7. Promotion gate

1. **Suite green** — `make test` passes, existing 339 tests plus the new ones.
2. **Coverage** — resolved share of the 500 citing circulars, reported with the
   full unresolved-name list ranked by citation count.
3. **Precision** — 50 edges sampled stratified by evidence tier, hand-labelled;
   precision ≥95% with a Clopper-Pearson 95% CI computed by the existing
   `sebi_rag.stats.clopper_pearson_ci`.
4. **No-op proof** — `make eval-asof` and `make bench-retrieval` outputs are
   byte-identical to the pre-change baseline. True by construction under §3.1,
   but asserted rather than assumed.

Results are written to `reports/`. Failing (3) means extending
`REGULATION_ALIASES` or raising the fuzzy threshold and re-auditing; failing (4)
means a `CircularMeta` field leaked and must be moved to the record.

## 8. Open questions

Both are empirical and resolve during implementation, not before:

- **`primary_regulation` tie-break.** The evidence-tier-then-count rule is
  untested against a circular that names one regulation in its subject line and
  another 40 times in its body. If the audit shows the rule picking the wrong
  regulation, the fallback is to leave `primary_regulation` null whenever the
  top two candidates share an evidence tier.
- **Fuzzy acceptance threshold.** Set against the observed 173 variants, chosen
  to admit `Mutual Fund`→`Mutual Funds` while rejecting cross-regulation
  confusions such as `Depositories and Participants` vs `Depositories`. The
  chosen value and the decoy set are recorded in the `regulations.py` docstring.
