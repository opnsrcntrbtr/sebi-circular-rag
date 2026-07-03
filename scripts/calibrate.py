"""Calibrate top_k and the abstention threshold against the citation-precision
signal, using the real stack (bge-m3 + bge-reranker-v2-m3 on MPS) over the
golden set. Retrieve+rerank is cached per query; only top_k / threshold vary.

Run:  HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
      PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src .venv/bin/python scripts/calibrate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag import eval as M  # noqa: E402
from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.eval_harness import _doc, _unique, load_golden  # noqa: E402
from sebi_rag.lineage import build_lineage, demote_superseded, load_records  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402

INDEX = ROOT / "data" / "index"
CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
lineage = build_lineage(load_records(CORPUS))
import os  # noqa: E402

GOLDEN = os.environ.get(
    "SEBI_RAG_GOLDEN",
    sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "eval" / "golden" / "golden_v5.jsonl"),
)
golden = load_golden(GOLDEN)
print(f"golden set: {GOLDEN}", flush=True)
emb = BGEM3Embedder(device="mps")
if HybridRetriever.index_exists(INDEX):
    retr = HybridRetriever.load(INDEX, emb)  # fast: no re-encode
else:
    retr = HybridRetriever.build(load_circulars(ROOT / "data" / "corpus" / "circulars.jsonl"), emb)
print(f"corpus chunks={len(retr.chunks)}  golden items={len(golden)}", flush=True)
rer = CrossEncoderReranker(device="mps")
print("models loaded", flush=True)

cache = []
for item in golden:
    cands = retr.retrieve(item["query"], top_n=50)
    reranked = rer.rerank(item["query"], [c for c, _ in cands])
    reranked = demote_superseded(reranked, lineage)  # supersession-aware
    retrieved_docs = _unique(_doc(c.id) for c, _ in cands)
    cache.append((item, reranked, retrieved_docs))


def evaluate(top_k: int, thr: float, k: int = 10) -> dict:
    recs, cprec, crec, abst = [], [], [], []
    for item, reranked, retrieved_docs in cache:
        relevant = set(item.get("relevant_circulars", []))
        top_score = reranked[0][1] if reranked else 0.0
        abstained = (not reranked) or top_score < thr
        if item.get("abstain"):
            abst.append(abstained)
            continue
        abst.append(not abstained)
        recs.append(M.recall_at_k(retrieved_docs, relevant, k))
        cited = [] if abstained else _unique(_doc(c.id) for c, _ in reranked[:top_k])
        hit = len(set(cited) & relevant)
        cprec.append(hit / len(cited) if cited else 0.0)
        crec.append(hit / len(relevant) if relevant else 0.0)
    mean = lambda xs: sum(xs) / len(xs) if xs else 0.0
    return dict(top_k=top_k, thr=thr, recall=mean(recs),
                cprec=mean(cprec), crec=mean(crec), abst=mean(abst))


rows = [evaluate(tk, th) for tk in (1, 2, 3, 5) for th in (0.05, 0.2, 0.4, 0.6)]
print("\ntop_k  thr  recall@10  cit_prec  cit_rec  abst_acc", flush=True)
for r in rows:
    print(f"{r['top_k']:>4}  {r['thr']:.1f}  {r['recall']:>8.2f}  "
          f"{r['cprec']:>8.2f}  {r['crec']:>7.2f}  {r['abst']:>7.2f}", flush=True)

valid = [r for r in rows if r["recall"] >= 0.999 and r["crec"] >= 0.999
         and r["abst"] >= 0.999]
best = max(valid, key=lambda r: (r["cprec"], r["top_k"]), default=None)
print("\nRECOMMEND:", best, flush=True)

# Per-item diagnostics at the pipeline defaults, so failures are traceable
# across index changes (e.g. F1 chunk enrichment).
TOP_K, THR = 3, 0.4
print(f"\n--- per-item diagnostics @ top_k={TOP_K} thr={THR} ---", flush=True)
for item, reranked, retrieved_docs in cache:
    relevant = set(item.get("relevant_circulars", []))
    top = reranked[0][1] if reranked else 0.0
    abstained = (not reranked) or top < THR
    if item.get("abstain"):
        print(f"{'OK  ' if abstained else 'FAIL'} {item['id']:<15} abstain  "
              f"top_score={top:.3f}", flush=True)
        continue
    r10 = M.recall_at_k(retrieved_docs, relevant, 10)
    cited = [] if abstained else _unique(_doc(c.id) for c, _ in reranked[:TOP_K])
    hit = len(set(cited) & relevant)
    ok = r10 >= 0.999 and hit == len(relevant) and not abstained
    print(f"{'OK  ' if ok else 'FAIL'} {item['id']:<15} r@10={r10:.0f} "
          f"top={top:.3f} cited={cited} want={sorted(relevant)}", flush=True)
