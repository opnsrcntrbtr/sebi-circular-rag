# Preregistration — hard_negative Subject-Gate False-Positive Investigation

**Written before execution.** Decision rule in §3 is fixed as of this document's commit. No golden
row has been relabeled and no threshold has been changed.

## 0. Motivation

The abstention root-cause investigation
(`docs/superpowers/specs/2026-09-03-architecture-review-w1-diagnostics.md`) found 10 of 21
`abstention_accuracy` mismatches are false answers on `hard_negative`-stratum golden rows
(`v7-hn-003, 007, 010, 011, 012, 026, 027, 028, 030`, plus `hn-settle`), all with `subject_sim`
0.432–0.5512 — clearing the `SEBI_RAG_SUBJ_THRESHOLD=0.42` OR-gate on subject similarity alone.
The bge-side audit (same corpus, same day) caught only 4 of these same rows; jina's reranking
surfaces 10. Two structurally different explanations fit the same data and this spec exists to
tell them apart before either is acted on:

- **(A) Labeling issue**: some of these rows are, like the `docs/status.md` "Hard Negative Fix
  (2026-07-30)" precedent (`hn-buyback`, `hn-takeover`, `hn-esop`, etc. — a *different* set of
  ids, relabeled from `abstain: True` to `False` because the corpus genuinely covers them), rows
  the corpus now has real coverage for and should not be labeled hard-negative at all.
- **(B) Judge-precision gap**: the rows are correctly labeled hard negatives (topically adjacent,
  legally distinct, no real corpus coverage), and `SubjectSimJudge`'s 0.42 OR-gate is genuinely too
  permissive for jina-surfaced near-domain contexts — a reranker-quality regression on
  discrimination, not a labeling error.

Conflating these would produce the wrong fix in either direction: relabeling a genuinely-hard
negative would corrupt the golden set (this repo's `refusal-criteria.md` explicitly refuses
fabricating/altering evidence without cause); tightening the judge threshold to fix a labeling
error would trade away true-answer accuracy for no reason.

## 1. Method

**Step 1 — read the corpus coverage for each of the 10 rows**, the same way the 2026-07-30 fix
did: for each row's query and its `must_not_contain`/rationale fields (already present in
`golden_v7.jsonl`), check whether `data/corpus/circulars.jsonl` has a circular that actually,
substantively covers the topic (not just shares vocabulary) — a hand read, not an automated
proxy, matching the discipline the 2026-07-30 fix and the W4 chunk-quality spec's validation
requirement both use.

**Step 2 — for rows confirmed as (A) labeling issues**, this spec stops there and hands off to the
existing golden-set relabeling process (`scripts/golden_v7/relabel_repooled.py` /
arbitration queue) — not something this spec executes itself.

**Step 3 — for rows confirmed as (B) genuine hard negatives**, inspect the actual reranked
`contexts` window `SubjectSimJudge.score()` was called against (available via
`ans.context_ids` — extend `scripts/analysis/abstention_mismatch_audit.py`'s existing per-row
capture, already logging `confidence`, to also dump the top context chunk texts for these specific
10 ids) to see whether the surfaced contexts are genuinely topically adjacent (a judge-precision
gap worth investigating further) or an artifact of some other retrieval bug (a different root
cause entirely).

## 2. Endpoints

| role | metric | source |
|---|---|---|
| PRIMARY | count of the 10 rows confirmed (A) labeling issue vs. (B) genuine hard negative | hand read, Step 1 |
| SECONDARY (only for (B) rows) | qualitative read of the surfaced context chunks: genuinely near-domain vs. an unrelated retrieval miss | Step 3 |

## 3. Decision rule — fixed in advance

1. If **all 10** are (A) → hand off entirely to the relabeling process; no judge/threshold change
   is warranted, and this spec's finding is "the abstention failure here is a golden-set defect,
   not a system defect."
2. If **all 10** are (B) → report as a genuine judge-precision gap; do **not** propose a specific
   threshold fix in this spec (that is a separate, future prereg with its own decision rule,
   mirroring the discipline `2026-09-03-abstain-threshold-drift-prereg.md` uses for the adjacent
   score-floor mechanism) — this spec's job is diagnosis, not remediation.
3. If **mixed** → report the split explicitly, row by row, rather than picking whichever bucket is
   larger and discarding the rest — a 6/4 split is two findings, not one weighted toward the
   majority.

## 4. Not permitted after seeing the result

- Relabeling any row's `abstain` field directly in `golden_v7.jsonl` as part of this spec's
  execution — relabeling goes through the existing arbitration process
  (`scripts/golden_v7/relabel_repooled.py`), which this spec does not invoke.
- Changing `SEBI_RAG_SUBJ_THRESHOLD` or `SubjectSimJudge`'s gate logic based on this spec's
  findings — diagnosis only, per §3.2.
- Treating a coincidental vocabulary overlap in the surfaced contexts as proof of (B) without
  reading whether the *topic*, not just wording, is genuinely adjacent — the 2026-07-30 fix's own
  root cause was exactly this kind of surface-level false signal in the other direction.
