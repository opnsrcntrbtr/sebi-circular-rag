"""ADR-002 follow-up: compare the production subject-sim gate against the
SECTION-AWARE variant (max over subject line + section heading) on golden_v5,
in one pass. Motivation: live false abstention on "What is a regulated
entity?" — rerank 0.997 but subject_sim 0.36 (definition section inside the
brokers master circular; doc-level subject can't see section-level evidence).
Risk to measure: hard negatives regressing via near-domain section headings.

Also probes the live failing query itself (not part of the metrics).

Run:  HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
      PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src .venv/bin/python scripts/eval_gate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.generate import SubjectSimJudge  # noqa: E402
from sebi_rag.lineage import build_lineage, demote_superseded, load_records  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402

INDEX = ROOT / "data" / "index"
CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
TOP_K = 3
SCORE_FLOOR = 0.05
THR = 0.42
PROBE = "What is a regulated entity?"

golden = load_golden(ROOT / "eval" / "golden" / "golden_v5.jsonl")
lineage = build_lineage(load_records(CORPUS))
emb = BGEM3Embedder(device="mps")
retr = HybridRetriever.load(INDEX, emb)
rer = CrossEncoderReranker(device="mps")
g_subj = SubjectSimJudge(emb, threshold=THR, section_threshold=None)
g_sect = SubjectSimJudge(emb, threshold=THR, section_threshold=None)  # scores below
print(f"golden={len(golden)}  chunks={len(retr.chunks)}  thr={THR}", flush=True)


def contexts_for(q: str):
    cands = retr.retrieve(q, top_n=50)
    rk = demote_superseded(rer.rerank(q, [c for c, _ in cands]), lineage)
    return rk[0][1] if rk else 0.0, [c for c, _ in rk[:TOP_K]]


cache = []
for item in golden:
    top, ctx = contexts_for(item["query"])
    s_subj = g_subj.score(item["query"], ctx)
    s_sect_only = g_sect.section_score(item["query"], ctx)
    cache.append((item, top, s_subj, max(s_subj, s_sect_only), s_sect_only))
print("scoring done", flush=True)


def auroc(pos, neg):
    if not pos or not neg:
        return float("nan")
    w = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return w / (len(pos) * len(neg))


for name, idx in (("subject-only (prod)", 2), ("subject+section", 3)):
    pos = [r[idx] for r in cache if not r[0].get("abstain")]
    neg = [r[idx] for r in cache if r[0].get("abstain")]
    correct = fa = hn = 0
    for item, top, *scores in cache:
        s = scores[idx - 2]
        answer = top >= SCORE_FLOOR and s >= THR
        if item.get("abstain"):
            correct += not answer
            hn += (not answer) and item["id"].startswith("hn-")
        else:
            correct += answer
            fa += (not answer) and top >= SCORE_FLOOR
    print(f"\n== {name} ==  AUROC={auroc(pos, neg):.3f}  "
          f"abst_acc={correct / len(cache):.3f}  gate_false_abst={fa}  "
          f"hn_caught={hn}/10", flush=True)
    print(f"   answerable min/med={min(pos):.3f}/{sorted(pos)[len(pos)//2]:.3f}  "
          f"abstain med/max={sorted(neg)[len(neg)//2]:.3f}/{max(neg):.3f}", flush=True)

# two-tier (production default): subj >= THR OR section-only >= SECT_THR
SECT_THR = 0.60
correct = fa = hn = 0
for item, top, s_subj, _s_max, s_sect in cache:
    answer = top >= SCORE_FLOOR and (s_subj >= THR or s_sect >= SECT_THR)
    if item.get("abstain"):
        correct += not answer
        hn += (not answer) and item["id"].startswith("hn-")
    else:
        correct += answer
        fa += (not answer) and top >= SCORE_FLOOR
print(f"\n== two-tier (subj>={THR} OR sect>={SECT_THR}) ==  "
      f"abst_acc={correct / len(cache):.3f}  gate_false_abst={fa}  "
      f"hn_caught={hn}/10", flush=True)

print("\n--- per-item (subj | max | section-only) ---", flush=True)
for item, top, s1, s2, s3 in cache:
    kind = "abstain" if item.get("abstain") else "answer "
    mark = " <-- sect-tier" if (s1 < THR and s3 >= SECT_THR) else ""
    print(f"{item['id']:<15} {kind} top={top:.3f} subj={s1:.3f} "
          f"max={s2:.3f} sect={s3:.3f}{mark}", flush=True)

top, ctx = contexts_for(PROBE)
ps, px = g_subj.score(PROBE, ctx), g_sect.section_score(PROBE, ctx)
print(f"\n--- live probe: {PROBE!r} ---", flush=True)
print(f"rerank_top={top:.3f}  subj={ps:.3f}  section-only={px:.3f}  "
      f"two-tier answers: {ps >= THR or px >= SECT_THR}", flush=True)
