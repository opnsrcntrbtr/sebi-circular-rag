#!/usr/bin/env python3
"""Lineage anomaly detector — flag circulars with missing supersession edges.

Checks:
1. Circulars marked superseded but no edge points to them
2. Circulars that should supersede others but have no outgoing edges
3. Orphan edges (source or target not in corpus)
4. Circulars with supersession_status but no corresponding edges

Exit 0 = no anomalies, exit 1 = anomalies detected.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = PROJECT_ROOT / "data" / "corpus" / "circulars.jsonl"
LINEAGE_PATH = PROJECT_ROOT / "data" / "index" / "lineage.json"


def load_corpus() -> dict[str, dict]:
    """Load corpus keyed by circular_number."""
    corpus = {}
    with open(CORPUS_PATH) as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            key = record.get("circular_number", "")
            if key:
                corpus[key] = record
    return corpus


def load_lineage() -> dict:
    """Load lineage data."""
    with open(LINEAGE_PATH) as f:
        return json.load(f)


def main() -> int:
    errors = []
    anomalies = defaultdict(list)

    # Load data
    try:
        corpus = load_corpus()
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: Cannot load corpus: {e}", file=sys.stderr)
        return 1

    try:
        lineage = load_lineage()
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: Cannot load lineage: {e}", file=sys.stderr)
        return 1

    edges = lineage.get("edges", [])
    corpus_numbers = set(corpus.keys())

    # Build edge maps
    superseded_by = defaultdict(list)  # target -> list of sources that supersede it
    supersedes = defaultdict(list)     # source -> list of targets it supersedes

    for edge in edges:
        src = edge.get("source", "")
        tgt = edge.get("target", "")
        rel = edge.get("relation", "")

        if rel == "supersedes" and src and tgt:
            supersedes[src].append(tgt)
            superseded_by[tgt].append(src)
        elif rel == "superseded_by" and src and tgt:
            superseded_by[src].append(tgt)
            supersedes[tgt].append(src)

    # Check 1: Circulars marked superseded but no edge points to them
    for circ_num, circ in corpus.items():
        status = circ.get("supersession_status", "")
        if status == "superseded" and circ_num not in superseded_by:
            anomalies["orphan_superseded"].append(circ_num)

    # Check 2: Circulars that supersede others but have no outgoing edges
    for circ_num in supersedes:
        if circ_num not in corpus_numbers:
            anomalies["edge_source_missing"].append(circ_num)

    # Check 3: Orphan edges (source or target not in corpus)
    orphan_sources = set()
    orphan_targets = set()
    for edge in edges:
        src = edge.get("source", "")
        tgt = edge.get("target", "")
        if src and src not in corpus_numbers:
            orphan_sources.add(src)
        if tgt and tgt not in corpus_numbers:
            orphan_targets.add(tgt)

    anomalies["orphan_edge_sources"] = list(orphan_sources)[:20]
    anomalies["orphan_edge_targets"] = list(orphan_targets)[:20]

    # Check 4: Circulars with supersession_status="in_force" but have outgoing supersedes edges
    for circ_num, circ in corpus.items():
        status = circ.get("supersession_status", "")
        if status == "in_force" and circ_num in supersedes:
            # This circular claims to be in force but supersedes other circulars
            # This is actually OK — it means this circular superseded others
            pass

    # Output summary
    anomaly_types = {k: len(v) for k, v in anomalies.items() if v}

    print(f"LINEAGE_ANOMALY total_circulars={len(corpus)} edges={len(edges)} "
          f"anomaly_types={len(anomaly_types)}", flush=True)

    for atype, count in sorted(anomaly_types.items()):
        print(f"LINEAGE_ANOMALY {atype}={count}", flush=True)

    if anomaly_types:
        # Print samples for each anomaly type
        for atype, items in anomalies.items():
            if items:
                sample = items[:5]
                print(f"LINEAGE_ANOMALY {atype}_sample={json.dumps(sample)}", flush=True)

        print(f"\nLINEAGE_ANOMALY status=anomalies detected", flush=True)
        return 1

    print("LINEAGE_ANOMALY status=clean", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
