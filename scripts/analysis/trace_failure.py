"""Trace each retrieval failure backwards through the pipeline (throwaway).

Checklist per spec: (1) answer text present in ingested corpus text?
(2) does it land in a coherent chunk? (3) dense-only vs sparse-only vs fused
rank of the gold doc, (4) reranker placement. Emits a proposed primary
bucket; final assignment is human (see the taxonomy report).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {  # env guards before torch/FlagEmbedding/faiss init (see bench_retrieval.py)
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(k, v)

from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.ingest_pdf import normalize_circular_number as norm  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402


def _ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def heading_only(text: str) -> bool:
    """Degenerate chunk heuristic: short and no sentence-final punctuation
    (the nominee-count bug class)."""
    body = text.split("|")[-1].strip()  # chunks are prefixed "doc | subject | ..."
    return len(body) < 80 and not re.search(r"[.;:]\s*$", body)


def first_gold_rank(chunk_ids: list[str], gold_docs: set[str]) -> int:
    for i, cid in enumerate(chunk_ids, start=1):
        if norm(cid.split("#", 1)[0]) in gold_docs:
            return i
    return -1


def first_answer_rank(chunk_ids: list[str], answer_ids: set[str]) -> int:
    """Rank of the first chunk that actually carries the answer text."""
    for i, cid in enumerate(chunk_ids, start=1):
        if cid in answer_ids:
            return i
    return -1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--failures", action="append", required=True,
                    help="failures.jsonl (repeatable)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=50)
    args = ap.parse_args()

    corpus = {}
    for line in (ROOT / "data" / "corpus" / "circulars.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        corpus[norm(r["circular_number"])] = r.get("text", "")

    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(ROOT / "data" / "index", emb)
    reranker = CrossEncoderReranker(device="mps")

    failures = []
    for fp in args.failures:
        failures += [json.loads(l) for l in Path(fp).read_text(encoding="utf-8").splitlines() if l.strip()]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in failures:
            gold_docs = {norm(c) for c in row["relevant_circulars"]}
            needles = [_ws(m) for m in row.get("must_contain", []) if m.strip()]

            # (1) extraction: is the answer text in the ingested corpus?
            hay = " ".join(_ws(corpus.get(d, "")) for d in gold_docs)
            text_in_corpus = all(n in hay for n in needles) if needles else bool(
                gold_docs & set(corpus)
            )

            # (2) chunking: which gold-doc chunks carry the answer, and are
            # they coherent?
            gold_chunks = []
            for c in retr.chunks:
                if norm(c.doc_id) in gold_docs and (
                    not needles or any(n in _ws(c.text) for n in needles)
                ):
                    gold_chunks.append({
                        "id": c.id, "len": len(c.text),
                        "heading_only": heading_only(c.text),
                    })

            # (3) retriever isolation
            q = row["query"]
            dense = [retr.chunks[i].id for i, _ in retr.dense.search(q, args.k)]
            sparse = [retr.chunks[i].id for i, _ in retr.sparse.search(q, args.k)]
            fused_pairs = retr.retrieve(q, top_n=args.k)
            fused = [c.id for c, _ in fused_pairs]
            dense_rank = first_gold_rank(dense, gold_docs)
            sparse_rank = first_gold_rank(sparse, gold_docs)
            fused_rank = first_gold_rank(fused, gold_docs)
            answer_ids = {g["id"] for g in gold_chunks}
            ans_dense_rank = first_answer_rank(dense, answer_ids)
            ans_sparse_rank = first_answer_rank(sparse, answer_ids)
            ans_fused_rank = first_answer_rank(fused, answer_ids)

            # (4) reranker placement (only meaningful if gold in candidates)
            rerank_rank = ans_rerank_rank = -1
            if fused_rank != -1:
                reranked = reranker.rerank(q, [c for c, _ in fused_pairs])
                reranked_ids = [c.id for c, _ in reranked]
                rerank_rank = first_gold_rank(reranked_ids, gold_docs)
                ans_rerank_rank = first_answer_rank(reranked_ids, answer_ids)

            # proposed bucket, in checklist order; when needles exist the
            # answer-chunk ranks are the real signal, doc ranks otherwise
            d_rank = ans_dense_rank if needles else dense_rank
            s_rank = ans_sparse_rank if needles else sparse_rank
            f_rank = ans_fused_rank if needles else fused_rank
            r_rank = ans_rerank_rank if needles else rerank_rank
            if not text_in_corpus:
                bucket = "extraction_loss"
            elif needles and not gold_chunks:
                bucket = "chunking_defect"  # text in corpus but in no chunk
            elif gold_chunks and all(g["heading_only"] for g in gold_chunks):
                bucket = "chunking_defect"
            elif d_rank == -1 and s_rank == -1:
                bucket = "embedding_semantic_miss"  # neither retriever; refine by hand
            elif d_rank == -1:
                bucket = "embedding_semantic_miss"
            elif s_rank == -1:
                bucket = "sparse_vocabulary_miss"
            elif f_rank == -1 or r_rank > 10:
                bucket = "fusion_ranking_loss"
            else:
                bucket = "fusion_ranking_loss"  # retrieved-but-low default
            # NOTE: metadata_filter_loss cannot be auto-detected here (no
            # metadata filtering happens inside HybridRetriever.retrieve);
            # assign it manually in Task 5 if as-of/validity scoping explains
            # a miss.

            f.write(json.dumps({
                "id": row["id"], "class": row["class"], "source": row["source"],
                "query": q, "text_in_corpus": text_in_corpus,
                "gold_chunks": gold_chunks[:10],
                "dense_rank": dense_rank, "sparse_rank": sparse_rank,
                "fused_rank": fused_rank, "rerank_rank": rerank_rank,
                "ans_dense_rank": ans_dense_rank,
                "ans_sparse_rank": ans_sparse_rank,
                "ans_fused_rank": ans_fused_rank,
                "ans_rerank_rank": ans_rerank_rank,
                "proposed_bucket": bucket,
            }, ensure_ascii=False) + "\n")
            print(f"{row['id']}: {bucket} (doc d={dense_rank} s={sparse_rank} "
                  f"f={fused_rank} r={rerank_rank} | ans d={ans_dense_rank} "
                  f"s={ans_sparse_rank} f={ans_fused_rank} r={ans_rerank_rank})")


if __name__ == "__main__":
    main()
