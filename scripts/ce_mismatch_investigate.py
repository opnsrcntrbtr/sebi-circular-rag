"""CE_MISMATCH false-abstention investigation (score-floor-diagnostic 2026-08-18).

For the 4 rows classified CE_MISMATCH (relevant doc in fusion pool, top CE
score < 0.42 gate), dump the reranked pool with CE scores + chunk text so we
can see WHY the cross-encoder scores the relevant chunk low:

- Is the relevant chunk a header/metadata chunk (no content)?
- Does the relevant chunk contain the query's key terms (lexical overlap)?
- What does the CE actually score high (the top pool chunks)?

Read-only. Reuses score_floor_diagnostic.py's exact load path.

Usage: PYTHONPATH=src python scripts/ce_mismatch_investigate.py
"""
from __future__ import annotations

import json
import os
import sys
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

from sebi_rag.embeddings import BGEM3Embedder
from sebi_rag.eval_harness import load_golden
from sebi_rag.rerank import CrossEncoderReranker
from sebi_rag.retrieve import HybridRetriever
from sebi_rag.settings import Settings

CE_MISMATCH_IDS = [
    "para-mfmaster",
    "para-glitch",
    "para-mfborrow",
    "para-pricedata",
]
GATE = 0.42
TOP_N_DUMP = 8


def main() -> None:
    s = Settings.load()
    print(f"loading index from {s.index_dir} ...", file=sys.stderr)
    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(s.index_dir, emb)
    reranker = CrossEncoderReranker(device="mps")
    golden = load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")
    rows = {r["id"]: r for r in golden}

    out = []
    for rid in CE_MISMATCH_IDS:
        r = rows[rid]
        q = r["query"]
        docs = set(r.get("relevant_circulars") or [])

        fused = retr.retrieve(q, top_n=50)
        pool = [c for c, _ in fused]
        reranked = reranker.rerank(q, pool)

        # locate the relevant chunk(s) in the pool
        rel_in_pool = [
            (i + 1, c, sc) for i, (c, sc) in enumerate(reranked) if c.doc_id in docs
        ]

        entry = {
            "id": rid,
            "query": q,
            "relevant": sorted(docs),
            "gate": GATE,
            "ce_top": round(reranked[0][1], 4) if reranked else None,
            "relevant_in_pool": [
                {"ce_rank": rk, "ce_score": round(sc, 4), "chunk_id": c.id,
                 "section": c.section, "text": c.text}
                for rk, c, sc in rel_in_pool
            ],
            "top_pool": [
                {"ce_rank": i + 1, "ce_score": round(sc, 4), "chunk_id": c.id,
                 "doc_id": c.doc_id, "section": c.section,
                 "is_relevant": c.doc_id in docs, "text": c.text}
                for i, (c, sc) in enumerate(reranked[:TOP_N_DUMP])
            ],
        }
        out.append(entry)

        # human-readable dump
        print(f"\n{'=' * 78}\n### {rid}\nQ: {q}\nrelevant: {sorted(docs)}")
        print(f"ce_top={entry['ce_top']}  gate={GATE}")
        print(f"--- relevant chunk(s) in pool ({len(rel_in_pool)}) ---")
        for rk, c, sc in rel_in_pool:
            print(f"  [CE rank {rk}, score {sc:.4f}] {c.id}")
            print(f"    section: {c.section}")
            print(f"    text: {c.text[:600]}")
        print(f"--- top {TOP_N_DUMP} pool chunks ---")
        for t in entry["top_pool"]:
            tag = "RELEVANT" if t["is_relevant"] else "         "
            print(f"  [{t['ce_rank']:>2}] {t['ce_score']:.4f} {tag} {t['doc_id']} :: {t['section']}")
            print(f"       {t['text'][:300]}")

    dest = ROOT / "reports" / "ce-mismatch-investigate-2026-08-18.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {dest}", file=sys.stderr)


if __name__ == "__main__":
    main()
