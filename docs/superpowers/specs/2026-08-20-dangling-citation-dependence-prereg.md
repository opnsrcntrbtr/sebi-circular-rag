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

## 6. OUTCOME (recorded after execution)

*Not yet run.*
