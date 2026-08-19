"""End-to-end wiring: segment -> hybrid retrieve -> rerank -> generate/abstain."""
from __future__ import annotations

from dataclasses import dataclass

from .embeddings import Embedder
from .generate import Answer, Generator, Judge, _BRACKET, _CITATION_MARGIN_DEFAULT, answer_with_abstention
from .lineage import Lineage, demote_superseded, superseded_citations
from .paraphrase_rescue import QueryRewriter, rescue_pool
from .regulations import reg_display_name
from .rerank import Reranker
from .retrieve import HybridRetriever
from .segment import Chunk


class _LineageAwareReranker:
    """Reranker wrapper that re-applies lineage handling to its output.

    The paraphrase rescue compares the rescued list's top score against the
    score floor. That comparison is only meaningful if the rescued list has had
    as-of exclusion / supersession demotion applied — otherwise a rescue could
    clear the floor on a chunk that demotion would have pushed back below it.
    """

    def __init__(self, reranker: "Reranker", pipeline: "RAGPipeline",
                 as_of: str | None) -> None:
        self._reranker = reranker
        self._pipeline = pipeline
        self._as_of = as_of

    def rerank(self, query: str, candidates: list[Chunk]) -> list[tuple[Chunk, float]]:
        return self._pipeline._apply_lineage(
            self._reranker.rerank(query, candidates), self._as_of)


@dataclass
class RAGPipeline:
    retriever: HybridRetriever
    reranker: Reranker
    generator: Generator
    abstain_threshold: float = 0.40  # calibrated (cross-encoder); see scripts/calibrate.py
    lineage: Lineage | None = None  # P2: flag superseded citations in answers
    superseded_penalty: float = 0.3  # demote superseded chunks in rerank (0 = drop)
    # prereg 2026-08-19-supersession-confidence-tier: penalty for circulars whose
    # supersession is only inferred from the master-circular title heuristic.
    # None = untiered (production default); see lineage.demote_superseded.
    inferred_supersession_penalty: float | None = None
    judge: Judge | None = None  # groundedness gate (ADR-001 item 7)
    regulatory_index: dict[str, dict] | None = None  # repealed-basis staleness signal
    citation_scorer: Reranker | None = None  # B': post-hoc answer-relevance filter
    citation_margin: float = _CITATION_MARGIN_DEFAULT  # margin for select_citations
    citation_min_keep: int = 1  # floor on kept citations; see select_citations
    query_rewriter: QueryRewriter | None = None  # paraphrase rescue (prereg 2026-08-19)
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

    def _apply_lineage(
        self, reranked: list[tuple[Chunk, float]], as_of: str | None,
    ) -> list[tuple[Chunk, float]]:
        """As-of exclusion or supersession demotion, applied to a reranked list.

        Extracted so the paraphrase-rescue list passes through exactly the same
        lineage handling as the original — a rescue must not be able to smuggle
        a superseded circular past supersession.
        """
        if as_of is not None and self.lineage is not None:
            # As-of queries score against the law as it stood on `as_of`:
            # a circular is excluded if (a) it did not yet exist on `as_of`,
            # or (b) a superseding circular had already been issued by `as_of`
            # (per-edge timing). Exclusion — not demotion — because a 0.3x
            # penalty leaves superseded chunks above non-superseded alternatives
            # when the former score ~1.0 pre-demotion (asof-p2 regression).
            # `kept or reranked` below falls back to the undemoted list if every
            # chunk is excluded, so no answer is lost. The global demotion in the
            # non-as_of branch (line 76) still uses superseded_penalty.
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
                if superseded_on_asof:
                    continue  # not the governing law on as_of; exclude from context
                kept.append((c, s))
            kept.sort(key=lambda cs: -cs[1])
            reranked = kept or reranked
        elif self.lineage is not None:
            reranked = demote_superseded(
                reranked, self.lineage, self.superseded_penalty,
                self.inferred_supersession_penalty)
        return reranked

    def query(
        self, question: str, pool: int = 50, top_k: int = 5,
        advisory: bool = False, as_of: str | None = None,
    ) -> tuple[Answer, list[str]]:
        candidates = self.retriever.retrieve(question, top_n=pool)
        pool_chunks = [c for c, _ in candidates]
        reranked = self._apply_lineage(
            self.reranker.rerank(question, pool_chunks), as_of)
        # Paraphrase rescue (prereg 2026-08-19): only fires when the pool is
        # already below the score floor, so rows that answer today are
        # untouched. `_LineageAwareReranker` keeps the rescued list on the same
        # lineage path, so the score compared against the floor is the score
        # the gate will see.
        reranked, rescue_query = rescue_pool(
            question, pool_chunks, reranked,
            _LineageAwareReranker(self.reranker, self, as_of),
            self.query_rewriter, self.abstain_threshold,
        )
        ans = answer_with_abstention(
            question, reranked, self.generator, self.abstain_threshold, top_k,
            judge=self.judge, advisory=advisory,
            citation_scorer=self.citation_scorer,
            citation_margin=self.citation_margin,
            citation_min_keep=self.citation_min_keep,
        )
        if rescue_query is not None:
            # Audit trail on an existing dict field — no new Answer field.
            ans.confidence["rescue_query"] = rescue_query
        if self.lineage is not None and not ans.abstained and ans.citations:
            flagged = superseded_citations(ans.citations, self.lineage)
            if flagged:
                ans.superseded = flagged  # full metadata: every flagged context
                # Strip bracket citations — flag only circulars actually discussed,
                # not merely cited via [ID] brackets (Option A compat).
                text_no_brackets = _BRACKET.sub("", ans.text)
                cited_in_text = {old: new for old, new in flagged.items()
                                 if old in text_no_brackets}
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
        if (self.regulatory_index is not None and not ans.abstained
                and ans.citations):
            seen, notes = set(), []
            for cit in ans.citations:
                cn = cit.split("#", 1)[0]
                if cn in seen:
                    continue
                seen.add(cn)
                entry = self.regulatory_index.get(cn)
                if (entry is None
                        or entry["regulatory_basis_status"] != "repealed_basis"
                        or cn not in _BRACKET.sub("", ans.text)):
                    continue
                for reg in entry["regulations"]:
                    if reg["status"] != "repealed":
                        continue
                    name = reg_display_name(reg["short_name"], reg["year"])
                    succ = reg["superseded_by"]
                    if succ:
                        sname = reg_display_name(succ["short_name"], succ["year"])
                        notes.append(f"{cn} rests on the {name}, which has been "
                                     f"repealed and replaced by the {sname}")
                    else:
                        notes.append(f"{cn} rests on the {name}, which has been "
                                     "repealed")
            if notes:
                ans.text += (
                    "\n\nNote: this answer cites circular(s) resting on a repealed "
                    "regulation — " + "; ".join(notes)
                    + ". Refer to the current regulation(s) for the governing "
                    "requirements."
                )
        if not ans.abstained and ans.unsupported_citations:
            refs = ", ".join(ans.unsupported_citations)
            ans.text += (
                f"\n\nWarning: the answer references {refs}, which is not in the "
                "retrieved sources — treat this citation with caution."
            )
        retrieved_ids = [c.id for c, _ in candidates]
        return ans, retrieved_ids
