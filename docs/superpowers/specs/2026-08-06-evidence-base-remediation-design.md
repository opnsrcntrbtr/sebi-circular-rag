# Spec A — Evidence Base Remediation

**Date:** 2026-08-06
**Status:** Design approved, not implemented
**Blocks:** `2026-08-06-autoresearch-loop-design.md` (Spec B). No intervention may run in the loop until A5 completes.

## 1. Problem

The intervention archive in `eval/runs/` does not describe the current system, and cannot be read by standard IR tooling. Four independent defects:

| # | Defect | Evidence |
|---|---|---|
| D1 | `run.trec` files are not valid TREC | Lines carry 15 whitespace-separated fields, not 6. `docid` is a chunk id whose middle segment is heading text containing spaces. `trec_eval` / `ir_measures` cannot parse them. |
| D2 | No qrels exist | `find eval -name "*qrel*"` returns nothing. Relevance judgments live only as `relevant_circulars` inside `golden_v7.jsonl`. No third party can re-score any run. |
| D3 | Archive spans 4 corpora and 3 eval sets | `corpus_sha256` has 4 distinct values across 26 runs; no run uses the current corpus `5f626dd9`. Cross-intervention ranking in `reports/ci_rescore.md` is invalid. |
| D4 | Label provenance is unexposed | `golden_v7.jsonl` rows carry no `label_source`. Labels derive from Claude, Qwen, Gemini and a human packet, but metrics pool them silently — inviting a circularity objection (LLM judgments evaluating an LLM retrieval system). |

D3 is knowable only because `results.json` already pins `corpus_sha256`, `golden_sha256` and `index_fingerprint`. The instrument was correct; nothing enforced it.

## 2. Non-goals

- Re-labelling or expanding `golden_v7`. Provenance is exposed, not changed.
- Any change to `CircularMeta` or `data/index/`. See `.claude/rules/circular-meta.md`.
- Any change to `*_spaces.py` or root `app.py`. See `.claude/rules/two-paths.md`.
- Building the loop. That is Spec B.

## 3. A1 — Valid TREC runfiles

### 3.1 Current chunk id grammar

```
<circular_id>#<heading_text>#<ordinal>
SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123#preamble#0
SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123#1. SEBI vide circular no. CIR/CFD/CMD/4/2015 dated September#1
```

`circular_id` contains `/` but no whitespace and no `#`. `heading_text` contains whitespace. `ordinal` is an integer.

### 3.2 Derived docid

```python
def chunk_docid(chunk_id: str) -> str:
    """Whitespace-free, collision-free TREC docid."""
    circular = chunk_id.split("#", 1)[0]
    ordinal = chunk_id.rsplit("#", 1)[1]
    return f"{circular}#{ordinal}"
```

`(circular, ordinal)` is unique per chunk, so the mapping is injective. Reversibility is preserved by a sidecar rather than by encoding.

### 3.3 Emitted artifacts per run

| File | Format | Purpose |
|---|---|---|
| `run.chunk.trec` | `qid Q0 docid rank score tag` | Chunk granularity, 6 fields exactly |
| `run.doc.trec` | same | Deduped to circular level: best (lowest) rank per circular, ranks renumbered 1..n |
| `docids.tsv` | `docid\tchunk_id` | Full-fidelity reverse mapping |

`run.doc.trec` exists because relevance judgments are circular-level (`relevant_circulars`) while retrieval is chunk-level. Scoring a chunk-level run against circular-level qrels is a category error; `run.doc.trec` is the artifact `trec_eval` should consume.

### 3.4 Legacy conversion

**The recovery logic already exists.** `benchmark.read_trec_run` (`src/sebi_rag/benchmark.py:395`) implements exactly this, and its docstring already documents the defect: *"the archived runfiles are NOT valid TREC and trec_eval cannot read them."* It is covered by `tests/test_rescore.py::TestReadTrecRun::test_recovers_doc_ids_containing_spaces`.

```
parts[0]     = qid
parts[1]     = "Q0"
parts[2:-3]  = chunk_id fragments (rejoined with " ")
parts[-3:]   = rank, score, tag
```

So D1 is a *known, documented, already-parsed* defect — what is missing is emitting a standards-compliant artifact, not the ability to read the old one. `scripts/autoresearch/convert_legacy_runs.py` is a thin driver over the existing reader: `read_trec_run` → `write_run_chunk` / `write_run_doc` / `write_docids`, for each of the 31 run directories. The original `run.trec` is retained unmodified as the historical record.

**Precondition:** recovery is valid only while `qid` and `tag` contain no whitespace. `read_trec_run` already raises `ValueError` on lines with fewer than 6 fields; the converter additionally asserts the whitespace precondition per line and aborts that file rather than writing a corrupt result.

**Naming caution:** `benchmark.write_qrels` (`:375`) already exists but emits **BEIR-style TSV** with a `query-id\tcorpus-id\tscore` header, consumed by `export_benchmark`. It is not TREC qrels format. §4's writer is a separate function and must not shadow or replace it.

## 4. A2 — qrels emission

`scripts/autoresearch/emit_qrels.py` writes `eval/qrels/<eval_set>.qrels`:

```
<qid> 0 <circular_id> 1
```

- One line per `(row.id, circular)` pair drawn from `relevant_circulars`.
- Binary relevance. Graded relevance is not available in `golden_v7` and is not invented.
- Rows with `abstain: true` contribute no qrels lines. They are scored by `abstention_accuracy`, not by retrieval metrics. The count of excluded rows is written to a header comment.
- Generated per eval set, keyed by `golden_sha256`, so a qrels file can never silently apply to a different golden set.

## 5. A3 — Metric parity test

Assert that the project's internal metrics equal the standard implementations on identical inputs.

```python
# tests/test_trec_parity.py
pytest.importorskip("ir_measures", reason="optional; run `make trec-parity` after installing")
```

| Internal (`src/sebi_rag/eval.py`) | Standard |
|---|---|
| `recall_at_k(ranked, relevant, 10)` | `R@10` |
| `mrr(ranked, relevant)` | `RR` |
| `ndcg_at_k(ranked, relevant, 10)` | `nDCG@10` |

Tolerance `1e-9`. Inputs are `run.doc.trec` + the matching qrels for the same frame.

**Dependency policy:** `ir_measures` is absent from the current environment and is added as an optional extra, not a runtime dependency. The test skips cleanly when it is missing so `make test` stays green at 667 passing; `make trec-parity` installs-or-fails loudly. This keeps the offline suite dependency-light while making the parity claim checkable on demand.

If a metric disagrees, the internal implementation is the thing that changes — the standard defines the term.

## 6. A4 — Epochs and frames

### 6.1 Definitions

- **Epoch** — a corpus snapshot, keyed by `corpus_sha256`. The corpus drifts uncontrolled (n8n `1_corpus_refresh.json`, weekly Sun 02:00), so it is the thing that needs a controlled identity.
- **Eval set** — a golden file, keyed by `golden_sha256`. Deliberately versioned, not drifting.
- **Frame** — the pair `(epoch, eval_set)`. **Two runs are comparable if and only if they share a frame.**

Epoch is *not* keyed on the pair. `golden`, `probes`, and `asof` are different instruments applied to the same corpus; folding them into the epoch key would wrongly split a single corpus into three.

### 6.2 Registry

`eval/epochs/epochs.jsonl`, append-only:

```json
{"epoch":"E4","opened":"2026-08-06","corpus_sha256":"5f626dd9a881f30884beb9fac972d710ea09151271964f8d546824f110121d8d",
 "corpus_rows":724,"chunks":78523,"status":"open","baseline_runs":{"3e44dfb9...":"eval/runs/E4-baseline-golden"}}
```

`baseline_runs` maps `golden_sha256` → baseline run path, so a frame is baselined independently of its siblings.

### 6.3 Backfill of the existing archive

`scripts/autoresearch/backfill_epochs.py` reads `results.json` from each run and assigns epochs. Nothing is discarded.

| Epoch | `corpus_sha256` | Runs |
|---|---|---|
| E1 | `4083518f` | ft-golden, ft-probes, iv2-golden, iv2-probes |
| E2 | `913e762c` | iv6–iv11 (golden + probes), iv-final, fp16_retrieval, asof-fp16 |
| E3 | `8971de0f` | baseline_retrieval |
| E4 | `5f626dd9` | asof-baseline — **current** |

26 of 31 run directories carry `results.json`. The remaining 5 (incl. `pool-sweep`, `iv11-splade-only-*`) are recorded as `epoch: null` and are excluded from all comparisons.

Eval sets observed: `f01d8779` (golden_v6), `99a9da66` (probes), `00999d42` (as-of), `3e44dfb9` (golden_v7, current — used by no intervention run).

### 6.4 Comparability guard

`rescore_runs.py` gains a hard refusal: any paired comparison whose two runs differ in `epoch` or `golden_sha256` raises rather than reporting a number.

Effect on the existing record:
- Each individual A/B pair stays valid — control and treatment always shared a frame. The provenance discipline held.
- The cross-intervention ranking implied by the `ci_rescore.md` summary table becomes unavailable, correctly. iv2 (E1) and iv8–iv11 (E2) were never measured on the same corpus.

## 7. A5 — Establish frame E4 / golden_v7

Baseline the current system on the current corpus and the current eval set — a frame in which **no intervention has ever been measured**.

| Run | Config |
|---|---|
| `E4-baseline-golden` | HEAD defaults, `citation_scorer_enabled=true`, margin 0.35 |
| `E4-iv2-golden` | glossary expansion + clause folding |
| `E4-iv8-golden` | HyDE third leg |
| `E4-iv9-golden` | contextual headers (full corpus) |
| `E4-iv10-golden` | targeted headers sidecar |
| `E4-iv11-golden` | SPLADE third leg |

All are config-toggleable, so none requires a reindex except those whose sidecar artifacts are stale.

Scope: `golden_v7` answerable rows, **n=219** (260 total − 41 abstain), versus n=45 in the legacy archive. Expected CI narrowing ≈ √(219/45) ≈ 2.2×.

`reports/ci_rescore.md` is regenerated for frame E4/golden_v7 only, with legacy frames retained in an appendix under an explicit "not comparable across frames" heading.

**Expected outcome to plan for:** iv2 is currently marked ADOPTED on `+2.2, p=1.000, 1 query changed` at n=45 on corpus `4083518f`, two epochs stale. It may not reproduce on E4. Retracting an adoption is a valid and expected result of this phase, not a failure of it.

## 8. A6 — Label provenance stratification

### 8.1 What already exists

`label_source` is **already present on all 260 rows**, but as free-text prose with 14 distinct values, and `review_status` is `adjudicated` for all 260 (zero information). Observed distribution:

| Existing `label_source` | n |
|---|---|
| `claude (draft adjudication)` | 95 |
| `v7-draft-2026-07` | 82 |
| `claude (abstain validation)` | 26 |
| `golden_v5` | 20 |
| `golden_v5 (promoted golden_v5)` | 13 |
| `claude (arbitration resolved: title_direct \| body_paraphrase)` | 14 |
| `corrected: actually SEBI {SAST,LODR,FVCI,IPEF,—} topic` | 7 |
| `external-flip` | 2 |
| `claude (qwen failed to find governing)` | 1 |

The genuinely human-labelled subset is approximately 7–9 rows. Where the 30 human labels from the `packet_human/` ingest landed is not recoverable from this field and is a question for the audit (§8.2).

### 8.2 Audit before classification

A read-only audit script reports, for each of the 14 values, how many rows each annotation artifact (`votes.jsonl`, `gemini/`, `qwen/`, `packet_human/`, `arbitration_queue.jsonl`) can account for. Classification rules are written against the audit's findings, not assumed.

### 8.3 Controlled vocabulary

A **new** field `label_tier` is added; free-text `label_source` is preserved unchanged as the provenance trail.

| `label_tier` | Meaning |
|---|---|
| `human` | Human-authored label or correction, no model input |
| `arbitrated` | Model disagreement resolved through `arbitration_queue.jsonl` |
| `model_single` | One model annotator, no corroboration |
| `inherited_v5` | Carried from golden_v5; provenance not recorded at the time |
| `draft_seeded` | Seeded draft row (`v7-draft-2026-07`) |
| `unknown` | Audit could not account for the row |

`golden_v7.jsonl` is the eval set, **not** `CircularMeta` — no chunk payload, no index mutation, constraint in `.claude/rules/circular-meta.md` respected.

### 8.4 Reporting rule

**Tiered reporting with no designated primary set.** Every metric is reported broken down by `label_tier` with its `n`, alongside the pooled n=260 figure. No tier is promoted to headline.

Designating the human tier as primary is rejected on the evidence: at n≈9 it has no power, which is the exact defect this programme exists to remove. Publications state plainly that human-only labelling is n≈9 and make no headline claim from it. `agreement.py` gains a `--by-tier` mode reporting κ and AC1 across tiers wherever two tiers overlap on the same rows.

## 9. Components

```
src/sebi_rag/autoresearch/
  __init__.py
  trecio.py      # chunk_docid, write_run_chunk, write_run_doc, write_docids,
                 # read_legacy_run, write_qrels
  epoch.py       # EpochRegistry, Frame, frame_of(results_json), assert_comparable
scripts/autoresearch/
  convert_legacy_runs.py
  emit_qrels.py
  backfill_epochs.py
  stratify_labels.py
```

Makefile targets: `qrels`, `trec-parity`, `epoch-status`, `epoch-backfill`.

## 10. Error handling

| Condition | Behaviour |
|---|---|
| Legacy line with whitespace in `qid` or `tag` | Abort that file, report path + line number, leave original untouched |
| `results.json` missing `corpus_sha256` | Run assigned `epoch: null`, excluded from comparisons, listed in backfill report |
| qrels requested for an eval set with no `relevant_circulars` | Fail loudly; do not emit an empty qrels file |
| `ir_measures` absent | Parity test skips with actionable message; `make trec-parity` fails |
| Cross-frame comparison attempted | `IncomparableFramesError` naming both frames |

## 11. Testing

TDD. All offline, no network, no model weights, inside `make test`:

| Test | Asserts |
|---|---|
| `test_chunk_docid_is_whitespace_free` | Over a sample of real chunk ids from `data/index/chunks.jsonl` |
| `test_chunk_docid_injective` | No two distinct chunk ids map to one docid |
| `test_run_chunk_trec_has_six_fields` | Every emitted line splits to exactly 6 |
| `test_legacy_roundtrip` | `read_legacy_run` recovers the exact chunk ids of a fixture |
| `test_run_doc_dedupes_to_best_rank` | Circular appearing at ranks 3 and 7 emits once at 3 |
| `test_qrels_match_golden` | qrels line set equals expansion of `relevant_circulars` |
| `test_qrels_exclude_abstain_rows` | No qrels lines for `abstain: true` |
| `test_frame_equality` | Same corpus + same golden ⇒ comparable; either differing ⇒ raises |
| `test_backfill_assigns_known_epochs` | E1–E4 assignment on fixture metadata |
| `test_parity_recall_mrr_ndcg` | vs `ir_measures`, skipped if absent |

## 12. Acceptance

1. All 31 run directories carry `run.chunk.trec`, `run.doc.trec`, `docids.tsv`, or an explicit exclusion reason.
2. `eval/qrels/` contains a qrels file per observed eval set.
3. `make trec-parity` passes with `ir_measures` installed.
4. `eval/epochs/epochs.jsonl` lists E1–E4 with run assignments.
5. `rescore_runs.py` raises on cross-frame comparison; a regression test proves it.
6. Frame E4/golden_v7 has a baseline plus the five re-run interventions, with `ci_rescore.md` regenerated at n=219.
7. Every `golden_v7` row carries `label_tier` from the controlled vocabulary; free-text `label_source` is unchanged; `agreement.py --by-tier` reports κ and AC1; the audit report records tier counts.
8. `make test` still passes at ≥667.

> **Scope note (2026-08-06):** §7 in this plan's execution covers the E4 **baseline only**. The five intervention re-runs (iv2, iv8, iv9, iv10, iv11) are deferred to a follow-up plan, because they are long-running measurement jobs with no code deliverable and iv9/iv11 may require rebuilding stale sidecars.
