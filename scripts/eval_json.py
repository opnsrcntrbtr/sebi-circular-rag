"""Emit one JSON line of retrieval/citation/abstention metrics over golden_v5
(env SEBI_RAG_GOLDEN to override) using the persisted index (no LLM, no Ollama).
Abstention mirrors PRODUCTION: score floor (settings.abstain_threshold) + the
subject-sim gate (generate.SubjectSimJudge), same defaults as api.py. Also
reports injection_flagged (F4: corpus records with non-empty injection_flags).
Model/progress noise goes to stderr; the single JSON object is the only stdout
line, for n8n to parse.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag import eval as M  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.eval_harness import _doc, _unique, load_golden  # noqa: E402
from sebi_rag.lineage import build_lineage, demote_superseded, load_records  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.settings import Settings  # noqa: E402

from sebi_rag.generate import SubjectSimJudge  # noqa: E402
from sebi_rag.ingest_pdf import injection_scan  # noqa: E402

s = Settings.load()
recs = load_records(s.corpus_path)
lin = build_lineage(recs)
emb = BGEM3Embedder(device="mps")
retr = HybridRetriever.load(s.index_dir, emb)
rer = CrossEncoderReranker(device="mps")
_sect = os.environ.get("SEBI_RAG_SECT_THRESHOLD", "0.60")
gate = SubjectSimJudge(
    emb, threshold=float(os.environ.get("SEBI_RAG_SUBJ_THRESHOLD", "0.42")),
    section_threshold=(None if _sect.lower() in ("off", "0") else float(_sect)))
golden = load_golden(os.environ.get(
    "SEBI_RAG_GOLDEN", str(ROOT / "eval" / "golden" / "golden_v5.jsonl")))

recall, cprec, crec, abst = [], [], [], []
for item in golden:
    relevant = set(item.get("relevant_circulars", []))
    cands = retr.retrieve(item["query"], top_n=50)
    rk = demote_superseded(rer.rerank(item["query"], [c for c, _ in cands]), lin)
    retrieved_docs = _unique(_doc(c.id) for c, _ in cands)
    contexts = [c for c, _ in rk[:s.top_k]]
    abstained = ((not rk) or rk[0][1] < s.abstain_threshold
                 or not gate.grounded(item["query"], contexts))  # production gate
    if item.get("abstain"):
        abst.append(abstained)
        continue
    abst.append(not abstained)
    recall.append(M.recall_at_k(retrieved_docs, relevant, 10))
    cited = [] if abstained else _unique(_doc(c.id) for c, _ in rk[:s.top_k])
    hit = len(set(cited) & relevant)
    cprec.append(hit / len(cited) if cited else 0.0)
    crec.append(hit / len(relevant) if relevant else 0.0)

mean = lambda xs: round(sum(xs) / len(xs), 3) if xs else 0.0
print(json.dumps({
    "ts": dt.datetime.now().isoformat(timespec="seconds"),
    "circulars": len({r["circular_number"] for r in recs}),
    "chunks": len(retr.chunks),
    "golden_items": len(golden),
    "top_k": s.top_k,
    "recall_at_10": mean(recall),
    "citation_precision": mean(cprec),
    "citation_recall": mean(crec),
    "abstention_accuracy": mean(abst),
    # live scan (older records predate the stored injection_flags field);
    # known-benign baseline = 1 (broker master's password-policy text)
    "injection_flagged": sum(1 for r in recs if injection_scan(r.get("text", ""))),
}))
