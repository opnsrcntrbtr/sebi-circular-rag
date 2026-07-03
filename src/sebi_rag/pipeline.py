"""End-to-end wiring: segment -> hybrid retrieve -> rerank -> generate/abstain."""
from __future__ import annotations

from dataclasses import dataclass

from .embeddings import Embedder
from .generate import Answer, Generator, Judge, answer_with_abstention
from .lineage import Lineage, demote_superseded, superseded_citations
from .rerank import Reranker
from .retrieve import HybridRetriever
from .segment import Chunk


@dataclass
class RAGPipeline:
    retriever: HybridRetriever
    reranker: Reranker
    generator: Generator
    abstain_threshold: float = 0.40  # calibrated (cross-encoder); see scripts/calibrate.py
    lineage: Lineage | None = None  # P2: flag superseded citations in answers
    superseded_penalty: float = 0.3  # demote superseded chunks in rerank (0 = drop)
    judge: Judge | None = None  # groundedness gate (ADR-001 item 7)

    @classmethod
    def build(
        cls,
        chunks: list[Chunk],
        embedder: Embedder,
        reranker: Reranker,
        generator: Generator,
        abstain_threshold: float = 0.40,
        lineage: Lineage | None = None,
    ) -> "RAGPipeline":
        return cls(
            retriever=HybridRetriever.build(chunks, embedder),
            reranker=reranker,
            generator=generator,
            abstain_threshold=abstain_threshold,
            lineage=lineage,
        )

    def query(
        self, question: str, pool: int = 50, top_k: int = 3,
        advisory: bool = False,
    ) -> tuple[Answer, list[str]]:
        candidates = self.retriever.retrieve(question, top_n=pool)
        reranked = self.reranker.rerank(question, [c for c, _ in candidates])
        if self.lineage is not None:
            reranked = demote_superseded(reranked, self.lineage, self.superseded_penalty)
        ans = answer_with_abstention(
            question, reranked, self.generator, self.abstain_threshold, top_k,
            judge=self.judge, advisory=advisory,
        )
        if self.lineage is not None and not ans.abstained and ans.citations:
            flagged = superseded_citations(ans.citations, self.lineage)
            if flagged:
                ans.superseded = flagged
                notes = "; ".join(
                    f"{old} has been superseded by {', '.join(new)}"
                    for old, new in flagged.items()
                )
                ans.text += (
                    f"\n\nNote: this answer cites circular(s) that are no longer in "
                    f"force — {notes}. Refer to the superseding circular(s) for "
                    "current requirements."
                )
        if not ans.abstained and ans.unsupported_citations:
            refs = ", ".join(ans.unsupported_citations)
            ans.text += (
                f"\n\nWarning: the answer references {refs}, which is not in the "
                "retrieved sources — treat this citation with caution."
            )
        retrieved_ids = [c.id for c, _ in candidates]
        return ans, retrieved_ids
