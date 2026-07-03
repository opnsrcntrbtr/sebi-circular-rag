"""P1 evaluation-harness test (offline).

Loads the real seed corpus (data/corpus/circulars.jsonl), adds the synthetic
sample circulars as distractors, runs the golden set through the harness with
the offline stack, and checks the metric suite.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from sebi_rag.corpus import load_circulars
from sebi_rag.embeddings import HashEmbedder
from sebi_rag.eval_harness import load_golden, run_eval
from sebi_rag.generate import ExtractiveStubGenerator
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.rerank import LexicalReranker
from sebi_rag.segment import hierarchical_chunk

from test_pipeline import CIRCULARS  # synthetic distractors

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
GOLDEN = ROOT / "eval" / "golden" / "golden_v1.jsonl"


def _pipeline():
    chunks = load_circulars(CORPUS)
    for meta, text in CIRCULARS:  # distractors
        chunks.extend(hierarchical_chunk(text, meta))
    return RAGPipeline.build(
        chunks=chunks,
        embedder=HashEmbedder(dim=512),
        reranker=LexicalReranker(),
        generator=ExtractiveStubGenerator(),
        abstain_threshold=0.30,  # calibrated: separates out-of-domain (~0.2) from valid (>=0.44)
    )


def test_real_corpus_loads_with_provenance_fields():
    chunks = load_circulars(CORPUS)
    assert chunks
    c = chunks[0]
    assert c.doc_id == "SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123"
    assert c.meta["version_lineage"]  # lineage captured (P2 seed)


def test_eval_harness_metric_suite():
    report = run_eval(_pipeline(), load_golden(GOLDEN), k=10)
    assert report.n == 5
    # the real circular is retrieved among distractors for every answered query
    assert report.recall_at_k == pytest.approx(1.0)
    assert report.mrr > 0.0
    assert 0.0 < report.ndcg_at_k <= 1.0
    # abstention correct on all 5 (g5 abstains, g1-g4 answer) at calibrated 0.30
    assert report.abstention_accuracy == pytest.approx(1.0)
    # the relevant circular is always among the citations
    assert report.citation_recall == pytest.approx(1.0)
    # precision in (0, 1]; with fine-grained chunking the relevant circular's
    # chunks dominate top-k so precision is high. The absolute value is the P1
    # calibration signal (varies with top_k / corpus), not a fixed invariant.
    assert 0.0 < report.citation_precision <= 1.0
    assert report.groundedness_proxy >= 0.0
    assert report.avg_latency_s >= 0.0
