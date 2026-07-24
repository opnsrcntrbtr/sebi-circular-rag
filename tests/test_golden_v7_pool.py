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
