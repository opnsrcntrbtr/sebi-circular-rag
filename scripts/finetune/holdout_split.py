"""Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-
bright-dawn.md): the contamination boundary every later mining script must
respect.

golden_v7 (n=260) is the ONLY eval set this intervention has, and it points
at 159 distinct gold circulars - 21.8% of the corpus. Mining training pairs
from those documents would let the fine-tuned embedder see (a paraphrase of)
its own eval answers during training, so a retrieval win could just be
memorization, not generalization.

Per the locked decision (document-level exclusion of a held-out SLICE, not
the whole 159): ~30% of the 159 gold circulars are held out entirely - zero
training pairs are ever mined from them - while the rest stay minable. This
gives two readings from one run instead of an all-or-nothing choice:
  - held_out rows: golden rows whose ENTIRE gold set is in the holdout slice
    -> a clean generalization signal, ~78 rows
  - in_corpus rows: golden rows with NO gold doc in the holdout slice
    -> weaker generalization claim (docs were minable), ~182 rows
  - mixed rows: multi-doc rows (multi_hop, lineage_supersession) straddling
    both - reported separately, pooled into neither headline number

Usage:
    PYTHONPATH=src .venv/bin/python scripts/finetune/holdout_split.py
Output:
    data/finetune/holdout_docs.json
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.eval_harness import load_golden  # noqa: E402

DEFAULT_GOLDEN_PATH = ROOT / "eval" / "golden" / "golden_v7.jsonl"
DEFAULT_OUT_PATH = ROOT / "data" / "finetune" / "holdout_docs.json"
HOLDOUT_FRACTION = 0.30
SEED = 42  # matches export_datasets.py's build_supersession_pairs seed


def gold_circulars(golden: list[dict]) -> list[str]:
    """Every distinct circular any golden_v7 row cites as relevant, sorted
    for determinism (set/dict iteration order must never leak into the
    split - two runs on the same golden file must pick the same slice)."""
    ids: set[str] = set()
    for row in golden:
        ids.update(row.get("relevant_circulars") or [])
    return sorted(ids)


def split_holdout(circulars: list[str], fraction: float = HOLDOUT_FRACTION,
                  seed: int = SEED) -> tuple[list[str], list[str]]:
    """Deterministic seeded sample. round(), not int(), so 159*0.30=47.7
    lands on 48 rather than silently truncating to 47."""
    rng = random.Random(seed)
    shuffled = circulars[:]
    rng.shuffle(shuffled)
    n_holdout = round(len(circulars) * fraction)
    holdout = sorted(shuffled[:n_holdout])
    minable = sorted(shuffled[n_holdout:])
    return holdout, minable


def classify_rows(golden: list[dict], holdout: set[str]) -> dict[str, list[str]]:
    """Partition golden_v7 row ids into held_out / in_corpus / mixed by
    whether their relevant_circulars fall entirely inside, entirely
    outside, or straddle the holdout set. Rows with no relevant_circulars
    (pure abstention rows) are excluded from all three - they have no gold
    document to be contaminated by or generalize to."""
    held_out, in_corpus, mixed = [], [], []
    for row in golden:
        rel = row.get("relevant_circulars") or []
        if not rel:
            continue
        in_holdout = [c for c in rel if c in holdout]
        if len(in_holdout) == len(rel):
            held_out.append(row["id"])
        elif not in_holdout:
            in_corpus.append(row["id"])
        else:
            mixed.append(row["id"])
    return {"held_out": sorted(held_out), "in_corpus": sorted(in_corpus),
            "mixed": sorted(mixed)}


def build(golden_path: Path, fraction: float, seed: int) -> dict:
    golden = load_golden(golden_path)
    circulars = gold_circulars(golden)
    holdout, minable = split_holdout(circulars, fraction, seed)
    rows = classify_rows(golden, set(holdout))
    return {
        "golden_path": str(golden_path),
        "seed": seed,
        "fraction": fraction,
        "gold_circulars_total": len(circulars),
        "holdout_docs": holdout,
        "minable_gold_docs": minable,
        "row_split": rows,
        "row_split_counts": {k: len(v) for k, v in rows.items()},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default=str(DEFAULT_GOLDEN_PATH))
    ap.add_argument("--out", default=str(DEFAULT_OUT_PATH))
    ap.add_argument("--fraction", type=float, default=HOLDOUT_FRACTION)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    result = build(Path(args.golden), args.fraction, args.seed)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"gold circulars: {result['gold_circulars_total']}")
    print(f"holdout: {len(result['holdout_docs'])}  "
          f"minable: {len(result['minable_gold_docs'])}")
    print(f"row split: {result['row_split_counts']}")
    print(f"-> {out_path}")


if __name__ == "__main__":
    main()
