# Next Steps Plan — 2026-08-14

**Status:** Design phase. Three workstreams in sequence:
1. Citation precision improvement (margin sweep)
2. Corpus expansion (scrape + rebuild)
3. Test coverage expansion

---

## Workstream 1: Citation Precision — Margin Sweep (0.35→0.45)

### Background
- B' selective citations active at margin 0.35 (chosen 2026-08-04)
- Full sweep data exists at `reports/b-prime-margin-sweep.md` showing the precision↔recall curve
- Current production: MLX generator, B' ON at margin 0.35
- Gate floors (2026-08-12, MLX generator): citation_recall 0.8124, citation_precision 0.1571
- Observed (MLX, B' @ 0.35): citation_recall 0.863, citation_precision 0.186

### Hypothesis
Loosening margin from 0.35 to ~0.45 recovers citation_recall toward the sweep's 0.8082 mean while accepting a small precision drop (expected ~0.19→~0.18). The net effect is a wider citation set with slightly lower per-citation precision but higher recall — beneficial for legal queries where missing a governing circular is worse than an extra tangential citation.

### Preregistered Analysis Plan

**Scope:** golden_v7.jsonl (n=260 adjudicated rows), scored via `score_row` under MLX generator.

**Endpoints:**
- PRIMARY: citation_recall (mean over adjudicated rows) — must improve or stay flat
- GUARDRAIL: citation_precision (mean) — must stay ≥ 0.1571 (armed floor)
- GUARDRAIL: abstention_accuracy — must stay ≥ 0.9335
- Descriptive: recall_at_k, ndcg_at_10

**Decision rule:**
| Outcome | Decision |
|---|---|
| recall improves/stays flat AND precision ≥ 0.1571 | Adopt the margin that maximizes recall while keeping precision ≥ floor + 0.02 (safety cushion) |
| precision < 0.1571 | Reject — guardrail breached |
| recall drops > 2pp | Reject — no benefit from loosening |

**Margin grid:** 0.35, 0.40, 0.45 (one pipeline pass per margin via capture-once script)

**Adoption threshold:** Must rescue ≥ 5 rows (citation_recall improvement of ~0.02) with precision staying above floor + 0.02 cushion (≥ 0.1771).

### Test Validation (TDD)
**Pre-condition:** All 792 existing tests must pass before sweep begins.
**Post-condition:** All 792 + new tests pass after adoption.

| Test File | Existing Tests to Verify | New Tests Required |
|---|---|---|
| `test_gate.py` | `test_hybrid_gate_overrides_judge_when_rerank_top_high`, `test_subject_sim_judge_separates_by_subject` | 3 new: boundary at 0.85, just below 0.85, no-judge inert |
| `test_selective_citations.py` | `test_keeps_only_contexts_within_margin_of_top`, `test_min_keep_widens_a_collapsed_selection` | 2 new: margin=0.45 behavior, all-below-margin+min_keep=1 |
| `test_non_sebi_filter.py` | (existing) | 3 new: "sebi+rbi" query, substring match ("arbitration"), empty string |
| `test_golden_v7_gate.py` | `test_citation_precision_is_gated_after_B_prime` | 0 (existing validates gate) |
| `test_settings.py` | `test_citation_scorer_enabled_env_on` | 0 (existing validates settings) |

**Validation sequence:**
1. `make test` — all 792 pass (baseline)
2. Add new tests → run only new tests first (`pytest -k "hybrid_boundary|margin_045|non_sebi_edge"`)
3. Run full suite → 792 + N pass
4. If margin adopted: re-run `make eval-asof` to confirm gate floors still pass

### Documentation Sync
| Doc | Change Required | Owner |
|---|---|---|
| `config.toml` | Update `citation_margin = 0.35` → new value (if adopted) | Auto |
| `docs/status.md` | Record sweep results, decision, new margin value | Manual |
| `docs/project_context.md` | Update §12 prerequisites if gate floors change | Manual |
### Implementation
- Modify `scripts/analysis/sweep_citation_margin_capture.py` to sweep 0.35–0.45
- Run under MLX generator (same as gate derivation)
- If criteria met: update `config.toml`, re-arm gate, commit

---

## Workstream 2: Corpus Expansion

### Background
- Current corpus: 724 circulars, 78,523 chunks
- Last index rebuild: 2026-08-14 (publish_hf.py --rebuild-index)
- SEBI publishes new circulars regularly

### Plan
1. Run `make scrape` (default MAX=50) to fetch newer circulars
2. Run `make scrape-master` (default MAX_MASTER=10) for master circulars
3. Validate corpus: `make validate-corpus`
4. Rebuild index: `make reindex` (or `make index`)
5. Re-run golden_v7 evaluation to measure impact on recall/precision
6. If metrics improve: push updated index + datasets to HF

### Acceptance Criteria
- Corpus grows by ≥ 10 new circulars (verifiable via corpus JSONL row count)
- All existing gate floors still pass after rebuild
- HF repos updated
### Test Validation (TDD)
**Pre-condition:** All 792 existing tests pass before scraping.
**Post-condition:** All 792 + new corpus-validation tests pass after rebuild.

| Test File | Existing Tests to Verify | New Tests Required |
|---|---|---|
| `test_validate_corpus.py` | All existing validation tests | 0 (existing validates corpus integrity) |
| `test_golden_v7_gate.py` | All gate tests (recall, precision, abstention floors) | 0 (gate must still pass) |
| `test_build_index_out_dir.py` | Index output structure tests | 0 (index format unchanged) |

**Validation sequence:**
1. `make test` — all 792 pass (pre-scan baseline)
2. Scrape + rebuild → `make validate-corpus` passes
3. `make eval-asof` — gate floors still pass (critical: corpus growth must not degrade quality)
4. If any floor breached → rollback, investigate

### Documentation Sync
| Doc | Change Required | Owner |
|---|---|---|
| `docs/status.md` | Update corpus row count, chunk count, index size | Manual |
| `README.md` | No change (corpus size is operational detail) | — |
---

## Workstream 3: Test Coverage Expansion

### Gap Analysis
Current tests (792) cover generate.py well for the happy path but have gaps:

**Missing tests:**
1. **Hybrid gate edge cases:**
   - Judge abstains, rerank_top exactly at 0.85 boundary (should pass)
   - Judge abstains, rerank_top just below 0.85 (should abstain)
   - No judge + hybrid gate (hybrid should be inert when no judge present)

2. **Subject sim judge edge cases:**
   - subject_sim exactly at 0.42 boundary (should pass)
   - section_score exactly at 0.60 boundary (should pass)
   - Both subject_sim and section_score below thresholds but rerank_top high (hybrid rescue)

3. **Citation scorer edge cases:**
   - Margin 0.45 (new proposed value) — verify select_citations behavior
   - All contexts below margin, min_keep=1 (should keep top)
   - Citation scorer disabled — verify all contexts cited

4. **Non-SEBI domain edge cases:**
   - Query contains "sebi" AND "rbi" — should NOT abstain (SEBI intent wins)
   - Query contains substring match of keyword (e.g., "arbitration" matching "rbi") — should NOT abstain
   - Query is empty string

5. **Faithfulness edge cases:**
   - Answer cites context not in contexts list — faithfulness should flag
   - Answer has no bracket citations at all

### Implementation
- Add tests to `tests/test_gate.py` (hybrid gate, subject sim)
- Add tests to `tests/test_selective_citations.py` (margin edge cases)
- Add tests to `tests/test_non_sebi_filter.py` (edge cases)
### Test Validation (TDD)
**Pre-condition:** All 792 existing tests pass before adding new tests.
**Post-condition:** All 792 + N tests pass after implementation.

| Test File | Existing Tests to Verify | New Tests Required |
|---|---|---|
| `test_gate.py` | All existing gate tests (12) | 6 new: hybrid boundary, no-judge inert, subject_sim boundary, section_score boundary, hybrid rescue |
| `test_selective_citations.py` | All existing citation tests (10) | 3 new: margin=0.45, all-below-margin+min_keep, scorer_disabled |
| `test_non_sebi_filter.py` | All existing filter tests (5) | 3 new: sebi+rbi query, substring match, empty string |
| `tests/test_canary_generator.py` | All existing canary tests (4) | 0 (canary is operational, not functional) |

**Validation sequence:**
1. `make test` — all 792 pass (baseline)
2. Add new tests → run only new tests first (`pytest -k "hybrid_boundary|margin_045|non_sebi_edge"`)
3. Run full suite → 792 + N pass (all must pass)
4. No regression: any existing test that fails is a blocker

### Documentation Sync
| Doc | Change Required | Owner |
|---|---|---|
| `docs/status.md` | Update test count (792 → 792+N), note new coverage areas | Manual |
| `README.md` | No change (test count is operational detail) | — |
---

## Execution Order & Dependencies

```
Workstream 1 (Margin Sweep) — standalone, ~40 min
    ↓
Workstream 2 (Corpus Expansion) — depends on Workstream 1 being stable
    ↓
Workstream 3 (Test Coverage) — standalone, can run anytime
```

### Final Validation Gate
After all three workstreams complete:
1. `make test` — 792 + N pass (no regressions)
2. `make eval-asof` — all gate floors still pass
3. `make validate-corpus` — corpus integrity verified
4. All documentation synced (status.md, project_context.md if needed)
**Total estimated time:** ~1 hour (mostly waiting for MLX generation)
