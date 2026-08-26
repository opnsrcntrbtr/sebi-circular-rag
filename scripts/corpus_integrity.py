#!/usr/bin/env python3
"""Corpus integrity checker — verify chunks.jsonl matches corpus JSONL.

Checks:
1. Every chunk's doc_id exists in corpus
2. Every corpus circular with index_date has corresponding chunks
3. No orphan chunks (doc_id not in corpus)
4. CircularMeta field count stable (no unexpected fields)

Exit 0 = all checks pass, exit 1 = any check fails.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = PROJECT_ROOT / "data" / "corpus" / "circulars.jsonl"
CHUNKS_PATH = PROJECT_ROOT / "data" / "index" / "chunks.jsonl"


def load_corpus() -> dict[str, dict]:
    """Load corpus into a dict keyed by circular_number."""
    corpus = {}
    with open(CORPUS_PATH) as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            key = record.get("circular_number", record.get("doc_id", ""))
            corpus[key] = record
    return corpus


def load_chunks() -> tuple[list[dict], set[str]]:
    """Load chunks and return (records, doc_ids)."""
    chunks = []
    doc_ids = set()
    with open(CHUNKS_PATH) as f:
        for line in f:
            if not line.strip():
                continue
            chunk = json.loads(line)
            doc_id = chunk.get("doc_id", "")
            chunks.append(chunk)
            if doc_id:
                doc_ids.add(doc_id)
    return chunks, doc_ids


def check_meta_fields(chunk: dict) -> list[str]:
    """Check that chunk meta has expected CircularMeta fields."""
    meta = chunk.get("meta", {})
    expected_fields = {
        "circular_number", "issue_date", "effective_date", "subject",
        "issuing_department", "supersession_status", "amendment_history",
        "version_lineage", "circular_type", "validity_status",
        "superseded_by_id",
    }
    extra = set(meta.keys()) - expected_fields
    if extra:
        return [f"Unexpected meta fields in {chunk.get('id', '?')}: {sorted(extra)}"]
    return []


def main() -> int:
    errors = []

    # Load data
    try:
        corpus = load_corpus()
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: Cannot load corpus: {e}", file=sys.stderr)
        return 1

    try:
        chunks, chunk_doc_ids = load_chunks()
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: Cannot load chunks: {e}", file=sys.stderr)
        return 1

    # Check 1: Every chunk's doc_id exists in corpus
    orphan_chunks = []
    for chunk in chunks:
        doc_id = chunk.get("doc_id", "")
        if doc_id and doc_id not in corpus:
            orphan_chunks.append(doc_id)

    if orphan_chunks:
        errors.append(
            f"FAIL: {len(orphan_chunks)} orphan chunks with doc_id not in corpus "
            f"(sample: {orphan_chunks[:5]})"
        )

    # Check 2: CircularMeta field stability
    meta_errors = []
    for chunk in chunks[:100]:  # Sample first 100 chunks
        meta_errors.extend(check_meta_fields(chunk))

    if meta_errors:
        errors.append(f"FAIL: Meta field issues (sample): {meta_errors[:3]}")

    # Check 3: Corpus circulars that should have chunks
    corpus_with_index = [
        c for c in corpus.values()
        if c.get("index_date") and not c.get("is_master")
    ]
    corpus_with_chunks = set(
        c["circular_number"] for c in corpus_with_index
        if c.get("circular_number") in chunk_doc_ids
    )
    missing_chunks = set(c["circular_number"] for c in corpus_with_index) - corpus_with_chunks

    if missing_chunks:
        errors.append(
            f"WARNING: {len(missing_chunks)} corpus circulars have index_date but no chunks "
            f"(sample: {sorted(missing_chunks)[:5]})"
        )

    # Summary output
    print(f"CORPUS_INTEGRITY corpus_count={len(corpus)} chunks_count={len(chunks)} "
          f"unique_docs={len(chunk_doc_ids)} orphan_chunks={len(orphan_chunks)} "
          f"meta_errors={len(meta_errors)} missing_chunks={len(missing_chunks)}", flush=True)

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    print("CORPUS_INTEGRITY status=PASS", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
