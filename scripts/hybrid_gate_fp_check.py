"""False positive check — hybrid gate over abstain=True rows.

Runs the pipeline over the 41 abstain=True (non-SEBI) rows and checks
how many would pass the hybrid gate at each threshold.

Usage: python scripts/hybrid_gate_fp_check.py
"""
from __future__ import annotations

import os, sys
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

# Filter to abstain=True rows (non-SEBI queries that should be rejected)
abstain_rows = [r for r in golden if r.get("abstain")]
print(f"Abstain rows: {len(abstain_rows)}")

# Run each abstain row and collect signals
results = []
for item in abstain_rows:
    ans, _ = pipeline.query(item["query"], top_k=5)
    rec = {
        "id": item.get("id", "?"),
        "query": item["query"][:80],
        "abstained": ans.abstained,
        "abstention_reason": ans.abstention_reason or "none",
    }
    if hasattr(ans, 'confidence') and ans.confidence:
        rec["subject_sim"] = ans.confidence.get("subject_sim")
        rec["section_sim"] = ans.confidence.get("section_sim")
        rec["rerank_top"] = ans.confidence.get("rerank_top")
    results.append(rec)

# Print signal distribution for abstain rows
print(f"\n=== Signal distribution (abstain=True rows) ===")
for r in sorted(results, key=lambda x: -x.get("rerank_top", 0)):
    subj = r.get('subject_sim')
    sect = r.get('section_sim')
    top = r.get('rerank_top')
    sv = f"{subj:.4f}" if subj is not None else 'N/A'
    sev = f"{sect:.4f}" if sect is not None else 'N/A'
    tv = f"{top:.4f}" if top is not None else 'N/A'
    print(f"  {r['id']:20s} reason={r['abstention_reason']:18s} subj={sv:>8s}  sect={sev:>8s}  top={tv:>8s}")

# Check false positives at each threshold
thresholds = [0.85, 0.80, 0.75]
print(f"\n=== False Positive Check ===")

for thresh in thresholds:
    fps = []
    for r in results:
        subj = r.get("subject_sim") or 0.0
        sect = r.get("section_sim") or 0.0
        top = r.get("rerank_top") or 0.0
        
        # Current gate: subject_sim >= 0.42 OR section_score >= 0.60
        current_pass = subj >= 0.42 or sect >= 0.60
        
        # Hybrid gate: current_pass OR rerank_top >= thresh
        hybrid_pass = current_pass or top >= thresh
        
        # A false positive: pipeline correctly abstains (abstained=True)
        # but hybrid gate would pass it
        if r["abstained"] and not current_pass and hybrid_pass:
            fps.append(r)
    
    print(f"\nThreshold {thresh}:")
    print(f"  False positives: {len(fps)}")
    for r in fps:
        print(f"    {r['id']:20s} subj={r.get('subject_sim') or 0:.4f} top={r.get('rerank_top') or 0:.4f}")
