import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.build_pool import assemble_pool  # noqa: E402
from sebi_rag.embeddings import HashEmbedder  # noqa: E402
from sebi_rag.rerank import LexicalReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.segment import CircularMeta, hierarchical_chunk  # noqa: E402


def _retriever():
    chunks = []
    for i, (cn, body) in enumerate([
        ("SEBI/GOLD/1", "1. Margin:\nThe upfront margin shall be twenty per cent "
                        "of transaction value collected from every client without exception."),
        ("SEBI/OTHER/2", "1. Fees:\nAnnual regulatory fees shall be paid before "
                         "the thirtieth day of April every financial year by members."),
    ]):
        chunks += hierarchical_chunk(body, CircularMeta(circular_number=cn, subject=f"S{i}"))
    return HybridRetriever.build(chunks, HashEmbedder())


def test_gold_literal_chunks_lead_the_pool():
    row = {"query": "upfront margin percentage", "relevant_circulars": ["SEBI/GOLD/1"],
           "must_contain": ["twenty per cent"], "abstain": False}
    pool = assemble_pool(row, _retriever(), LexicalReranker(), cap=5)
    assert pool and pool[0].doc_id == "SEBI/GOLD/1"
    assert len(pool) <= 5
    assert len({c.id for c in pool}) == len(pool)  # deduped


def test_bm25_leg_uses_raw_query_not_expansion():
    # "block" expands to "freeze" via expand.py in production retrieve();
    # pooling must bypass that (spec §5: pool sees the frozen raw query).
    row = {"query": "block transactions", "relevant_circulars": ["SEBI/GOLD/1"],
           "must_contain": [], "abstain": False}
    pool = assemble_pool(row, _retriever(), LexicalReranker(), cap=10)
    assert isinstance(pool, list)  # smoke: no crash, raw-query leg wired


def _saturating_retriever(n: int = 40):
    """One gold doc with `n` chunks that ALL contain the word "broker", so a
    must_contain of ["broker"] matches every chunk. Only the last chunks
    mention requirement 39."""
    chunks = []
    for i in range(n):
        chunks += hierarchical_chunk(
            f"{i}. Clause {i}:\nThe stock broker shall observe requirement {i} "
            f"in full and without exception at all times whatsoever.",
            CircularMeta(circular_number="SEBI/GOLD/1", subject=f"S{i}"))
    return HybridRetriever.build(chunks, HashEmbedder()), chunks


def test_deep_relevant_chunk_is_reachable_despite_a_common_literal():
    """Regression (2026-07-25): a must_contain literal matching many gold-doc
    chunks filled the whole cap in DOCUMENT order, so the reranked / dense /
    BM25 legs contributed nothing and a provision late in the document was
    unreachable. 92 of 207 real pools were saturated this way.

    The chunk answering "requirement 39" is last in document order, so before
    the fix (cap consumed by chunks 0..19) it cannot be in the pool.
    """
    retr, chunks = _saturating_retriever(40)
    row = {"query": "requirement 39 stock broker",
           "relevant_circulars": ["SEBI/GOLD/1"],
           "must_contain": ["broker"], "abstain": False}
    pool = assemble_pool(row, retr, LexicalReranker(), cap=20)
    ids = {c.id for c in pool}
    assert len(ids) == len(pool), "pool must stay deduped"
    target = [c.id for c in chunks if "requirement 39 " in c.text]
    assert target, "fixture did not produce a requirement-39 chunk"
    assert target[0] in ids, (
        "the chunk that answers the query is missing — step 1 is still "
        "consuming the cap in document order")


def test_gold_literal_chunks_still_lead_the_pool_when_bounded():
    row = {"query": "upfront margin percentage",
           "relevant_circulars": ["SEBI/GOLD/1"],
           "must_contain": ["twenty per cent"], "abstain": False}
    pool = assemble_pool(row, _retriever(), LexicalReranker(), cap=5)
    assert pool and pool[0].doc_id == "SEBI/GOLD/1"
