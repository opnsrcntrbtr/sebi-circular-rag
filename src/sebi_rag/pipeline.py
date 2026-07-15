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
        advisory: bool = False, as_of: str | None = None,
    ) -> tuple[Answer, list[str]]:
        candidates = self.retriever.retrieve(question, top_n=pool)
        reranked = self.reranker.rerank(question, [c for c, _ in candidates])
        if as_of is not None and self.lineage is not None:
            # As-of queries score against the law as it stood on `as_of`:
            # a circular is demoted only if a superseding circular had
            # already been issued by `as_of` (per-edge timing). The global
            # demotion below encodes *today's* status, and governing_on is
            # unreliable here — master reference-lists join circulars into
            # one giant family whose latest member out-governs everything.
            dates = {c.doc_id: (c.meta.get("issue_date") or "")
                     for c, _ in reranked}
            kept = []
            for c, s in reranked:
                d = dates.get(c.doc_id, "")
                if d and d > as_of:
                    continue  # circular did not exist on the as-of date
                superseded_on_asof = any(
                    (dates.get(nb) or "") and dates[nb] <= as_of
                    for nb in self.lineage.superseded_by.get(c.doc_id, [])
                )
                kept.append(
                    (c, s * self.superseded_penalty if superseded_on_asof else s)
                )
            kept.sort(key=lambda cs: -cs[1])
            reranked = kept or reranked
        elif self.lineage is not None:
            reranked = demote_superseded(reranked, self.lineage, self.superseded_penalty)
        ans = answer_with_abstention(
            question, reranked, self.generator, self.abstain_threshold, top_k,
            judge=self.judge, advisory=advisory,
        )
        if self.lineage is not None and not ans.abstained and ans.citations:
            flagged = superseded_citations(ans.citations, self.lineage)
            if flagged:
                ans.superseded = flagged  # full metadata: every flagged context
                cited_in_text = {old: new for old, new in flagged.items()
                                 if old in ans.text}
                if cited_in_text:
                    notes = "; ".join(
                        f"{old} has been superseded by {', '.join(new)}"
                        for old, new in cited_in_text.items()
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
