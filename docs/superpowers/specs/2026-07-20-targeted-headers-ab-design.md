# Targeted Contextual Headers with A/B Measurement (iv10) — Design

**Date:** 2026-07-20
**Status:** approved (scope, header reuse, sup-04 override, and A/B mechanism chosen by user)
**Predecessor:** `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md`
§5.4 (iv9: scoped-but-bulk contextual headers rejected — probes failures
4→5, golden recall@10 below floor, two unrelated items newly failed),
spec `2026-07-19-contextual-headers-design.md`, plan
`2026-07-19-contextual-headers.md`.

## Problem

iv9 generated headers for 18,125 chunks (23% of the corpus) in one bulk
pass and measured a net-negative result: probe-par-03's document rank
improved sharply (7 → 2) but its answer chunk stayed a candidate miss, and
two previously-passing items (`probe-par-02`, `para-mfborrow`) — unrelated
to any target failure — newly failed, with recall@10 dropping below the
0.956 floor on golden. The report's working hypothesis: uniform-register
header text added to a large fraction of the corpus at once shifts
dense-embedding distances broadly, hurting unrelated queries as a side
effect of scale, not of the header content itself.

This design isolates **scale** as the only changed variable: same header
content (reused verbatim from iv9, deterministic greedy decoding), same
model, same mechanism — applied to a document set two orders of magnitude
smaller.

## Scope (user decision)

Three documents, chosen because they are the failure-adjacent documents
for every remaining probes-gate target:

| doc_id | probe(s) |
|---|---|
| `SEBI/HO/DDHS/DDHS-POD2/P/CIR/2025/101` | probe-par-03 |
| `SEBI/HO/CFD/PoD2/CIR/P/0155` | probe-sup-04 |
| `SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/91` | probe-tbl-05, probe-num-05 |

All depth≥3-or-annex chunks (iv9's `in_scope` predicate,
`src/sebi_rag/context_headers.py`) within these three documents, **plus an
explicit override** for probe-sup-04's actual answer chunk
(`SEBI/HO/CFD/PoD2/CIR/P/0155#4. …`, section id `"4."`, depth 1) — iv9's
scope rule structurally excluded it, and this cycle targets that failure
by name, so it must be reachable. Total: tens to low hundreds of chunks
(exact count reported after the filter step, expected well under 500).

## Header reuse (user decision)

The iv9 sidecar (18,125 rows, committed at `d6f323f`, `git show
d6f323f:data/corpus/context_headers.jsonl`) already contains 7B-generated
headers for every depth≥3/annex chunk in these three documents — iv9's
scope was a superset of this one. Greedy decoding is deterministic, so
regenerating would reproduce identical text. **Reuse those rows as-is**;
generate exactly one new header (the sup-04 override) via the existing
`HeaderGenerator.load()` (`src/sebi_rag/context_headers.py`, unchanged
from iv9 — same model, same prompt, same silent-failure contract).

Output: a new sidecar `data/corpus/context_headers_targeted.jsonl`, kept
separate from the (git-preserved, working-tree-removed) iv9 file so the
two experiments are never conflated.

## Components

### 1. `scripts/select_targeted_headers.py` (new script)

- Reads the iv9 sidecar from git history (`git show
  d6f323f:data/corpus/context_headers.jsonl`, piped to a temp file — the
  working tree no longer has it after the iv9 revert) and filters rows
  whose `chunk_id` starts with one of the three target `doc_id` values
  (`chunk_id.split("#")[0] in TARGET_DOCS`).
- Loads the corpus, finds probe-sup-04's specific chunk (the one whose
  `id.split("#")[0] == "SEBI/HO/CFD/PoD2/CIR/P/0155"` and section starts
  `"4."`), and generates its header via `HeaderGenerator.load()`.
- Writes the combined rows to `data/corpus/context_headers_targeted.jsonl`.
- Prints the final row count and the doc_id breakdown for verification
  before any index build runs.

### 2. `scripts/build_index.py` (modify)

Add one optional CLI argument:

```python
ap.add_argument("--context-headers",
                 default=str(ROOT / "data" / "corpus" / "context_headers.jsonl"))
```

(build_index.py currently uses `argparse` implicitly via `sys.argv` checks
for `--full`; this adds a proper `argparse.ArgumentParser` for this one
flag, defaulting to the same hardcoded path iv9 used — so default
behavior with no sidecar present is unchanged: `load_headers` returns
`{}`, `apply_context_headers` is a no-op.) The chunk-loading line changes
from a hardcoded path to `args.context_headers`.

No other change: `apply_context_headers`/`load_headers`
(`src/sebi_rag/context_headers.py`, from the iv9 plan) are reused
verbatim.

## A/B mechanism (user decision)

Two full index builds, both freshly benchmarked — not an assumption that
the post-iv9 revert reproduces iv7 bit-for-bit:

- **A (baseline):** the current index, already reverted to no-headers
  state (this revert is in progress as of this spec, tracked outside this
  cycle). Benchmark it fresh into `eval/runs/iv10-a-probes/` and
  `eval/runs/iv10-a-golden/`.
- **B (targeted headers):** `make reindex`-equivalent invocation of
  `scripts/build_index.py --context-headers
  data/corpus/context_headers_targeted.jsonl` (incremental — only the
  three target documents' checksums change, so only their chunks
  re-embed; expect minutes, not hours). Benchmark into
  `eval/runs/iv10-b-probes/` and `eval/runs/iv10-b-golden/`.
- Before building B, snapshot A's `data/index/` directory (a plain
  recursive copy to a scratch path). After B's benchmarks, **restore A by
  copying the snapshot back** — not by rebuilding, which would cost
  another embedding pass and risks reproducing a subtly different state.
  The working system is left in the known-good, no-headers state
  regardless of B's outcome — this cycle must not leave a regressed index
  live, the same operational mistake risk flagged in iv9's wrap-up.

## Testing (TDD, offline)

New `tests/test_select_targeted_headers.py`:

- Filtering: given a small fake sidecar with mixed doc_ids, only rows for
  the three target docs are kept.
- The sup-04 override row is added when missing from the filtered set,
  using an injected fake generator (no MLX at test time).
- Row count and doc_id breakdown are printed (captured via capsys).

`build_index.py`'s new flag needs no new unit test beyond what iv9's
`apply_context_headers`/`load_headers` tests already cover (signature and
no-op-when-absent are already pinned); the flag is argparse plumbing only.

## Measurement & gates

- **Primary question:** does B resolve probe-par-03 and/or probe-sup-04
  relative to A, **without B regressing any item that passes in A** (the
  run's own control, not iv7 — the tightest possible comparison).
- Chunk count unchanged (77,859) in both A and B.
- `make test` green (unchanged suite — no new fixtures needed) throughout.
- Report results (verbatim numbers for A and B, item-by-item diff, met or
  not) as report §5.5. If B regresses anything A didn't, that is a
  stronger, more localized negative signal than iv9's corpus-wide one and
  must be reported as such — no silent iteration, no leaving the
  regressed index live (per the A/B mechanism's restore step above).

## Out of scope

- Any chunk outside the three target documents.
- Regenerating headers already present in the iv9 sidecar for these docs
  (reused verbatim per the decision above).
- SPLADE (the sibling report-§4 option, untouched this cycle).
- API/Settings wiring: retrieval code is untouched, as in iv9.
