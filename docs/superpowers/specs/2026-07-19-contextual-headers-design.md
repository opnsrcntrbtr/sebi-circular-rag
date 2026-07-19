# Scoped Contextual Chunk Headers — Design

**Date:** 2026-07-19
**Status:** approved (approach, scope, and pilot gate chosen by user)
**Predecessor:** `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md`
§5.3 (iv8: HyDE third leg rejected — probes gate 4 > 3, golden regression),
specs `2026-07-17-wrapped-clause-folding-design.md`,
`2026-07-18-glossary-winding-expansion-design.md`,
`2026-07-18-hyde-third-leg-design.md`.

## Problem

After three interventions (fold iv6, glossary iv7, HyDE iv8 — rejected) the
probes gate stays at 4 answer-level failures (target ≤ 3). Verified evidence
that shaped this design:

- probe-par-03's answer chunk (`…CIR/2025/101#4.1.1.2`) sits under an
  ancestor chain with **no numbered §4 heading** — the governing section is
  the unnumbered line "Guideline for CRAs on Suspension, Cancellation or
  Surrender of Certificate of Registration:", and "winding down" occurs
  **nowhere** in that document region. No deterministic fold or query-side
  synonym can inject vocabulary the document never contains.
- iv8's one success (para-aifmaster answer 28 → 12 when the generated text
  carried the right domain nouns) shows the dense leg responds when
  bridging vocabulary is present in the compared text.
- iv8's failure mode (markdown/circular boilerplate; lay-term parroting) is
  a query-time problem: the model had to *guess* statutory vocabulary. At
  index time the model *reads* the statutory text and paraphrases toward
  lay vocabulary — the tractable direction.

Chosen intervention (report §4 candidate): **contextual chunk headers**,
scoped, with a pilot go/no-go before any long generation run. SPLADE and a
HyDE redesign were considered and declined (SPLADE's MS-MARCO-learned
expansions are unlikely to bridge "winding down" ↔ "surrender"; HyDE's
missing-vocabulary problem is structural at query time).

## Scope (user decision)

Headers for **deep sub-clause chunks (section depth ≥ 3, e.g. `x.y.z…`) plus
annex/appendix/schedule-headed chunks**: 17,601 + 595 ≈ **18.2k of 77,859**
chunks (~5–8 h one-time MLX generation). Shallow chunks keep their existing
discriminative headings. Full-corpus headers (~30+ h) explicitly declined.

## Components

### 1. `src/sebi_rag/context_headers.py` (new module)

Mirrors the `HydeExpander` pattern (`src/sebi_rag/hyde.py`):

```python
class HeaderGenerator:
    def __init__(self, generate: Callable[[str], str], max_chars: int = 200): ...
    def describe(self, subject: str, governing: str, chunk_text: str) -> str: ...

    @classmethod
    def load(cls, model: str = "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
             max_tokens: int = 80) -> "HeaderGenerator": ...
```

- `describe` prompts for **one plain-prose sentence stating what the
  provision governs, naming it in both everyday and statutory terms**. The
  prompt embeds anti-boilerplate constraints learned from iv8: *no
  markdown, no headings, no dates, no circular numbers, one sentence only*.
- Output post-processing: strip whitespace and any leading markdown
  characters (`#*>-`), collapse internal newlines to spaces, truncate to
  `max_chars`. Silent-failure contract identical to `HydeExpander`: any
  exception or empty/whitespace output → `""`.
- `load()` is the only MLX entry point (greedy decode → deterministic);
  escalation model for the pilot: `mlx-community/Qwen2.5-7B-Instruct-4bit`
  via the `model` parameter.

### 2. `scripts/generate_context_headers.py` (new script)

- Reads the corpus, chunks it with the existing `hierarchical_chunk`, and
  selects in-scope chunks: section number depth ≥ 3
  (`re.match(r"^\d+(?:\.\d+){2,}", section)`) or section matching
  `annex|appendix|schedule` (case-insensitive).
- Writes `data/corpus/context_headers.jsonl` rows:
  `{"chunk_id", "header", "model"}`.
- **Resumable:** skips chunk ids already present in the output file.
- `--limit N` and `--ids <file>` for the pilot; `--model` to escalate.
- The `governing` argument to `describe` is derived from the chunk itself:
  the first body line (below the breadcrumb) when it matches the numbered
  heading pattern `^\d+(\.\d+)*[.)]\s` — i.e. the clause folded in by iv6 —
  else `""`. No separate heading bookkeeping.
- The prompt sees only corpus text (subject, governing clause, chunk body)
  — never probe or golden wording. Eval-hygiene rule as in iv7.

### 3. Index merge (modify `scripts/build_index.py` chunk assembly)

- After chunking, a pure function
  `apply_context_headers(chunks: list[Chunk], headers: dict[str, str]) -> list[Chunk]`
  (in `src/sebi_rag/context_headers.py`) returns chunks whose text has the
  header inserted as a line below the existing breadcrumb line. Missing
  sidecar file or missing chunk id → chunk unchanged.
- Chunk **count and IDs unchanged** (gate: 77,859). Text changes flow
  through the existing per-doc checksum, so only enriched docs re-embed.

## Pilot go/no-go (before the full run)

Generate headers for the known failure chunks only (via `--ids`): the CRA
`…CIR/2025/101#4.1.1.x` chunks, probe-sup-04's LODR appendix chunk, and the
tbl-05/num-05 answer chunks. Inspect (human/agent judgment, recorded in the
report):

- par-03 chunks: header contains winding-down/ceasing-operations phrasing
  alongside surrender/cancellation vocabulary.
- sup-04 chunk: header describes a list of circulars withdrawn/rescinded.
- No markdown/boilerplate artifacts.

If the 1.5B output fails this, escalate once to Qwen2.5-7B-Instruct-4bit
and re-check. If it still fails: **stop and report no-go** — do not run the
18.2k generation. The pilot inspects failure chunks but feeds them nothing
from the eval sets.

## Testing (TDD, offline — fake callables, no MLX at test time)

New `tests/test_context_headers.py`:

- `describe` prompt contains subject, governing clause, chunk text, and the
  anti-boilerplate instruction; output stripped and truncated.
- Markdown-prefixed / multi-line generator output is cleaned to one plain
  line.
- Exception or empty output → `""`.
- `apply_context_headers`: header inserted below the breadcrumb line; chunk
  id/count unchanged; chunk without a sidecar entry is returned unchanged;
  empty header string → unchanged.
- Scope filter: depth-3 section selected, depth-2 not, annex heading
  selected (unit-test the selection predicate).

## Measurement & gates

Full scoped generation (~18.2k), commit the sidecar, `make reindex`
(~30 min MPS + re-embed of enriched docs), then benchmarks into fresh
run dirs `eval/runs/iv9-probes/` and `eval/runs/iv9-golden/` (never
overwrite earlier runs), plus `scripts/analysis/extract_misses.py` on both.

- Probes answer-level failures ≤ 3 (from 4) — probe-par-03 and
  probe-sup-04 are the targets.
- Golden answer-level failures ≤ 3 and doc recall@10 ≥ 0.956.
- No new failure IDs vs iv7 (the standing baseline; HyDE stays off).
- Chunk count 77,859 unchanged.
- `make test` green (271 + new tests) after every step.

Report results (verbatim numbers, met or not, including the pilot verdict
and which model it selected) as report §5.4. If the gate is unmet, that is
a decision point per the standing rule — no silent iteration.

## Out of scope

- Headers for shallow (depth < 3, non-annex) chunks.
- SPLADE and HyDE redesign (declined this cycle; evidence recorded above).
- Any API/serving change: retrieval code is untouched — enrichment is
  entirely index-side.
