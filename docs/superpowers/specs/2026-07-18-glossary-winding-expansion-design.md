# Glossary Winding-Down Expansion (Part A) + HyDE Boundary (Part B) — Design

**Date:** 2026-07-18
**Status:** approved (approach "A then B" chosen by user)
**Predecessor:** `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md`
§5.1 (iv6 verdict: probes gate 4 > 3, probe-par-03 residual is semantic, not
truncation), spec `docs/superpowers/specs/2026-07-17-wrapped-clause-folding-design.md`.

## Problem

probe-par-03 ("When a rating agency is winding down its business, can
companies pull their ongoing rating assignments?") stays an answer-level
candidate miss after wrapped-clause folding (iv6). Verified failure chain:

- Doc-level retrieval is fine (CRA master circular at rank 5).
- The folded answer chunk `…CIR/2025/101#4.1.1.2` now contains the full
  governing clause ("…request for surrender of certificate of registration
  ('the Request') to SEBI, as applicable, the concerned CRA shall – …not
  take any new clients or fresh mandates") but never enters the top-50 pool.
- The gap is lexical/semantic: query says *winding down / pull / ongoing
  rating assignments*; the chunk says *surrender / cancellation / withdraw /
  new clients / fresh mandates*. Zero content-word overlap for BM25; bge-m3
  does not bridge it against 77k competitors. BM25 is instead drawn to the
  KRA circular, which uses "winding down" literally.

Corpus grounding (full-corpus counts, `data/corpus/circulars.jsonl`):
"winding" 304, "wind down" 35, "wound" 108, "surrender" 603, "mandate"
1536, "withdraw any assignment" 7. SEBI itself uses "winding down" for some
intermediaries (KRAs, AIFs) and "surrender/cancellation of certificate of
registration" for CRAs — the mapping below bridges SEBI's own inconsistent
vocabulary, it is not reverse-engineered from the probe.

## Part A (this cycle): glossary extension

Extend `GLOSSARY` in `src/sebi_rag/expand.py` (intervention #2 mechanism —
deterministic, additive, sparse-leg only; dense leg keeps the raw query;
no reindex, no latency cost) with three entries in the existing
single-lowercase-token-key format:

```python
# probe-par-03: "winding down / pull assignments" vs corpus
# "surrender/cancellation of certificate of registration; withdraw assignment"
"winding": ("surrender", "wound-up", "cancellation"),
"wind": ("surrender", "wound-up"),
"pull": ("withdraw",),
```

Rescue path: iv6 folding put "surrender … certificate … registration" into
chunk 4.1.1.2; this expansion puts "surrender / withdraw" into the BM25
query — the two interventions meet in the middle.

Eval-hygiene rule: entries must be justified by corpus-wide vocabulary (as
above), never by a single probe's wording; golden must not regress.

## Testing (TDD, offline)

New tests in `tests/test_expand.py`, existing style:

- "winding down" query expands to include "surrender" (red first).
- "pull" query expands to include "withdraw".
- An unrelated query (no glossary tokens) is returned unchanged.
- All existing expansion tests stay green.

## Measurement & gates (Part A)

No reindex. Re-run both benchmarks against the current index into fresh run
dirs `eval/runs/iv7-probes/` and `eval/runs/iv7-golden/` (never overwrite
`ft-*`, `iv-final-*`, `iv6-*`), then `scripts/analysis/extract_misses.py`
on both.

- Probes answer-level failures ≤ 3 (from 4) — probe-par-03 is the target.
- Golden answer-level failures ≤ 3 and doc recall@10 ≥ 0.956.
- No previously-passing probe or golden item newly fails.
- `make test` green (262 + new expand tests) after every step.

Report results (verbatim numbers, met or not) as report §5.2.

## Part B boundary (HyDE — designed later, not in this cycle)

Recorded here only as trigger + shape; explicitly out of scope for Part A's
implementation plan:

- **Trigger:** iv7 leaves the probes gate unmet, or the user chooses to
  attack the remaining semantic residues that no glossary entry can reach
  (para-aifmaster pure-paraphrase gap, probe-sup-04 lineage/table gap).
- **Shape:** local-LLM hypothetical-answer generation whose embedding is
  substituted into the dense leg only; sparse leg and reranker unchanged;
  feature-flagged off by default; reuses the existing local generator stack.
- **Process:** full HyDE design gets its own brainstorm → spec → plan cycle.
