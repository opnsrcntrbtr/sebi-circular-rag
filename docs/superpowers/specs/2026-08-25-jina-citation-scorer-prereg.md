# Preregistration — B′ citation scorer: jina-reranker-v3 (listwise) vs bge-reranker-v2-m3 (pointwise)

**Written before execution.** Decision rule in §6 and the not-permitted list in §8 are fixed as of
this document's commit. No arm has been run.

Roadmap: `docs/research-roadmap-2026-08-19.md` R4 ("reranker architecture — inter-passage
attention"), read against the R0 post-mortem (2026-08-20) and the R1 outcome (2026-08-23).

---

## 0. Why this is a new arm, not a repeat of R1

R0's post-mortem established the standing fact this arm inherits: `answer_with_abstention` sets
`ans.citations` from **either** `select_citations(...)` with B′ armed **or** cite-all without it —
the generated brackets are never the source. With B′ armed, **`select_citations`'s scorer is the
only control surface on `citation_recall`/`citation_precision`.**

Two attempts to change *what that scorer measures* have already run and failed the same way:

| arm | criterion swapped in | zero-cite | outcome |
|---|---|---|---|
| NLI attribution (2026-08-12) | entailment | 19 → 54 | REJECTED |
| R1 warrant judge (2026-08-23) | warrant (relation/modality/scope/temporal/numeric) | 16 → 47 | REJECTED |

Both replaced a **pointwise** scorer's *criterion* while keeping it pointwise. Neither touched the
**architecture**: bge-reranker-v2-m3 scores each `(answer_text, context)` pair independently, so it
structurally cannot compare candidates against each other — it cannot express "these two chunks say
almost the same thing, but only one governs" or "this chunk is topically closer to the answer than
that superseded one, even though both look relevant in isolation". That is an *inter-passage*
question, not a criterion question.

`docs/research-roadmap-2026-08-19.md` R4 named this exact gap (citing Set-Encoder, arXiv:2404.06912)
for the *retrieval* reranker and was addressed there: ADR-004 adopted `jina-reranker-v3-mlx`
(arXiv:2509.25085) for `pipeline.reranker`, a listwise reranker with causal self-attention across
the whole candidate set in one forward pass — "last but not late interaction" per the paper — measured
on golden_v7 (recall@10 +2.42%, nDCG@10 +6.76%, no regression, `docs/adr-004-...md`).

**But ADR-004 deliberately did not extend to B′.** `config.toml:16-18` and `rerank.py`'s
`retrieval_reranker_for` docstring both record this as an explicit scope boundary, not an oversight:
*"citation_scorer_for is always built against `bge_reranker` directly and is never routed through
this function's choice"* — reasoned from R1's finding that "the citation-scoring role can fail
independently of retrieval-reranking quality." That reasoning is sound as a decoupling *default*; it
is not evidence against testing jina as B′'s scorer, since B′ was never given the listwise mechanism
to fail with.

**The claim this arm tests:** a listwise, inter-passage-aware scorer is a third, architecturally
distinct citation-selection criterion — not a third attempt at entailment or warrant — and is best
positioned to fix exactly the citation failure classes that look like a disambiguation problem:

| cause (status.md 2026-08-13, MLX generator, n=19 zero-cite) | rows | disambiguation-shaped? |
|---|---|---|
| supersession demotion (relevant doc ranked out by a near-duplicate re-issue) | 6 | yes |
| reranker ordering | 3 | yes |
| B′ (pointwise collapse / wrong pick among relevant-looking contexts) | 4 | yes |
| subject_gate false abstention | 3 | no — upstream of citation selection |
| score_floor | 2 | no — upstream |
| non-SEBI false positive | 1 | no — upstream |

13 of 19 (68%) are exactly the "which of these similar-looking chunks is the one that governs"
question a pointwise scorer cannot represent. This arm's ceiling is therefore larger than R1's
(4 rows, B′-only) — but per `iv-series-verdicts-unpowered`, ceiling size is not the endpoint; see §4.

---

## 1. What this is not

- Not a repeat of the NLI/warrant attempts: those swapped *criterion* (entailment, warrant) inside
  the same pointwise architecture. This swaps *architecture* (listwise, inter-passage) while keeping
  the criterion the same family as production today (relevance-of-context-to-answer-text).
- Not a claim that jina is "better" in general — ADR-004's own bar was **measured benefit on SEBI
  data**, not the vendor's BEIR numbers. This arm applies that same bar to the citation-scoring role.
- Not a generator change. R0 already established the generator cannot move these metrics while B′
  is armed; this arm holds the generator, retrieval, `top_k`, dedup, `margin`, and `min_keep` fixed
  and changes only the scorer object `select_citations` receives — exactly R1's single-variable
  design (§3 there), reused here.

---

## 2. The trade this is measuring

Cost: **zero additional model residency in production.** Unlike R1 (a 7B judge call per query, on
top of generation — R1 §9's honestly-stated latency blocker), jina-reranker-v3-mlx is already
loaded in production today (`config.toml: reranker_model = "jina"`, ADR-004). If this arm is
adopted, `api.build_default_pipeline` reuses the *same* resident instance for both roles (wired
2026-08-25 — see §9). The cost premise that sank R1's deployability (two models resident, doubled
per-query latency) does not apply here by construction, not by measurement-yet-to-come.

Benefit being tested: whether listwise scoring recovers citation quality on the disambiguation-shaped
failure rows the two pointwise-criterion swaps could not reach.

---

## 3. Method

**Single variable: the scorer object `select_citations` receives.** Same pool (50), same retrieval,
same `pipeline.reranker` ordering (jina, ADR-004 production default), same `top_k=10`, same doc_id
dedup, same `superseded_penalty=0.3`, same `margin=0.35`, same `min_keep=1`, same generator
(production 1.5B — R0 established holding it constant is free and keeps the arm cheap).

Routing goes through the existing seam: `generate.citation_scorer_for(enabled, reranker, backend)`
already dispatches `"reranker"` | `"nli"` | `"warrant"`. `"jina"` is a **fourth backend**, added
2026-08-25 (`generate.py`), not a new code path — so eval and production cannot diverge, the
property this function exists to guarantee.

### 3.1 `select_citations` needs no change — jina fits the existing protocol, unlike R1's judge

R1 §3.1–3.2 had to solve a real problem: `_judge_prompt_identify`'s call shape returns one excerpt,
but B′ needs a set, so the warrant judge had to be built to emit a set and score it onto the
`Reranker` protocol's `[0.0, 1.0]` convention.

**`JinaMLXReranker` already satisfies `Reranker` exactly** (`rerank.py:124-165`, ADR-004): it
implements `.rerank(query, candidates) -> list[(Chunk, float)]`, the identical shape
`CrossEncoderReranker` provides and `select_citations` already calls as
`scorer.rerank(answer_text, contexts)` (`generate.py:119`). No new call shape, no new parser, no
degeneracy-probe precondition (§3.3 in R1 existed because a *prompted* judge can return unparseable
text; a reranker forward pass cannot). The margin/`min_keep` semantics measured under bge are
preserved bit-for-bit — a jina-vs-control difference is attributable to the architecture change and
nothing else.

### 3.2 Score scale caution

jina's score distribution is not bge's (`config.toml:25-27`, ADR-004: median top-score 0.45 vs bge's
0.98, can go negative). `select_citations`' margin test (`s >= top - margin`) is relative to each
row's own top score, so this does **not** require re-deriving `citation_margin` — the margin already
operates scale-invariantly per row. This is stated explicitly because the *abstain* threshold
(`abstain_threshold`) **did** need recalibration for jina (0.05→0.12,
`jina_abstain_threshold_calibration.py`) and a reader familiar with that precedent should not assume
the same is true here without checking the mechanism, which differs.

---

## 4. Endpoints

**Cohort.** The perfect-retrieval subset, **recomputed on the live index and persisted with its
corpus hash** — not a stored artifact (per `iv-series-verdicts-unpowered` / R1 §4: "recompute, never
quote").

| role | metric | note |
|---|---|---|
| **PRIMARY** | `citation_precision` | the channel both prior B′ arms were measured on (R1 §1.2: +57% for bge-vs-off); keeps this arm comparable to R1's result on the same axis |
| **GUARDRAIL** | zero-cite rows | zero tolerance on increase — the NLI/R1 failure shape |
| **GUARDRAIL** | `citation_recall` | must not fall below the armed floor (`gate_v7.json`, not quoted) |
| SECONDARY | `citation_recall` (as effect), per-query latency (informational only — §2 already establishes no residency cost) | reported, not decisive |
| CONFIRMATORY | primary + guardrails split by `label_tier` (CS1: 68.8% of the gate is model-labelled) | reported alongside |

⚠️ **Correction made during self-review, before running.** This section originally also committed to
a confirmatory split by "disambiguation-shaped vs upstream" failure class, keyed to §0's table. That
table is a **corpus-level aggregate** from the 2026-08-13 status.md entry (6 demotion / 4 B′ / 3
reranker / 3 subject_gate / 2 score_floor / 1 non-SEBI) — no per-row cause label for those 19 rows
was ever persisted to a file this script can load. Producing that split would require either
re-deriving row-level causes (out of scope here) or fabricating the mapping, which this project's
refusal criteria forbid. **Dropped as a script deliverable.** §0's table remains valid as the
*motivation* for the arm; it is not re-claimed as a measured confirmatory output.

Per-row records captured in the generate-phase dump (id, task_type, label_tier, answer_text,
context_ids, both arms' citations/measures) so the label-tier split is available without a re-run.

---

## 5. Arms

**Control** — B′ with `backend="reranker"` (bge-reranker-v2-m3, pointwise), `margin=0.35`,
`min_keep=1`. Production today.

**J1** — B′ with `backend="jina"` (jina-reranker-v3-mlx, listwise), same `margin`, same `min_keep`.

Both arms score the **same** answer text and the **same** context window per row (generated once,
reused for both — the 1.5B generator is deterministic under greedy decoding, so this introduces no
noise between arms, matching R1 §method exactly).

**Rejected in advance:**
- Sweeping `margin` for J1 specifically — two variables, uninterpretable result (R1 §5's same rule).
- Any arm that also changes the generator or `pipeline.reranker`'s ordering — both already fixed by
  ADR-004/R0 and confounding either back in wastes an answered question.
- Reporting jina's raw score distribution as evidence of anything before the margin/keep logic is
  applied to it (§3.2 explains why the scale differs but the mechanism doesn't need recalibration —
  that reasoning is not a substitute for measuring the actual kept-set difference).

---

## 6. Decision rule — fixed in advance

Adopt J1 **only if all three hold**:

1. **`citation_precision` increases by ≥ +0.02 absolute** on the recomputed cohort (matching R1 §6's
   effect-size floor exactly, both for comparability and because R1 established this floor's
   rationale — the `superseded_penalty` confirmatory run's undirected criterion adopted a 1-row,
   p=1.000 result, and this arm does not repeat that).
2. **Zero-cite does not increase.** Zero tolerance on direction, same as R1 §6.2.
3. **`citation_recall` stays at or above its armed floor** (read `eval/golden/gate_v7.json` at run
   time, never a quoted table value).

**If 1 holds but 2 or 3 fails → REJECT.** Recorded as rejected, not "promising, needs tuning" — same
rule R1 fixed and the same reason: a promising direction without a passed guardrail is not evidence
for adoption, it is an unfinished measurement.

**If 1 fails → REJECT regardless of 2/3.** A precision gain below the effect floor, even a positive
one, is within the range the `superseded_penalty` precedent showed to be noise-indistinguishable at
this cohort size.

---

## 7. Confirmation required before adoption

J1 clearing §6 on the cohort is **not** adoption. Required before arming `config.toml`:

- Full `eval_json_full` (n=260) against the armed floors, `floors_ok: true`.
- Floors are model-dependent (`project_context.md` §7.4). J1 does not change the generator (§1), so
  unlike R1 this does **not** require re-deriving the gate — the floors were derived and are measured
  under the MLX generator regardless of which reranker/scorer produced the citations
  (`eval_generator_for` governs generator identity only; `citation_scorer_for` is orthogonal). This
  is stated explicitly so a future reader does not assume every B′ arm requires a floor re-derivation
  — R1 did because it introduced a second generator into the path; J1 does not.

---

## 8. Not permitted after seeing the result

- Changing the primary endpoint, the guardrails, or the +0.02 effect-size floor.
- Reporting the cohort result as a gate result, or deriving/arming any floor from the cohort.
- Quoting a prior-index cohort value (§4) — recompute on the live index every run.
- Recording a §6-failing result as "directionally positive".
- Cherry-picking the disambiguation-shaped confirmatory split as the adoption basis if the primary
  (§6.1, unconditional) fails — the confirmatory split is diagnostic, not a second adoption path.

---

## 9. Implementation notes

**Files (landed 2026-08-25, before this run):**
- `src/sebi_rag/generate.py` — `"jina"` branch in `citation_scorer_for` (lazy-loaded via
  `jina_loader`, same pattern as `nli_loader`). No change to `select_citations` (§3.1).
- `src/sebi_rag/api.py` — `build_default_pipeline` reuses the already-built `retrieval_reranker`
  instance as the jina citation scorer when both `reranker_model` and `citation_scorer_backend` are
  `"jina"`, instead of loading a second MLX model (§2's zero-residency-cost claim, made true by
  construction rather than asserted).
- `src/sebi_rag/settings.py` — `citation_scorer_backend` docstring extended to `reranker | nli |
  warrant | jina`. Default unchanged (`"reranker"`); `citation_scorer_enabled` default unchanged
  (`False` — B′ is armed via a separate flag, currently `true` in the running eval config but the
  dataclass default stays conservative, matching existing convention).
- `tests/test_selective_citations.py` — three new offline tests for the `"jina"` backend branch
  (lazy-load via injected loader, ignores the bge positional, disabled beats backend choice),
  mirroring the existing `"nli"` backend tests exactly. No network/model access.
- `scripts/analysis/jina_citation_scorer_cohort.py` — cohort measurement script, structured as
  generate → score → report phases (R1's generate/judge/report pattern; "score" replaces "judge"
  since no LLM is involved — a plain reranker forward pass over the fixed (answer_text, contexts)
  pairs, run in the same process as generation if convenient, since there is no residency conflict
  to isolate against, unlike R1's 1.5B-vs-7B split).

**Hard constraints.** No new field on `CircularMeta` (`segment.py:131`). No edit to `*_spaces.py` or
root `app.py`. `config.toml` is not touched by this spec — `citation_scorer_backend` is selected via
`SEBI_RAG_CITATION_SCORER_BACKEND` for the cohort run, leaving production config untouched pending
§6/§7.

---

## 10. OUTCOME (recorded after execution)

**❌ REJECTED 2026-08-25.** Script `scripts/analysis/jina_citation_scorer_cohort.py`, report
`reports/jina-citation-scorer-cohort-2026-08-25.json`. Cohort recomputed on the live index:
**201 of 204** eligible rows (matches R1's and R2's recompute on this same index exactly).

| metric | control (bge) | J1 (jina) | delta | rule |
|---|---|---|---|---|
| citation_precision | 0.1770 | **0.3206** | **+0.1436** | §6.1 needs ≥ +0.02 ✅ |
| zero_cite | 15 | **24** | **+9** | §6.2 needs ≤ 0 ❌ |
| citation_recall | 0.9154 | 0.8706 | −0.0448 | §6.3 needs ≥ 0.8169 (armed floor) ✅ (margin +0.0537) |
| context_recall | 0.9826 | 0.9826 | 0.0000 | invariant by construction — neither arm touches retrieval |

**Verdict: REJECT on §6.2 alone** (§6.1 and §6.3 both pass). Same failure shape as the two prior
scorer-swap attempts (NLI 19→54, R1 warrant 16→47) — a precision gain bought partly by citing less,
this time via architecture rather than criterion.

**Mechanism — checked, not assumed.** The smoke test (n=3, §method note above) suggested pure
margin-collapse to `min_keep=1`: all three sampled rows dropped to exactly one citation, precision
→ 1.0. At full cohort scale that pattern is real but **not the dominant cause**:

- Mean citations per row: control 6.85 → J1 **4.43** (more selective, as expected from a tighter
  listwise ranking, not from `min_keep` collapse specifically).
- Rows with exactly 1 citation: control 6/201 → J1 **25/201** — collapse rate roughly quadrupled,
  but 176 of 201 J1 rows still keep ≥2.
- **Of the 13 rows that flipped from control-cited to J1-zero-cite, only 4 collapsed to a single
  (wrong) citation.** The other 9 kept 2 or more citations and still missed every relevant document.

**So the primary failure is not margin collapse — it is that jina, scoring `(answer_text,
contexts)`, ranks the genuinely relevant document below others in a meaningful fraction of rows.**
That is a real result about the scoring *regime*, not an artifact of `margin`/`min_keep`: ADR-004
benchmarked and adopted jina-reranker-v3 against the **original user query** for retrieval ordering;
B′ calls the identical `.rerank()` method with the **generated answer text** as the query
(`generate.py:119`, unchanged by this arm per §3.1). Those are different tasks, and this arm's
result says jina's listwise advantage does not transfer from one to the other on this corpus. The
inter-passage mechanism §0 hypothesized as a fix for disambiguation-shaped failures instead removed
the correct document from contention in more rows than it rescued.

**What this does and does not establish.** It does **not** revisit R4's retrieval-ordering
adoption (ADR-004) — that arm scored the original query against contexts and remains measured
positive on its own terms; nothing here touches `pipeline.reranker`. It **does** establish that
**listwise/inter-passage architecture, by itself, is not sufficient for the citation-scoring role**
— the third distinct approach (after entailment and warrant) to fail on B′, and by a within-cohort
margin (+9 zero-cite) between R1's warrant result (+31) and the original NLI result (+35). B′'s
scorer has now been tried as a pointwise reranker (production), an entailment model, a warrant
judge, and a listwise reranker; only the pointwise reranker (bge, production today) has cleared
its own guardrails.

**Not permitted and not done:** no margin re-tuning was attempted after seeing this pattern (§5,
§8); the collapse mechanism was investigated with existing dump data only, not a re-run.

**Shipped, and stays inert.** `citation_scorer_for`'s `"jina"` branch (`generate.py`),
`build_default_pipeline`'s reuse wiring (`api.py`), and the cohort script land in this commit.
`config.toml`'s `citation_scorer_backend` is not present (defaults to `"reranker"` in
`settings.py`) — unaffected, this arm never touched it. 885 tests pass (882 baseline + 3 new for
the `"jina"` backend branch), no regressions; 4 pre-existing failures (`test_export_integration.py`,
`test_segment.py` — corpus/segment drift, confirmed present on `main` before this change via
`git stash`) are unrelated.
