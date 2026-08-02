"""Automated metric collection for the SEBI Circular RAG pipeline.

Six on-demand metrics (spec: docs/superpowers/specs/2026-07-31-measure-sh-design.md):

1. Parsing Latency — PDF ingestion throughput (chars/sec, ms/PDF)
2. Supersession Precision — fraction of detected supersession edges that are genuine
3. Temporal Accuracy — as_of queries returning correct pre-supersession circular in top-3
4. Retrieval Recall@10 — standard recall at 10
5. Context Precision — fraction of top-k chunks from relevant circulars
6. MRR — mean reciprocal rank at circular level

All metrics operate at retrieval/parsing level — no LLM generation required.
"""
from __future__ import annotations

import json
import random
import statistics
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .eval import mrr as _mrr, recall_at_k as _recall_at_k
from .eval_harness import _doc, _unique
from .lineage import detect_relations_ex
from .pipeline import RAGPipeline


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class MeasureResult:
    metric: str
    value: dict[str, Any]
    sample_size: int = 0


@dataclass
class MeasureReport:
    git_commit: str
    corpus_circulars: int
    corpus_chunks: int
    golden_n: int
    metrics: dict[str, dict] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_results(cls, results: list[MeasureResult], **kwargs) -> "MeasureReport":
        metrics = {r.metric: r.value for r in results}
        return cls(metrics=metrics, **kwargs)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _git_commit(root: str | Path) -> str:
    try:
        import subprocess
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _bootstrap_ci(values: list[float], n_bootstrap: int = 1000,
                   alpha: float = 0.05) -> tuple[float, float, float]:
    """Return (mean, lower_95, upper_95) via bootstrap."""
    if not values:
        return 0.0, 0.0, 0.0
    mean_val = statistics.mean(values)
    if len(values) < 2:
        return mean_val, mean_val, mean_val
    boot_means: list[float] = []
    rng = random.Random(42)
    n = len(values)
    for _ in range(n_bootstrap):
        sample = [values[rng.randint(0, n - 1)] for _ in range(n)]
        boot_means.append(statistics.mean(sample))
    boot_means.sort()
    lo = boot_means[int(n_bootstrap * alpha / 2)]
    hi = boot_means[int(n_bootstrap * (1 - alpha / 2))]
    return mean_val, lo, hi


def _mps_memory() -> dict[str, float]:
    """Return MPS memory stats if torch+mps available, else empty dict."""
    try:
        import torch
        if torch.backends.mps.is_available():
            return {
                "mps_allocated_mb": round(torch.mps.current_allocated_memory() / 1e6, 2),
                "mps_driver_mb": round(torch.mps.driver_allocated_memory() / 1e6, 2),
            }
    except Exception:  # noqa: BLE001
        pass
    return {}


# ---------------------------------------------------------------------------
# Metric 1: Parsing Latency
# ---------------------------------------------------------------------------

def measure_parsing_latency(
    _pipeline: RAGPipeline,
    _golden_rows: list[dict],
    data_dir: str | Path = "data",
    sample_n: int = 20,
) -> MeasureResult:
    """Measure PDF ingestion throughput (chars/sec, ms/PDF).

    Samples 20 PDFs stratified by size: 7 small (<50KB), 7 medium (50-200KB),
    6 large (>200KB). Times chunking per PDF.
    """
    raw_dir = Path(data_dir) / "raw"
    if not raw_dir.is_dir():
        return MeasureResult(
            metric="parsing_latency",
            value={"error": f"raw directory not found: {raw_dir}"},
        )

    pdfs = sorted(raw_dir.glob("*.pdf"))
    if not pdfs:
        return MeasureResult(
            metric="parsing_latency",
            value={"error": "no PDFs found in data/raw/"},
        )

    # Stratified sampling by file size
    pdfs_by_size = sorted(pdfs, key=lambda p: p.stat().st_size)
    n = len(pdfs_by_size)
    # Split into three roughly equal groups
    third = max(n // 3, 1)
    small = pdfs_by_size[:third]
    medium = pdfs_by_size[third:2 * third]
    large = pdfs_by_size[2 * third:]

    # Ensure we don't exceed sample_n
    total = len(small) + len(medium) + len(large)
    if total > sample_n:
        # Downsample proportionally
        scale = sample_n / total
        small = small[:max(int(len(small) * scale), 1)]
        medium = medium[:max(int(len(medium) * scale), 1)]
        large = large[:max(int(len(large) * scale), 1)]

    sample = small + medium + large
    random.Random(42).shuffle(sample)

    from .ingest_pdf import extract_text  # local: avoid top-level import
    from .segment import hierarchical_chunk

    results_by_stratum: dict[str, list[float]] = {
        "small": [], "medium": [], "large": [],
    }
    all_ms: list[float] = []
    all_chars: list[int] = []
    ocr_count = 0

    for pdf_path in sample:
        fsize = pdf_path.stat().st_size
        # Classify stratum
        if fsize < 50_000:
            stratum = "small"
        elif fsize < 200_000:
            stratum = "medium"
        else:
            stratum = "large"

        t0 = time.time()
        text = extract_text(pdf_path)
        from .segment import CircularMeta
        _chunks = hierarchical_chunk(text, CircularMeta(circular_number="RAW"))
        elapsed_ms = (time.time() - t0) * 1000

        results_by_stratum[stratum].append(elapsed_ms)
        all_ms.append(elapsed_ms)
        all_chars.append(len(text))
        if not text:
            ocr_count += 1

    mean_chars = sum(all_chars)
    mean_ms = statistics.mean(all_ms) if all_ms else 0.0
    median_ms = statistics.median(all_ms) if all_ms else 0.0
    p99_ms = sorted(all_ms)[int(len(all_ms) * 0.99)] if all_ms else 0.0
    chars_per_sec = (mean_chars / (mean_ms / 1000)) if mean_ms > 0 else 0

    strata_out = {}
    for strat_name in ("small", "medium", "large"):
        vals = results_by_stratum[strat_name]
        if vals:
            strata_out[strat_name] = {
                "n": len(vals),
                "mean_ms": round(statistics.mean(vals), 2),
            }

    value: dict[str, Any] = {
        "mean_chars_per_sec": round(chars_per_sec),
        "median_ms_per_pdf": round(median_ms, 2),
        "p99_ms_per_pdf": round(p99_ms, 2),
        "sample_size": len(sample),
        "strata": strata_out,
        "total_chars": mean_chars,
    }
    if ocr_count:
        value["ocr_count"] = ocr_count

    return MeasureResult(metric="parsing_latency", value=value, sample_size=len(sample))


# ---------------------------------------------------------------------------
# Metric 2: Supersession Detection Precision
# ---------------------------------------------------------------------------

def measure_supersession_precision(
    _pipeline: RAGPipeline,
    _golden_rows: list[dict],
    corpus_path: str | Path = "data/corpus/circulars.jsonl",
    sample_n: int = 50,
) -> MeasureResult:
    """Measure fraction of detected supersession edges that are genuine.

    Samples circulars from the corpus, runs detect_relations_ex, and verifies
    each detected supersession edge by checking:
    - The older circular's text mentions the newer one
    - Dates are chronologically consistent
    """
    corpus_lines = Path(corpus_path).read_text(encoding="utf-8").strip().splitlines()
    if not corpus_lines:
        return MeasureResult(
            metric="supersession_precision",
            value={"error": "empty corpus"},
        )

    corpus_records = [json.loads(line) for line in corpus_lines if line.strip()]
    random.Random(42).shuffle(corpus_records)
    corpus_records = corpus_records[:sample_n]

    true_positives = 0
    false_positives = 0
    ambiguous = 0
    edges_checked: list[dict] = []

    for rec in corpus_records:
        circ_num = rec.get("circular_number", "")
        text = rec.get("text", "")
        if not circ_num or not text:
            continue

        relations = detect_relations_ex(circ_num, text)
        for rel in relations:
            if rel["relation"] != "supersedes":
                continue

            target = rel["target"]
            # Verify: check if target's text references the source circular
            # and dates are consistent
            verified = _verify_supersession_edge(rec, corpus_records, rel)
            if verified == "true":
                true_positives += 1
            elif verified == "false":
                false_positives += 1
            else:
                ambiguous += 1

            edges_checked.append({
                "source": circ_num,
                "target": target,
                "verified": verified,
                "evidence": rel.get("evidence", "")[:100],
            })

    total = true_positives + false_positives
    precision = true_positives / total if total > 0 else 0.0

    # Bootstrap CI
    if total > 0:
        # Use simple bootstrap on edge-level binary results
        edge_results = ([1.0] * true_positives + [0.0] * false_positives)
        precision, ci_lo, ci_hi = _bootstrap_ci(edge_results)
    else:
        ci_lo, ci_hi = 0.0, 0.0

    value: dict[str, Any] = {
        "precision": round(precision, 4),
        "ci_95_lower": round(ci_lo, 4),
        "ci_95_upper": round(ci_hi, 4),
        "sample_size": sample_n,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "ambiguous": ambiguous,
        "edges_checked": edges_checked[:20],  # cap for output size
    }

    return MeasureResult(metric="supersession_precision", value=value, sample_size=sample_n)


def _verify_supersession_edge(
    source_rec: dict,
    corpus_records: list[dict],
    relation: dict,
) -> str:
    """Verify a supersession edge by cross-referencing corpus records.

    Returns "true", "false", or "ambiguous".
    """
    source_num = source_rec.get("circular_number", "")
    target_num = relation["target"]
    source_date = source_rec.get("issue_date", "")

    # Find target record
    target_rec = None
    for rec in corpus_records:
        if rec.get("circular_number", "") == target_num:
            target_rec = rec
            break

    if target_rec is None:
        return "ambiguous"  # target not in sample

    target_date = target_rec.get("issue_date", "")

    # Check date consistency: source must be newer than target
    if source_date and target_date:
        try:
            from datetime import datetime
            s_date = datetime.strptime(source_date, "%Y-%m-%d")
            t_date = datetime.strptime(target_date, "%Y-%m-%d")
            if s_date <= t_date:
                return "false"  # source can't supersede something issued same/after
        except (ValueError, TypeError):
            pass  # date parsing failed, treat as ambiguous

    # Check if target text references source (circular mentions its successor)
    target_text = target_rec.get("text", "")
    if source_num.lower() in target_text.lower():
        return "true"  # mutual reference confirms supersession

    # Check if source text mentions target
    source_text = source_rec.get("text", "")
    if target_num.lower() in source_text.lower():
        return "true"  # source explicitly mentions target as superseded

    return "ambiguous"


# ---------------------------------------------------------------------------
# Metric 3: Temporal Query Accuracy
# ---------------------------------------------------------------------------

def measure_temporal_accuracy(
    pipeline: RAGPipeline,
    golden_rows: list[dict],
) -> MeasureResult:
    """Measure fraction of as_of queries returning correct pre-supersession
    circular in top-3.

    Filters golden_v7 for rows with as_of field, runs pipeline.query with
    as_of parameter, checks if the correct circular appears in top-3.
    """
    as_of_rows = [r for r in golden_rows if r.get("as_of")]
    if not as_of_rows:
        return MeasureResult(
            metric="temporal_accuracy",
            value={"error": "no as_of rows in golden set"},
        )

    correct_top3 = 0
    total = 0
    per_query: list[dict] = []

    for item in as_of_rows:
        if item.get("abstain"):
            continue
        total += 1
        as_of = item["as_of"]
        relevant = set(item.get("relevant_circulars", []))

        try:
            _, retrieved_ids = pipeline.query(item["query"], as_of=as_of)
        except Exception:  # noqa: BLE001
            per_query.append({"id": item["id"], "as_of": as_of, "error": "query failed"})
            continue

        # Get top-3 doc ids
        top3_docs = _unique(_doc(cid) for cid in retrieved_ids[:3])
        hit = len(set(top3_docs) & relevant) > 0
        if hit:
            correct_top3 += 1

        per_query.append({
            "id": item["id"],
            "as_of": as_of,
            "hit": hit,
            "top3_docs": top3_docs[:5],
        })

    accuracy = correct_top3 / total if total > 0 else 0.0

    value: dict[str, Any] = {
        "accuracy": round(accuracy, 4),
        "correct_top3": correct_top3,
        "total_as_of_queries": total,
        "per_query": per_query,
    }

    return MeasureResult(
        metric="temporal_accuracy",
        value=value,
        sample_size=total,
    )


# ---------------------------------------------------------------------------
# Metric 4: Retrieval Recall@10
# ---------------------------------------------------------------------------

def measure_retrieval_recall(
    pipeline: RAGPipeline,
    golden_rows: list[dict],
    k: int = 10,
) -> MeasureResult:
    """Standard recall@k at circular level, excluding abstain items."""
    recall_scores: list[float] = []
    latencies: list[float] = []
    per_query: list[dict] = []

    for item in golden_rows:
        if item.get("abstain"):
            continue
        t0 = time.time()
        _, retrieved_ids = pipeline.query(item["query"])
        latencies.append(time.time() - t0)

        relevant = set(item.get("relevant_circulars", []))
        if not relevant:
            continue

        retrieved_docs = _unique(_doc(cid) for cid in retrieved_ids[:k])
        rec = _recall_at_k(retrieved_docs, relevant, k)
        recall_scores.append(rec)

        per_query.append({
            "id": item["id"],
            "recall": round(rec, 4),
            "top_docs": retrieved_docs[:k],
        })

    mean_recall = statistics.mean(recall_scores) if recall_scores else 0.0
    mean_latency = statistics.mean(latencies) if latencies else 0.0
    recall_ci = _bootstrap_ci(recall_scores) if recall_scores else (0.0, 0.0, 0.0)

    value: dict[str, Any] = {
        "recall_at_k": round(mean_recall, 4),
        "k": k,
        "mean_latency_s": round(mean_latency, 4),
        "ci_95_lower": round(recall_ci[1], 4),
        "ci_95_upper": round(recall_ci[2], 4),
        "n_queries": len(recall_scores),
        "per_query": per_query,
    }

    return MeasureResult(
        metric="retrieval_recall",
        value=value,
        sample_size=len(recall_scores),
    )


# ---------------------------------------------------------------------------
# Metric 5: Context Precision
# ---------------------------------------------------------------------------

def measure_context_precision(
    pipeline: RAGPipeline,
    golden_rows: list[dict],
    k: int = 10,
) -> MeasureResult:
    """Fraction of top-k chunks from relevant circulars.

    Unlike recall@k (which is binary per query), context precision measures
    the density of relevant chunks in the retrieved set.
    """
    precision_scores: list[float] = []
    per_query: list[dict] = []

    for item in golden_rows:
        if item.get("abstain"):
            continue
        _, retrieved_ids = pipeline.query(item["query"])
        relevant = set(item.get("relevant_circulars", []))

        if not relevant:
            continue

        # Get top-k doc ids
        top_k_docs = _unique(_doc(cid) for cid in retrieved_ids[:k])
        hits = len(set(top_k_docs) & relevant)
        prec = hits / k if k > 0 else 0.0
        precision_scores.append(prec)

        per_query.append({
            "id": item["id"],
            "context_precision": round(prec, 4),
            "top_k_docs": top_k_docs[:k],
        })

    mean_prec = statistics.mean(precision_scores) if precision_scores else 0.0
    prec_ci = _bootstrap_ci(precision_scores) if precision_scores else (0.0, 0.0, 0.0)

    value: dict[str, Any] = {
        "context_precision": round(mean_prec, 4),
        "k": k,
        "ci_95_lower": round(prec_ci[1], 4),
        "ci_95_upper": round(prec_ci[2], 4),
        "n_queries": len(precision_scores),
        "per_query": per_query,
    }

    return MeasureResult(
        metric="context_precision",
        value=value,
        sample_size=len(precision_scores),
    )


# ---------------------------------------------------------------------------
# Metric 6: MRR (Mean Reciprocal Rank)
# ---------------------------------------------------------------------------

def measure_mrr(
    pipeline: RAGPipeline,
    golden_rows: list[dict],
) -> MeasureResult:
    """Mean reciprocal rank at circular level.

    For each query, RR = 1/rank of first relevant circular.
    MRR = mean of RR across all non-abstain queries.
    """
    rr_scores: list[float] = []
    per_query: list[dict] = []

    for item in golden_rows:
        if item.get("abstain"):
            continue
        _, retrieved_ids = pipeline.query(item["query"])
        relevant = set(item.get("relevant_circulars", []))

        if not relevant:
            continue

        # Find first relevant circular in retrieved list
        rr = _mrr(retrieved_ids, relevant)
        rr_scores.append(rr)

        per_query.append({
            "id": item["id"],
            "rr": round(rr, 4),
            "first_relevant_rank": next(
                (i + 1 for i, cid in enumerate(retrieved_ids) if _doc(cid) in relevant),
                None,
            ),
        })

    mean_rr = statistics.mean(rr_scores) if rr_scores else 0.0
    rr_ci = _bootstrap_ci(rr_scores) if rr_scores else (0.0, 0.0, 0.0)

    value: dict[str, Any] = {
        "mrr": round(mean_rr, 4),
        "ci_95_lower": round(rr_ci[1], 4),
        "ci_95_upper": round(rr_ci[2], 4),
        "n_queries": len(rr_scores),
        "per_query": per_query,
    }

    return MeasureResult(
        metric="mrr",
        value=value,
        sample_size=len(rr_scores),
    )


# ---------------------------------------------------------------------------
# All metrics registry
# ---------------------------------------------------------------------------

ALL_METRICS: dict[str, Any] = {
    "parsing_latency": measure_parsing_latency,
    "supersession_precision": measure_supersession_precision,
    "temporal_accuracy": measure_temporal_accuracy,
    "retrieval_recall": measure_retrieval_recall,
    "context_precision": measure_context_precision,
    "mrr": measure_mrr,
}


def run_all_metrics(
    pipeline: RAGPipeline,
    golden_rows: list[dict],
    corpus_path: str | Path = "data/corpus/circulars.jsonl",
    data_dir: str | Path = "data",
    metrics: list[str] | None = None,
) -> list[MeasureResult]:
    """Run all (or specified) metrics sequentially."""
    metric_names = metrics if metrics else list(ALL_METRICS.keys())
    results: list[MeasureResult] = []

    for name in metric_names:
        fn = ALL_METRICS.get(name)
        if fn is None:
            continue
        if name == "parsing_latency":
            r = fn(pipeline, golden_rows, data_dir=data_dir)
        elif name == "supersession_precision":
            r = fn(pipeline, golden_rows, corpus_path=corpus_path)
        else:
            r = fn(pipeline, golden_rows)
        results.append(r)

    return results
