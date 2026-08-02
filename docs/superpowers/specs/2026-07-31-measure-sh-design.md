# Design Spec: `.auto/measure.sh` — Automated Metric Collection

**Date:** 2026-07-31
**Status:** Approved by user (2026-07-31)
**Approach:** Modular library + thin CLI (Approach A)

---

## 1. Goal

Provide automated, reproducible collection of 6 new metrics beyond the existing golden-set evaluation (recall@10, MRR, nDCG, citation prec/rec, abstention accuracy). Output both machine-parseable JSONL and human-readable markdown.

## 2. Architecture

### File Layout
```
src/sebi_rag/measure.py              ← Core metric functions (6 metrics as pure functions)
src/sebi_rag/measure_models.py       ← Dataclasses: MeasureResult, MeasureReport
scripts/bench_metrics.py             ← CLI entry point (argparse, orchestrates pipeline + metrics)
.auto/measure.sh                     ← Thin bash wrapper: calls bench_metrics.py → JSONL + MD
Makefile                             ← Add `measure` target
```

### Data Flow
```
.measure.sh
    │
    ├─► python scripts/bench_metrics.py --golden eval/golden/golden_v7.jsonl
    │       │
    │       ├─► loads pipeline (retriever + reranker only, NO generator)
    │       ├─► runs each metric function from measure.py
    │       ├─► collects MeasureResult objects into MeasureReport
    │       ├─► writes JSONL to .auto/runs/measure_YYYYMMDD.jsonl
    │       └─► writes markdown summary to .auto/reports/measure_YYYYMMDD.md
    │
    └─► prints summary table to stdout
```

### Key Design Decisions
- **No generator needed**: All 6 metrics operate at retrieval/parsing level; no LLM generation required
- **Pipeline reuse**: `bench_metrics.py` builds a lightweight pipeline (retriever + reranker only) — same pattern as `bench_retrieval.py`
- **MPS measurement**: Uses `torch.mps.current_allocated_memory()` and `torch.mps.max_memory_allocated()` — no external tools needed
- **Idempotent**: Each run appends to JSONL; markdown is overwritten (latest snapshot)
- **On-demand only**: No CI integration, no pre-commit hook. Developer runs `make measure` manually

## 3. Metric Specifications

### 3.1 Parsing Latency (`measure_parsing_latency`)

**Purpose:** Measure PDF ingestion throughput (chars/sec, chunks/min).

**Input:** Corpus JSONL path from pipeline config.

**Algorithm:**
1. Sample 20 PDFs stratified by size: 7 small (<50KB), 7 medium (50-200KB), 6 large (>200KB)
2. For each PDF, time the chunking step (from raw text extraction to Chunk list)
3. Compute mean chars/sec, median ms per PDF, p99 ms per PDF

**Output Schema:**
```json
{
  "metric": "parsing_latency",
  "mean_chars_per_sec": 12345,
  "median_ms_per_pdf": 450,
  "p99_ms_per_pdf": 1200,
  "sample_size": 20,
  "strata": {
    "small": {"n": 7, "mean_ms": 120},
    "medium": {"n": 7, "mean_ms": 450},
    "large": {"n": 6, "mean_ms": 1200}
  }
}
```

**Implementation Notes:**
- Reuse `ingest_pdf.py` chunking logic; do not re-implement PDF parsing
- Sample selection: use existing `data/raw/` directory, sort by file size, pick stratified sample
- If OCR is needed for any PDF in the sample, time that separately and report `ocr_ms` field

### 3.2 Supersession Detection Precision (`measure_supersession_precision`)

**Purpose:** Measure what fraction of detected supersession edges are genuine (not false positives from regex matching).

**Input:** `lineage.Lineage` object + corpus records.

**Algorithm:**
1. Sample 50 edges from `lineage.supersedes` (uniform random)
2. For each sampled edge `(newer, older)`:
   - Verify `older` text actually contains a supersession reference to `newer` (or vice versa)
   - Cross-check: does the newer circular's subject/date logically follow the older one?
   - Mark as `true` or `false` based on manual verification criteria
3. Precision = true_edges / total_sampled
4. Compute 95% Wilson confidence interval

**Output Schema:**
```json
{
  "metric": "supersession_precision",
  "precision": 0.94,
  "ci_95_lower": 0.83,
  "ci_95_upper": 0.99,
  "sample_size": 50,
  "true_positives": 47,
  "false_positives": 3,
  "ambiguous": 0
}
```

**Implementation Notes:**
- The verification step is heuristic-based (not fully automated): check if the older circular's text mentions the newer one by number, or if dates are consistent
- If verification is inconclusive for any edge, exclude it from the count and note in `ambiguous` field
- Reference: current precision is ~96.8% (90 false positives removed from 2850 edges per status.md)

### 3.3 Temporal Query Accuracy (`measure_temporal_accuracy`)

**Purpose:** Measure what fraction of `as_of` queries return the correct pre-supersession circular in top-3.

**Input:** golden_v7 rows with `as_of` field (15 rows) + lineage object.

**Algorithm:**
1. Filter golden_v7 for rows where `as_of` is present (expect ~15)
2. For each as_of query:
   - Run `pipeline.query(question, as_of=row["as_of"], top_k=3)`
   - Check if any chunk in the top-3 belongs to the correct pre-supersession circular (from `row["relevant_circulars"]`)
   - Mark as correct if at least one hit in top-3
3. Accuracy = correct / total_as_of_queries

**Output Schema:**
```json
{
  "metric": "temporal_accuracy",
  "accuracy": 0.93,
  "correct": 14,
  "total": 15,
  "failures": [
    {"id": "v7-ls-038", "as_of": "2020-01-01", "expected_circulars": ["SEBI/HO/MRD/..."], "top3_docs": ["SEBI/HO/MRD/other"]}
  ]
}
```

**Implementation Notes:**
- This metric specifically tests the `as_of` parameter in `pipeline.query()` (line 50-72 of pipeline.py)
- If fewer than 10 as_of queries exist, report `insufficient_data: true` and skip
- The pipeline's as_of logic demotes circulars only if a superseding circular was issued by the as_of date

### 3.4 RRF Fusion Gain (`measure_rrf_fusion_gain`)

**Purpose:** Quantify the benefit of RRF fusion over single-leg retrieval (dense-only, BM25-only).

**Input:** golden_v7 rows (all 260) + pipeline with retriever.

**Algorithm:**
1. For each golden query, run retrieval three ways:
   - **Dense-only:** `retriever.dense.search(query, top_n=50)`
   - **BM25-only:** `retriever.sparse.search(query, top_n=50)`
   - **RRF-fused:** `retriever.retrieve(query, top_n=50)` (uses RRF)
2. For each leg, compute recall@10 and MRR against golden `relevant_circulars`
3. Gain = (rrf_value - max(dense, bm25)) / max(dense, bm25) × 100

**Output Schema:**
```json
{
  "metric": "rrf_fusion_gain",
  "dense_recall10": 0.85,
  "bm25_recall10": 0.78,
  "rrf_recall10": 0.92,
  "dense_mrr": 0.72,
  "bm25_mrr": 0.65,
  "rrf_mrr": 0.80,
  "gain_recall10_pct": 8.2,
  "gain_mrr_pct": 11.1
}
```

**Implementation Notes:**
- Reuse `retrieve.py`'s internal methods; do not modify the retriever's public API
- The dense and sparse searches should use identical `top_n=50` pool size for fair comparison
- If dense or BM25 alone outperforms RRF on any query, that's a data point to note (RRF should never hurt)

### 3.5 Context Precision (`measure_context_precision`)

**Purpose:** Measure what fraction of retrieved chunks contain genuinely relevant content (not just keyword matches).

**Input:** golden_v7 rows (all 260) + pipeline with retriever.
**Algorithm:**
1. For each golden query, retrieve top-10 chunks via `pipeline.retriever.retrieve(query, top_n=10)`
2. For each retrieved chunk, determine relevance:
   - Strip F1 enrichment prefix from chunk text (remove `circular_no | subject | section` prefix)
   - Tokenize both the stripped chunk text and the query (lowercase, alphanumeric tokens)
   - **Relevant:** chunk's doc_id in `row["relevant_circulars"]` AND ≥2 query tokens appear in stripped chunk text
   - **Irrelevant:** chunk's doc_id not in relevant_circulars, OR <2 query tokens in stripped text
3. Precision = relevant_chunks / total_chunks_evaluated

**Output Schema:**
```json
{
  "metric": "context_precision",
  "precision": 0.72,
  "total_chunks_evaluated": 2600,
  "relevant_chunks": 1872,
  "irrelevant_chunks": 728,
  "false_positive_rate": 0.28
}
```

**Implementation Notes:**
- The F1 enrichment (prepending circular_no + subject to every chunk) may cause false positives — chunks that match only because of the prefix, not the actual clause text
- This metric helps evaluate whether F1 enrichment is helping or hurting precision
- Token overlap threshold of 2 prevents single-word prefix matches from counting as relevant
- Relevance determination: chunk's doc_id in relevant_circulars AND chunk text (minus prefix) contains query-relevant content

### 3.6 MPS Memory Utilization (`measure_mps_memory`)

**Purpose:** Measure peak MPS memory usage during pipeline operation.

**Input:** Pipeline with loaded embedder + reranker (no golden set needed).

**Algorithm:**
1. Record `torch.mps.current_allocated_memory()` before any pipeline load
2. Load index (retriever.build or retriever.load)
3. Record memory after index load
4. Run one warm-up query (measure during query)
5. Run full golden_v7 evaluation (measure peak)
6. Record `torch.mps.max_memory_allocated()` at end

**Output Schema:**
```json
{
  "metric": "mps_memory",
  "before_load_gb": 0.1,
  "after_index_gb": 3.2,
  "during_query_gb": 4.5,
  "peak_gb": 4.8,
  "headroom_gb": 43.2,
  "total_ram_gb": 48.0
}
```

**Implementation Notes:**
- Use `torch.mps.current_allocated_memory()` for current usage, `torch.mps.max_memory_allocated()` for peak
- Convert bytes to GB: `memory_bytes / 1e9`
- If MPS is not available, record `"mps_available": false` and skip measurement
- Total RAM from `sysctl -n hw.memsize` or `psutil.virtual_memory().total`

## 4. Data Models (`src/sebi_rag/measure_models.py`)

```python
from dataclasses import dataclass, field, asdict
from typing import Any
from datetime import datetime

@dataclass(frozen=True)
class MeasureResult:
    """Single metric result."""
    metric: str                    # e.g., "parsing_latency"
    value: dict[str, Any]          # metric-specific data
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

@dataclass(frozen=True)
class MeasureReport:
    """Complete measurement run report."""
    ts: str                        # ISO timestamp
    git_commit: str                # current git commit hash
    corpus_circulars: int          # number of circulars in corpus
    corpus_chunks: int             # number of chunks in index
    golden_n: int                  # number of golden rows evaluated
    metrics: dict[str, dict]       # {metric_name: metric_value_dict}

    def to_json(self) -> str:
        import json
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_results(cls, results: list[MeasureResult], **kwargs) -> "MeasureReport":
        metrics = {r.metric: r.value for r in results}
        return cls(metrics=metrics, **kwargs)
```

## 5. CLI Interface (`scripts/bench_metrics.py`)

### Argument Parser
```python
import argparse

parser = argparse.ArgumentParser(description="Measure SEBI Circular RAG metrics")
parser.add_argument("--golden", default="eval/golden/golden_v7.jsonl",
                    help="Path to golden set JSONL")
parser.add_argument("--metrics", nargs="+", default=None,
                    help="Specific metrics to run (default: all)")
parser.add_argument("--dry-run", action="store_true",
                    help="Build pipeline, skip metrics")
parser.add_argument("--out-dir", default=".auto/runs",
                    help="Output directory for JSONL")
parser.add_argument("--report-dir", default=".auto/reports",
                    help="Output directory for markdown reports")
```

### Execution Flow
1. Parse args, set up paths
2. Build lightweight pipeline (retriever + reranker only)
3. Load golden set, validate
4. For each metric (all or specified):
   - Call `measure_<name>(pipeline, golden_rows)`
   - Collect `MeasureResult` objects
5. Build `MeasureReport` with metadata (git commit, corpus counts)
6. Write JSONL to `.auto/runs/measure_YYYYMMDD.jsonl` (append)
7. Write markdown to `.auto/reports/measure_YYYYMMDD.md` (overwrite)
8. Print summary table to stdout

## 6. Output Formats

### JSONL (`.auto/runs/measure_YYYYMMDD.jsonl`)
One line per run, append-only. Each line is a `MeasureReport` serialized via `asdict()`.

### Markdown (`.auto/reports/measure_YYYYMMDD.md`)
```markdown
# Measure Report — YYYY-MM-DD

| Metric | Value | Status |
|---|---|---|
| Parsing Latency | 12,345 chars/sec | ✅ |
| Supersession Precision | 94.0% (CI: 83-99%) | ✅ |
| Temporal Accuracy | 93.3% (14/15) | ✅ |
| RRF Fusion Gain | +8.2% over best single leg | ✅ |
| Context Precision | 72.0% of retrieved chunks relevant | ⚠️ <80% target |
| MPS Peak Memory | 4.8 GB / 48 GB (90% headroom) | ✅ |

---
*Generated by .auto/measure.sh — SEBI Circular RAG*
```

### Status Thresholds (for markdown table)
| Metric | ✅ Pass | ⚠️ Warning | ❌ Fail |
|---|---|---|---|
| Parsing Latency | >10,000 chars/sec | 5,000-10,000 | <5,000 |
| Supersession Precision | ≥90% | 80-90% | <80% |
| Temporal Accuracy | ≥90% | 75-90% | <75% |
| RRF Fusion Gain | >5% improvement | 0-5% | Negative (RRF hurts) |
| Context Precision | ≥80% | 60-80% | <60% |
| MPS Headroom | >30 GB | 15-30 GB | <15 GB |

## 7. Makefile Integration

Add to existing `Makefile`:
```makefile
measure:
	@bash .auto/measure.sh

.PHONY: measure
```

### `.auto/measure.sh` (thin wrapper)
```bash
#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== SEBI Circular RAG — Automated Metrics ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Ensure output directories exist
mkdir -p .auto/runs .auto/reports

# Run the Python benchmark script
python scripts/bench_metrics.py "$@"

echo ""
echo "=== Metrics written to .auto/runs/ and .auto/reports/ ==="
```

## 8. Testing Strategy

### Unit Tests (`tests/test_measure.py`)
- Test each `measure_*` function with mock pipeline and synthetic golden data
- Test `MeasureResult` and `MeasureReport` serialization
- Test CLI argument parsing in `bench_metrics.py`

### Integration Tests (smoke)
- Run with `--dry-run` to verify pipeline builds without errors
- Run with a small golden subset (n=5) to verify end-to-end output

### Test Data
- Use existing `HashEmbedder` and `LexicalReranker` for fast offline tests
- Real metrics (MPS memory, parsing latency) require real pipeline — mark as `not integration` for fast tests

## 9. Dependencies

- **No new external dependencies** — all metrics use existing libraries:
  - `torch` (for MPS measurement)
  - `faiss`, `bm25s` (already in use via retriever)
  - `lineage.py`, `benchmark.py`, `eval_harness.py` (existing modules)
- **New files:** 4 source files + 1 bash script + Makefile addition

## 10. Scope Boundaries (YAGNI)

### In Scope
- All 6 metrics as specified above
- JSONL + markdown output
- CLI interface with `--metrics` filter
- Makefile integration

### Out of Scope (explicitly excluded)
- CI/CD integration (on-demand only per user decision)
- Pre-commit hook (on-demand only)
- Trend analysis across runs (JSONL is append-only; trend analysis is a future enhancement)
- Alerting / threshold enforcement (markdown shows status but no automated gating)
- Parallel metric execution (sequential is fine for ~5-10 min total runtime)
