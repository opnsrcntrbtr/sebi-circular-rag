# W1 Diagnostics — Live Stack Position (2026-09-03 architecture review)

Not a prereg — a diagnostic results log for W1.1/W1.2/W1.3 from
`/architecture-review`'s 2026-09-03 session. No production files (`eval/golden/gate_v7.json`,
`config.toml`) were changed by any run recorded here.

## W1.3 — Corpus-growth displacement (complete)

Script: `scripts/analysis/corpus_growth_displacement.py`. Retrieval + rerank only, no generator.
Output: `reports/corpus-growth-displacement-2026-09-03.json`.

**Pre-expansion set derivation.** The candidate archived `docids.tsv` files were checked first
and rejected: every one is a per-run *retrieved-doc* subset (313-886 distinct circulars), not a
full corpus manifest — none reconstructs anywhere near 730. Instead, filtering corpus records by
`provenance` parse-date < `2026-08-28` gives **exactly 730** records, matching
`docs/status.md`'s own "grown from 730" figure precisely. This is the set used below.

**Results** (214/260 golden_v7 rows have gold circulars entirely pre-expansion):

| Metric | Value |
|---|---|
| Mean post-expansion docs in fusion top-10 | 0.986 / 10 |
| Mean post-expansion docs in (reranked) context top-10 | 0.916 / 10 |
| Gold survival rate, fusion top-10 | 91.12% |
| Gold survival rate, context top-10 | 91.12% (identical in aggregate) |

**Reading.** Corpus growth occupies roughly 1 of 10 top-10 slots on average — real, but modest,
displacement. The aggregate gold-survival rate is numerically identical at both stages, but this
is **not** because reranking is neutral per row: 14 of 214 rows flip survival status between
fusion and context (checked directly — `per_row` in the output JSON), split roughly evenly between
rescues and demotions, and they cancel in the mean. 19 rows lose their gold circular already at
the fusion (pre-rerank) stage — that loss is attributable to retrieval/corpus composition, not to
the reranker swap, since the reranker never sees a document fusion didn't retrieve.

**Implication for the ndcg@10 drop (0.6512→0.5934 in the 2026-09-02 gate re-derivation):** an
~8.9% gold-loss rate at the fusion stage, on a corpus that grew from 730 to 1,490 circulars
covering years of additional master-circular history, is consistent with a retrieval-side (BM25
IDF shift + wider FAISS candidate pool) contribution to the drop, independent of whichever
fraction the reranker swap or the two chunker fixes contribute. This is descriptive evidence, not
a decomposition — see the plan's rejection of a formal ablation (power/validity, §W1 rationale) —
but it rules out "the reranker swap explains all of it" as the sole story.

**⚠️ Correction (2026-09-03, discovered investigating the abstention failure below): the "reranker
swap" contribution to the 2026-09-02 floor movement never actually happened in the script that
derives floors.** `derive_thresholds.py` deliberately never switches reranker (fixed on bge by
design, `docs/status.md:907`) — only the corpus-growth axis genuinely moved between the 2026-08-13
and 2026-09-02 derivations. This W1.3 diagnostic's own retrieval+rerank pipeline construction
(`scripts/analysis/corpus_growth_displacement.py`) correctly uses `retrieval_reranker_for`, so its
numbers above describe the real jina-reranked production system and are unaffected by this
correction — only the attribution of the *gate's* floor movement (not this diagnostic's own
findings) needed fixing. See `docs/status.md`'s 2026-09-03 correction entry.

## Follow-up investigation: root-causing the abstention_accuracy failure (2026-09-03)

W1.2 found `abstention_accuracy` failing (0.919 vs floor 0.9373). Per
`superpowers:systematic-debugging`, Phase 1 evidence gathering:

**False start, corrected.** A first diagnostic script (`scripts/analysis/abstention_mismatch_audit.py`)
copied `derive_thresholds.py`'s pipeline-construction pattern, which passes the raw
`CrossEncoderReranker` (bge) directly — correct for `derive_thresholds.py` (deliberate, fixed
floor baseline) but wrong for a script meant to reproduce what failed the gate. That first run
measured 0.9654 (9 mismatches) — a real bge-side number
(`reports/abstention-mismatch-audit-bge-2026-09-03.json`), but not the system that fails the gate.
Fixed to route through `retrieval_reranker_for(s.reranker_model, rer)`, matching `api.py`/
`eval_json.py`; the corrected run reproduces 0.9192 (21 mismatches,
`reports/abstention-mismatch-audit-jina-2026-09-03.json`), matching `eval_json.py`'s 0.919 exactly
— confirming this is a real, reproducible jina-side result, not run-to-run noise.

**Three independent, confirmed mechanisms** in the 21 mismatches (not one root cause):

1. **8 false abstentions via `score_floor`**, `rerank_top` clustered tightly at 0.0499–0.1135,
   just under `abstain_threshold=0.12` — spread across 6 task types (title_direct,
   body_paraphrase×2, lineage_supersession×2, multi_hop, repealed_basis, one hard_negative
   direction-flip). `abstain_threshold=0.12` was calibrated 2026-08-24 against the 730-circular
   corpus (`reports/jina-abstain-threshold-calibration-2026-08-24.json`) — 4 days *before* the
   2026-08-28 corpus expansion to 1,490. The score distribution these 8 queries sit in may have
   shifted since calibration; not yet confirmed against the original calibration's own score
   distribution.
2. **10 false answers on `hard_negative` rows**, `subject_sim` 0.432–0.5512 — all clearing the
   `SEBI_RAG_SUBJ_THRESHOLD=0.42` OR-gate on subject similarity alone, regardless of `section_sim`
   (several of which sit well below the 0.60 section threshold). `subject_sim` is computed by
   `SubjectSimJudge` over BGE-M3 embeddings of the *actually-reranked* top-k contexts — unchanged
   embedder, but a different reranker surfaces different contexts. The bge-side audit found only
   4 of these same rows failing this way; jina surfaces 10 — evidence the reranker choice, not the
   embedder, drives which near-domain hard-negative rows look "grounded enough."
3. **2 false abstentions via `subject_gate`** on `numeric_table` rows (v7-nt-013, v7-nt-025) with
   `rerank_top` 0.48–0.52 — the highest scores in the entire mismatch set, and near jina's own
   observed ceiling (max 0.67 across all 260 calibration rows), yet nowhere close to
   `HYBRID_THRESHOLD=0.85` (`generate.py:727`), so the near-ceiling override that would otherwise
   rescue an ungrounded-but-confident query never fires. **This directly confirms the
   HYBRID_THRESHOLD dead-code finding from earlier in this investigation as causally contributing**
   — reversing the initial read (first audit run, before the reranker bug was found, showed zero
   `subject_gate` mismatches and looked like a falsified hypothesis; the corrected jina-side run
   shows it is real, just smaller than initially guessed — 2 of 21, not the sole cause).

**Not yet investigated further** (each is its own recalibration/design decision, not something to
fold into this diagnostic pass, per `docs/status.md`'s existing precedent of rejecting the
adjacent rescue arm R1 on 2026-08-19 without a preregistered decision rule): whether
`abstain_threshold` needs re-calibrating post-corpus-growth, whether the hard-negative subject-gate
false-positive rate is a labeling issue (cf. the 2026-07-30 hard-negative relabeling precedent) or
a genuine judge-precision gap, and whether `HYBRID_THRESHOLD` should be recalibrated to jina's
score scale or removed.

## W1.2 — Live stack vs. currently armed floors (complete)

Run: `scripts/eval_json.py`, live stack (1,490 circulars, 83,752 chunks, chunker
`2026-09-03-toc-long-title-merge`), 260 golden_v7 rows. Output:
`eval/runs/live-stack-eval-2026-09-03.json`. `eval/golden/gate_v7.json` was only read, never
written, by this run.

**This is the first pass/fail measurement taken since the 2026-08-24 jina adoption / 2026-08-28
corpus expansion / three 2026-09-0[1-3] chunker fixes** — `docs/status.md:1542` named exactly this
measurement as the missing next step.

| metric | floor (armed 2026-09-02) | observed | margin | status |
|---|---|---|---|---|
| recall_at_k | 0.8397 | 0.888 | +0.0483 | PASS |
| context_recall | 0.8192 | 0.920 | +0.1008 | PASS |
| ndcg_at_10 | 0.5934 | 0.643 | +0.0496 | PASS |
| citation_recall | 0.7347 | 0.826 | +0.0913 | PASS |
| citation_precision | 0.1466 | 0.178 | +0.0314 | PASS |
| **abstention_accuracy** | **0.9373** | **0.919** | **−0.0183** | **FAIL** |

**`floors_ok: false`** (self-reported by `eval_json.py`'s gate block). Five of six metrics clear
the armed gate with healthy margin — the ndcg@10/recall/citation-recall drops from the 2026-09-02
re-derivation were not compounded by anything that happened since (the two chunker fixes shipped
after that derivation did not make retrieval worse; if anything the live numbers sit comfortably
above the newly-lowered floors). **Abstention accuracy is the one real fail**, missing its floor
by 1.83pp. Candidate causes not yet investigated: (a) generator/MLX run-to-run variance on
borderline SubjectSimJudge cases, (b) an interaction between the 2026-09-02/09-03 chunker fixes
(gap-merge, TOC-title-merge) and which chunks land in context for hard-negative/abstain rows,
(c) ordinary bootstrap noise given the floor's own `_FLOOR_CUSHION=0.005` is smaller than this
1.83pp gap. Not diagnosed further here — out of this diagnostic's scope; flagged as the concrete
next question for whoever picks up the abstention axis.

## W1.1 — Re-derive floors on live stack (complete)

`make golden-v7-gate` writes `DEFAULT_GATE_PATH` in place — captured immediately to
`eval/runs/gate-v7-rederive-2026-09-03.json`, then the pre-run armed file (backed up before the
run started) was restored. **Verified**: `git diff --exit-code eval/golden/gate_v7.json` clean —
the armed CI gate was not disturbed by this diagnostic.

| metric | armed (2026-09-02, chunker `table-row-merge`) | re-derived (2026-09-03, chunker `toc-long-title-merge`) | Δ |
|---|---|---|---|
| recall_at_k | 0.8397 | 0.8397 | 0.0000 |
| context_recall | 0.8192 | 0.8238 | +0.0046 |
| ndcg_at_10 | 0.5934 | 0.5934 | 0.0000 |
| citation_recall | 0.7347 | 0.7461 | +0.0114 |
| abstention_accuracy | 0.9373 | 0.9373 | 0.0000 |
| citation_precision | 0.1466 | 0.1500 | +0.0034 |

**Reading.** Two chunker versions' worth of drift (`table-row-merge` → `gap-merge` →
`toc-long-title-merge`) moved floors by at most +1.14pp, with three of six metrics unchanged
to 4 decimal places. This is an order of magnitude smaller than the 2026-09-02 reranker+corpus
re-derivation's 5-8pp moves, and well inside golden_v7's own noise floor (`golden-v7-underpowered`
memory: ~4pp resolution at n=216-260) — consistent with the two chunker fixes being genuinely
small, chunk-shape-only changes rather than the kind of stack change `refusal-criteria.md`'s
invalidation rule was written to catch. This does not mean chunker version should stay off that
rule's axis list (W2's spec already adds it, on the correctness argument that *any* stack
divergence should be fingerprinted, not on the size of this particular drift) — but it does mean
this specific past drift, while real, was not itself hiding a material regression.

## Answering the original review question

**Did retrieval quality regress?** Not further, as of the live stack — W1.2 shows five of six
gated metrics clear the (already-lowered) 2026-09-02 floors with 3-10pp of margin. The 5.78pp
ndcg@10 drop recorded at the 2026-09-02 re-derivation is real relative to the 2026-08-13
measurement, and is attributable to **corpus growth alone** (corrected above — the reranker
channel never actually changed in `derive_thresholds.py`): W1.3 shows corpus growth alone
displaces gold documents from top-10 in ~8.9% of eligible pre-expansion queries, consistent with
being the sole driver of that drop.

**The one metric that did fail live is abstention_accuracy** — a finding this diagnostic surfaced
that the 2026-09-02 entry's own numbers could not show, because no one had measured the live
stack against them until now. Root-caused to three independent, confirmed mechanisms (not one):
a score-floor threshold that may need recalibrating post-corpus-growth, a reranker-choice-dependent
false-positive rate on hard-negative rows via the subject-similarity groundedness gate, and a
hardcoded near-ceiling override (`HYBRID_THRESHOLD=0.85`) that was calibrated for bge's score
scale and is unreachable under jina's (max observed 0.67). None of these three has a chosen fix
yet — each needs its own preregistered decision, per this repo's existing precedent
(`docs/status.md`'s rescue arm R1, rejected 2026-08-19 for the adjacent CE-paraphrase-collapse
problem, without which a "fix" risks becoming an undisciplined threshold chase).

**Bonus finding, larger in scope than the abstention question that surfaced it:** the gate's
floor-derivation script (`derive_thresholds.py`) has, by design, never used the jina reranker on
any derivation since ADR-004 (2026-08-24) — a fixed bge-anchored quality bar, intentional and
documented (`docs/status.md:907`), but undocumented in the *dated* 2026-09-02 re-derivation entry,
which falsely claimed `reranker: jina-reranker-v3-mlx`. Corrected in `docs/status.md`,
`.claude/rules/refusal-criteria.md`, and `docs/project_context.md` (2026-09-03 entries/edits); the
gate-stack-fingerprint spec (W2) was itself amended before landing, since its original design would
have written the same false claim into `gate_v7.json` in machine-readable form.
