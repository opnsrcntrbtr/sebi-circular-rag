# Preregistration — does golden_v7 depend on circulars the corpus does not hold?

**Written before execution.** §4 decision rules and §5 not-permitted are fixed as of this commit.
No judge call has been made.

Follows `docs/corpus-coverage-2026-08-20.md` §7 and R3's void
(`2026-08-19-crossref-eval-validity-prereg.md` §10).

---

## 1. The question, and why it decides more than it looks like

`docs/corpus-coverage-2026-08-20.md` established **exposure**: 42 of 260 golden_v7 rows (16.2%)
rest on a non-master gold document that cites a circular the corpus does not hold. It explicitly
declined to call that a defect rate, because a gold document citing an absent circular does not
establish that the question *needs* it.

This spec makes the missing inference testable. The answer decides which of two worlds the roadmap
is in:

- **Dependence is real** → pool `R@50 = 0.9861` is substantially an artifact of the eval being
  built from the corpus (gold documents are 97.5% corpus members — you cannot label a document you
  do not hold). "Retrieval is saturated" would then be scoped to a set that cannot express the
  dominant failure, and **corpus coverage becomes the binding constraint on the whole roadmap**.
- **Dependence is not real** → saturation stands as measured, the roadmap's ranking survives, and
  the coverage memo reduces to a scope note about the temporal machinery (§6 there).

## 2. Method

**Judge.** `Qwen3.6-35B-A3B-OptiQ-4bit` via oMLX at `http://127.0.0.1:8001/v1`, temperature 0.
⚠️ **Deviation recorded:** R3 §3.2 designates `Qwen3.6-35B-A3B-MLX-4bit`. The available build is the
**OptiQ** quantisation of the same base model. Same model family and size, different quantisation.
Recorded rather than silently substituted; it does not affect group comparison, since both arms are
judged by the identical build.

**Context construction.** Labelled evidence quotes (`relevant_chunks[].quote`, present on 100% of
both groups, median ~220 chars) are too short to assess self-sufficiency alone. Each quote is
located in its gold document and a **±6,000-character window** is taken around it; windows are
merged per row. Bounded, and it captures where a cross-reference pointer would sit.

**The judgement is verifiable, not self-reported.** Following `_judge_prompt_identify`'s design
("naming which excerpt governs is harder to bluff than agreeing"), the judge must **name** the
circular it says is required. A named circular is then checked against the corpus in code. A row
counts as *dependent* only when the judge names a circular that the corpus **does not hold**.
Saying "more information is needed" without naming a resolvable-and-absent circular does not count.

**Blinding.** The judge sees only the query and the window. It is never told which group a row is
in, that a group exists, or which references are held.

**Groups.** Treatment = the 42 exposed rows. Control = **all 56** rows whose non-master gold
document has **no** dangling citation. All rows used; no sampling.

⚠️ **The strata are unbalanced** — control is `title_direct`-heavy (14 vs 5), the easiest stratum,
which biases *against* finding a difference. §4 therefore requires the difference to survive a
stratum-matched sensitivity check, and that check is specified here rather than chosen later.

## 3. ⚠️ This design is deliberately conservative

Quote-anchored windows favour a self-sufficiency verdict: the quote was selected by the adjudicator
*as* the evidence for the answer. A pre-judge signal points the same way — only **3 of 48**
treatment quotes contain an unheld reference inline.

So the instrument **under-detects dependence**. That asymmetry is intentional and it sets how each
outcome may be read: **a positive finding is strong; a null is weak** and must be reported as
"this design did not detect dependence", never as "the documents are not needed".

## 4. Decision rule — fixed in advance

Let **T** and **C** be the dependent-row rates in treatment and control.

1. **T − C ≥ 20pp and T ≥ 30%**, surviving the stratum-matched check → **dependence established.**
   Corpus coverage becomes the binding constraint; the saturation conclusion is scoped, and
   retrieval work reopens under preregistration.
2. **|T − C| < 10pp** → **no dependence detected by this design.** Saturation stands. Report with
   the §3 conservatism caveat attached.
3. **10pp ≤ T − C < 20pp**, or the stratum-matched check does not survive → **inconclusive.**
   Record and stop. Do not re-slice to move it across a boundary.
4. **VOID** if any of: unparseable judge output on > 20% of rows; **C > T** (the instrument is not
   measuring what it claims); or the judge names circulars that appear nowhere in the supplied
   window on > 20% of dependent verdicts (fabrication).

**No outcome of this experiment ships code or moves a gate floor.** It re-ranks a roadmap.

## 5. Not permitted after seeing the result

- Changing the window size, the groups, the prompt, or the §4 thresholds and re-reporting as
  preregistered. Any change is a new run recorded alongside this one.
- Reporting outcome 2 as evidence that the corpus is adequate — §3 forbids that reading.
- Reporting outcome 3 as support for either side.
- Treating outcome 1 as licence to adopt any previously rejected retrieval arm. iv2/iv8/iv9/iv10/
  iv11 were rejected on their own endpoints and stay rejected.
- Quoting the 16.2% exposure figure as a defect rate. It never was one.

## 6. OUTCOME

### Run 1 — VOID (instrument failure)

`reports/dangling-dependence-2026-08-20-run1-VOID.json`. Numbers preserved for the record and
**must not be quoted**: they were produced by a parser reading text that is not an answer.

§4.4 fired on the fabrication guardrail — **28.6%** of dependent verdicts (2 of 7) named a
circular absent from the supplied window, against a 20% ceiling. Investigating *why* found a
deeper failure that invalidates every verdict, not just those two:

**The judge is a reasoning model, and its thinking never terminated.** With
`max_tokens = 1024`, a real prompt (1,638 prompt tokens) returned `finish_reason: length` after
1,024 completion tokens of unfinished chain-of-thought. Because the thinking block never closed,
oMLX could not split it out: `reasoning_content` came back **empty** and 3,955 characters of
partial reasoning landed in **`content`**. The model never emitted its answer at all.

The parser then read that reasoning as if it were a verdict. `"NEEDS" in reply` matched
deliberative text, and `REF_RE.search(reply)` took the **first circular number anywhere in the
reply** — frequently the excerpt's *own* number, which the model restates while analysing the
input. So `needs_held = 50`, `needs_unnamed = 22`, `sufficient = 18` are all artefacts.

⚠️ **Why the smoke test passed and the run did not.** The pre-run check used a 22-token prompt,
which the model finished comfortably, returning a clean `content` of `'SUFFICIENT'` with
`reasoning_content` correctly separated. Truncation only appears at realistic prompt lengths. A
smoke test on a toy input verified the transport, not the instrument — and running 98 rows on
that basis is what made the whole run disposable.

### Run 2 — instrument fixed

Per §5 this is **a new run recorded alongside run 1**, not a re-report of it. Fixes, all made
before observing any run-2 result:

1. **Thinking disabled** (`chat_template_kwargs: {enable_thinking: false}`), `max_tokens` 128.
   The task is a bounded extractive classification — does this excerpt defer to another circular —
   so deliberation is not required and a single strict line is. Verified on 4 rows: clean
   one-line replies in the preregistered format at ~2 s/row.
2. **`finish_reason == "length"` is now an explicit `__TRUNCATED__` marker**, never silently
   accepted as a reply.
3. **Strict parse**: last non-empty line only, prefix-anchored on `SUFFICIENT` / `NEEDS`, and the
   circular taken from *after* the `NEEDS` marker rather than from anywhere in the text.
4. **Normalised containment** for the fabrication check (whitespace/case), so a judge that
   reformats a circular number is not scored as fabricating one. The guardrail **threshold**
   (§4.4, 20%) is unchanged.

The sample also showed run 1's verdicts were unstable, not merely mis-parsed: `v7-bp-005` returns
`SUFFICIENT` under the fixed instrument where run 1 recorded `needs_unheld`.

### Run 2 result — §4.2: **no dependence detected by this design**

`reports/dangling-dependence-2026-08-20-run2.json`

| | dependent | n | rate |
|---|---|---|---|
| treatment (gold doc has a dangling citation) | **1** | 42 | **2.4%** |
| control (gold doc has none) | **0** | 56 | **0.0%** |
| **Δ** | | | **+2.4pp** |

Verdicts across all 98 rows: `sufficient` **91**, `needs_held` 3, `needs_unnamed` 3,
`needs_unheld` **1**.

**Validity — all §4.4 void checks clear:** unparseable **0.0%** (ceiling 20%), fabricated names
**0.0%** (ceiling 20%), C < T, 0 rows context-truncated.

**Determinism verified** (required by R3 §3.2, "re-runs must be byte-identical"): the run-2
request shape returns identical output on 4/4 repeats of a real 12,000-char row. ⚠️ Counter-
intuitively, *hardening* the sampler broke this — adding `top_k=1`, `top_p=1.0`,
`repetition_penalty=1.0` produced 3 different answers from 3 identical requests, while
`temperature=0` alone with server defaults was stable. Do not "fix" determinism by pinning
sampler parameters on this server.

§4.2 applies: **|T − C| = 2.4pp < 10pp.** Recorded as *no dependence detected by this design*.

### What this licenses, and what it does not

✅ **Saturation stands as measured.** The corpus-coverage memo's 16.2% exposure figure does **not**
translate into demonstrated dependence, and R1/R0′ remain the ranked roadmap items.

❌ **This is NOT evidence that the corpus is adequate** — §5 forbids that reading, and §3 explains
why: the instrument is deliberately conservative. Windows are anchored on quotes the adjudicator
selected *as* the evidence for the answer, so self-sufficiency is the outcome the design favours.
A null here is weak evidence, by construction.

⚠️ **A second, unplanned conservatism was introduced by the run-1 fix.** Disabling thinking was
necessary to get a parseable answer, but it means these are *undeliberated* judgements — and 91 of
98 rows returning `SUFFICIENT` is consistent with a model taking the cheap path. The user's oMLX
config sets `reasoning_effort: high` with `thinking_budget_tokens: 4096`, so a thinking-enabled
replication is well-defined: it needs `max_tokens > 4096 + answer` (≥5120), which is exactly what
run 1 lacked at 1024. **That replication has not been run**, and until it is, the null carries this
caveat as well as §3's.

### Root cause of run 1, confirmed from the server config

The user's model settings show `thinking_budget_enabled: true` with `thinking_budget_tokens: 4096`.
Run 1 allowed `max_tokens: 1024`. The model was budgeted 4× more reasoning than it was permitted to
emit, so `finish_reason: length` was **guaranteed** — not bad luck. Any thinking-enabled call on
this server must set `max_tokens` above the thinking budget plus the answer.
