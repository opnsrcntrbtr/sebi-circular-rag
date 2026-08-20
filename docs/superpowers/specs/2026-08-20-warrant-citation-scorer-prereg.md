# Preregistration — R1: warrant-calibrated citation scorer for B′

**Written before execution.** Decision rules in §6 and the not-permitted list in §8 are fixed as of
this document's commit. No arm has been run.

Roadmap: `docs/research-roadmap-2026-08-19.md` R1 (UNBLOCKED + PROMOTED 2026-08-20).

---

## 0. Read this first — the roadmap's proposed endpoint is wrong for this intervention

R1's roadmap entry specifies *"zero-cite as primary, matching the two prior B′ arms so results are
comparable."* **Comparability is the right instinct and the wrong endpoint here**, for a reason that
is already measured.

The 19 zero-cite rows under the MLX generator decompose as (status.md 2026-08-13):

| cause | rows |
|---|---|
| supersession demotion | 6 |
| **B′** | **4** |
| reranker ordering | 3 |
| subject_gate false abstention | 3 |
| score_floor | 2 |
| non-SEBI false positive | 1 |

**B′ causes 4 of 19.** R1 changes only what B′ scores, so on a zero-cite endpoint its *ceiling* — a
perfect warrant judge that fixes every B′-caused row and breaks none — is **4 rows**. The other 15
fail upstream of citation selection and are untouchable from here.

Two measured precedents say a 4-row ceiling is not detectable on this cohort:

| prior arm | zero-cite change | p |
|---|---|---|
| `superseded_penalty` 0.3 → 0.5 (2026-08-13) | 19 → 18 (**1 row**) | **1.000** |
| R2 supersession tiering (2026-08-20) | 14 → 19 (wrong direction) | rejected on §6.3 |

An endpoint whose best case is 4 rows, on an instrument that returned p=1.000 at 1 row, is
**underpowered by construction**. Preregistering it would buy a near-guaranteed null that says
nothing about the hypothesis — the failure mode the iv-series already produced repeatedly.

**Therefore this spec makes `citation_precision` primary and zero-cite a guardrail.** That is a
deliberate, pre-committed deviation from the roadmap text, recorded here rather than chosen after
seeing a result. The justification is that precision is the channel where B′'s effect is *measured
to be large* (+57%, §1.2) and zero-cite is where its known failure mode lives (§1.3) — so this
assignment tests the hypothesis on the axis it can move while guarding the axis it can break.

---

## 1. Why

### 1.1 With B′ armed, this is the only lever on the citation metrics

Established by R0's post-mortem (2026-08-20). `answer_with_abstention` (`generate.py:551`):

```python
if citation_scorer is not None:
    citations = select_citations(text, contexts, citation_scorer, ...)
else:
    citations = [c.id for c in contexts]
```

`ans.citations` comes from `select_citations` or from cite-all. **It never comes from the model's
emitted brackets** — `select_citations` (`generate.py:90`) scores
`scorer.rerank(answer_text, contexts)` and never parses one. B′ is armed in production
(`citation_scorer_enabled = true`).

R0 measured the consequence: raising bracket firing 0.0% → 47.6% by swapping the generator to 7B
moved `citation_recall` +0.007 and `citation_precision` −0.007. **The generator is not a control
surface for citations. B′'s criterion is the whole mechanism.**

### 1.2 B′ is not broken — it is scoring the wrong quantity

B′ buys `citation_precision` **+57%** and costs 4 zero-cite rows (2026-08-13: *"B′ costs 4 rows for
+57% citation_precision — leave it alone"*). The repo's own conclusion is that its scorer is a
**relevance** model doing an **attribution** job — *"a relevance reranker used as an attribution
scorer"*. R1 does not remove B′; it changes the criterion inside it.

### 1.3 ⚠️ Scorer replacement has already failed twice, and the failure has a shape

Both NLI attempts were rejected. The valid run (Run 2, both arms under MLX, all three validity
checks passed) measured **zero-cite 19 (reranker) vs 54 (NLI), Δ +0.1699, p=0.0001**. Run 1 was
confounded by `ExtractiveStubGenerator` returning `contexts[0].text` verbatim — a limitation
preregistered in advance.

The standing conclusion was *"stop pursuing attribution/NLI scorers for B′; entailment is the wrong
criterion — a context can be the governing provision without entailing a paraphrase of it."*

**This spec's claim is that warrant is a third criterion, not a third attempt at entailment.** That
claim is the thing under test. It is falsifiable and §6 fixes how: if warrant reproduces the NLI
failure *shape* — zero-cite inflation — it is rejected on the guardrail regardless of what precision
does.

### 1.4 External support

- [2605.28044](https://arxiv.org/abs/2605.28044) — warrant ≠ relevance ≠ entailment; warrant-focused
  prompting 47.2% → 75.5%; overlap signals non-monotone on 32.8–36.4% of cases.
- [2509.21557](https://arxiv.org/abs/2509.21557) — post-hoc is the right paradigm for legal
  attribution, which is why the architecture is retained and only the criterion changes.

⚠️ Both are **paper-reported on their own benchmarks**, not on SEBI data. They motivate the
hypothesis; they are not evidence for it here.

---

## 2. The trade this is measuring

B′ today: keep contexts whose *topical relevance to the answer text* is within `margin=0.35` of the
top. The failure this targets is a context that is **about** the subject without **governing** it —
which for a regulatory corpus is the difference between a citation that supports a legal claim and
one that merely shares vocabulary.

The trade being bought: warrant judgement is a **prompted generation**, so it costs a model call per
query where the cross-encoder costs a forward pass. §9 states the cost premise honestly.

---

## 3. Method

**Single variable: the scorer B′ consults. Everything else is held.** Same pool (50), same
retrieval, same reranker, same `top_k=10`, same doc_id dedup, same `margin` semantics, same
`min_keep`, same generator (production 1.5B — R0 established the generator does not move these
metrics, so holding it constant is free and keeps the arm cheap).

Routing goes through the existing seam: `generate.citation_scorer_for(enabled, reranker, backend)`
already dispatches on `backend` (`"reranker"` | `"nli"`). The warrant judge is a **third backend**,
not a new code path — so eval and production cannot diverge, which is the property
`citation_scorer_for` exists to guarantee.

### 3.1 The judge must emit a SET, not one excerpt

`_judge_prompt_identify` (`generate.py:225`) already implements the right *call shape*: closed-set
identification over numbered excerpts, **one call**, verifiable reply ("the reply must be one of the
offered numbers"; *"naming which excerpt governs is harder to bluff than agreeing"*).

⚠️ **But it returns exactly one excerpt, and B′ needs a set.** Porting it naively collapses citations
to a single context — precisely the failure `min_keep` exists to prevent, measured 2026-08-12 as
**19 of 34 zero-cite rows caused by margin collapse**. The warrant prompt must therefore admit a
set ("reply with every excerpt number that governs, or none"), and unparseable replies must fall
back to the current reranker scorer rather than to an empty set.

### 3.2 `select_citations` needs no change — the judge fits the existing protocol

`select_citations` consumes `scorer.rerank(answer_text, contexts) -> [(chunk, score)]` descending,
keeps `s >= top - margin`, and floors the kept set at `min_keep`. A warrant judge satisfies this
**as-is** by scoring **1.0 for governing excerpts and 0.0 otherwise**: with `margin = 0.35` and
`top = 1.0` the keep test is `s >= 0.65`, which admits exactly the governing set and nothing else,
while `min_keep` still guards the all-zero case.

So W1 is a new `Reranker`-shaped backend and **no edit to `select_citations`**. That matters for
interpretation as much as for effort: the margin/`min_keep` semantics the two prior B′ arms were
measured under are preserved bit-for-bit, so a W1-vs-control difference is attributable to the
criterion and not to a changed keep rule.

### 3.3 A degeneracy probe runs FIRST and can abort the arm

Per `qwen15b-cannot-follow-instructions`: probe before preregistering any
generator-transforms-text intervention. Before the cohort run, on the frozen 50-row
`eval/probes/screen_v1.jsonl`, measure **parseable-reply rate**. If the judge cannot return a
parseable set on **≥ 80%** of rows, the arm is **abandoned before the cohort run** and recorded as a
no-op, not as a negative result. 1.5B is expected to fail this outright (0.0% instruction-following,
T-Screen 2026-08-20); the judge therefore runs at **7B**, which is the only size measured to follow a
prompted instruction (47.6%).

---

## 4. Endpoints

**Cohort.** The perfect-retrieval subset, **recomputed on the live index and persisted with its
corpus hash**. ⚠️ It is *not* a stored artifact and is index-dependent: R2 measured **201 of 204**
eligible where the prior index gave 206, and *every* prior-index reference value was wrong
(`stale@1` 1→7, `stale@3` 83→100, `zero_cite` 19→14). **Recompute, never quote.**

| role | metric | note |
|---|---|---|
| **PRIMARY** | `citation_precision` | the channel where B′'s effect is measured large (§1.2) |
| **GUARDRAIL** | zero-cite rows | the NLI failure shape (§1.3); see §6.2 |
| **GUARDRAIL** | `citation_recall` | must not fall below the armed floor |
| SECONDARY | `citation_recall` (as effect), parseable-reply rate, per-query latency | reported, not decisive |
| CONFIRMATORY | primary + guardrails split by `label_tier` | CS1: 68.8% of the gate is model-labelled |

Per-row records are captured via `SEBI_RAG_EVAL_ROWS` (landed 2026-08-20) so the label-tier split
and the composition analysis are available **without a re-run**. Both R0 arms lacked this and could
not be decomposed.

---

## 5. Arms

**Control** — B′ with the current cross-encoder scorer, `margin=0.35`, `min_keep=1`. Production
today.

**W1** — B′ with the warrant judge backend, same `margin` semantics where applicable, same
`min_keep`, judge at 7B.

**Rejected in advance:**
- Sweeping the warrant prompt across variants and reporting the best — that refits to the observed
  set (the `superseded_penalty` lesson, and the reason §8 exists).
- Tuning `margin` in the same arm — two variables, uninterpretable result.
- Any arm that also changes the generator — R0 already answered that question, and confounding it
  back in would waste the answer.

---

## 6. Decision rule — fixed in advance

Adopt W1 **only if all three hold**:

1. **`citation_precision` increases** on the recomputed cohort.
2. **Zero-cite does not increase.** Zero tolerance on direction. This is the NLI failure shape
   (19 → 54) and the single most likely way for a warrant judge to fail; a precision gain bought by
   citing less is not the trade this is testing.
3. **`citation_recall` stays at or above its armed floor** (read `eval/golden/gate_v7.json`, do not
   quote a doc table).

**If 1 holds but 2 or 3 fails → REJECT.** Recorded as rejected, not as "promising, needs tuning".

**⚠️ Effect-size floor, fixed now because it was missing last time.** The `superseded_penalty`
confirmatory run *"specified a direction and no minimum effect size"* and consequently adopted
nothing on a 1-row gain at p=1.000. This spec requires the primary to clear **+0.02 absolute**
`citation_precision` (~+10% relative on an observed ~0.19, matching §7.2's ≥10% rule) — a direction
alone is not sufficient.

---

## 7. Confirmation required before adoption

W1 clearing §6 on the cohort is **not** adoption. Required before arming anything:

- Full `eval_json_full` (n=260) against the armed floors, `floors_ok: true`.
- ⚠️ **Floors are model-dependent** (`project_context.md` §7.4, added 2026-08-20). W1 introduces a
  7B judge into the citation path. If the gate is re-derived, it must be re-derived under W1, and
  measured under W1 — `eval_generator_for` / `citation_scorer_for` guarantee this cannot silently
  diverge. **A W1 measurement compared against control-derived floors is a category error, not a
  pass.**

---

## 8. Not permitted after seeing the result

- Changing the primary endpoint, the guardrails, or the +0.02 effect-size floor.
- Re-running with a different warrant prompt and reporting that instead. If the first prompt fails
  the degeneracy probe (§3.3), the arm is abandoned — a second prompt is a **new preregistration**.
- Reporting the cohort result as a gate result, or deriving/arming any floor from the cohort.
- Quoting a prior-index cohort value (§4).
- Recording a §6-failing result as "directionally positive".

---

## 9. Implementation notes and the cost premise

**Files.** `src/sebi_rag/generate.py` — a `"warrant"` branch in `citation_scorer_for` (which
already dispatches `"reranker"` | `"nli"` and raises on unknown kinds), a warrant prompt beside
`_judge_prompt_identify`, and a set-returning parser with reranker fallback. **No change to
`select_citations`** (§3.2). ⚠️ `citation_scorer_backend` exists in `settings.py:78` (default
`"reranker"`) but is **not currently present in `config.toml`** — the arm selects it via
`SEBI_RAG_CITATION_SCORER_BACKEND`, leaving production config untouched, and it is added to
`config.toml` only on adoption.

**Hard constraints.** No new field on `CircularMeta` (`segment.py:131` → 78,630 chunks). No edit to
`*_spaces.py` or root `app.py`. `pipeline._apply_lineage`'s as_of branch untouched.

**⚠️ Cost premise, stated honestly.** A 7B judge call per query, in production, on top of
generation. From the 2026-08-20 clean runs: 7B generation is ~8.5 s/query at p50 and the full gate
is ~44 min. Adding a judge call plausibly doubles per-query latency against `timeout_s = 30`, and
means **two models resident** if the generator stays at 1.5B. **This is not a blocker to measuring
W1, but it is a blocker to shipping it**, and it must be measured (§4 secondary) rather than
assumed. If W1 clears §6 but cannot meet the latency budget, the honest outcome is "criterion
validated, deployment blocked" — recorded as such, not quietly adopted.

⚠️ Per `latency-probes-need-two-runs`: any latency figure reported from this arm requires **two
runs**, one with `SEBI_PROBE_ORDER=reverse`. A single run invented a timeout tail on 2026-08-20.

---

## 10. OUTCOME (recorded after execution)

*Not yet run.*
