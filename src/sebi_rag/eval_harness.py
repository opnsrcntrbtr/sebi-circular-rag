"""Golden-set evaluation harness (P1).

Runs the pipeline over a labelled golden set and reports the metric suite from
docs/project_context.md section 7: retrieval Recall@k / MRR / nDCG, citation
precision & recall, abstention accuracy, a groundedness proxy, and latency.

Chunk ids are "<circular_number>#<section>#<para>"; the document id is the
circular number (prefix before '#'), so metrics are computed at circular level.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from . import eval as M
from .pipeline import RAGPipeline


def _doc(chunk_id: str) -> str:
    return chunk_id.split("#", 1)[0]


def _unique(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


@dataclass
class EvalReport:
    n: int
    recall_at_k: float
    mrr: float
    ndcg_at_k: float
    citation_precision: float
    citation_recall: float
    abstention_accuracy: float
    groundedness_proxy: float   # answer_contains hit rate on answered items
    faithfulness: float         # bracketed citations grounded in retrieved context
    avg_latency_s: float
    k: int
    chunk_recall_at_k: float = 0.0
    chunk_mrr: float = 0.0
    chunk_labeled_n: int = 0
    must_not_cite_violation_rate: float = 0.0
    gate: dict | None = None  # same aggregate, restricted to review_status == "adjudicated"


def load_golden(path: str | Path) -> list[dict]:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _eval_item(pipeline: RAGPipeline, item: dict, k: int, by_doc) -> dict:
    from .benchmark import resolve_chunk_spans  # local: benchmark imports us at top level

    rec: dict = {"adjudicated": item.get("review_status") == "adjudicated"}
    relevant = set(item.get("relevant_circulars", []))
    t0 = time.time()
    ans, retrieved_ids = pipeline.query(item["query"], as_of=item.get("as_of"))
    rec["latency"] = time.time() - t0

    if item.get("abstain"):
        rec["abstain_ok"] = ans.abstained
        return rec

    rec["abstain_ok"] = not ans.abstained
    rec["faith"] = ans.faithfulness
    retrieved_docs = _unique(_doc(i) for i in retrieved_ids)
    rec["recall"] = M.recall_at_k(retrieved_docs, relevant, k)
    rec["mrr"] = M.mrr(retrieved_docs, relevant)
    rec["ndcg"] = M.ndcg_at_k(retrieved_docs, relevant, k)

    pred = _unique(_doc(c) for c in ans.citations)
    hit = len(set(pred) & relevant)
    rec["cprec"] = hit / len(pred) if pred else 0.0
    rec["crec"] = hit / len(relevant) if relevant else 0.0

    want = (item.get("answer_contains") or "").lower()
    rec["ground"] = 1.0 if want and want in ans.text.lower() else 0.0

    forbidden = set(item.get("must_not_cite", []))
    if forbidden:
        cited_docs = set(pred)
        rec["mnc_violation"] = 1.0 if cited_docs & forbidden else 0.0

    gold_chunks = set(resolve_chunk_spans(item, by_doc))
    if gold_chunks:
        top = retrieved_ids[:k]
        rec["chunk_recall"] = len(set(top) & gold_chunks) / len(gold_chunks)
        rec["chunk_mrr"] = next(
            (1.0 / r for r, cid in enumerate(retrieved_ids, 1) if cid in gold_chunks), 0.0)

    return rec


def _aggregate(recs: list[dict], k: int) -> dict:
    chunk = [r for r in recs if "chunk_recall" in r]
    return {
        "n": len(recs),
        "recall_at_k": _mean([r["recall"] for r in recs if "recall" in r]),
        "mrr": _mean([r["mrr"] for r in recs if "mrr" in r]),
        "ndcg_at_k": _mean([r["ndcg"] for r in recs if "ndcg" in r]),
        "citation_precision": _mean([r["cprec"] for r in recs if "cprec" in r]),
        "citation_recall": _mean([r["crec"] for r in recs if "crec" in r]),
        "abstention_accuracy": _mean([r["abstain_ok"] for r in recs]),
        "groundedness_proxy": _mean([r["ground"] for r in recs if "ground" in r]),
        "faithfulness": _mean([r["faith"] for r in recs if "faith" in r]),
        "avg_latency_s": _mean([r["latency"] for r in recs]),
        "k": k,
        "chunk_recall_at_k": _mean([r["chunk_recall"] for r in chunk]),
        "chunk_mrr": _mean([r["chunk_mrr"] for r in chunk]),
        "chunk_labeled_n": len(chunk),
        "must_not_cite_violation_rate": _mean(
            [r["mnc_violation"] for r in recs if "mnc_violation" in r]),
    }


def run_eval(pipeline: RAGPipeline, golden: list[dict], k: int = 10) -> EvalReport:
    from .benchmark import chunks_by_doc  # local: benchmark imports us at top level

    by_doc = chunks_by_doc(pipeline.retriever.chunks)
    recs = [_eval_item(pipeline, item, k, by_doc) for item in golden]
    agg = _aggregate(recs, k)
    gated = [r for r in recs if r["adjudicated"]]
    agg["gate"] = _aggregate(gated, k) if gated else None
    return EvalReport(**agg)


def report_dict(report: EvalReport) -> dict:
    return asdict(report)
