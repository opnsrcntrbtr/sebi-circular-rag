# B′ attribution scorer (NLI) — Preregistered Analysis

**Written:** 2026-08-12, **before** the scorer was implemented or any measurement taken.
**Status:** analysis plan frozen. Deviations get recorded as deviations, not edited away.

---

## 1. Hypothesis

B′ currently scores answer↔context with `CrossEncoderReranker` (bge-reranker-v2-m3), a
**query↔document relevance** model. Citation selection needs **attribution**: does this context
support this answer. That is a model-task mismatch.

Measured consequence (2026-08-12, 206 golden_v7 rows where retrieval found *every* relevant doc):

| | B′ OFF | B′ ON (reranker) | B′ ON + min_keep=3 |
|---|---|---|---|
| zero-cite rows | 15 | **34** | 29 |
| citation_recall | 0.9248 | 0.8204 | 0.8447 |
| citation_precision | 0.1240 | 0.2361 | 0.1973 |

19 rows cite nothing **solely** because B′ is on. On 14 of those the relevant document is not even
top-3 by answer-relevance — so no `margin`/`min_keep` value recovers them. That is the specific
failure an entailment scorer should fix.

**H1:** an NLI entailment scorer reduces zero-cite rows below 34 while holding
citation_precision at or above the gate floor.

## 2. Test bed — and why this subset

`eval/golden/golden_v7.jsonl`, restricted to the **206 rows where `recall >= 0.999`** under the
current production pipeline (retrieval found every relevant document).

This subset is the correct test bed precisely because **retrieval is not a variable in it**. Any
citation failure there is attributable to the citation stage alone. Retrieval is unchanged by this
intervention, so the subset is stable across arms — verified by asserting the arm's per-row
`recall` vector is identical to the control's before any comparison is made. **If that assertion
fails, the comparison is void and must be reported as void, not repaired.**

## 3. Primary endpoint — single, decisional

**Zero-cite count**: number of rows in the subset with `citation_recall == 0`.

Chosen because it is the *catastrophic* failure — a grounded answer citing nothing relevant is
qualitatively worse for a legal tool than one citing partially. Mean citation_recall hides it.

- **Test:** `sebi_rag.stats.paired_delta` on the per-row binary indicator `citation_recall == 0`,
  two-sided randomization, 10,000 resamples, seed 0 — the same function used for iv8/iv11.
- Discordant pair counts (fixed→broken, broken→fixed) reported alongside; they are the raw
  evidence and must appear whatever the p-value says.
- **α = 0.05**, two-sided, uncorrected — one preregistered primary endpoint needs no correction.

## 4. Secondary (descriptive, never decisional)

`citation_recall`, `citation_precision`, per-stratum zero-cite counts, wall-clock scoring latency.

## 5. Guardrail — a veto, not an endpoint

**citation_precision must stay ≥ 0.1896** (the armed `gate_v7.json` floor). An arm that fixes
zero-cite by citing everything is the B′-OFF baseline in disguise (precision 0.1240) and is
refused regardless of the primary endpoint.

Latency veto: > 3× the current B′ scoring cost.

## 6. Decision rule — fixed in advance

| Outcome | Decision |
|---|---|
| zero-cite < 34, p < 0.05, **and** precision ≥ 0.1896 | **Adopt.** Switch B′ backend to NLI, re-arm the gate, update status. |
| zero-cite < 34, p ≥ 0.05, precision ≥ 0.1896 | **Hold.** Directionally right, underpowered. Do not switch the default. |
| precision < 0.1896 | **Reject** — guardrail breached, regardless of zero-cite. |
| zero-cite ≥ 34 | **Reject.** The mismatch hypothesis is wrong; stop pursuing it. |

## 7. Model

`cross-engine NLI cross-encoder`, premise = context text, hypothesis = answer text, score =
P(entailment). The entailment class index is read from the model's `id2label` at load time and
**never hardcoded** — a wrong index silently inverts the scorer and would look like a null result.

Primary candidate: `cross-encoder/nli-deberta-v3-base`. If it cannot be obtained or loaded, that is
recorded as an execution blocker; substituting a different model class is a deviation and must be
labelled as one.

## 8. Not permitted after seeing the result

- Switching the primary endpoint to citation_recall because it looks better.
- Tuning the entailment threshold or `min_keep` post hoc and reporting the best.
- Dropping strata (e.g. numeric_table) as "unrepresentative".
- Reporting the arm against a re-derived subset rather than the frozen 206 rows.

---

## 10. OUTCOME (recorded 2026-08-12, after execution)

Model loaded: `cross-encoder/nli-deberta-v3-base`, entailment index **1, read from `id2label`**
(not assumed). Direction smoke-tested before the run: supporting context 0.9945, unrelated 0.0017.

Subset-stability assertion (§2) **passed**: 0 rows differ in retrieval between arms; frozen subset
= 206 rows.

| | B′ OFF | B′ reranker (control) | B′ NLI |
|---|---|---|---|
| **ZERO-CITE (primary)** | 15 | **34** | **82** |
| citation_recall | 0.9248 | 0.8204 | 0.5752 |
| citation_precision | 0.1240 | 0.2361 | 0.4263 |

Primary endpoint, paired on the binary zero-cite indicator:
**Δ = +0.2330** (worse), 95% CI [+0.1748, +0.2961], **p = 0.0001**.
NLI **fixed 1** row and **broke 49**.

### Decision, per the §6 rule fixed in advance

zero-cite (82) ≥ 34 → **REJECT.** Default stays `citation_scorer_backend = "reranker"`.
Production behaviour unchanged.

### Why — and why this result is NOT informative about H1

The §9 limitation is the dominant explanation, and it is worse than anticipated.
`ExtractiveStubGenerator.generate` returns `contexts[0].text` **verbatim**. So B′ under the stub
asks the NLI model: *does context_i entail context_0's own text?* That is trivially true for
context_0 and false for nearly everything else. The kept set collapses to the single top context
by construction, and every row whose top context is not relevant becomes a zero-cite.

This is visible in the numbers: precision nearly doubles (0.2361 → 0.4263) while recall collapses
(0.8204 → 0.5752) — the signature of keeping far fewer citations, not of scoring them better.

The relevance reranker is not exposed to this degeneracy in the same way: it scores topical
relevance, which stays high for paraphrases and related provisions, so it keeps a wider set.

**Therefore:** the mismatch hypothesis (H1) is **neither confirmed nor refuted**. The experiment as
preregistered rejects the NLI backend *under the stub generator*, which is the honest reading of
the rule as written — but it does not establish that entailment scoring is wrong for production,
because the stub makes the premise/hypothesis pair degenerate.

This confound was preregistered in §9 rather than discovered afterwards. It is recorded as a
limitation of the design, not used to overturn the decision.

### What a valid test requires

Re-run with a **real generated answer** (MLX `Qwen2.5-1.5B-Instruct-4bit`, the production
generator) so `answer_text` is a genuine paraphrase rather than a copy of `contexts[0]`. Only then
does entailment(context, answer) measure attribution. That run is more expensive (real generation
over 206 rows) and is a separate preregistered experiment — **the gate floors were themselves
derived under the stub, so switching the generator changes the comparison basis and needs its own
control arm.**

---

## 11. ADDENDUM — Run 2 under the real MLX generator (frozen 2026-08-12, before execution)

Run 1 (§10) was confounded: the stub returns `contexts[0].text` verbatim, making the NLI
premise/hypothesis pair degenerate. This addendum re-tests H1 with a genuine generated answer.

**Change from Run 1 — exactly one thing:** `ExtractiveStubGenerator` → `MLXGenerator`
(`mlx-community/Qwen2.5-1.5B-Instruct-4bit`, greedy decoding, deterministic).

**Both arms are re-run under MLX.** The Run-1 control is not reused: it was measured under the
stub, and comparing an MLX treatment against a stub control would confound the generator change
with the scorer change — the same class of error this addendum exists to correct.

| Arm | Generator | B′ backend |
|---|---|---|
| Control | MLXGenerator | `reranker` |
| Treatment | MLXGenerator | `nli` |

**Why the pairing is clean:** `answer_with_abstention` generates the answer text *before*
`select_citations` runs, and greedy decoding is deterministic. Given identical contexts, both arms
see **identical answer text**. The arms therefore differ in citation selection and nothing else.
This is asserted, not assumed — see the validity checks below.

### Validity checks (any failure ⇒ result reported VOID, not repaired)

1. Per-row `recall` identical across arms (retrieval untouched).
2. Per-row `abstention` identical across arms (the gate runs pre-generation).
3. The frozen subset remains the same 206 perfect-retrieval rows.

### Endpoints, α, and decision rule

**Unchanged from §3–§6.** Primary = zero-cite count on the 206-row subset, paired randomization
test on the binary indicator, α=0.05 two-sided. Guardrail: citation_precision ≥ 0.1896.

| Outcome | Decision |
|---|---|
| zero-cite < control, p < 0.05, precision ≥ 0.1896 | **Adopt** the NLI backend |
| zero-cite < control, p ≥ 0.05, precision ≥ 0.1896 | **Hold** — directionally right, underpowered |
| precision < 0.1896 | **Reject** — guardrail breached |
| zero-cite ≥ control | **Reject** — H1 refuted under a valid test |

### Pre-declared interpretation

The MLX control's absolute numbers will differ from the stub control's (34 zero-cite). That is
expected and is **not** itself a finding about B′ — it is the generator change. Only the
MLX-control vs MLX-treatment contrast is decisional. The stub-vs-MLX control difference may be
reported descriptively but must not be used to argue for or against the NLI backend.

---

## 12. OUTCOME — Run 2 (recorded 2026-08-12, after execution)

Generator: `MLXGenerator`, `mlx-community/Qwen2.5-1.5B-Instruct-4bit`, greedy.

**Validity checks — all PASS:**
1. Per-row `recall` identical across arms ✅
2. Per-row `abstention` identical across arms ✅
3. Frozen subset = 206 rows, **identical row set to Run 1** ✅

| | STUB rerank | STUB nli | **MLX rerank (control)** | **MLX nli (treatment)** |
|---|---|---|---|---|
| **zero-cite (primary)** | 34 | 82 | **19** | **54** |
| citation_recall | 0.8204 | 0.5752 | 0.8981 | 0.7354 |
| citation_precision | 0.2361 | 0.4263 | 0.1948 | 0.2204 |

**Primary endpoint (MLX control vs MLX NLI):** Δ = **+0.1699 worse**,
95% CI [+0.1165, +0.2233], **p = 0.0001**. NLI **fixed 2** rows and **broke 37**.
Guardrail: citation_precision 0.2204 ≥ 0.1896 — not breached, but irrelevant given the primary.

### Decision, per §11 rule fixed in advance

zero-cite (54) ≥ control (19) → **REJECT. H1 is refuted under a valid test.**

Default remains `citation_scorer_backend = "reranker"`. Production unchanged.

### What is now established

The stub confound is removed: answer text is genuine generated prose, so
entailment(context, answer) measures attribution as intended. The result stands on its own.

**The model-task mismatch hypothesis is wrong.** An entailment scorer is *worse* than the
relevance reranker for this citation-selection task, and by a wide, highly significant margin in
the same direction as Run 1. Two independent runs, one confounded and one clean, agree.

Plausible mechanism (not tested, offered as explanation rather than finding): SEBI citation
selection wants contexts that are *about* the provision the answer discusses. Entailment is
stricter — a context can be the governing provision without textually entailing a paraphrase of
it, particularly for `numeric_table` and `lineage_supersession` rows where the answer restates a
figure or a supersession relation the context implies but does not assert.

**Stop pursuing attribution/NLI scorers for B′.** The remaining 19 zero-cite rows under production
are a smaller problem than the stub measurement suggested (34), and B′'s catastrophic-failure rate
is roughly half what was believed.

### Descriptive, explicitly non-decisional (§11)

The MLX control beats the stub control on zero-cite (19 vs 34) and citation_recall
(0.8981 vs 0.8204) but is *worse* on citation_precision (0.1948 vs 0.2361).

⚠️ **Flag, not a finding:** the armed gate's `citation_precision` floor (0.1896) was derived under
the **stub** generator, while production runs MLX. On this 206-row subset MLX precision is 0.1948 —
about 0.005 above that floor. The denominators differ (gate = 260 adjudicated rows incl. abstain;
this = 206 answerable perfect-retrieval rows), so **this is not evidence the gate is at risk** and
must not be reported as such. It is a question worth answering with a matched measurement.

## 9. Standing limitation

This measures citation selection under `ExtractiveStubGenerator`, matching how the gate floors were
derived. It does **not** measure the production MLX generator's answer text. A scorer that helps the
stub may behave differently on real generated answers; that is a separate experiment.
