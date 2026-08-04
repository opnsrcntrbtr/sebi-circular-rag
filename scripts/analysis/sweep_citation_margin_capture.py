"""Capture-once margin sweep for B' selective citations.

One pipeline pass over the golden_v7 adjudicated ANSWERABLE rows using the REAL
pipeline.query (citation_scorer=None), which yields the authoritative deduped
top-k contexts (as ans.citations) and the real abstained flag — so nothing is
re-implemented. Per answered row we recompute the answer-relevance scores once
(rer.rerank(answer_text, contexts)); every margin is then evaluated instantly on
those cached scores. Citation metrics use the same formulae as golden_v7.score.

Self-validation: reproduces the four full-pass points already measured
(mechanical 0.119/0.888, m0.30 0.241/0.747, m0.20 0.274/0.694, m0.15 0.292/0.646).
Only GUIDES the margin choice; the authoritative gate floors come from the real
derive_thresholds run afterward.
"""
from __future__ import annotations
import os, sys, json
from pathlib import Path

ROOT = Path("/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG")
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag.embeddings import BGEM3Embedder
from sebi_rag.eval_harness import load_golden, _doc, _unique
from sebi_rag.generate import ExtractiveStubGenerator, SubjectSimJudge
from sebi_rag.lineage import build_lineage, load_records
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.rerank import CrossEncoderReranker
from sebi_rag.retrieve import HybridRetriever
from sebi_rag.settings import Settings

def log(*a): print(*a, file=sys.stderr, flush=True)

s = Settings.load()
log(f"top_k={s.top_k} abstain_threshold={s.abstain_threshold}")
recs = load_records(s.corpus_path)
lin = build_lineage(recs)
emb = BGEM3Embedder(device="mps")
retr = HybridRetriever.load(s.index_dir, emb)
rer = CrossEncoderReranker(device="mps")
_sect = os.environ.get("SEBI_RAG_SECT_THRESHOLD", "0.60")
judge = SubjectSimJudge(emb, threshold=0.42,
                        section_threshold=(None if _sect.lower() in ("off", "0") else float(_sect)))
# Mechanical pipeline (citation_scorer=None): ans.citations == deduped top-k contexts.
pipe = RAGPipeline(retriever=retr, reranker=rer, generator=ExtractiveStubGenerator(),
                   abstain_threshold=s.abstain_threshold, lineage=lin, judge=judge)
by_id = {c.id: c for c in retr.chunks}

rows = load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")
adj = [r for r in rows if r.get("review_status") == "adjudicated" and not r.get("abstain")]
log(f"adjudicated answerable rows: {len(adj)}")

cache = []  # per row: {abstained, relevant, scored:[(cid, score)] | None}
for i, item in enumerate(adj):
    relevant = set(item.get("relevant_circulars", []))
    ans, _ = pipe.query(item["query"], top_k=s.top_k, as_of=item.get("as_of"))
    if ans.abstained or not ans.citations:
        cache.append({"abstained": True, "relevant": relevant, "scored": None})
        continue
    contexts = [by_id[c] for c in ans.citations if c in by_id]
    scored = rer.rerank(contexts[0].text, contexts)          # answer-relevance, once
    cache.append({"abstained": False, "relevant": relevant,
                  "scored": [(c.id, float(sc)) for c, sc in scored]})
    if i % 40 == 0:
        log(f"  cached {i+1}/{len(adj)}")

mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else None

def cited_docs(entry, margin, mechanical=False):
    if entry["abstained"]:
        return []
    scored = entry["scored"]
    if mechanical:
        ids = [cid for cid, _ in scored]
    else:
        top = scored[0][1]
        ids = [cid for cid, sc in scored if sc >= top - margin]
    return _unique(_doc(cid) for cid in ids)

def metrics(margin, mechanical=False):
    precs, recs = [], []
    for e in cache:
        cited = cited_docs(e, margin, mechanical)
        rel = e["relevant"]
        hit = len(set(cited) & rel)
        precs.append(hit / len(cited) if cited else 0.0)
        recs.append(hit / len(rel) if rel else 0.0)
    return {"citation_precision": mean(precs), "citation_recall": mean(recs), "n": len(precs)}

results = [{"label": "mechanical (cite-all)", "margin": None, **metrics(0, mechanical=True)}]
for m in (0.60, 0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15):
    results.append({"label": f"margin={m}", "margin": m, **metrics(m)})
for r in results:
    log(f"  -> {r}")

print(json.dumps(results, indent=2))
Path("/private/tmp/claude-501/-Users-ianpinto-sebi-circular-sota-rag-SEBI-circular-RAG/ba147b89-7ac0-4eda-b081-8151d7b0a6d2/scratchpad/capture_sweep_result.json").write_text(json.dumps(results, indent=2))
