# Is retrieval saturated, or can the eval set not show otherwise?

**2026-08-20.** Reproduce with `PYTHONPATH=src python scripts/analysis/corpus_coverage.py`
(`reports/corpus-coverage-2026-08-20.json`). Read-only. **This memo measures exposure, not
demonstrated harm** — see §5, which is the part that keeps it honest.

## 1. Why this got asked

R3 went void on 2026-08-20 because a cross-reference stratum could not be mined: 374 of 507
`references` edges point at circulars outside the 730-record corpus. The interesting part is not
that R3 failed — it is *why*. The corpus could not supply the documents that would make retrieval
hard. That invites a question about every retrieval conclusion this project has drawn.

## 2. The eval set is conditioned on corpus membership

**155 of 159 golden_v7 gold circulars (97.5%) are corpus members.** This is not a flaw in the
labelling; it is unavoidable. You cannot mark a document as the gold answer if you do not hold it.

The consequence is structural: **golden_v7 can only pose questions the corpus can already answer.**
Pool `R@50 = 0.9861` is therefore partly a measurement of *"can we find a document we know we
hold"* — a question whose answer was never seriously in doubt.

## 3. The corpus is a recent slice of a much larger body of law

| | |
|---|---|
| circulars held | **730** |
| issued before 2022-01-01 | **61 (8.4%)** |
| distinct circulars referenced by held documents | 1,377 |
| ...**absent** from the corpus | **982 (71.3%)** |

The missing set concentrates in 2010–2021 — precisely the years the corpus does not cover.

## 4. ⚠️ But master circulars inflate that number ~10×

A master circular rescinds a long schedule, so its citations are **bookkeeping, not substantive
cross-reference**. Splitting by document class changes the picture materially:

| document class | docs | reference mentions | unresolvable | % |
|---|---|---|---|---|
| master | 135 | **8,115** | 6,805 | 83.9% |
| **ordinary** | 595 | **788** | **512** | **65.0%** |

Ordinary circulars make only 788 references in total — about 1.3 each. **SEBI's ordinary circulars
are largely self-contained**, which is a genuine mitigating fact and cuts against the alarming
headline. The substantive gap is **267 distinct missing targets**, not 982.

## 5. In-eval exposure — and what it does *not* show

Restricting to the 87 **non-master** gold documents:

| | |
|---|---|
| non-master gold docs citing a circular we do not hold | **36 (41.4%)** |
| distinct unresolvable circulars they name | **85** |
| golden_v7 rows resting on such a document | **42 of 260 (16.2%)** |

By stratum: body_paraphrase 13, lineage_supersession 7, multi_hop 7, repealed_basis 6,
title_direct 5, hard_negative 3, numeric_table 1 — concentrated in the reasoning strata.

⚠️ **This is exposure, not harm.** A gold document citing an absent circular does **not** establish
that the question needs that circular to be answered correctly. **No row has been shown to be
answered wrongly because of a missing document.** Anyone quoting the 16.2% as a defect rate is
misreading it — that inference is exactly the step this memo declines to take without the test in §7.

## 6. The temporal machinery cannot be exercised

The project ships supersession tracking, `as_of` date-scoped queries, `governing_on`,
`regulatory_basis_status`, and repealed-basis advisory notes. All of it reasons about *law over
time*. At **8.4% pre-2022 coverage**, that reasoning has almost nothing to reason over: **14 of the
15 `as_of` golden rows are dated 2022 or later**, and the single 2013 row probes an era where the
corpus holds a few dozen documents.

This is the sharpest finding here, because it is a coherence problem rather than a measurement one.
Either the corpus should grow to match the machinery, or the machinery's scope should be stated
honestly as "current law, 2022 onward". Both positions are defensible. **Holding both at once is
not**, and today the project holds both.

## 7. What would settle it — cheap, and not yet run

The open question is binary: is `R@50 = 0.9861` a property of the retriever, or of how the eval set
was built? The test is the 42 exposed rows: **does answering them correctly require the dangling
citation, or is the gold document self-sufficient?**

That is exactly R3 §3.3's F2 filter ("answerable from A alone?") applied to existing rows rather
than mined pairs — so the protocol is already written and already preregistered. It needs the oMLX
judge on `127.0.0.1:8001`, which is **not currently running**. A 42-row judged sample is minutes of
compute, not hours.

- If most of the 42 **need** the absent document → saturation is an artifact of eval construction,
  and corpus coverage becomes the binding constraint on the whole roadmap.
- If most are **self-sufficient** → saturation is real, the roadmap's ranking stands, and this memo
  reduces to a scope note about §6.

## 8. ⚠️ The incentive runs the wrong way

Corpus expansion would **lower the gate metrics**. Adding documents adds distractors: retrieval gets
genuinely harder, `recall_at_k` and `ndcg_at_10` fall, and the armed floors — derived on the
730-circular frame — would need re-derivation. `rescore_runs.py` already raises
`IncomparableFramesError` across frames, so this cannot be papered over.

So the gate, as currently armed, **structurally penalises the change most likely to improve the
system**. Any corpus-expansion work must preregister that a metric drop is *expected and is not a
failure*, or the gate will veto the right decision. Recording this now, before any number moves,
is the only way that pre-commitment is worth anything.
