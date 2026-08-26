"""SPIKE — throwaway, not preregistered. Answers one question before any R6 design work:

Does bge-m3 retrieve competitively under mean pooling AT ALL, on today's existing chunk
boundaries (no late chunking yet — just a pooling-mode swap), or is CLS-vs-mean too large a
gap to make late chunking (which REQUIRES mean pooling — arXiv:2409.04701) viable with this
model regardless of implementation effort?

Method (cheap, not a full re-encode): for a small sample of golden_v7 rows, take the
production retriever's top-N candidate pool (built from the persisted CLS-pooled FAISS index
— no re-embedding needed for this step), then re-embed ONLY those pooled candidates + the
query with a second BGEM3Embedder instance constructed with pooling_method="mean", and check
where the correct document ranks under mean-pooled cosine similarity within that same pool.
This is the same "fixed pool, swap one thing, rescore" pattern this repo already uses for
reranker/scorer arms (bench_retrieval.py --rerank, jina_citation_scorer_cohort.py) — applied
here to a pooling-mode question instead of a reranker/scorer question.

Not a recall@k measurement from scratch (the pool itself was chosen by CLS embeddings), and not
adopted or preregistered. If mean pooling can't even preserve the ranking of a document CLS
already found, it has no chance of doing so from a full-document late-chunked embedding either
— decisive in the negative direction. A positive result would still need a real preregistered
spec before design work resumes; a positive result here is necessary, not sufficient.

Usage: PYTHONPATH=src python scratchpad/late_chunking_pooling_spike.py [--n 30]
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

for _k, _v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(_k, _v)

GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
POOL = 50


def eligible(item: dict) -> bool:
    return (not item.get("abstain") and not item.get("as_of")
            and bool(item.get("relevant_circulars")))


def main(n: int) -> None:
    import numpy as np
    from sebi_rag.eval_harness import _doc, load_golden
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.retrieve import HybridRetriever
    from sebi_rag.settings import Settings

    s = Settings.load()
    print("loading production (CLS-pooled) embedder + retriever...", file=sys.stderr)
    cls_embedder = BGEM3Embedder()  # pooling_method defaults to "cls" — production today
    retriever = HybridRetriever.load(Path(s.index_dir), cls_embedder)

    print("loading a SECOND bge-m3 instance with pooling_method='mean' "
          "(not persisted, not indexed — spike only)...", file=sys.stderr)
    from FlagEmbedding import BGEM3FlagModel
    mean_model = BGEM3FlagModel("BAAI/bge-m3", pooling_method="mean", devices="mps")

    def mean_encode(texts: list[str]) -> "np.ndarray":
        v = np.asarray(mean_model.encode(texts, return_dense=True,
                                          batch_size=16)["dense_vecs"], dtype="float32")
        norm = np.linalg.norm(v, axis=1, keepdims=True)
        norm[norm == 0] = 1.0
        return v / norm

    items = [i for i in load_golden(GOLDEN) if eligible(i)][:n]
    print(f"sample: {len(items)} rows", file=sys.stderr)

    cls_hits, mean_hits, cls_topk_hits, mean_topk_hits = 0, 0, 0, 0
    top_k = 10
    t0 = time.time()
    for i, it in enumerate(items, 1):
        relevant = set(it["relevant_circulars"])
        cand = retriever.retrieve(it["query"], top_n=POOL)  # [(Chunk, cls_score), ...] desc
        pool_docs = {_doc(c.id) for c, _ in cand}
        if not relevant.issubset(pool_docs):
            continue  # not a fair comparison if CLS pool doesn't even contain the gold doc

        cls_hits += 1
        cls_top = [_doc(c.id) for c, _ in cand[:top_k]]
        if relevant & set(cls_top):
            cls_topk_hits += 1

        # re-embed the SAME pool + query under mean pooling
        chunks = [c for c, _ in cand]
        qv = mean_encode([it["query"]])[0]
        cv = mean_encode([c.text for c in chunks])
        scores = cv @ qv
        order = (-scores).argsort()
        mean_top = [_doc(chunks[j].id) for j in order[:top_k]]
        mean_hits += 1
        if relevant & set(mean_top):
            mean_topk_hits += 1

        if i % 10 == 0:
            print(f"  {i}/{len(items)}  ({time.time()-t0:.0f}s)", file=sys.stderr)

    print(f"\nfair-comparison rows (gold doc in CLS pool): {cls_hits}")
    print(f"CLS-pooled recall@{top_k} within that pool:  {cls_topk_hits}/{cls_hits}")
    print(f"mean-pooled recall@{top_k} on the SAME pool: {mean_topk_hits}/{mean_hits}")
    print(f"runtime: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    args = ap.parse_args()
    main(args.n)
