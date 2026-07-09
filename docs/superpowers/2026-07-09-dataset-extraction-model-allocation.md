# Dataset Extraction Implementation — Model Allocation Plan

**Date:** 2026-07-09
**Goal:** Allocate the ~4–5 dataset-extraction TDD tasks across Fable 5, Sonnet 5, and Haiku 4.5 for optimal token efficiency across sessions while maintaining quality and speed.

**Context:** This work completes the SEBI RAG publication cycle (scraper alignment ✅ + dataset extraction 🎯). Tasks are clean, scoped, and build on validated code patterns from semantic-routing work.

---

## Task Breakdown & Model Allocation

### Task 1: Export pipeline scaffold + corpus config builder
**Complexity:** Medium (data transformation, schema design, validation reuse)
**Estimated scope:** 
- `scripts/export_datasets.py` skeleton + `make export-datasets` target
- Corpus builder: circulars.jsonl → Parquet/JSONL with null handling, date parsing, provenance rewrite
- Unit tests: schema conformance, row count parity, invariant re-check via `validate_corpus`

**Token characteristics:**
- Heavy re-reading of existing `validate_corpus.py` patterns to reuse
- File I/O boilerplate (polars/pandas schema definition)
- Test fixture setup for multiple formats

**Allocation:** **Fable 5** ⭐
- **Why:** Fable excels at boilerplate scaffold + schema design work. The corpus builder is deterministic, reuses existing patterns, and has clear success criteria (row/column count, format output). Fable will author the main skeleton efficiently.
- **Token savings:** Avoids Sonnet's verbosity for straightforward data-transform code; keeps the scaffold lean.
- **Output:** Working export script with corpus config + passing tests, committed.

---

### Task 2: Chunks + lineage + eval configs
**Complexity:** Medium-High (three similar-but-distinct configs, metadata flattening, edge-list deriving)
**Estimated scope:**
- Chunks builder: flatten nested `meta` into top-level columns, strip context header, dedup
- Lineage builder: derive forward edges only (dedupe superseded_by/amended_by inverses), resolve `target_in_corpus` flag
- Eval builder: v6 schema validation, BEIR/TREC emission, run metadata assembly
- Unit tests: per-config schema, row parity, BEIR qrels shape, TREC runfile format

**Token characteristics:**
- Complex nested-to-flat transformations (chunks metadata)
- Graph reasoning (lineage deduping, inverse derivation)
- Multiple output formats (BEIR, TREC, JSON) with strict schemas
- Test fixtures larger than Task 1

**Allocation:** **Sonnet 5** ⭐⭐
- **Why:** Sonnet's reasoning and code synthesis excel at multi-config handling, format diversity, and complex schema reasoning. Lineage derivation (inverses, target_in_corpus lookup across 603 records) and BEIR/TREC emission benefit from Sonnet's precision.
- **Trade:** Sonnet costs more tokens, but this task's complexity (3 builders × 3 formats) justifies it. Fable's output feeds Sonnet's input (export script architecture), so Sonnet can focus on builders, not scaffold.
- **Output:** Chunks, lineage, eval configs fully tested; all four formats emitted and validated.

---

### Task 3: Transformed task datasets (citation-normalization + supersession-pairs)
**Complexity:** High (label generation, sampling, span extraction, cross-validation)
**Estimated scope:**
- Citation-normalization: re-run `ingest_pdf.py` reference-extraction logic over corpus text, emit raw→normalized pairs + context windows + format family
- Supersession-pairs: positive sampling from lineage edges, negative sampling from same-dept non-linked pairs at 2:1 ratio, label round-trip verification
- Unit tests: pair validity (no cross-contamination), label consistency, format family coverage, sampling distribution (2:1 negative ratio)

**Token characteristics:**
- Logic-heavy (reference extraction loop, bipartite sampling algorithm)
- Cross-validation (do labels round-trip through normalize_circular_number?)
- Test fixtures larger (36k+ chunk iterations, 1.4k edges × negative sample expansion)
- Requires understanding ingest_pdf extraction strategies

**Allocation:** **Sonnet 5** ⭐⭐
- **Why:** Label generation requires semantic reasoning about what makes a valid citation span, how to handle edge cases (abbreviated refs, cross-references), and sampling fairness. Sonnet is strongest at this reasoning + correctness.
- **Justification:** Although expensive, this task is the most novel and correctness-critical. Labels are the dataset's value proposition. Fable's efficiency is less important than Sonnet's quality here.
- **Dependency:** Depends on Task 2 (lineage builder outputs), so sequence is Fable → Sonnet Tasks 2&3 in parallel or Task 2 first.
- **Output:** Citation-normalization (36k+ pairs, format families validated) and supersession-pairs (~4–5k, 2:1 negatives) both tested and committed.

---

### Task 4: Dataset cards + platform packaging
**Complexity:** Low-Medium (boilerplate, compliance checklist, multi-platform paths)
**Estimated scope:**
- HF dataset card (README.md): YAML configs per dataset, "Source Data" section, licensing/disclaimers, model cards for transforms
- Kaggle metadata.json: title, description, file list, license selection
- Zenodo submission pack: tarball manifest, DOI placeholder, metadata JSON
- AIKosh submission pack: CSV structure, licensing doc, EOI template
- Card linting tests: YAML parses, required sections present, no TBD placeholders

**Token characteristics:**
- Mostly templated (copy structure, fill fields)
- Lightweight validation (section presence, YAML syntax)
- No complex logic or cross-validation
- Well-understood patterns (same card structure across 4 platforms)

**Allocation:** **Haiku 4.5** ⭐
- **Why:** Haiku is perfect for templated, low-logic card generation. The work is straightforward: fill in known structure, validate presence of sections, emit per-platform variants. No reasoning required.
- **Token savings:** Haiku's speed + low context overhead makes this fast and cheap. Frees Sonnet from boilerplate.
- **Output:** All four platform cards generated + linting tests pass; AIKosh pack ready for user's manual registration.

---

### Task 5: Integration + live export test
**Complexity:** Low (orchestration, smoke test, sanity check)
**Estimated scope:**
- Wire Tasks 1–4 into a single `make export-datasets` target
- Run against the live 603-record corpus + all configs
- Verify output files exist, have correct row counts, checksums, no validation errors
- Document exported file inventory + version tag (v2026.07)

**Token characteristics:**
- Minimal new code (mostly invoking existing builders)
- Integration testing (orchestration, not feature testing)
- File I/O spot-checks

**Allocation:** **Haiku 4.5** ⭐
- **Why:** Pure orchestration + smoke testing. Haiku can wire the Makefile, run the export, and verify output without heavy reasoning.
- **Dependency:** Depends on all Tasks 1–4 being complete and tested.
- **Output:** Full export run succeeds; dataset files ready for upload in subsequent sessions.

---

## Execution Sequence

```
Session 1 (Fable 5):
  └─ Task 1 (corpus config) ✅

Session 2 (Sonnet 5):
  ├─ Task 2 (chunks + lineage + eval)
  └─ Task 3 (citation-norm + supersession-pairs)
     [can run in parallel if isolated, else Task 2 → Task 3]

Session 3 (Haiku 4.5):
  ├─ Task 4 (cards + packaging)
  └─ Task 5 (integration + smoke test)
```

**Why this order:**
1. **Fable first:** Establishes the export script architecture; Task 2&3 inherit from it.
2. **Sonnet next:** Complex transformations and label generation depend on export script; use Sonnet's reasoning fully.
3. **Haiku last:** Cards and integration are pure boilerplate; no blocking dependencies within Haiku's scope.

---

## Token Cost Estimates

| Task | Model | Tokens (approx) | Rationale |
|------|-------|---|---|
| 1 | Fable 5 | 8–12k | Scaffold + one config, straightforward patterns |
| 2 | Sonnet 5 | 20–25k | Three builders, multiple formats, complex schema reasoning |
| 3 | Sonnet 5 | 25–30k | Label generation, sampling, cross-validation logic |
| 4 | Haiku 4.5 | 6–10k | Templated cards, repetitive structure |
| 5 | Haiku 4.5 | 4–6k | Orchestration + smoke test, minimal new code |
| **Total** | — | **63–83k** | ~30% savings vs. all-Sonnet (~110–130k) |

**Savings breakdown:**
- Using Fable for Task 1 saves ~8–10k (vs. Sonnet boilerplate)
- Using Haiku for Tasks 4&5 saves ~10–12k (vs. Sonnet verbosity on templated work)
- **Net efficiency gain:** ~18–22% token reduction, while maintaining quality via Sonnet's reasoning on high-value tasks

---

## Quality Checkpoints

- **Task 1 gate:** Corpus config row/column count matches source; full test suite passes
- **Task 2 gate:** ✅ chunks/lineage/eval emit correct row counts (36603/1434/56); full suite green
- **Task 3 gate:** ✅ citation pairs round-trip through normalize_circular_number (verified: `normalized_circular_number == normalize_circular_number(raw_reference)` for all rows); supersession pairs hit the requested 2:1 negative ratio exactly (854 = 427×2); no linked pair appears among the negatives (tested)
- **Task 4 gate:** All cards lint (YAML valid, required sections present); platform-specific fields populated
- **Task 5 gate:** Full export run completes without error; output files exist; checksums stable; v2026.07 version tag recorded

---

## Handoff Notes for Each Model

### For Fable 5 (Task 1): ✅ DONE 2026-07-09 (commit c9878d1, branch `dataset-export`)
- Delivered: `scripts/export_datasets.py` — validate → transform → emit pipeline; functional style (`build_corpus_rows()` pure transform + `export_corpus()` orchestrator + shared `_emit()` writer) rather than a class, matching repo idiom
- Corpus config: Parquet + JSONL under `dist/datasets/corpus/` + `manifest.json` (source sha256, snapshot version from max issue_date → `v2026.07`); provenance → `extraction_date`; empty strings → null; refuses export on `validate_corpus` violations
- Live run verified: 603 rows, 6.5 MB Parquet, schema = `CORPUS_SCHEMA`; `make export-datasets` target added; `dist/` gitignored
- Tests: `tests/test_export_datasets.py` (5 offline tests); full suite 105 passed
- Sonnet note: extend `_emit()` + `manifest["configs"]` for each new config; reuse `CORPUS_SCHEMA` list-of-columns pattern per config

### For Sonnet 5 (Tasks 2 & 3): ✅ DONE 2026-07-09 (commits 2cfc921, 77b9dff, branch `dataset-export`)
- Delivered as functions, not classes (kept Task 1's idiom): `build_chunk_rows`, `build_lineage_rows`, `build_eval_rows`, `build_citation_pairs`, `build_supersession_pairs`, each a pure transform tested independently of I/O
- Manifest is now cumulative: `_update_manifest()` merges each config's entry into one shared `dist/datasets/manifest.json` instead of each export overwriting it (Task 1's `export_corpus` was refactored onto this helper too — its standalone test still passes unchanged)
- `_emit()` hardened to write a typed empty Parquet table when a config produces zero rows (was a `KeyError` crash before — real corpora can have zero cross-references)
- Live row counts (differ from the design spec's rough estimates — **use these actual numbers in the cards, not the spec's guesses**):
  - `chunks`: 36,603 · `lineage`: 1,434 edges (948 unique targets, only 427 in-corpus) · `eval`: 56
  - `citation-normalization`: **2,951** (spec guessed "36k+") — family split 2175 new-standard / 765 old-standard / 11 dept-order-2026
  - `supersession-pairs`: **1,281** (spec guessed "~4-5k") — 408 supersedes / 19 amends / 854 unrelated (2:1 negative ratio, seeded/deterministic); positives are gated on both lineage endpoints being in the 603-record corpus, which only 427/1434 edges satisfy — this is the real bottleneck, not text availability
- Full test suite: 122 passed (17 new tests across Tasks 2–3)
- **Known data-quality caveat to flag in the card** (pre-existing, not introduced by this work): some master-circular `subject` fields are oversized (up to ~2900 chars — a body-text capture artifact in `ingest_pdf.py`'s `_subject()`), visible in both `corpus` and `supersession-pairs` configs. Note it next to the existing `issuing_department`-UNKNOWN-for-124-records caveat; do not attempt to fix the parser as part of Task 4/5.
- Haiku note: `X.CORPUS_SCHEMA`, `X.CHUNKS_SCHEMA`, `X.LINEAGE_SCHEMA`, `X.EVAL_SCHEMA`, `X.CITATION_SCHEMA`, `X.SUPERSESSION_SCHEMA` are the six column-order lists to build per-config card tables/dtype docs from; `X.export_all(...)` is the single entry point `make export-datasets` already calls

### For Haiku 4.5 (Tasks 4 & 5):
- Inherit: Directory structure and row counts from Tasks 1–3 (six configs already exporting cleanly under `dist/datasets/<config>/{name}.jsonl,.parquet`, plus one shared `manifest.json`)
- Task 4: Generate `dist/datasets/README.md` (HF card, one YAML config block per dataset config using the six `*_SCHEMA` lists above for dtypes), `metadata.json` (Kaggle), `ZENODO_SUBMISSION_PACK/`, `AIKOSH_SUBMISSION_PACK/`. Include the two data-quality caveats noted above (department-UNKNOWN, oversized subjects) plus the citation-normalization/supersession-pairs actual row counts (not the spec's estimates)
- Task 5: `make export-datasets` orchestration already exists and works (Tasks 1–3 wired it); Task 5's job is narrower now — smoke-test the full run is idempotent/reproducible (same manifest checksums on a second run against unchanged source data) and confirm the `v2026.07` version tag is consistent across all six configs' manifest entries
- Tests: Card YAML validation, file presence, checksums, row counts
- Commit messages: "feat: dataset cards for HF/Kaggle/Zenodo/AIKosh" + "feat: integration and live export verification"

---

## Risk Mitigation

1. **Fable's Task 1 doesn't cover all edge cases** → Sonnet reviews Task 1's export skeleton at the start of Task 2; refine if needed. (Low risk — Fable's boilerplate is usually solid.)
2. **Sonnet's Task 2/3 generates too much data** → Test with a small slice (e.g., 50 circulars) first; scale up after validation.
3. **Haiku's cards miss platform-specific requirements** → Include platform docs (HF dataset card spec, Kaggle metadata schema, Zenodo submission guide) as inline links in the task prompts.
4. **Checksum/version stability** → All tasks should record source checksums (corpus.jsonl, index/lineage.json, golden v5) in the manifest; makes incremental updates safe.

---

## Outcome

**This session:**
- ✅ Semantic-routing alignment (scraper + recovery) — complete, merged, tested

**Next sessions (model-allocated):**
- **Fable 5:** Export scaffold (Task 1)
- **Sonnet 5:** Configs + transforms (Tasks 2–3)
- **Haiku 4.5:** Cards + integration (Tasks 4–5)

**Final outcome:** Six dataset configs (corpus, chunks, lineage, eval, citation-norm, supersession-pairs) exported, tested, packaged, and ready for upload to HF/Kaggle/Zenodo/AIKosh. Complete publication workflow documented.

**Estimated session time:**
- Fable: 20–30 min (Task 1)
- Sonnet: 40–60 min (Tasks 2–3 in parallel or sequence)
- Haiku: 15–20 min (Tasks 4–5)
