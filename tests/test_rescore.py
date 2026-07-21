"""Re-scoring archived runfiles: round-trip and agreement with the live metric."""
from __future__ import annotations

import pytest

from sebi_rag.benchmark import (
    per_query_recall,
    read_trec_run,
    run_retrieval_benchmark,
    write_trec_run,
)
from sebi_rag.embeddings import HashEmbedder
from sebi_rag.generate import ExtractiveStubGenerator
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.rerank import LexicalReranker
from sebi_rag.segment import CircularMeta, hierarchical_chunk


class TestReadTrecRun:
    def test_round_trips_a_simple_run(self, tmp_path):
        rankings = {"q1": [("A/1#s#0", 0.5), ("A/2#s#0", 0.25)]}
        p = tmp_path / "run.trec"
        write_trec_run(p, "r", rankings)
        assert read_trec_run(p) == {
            "q1": [("A/1#s#0", 0.5), ("A/2#s#0", 0.25)]
        }

    def test_recovers_doc_ids_containing_spaces(self, tmp_path):
        """The archived runfiles embed section headings in the doc id."""
        doc = "SEBI/HO/CIR/2023/1#3. With the issuance of this Circular#8"
        p = tmp_path / "run.trec"
        write_trec_run(p, "baseline-retrieval", {"surv": [(doc, 0.03)]})
        assert read_trec_run(p)["surv"][0][0] == doc

    def test_orders_documents_by_rank_not_file_order(self, tmp_path):
        p = tmp_path / "run.trec"
        p.write_text(
            "q1 Q0 doc-b 2 0.10000000 r\nq1 Q0 doc-a 1 0.90000000 r\n",
            encoding="utf-8",
        )
        assert [d for d, _ in read_trec_run(p)["q1"]] == ["doc-a", "doc-b"]

    def test_malformed_line_rejected(self, tmp_path):
        p = tmp_path / "run.trec"
        p.write_text("q1 Q0 doc 1\n", encoding="utf-8")
        with pytest.raises(ValueError):
            read_trec_run(p)


class TestPerQueryRecall:
    def _golden(self):
        return [
            {"id": "a", "query": "q", "relevant_circulars": ["A/1"], "abstain": False},
            {"id": "b", "query": "q", "relevant_circulars": ["Z/9"], "abstain": False},
            {"id": "no", "query": "q", "relevant_circulars": [], "abstain": True},
        ]

    def test_scores_each_query_and_skips_abstain_items(self):
        rankings = {
            "a": [("A/1#s#0", 1.0)],
            "b": [("A/1#s#0", 1.0)],
            "no": [("A/1#s#0", 1.0)],
        }
        scores = per_query_recall(rankings, self._golden())
        assert scores == {"a": 1.0, "b": 0.0}

    def test_deduplicates_chunks_to_circulars_before_cutoff(self):
        """Ten chunks of one circular must not crowd the cutoff: the k applies
        to unique circulars, as in run_retrieval_benchmark."""
        ranked = [(f"B/2#s#{i}", 1.0) for i in range(10)] + [("A/1#s#0", 0.1)]
        scores = per_query_recall({"a": ranked}, self._golden()[:1], k=10)
        assert scores["a"] == 1.0

    def test_mean_reproduces_the_archived_aggregate(self, tmp_path):
        """End-to-end guarantee behind the re-scoring script: replaying a
        runfile yields exactly the recall_at_10 the run recorded."""
        meta = CircularMeta(circular_number="SMOKE/1", issue_date="2026-01-01",
                            subject="nomination norms for demat accounts")
        chunks = hierarchical_chunk(
            "1. Nomination\nInvestors may nominate a beneficiary or opt out.", meta)
        pipeline = RAGPipeline.build(
            chunks=chunks, embedder=HashEmbedder(dim=128),
            reranker=LexicalReranker(), generator=ExtractiveStubGenerator(),
        )
        golden = [{"id": "smoke", "query": "nomination beneficiary demat account",
                   "relevant_circulars": ["SMOKE/1"], "abstain": False}]
        result = run_retrieval_benchmark(pipeline, golden, run_name="t")

        p = tmp_path / "run.trec"
        write_trec_run(p, "t", result["rankings"])
        scores = per_query_recall(read_trec_run(p), golden)
        replayed = sum(scores.values()) / len(scores)
        assert replayed == pytest.approx(result["recall_at_10"])
