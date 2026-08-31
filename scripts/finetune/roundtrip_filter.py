"""Phase 1 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-
bright-dawn.md): Promptagator round-trip consistency filter
(arXiv:2209.11755) for LLM-synthesized queries.

A synthesized query is kept only if retrieving with it against the FROZEN
BASE index (data/index, the pre-fine-tune bge-m3 - this must run before
training, on the same corpus snapshot every other phase pins) returns the
query's own source document in the top-k. Reported at +2.5 nDCG average,
improving 8/11 BEIR datasets. Zero LLM cost - this is why Phase 1 specs no
second annotator leg for quality control.

Two filters, applied in this order (cheap first):

1. Boilerplate positives. Post-hoc cleanup for a real defect found via
   spot-check on the completed real run: multi_hop/lineage_supersession
   candidate selection (before a later fix, see synthesize_queries.py's
   git history) could pick a target chunk that trails into a signature
   block or "available on the SEBI website" closing line. Reuses
   synthesize_queries._has_boilerplate rather than re-running the LLM for
   the ~313/6263 affected rows - cheaper, and this filter is about to run
   anyway.

2. Round-trip retrieval consistency (the actual Promptagator filter).

positive_doc resolution: rows from a run predating the positive_doc field
(the real Phase 1 run's raw output does) don't carry it, and source_id
(which would let it be recovered by parsing) isn't persisted in the output
row either - only used internally for caching during synthesis. Resolved
here via a reverse lookup (chunk text -> doc_id) built from the corpus
itself, which works uniformly regardless of when a row was generated,
rather than trusting a per-row id that may not exist.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/finetune/roundtrip_filter.py
Output:
    data/finetune/pairs_synth.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from finetune.mine_structural_pairs import (  # noqa: E402
    _strip_context_header,
    load_chunks_by_doc,
)
from finetune.synthesize_queries import _has_boilerplate  # noqa: E402

DEFAULT_RAW = ROOT / "data" / "finetune" / "pairs_synth_raw.jsonl"
DEFAULT_CHUNKS = ROOT / "data" / "index" / "chunks.jsonl"
DEFAULT_INDEX_DIR = ROOT / "data" / "index"  # FROZEN base index - never the
                                             # fine-tuned one; this must run
                                             # before training
DEFAULT_OUT = ROOT / "data" / "finetune" / "pairs_synth.jsonl"
DEFAULT_TOP_K = 10  # matches recall@10, the project's primary retrieval metric


def load_rows(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
           if l.strip()]


def filter_boilerplate(rows: list[dict]) -> tuple[list[dict], int]:
    """Returns (kept, n_dropped)."""
    kept = [r for r in rows if not _has_boilerplate(r["positive"])]
    return kept, len(rows) - len(kept)


def build_text_to_doc_map(chunks_by_doc: dict[str, list[dict]]) -> dict[str, str]:
    """Reverse lookup for rows predating the positive_doc field. Header-
    stripped to match how `positive` values were built during synthesis -
    an unstripped lookup would silently never match anything."""
    out: dict[str, str] = {}
    for doc_id, chunks in chunks_by_doc.items():
        for c in chunks:
            body = _strip_context_header(c["text"], doc_id)
            out[body] = doc_id
    return out


def resolve_positive_doc(row: dict, text_to_doc: dict[str, str]) -> str | None:
    """Prefer the row's own positive_doc field (future runs); fall back to
    the reverse text lookup for rows generated before that field existed.
    Returns None if neither resolves - caller must drop such a row rather
    than guess."""
    if row.get("positive_doc"):
        return row["positive_doc"]
    return text_to_doc.get(row["positive"])


def roundtrip_check(rows: list[dict], retriever, text_to_doc: dict[str, str],
                    top_k: int = DEFAULT_TOP_K) -> tuple[list[dict], dict]:
    """Retrieves with each row's query against `retriever` (the frozen base
    index) and keeps the row only if its resolved positive_doc appears
    among the top-k retrieved documents' ids. One retrieve() call per row
    (not batched like mine_hard_negatives) - .retrieve() exercises the
    SAME hybrid dense+sparse+RRF path production actually uses, which is
    the faithful thing to validate a synthetic query against, and at
    ~6.3k rows the per-call cost (embed + FAISS + BM25, all local, no LLM)
    is small enough that batching isn't worth the added complexity here."""
    kept = []
    n_no_doc_resolved = n_failed_roundtrip = 0
    for r in rows:
        positive_doc = resolve_positive_doc(r, text_to_doc)
        if positive_doc is None:
            n_no_doc_resolved += 1
            continue
        retrieved = retriever.retrieve(r["query"], top_n=top_k)
        retrieved_docs = {c.doc_id for c, _ in retrieved}
        if positive_doc in retrieved_docs:
            kept.append({**r, "positive_doc": positive_doc})
        else:
            n_failed_roundtrip += 1
    stats = {"n_no_doc_resolved": n_no_doc_resolved,
             "n_failed_roundtrip": n_failed_roundtrip, "n_kept": len(kept)}
    return kept, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(DEFAULT_RAW))
    ap.add_argument("--chunks", default=str(DEFAULT_CHUNKS))
    ap.add_argument("--index-dir", default=str(DEFAULT_INDEX_DIR),
                    help="FROZEN base index - must predate any fine-tuning")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    args = ap.parse_args()

    rows = load_rows(Path(args.raw))
    print(f"raw rows: {len(rows)}")

    rows, n_boilerplate = filter_boilerplate(rows)
    print(f"after boilerplate filter: {len(rows)} (dropped {n_boilerplate})")

    chunks_by_doc = load_chunks_by_doc(Path(args.chunks))
    text_to_doc = build_text_to_doc_map(chunks_by_doc)

    from sebi_rag.api import _embed_kwargs
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.retrieve import HybridRetriever
    from sebi_rag.settings import Settings

    embedder = BGEM3Embedder(**_embed_kwargs(Settings.load()))
    retriever = HybridRetriever.load(args.index_dir, embedder)

    kept, stats = roundtrip_check(rows, retriever, text_to_doc, args.top_k)
    print(f"round-trip filter: {stats}")

    if len(kept) == len(rows) - n_boilerplate:
        print("WARNING: round-trip filter retained ~100% of rows - a filter "
             "retaining everything is not filtering (plan verification step 5)")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"kept: {len(kept)} -> {out_path}")


if __name__ == "__main__":
    main()
