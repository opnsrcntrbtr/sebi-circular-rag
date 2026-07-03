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


def load_golden(path: str | Path) -> list[dict]:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def run_eval(pipeline: RAGPipeline, golden: list[dict], k: int = 10) -> EvalReport:
    recs, mrrs, ndcgs, cprec, crec, ground, faith = [], [], [], [], [], [], []
    abstain_ok, latencies = [], []

    for item in golden:
        relevant = set(item.get("relevant_circulars", []))
        t0 = time.time()
        ans, retrieved_ids = pipeline.query(item["query"])
        latencies.append(time.time() - t0)

        if item.get("abstain"):
            abstain_ok.append(ans.abstained)
            continue

        abstain_ok.append(not ans.abstained)
        faith.append(ans.faithfulness)
        retrieved_docs = _unique(_doc(i) for i in retrieved_ids)
        recs.append(M.recall_at_k(retrieved_docs, relevant, k))
        mrrs.append(M.mrr(retrieved_docs, relevant))
        ndcgs.append(M.ndcg_at_k(retrieved_docs, relevant, k))

        pred = _unique(_doc(c) for c in ans.citations)
        hit = len(set(pred) & relevant)
        cprec.append(hit / len(pred) if pred else 0.0)
        crec.append(hit / len(relevant) if relevant else 0.0)

        want = (item.get("answer_contains") or "").lower()
        ground.append(1.0 if want and want in ans.text.lower() else 0.0)

    mean = lambda xs: sum(xs) / len(xs) if xs else 0.0
    return EvalReport(
        n=len(golden),
        recall_at_k=mean(recs),
        mrr=mean(mrrs),
        ndcg_at_k=mean(ndcgs),
        citation_precision=mean(cprec),
        citation_recall=mean(crec),
        abstention_accuracy=mean(abstain_ok),
        groundedness_proxy=mean(ground),
        faithfulness=mean(faith),
        avg_latency_s=mean(latencies),
        k=k,
    )


def report_dict(report: EvalReport) -> dict:
    return asdict(report)
