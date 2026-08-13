"""One scoring path shared by `eval_json.py` (which measures) and
`derive_thresholds.py` (which sets the floors those measurements are
compared against).

Deliberately a single function rather than a copy in each script: floors
derived under one set of semantics and compared against measurements taken
under another is a silent failure - the gate keeps reporting numbers, they
just no longer mean anything. Whatever this function does, both sides do.

Kept out of `gate_select.py` because that module must stay import-light for
the offline test suite; this one pulls in the eval stack.
"""
from __future__ import annotations


def score_row(pipeline, item: dict, top_k: int) -> dict:
    """Score one golden row through the production-shaped pipeline.

    Returns per-row components rather than aggregates so callers can pool
    them however they need (whole set, adjudicated subset, per stratum)
    without rescoring. `recall`/`citation_*` are absent on abstain rows -
    there is nothing to retrieve or cite - so callers must skip missing keys
    rather than default them to 0.0, which would drag the means down with
    scores that were never measured.
    """
    from sebi_rag import eval as M
    from sebi_rag.eval_harness import _doc, _unique

    rec = {"adjudicated": item.get("review_status") == "adjudicated"}
    relevant = set(item.get("relevant_circulars", []))
    ans, retrieved_ids = pipeline.query(
        item["query"], top_k=top_k, as_of=item.get("as_of"))

    if item.get("abstain"):
        rec["abstention"] = 1.0 if ans.abstained else 0.0
        return rec
    rec["abstention"] = 0.0 if ans.abstained else 1.0

    retrieved_docs = _unique(_doc(i) for i in retrieved_ids)
    rec["recall"] = M.recall_at_k(retrieved_docs, relevant, 10)
    # recall@10 is ceiling-limited on this corpus (~0.956 baseline), so it
    # cannot see a regression that keeps the same documents in the top-10 and
    # merely reorders them. nDCG@10 is rank-sensitive and has real headroom.
    rec["ndcg"] = M.ndcg_at_k(retrieved_docs, relevant, 10)
    # `retrieved_docs` above comes from pipeline.query's `retrieved_ids`, the
    # PRE-rerank fusion list (pipeline.py:141). The answer and its citations
    # are built from `ans.context_ids` — post-rerank, post-demote_superseded.
    # Measured 2026-08-13: fusion recall 0.9534 vs context recall 0.9240, and
    # the fusion view hides 6 of 15 complete misses.
    context_docs = _unique(_doc(i) for i in ans.context_ids)
    rec["context_recall"] = M.recall_at_k(context_docs, relevant, 10)
    cited = [] if ans.abstained else _unique(_doc(c) for c in ans.citations)
    hit = len(set(cited) & relevant)
    rec["citation_precision"] = hit / len(cited) if cited else 0.0
    rec["citation_recall"] = hit / len(relevant) if relevant else 0.0
    return rec


def vectors(recs: list[dict], adjudicated_only: bool = False) -> dict[str, list[float]]:
    """Per-row records -> metric -> score vector, skipping rows where the
    metric was never measured (see `score_row`)."""
    if adjudicated_only:
        recs = [r for r in recs if r["adjudicated"]]
    keys = ("recall", "context_recall", "ndcg", "citation_precision",
            "citation_recall", "abstention")
    return {k: [r[k] for r in recs if k in r] for k in keys}
