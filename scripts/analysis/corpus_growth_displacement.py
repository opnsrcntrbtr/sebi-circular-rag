"""W1.3 diagnostic (2026-09-03 architecture review): does the 730->1,490 corpus
expansion (2026-08-28 bounded scrape) displace gold documents out of top-10 for
queries whose gold circulars are entirely pre-expansion?

Descriptive only - no significance test, no arm, no gate. Runs retrieval +
rerank directly against the live persisted index; does NOT invoke the
generator, so this is far cheaper than eval_json.py and safe to run alongside
it.

Pre-expansion set is derived from each corpus record's `provenance` field
(free-text "Parsed from PDF ... on YYYY-MM-DD"), not from an archived TREC
docids.tsv - those files were checked and found to be per-run *retrieved-doc*
subsets (313-886 distinct circulars each), not full corpus manifests, so none
of them reconstructs the true 730. Filtering `provenance` dates < 2026-08-28
does: 730 records, matching docs/status.md's own count exactly.

Usage:
    PYTHONPATH=src python scripts/analysis/corpus_growth_displacement.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

EXPANSION_CUTOFF = "2026-08-28"
GOLDEN_PATH = ROOT / "eval" / "golden" / "golden_v7.jsonl"
OUT_PATH = ROOT / "reports" / "corpus-growth-displacement-2026-09-03.json"


def _doc(chunk_id: str) -> str:
    return chunk_id.split("#", 1)[0]


def _chunk_id(c) -> str:
    return c["id"] if isinstance(c, dict) else c.id


def _unique(ids):
    seen, out = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def load_pre_expansion_ids(corpus_path: Path) -> set[str]:
    pre_ids = set()
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            prov = rec.get("provenance") or ""
            m = re.search(r"(\d{4}-\d{2}-\d{2})", prov)
            date = m.group(1) if m else None
            if date is not None and date < EXPANSION_CUTOFF:
                pre_ids.add(rec["circular_number"])
    return pre_ids


def main() -> None:
    from sebi_rag.eval_harness import load_golden
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.rerank import CrossEncoderReranker
    from sebi_rag.retrieve import HybridRetriever
    from sebi_rag.settings import Settings

    s = Settings.load()
    pre_ids = load_pre_expansion_ids(Path(s.corpus_path))
    print(f"pre-expansion corpus set: {len(pre_ids)} circulars "
          f"(expect ~730; docs/status.md's own count)", file=sys.stderr)

    rows = load_golden(GOLDEN_PATH)
    eligible = [
        r for r in rows
        if not r.get("abstain")
        and r.get("relevant_circulars")
        and all(c in pre_ids for c in r["relevant_circulars"])
    ]
    print(f"{len(eligible)}/{len(rows)} golden_v7 rows have gold circulars "
          f"entirely pre-expansion", file=sys.stderr)

    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(s.index_dir, emb)
    rer = CrossEncoderReranker(device="mps")

    per_row = []
    for item in eligible:
        fusion = retr.retrieve(item["query"], top_n=50)
        fusion_docs = _unique(_doc(c.id) for c, _ in fusion)[:10]
        fusion_post_expansion = sum(1 for d in fusion_docs if d not in pre_ids)

        reranked = rer.rerank(item["query"], [c for c, _ in fusion])
        context_docs = _unique(_doc(_chunk_id(c)) for c, _ in reranked)[:10]
        context_post_expansion = sum(1 for d in context_docs if d not in pre_ids)

        gold_hit_fusion = any(d in item["relevant_circulars"] for d in fusion_docs)
        gold_hit_context = any(d in item["relevant_circulars"] for d in context_docs)

        per_row.append({
            "id": item["id"],
            "fusion_top10_post_expansion": fusion_post_expansion,
            "context_top10_post_expansion": context_post_expansion,
            "gold_survives_fusion_top10": gold_hit_fusion,
            "gold_survives_context_top10": gold_hit_context,
        })

    n = len(per_row)
    mean = lambda xs: sum(xs) / len(xs) if xs else 0.0
    payload = {
        "derived_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "pre_expansion_corpus_n": len(pre_ids),
        "eligible_rows": n,
        "mean_fusion_top10_post_expansion_count": mean(
            [r["fusion_top10_post_expansion"] for r in per_row]),
        "mean_context_top10_post_expansion_count": mean(
            [r["context_top10_post_expansion"] for r in per_row]),
        "gold_survival_rate_fusion": mean(
            [1.0 if r["gold_survives_fusion_top10"] else 0.0 for r in per_row]),
        "gold_survival_rate_context": mean(
            [1.0 if r["gold_survives_context_top10"] else 0.0 for r in per_row]),
        "per_row": per_row,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT_PATH}", file=sys.stderr)
    print(json.dumps({k: v for k, v in payload.items() if k != "per_row"}, indent=2))


if __name__ == "__main__":
    main()
