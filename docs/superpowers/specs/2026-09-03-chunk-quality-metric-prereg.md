# Preregistration — Intrinsic Chunk-Quality Metric

**Written before implementation.** Design in §1 and the validation requirement in §3 are fixed
as of this document's commit. No detector code has been written.

## 0. Motivation

Three chunker fixes have shipped against the retrieval unit with **zero production metric**:

| Version | Date | Judged by |
|---|---|---|
| `2026-09-01-table-row-merge` | 2026-09-01 | chunk-quality inspection only |
| `2026-09-02-table-row-gap-merge` | 2026-09-02 | chunk-quality inspection only |
| `2026-09-03-toc-long-title-merge` | 2026-09-03 | chunk-quality inspection only |

Each entry in `docs/status.md` states the same reason: `golden_v7` (n=260) cannot resolve
chunk-boundary effects this small (`golden-v7-underpowered` — n≈834 needed for 4pp ndcg). That
reasoning is sound, but it leaves three shipped changes to `hierarchical_chunk()` — which every
one of 83,752 current chunks passes through — resting entirely on eyeballing one TOC document.
This spec is the gap-filler: a metric independent of golden-set power, computed directly over the
persisted chunks.

## 1. Design

Two rates computed over `data/index/chunks.jsonl`, grouped by the chunk's stamped
`chunker_version` (already present per `retrieve.py:243`) so all versions still represented in
history can be compared side by side:

- **`shredded_row_rate`** — chunks that are a bare numbered stub (e.g. `"5."` or `"3.\n"`) with no
  substantive body text following it within the chunk.
- **`orphan_fragment_rate`** — chunks that are a title/label continuation fragment with no owning
  numbered row in the same chunk (the TOC-wrapped-title and finstat-row-label failure shapes
  named in `docs/status.md`'s 2026-09-02 scoping entry).

Both are corpus-level counts, reported as `count / total_chunks_for_that_version` — no query, no
golden set, no generator involved. This makes them cheap enough to compute after every chunker
change and diff against the previous version's rate.

**Detector is a fresh regex/heuristic pass**, not a reuse of `_is_table_row_candidate` /
`_is_table_row_filler` from `segment.py` — reusing the production discriminator to validate itself
would be circular (a chunk that dodges the discriminator by construction would also dodge a
detector built from the same predicate).

## 2. Validation — the hard requirement

`docs/status.md`'s 2026-09-02 scoping entry already flags its own prevalence numbers as unusable:
"crude regex proxy, not a validated count … neither number is the actual defect count". Building
a detector calibrated against that proxy and reporting its output as ground truth would repeat the
exact mistake that entry warns against.

**Before any rate is reported:**
1. Hand-label a stratified sample from the three surfaces already named in that entry:
   - ~30 docs from the 198 flagged by the bare `"N.\n"` line proxy (TOC-candidate surface)
   - ~20 docs from the 49 flagged by `Sl.`/`No.` + numbered lines (finstat-table-candidate surface)
   - ~20 docs matching **neither** proxy, as a negative control
2. For each sampled doc, hand-mark every chunk as shredded / orphan / neither, reading the actual
   extracted text (not the proxy regex's guess).
3. Run the detector over the same sample; report **precision and recall against the hand labels**,
   not against the proxy counts.
4. Only if precision and recall are both reported (any values — this step does not gate adoption,
   it gates whether the *rate* is trustworthy enough to quote) does the corpus-wide rate get
   written into `docs/status.md` or cited as evidence for a chunker decision.

## 3. Decision rule — fixed in advance

This spec produces a **measurement tool**, not an intervention — there is no adopt/reject arm.
The rule is about trustworthiness of the output, not about a threshold to clear:

- Detector precision/recall against the hand-labeled sample **must be reported alongside every
  rate** it produces, permanently — a rate without its own validation numbers next to it is not
  a valid citation of this metric.
- If detector precision on the hand-labeled sample is below ~0.7, the metric is reported as
  "directional only, not yet a reliable count" rather than silently used as if precise.

## 4. Not permitted after seeing the result

- Reporting `shredded_row_rate` or `orphan_fragment_rate` without the precision/recall numbers
  that validate the detector producing them.
- Retroactively scoring the three already-shipped fixes and treating that retroactive score as
  proof any one of them was net-positive for retrieval quality — this metric measures chunk
  *shape*, not downstream retrieval effect; a chunk-quality improvement and a retrieval-quality
  improvement are different claims.
- Using this spec's detector as the basis for a next interleaved-layout fix without a separate,
  explicit design decision — `docs/status.md`'s 2026-09-02 scoping entry deliberately treats
  scoping and implementing as separate decisions, and this spec preserves that separation.
- Extending the detector to also fire on golden_v7 query-answer text — it is corpus-only by
  design; conflating it with retrieval evaluation reintroduces the power problem this metric
  exists to route around.
