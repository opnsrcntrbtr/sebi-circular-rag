# SPLADE Learned-Sparse Third RRF Leg (iv11) — Design

**Date:** 2026-07-20
**Status:** approved (success criterion, model/license, architecture, data
flow, and measurement all chosen by user)
**Predecessor:** `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md`
§4 (#4 — learned sparse retrieval as third RRF leg, the last untried
ranked intervention) and §5.5 (iv10 targeted headers: insufficient, the
two stubborn probes shown to be answer-chunk-text gaps). Sibling
precedent: iv8 HyDE third-leg wiring (`hyde_text` opt-in additive leg).

## Problem & residual shift

Report §4 justified SPLADE against 5 `sparse_vocabulary_miss` failures
(para-freeze, probe-tbl-05, probe-sup-01, probe-par-01, probe-par-02 —
the same set as intervention #2). Since that report, iv6 (wrapped-clause
folding) and iv7 (glossary expansion) closed **4 of those 5**. The current
residual after iv10 is:

| set | id | bucket (original taxonomy) | class in A |
|---|---|---|---|
| probes | probe-par-03 | chunking_defect | candidate_miss |
| probes | probe-sup-04 | embedding_semantic_miss | candidate_miss |
| probes | probe-num-05 | fusion_ranking_loss | ranked_low |
| probes | probe-tbl-05 | sparse_vocabulary_miss | ranked_low |
| golden | para-aifmaster | embedding_semantic_miss | ranked_low |
| golden | para-parrva | embedding_semantic_miss | ranked_low |

Only probe-tbl-05 survives from SPLADE's original bucket. The residual is
now dominated by `embedding_semantic_miss` paraphrase gaps
(para-aifmaster: "Category II private pooled investment vehicle" vs
"Alternative Investment Fund"; para-parrva; probe-sup-04). SPLADE performs
*learned term expansion* — it sits between BM25's exact-match and dense's
full-semantic reach and expands both queries and documents into a shared
learned lexical space — so it is a plausible structural improver for
exactly these paraphrase gaps, even though its original narrow bucket is
mostly resolved.

**Success criterion (user decision):** treat SPLADE as a general recall
third-leg. Measure BM25+SPLADE fusion (B) vs the current BM25+dense (A)
across the full probes+golden set; success = net answer-level recall
improvement with **zero regressions vs A** (iv10's item-by-item
no-regression discipline). This does not pre-commit to fixing any specific
probe.

## Model & license (user decision)

`prithivida/Splade_PP_en_v1` — Apache-2.0, ~110M params, an independent
SPLADE++ reimplementation intended for production use. The Apache license
is clean for the project's publishable-datasets posture (`make
export-datasets` → `dist/datasets`), unlike `naver/splade-v3`
(CC-BY-NC-4.0, non-commercial). Standard HF transformers MLM head; runs on
MPS with `PYTORCH_ENABLE_MPS_FALLBACK=1`.

## Architecture (user decision)

SPLADE is a **non-destructive, opt-in third RRF leg**. Unlike iv9/iv10
(which rewrote chunk text and forced a dense re-embed, risking
corpus-wide embedding shift), a SPLADE leg is purely additive and
rank-fused: it never touches `dense.faiss` or the BM25 index. Two
consequences:

- **No snapshot/restore dance.** The existing index is never modified. A/B
  is "fuse 2 legs" vs "fuse 3 legs" against the *same* untouched
  dense+BM25 index. iv10's central operational risk (leaving a regressed
  index live) structurally cannot occur.
- **The iv9 scale lesson does not transfer.** iv9's regression came from
  injecting similar-register text into 23% of the *dense* embedding space.
  SPLADE weights live in a separate lexical space that meets the others
  only at the RRF rank-fusion step, so a **full-corpus** SPLADE index is
  correct here (a partial one would create coverage holes).

### Components

1. **`SpladeIndex`** (new class, `src/sebi_rag/splade.py`) — mirrors
   `SparseIndex`'s interface:
   - `build(texts: list[str]) -> None`: runs the Splade_PP MLM encoder over
     chunk texts (MPS, batched) to produce per-chunk sparse term-weight
     vectors, stored as a **scipy CSR matrix** (~77,859 docs × ~30,522
     vocab; ~15M nonzeros — trivial in memory).
   - `search(query: str, k: int) -> list[tuple[int, float]]`: encodes the
     query to a sparse weight vector, sparse dot-product against the CSR
     matrix, returns top-k `(idx, score)` in the exact tuple shape
     `rrf_fuse` already consumes.
   - `save(path)` / `load(path)`: persist/restore the CSR matrix and meta.
   - Dependency-injectable encoder (constructor takes an encode callable)
     so tests run offline with a hand-built fake — same pattern as iv10's
     `HeaderGenerator(fake)`.

2. **Persistence** — a separate artifact `data/index/splade.npz` (CSR:
   `data`, `indices`, `indptr`, `shape`) plus `data/index/splade_meta.json`
   (`{n, vocab_size, model, checksum}`), built once (~3.5h one-time MPS
   encode, cached), loaded in <1s thereafter. The artifact sits alongside
   the existing index files but is loaded only on demand.

3. **Wiring in `HybridRetriever.retrieve()`** — an opt-in leg mirroring the
   `hyde_text` precedent (iv8): when a `SpladeIndex` is attached and
   requested, append `self.splade.search(query, k_splade)` as a third
   ranking into `legs` before `rrf_fuse`. Off/absent by default →
   byte-identical current behavior. `rrf_fuse` is unchanged (it already
   accepts an arbitrary list of rankings).

4. **Pilot gate before the 3.5h encode** (iv9 go/no-go pattern) — encode
   just the ~6 residual-failure queries and their known answer chunks,
   print the shared/overlapping learned expansion terms, and confirm
   SPLADE actually assigns bridging terms across the paraphrase gap (e.g.
   the AIF query and the AIF answer chunk activate an overlapping term
   set). Go/no-go before committing the full-corpus pass.

## Data flow & persistence (user decision)

### Build path — `scripts/build_splade_index.py` (standalone)

Kept separate from `build_index.py` so the 3.5h SPLADE encode never
entangles with the routine dense/BM25 reindex.

1. Loads the same `data/corpus/circulars.jsonl` chunks in **identical
   order** to the dense index — critical, since RRF fuses on positional
   `idx` and `self.chunks[i]` must line up across all three legs.
2. Runs Splade_PP over chunk texts on MPS in batches
   (`PYTORCH_ENABLE_MPS_FALLBACK=1`, as the other encoders use).
3. Writes `data/index/splade.npz` + `splade_meta.json`. The stored `n`
   must equal the dense index's `n=77859`; a mismatch guard aborts the
   load rather than silently mis-fusing.

### Query path

At `retrieve()` time, when the SPLADE leg is active: encode the **raw
query** (no glossary expansion — SPLADE performs its own learned
expansion; the iv7 glossary stays on the BM25 leg only), sparse
dot-product against the CSR matrix, top-`k_splade=50`, appended as the
third ranking.

### Load path

`HybridRetriever.load()` gains an optional SPLADE load: if `splade.npz`
exists *and* the caller requests it, attach a `SpladeIndex`; otherwise the
retriever is exactly today's 2-leg object. The Spaces/CPU demo path (which
won't ship the SPLADE artifact) and all existing tests stay untouched.

### Deliberately unchanged

`expand_query` (BM25 leg only), the reranker, `rrf_fuse`'s `k_const=60`,
the dense index, and `build_index.py`'s default behavior. SPLADE is
strictly opt-in and additive at every layer.

## Measurement & gates (user decision)

A/B, iv10 discipline but non-destructive (nothing to restore — A is
reproducible on demand by leaving the leg off):

- **A (control):** current 2-leg retrieval (dense + BM25). Fresh benchmark
  into `eval/runs/iv11-a-probes/` and `eval/runs/iv11-a-golden/`.
- **B (treatment):** 3-leg (dense + BM25 + SPLADE), same untouched index.
  Benchmark into `eval/runs/iv11-b-probes/` and `eval/runs/iv11-b-golden/`.
- **3-way diagnostic** (§4 asked for BM25 vs SPLADE vs BM25+SPLADE): also
  record a SPLADE-only leg run into `eval/runs/iv11-splade-only-probes/`
  and `…-golden/`, to see whether SPLADE independently reaches the residual
  answer chunks or only helps via fusion.
- **Gate:** net answer-level recall improvement across probes+golden with
  **zero regressions vs A** (item-by-item diff by id, exactly like iv10's
  Task 4). Chunk count and the dense/BM25 index are unchanged by
  construction.

## Testing (TDD, offline — no MPS at test time)

New `tests/test_splade.py`:

- `SpladeIndex.search` returns correctly-shaped `(idx, score)` tuples in
  top-k order, driven by an **injected fake encoder** (hand-built CSR with
  known term weights) — same DI pattern as iv10.
- `rrf_fuse` with 3 legs produces the expected fused order on a small
  fixture (pins the additive-leg contract).
- Load-guard: `n` mismatch between `splade_meta.json` and the dense index
  raises rather than mis-fusing.
- Flag-off: `retrieve()` with SPLADE inactive is byte-identical to today
  (pins the no-op default).

## Error handling

- Missing `splade.npz` with the leg requested → clear error at load, **not**
  a silent 2-leg fallback (we never want to think we're measuring B but
  actually measure A). Mirrors the `n`-mismatch guard.
- Query-encode failure → the leg **raises** (eval context wants loud
  failure, not silent degradation — deliberately the opposite of the
  header generator's silent-empty contract).

## Out of scope

- Promoting SPLADE to the default API/Settings/pipeline path (deferred to a
  follow-on if B wins, exactly as HyDE and headers stayed eval-only in
  their cycles).
- Replacing BM25 with SPLADE (BM25's exact-match strength on statutory
  numerals like "68-74" is retained; SPLADE is additive, not a
  replacement).
- Any change to the dense index, reranker, or glossary.
- The Spaces/CPU demo path (won't ship the SPLADE artifact).
