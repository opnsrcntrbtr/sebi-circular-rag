# Benchmark Evaluation Handoff — 2026-07-09

## Purpose

This handoff captures the benchmark-evaluation upgrade implemented after the
Enhanced Benchmark Evaluation Plan. Use it as the first stop for future Codex,
GitHub Copilot, or Claude Code sessions that continue benchmark research,
dataset publication, external judging, or regression-harness work.

The implementation is a foundation slice, not the completed ~200-item benchmark:
`golden_v6` currently preserves the 56 curated `golden_v5` rows in an expanded
schema and marks them `review_status=seeded`. The next research step is label
expansion and adjudication, not another schema rewrite.

## Current State

- New benchmark helper module: `src/sebi_rag/benchmark.py`
  - Golden v6 enrichment and schema validation.
  - BEIR-style `corpus.jsonl`, `queries.jsonl`, and qrels export.
  - TREC runfile writer.
  - Retrieval-only benchmark helper.
  - Reproducibility metadata: git commit, env guards, corpus checksum, index
    fingerprint, golden checksum, model IDs, runtime params.
  - Research-only judge-result sidecar writer; gold labels are never modified by
    optional judges.
- New enriched benchmark seed: `eval/golden/golden_v6.jsonl`
  - 56 rows copied from `golden_v5`.
  - Added fields: `relevant_chunks`, `must_contain`, `must_not_contain`,
    `task_type`, `difficulty`, `expected_citation_level`, `rationale`,
    `label_source`, `review_status`.
  - Current distribution from export smoke:
    - `title_direct`: 30
    - `body_paraphrase`: 15
    - `hard_negative`: 10
    - `far_negative`: 1
    - `seeded`: 56
- New scripts:
  - `scripts/build_golden_v6.py`: regenerates `golden_v6` from frozen `golden_v5`
    and validates it.
  - `scripts/export_benchmark.py`: writes public benchmark artifacts under
    `dist/benchmark` by default.
  - `scripts/bench_retrieval.py`: retrieval-only benchmark with real-index mode
    and `--smoke` offline mode.
- New Make targets:
  - `make bench-retrieval`
  - `make benchmark-export`
- Tests:
  - `tests/test_benchmark.py` covers schema guardrails, BEIR/qrels export,
    TREC runfile shape, research-only judge sidecars, reproducibility metadata,
    and the retrieval smoke CLI.

## Important Commands

```bash
# Regenerate the enriched v6 seed from v5.
.venv/bin/python scripts/build_golden_v6.py

# Export benchmark artifacts to the repo default path.
make benchmark-export

# Export to a temporary path for validation without committing generated bundles.
.venv/bin/python scripts/export_benchmark.py --out /private/tmp/sebi-rag-benchmark-export

# Fast offline retrieval benchmark smoke.
.venv/bin/python scripts/bench_retrieval.py --smoke --out /private/tmp/sebi-rag-bench-smoke

# Real retrieval benchmark over persisted index and BGE-M3.
make bench-retrieval

# Focused benchmark tests.
.venv/bin/python -m pytest -q tests/test_benchmark.py

# Full offline suite.
.venv/bin/python -m pytest -q -m "not integration"
```

Verified on 2026-07-09:

- `tests/test_benchmark.py`: 5 passed.
- Full offline suite: 100 passed, 2 integration tests deselected, 1 existing
  Starlette/httpx warning.
- `scripts/bench_retrieval.py --smoke`: produced `run.trec` and `results.json`.
- `scripts/export_benchmark.py --out /private/tmp/sebi-rag-benchmark-export`:
  exported 36,603 corpus rows, 56 queries, 15,185 qrels, and dataset-quality
  summary for 603 circulars.

## Artifact Layout

`scripts/export_benchmark.py` writes:

```text
dist/benchmark/
├── README.md
├── retrieval-benchmark/
│   ├── corpus.jsonl
│   ├── queries.jsonl
│   └── qrels/test.tsv
├── rag-benchmark/
│   └── golden_v6.jsonl
└── dataset-quality/
    └── summary.json
```

Retrieval export semantics:

- `corpus.jsonl` is chunk-level. `_id` is the stable chunk ID.
- `queries.jsonl` has `_id` and `text`.
- `qrels/test.tsv` uses `query-id`, `corpus-id`, `score`.
- Current `golden_v6` has mostly circular-level labels, so qrels expand each
  relevant circular to all its chunks with score `1`. Future curated
  `relevant_chunks` labels should be score `2` and will override circular
  expansion for that query.

Run artifact semantics:

- `scripts/bench_retrieval.py` writes `run.trec` and `results.json`.
- `results.json` intentionally excludes the full rankings; rankings live in the
  TREC runfile.
- Metadata is designed to make every benchmark result auditable against the exact
  corpus/index/golden snapshot.

## Design Decisions To Preserve

- Keep benchmark concerns separate from production RAG behavior.
- Keep production gates local-first and deterministic by default.
- External LLM judges are allowed only as research sidecars. Their outputs must
  not overwrite `golden_v6` labels.
- Preserve original circular IDs in gold files. Use
  `normalize_circular_number()` only for matching/comparison.
- Treat `golden_v6` as a seed schema until enough labels are reviewed. Do not
  market current exports as a broad leaderboard.
- Prefer chunk-level `relevant_chunks` for new hard cases, especially numeric,
  table-like, lineage, and exact-reference questions.

## Recommended Next Tasks

1. Expand `golden_v6` toward ~200 reviewed items.
   - Preserve the current 56 seeded rows.
   - Add balanced slices:
     - title/direct queries
     - body-grounded paraphrases
     - numeric or table-like questions
     - lineage/supersession questions
     - exact circular-number lookups
     - near-domain hard negatives
   - Mark new rows `draft` first, then `reviewed` or `adjudicated`.
2. Add a curation helper script.
   - Suggest candidate queries from corpus subjects, body spans, lineage edges,
     and known hard-negative topics.
   - Emit draft JSONL rows without treating them as reviewed.
3. Add richer retrieval metrics.
   - Use qrels to compute nDCG@10, MAP, Recall@k, Precision@k, and MRR from
     TREC runfiles.
   - Keep the existing canary JSON stable or explicitly version new fields.
4. Add optional judge sidecar adapters.
   - Store outputs under an ignored or explicit `eval/judges/<run>/` path.
   - Include prompt version, model ID, provider/runtime, temperature, and raw
     verdict fields.
   - Keep judge outputs separate from gold labels.
5. Convert export bundles to Parquet for publication.
   - Current exports are JSONL/TSV and dataset-card YAML friendly.
   - Hugging Face publication should add typed features/Parquet when ready.
6. Decide whether `dist/benchmark/` and `eval/runs/` should be committed or
   ignored.
   - The scripts currently produce these paths, but temporary validation used
     `/private/tmp` to avoid adding large generated bundles by accident.

## Watchouts

- `uv.lock` appeared as untracked in the working tree during this work, but was
  not created or edited by the benchmark implementation. Do not delete it unless
  the owner confirms it is disposable.
- `normalize_circular_number()` returns a comparison key by stripping `SEBI/` and
  casefolding. It is not a storage format for labels.
- The qrels row count is large because circular-level relevance expands to every
  chunk in a relevant circular. This is acceptable as a bridge, but curated
  chunk-level qrels are the desired endpoint.
- Running `make bench-retrieval` uses the real BGE-M3/index path and can be much
  slower than `--smoke`.
- Generated public benchmark bundles may be large. Validate in `/private/tmp`
  before deciding what to commit.

## Files Changed In This Slice

- `Makefile`
- `docs/superpowers/specs/2026-07-09-sebi-public-datasets-design.md`
- `eval/golden/golden_v6.jsonl`
- `scripts/bench_retrieval.py`
- `scripts/build_golden_v6.py`
- `scripts/export_benchmark.py`
- `src/sebi_rag/benchmark.py`
- `tests/test_benchmark.py`

