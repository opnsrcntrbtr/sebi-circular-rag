# Master Circular Coverage: Ingestion, Schema, and Verification — Design

Date: 2026-07-13
Status: Approved design (brainstormed with Fable 5; execution is model-agnostic — see §5)
Branch context: `spaces` (post as-of fixes, 199ff2e)

## Goal

Ingest **all** SEBI master circulars listed on the official Master Circulars
listing (https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=6&smid=0,
~135 documents as of 2026-07-13) into the existing pipeline; enhance the
schema/metadata for master circulars; and build a permanent
**coverage-verification module** that statistically confirms, against the live
listing, what is ingested and processed in `data/` and `dist/datasets/`.

## Ground truth (measured 2026-07-13)

- `scripts/scrape_sebi.py` already supports `--section master-circulars`
  (`SECTIONS = {"circulars": (1, 7, 0), "master-circulars": (1, 6, 0)}`), but
  the Make target only ever ran the regular `circulars` section.
- Corpus: 603 records; 43 classified `MASTER_CIRCULAR`; only **25** records
  have a `/legal/master-circulars/` source_url. ≈110 master circulars missing.
- Metadata layer (`src/sebi_rag/metadata.py`) has locked rules: additive
  fields only; only `explicit_text` edges affect `validity_status`.

## 1. Coverage-verification module (build FIRST)

New `src/sebi_rag/verify_master.py` (library) + `scripts/verify_master.py`
(CLI), exposed as `make verify-master`.

- **Manifest fetch:** reuse `scrape_sebi.py` paging/session logic to walk the
  live ssid=6 listing into `data/manifests/master_circulars.jsonl` — one row
  per listed master circular: title, listing date, detail URL, PDF URL,
  department (parsed from title where present).
- **Diff engine:** join manifest ↔ `data/corpus/circulars.jsonl` (primary key
  source_url; fallback PDF sha256, then circular_number) ↔
  `dist/datasets/corpus`. Every manifest row gets exactly one status:
  `ingested_ok | fetched_not_ingested | parse_failed | missing |
  unfetchable`, plus corpus-side `extra_in_corpus` for master-typed records
  absent from the listing.
- **Statistical summary:** write `reports/master_coverage.json` (machine) and
  `reports/master_coverage.md` (human): totals, coverage %, breakdowns by
  year / department / circular_type / validity_status, per-PDF validation
  flags (parse success, non-degenerate text, issue date extracted, circular
  number extracted), and the explicit gap list.
- **Offline-testable:** listing-page HTML fixtures under `tests/fixtures/`;
  network is touched only in real runs (CLI flag or env guard).

## 2. Ingestion to 100%

- New `make scrape-master` → `scripts/scrape_sebi.py --section
  master-circulars --max 200 --rate 3` (MAX overridable).
- Iterate loop: scrape → `make verify-master` → fix parser failures (very
  large PDFs, scanned PDFs via existing `--ocr`, format variants) → repeat
  until every manifest row is `ingested_ok` or documented `unfetchable`
  (dead link on SEBI's side, with reason recorded). Coverage claim is then
  "100% of retrievable documents".
- Every ingested PDF must pass the degenerate-chunk guard (regression lesson
  from the nominee-count bug): no heading-only chunks admitted.

## 3. Schema / metadata enhancements (additive only)

Per the locked migration rules in `metadata.py` — new fields are additive;
existing fields never change meaning; only `explicit_text` edges affect
`validity_status`.

- **Identity fields** on corpus records:
  - `is_master: bool` (true iff `circular_type == "MASTER_CIRCULAR"`),
  - `master_series: str | null` — normalized topic (e.g. "Mutual Funds"),
    derived from the subject line via a small maintained rule table,
  - `master_edition: int | null` — issue year,
  - `previous_edition: str | null` — circular_number of the prior edition in
    the same series, linked chronologically.
- **Consolidation lineage:** parser for the rescission appendix ("List of
  circulars superseded/rescinded") in master-circular PDFs. Emits
  `supersession_edges` rows with `relation: "consolidates"`; confidence is
  `explicit_text` when the appendix supplies circular numbers/dates,
  `inferred` otherwise. Feeds the existing tiered-edge model unchanged.
- Runs inside the existing annotate stage of `make reindex`.

## 4. Downstream propagation

1. `make reindex` (FAISS/BM25 rebuild).
2. Full offline test suite (baseline 212 tests) + golden as-of eval (13/13
   gate) must stay green.
3. `make export-datasets` — all 6 configs regenerate; corpus/lineage/
   supersession configs pick up new records and consolidates edges.
4. Push to HF Hub: `opnsrcntrbtrian/sebi-circulars` (dataset) and the index
   repo, per the existing dataset-push runbook.
5. Redeploy Space `opnsrcntrbtrian/sebi-circular-rag-demo`; live smoke test:
   one master-circular question, the nominee regression question, one as-of
   query.
6. Final `make verify-master` run whose report also covers
   `dist/datasets/corpus` — this closes the loop and is the artifact that
   "confirms with statistical summary".

## 5. Execution model: model-agnostic handoff

This spec and its implementation plan are the handoff artifacts. Execution in
later sessions may be performed by **any** model or harness — Claude models,
local models (MLX/Ollama), or other tools — no Claude model is mandatorily
allocated to any task.

- The implementation plan (written next, under `docs/superpowers/plans/`)
  must be self-contained: each task carries its own context, exact commands,
  file paths, and verifiable acceptance criteria, so an executor needs only
  the plan document plus the repo.
- Deterministic steps (scraping, reindex, exports, evals, HF pushes) are
  plain scripts/Make targets — no LLM required.
- Validation is embedded in each task as runnable commands and expected
  outputs (tests green, eval gate 13/13, verify-master coverage numbers) —
  correctness is checked by the harness, not by a particular model's review.
- Fable involvement: at most one **minimal final review at the very end**
  (whole-branch diff + final coverage report), and only if the user requests
  it. No intermediate Fable review gates.

## 6. Error handling & testing

- Scraper: per-item retry with rate backoff; hard failures become manifest
  statuses (`unfetchable` with reason), never crash the run.
- Verification module unit tests: manifest HTML parsing, diff-engine status
  assignment, report aggregation — all on fixtures.
- Metadata tests: series/edition derivation table cases; appendix parser on
  fixtures extracted from 3–4 real master circulars (different departments
  and eras, including one pre-2015 format).
- Regression: existing offline suite and 13/13 as-of eval must pass at every
  task boundary.

## Out of scope

- Regular-circulars reconciliation (only master circulars this effort).
- Chapter-aware chunk hierarchy and listing-page department capture as
  authoritative metadata (both offered and not selected).
- Any change to existing `supersession_status` semantics.
