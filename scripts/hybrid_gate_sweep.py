"""Hybrid gate sweep — preregistered analysis (2026-08-13).

Runs the pipeline over answerable rows to find false abstentions,
collects subject_sim/section_score/rerank_top signals, and applies
hybrid gate thresholds post-hoc per the preregistered spec.

Usage: python scripts/hybrid_gate_sweep.py [--all]
"""
from __future__ import annotations

import argparse, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
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

s = Settings.load()
recs = load_records(s.corpus_path)
lin = build_lineage(recs)
emb = BGEM3Embedder(device="mps")
retr = HybridRetriever.load(s.index_dir, emb)
rer = CrossEncoderReranker(device="mps")
judge = SubjectSimJudge(emb, threshold=0.42, section_threshold=0.60)
gen = ExtractiveStubGenerator()

pipeline = RAGPipeline(
    retriever=retr, reranker=rer, generator=gen,
    abstain_threshold=0.42, lineage=lin, superseded_penalty=0.3,
    judge=judge, citation_scorer=None,
)

golden = load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")

# Find answerable rows where pipeline abstains (false abstentions)
answerable = [r for r in golden if not r.get("abstain")]

parser = argparse.ArgumentParser()
parser.add_argument("--all", action="store_true", help="Run all 219 answerable rows (slow)")
args = parser.parse_args()

if not args.all:
    answerable = answerable[:50]
    print(f"Running on first {len(answerable)} answerable rows (use --all for all 219)")
else:
    print(f"Running on all {len(answerable)} answerable rows")

false_abstentions = []
for i, item in enumerate(answerable):
    ans, _ = pipeline.query(item["query"], top_k=5)
    if ans.abstained:
        rec = {
            "id": item.get("id", "?"),
            "query": item["query"][:80],
            "abstention_reason": ans.abstention_reason or "none",
        }
        if hasattr(ans, 'confidence') and ans.confidence:
            rec["subject_sim"] = ans.confidence.get("subject_sim")
            rec["section_sim"] = ans.confidence.get("section_sim")
            rec["rerank_top"] = ans.confidence.get("rerank_top")
        false_abstentions.append(rec)
    if (i + 1) % 25 == 0:
        print(f"  Processed {i+1}/{len(answerable)}, false abstentions so far: {len(false_abstentions)}")

print(f"\nFalse abstentions: {len(false_abstentions)}")
for r in sorted(false_abstentions, key=lambda x: -x.get("rerank_top", 0)):
    subj = r.get('subject_sim')
    sect = r.get('section_sim')
    top = r.get('rerank_top')
    sv = f"{subj:.4f}" if subj is not None else 'N/A'
    sev = f"{sect:.4f}" if sect is not None else 'N/A'
    tv = f"{top:.4f}" if top is not None else 'N/A'
    print(f"  {r['id']:20s} reason={r['abstention_reason']:18s} subj={sv:>8s}  sect={sev:>8s}  top={tv:>8s}")

# Apply hybrid gate thresholds
thresholds = [0.85, 0.80, 0.75]
print(f"\n=== Hybrid Gate Sweep ===")

for thresh in thresholds:
    rescues = []
    for r in false_abstentions:
        subj = r.get("subject_sim") or 0.0
        sect = r.get("section_sim") or 0.0
        top = r.get("rerank_top") or 0.0
        
        # Current gate: subject_sim >= 0.42 OR section_score >= 0.60
        current_pass = subj >= 0.42 or sect >= 0.60
        
        # Hybrid gate: current_pass OR rerank_top >= thresh
        hybrid_pass = current_pass or top >= thresh
        
        if not current_pass and hybrid_pass:
            rescues.append(r)
    
    print(f"\nThreshold {thresh}:")
    print(f"  Rescues: {len(rescues)}")
    for r in rescues:
        print(f"    {r['id']:20s} subj={r.get('subject_sim', 0):.4f} top={r.get('rerank_top', 0):.4f}")
