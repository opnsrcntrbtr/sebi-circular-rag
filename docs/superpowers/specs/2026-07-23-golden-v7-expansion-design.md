# Golden v7: n≥250 stratified eval set with chunk-level labels and an external slice

**Date:** 2026-07-23
**Status:** Approved (design review 2026-07-23)
**Predecessors:** golden_v5 (frozen, n=56, current CI gate), golden_v6 (frozen, n=56 seed
in the enriched schema, `review_status: seeded`, `relevant_chunks` empty),
probes_v1 (n=25, diagnostic, separate), golden_asof_v1 (n=13, separate runner).

## 1. Problem

Every retrieval A/B since iv1 has been decided on n=56, where one query flip moves
recall@10 by ±1.8 points and the archived verdicts show p=1.000 on 0–2 discordant
queries. The 2026-07-23 adversarial architecture panel ranked eval growth as the gate
for all further retrieval work. Three defects to fix at once:

1. **Power:** n=56 cannot detect the effect sizes being engineered.
2. **Granularity:** labels are circular-level only; `relevant_chunks` exists in the
   v6 schema but is empty, and the harness never consumes it.
3. **Independence:** all labels were authored by the pipeline authors; the glossary
   intervention (`expand.py`) was even tuned on named probe failures. No label has
   ever been checked by anyone (or anything) outside the project.

## 2. Decisions locked at design review

| Decision | Choice |
|---|---|
| External slice | Hybrid: user blind-labels 30 rows via a packet; Gemini (key present in env) independently adjudicates 100 rows; the 30 are a subset of the 100 for three-way agreement |
| Strata mix | "Proposed mix" (§4), n=260 total, ~19% abstain |
| Gate policy | Self-expanding: CI reports full v7 but hard pass/fail is computed only over `review_status == "adjudicated"` rows; v5/v6 frozen read-only |
| Build approach | Approach A: deterministic scripted machinery for sampling/mining/pooling/packets/agreement; Claude judgment only for query drafting and pooled-chunk relevance, in resumable batches |

## 3. Row schema (v7)

v6 schema plus three additions, one change:

```json
{
  "id": "v7-tmp-041",
  "query": "…",
  "relevant_circulars": ["SEBI/HO/…"],
  "relevant_chunks": [{"doc": "SEBI/HO/…", "quote": "verbatim source substring"}],
  "answer_contains": "…",
  "must_contain": ["…"], "must_not_contain": ["…"],
  "must_not_cite": ["SEBI/HO/… (optional, temporal stratum)"],
  "abstain": false,
  "as_of": null,
  "task_type": "temporal_supersession",
  "difficulty": "hard",
  "expected_citation_level": "chunk",
  "rationale": "…",
  "label_source": "v7-miner-lineage | golden_v5 | …",
  "review_status": "draft | seeded | adjudicated"
}
```

- **`relevant_chunks` is span-anchored** (`{doc, quote}`), not chunk-ID-anchored.
  Quotes are verbatim substrings (≥40 chars, whitespace-normalized on comparison) of
  the source circular's text, resolved to chunk IDs **at eval time** by substring
  match over that doc's chunks. Rationale: chunk IDs embed section headings and the
  chunker has already changed once (nominee-bug fix); quotes survive re-chunking. A
  quote that resolves to zero chunks is a hard `validate_golden` error, so
  re-chunking drift is loud, never silent. Resolution to multiple chunks (overlap
  windows) is fine: all matching chunk IDs count as relevant.
- **`as_of`** (optional ISO date): harness passes it to `pipeline.query(as_of=…)`.
  Full-pipeline mode only; the golden_asof_v1 selector-mode runner is untouched.
- **`must_not_cite`** (optional): circular numbers that must NOT appear in
  `answer.citations` — used by the temporal stratum (predecessor circular). Harness
  reports the violation rate.
- The 56 v5-lineage rows keep their existing ids; new rows use `v7-<stratum>-NNN`.
- Annotation artifacts (packets, returned labels, per-annotator votes, κ) live in
  `eval/golden/v7_annotations/`, never in golden rows. Golden carries only the
  final label + `review_status` + `label_source`.

## 4. Strata (n=260: 56 carried + 204 new; ~207 answerable / ~53 abstain)

| task_type | carried | new | total | Source & generation rule |
|---|---|---|---|---|
| title_direct | 30 | 10 | 40 | Circulars sampled stratified by year × issuing department; query asks the subject naturally |
| body_paraphrase | 15 | 45 | 60 | Non-heading body chunks sampled; query re-expresses the provision in lay vocabulary |
| numeric_table | 0 | 30 | 30 | Chunks matching numeric/annexure patterns (`%`, lakh, crore, days, "Annexure", thresholds); query asks for the number/deadline; `must_contain` = the literal |
| temporal_supersession | 0 | 40 | 40 | Mined from `lineage.json` `superseded_by` pairs (1,348 entries) where both docs are in-corpus. 25 undated: gold = successor, `must_not_cite` = predecessor. 15 dated: `as_of` set between predecessor and successor issue dates so gold = **predecessor** (the pool-exhaustion adversarial shape); ≥3 of these with `as_of` predating the predecessor → `abstain: true` |
| multi_hop | 0 | 20 | 20 | Circular pairs joined by reference edges (lineage `edges`) or shared regulatory basis; query answerable only with both; `relevant_circulars` lists both |
| repealed_basis | 0 | 20 | 20 | Circulars with `regulatory_basis_status == "repealed_basis"` (74 available); query asks the requirement; `must_contain` includes `"repealed"` so the pipeline's advisory note is asserted |
| hard_negative | 10 | 30 | 40 | Near-domain unanswerable (RBI/IRDAI/MCA lookalikes, SEBI topics absent from the 705-circular corpus); `abstain: true` |
| far_negative | 1 | 9 | 10 | Out-of-domain; `abstain: true` |

Abstain accounting: carried 11 + new hard/far negatives 39 (30 + 9) + ~3 dated
temporal abstains (budgeted inside temporal's 40) ≈ 53 abstain, ≈ 207 answerable.

Difficulty is assigned per row at drafting time (`easy`/`medium`/`hard`) with the
constraint that every stratum contains ≥20% hard.

## 5. Anti-leakage rules (binding on every generation step)

1. **One-shot drafting.** Queries are drafted from sampled source text only and are
   frozen before any retrieval runs. No drafting step may iterate a query against
   the retriever until it succeeds/fails — that is how the glossary overfit
   happened, in reverse.
2. **No glossary consultation.** Paraphrase drafting must not read `expand.py`.
   After drafting, a script tags rows whose query tokens collide with GLOSSARY keys
   (`glossary_overlap: true` in the sidecar, not in golden) so glossary-dependence
   can be analyzed later.
3. **Negatives may use retrieval for verification only.** A BM25 sweep confirming
   the corpus has no governing document for a negative query is verification of
   absence, not optimization, and is allowed.
4. **Seeded determinism.** All sampling/mining uses seed 20260723; scripts are
   idempotent and re-runnable.

## 6. Chunk-label protocol (pooled judging)

For each answerable frozen query, `build_pool.py` assembles a candidate pool
(cap ~20, deduped): BM25 top-15 (raw query) ∪ dense top-15 ∪ RRF+cross-encoder
top-15 ∪ all chunks of the gold circular(s) containing any `must_contain` literal.
Claude judges each pooled chunk — relevant iff it contains the governing provision,
not merely the topic — and records the verbatim supporting quote, which becomes the
span anchor in `relevant_chunks`. Judging happens in resumable batches with a work
queue (`v7_annotations/pool_queue.jsonl`); each judged row carries the batch id.
Pooled labeling is standard TREC practice; chunks outside the pool are presumed
non-relevant for metric purposes.

## 7. External slice

- **Sampling:** 100 rows stratified proportionally across all 8 strata (negatives
  included); 30 of the 100 additionally form the human packet.
- **Human packet:** self-contained HTML in `v7_annotations/packet_human/` — per row:
  the query + shuffled pooled excerpts (no scores, no ranks, no system answers) +
  "which excerpt(s) contain the governing provision, or none?" + a free-text
  expected-answer literal. Returns as CSV; `ingest_packet.py` merges it.
- **Gemini leg:** same protocol via API (`GEMINI_API_KEY`, model configurable via
  `GOLDEN_GEMINI_MODEL`, default `gemini-3-flash-preview`), responses cached to
  `v7_annotations/gemini/` so reruns are free; resumable.
- **Agreement & promotion:**
  - Gemini-only rows (70): Gemini agrees with Claude labels → `adjudicated`;
    disagrees → user-arbitration queue.
  - Three-way rows (30): human + Gemini + Claude all agree → `adjudicated`; any
    disagreement → user-arbitration queue (user's decision is final and promotes).
  - Both externals agreeing on the same alternative label overrides Claude's label.
  - **Exception:** dated `as_of` temporal rows never auto-promote — they enter the
    arbitration queue regardless of agreement, and promote only after the as-of
    retrieval fix merges (§11), so the gate cannot inherit a known-broken behavior.
  - Agreement unit: per row, the *set* of excerpts marked governing (or "none")
    must match exactly; κ is computed on that row-level match, per annotator pair,
    per stratum.
  - `agreement.py` emits `reports/golden_v7_agreement.md`: Cohen's κ per annotator
    pair per stratum + Clopper-Pearson CI on Claude-label accuracy.
- The 56 v5-lineage rows are grandfathered `adjudicated` (they have gated CI for
  weeks). Expected gate size immediately after the external pass: ~156 rows
  (56 + ~100), growing later via user arbitration/spot-review batches.

## 8. Harness & gate changes

`eval_harness.py`:
- `resolve_chunk_spans(rows, chunks)` — span→chunk-ID resolution (shared with
  `validate_golden`).
- Chunk-level metrics: `chunk_recall_at_k`, `chunk_mrr`, computed over rows with
  non-empty `relevant_chunks` against `retrieved_ids`; circular-level metrics
  unchanged (continuity with v5 history).
- `as_of` passthrough; `must_not_cite` violation rate.
- `run_eval` keeps its signature; the report gains a `gate` sub-report computed
  over the `adjudicated` subset. The CI emitter script and
  gate thresholds switch from golden_v5 to the v7 adjudicated subset; abort
  thresholds are re-derived once on that subset with the existing bootstrap
  machinery (`stats.py`) before the flip lands.

`benchmark.py`: `validate_golden` rails extended — id uniqueness/format, strata
counts match §4, every non-abstain row has ≥1 `relevant_circulars`, every
`relevant_chunks` quote resolves against the live corpus, `as_of` well-formed,
abstain rows have no gold labels, `must_not_cite` only on temporal rows.

## 9. New code layout

```
scripts/golden_v7/
  mine_strata.py        # samplers + lineage/regulation miners → per-stratum candidate files
  build_pool.py         # candidate pools for labeling (runs the real index once)
  make_packet.py        # human HTML packet + CSV ingest
  gemini_adjudicate.py  # Gemini leg, cached, resumable
  agreement.py          # κ, promotion, agreement report
eval/golden/golden_v7.jsonl
eval/golden/v7_annotations/   # pools, packets, votes, queues (sidecar; committed)
```

Makefile: `make golden-v7-mine`, `golden-v7-pool`, `golden-v7-packet`,
`golden-v7-agree`, and `make eval` repointed at v7 after the gate flip.

## 10. Execution phases

1. **Rails first (TDD):** schema constants, `validate_golden` extensions, span
   resolver, harness chunk metrics + gate subset + `as_of`/`must_not_cite` — all
   offline-testable with HashEmbedder + tiny synthetic corpus.
2. **Mining:** `mine_strata.py` outputs per-stratum candidate source material.
3. **Drafting:** Claude drafts the 204 new rows in stratum batches (queries
   frozen at the end of this phase; `review_status: draft`).
4. **Pooling + labeling:** `build_pool.py`, then Claude judges pools in batches;
   `relevant_chunks` filled for all 210 answerable rows.
5. **External pass:** packet + Gemini leg + agreement + promotion.
6. **Gate flip:** threshold re-derivation on the adjudicated subset; CI emitter
   repointed; v5/v6 marked frozen in docs.
7. **Reporting:** agreement report, strata census, CLAUDE.md/status.md updates.

## 11. Out of scope

- The as-of hard-filter retrieval fix (panel recommendation #2) — v7's dated
  temporal rows are designed to *expose* that bug, not fix it. Expect those rows
  to fail until the fix lands; they are reported but only gate once adjudicated
  AND the fix is merged (they enter the arbitration queue like any dispute).
- M3 self-hybrid consolidation, parent-context assembly, generator upgrade
  (panel recommendations #3–4).
- Probes_v1 and golden_asof_v1 stay separate diagnostic sets, unchanged.

## 12. Risks

- **Claude drafting/labeling bias** — mitigated by the external pass, the
  arbitration queue, and the agreement report making residual disagreement
  visible rather than averaged away.
- **Gemini availability/quality** — cached + resumable; model swappable by env;
  worst case the human packet alone still yields an external slice (30 rows).
- **User turnaround on the packet** — gate still grows via the Gemini-only leg;
  the packet blocks only the three-way slice.
- **Dated temporal rows fail by design pre-fix** — explicitly handled in §11 so
  the gate cannot be poisoned by known-broken behavior.
