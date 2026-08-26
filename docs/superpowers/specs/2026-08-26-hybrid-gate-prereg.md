# Preregistration — Hybrid Abstention Gate (cross-encoder OR override)

**Written before execution.** Decision rule in §3 and the not-permitted list in §4 are fixed as of
this document's commit. No arm has been run. Task per
`docs/superpowers/plans/2026-08-26-hybrid-gate-and-set-encoder.md` Task 1 (also
`.superpowers/sdd/2026-08-26-hybrid-gate-and-set-encoder/task-1-brief.md`), closing out the
2026-08-13 decision "pursue hybrid gate experiment for subject_gate rows only"
(`docs/status.md:1230`), never previously run.

Report/results artifact (not this doc): `reports/hybrid-gate-cohort-2026-08-26.json`, produced by
the rewritten `scripts/hybrid_gate_sweep.py`.

## 0. Correction to the brief's own stated value — recorded before running anything

The task brief (and the plan it was extracted from) both state "the real `Settings.abstain_threshold`
(0.05)". Checked, not assumed: `PYTHONPATH=src python3 -c "from sebi_rag.settings import Settings;
print(Settings.load().abstain_threshold)"` prints **0.12**, not 0.05. `config.toml` (`[service]`,
committed 2026-08-24 alongside ADR-004) explicitly recalibrated `abstain_threshold` from 0.05 to
0.12 for jina's score scale — the brief's "(0.05)" is stale w.r.t. a change made the same day as the
reranker swap it's supposed to already account for. The instruction that matters is the *mechanism*
("use `Settings.abstain_threshold` via `Settings.load()`, never hardcode 0.42") — that mechanism is
followed exactly; the specific number it resolves to (0.12) is reported as what the code actually
does, not silently corrected to match a stale parenthetical. This does not change anything else in
this design: 0.12 is still nowhere near 0.42 (the `SubjectSimJudge` threshold the original 2026-08-13
script wrongly reused), so the conflation bug fix is identical either way.

## 1. Method

**Fixed targets (from `docs/status.md:1223-1227`, 2026-08-13 diagnosis, re-confirmed
`docs/status.md:864` 2026-08-26):** `v7-ls-029`, `v7-nt-013`, `v7-nt-025` — all three diagnosed
`abstention_reason=subject_gate` (relevant doc retrieved at rank 0/1, `subject_sim` just under 0.42,
`rerank_top` near-ceiling under the *old* bge reranker). Under jina (ADR-004, 2026-08-24) their
`rerank_top` values were already measured once, independently of this task, by
`scripts/analysis/jina_abstain_threshold_calibration.py`
(`reports/jina-abstain-threshold-calibration-2026-08-24.json`):

| id | jina rerank_top (2026-08-24 calibration) |
|---|---|
| v7-ls-029 | 0.3430 |
| v7-nt-013 | 0.4432 |
| v7-nt-025 | 0.4923 |

These are cited as the empirical basis for the candidate grid below — they come from a prior,
independently-run measurement (not this task's own result) using the exact same methodology
(`retrieve → jina.rerank → demote_superseded(0.3)`, matching `answer_with_abstention`'s
`rerank_top`). This task's own run may reproduce slightly different values (corpus grows between
scrapes) — the grid is chosen wide enough to tolerate that drift.

**Pipeline under test** (`scripts/hybrid_gate_sweep.py`, rewritten):
- `reranker = JinaMLXReranker()` — current prod (`config.toml reranker_model="jina"`, ADR-004).
- `abstain_threshold = Settings.load().abstain_threshold` (0.12, see §0) — the score-floor gate.
  Never the `SubjectSimJudge` threshold (0.42); that conflation was the 2026-08-13 script's bug.
- `judge = SubjectSimJudge(emb, threshold=0.42, section_threshold=0.60)` — unchanged, matches prod
  defaults (`SEBI_RAG_SUBJ_THRESHOLD`/`SEBI_RAG_SECT_THRESHOLD` env defaults in `api.py`).
- `generator = ExtractiveStubGenerator()` — abstention is decided in `answer_with_abstention` before
  generation runs (`generate.py:708-729`), so the stub is faithful for this analysis and ~2 orders of
  magnitude faster than MLX over 219+41 rows (established precedent: `docs/status.md` 2026-08-13
  "Abstention is decided before generation, so the stub generator is faithful").
- `citation_scorer=None`, `superseded_penalty=0.3` (prod default) — citation scoring plays no role in
  the abstention decision being measured.

**Run over the full `golden_v7.jsonl`** (n=260, `eval_harness.load_golden` +
`benchmark.validate_golden`, matching every `scripts/analysis/*.py` script from this session), not a
subsample — collecting `ans.confidence.get("subject_sim")`, `ans.confidence.get("section_sim")`
(note: code key is `section_sim`, not `section_score` — confirmed at `generate.py:723`),
`ans.confidence.get("rerank_top")`, `ans.abstained`, `ans.abstention_reason` for every row.

**Guardrail cohort:** all 41 `item.get("abstain") is True` rows in golden_v7. Per `generate.py`'s
actual control flow (score-floor check at line 710 happens *before* the subject-gate check at line
728), a row still vetoed by the score floor (`rerank_top < 0.12`) is structurally immune to the
hybrid OR-rule — the rule only ever gets evaluated for rows that already cleared the score floor.
Guardrail rows are reported in two groups: (a) score-floor-immune (unaffected by any T, by
construction), (b) score-floor-cleared (at risk of the hybrid rule flipping them to a false answer —
this is the group the false-positive count in §2/§3 is computed over).

**Candidate `T` grid** (bracketing the three targets' known scores from the table above, with margin
for index drift and one point above the highest target to observe guardrail-cost growth continuing
past the last target): **T ∈ {0.30, 0.35, 0.40, 0.45, 0.50, 0.55}**. Explicitly *not* reusing the old
script's bge-scaled 0.85/0.80/0.75 (jina's own observed max score in the 2026-08-24 calibration was
0.67, so 0.85 is outside jina's range entirely and could never fire — see §5 finding).

## 2. Endpoints

| role | metric | source |
|---|---|---|
| PRIMARY (count) | targets rescued (of 3) per candidate `T` | hybrid rule applied post-hoc to collected `subject_sim`/`section_sim`/`rerank_top` |
| PRIMARY (safety) | guardrail false positives introduced (of the score-floor-cleared guardrail rows) per candidate `T` | same post-hoc application over the 41 gold-abstain rows |
| PRIMARY (Global Constraints bar) | `abstention_accuracy` delta, full golden_v7 (n=260), hybrid-gate arm vs current-prod arm, paired per query (1 = pipeline's abstain/answer decision matches gold `abstain` label, 0 otherwise) | `stats.py:paired_delta` |
| GUARDRAIL | `make test` | must stay green; no `config.toml` change ships from this loop regardless of outcome |

**Power note (disclosed in advance, not after seeing the result):** the maximum possible number of
discordant pairs this experiment can produce is 3 (the targets) plus however many guardrail rows flip
(disqualifying if >0, see §3). In the best case — all 3 targets rescued, 0 guardrail flips — the
per-query abstention-accuracy vector has exactly 3 nonzero entries (all +1/260) out of 260. Under
`paired_delta`'s sign-flip permutation null, the observed statistic is the extreme value (all three
concordant), so the two-sided achievable p-value is bounded below by the probability all three
independent sign flips land the same way as observed — combinatorially ≈ 2×(1/2)³ = 0.25 in the
continuous limit, i.e. **this design cannot reach p<0.05 even in its best possible outcome**. This
mirrors this project's own recorded pattern for rare-event flips (iv-series A/B tests return p=1.000
on 0–2 discordant queries; this experiment's own memory-documented sibling needs ≥6 discordant rows
to have any chance of significance). §3 accounts for this explicitly rather than silently failing the
generic bar.

## 3. Decision rule — fixed in advance

**Step 1 — disqualifying safety filter.** Only candidate `T` values with **zero** guardrail false
positives (among score-floor-cleared gold-abstain rows) are eligible at all. Per the brief: "a hybrid
gate that rescues the 3 targets must not flip previously-correct abstentions to false answers" — this
is a hard precondition, not something a target-rescue count can outweigh. `T` values that fail this
are excluded from consideration entirely, regardless of how many targets they rescue.

**Step 2 — Global Constraints bar, applied to eligible `T`s only.** For each eligible `T`, compute
`stats.py:paired_delta` on the full-golden_v7 abstention-accuracy vector (hybrid-gate arm vs
current-prod arm). A `T` is **adopted-as-recommendation** if, in addition to Step 1:
- rescued_targets(T) ≥ 1, **and**
- `|Δ abstention_accuracy| ≥ 0.01`, **and**
- `PairedResult.significant is True` (permutation p<0.05 **and** paired bootstrap CI excludes 0).

Among `T`s meeting all of the above, prefer the one maximizing rescued_targets(T); tie-break smallest
`T` (same knee-selection convention as
`scripts/analysis/jina_abstain_threshold_calibration.py`'s `min(..., key=(false_abstentions, thr))`).

**Step 3 — outcomes:**
- **NULL (categorical/safety):** no `T` in the grid survives Step 1 (every `T` that rescues ≥1 target
  also introduces ≥1 guardrail false positive). Current gate carries forward unchanged. This is the
  same class of outcome as the 2026-08-13 "both threshold levers are dead" finding for the plain
  subject-threshold nudge.
- **NULL (Global Constraints bar, disclosed low-power outcome):** at least one `T` survives Step 1
  (rescues ≥1 target, 0 guardrail false positives) but none clears Step 2's significance bar. Per the
  Power Note in §2, this is the *anticipated* outcome for a ≤3-discordant-row effect and is recorded
  as NULL under the same bar this project applies everywhere else — not treated as a deviation, and
  not a basis for lowering the bar (see §4). The safe/targeted rescue numbers are still reported in
  full for the record as a disclosed descriptive (non-adopted) finding.
- **ADOPTED-AS-RECOMMENDATION:** at least one `T` clears both Step 1 and Step 2. Recommendation only
  — no `config.toml` change ships from this task regardless of this outcome.

## 4. Not permitted after seeing a result

- Lowering the 0.01/significance bar because Step 1 produced a safe, targeted rescue that is close
  but not significant (matches this project's standing discipline, e.g.
  `2026-08-26-retrieval-param-sweep-prereg.md` §4, `2026-08-24-jina-reranker-v3-prereg.md` §4).
- Treating a "NULL (Global Constraints bar)" outcome as grounds to invent a different, more lenient
  statistical test post-hoc — the Power Note in §2 already discloses this is expected; the recorded
  outcome is NULL under the bar that was fixed in advance, not a search for a bar that passes.
  However, the descriptive safe-rescue numbers (rescued/guardrail counts) are meaningful and are still
  reported per the audit's own instruction to record what was measured, not filed as "no information."
- Reporting this run's numbers against `eval/golden/gate_v7.json` floors — those floors are
  model-dependent (`.claude/rules/refusal-criteria.md`) and this changes the abstention gate, which
  the floors assume fixed.
- Shipping any `config.toml` change from this task, adopted or not — out of scope per the plan's
  explicit ruling; requires a separate, explicitly-approved follow-up.
- Touching `para-mfborrow`/`para-pricedata` (score_floor false abstentions, a different, already
  explored lever per `docs/status.md:1228`) — out of scope for this hybrid-gate-only experiment.

## 5. Recorded outcome

_Filled in after the run below._
