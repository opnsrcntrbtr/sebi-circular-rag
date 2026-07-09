"""Benchmark dataset validation, export, and reproducibility helpers.

The public benchmark layer is intentionally separate from the production RAG
pipeline. Gold labels stay immutable; optional judge outputs and run artifacts
are written beside them.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .eval_harness import _doc, _unique, load_golden
from .ingest_pdf import normalize_circular_number
from .pipeline import RAGPipeline
from .segment import Chunk

TASK_TYPES = {
    "title_direct",
    "body_paraphrase",
    "numeric_table",
    "lineage_supersession",
    "exact_circular",
    "hard_negative",
    "far_negative",
}
DIFFICULTIES = {"easy", "medium", "hard"}
CITATION_LEVELS = {"none", "circular", "chunk"}
REVIEW_STATUSES = {"seeded", "draft", "reviewed", "adjudicated"}


@dataclass(frozen=True)
class BenchmarkIssue:
    item_id: str
    message: str


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dir_fingerprint(path: str | Path) -> str:
    """Stable digest over files in a directory tree."""
    root = Path(path)
    h = hashlib.sha256()
    if not root.exists():
        return ""
    for p in sorted(x for x in root.rglob("*") if x.is_file()):
        h.update(str(p.relative_to(root)).encode("utf-8"))
        h.update(b"\0")
        h.update(sha256_file(p).encode("ascii"))
        h.update(b"\0")
    return h.hexdigest()


def git_commit(root: str | Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:  # noqa: BLE001 - metadata should not break benchmarks
        return "unknown"


def run_metadata(
    *,
    root: str | Path,
    corpus_path: str | Path,
    index_dir: str | Path,
    golden_path: str | Path,
    run_name: str,
    models: dict[str, str],
    params: dict[str, Any],
    started_at: float | None = None,
) -> dict[str, Any]:
    root_p = Path(root)
    env_keys = (
        "TOKENIZERS_PARALLELISM",
        "OMP_NUM_THREADS",
        "PYTORCH_ENABLE_MPS_FALLBACK",
        "HF_HUB_DISABLE_XET",
    )
    return {
        "run_name": run_name,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(started_at or time.time())),
        "git_commit": git_commit(root_p),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "models": models,
        "params": params,
        "env": {k: os.environ.get(k, "") for k in env_keys},
        "corpus_sha256": sha256_file(corpus_path),
        "index_fingerprint": dir_fingerprint(index_dir),
        "golden_sha256": sha256_file(golden_path),
    }


def enrich_golden_item(item: dict[str, Any], *, source_version: str = "golden_v5") -> dict[str, Any]:
    """Convert legacy golden rows into the v6 schema."""
    abstain = bool(item.get("abstain"))
    relevant = [str(c).strip() for c in item.get("relevant_circulars", [])]
    item_id = str(item["id"])
    if abstain:
        task_type = "far_negative" if item_id == "abstain" else "hard_negative"
        difficulty = "easy" if item_id == "abstain" else "hard"
        citation_level = "none"
    elif item_id.startswith("para-"):
        task_type = "body_paraphrase"
        difficulty = "hard"
        citation_level = "circular"
    else:
        task_type = "title_direct"
        difficulty = "medium"
        citation_level = "circular"
    return {
        "id": item_id,
        "query": item["query"],
        "relevant_circulars": relevant,
        "relevant_chunks": item.get("relevant_chunks", []),
        "answer_contains": item.get("answer_contains", ""),
        "must_contain": (
            [item["answer_contains"]] if item.get("answer_contains") else []
        ),
        "must_not_contain": item.get("must_not_contain", []),
        "abstain": abstain,
        "task_type": item.get("task_type", task_type),
        "difficulty": item.get("difficulty", difficulty),
        "expected_citation_level": item.get("expected_citation_level", citation_level),
        "rationale": item.get(
            "rationale",
            f"Seeded from {source_version}; needs human review before adjudicated use.",
        ),
        "label_source": item.get("label_source", source_version),
        "review_status": item.get("review_status", "seeded"),
    }


def build_golden_v6(seed_path: str | Path, out_path: str | Path) -> list[dict[str, Any]]:
    rows = [enrich_golden_item(item) for item in load_golden(seed_path)]
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return rows


def validate_golden(rows: list[dict[str, Any]]) -> list[BenchmarkIssue]:
    issues: list[BenchmarkIssue] = []
    seen: set[str] = set()
    for i, row in enumerate(rows):
        item_id = str(row.get("id", f"<row-{i}>"))
        if item_id in seen:
            issues.append(BenchmarkIssue(item_id, "duplicate id"))
        seen.add(item_id)
        for field in (
            "query",
            "relevant_circulars",
            "relevant_chunks",
            "must_contain",
            "must_not_contain",
            "abstain",
            "task_type",
            "difficulty",
            "expected_citation_level",
            "rationale",
            "label_source",
            "review_status",
        ):
            if field not in row:
                issues.append(BenchmarkIssue(item_id, f"missing field: {field}"))
        relevant = row.get("relevant_circulars", [])
        if row.get("abstain") and relevant:
            issues.append(BenchmarkIssue(item_id, "abstain item has relevant_circulars"))
        if not row.get("abstain") and not relevant:
            issues.append(BenchmarkIssue(item_id, "answerable item has no relevant_circulars"))
        if row.get("task_type") not in TASK_TYPES:
            issues.append(BenchmarkIssue(item_id, f"invalid task_type: {row.get('task_type')}"))
        if row.get("difficulty") not in DIFFICULTIES:
            issues.append(BenchmarkIssue(item_id, f"invalid difficulty: {row.get('difficulty')}"))
        if row.get("expected_citation_level") not in CITATION_LEVELS:
            issues.append(
                BenchmarkIssue(item_id, f"invalid expected_citation_level: {row.get('expected_citation_level')}")
            )
        if row.get("review_status") not in REVIEW_STATUSES:
            issues.append(BenchmarkIssue(item_id, f"invalid review_status: {row.get('review_status')}"))
        for c in relevant:
            if not str(c).strip() or str(c) != str(c).strip():
                issues.append(BenchmarkIssue(item_id, f"invalid circular: {c}"))
    return issues


def beir_corpus_rows(chunks: list[Chunk]) -> list[dict[str, Any]]:
    rows = []
    for c in chunks:
        meta = c.meta or {}
        rows.append(
            {
                "_id": c.id,
                "title": " | ".join(
                    p for p in (c.doc_id, meta.get("subject", ""), c.section) if p
                ),
                "text": c.text,
                "doc_id": c.doc_id,
                "section": c.section,
                "issue_date": meta.get("issue_date", ""),
                "effective_date": meta.get("effective_date", ""),
                "issuing_department": meta.get("issuing_department", ""),
                "supersession_status": meta.get("supersession_status", ""),
            }
        )
    return rows


def beir_query_rows(golden: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{"_id": row["id"], "text": row["query"]} for row in golden]


def qrels_rows(golden: list[dict[str, Any]], chunks: list[Chunk]) -> list[tuple[str, str, int]]:
    by_doc: dict[str, list[Chunk]] = {}
    by_id = {c.id: c for c in chunks}
    for c in chunks:
        by_doc.setdefault(normalize_circular_number(c.doc_id), []).append(c)
    rows: list[tuple[str, str, int]] = []
    for item in golden:
        if item.get("abstain"):
            continue
        explicit = [cid for cid in item.get("relevant_chunks", []) if cid in by_id]
        if explicit:
            rows.extend((item["id"], cid, 2) for cid in explicit)
            continue
        for doc in item.get("relevant_circulars", []):
            # Circular-level labels are expanded to all chunks with a lower
            # grade. Curated chunk labels can later override with grade 2.
            for c in by_doc.get(normalize_circular_number(doc), []):
                rows.append((item["id"], c.id, 1))
    return rows


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_qrels(path: str | Path, rows: list[tuple[str, str, int]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        f.write("query-id\tcorpus-id\tscore\n")
        for qid, cid, score in rows:
            f.write(f"{qid}\t{cid}\t{score}\n")


def write_trec_run(
    path: str | Path,
    run_name: str,
    rankings: dict[str, list[tuple[str, float]]],
) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        for qid, ranked in rankings.items():
            for rank, (doc_id, score) in enumerate(ranked, start=1):
                f.write(f"{qid} Q0 {doc_id} {rank} {score:.8f} {run_name}\n")


def export_beir(
    *,
    chunks: list[Chunk],
    golden: list[dict[str, Any]],
    out_dir: str | Path,
) -> dict[str, int]:
    out = Path(out_dir)
    write_jsonl(out / "corpus.jsonl", beir_corpus_rows(chunks))
    write_jsonl(out / "queries.jsonl", beir_query_rows(golden))
    qrels = qrels_rows(golden, chunks)
    write_qrels(out / "qrels" / "test.tsv", qrels)
    return {"corpus": len(chunks), "queries": len(golden), "qrels": len(qrels)}


def run_retrieval_benchmark(
    pipeline: RAGPipeline,
    golden: list[dict[str, Any]],
    *,
    top_n: int = 50,
    run_name: str = "offline-smoke",
) -> dict[str, Any]:
    rankings: dict[str, list[tuple[str, float]]] = {}
    recall10: list[float] = []
    latencies: list[float] = []
    for item in golden:
        t0 = time.time()
        retrieved = pipeline.retriever.retrieve(item["query"], top_n=top_n)
        latencies.append(time.time() - t0)
        rankings[item["id"]] = [(c.id, float(score)) for c, score in retrieved]
        if not item.get("abstain"):
            docs = _unique(_doc(c.id) for c, _ in retrieved)
            relevant = set(item.get("relevant_circulars", []))
            hit = len(set(docs[:10]) & relevant)
            recall10.append(hit / len(relevant) if relevant else 0.0)
    mean = lambda xs: sum(xs) / len(xs) if xs else 0.0
    return {
        "run_name": run_name,
        "n": len(golden),
        "recall_at_10": mean(recall10),
        "avg_retrieval_latency_s": mean(latencies),
        "rankings": rankings,
    }


def write_judge_results(path: str | Path, rows: list[dict[str, Any]]) -> None:
    """Write optional research-only judge outputs beside, never into, gold labels."""
    serializable = []
    for row in rows:
        r = dict(row)
        r.setdefault("research_only", True)
        serializable.append(r)
    write_jsonl(path, serializable)
