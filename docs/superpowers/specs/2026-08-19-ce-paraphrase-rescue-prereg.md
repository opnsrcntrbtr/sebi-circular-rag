# CE Paraphrase Rescue — Preregistered Analysis

**Written:** 2026-08-19, **before** the rescue pass is implemented or run.
**Status:** analysis plan frozen. Deviations get recorded as deviations, not edited away.
**Supersedes as the active thread:** `2026-08-13-hybrid-gate-prereg.md` §10b (score-floor cohort).

---

## 0. Correction to the 2026-08-18 diagnostic — read this first

`scripts/score_floor_diagnostic.py:46` sets `GATE = 0.42` and classifies a row as
`CE_MISMATCH` when the cross-encoder's `ce_top` falls below it. **0.42 is the wrong
constant.** It is the `SubjectSimJudge` threshold (`generate.py:322`) — a cosine
subject-line similarity floor on a different scale and a different signal.

The cross-encoder score floor is `Settings.abstain_threshold` = **0.05**
(`settings.py:66`, `config.toml [service]`), and it is what both the API (`api.py:150`) and
the eval harness (`eval_json.py:66`) pass to `answer_with_abstention`. The `0.40` default on
`pipeline.py:20` is a dataclass default that neither path uses.

Ground truth, from running the production pipeline on all four rows
(`scripts/analysis/abstention_reason_check.py`, `reports/abstention-reason-check-2026-08-19.json`):

| Row | ce_top | vs 0.05 floor | production behaviour |
|---|---|---|---|
| para-mfmaster | 0.3577 | 7.2× above | **answers, cites the relevant circular** |
| para-glitch | 0.0631 | 1.3× above | **answers, cites the relevant circular** |
| para-mfborrow | 0.0296 | below | abstains, `reason=score_floor` |
| para-pricedata | 0.0114 | below | abstains, `reason=score_floor` |

**Two of the four "CE_MISMATCH" rows are not failures at all.** They answer correctly today.
The real cohort is **2 rows**, and it matches the `score_floor` rows already recorded in
`docs/status.md` on 2026-08-13 (para-mfborrow, para-pricedata) — status.md was right; the
2026-08-18 diagnostic introduced the error.

Everything below uses 0.05.

Incidental finding: para-glitch's boilerplate pileup (six near-identical "Penalty on
malfunction of software used by broker" clauses) is **already handled** — supersession
demotion pushes those older master-circular vintages down, dropping the observed `ce_top`
from 0.1024 (undemoted, as the diagnostic measured it) to 0.0631 (production), with the
correct 2026 circular in the context window and cited. No pool-hygiene work is warranted.

## 1. Why

Two answerable golden_v7 rows abstain with `reason=score_floor`. In both, the relevant
document is retrieved and **ranked first** by the cross-encoder, which then scores it near
zero:

| Row | rerank_top | relevant doc CE rank | subject_sim |
|---|---|---|---|
| para-mfborrow | 0.0296 | 1 | 0.5922 |
| para-pricedata | 0.0114 | 1 | 0.5233 |

Not a recall failure, not a ranking failure. The cross-encoder puts the right document first
and then refuses to score it.

### What these queries have in common

Every domain term is replaced by a lay synonym:

| Row | query says | corpus says |
|---|---|---|
| para-mfborrow | "short-term bank loan", "same-day cash mismatch", "exiting unitholders" | "Intraday Borrowings", "settlement mismatch", "redemption" |
| para-pricedata | "exchange quotes", "teaching institute that is not a regulated entity" | "price data", "educational purposes", "unregulated entities" |

Query length is not the discriminator — these are 15 words, and the `para-*`/`body_paraphrase`
rows that pass are 12–15 words. The discriminator is vocabulary-substitution distance.

### The floor is not the problem, and cannot be tuned around

`scripts/analysis/score_floor_utility.py` computes `rerank_top` exactly as production does
(retrieve → rerank → supersession demotion) over all 245 non-as-of golden_v7 rows
(`reports/score-floor-utility-2026-08-19.json`):

| | count |
|---|---|
| correct abstentions caught by the floor (`abstain=True`, below 0.05) | **29 of 41** |
| answerable rows lost to the floor (`abstain=False`, below 0.05) | **2 of 204** |

The floor earns its place: it catches every far-negative (`v7-fn-*`, 0.0001–0.0006) and most
hard negatives. And the two false abstentions sit **inside** the true-positive band, not below
it:

```
caught correct abstentions:  0.0001 ............ 0.0462
false abstentions:                0.0114   0.0296
first abstain row above floor:                        0.0578
```

No threshold separates them. Lowering the floor to rescue para-pricedata (0.0114) releases
~25 correct abstentions with it. **Threshold tuning is dead here — now by measurement, with
the correct constant, rather than by assertion.**

### Probe: the cross-encoder is capable, it is being asked the wrong question

`scripts/analysis/ce_query_reform_probe.py` rescores the **same captured pool** — no
re-retrieval, no index change — under four query variants
(`reports/ce-query-reform-probe-2026-08-19.json`):

| Row | orig (control) | reform | title | subq |
|---|---|---|---|---|
| para-mfborrow | 0.0296 | **0.9943** | 0.9964 | 0.9961 |
| para-pricedata | 0.0114 | **0.9774** | 0.9937 | 0.9914 |
| _(para-mfmaster)_ | 0.3577 | 0.9234 | 0.9949 | 0.9916 |
| _(para-glitch)_ | 0.1024 | 0.9982 | 0.9991 | 0.9988 |

The `orig` arm reproduces the recorded `ce_top` to 4 decimals, so the replay is faithful.
Under a domain-vocabulary query both target rows clear 0.05 by two orders of magnitude, and
`argmax_is_relevant` is True.

**⚠️ The probe's variants were hand-written with knowledge of the gold document.** They
establish a *ceiling* — the cross-encoder can score these chunks 0.97–0.99 — and they falsify
"the reranker is too weak for this corpus". They do **not** establish that an automatic
rewriter without gold knowledge finds that vocabulary. That is what this experiment tests.

### Hypotheses this retires

- **"Boilerplate competition"** — see §0: supersession demotion already handles it, and
  para-glitch answers correctly.
- **"Degenerate stub chunk"** (para-mfmaster's rank-1 chunk is a 3-line notification stub) —
  the row answers correctly, and the same stub scores 0.9234 under `reform`.

Both were plausible from the pool dump alone. Measurement rules them out.

## 2. The trade this is measuring

The score floor refuses to answer when no retrieved context is relevant enough, and §1 shows
it catches 29 of 41 correct abstentions. A rescue pass that re-scores with a rewritten query
**weakens that guard by construction**: any query can be rewritten into something the
cross-encoder likes.

- **Benefit:** rescuing answerable queries whose vocabulary is lay rather than statutory.
- **Risk:** releasing correct abstentions — a hard negative or far negative rewritten into
  SEBI vocabulary, scoring high against topically-adjacent context.

With 2 rows to rescue and 29 to hold, the guardrail is the experiment.

**Stated in advance:** a 2-row rescue is a small prize. The repo rejected `superseded_penalty`
0.5 on a 1-row gain (2026-08-13). If the guardrail costs anything at all, this should not
ship. It is preregistered anyway because the mechanism — paraphrase collapse at the CE stage —
is now demonstrated and will recur as the corpus and query mix grow.

## 3. Method

**Rescue-pass only.** The rewrite fires **only** when the original query has already failed the
floor — 31 of 245 non-as-of rows. Queries that pass the floor are untouched bit-for-bit, so
the 204 answering rows cannot be disturbed.

```
reranked = rerank(query, pool)             # unchanged
if rescuer and reranked[0].score < floor:  # 31 of 245 rows
    q2 = rescuer.rewrite(query, reranked[:5])
    alt = rerank(q2, pool)                 # SAME pool — no re-retrieval
    if alt[0].score >= floor:
        reranked = alt
```

Fixed properties, frozen here:

- **Same pool.** Retrieval is not re-run. The rescue cannot repair a recall failure and is not
  credited for one.
- **The rewriter never sees the gold label.** It sees the query and the top-5 reranked pool
  chunks (pseudo-relevance feedback). In both target rows the relevant doc is rank 1 in that
  window — that is the mechanism, not a leak.
- **Lineage semantics preserved.** As-of exclusion / `superseded_penalty` demotion is applied
  to the rescued list by the same code path as the original list. A rescue cannot smuggle a
  superseded circular past supersession handling.
- **Deterministic.** Greedy decoding, `max_tokens=48`. Reruns must be byte-identical.
- **Off by default.** `[service] paraphrase_rescue = false` until §6 says otherwise.

## 4. Endpoints

Cohort: the **31 non-as-of golden_v7 rows with `rerank_top < 0.05`** — 2 answerable, 29
correctly abstaining. Row ids are fixed in `reports/score-floor-utility-2026-08-19.json`
before the rewriter exists.

- **PRIMARY — `rescued`**: of the **2** answerable rows (para-mfborrow, para-pricedata), how
  many reach `rerank_top >= 0.05` after the rescue **with a chunk from the relevant circular
  as argmax**. Scoring high on the wrong chunk is not a rescue and counts 0.
- **GUARDRAIL — `false_positive`**: of the **29** correctly-abstaining rows, how many the
  rescue lifts to or above the floor.
- **SECONDARY — `rewrite_degenerate`**: rewrites that are empty, unchanged from the input,
  over 40 words, or not a question / noun phrase. A high count means the 1.5B rewriter is the
  bottleneck, not the design.
- **COST — `rescue_latency_ms`**: median added latency on rows where the rescue fires.

## 5. Arms

| Arm | Rewriter |
|---|---|
| **Control** | none (production today) |
| **R1** | `MLXQueryRewriter`, Qwen2.5-1.5B-Instruct-4bit, PRF prompt over the top-5 pool chunks' subject lines + section headings |

Single arm by design. Three alternatives are **rejected in advance**, recorded so they are not
silently reintroduced:

- **Glossary expansion** (`expand.py`): 26 single-token synonyms. These failures are multi-word
  concept substitutions ("short-term bank loan" → "intraday borrowing"). Extending the glossary
  to cover two known rows is fitting the intervention to the eval set.
- **Deterministically appending pool subject lines to the query**: boosts whichever documents
  already ranked top, for every query, opening the floor almost everywhere. Cannot be guarded.
- **A stronger cross-encoder**: the probe shows the incumbent already scores these chunks
  0.97–0.99. Model capacity is not the constraint.

## 6. Decision rule — fixed in advance

1. Discard R1 if `false_positive > 0`. Releasing a correct abstention is worse in this domain
   than keeping a false abstention. Zero tolerance, same rule as the hybrid gate prereg §6.
2. Adopt only if `rescued == 2` of 2. At this cohort size a 1-row rescue does not justify an
   LLM call in the query path — see §2.
3. If `rewrite_degenerate >= 50%` of fired rows → the verdict is **"rewriter too small"**, not
   "hypothesis false". Record it as such; re-running with a larger local model is a new arm.
4. If R1 qualifies under 1+2 → proceed to §7. Otherwise keep the current gate, record the null,
   and leave the flag off.

## 7. Confirmation required before adoption

The cohort measurement in §4 measures **gate behaviour on 31 rows**. It is not a shipping
verdict. Any arm selected by §6 must be confirmed by a full `eval_json_full` run (MLX
generator, B′ on) reporting, against the armed floors in `eval/golden/gate_v7.json`:

| Metric | Floor |
|---|---|
| abstention_accuracy | 0.934 |
| citation_recall | 0.8169 |
| citation_precision | 0.1577 |
| context_recall | 0.874 |
| ndcg_at_10 | 0.6512 |

`floors_ok: true` required. A cohort result alone is **not** grounds to enable the flag.

## 8. Not permitted after seeing the result

- Relaxing the zero-false-positive guardrail to admit a rescuing arm.
- Editing the rewriter prompt after seeing which rows it fails, then re-reporting as if
  preregistered. A prompt change is a **new arm**, recorded alongside this one, not instead.
- Swapping the primary to `rerank_top` improvement (continuous, always-favourable) in place of
  the row count.
- Counting a row as rescued when the argmax chunk is not from the relevant circular.
- Lowering the 0.05 floor in the same experiment. Single variable.
- Re-adding para-mfmaster or para-glitch to the cohort. §0 shows they answer correctly; they
  are not failures and cannot be credited as rescues.

## 9. Implementation notes

New module `src/sebi_rag/paraphrase_rescue.py`:

```python
class QueryRewriter(Protocol):
    def rewrite(self, query: str, chunks: list[Chunk]) -> str | None: ...
```

`MLXQueryRewriter` loads its own quantized model and returns `None` on a degenerate rewrite
(empty / unchanged / >40 words) so the caller falls through to the unmodified abstention.

Wiring is in `pipeline.py:query`, **not** `generate.py`. The lineage/as-of block
(`pipeline.py:52-79`) is extracted to a helper so the original and rescued lists pass through
identical supersession handling; `answer_with_abstention` is untouched. The rewritten query is
recorded on `Answer.confidence["rescue_query"]` for audit — `confidence` is an existing `dict`
field, so no dataclass field is added.

Hard constraints this change must respect:

- **No new field on `CircularMeta`** (`segment.py:131` does `asdict(meta)` → 78,630 chunks).
- **No edit to `*_spaces.py` or root `app.py`** — CPU-only HF Spaces demo, separate path.
- Config lives under `[service]`, not `[spaces]`.

Measurement harness: `scripts/analysis/ce_rescue_cohort.py`, reporting §4's four endpoints
over the 31 below-floor rows fixed in `reports/score-floor-utility-2026-08-19.json`.

## 10. OUTCOME (recorded after execution)

**Run:** 2026-08-19, `scripts/analysis/ce_rescue_cohort.py`,
`reports/ce-rescue-cohort-2026-08-19.json`. Arm R1 as specified in §5, flag left off.

### §4 endpoints

| Endpoint | Result | Rule |
|---|---|---|
| PRIMARY `rescued` | **0 of 2** | §6.2 requires 2 |
| GUARDRAIL `false_positive` | **2 of 29** | §6.1 requires 0 |
| SECONDARY `rewrite_degenerate` | **23 of 31 (74.2%)** | §6.3 threshold is 50% |
| COST `rescue_latency_ms` | 501 ms median | — |

### Decision: **R1 REJECTED**

Rule 1 fires first and is disqualifying on its own. Rule 3 also fires, and the two together
say something sharper than either alone.

**The guardrail breach.** Two near-domain hard negatives were rewritten into plausible
regulatory questions that then cleared the floor:

| Row | before | after | rewrite |
|---|---|---|---|
| v7-hn-002 | 0.0313 | **0.0794** | "Are there RBI guidelines on how often gold used as collateral must be revalued by NBFCs?" |
| v7-hn-022 | 0.0046 | **0.0685** | "In the context of the SEBI circular, what is the maximum period after which a subscriber can make a partial withdrawal from the National Pension Scheme?" |

v7-hn-022 is the clearest failure: the rewriter injected the phrase *"In the context of the
SEBI circular"* into a question about the NPS — a scheme SEBI does not regulate — manufacturing
the surface anchor the floor exists to detect the absence of. This is the risk named in §2,
realised exactly as described.

**The rewriter failed on both target rows.** Qwen2.5-1.5B-Instruct-4bit returned the input
**verbatim** for para-pricedata and para-mfborrow, caught by the `unchanged` degeneracy check:

```
para-mfborrow  in:  "Can an asset manager take a short-term bank loan to bridge a
                     same-day cash mismatch when paying out exiting unitholders?"
               out: "Can an asset manager take a short-term bank loan to bridge a
                     same-day cash mismatch when paying out exiting unitholders?"
```

So the model rewrote where rewriting was harmful and declined to rewrite where it was needed.
Consistent with the same model's known behaviour elsewhere in this project (it emits zero
parseable bracket citations under Option A selective citations, 2026-08-03).

### What this does and does not establish

- **Establishes:** arm R1 — this rewriter, this prompt — is rejected, and would have cost 2
  correct abstentions in exchange for nothing.
- **Does not establish:** that the paraphrase-rescue *design* fails. Per §6.3 the primary
  endpoint was never actually exercised: the rewriter produced no rewrite at all on either
  target row, so `rescued = 0` measures the rewriter, not the mechanism. The §1 probe ceiling
  (0.977–0.994 under a hand-written domain query) is untouched by this run.
- **Also does not establish** that a larger rewriter would pass. The guardrail failure is not
  obviously a capacity problem — a *more* capable rewriter may be *better* at manufacturing
  plausible SEBI phrasing for an out-of-domain question, which is precisely the failure mode.
  Any larger-model arm must be judged on the guardrail first.

### Per §8, not done

The prompt was **not** edited after seeing these results, and no arm was re-run. A different
rewriter or prompt is a **new arm** requiring its own preregistration recorded alongside this
one.

### Disposition

`paraphrase_rescue = false` in `config.toml`. The code ships inert and tested (22 tests,
`tests/test_paraphrase_rescue.py`) so a future arm needs a rewriter, not a re-implementation.
The two false abstentions (para-mfborrow, para-pricedata) remain **known limitations**,
alongside the 3 documented on 2026-08-13.

### If a next arm is attempted

The guardrail is the hard part, not the rescue. A candidate design that attacks it directly:
constrain the rewrite to **vocabulary drawn from the retrieved pool** (extractive
substitution) rather than free generation, so an out-of-domain query cannot acquire SEBI
phrasing that is not already in its own retrieved context. That is a different mechanism, and
it needs its own prereg.
