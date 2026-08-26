# Plan: Hybrid Abstention Gate + Set-Encoder Reranker Benchmark

## Context

This project (local-first SEBI Circular RAG, Apple M4 Pro) runs a disciplined
prereg-driven improvement loop recorded in `docs/status.md`. As of today
(2026-08-26) the entire R0–R7 research roadmap
(`docs/research-roadmap-2026-08-19.md`) has been closed out — every item
rejected, voided, gated-out, or adopted — and a separate 5-turn retrieval
parameter sweep (RRF k / pool depth / expansion / reranker interaction) just
completed this session with all nulls except an independent reconfirmation
of the current reranker (jina-reranker-v3-mlx, ADR-004).

Two genuinely open items survived a full audit of `docs/status.md`,
`docs/project_context.md`, and the existing worktrees (confirmed the
"constraint relaxation" and "Jina vs bge" threads from an old, repeatedly
stale-redelivered handoff are **already done** — no action needed there):

1. **Hybrid abstention gate** — `scripts/hybrid_gate_sweep.py` was written
   2026-08-13 when the project decided "pursue hybrid gate experiment for
   subject_gate rows only" (`docs/status.md:1230`), but it was **never run
   or its result recorded**. Today's R5 gate closure (`docs/status.md:864`)
   re-confirmed the same 3 rows (`v7-ls-029`, `v7-nt-013`, `v7-nt-025`) are
   still false-abstaining on `subject_sim` (0.4073 / 0.3108 / 0.4105, all
   just under the 0.42 threshold) with the documented fix path still listed
   as "Hybrid gate (cross-encoder OR)" and still unexecuted.
2. **Set-Encoder reranker** — `docs/status.md:935` names it "the one
   architecturally-motivated, permissively-licensed reranker candidate not
   yet tried" (unlike Jina and Qwen3-Reranker, both already implemented,
   benchmarked, and resolved). Confirmed via web research: Schlatt et al.,
   ECIR 2025 (arXiv:2404.06912), Apache 2.0 licensed, HF checkpoint
   `webis/set-encoder-base` (0.1B params, electra-base-discriminator
   backbone), inference via the `lightning-ir` package
   (`CrossEncoderModule("webis/set-encoder-base").score(query, docs)`).

**A real bug was found in the unrun script** — worth fixing rather than
just executing as-is: `hybrid_gate_sweep.py:38` passes
`abstain_threshold=0.42` to `RAGPipeline`, but 0.42 is the `SubjectSimJudge`
threshold, not the cross-encoder score floor (`Settings.abstain_threshold`
= 0.05). This is the *exact* conflation `.claude/rules/refusal-criteria.md`
calls out as having caused a real misclassified diagnostic on 2026-08-18.
The script also hardcodes `CrossEncoderReranker` (bge), which predates
ADR-004 (jina adopted 2026-08-24) — it would be benchmarking the wrong
current baseline. And the rerank_top thresholds it sweeps (0.85/0.80/0.75)
were implicitly calibrated for bge's score distribution; per
`project_context.md` §7.3 ("0.05 does not transfer to a different
reranker"), these do not transfer to jina without recalibration.

**Outcome wanted:** both items get a properly preregistered, executed,
recorded analysis — following this project's own established discipline
(prereg doc with fixed decision rule → run → record verdict in
`docs/status.md`) — so the backlog reflects reality instead of a stale
"decided but not done" item and a "not yet tried" candidate.

## Decisions already made (with the user, before this plan)

- Both Task A (hybrid gate) and Task B (Set-Encoder) are in scope, planned
  as one SDD run with two independent tasks.
- Task B is **benchmark-only**: implement enough to run a preregistered
  comparison against the current reranker (jina) on golden_v7, in the same
  spirit as ADR-004. No adoption authorized from this plan — a win is
  reported as a recommendation, not shipped to `config.toml`.
- Runs in a **new git worktree + branch** off `main`.

**Ruling (mine, to record in the plan since it wasn't explicitly asked):**
Task A is also treated as report-and-recommend, not auto-ship — matching
this project's repeated standing rule ("no config.toml change ships without
a separate, explicitly-approved follow-up," restated in every prereg this
session and in `docs/status.md`'s own decision entries). If Task A's result
clears its own decision rule, the task's deliverable is the prereg doc +
`docs/status.md` entry + recommendation, not a `config.toml` edit. If this
is wrong, the cost is small: a follow-up "please ship it" message, not a
silently-changed abstention gate in production.

## Global Constraints (bind both tasks)

- No edits to `CircularMeta` in `src/sebi_rag/segment.py` (hard architectural
  constraint — `hierarchical_chunk()` does `meta=asdict(meta)`, would mutate
  the persisted 985 MB index).
- Do not edit `*_spaces.py` / root `app.py` (HF Spaces CPU demo — separate
  code path, `config.toml [spaces]`).
- No `config.toml` change ships from either task without separate,
  explicit follow-up approval — both are report + recommendation only.
- Every experiment is preregistered before it runs: a fixed decision rule
  (adopt/null bar) and a "not permitted after seeing a result" list, in the
  style of `docs/superpowers/specs/2026-08-26-retrieval-param-sweep-prereg.md`
  and `docs/superpowers/specs/2026-08-24-jina-reranker-v3-prereg.md`. Decision
  rule for both tasks (use unless a task's brief states otherwise): adopt
  only if `|Δ| ≥ 0.01` on a primary metric **and**
  `stats.py:PairedResult.significant` (permutation p<0.05, paired bootstrap
  CI excludes 0) — the same rule already vetted this session.
- `PYTHONPATH=src` + the standard env guard block
  (`TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1
  PYTORCH_ENABLE_MPS_FALLBACK=1 HF_HUB_DISABLE_XET=1`) for every script run,
  matching every existing script in `scripts/` and `scripts/analysis/`.
- `make test` (`pytest -q -m "not integration"`) must stay green after each
  task's commits — currently 901 passed, 2 skipped, 3 deselected on `main`.
- Never compare a changed-config run against `eval/golden/gate_v7.json`
  floors directly (category error per `.claude/rules/refusal-criteria.md`
  — those floors are model-dependent). Report deltas paired against the
  *current-prod* run on the same queries instead.
- Reuse existing infra, do not reinvent: `stats.py:paired_delta` /
  `bootstrap_ci` for significance, `eval_harness.load_golden` /
  `eval_harness._unique` for golden-set loading and doc-dedup,
  `benchmark.py:run_retrieval_benchmark` / `resolve_chunk_spans` where a
  full pipeline run (not just retrieval) is needed, the `Reranker` Protocol
  in `rerank.py` for any new reranker class.

## Task 1 — Fix and run the hybrid abstention gate experiment

**Files:** rewrite `scripts/hybrid_gate_sweep.py` (existing but broken/stale
— see bugs above); new prereg doc
`docs/superpowers/specs/2026-08-26-hybrid-gate-prereg.md`; new report
`reports/hybrid-gate-cohort-2026-08-26.json` (or similar); `docs/status.md`
entry recording the verdict.

**What it must do, correctly this time:**
1. Build the pipeline with **current production config**: reranker = jina
   (`JinaMLXReranker`, per `config.toml reranker_model="jina"`, ADR-004), and
   the real `Settings.abstain_threshold` (0.05) for the score-floor gate —
   never pass 0.42 there. `SubjectSimJudge(emb, threshold=0.42,
   section_threshold=0.60)` is correct as the existing script has it — that
   part is fine, only the `RAGPipeline(abstain_threshold=...)` argument is
   wrong.
2. Run over golden_v7 answerable rows (`eval_harness.load_golden` +
   `validate_golden`, matching the pattern in every `scripts/analysis/*.py`
   script from this session) to (a) reproduce the false-abstention set,
   confirming it is still exactly (or a superset containing)
   `v7-ls-029`/`v7-nt-013`/`v7-nt-025`, and (b) collect
   `subject_sim`/`section_score`/`rerank_top` for every abstained row and
   every answered row (the answered rows are the guardrail cohort — a
   hybrid gate that rescues the 3 targets must not flip previously-correct
   abstentions to false answers).
3. **Recalibrate, don't reuse, the rerank_top threshold candidates.** The
   old script's 0.85/0.80/0.75 were implicitly bge-scaled. Under jina's
   score distribution, derive candidate thresholds from the *observed*
   `rerank_top` values of the 3 target rows and the surrounding guardrail
   cohort (e.g. a small grid bracketing the targets' own scores), not the
   old literal numbers.
4. Hybrid gate rule to test: pass (answer) if
   `subject_sim >= 0.42 OR section_score >= 0.60 OR rerank_top >= T`, for
   each candidate `T`. Primary metric: count of targets rescued (of 3) vs.
   count of guardrail false positives introduced (of the answerable-and-
   correctly-answered cohort). Decision rule per Global Constraints, applied
   to the resulting abstention_accuracy delta.
5. Preregister before running: the 3 target IDs, the guardrail cohort
   definition, the candidate `T` grid, and the adopt/null rule — fixed in
   advance, in the same structural style as this session's
   `2026-08-26-retrieval-param-sweep-prereg.md` (§1 Method, §2 Endpoints,
   §3 Decision rule, §4 Not permitted after seeing a result, §5 Recorded
   outcome).
6. Record the verdict in `docs/status.md` (new dated entry, same style as
   the existing log) whether adopted-as-recommendation or null.

**Out of scope for Task 1:** shipping any gate change to `config.toml`;
touching `para-mfborrow`/`para-pricedata` (those are `score_floor` false
abstentions, a different, already-explored lever per `docs/status.md:1228`
— "Relax floor (releases 13 FPs)" — not part of this hybrid-gate scope).

## Task 2 — Set-Encoder reranker benchmark (report-only)

**Files:** `pyproject.toml` (add `lightning-ir` dependency, optional
extra if the project uses extras elsewhere — check existing pattern e.g.
`[eval]` extra referenced in `tests/test_trec_parity.py`'s skip reason);
new `SetEncoderReranker` class in `src/sebi_rag/rerank.py`; extend
`scripts/bench_retrieval.py`'s `--reranker` choices
(currently `["crossencoder", "jina"]`) to add `"set-encoder"`; new prereg
doc `docs/superpowers/specs/2026-08-26-set-encoder-prereg.md`; `docs/status.md`
entry.

**Implementation:**
1. `SetEncoderReranker` conforms to the existing `Reranker` Protocol
   (`rerank(query: str, candidates: list[Chunk]) -> list[tuple[Chunk, float]]`
   — mirror `CrossEncoderReranker`'s constructor shape (`model` name
   default `"webis/set-encoder-base"`, `device` param). Wrap
   `lightning_ir.CrossEncoderModule(model).score(query, [c.text for c in
   candidates])`, pair scores back with their original `Chunk` objects, sort
   descending — same contract `JinaMLXReranker`/`CrossEncoderReranker`
   already implement, read those two for the exact pairing/sorting idiom.
2. Device: default to **CPU**, matching `CrossEncoderReranker`'s own
   documented reason ("MPS crashes CrossEncoder — segfault 139" on this
   hardware, `rerank.py:201-204`). The implementer may empirically test MPS
   for lightning-ir specifically (it's a different runtime than
   sentence-transformers' `CrossEncoder`) but must default safely to CPU
   unless MPS is verified stable.
3. `bench_retrieval.py --reranker set-encoder --rerank` must work end to
   end exactly like the existing `--reranker jina`/`crossencoder` paths —
   no new wrapper classes needed there, just extend the existing
   `if args.reranker == "jina": ... else: ...` branch (or equivalent) with
   a third arm.
4. Preregister: golden_v7 (n=260), primary metrics `recall_at_10` /
   `ndcg_at_10` (matching `run_retrieval_benchmark`'s own field names, as
   this session's retrieval-param-sweep report already had to reconcile
   `doc_recall_at_10` vs. bare `recall_at_10` naming — be consistent with
   whichever script actually produces the numbers), paired against the
   current-prod jina run on the same queries via `stats.py:paired_delta`.
   Fixed decision rule per Global Constraints. State explicitly: this is
   **not** a re-derivation of ADR-004, and per
   `.claude/rules/refusal-criteria.md`, the result is not compared against
   `gate_v7.json` floors.
5. Run it, record the verdict (adopt-recommended / null) in
   `docs/status.md` and the prereg doc's §5. **No config.toml edit**
   regardless of outcome — that requires a separate approved follow-up.

**Out of scope for Task 2:** fine-tuning Set-Encoder on SEBI data (that's
the separate, much larger, not-yet-scoped "bge-m3 fine-tuning" idea from
old status.md notes — explicitly not part of this plan); porting to MLX;
wiring into the citation scorer (`B'`) role — this is a retrieval-ordering
reranker benchmark only, matching what ADR-004 tested Jina/bge for.

## Verification (both tasks)

- `make test` green after each task's commits (901 passed baseline).
- Each task's prereg doc exists **before** its script's first run (commit
  order matters for the "preregistered before seeing a result" discipline
  this project enforces everywhere else).
- Each task ends with a `docs/status.md` entry in the file's existing style
  (newest entries prepended near the top, dated, verdict stated plainly).
- Task 2's new dependency doesn't break `make test` collection (import-time
  failures if `lightning-ir` is missing) — follow the existing pattern for
  optional/heavy deps (e.g. how SPLADE's `splade_encoder.py` or the
  `[eval]` extra are guarded) so offline tests don't require
  `lightning-ir` to be installed.
- Final whole-branch review (per subagent-driven-development) checks both
  tasks' diffs together before merge is offered via
  `superpowers:finishing-a-development-branch`.
