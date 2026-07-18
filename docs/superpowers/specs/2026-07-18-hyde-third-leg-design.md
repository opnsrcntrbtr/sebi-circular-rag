# HyDE Third-Leg Retrieval (Part B) — Design

**Date:** 2026-07-18
**Status:** approved (third-RRF-leg wiring and eval-only flag chosen by user)
**Predecessor:** `docs/superpowers/specs/2026-07-18-glossary-winding-expansion-design.md`
Part B boundary; trigger fired per report
`docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` §5.2
(iv7: probes gate 4 > 3 after both deterministic interventions).

## Problem

probe-par-03 remains an answer-level candidate miss after wrapped-clause
folding (iv6) and glossary expansion (iv7). Both deterministic levers are
exhausted: the folded chunk `…CIR/2025/101#4.1.1.2` contains the statutory
vocabulary, but the query ("winding down", "pull ongoing rating
assignments") and the chunk body ("surrender of certificate", "not take any
new clients or fresh mandates") share too little for BM25 to discriminate
(603 corpus-wide "surrender" hits dilute the expanded query), and bge-m3's
raw-query embedding does not bridge the paraphrase against 77k competitors.
A hypothetical statutory-style answer, embedded in place of nothing (as an
additional dense signal), is the designed next step (report §4
intervention #5).

## Design decisions (user-selected)

- **Wiring: third RRF leg.** `rrf_fuse([dense(query), sparse(expanded),
  dense(hyde_text)])`. Purely additive — raw dense and sparse legs
  untouched; HyDE's contribution is isolated and attributable.
- **Flag scope: eval-only opt-in.** `HybridRetriever.retrieve()` gains an
  optional parameter defaulting to off; `scripts/bench_retrieval.py` gains
  `--hyde`. The live API path is untouched this cycle; API wiring is a
  follow-on only if the gates pass.

## Components

### 1. `src/sebi_rag/hyde.py` (new module)

One responsibility: turn a query into a hypothetical statutory passage.

```python
class HydeExpander:
    def __init__(self, generate: Callable[[str], str], max_chars: int = 1200): ...
    def hypothesize(self, query: str) -> str: ...

    @classmethod
    def load(cls, model: str = "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
             max_tokens: int = 150) -> "HydeExpander": ...
```

- `hypothesize` wraps the query in a fixed prompt — "Write a short passage
  in the style of a SEBI circular provision that would answer this
  question. Use formal regulatory vocabulary. Question: {query}" — calls
  `generate`, strips whitespace, and truncates to `max_chars`. Failure is
  silent by design: any exception from `generate` or an empty/whitespace
  result returns `""`, which callers treat as no-HyDE.
- `load()` is the only place MLX enters: it builds the callable from
  `mlx_lm` load/generate (greedy decode → deterministic), same runtime as
  `MLXGenerator` in `src/sebi_rag/generate.py:265`. Tests never call it.

### 2. `HybridRetriever.retrieve` (modify `src/sebi_rag/retrieve.py:165-173`)

```python
def retrieve(self, query, k_dense=50, k_sparse=50, top_n=50,
             hyde_text: str | None = None) -> list[tuple[Chunk, float]]
```

- When `hyde_text` is a non-empty string: dense-search it with `k_dense`
  and fuse three legs; otherwise behavior is byte-identical to today
  (pinned by regression test). Empty string is treated as `None`.
- The retriever never generates; the caller passes the text. No LLM
  dependency enters `retrieve.py`.

### 3. `scripts/bench_retrieval.py` (add `--hyde` flag)

- With `--hyde`: build `HydeExpander.load()` once; per query call
  `hypothesize` and pass the result as `hyde_text`; write every
  `{"id", "query", "hyde"}` row to `<out>/hyde.jsonl` for audit.
- Without `--hyde`: unchanged behavior and output.
- Run metadata (`results.json`) records `"hyde": true/false` in params.

## Testing (TDD, offline — fake generator, no MLX at test time)

New `tests/test_hyde.py`:

- `hypothesize` passes a prompt containing the query and the phrase
  "SEBI circular" to the injected callable; returns its stripped output.
- Exception or empty output from the callable → `""`.
- Output longer than `max_chars` is truncated.

Extended `tests/test_expand.py`-style wiring tests (in `tests/test_hyde.py`
using `HashEmbedder` + tiny corpus, mirroring the existing pattern in
`tests/test_expand.py:48-105`):

- `retrieve(hyde_text=…)` rescues a paraphrase-gap chunk: a chunk whose
  vocabulary matches the hypothetical text but not the query enters the
  fused top-k.
- `retrieve()` and `retrieve(hyde_text="")` return identical results to
  each other and to the pre-change behavior (regression pin).

## Measurement & gates

Benchmarks with `--hyde` into fresh run dirs `eval/runs/iv8-probes/` and
`eval/runs/iv8-golden/` (never overwrite `ft-*`, `iv-final-*`, `iv2-*`,
`iv6-*`, `iv7-*`), then `scripts/analysis/extract_misses.py` on both.

- Probes answer-level failures ≤ 3 (from 4) — probe-par-03 is the target.
- Golden answer-level failures ≤ 3 and doc recall@10 ≥ 0.956.
- No new failure IDs vs iv7 on either eval set (RRF re-ranks everything, so
  the additive leg must be verified harmless, not assumed).
- `make test` green (265 + new hyde tests) after every step.

Report results (verbatim numbers, met or not) as report §5.3. If the probes
gate is still unmet, that is decision-point evidence for the remaining
report-§4 options (SPLADE, contextual headers) — no silent iteration.

## Out of scope

- API/Settings wiring of HyDE (follow-on only if gates pass).
- Model upgrades beyond the cached Qwen2.5-1.5B-Instruct-4bit.
- Caching hypothetical passages across runs (greedy decode is already
  deterministic; `hyde.jsonl` per run dir suffices for audit).
