# Dataset Card Accuracy: Root-Cause Fix + Correction — Design

Date: 2026-07-14
Status: Approved design

## Goal

`opnsrcntrbtrian/sebi-circulars`'s live HF dataset card (already pushed) and
this repo's `README.md` / `README-spaces.md` show stale numbers from before
the master-circular-coverage plan (603 circulars, 34,883 chunks, etc.)
against a corpus that is now 705 records / 77,859 chunks. Fix the root cause
so this can't silently drift again, correct every affected surface, and
repush/redeploy so the live artifacts match.

## Root cause

`scripts/export_datasets.py`'s four card-generator functions —
`build_hf_card`, `build_kaggle_metadata`, `build_zenodo_pack`,
`build_aikosh_pack` — each receive a `datasets: dict[str, dict]` parameter
already populated with correct live row counts
(`datasets[cfg]["rows"]`, read straight from `manifest.json`), but hardcode
the numbers into prose/table strings instead of using it:

- Row counts: `603`, `34,883`, `1,437`, `2,951`, `1,281` appear as literals
  at lines 432, 438–443, 458, 588–590, 616 of `build_hf_card` /
  `build_kaggle_metadata` / `build_zenodo_pack`.
- `issuing_department=UNKNOWN` count: hardcoded `"124/603"` (line 458, 543)
  — not derived from the corpus.
- Snapshot date: hardcoded `"2026-07-13"` (lines 430, 627).

Ground truth as of 2026-07-14:

| Metric | Old (hardcoded) | Correct (live) |
|---|---|---|
| corpus rows | 603 | 705 |
| chunks rows | 34,883 | 77,859 |
| lineage rows | 1,437 | 4,483 |
| eval rows | 56 | 56 (unchanged) |
| citation-normalization rows | 2,951 | 8,802 |
| supersession-pairs rows | 1,281 | 2,769 |
| `issuing_department=UNKNOWN` | 124/603 | 158/705 |
| corpus date range | "2021–2026" (README.md prose) | 2010-04-06 to 2026-07-07 |

## Fix

### 1. Parameterize the four card generators (`scripts/export_datasets.py`)

- Row-count table cells and prose sentences read from `datasets[cfg]["rows"]`
  (already passed in) instead of literals.
- Snapshot date computed as `dt.date.today().isoformat()` at the point
  `write_dataset_cards()` runs — reflects when the card was actually
  generated, no manual upkeep.
- Two new computed values threaded into `datasets` (or a sibling dict) by
  `write_dataset_cards()` before calling the builders:
  - `issuing_department_unknown_count` / `issuing_department_total` —
    counted from the corpus records already loaded for export.
  - `issue_date_min` / `issue_date_max` — min/max ISO `issue_date` across
    corpus records (skipping empty/non-ISO values, matching the pattern
    already used elsewhere in this codebase, e.g. `verify_master.py`'s
    `_ISO_RE`).
- Function signatures change minimally: `build_hf_card`,
  `build_kaggle_metadata`, `build_zenodo_pack`, `build_aikosh_pack` gain
  access to these two new computed fields via the existing `datasets` dict
  argument (added as a reserved key, e.g. `datasets["_stats"]`, so per-config
  entries keep their current shape and existing callers/tests aren't broken).

### 2. Regression test (`tests/test_dataset_cards.py`)

New test(s) asserting:
- Every row-count number in the generated `build_hf_card()` output string
  matches the corresponding `datasets[cfg]["rows"]` value passed in (parse
  the markdown table, compare against input — not a hardcoded expected
  literal, so it can't itself go stale).
- The UNKNOWN-department fraction and date range appearing in the card
  match values independently computed from a small fixture corpus in the
  test (not the real 705-record corpus — keeps the test offline/fast).
- Existing `test_dataset_cards.py` cases (already covering schema/format)
  continue to pass unmodified.

### 3. Regenerate + repush

- `make export-datasets` — regenerates `dist/datasets/README.md`,
  `metadata.json`, and the Kaggle/Zenodo/AIKOSH packs with correct live
  numbers.
- `make test` — offline suite green, including the new card-accuracy tests.
- Dry-run `python scripts/push_datasets.py` — confirm the upload plan.
- **Live push** `python scripts/push_datasets.py --yes` to
  `opnsrcntrbtrian/sebi-circulars` — pauses for explicit user confirmation
  before running (shared, hard-to-reverse action, same as the master-circular
  plan's precedent).

### 4. Hand-correct the two static docs + redeploy

- `README.md` (project root): Dataset Configurations table (all 6 row
  counts), the `**Corpus:**`-style prose line, the "Corpus spans 2021–2026"
  disclaimer (→ real min–max range), and the `issuing_department` UNKNOWN
  caveat (124/603 → 158/705) — all set to the values computed in step 1,
  not re-derived independently.
- `README-spaces.md`: already corrected locally in the prior session
  (77.9k chunks / 705 circulars line) but never deployed. Audit the rest of
  the file once more for any other stale numeric mention, then redeploy via
  `scripts/deploy_space.py --repo opnsrcntrbtrian/sebi-circular-rag-demo` so
  the live Space's README.md (pushed from this file) matches.
- No live smoke test needed for this pass — this is a docs-only Space
  redeploy (README content only, no code/index change), so the existing
  Task-10 smoke test from the master-circular plan remains the relevant
  functional verification and doesn't need re-running.

## Out of scope

- Kaggle/Zenodo/AIKOSH packs are fixed at the generator level (same
  parameterization) but not submitted/pushed to those platforms — no
  platform account exists for them yet in this project.
- No change to `manifest.json`'s generation (already correct — it reads
  straight from row counts, this bug was isolated to the prose/table
  builders).
- No change to the dataset's actual content/schema — this is purely a
  documentation-accuracy fix.

## Testing

- `tests/test_dataset_cards.py` — new assertions per "Regression test" above.
- `make test` full offline suite stays green.
- Manual verification after push: fetch the live
  `opnsrcntrbtrian/sebi-circulars` README.md and confirm it shows 705/77,859/
  4,483/8,802/2,769; fetch the live Space's README.md and confirm the
  corpus-count line matches `README-spaces.md`.
