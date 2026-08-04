"""Margin sweep for B' selective citations on the golden_v7 adjudicated set.

One model load; per margin, build a RAGPipeline with citation_scorer=rer and
that margin, score every adjudicated row via the REAL score_row, and report
mean citation_precision / citation_recall / recall / abstention. Includes a
mechanical baseline (citation_scorer=None == cite-all) for reference.

This only GUIDES the margin choice; the authoritative gate floors come from
the real derive_thresholds run afterward.
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
from sebi_rag.eval_harness import load_golden
from sebi_rag.generate import ExtractiveStubGenerator, SubjectSimJudge
from sebi_rag.lineage import build_lineage, load_records
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.rerank import CrossEncoderReranker
from sebi_rag.retrieve import HybridRetriever
from sebi_rag.settings import Settings
from golden_v7.score import score_row, vectors

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

rows = load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")
adj = [r for r in rows if r.get("review_status") == "adjudicated"]
log(f"adjudicated rows: {len(adj)}")

mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else None

def run(citation_scorer, margin, label):
    pipe = RAGPipeline(retriever=retr, reranker=rer, generator=ExtractiveStubGenerator(),
                       abstain_threshold=s.abstain_threshold, lineage=lin, judge=judge,
                       citation_scorer=citation_scorer, citation_margin=margin)
    scored = [score_row(pipe, item, s.top_k) for item in adj]
    v = vectors(scored)
    row = {"label": label, "margin": margin,
           "citation_precision": mean(v["citation_precision"]),
           "citation_recall": mean(v["citation_recall"]),
           "recall_at_k": mean(v["recall"]),
           "abstention": mean(v["abstention"]),
           "n_cited_rows": len(v["citation_precision"])}
    log(f"  -> {row}")
    return row

results = []
results.append(run(None, 0.0, "mechanical (B' off, cite-all)"))
for m in (0.30, 0.20, 0.15, 0.10, 0.05):
    results.append(run(rer, m, f"B' margin={m}"))

print(json.dumps(results, indent=2))
Path("/private/tmp/claude-501/-Users-ianpinto-sebi-circular-sota-rag-SEBI-circular-RAG/ba147b89-7ac0-4eda-b081-8151d7b0a6d2/scratchpad/sweep_result.json").write_text(json.dumps(results, indent=2))
