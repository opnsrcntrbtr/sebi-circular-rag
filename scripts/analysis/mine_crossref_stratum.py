"""R3 §3.1 — mine cross-reference (A cites B) candidate pairs.

Spec: docs/superpowers/specs/2026-08-19-crossref-eval-validity-prereg.md §3.1.
Frozen criteria only. No LLM, no retrieval, no scoring — this is the mining
stage, and it is deterministic.

⚠️ Spec correction discovered at execution: §3.1 says "from the persisted lineage
graph ... relation class `cites`". Neither holds.
  1. The class is named `references` (lineage.detect_relations_ex), not `cites`.
  2. The PERSISTED graph contains NO such edges: build_lineage handles only the
     "supersedes" and "amends" branches and silently drops "references" (no else
     clause, lineage.py:174-184). data/index/lineage.json is 4536 supersedes +
     41 amends + 0 references.
So the pairs must be re-extracted from corpus text. The extractor is unchanged;
only the source of the edges differs from what §3.1 assumed.

⚠️ Known extractor coarseness, quantified in the output: detect_relations_ex
classifies EVERY reference in a document as "supersedes" whenever the document
contains any SUPERSEDE_RE match anywhere (lineage.py:47). Cross-references
living in such documents are therefore invisible to this mining pass. The
`suppressed_by_supersede_doc` counter reports how many that is.

Usage: PYTHONPATH=src python scripts/analysis/mine_crossref_stratum.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
DEST = ROOT / "reports" / "crossref-mining-2026-08-20.json"

MIN_CHUNKS = 3          # §3.1: B contributes >= 3 non-degenerate chunks
MIN_BODY = 80           # §3.1: "non-degenerate" = body >= 80 chars
MAX_PER_SOURCE = 3      # §3.1: at most 3 pairs per source circular A
TARGET = 600            # §3.1: mine to 600 candidates


def main() -> None:
    from sebi_rag.lineage import build_lineage, detect_relations_ex, load_records
    from sebi_rag.settings import Settings

    s = Settings.load()
    recs = load_records(s.corpus_path)
    by_cn = {r["circular_number"]: r for r in recs}
    print(f"corpus: {len(recs)} records", file=sys.stderr)

    lin = build_lineage(recs)
    superseded = set(lin.superseded_by)          # in_force == not superseded

    # non-degenerate chunk counts per circular, from the persisted index
    chunk_counts: Counter = Counter()
    idx = Path(s.index_dir) / "chunks.jsonl"
    with idx.open() as f:
        for line in f:
            c = json.loads(line)
            body = c["text"]
            # F1 enrichment prepends "circular_no | subject" as line 0; the body
            # is what follows, and that is what "degenerate" refers to.
            body = body.split("\n", 1)[1] if "\n" in body else ""
            if len(body.strip()) >= MIN_BODY:
                chunk_counts[c["meta"]["circular_number"]] += 1
    print(f"index: {sum(chunk_counts.values())} non-degenerate chunks over "
          f"{len(chunk_counts)} circulars", file=sys.stderr)

    golden_docs: set[str] = set()
    for l in GOLDEN.read_text().splitlines():
        if l.strip():
            golden_docs.update(json.loads(l).get("relevant_circulars") or [])

    stats = Counter()
    per_source: defaultdict[str, int] = defaultdict(int)
    pairs = []
    for r in recs:
        a = r["circular_number"]
        rels = detect_relations_ex(a, r.get("text", ""))
        # quantify the coarseness noted in the docstring
        if any(e["relation"] == "supersedes" for e in rels):
            stats["suppressed_by_supersede_doc"] += sum(
                1 for e in rels if e["relation"] == "supersedes")
        for e in rels:
            if e["relation"] != "references":
                continue
            stats["raw_reference_edges"] += 1
            b = e["target"]
            if b not in by_cn:
                stats["drop_b_not_in_corpus"] += 1
                continue
            if b in superseded:
                stats["drop_b_superseded"] += 1
                continue
            if chunk_counts[b] < MIN_CHUNKS:
                stats["drop_b_too_few_chunks"] += 1
                continue
            if a in golden_docs or b in golden_docs:
                stats["drop_in_golden_v7"] += 1
                continue
            if per_source[a] >= MAX_PER_SOURCE:
                stats["drop_source_cap"] += 1
                continue
            per_source[a] += 1
            stats["kept"] += 1
            pairs.append({"a": a, "b": b,
                          "a_subject": (by_cn[a].get("subject") or "")[:200],
                          "b_subject": (by_cn[b].get("subject") or "")[:200],
                          "b_chunks": chunk_counts[b],
                          "evidence": e["evidence"][:300]})

    out = {
        "spec": "docs/superpowers/specs/2026-08-19-crossref-eval-validity-prereg.md §3.1",
        "stage": "MINING ONLY — no query generation, no scoring, no metric",
        "spec_corrections": [
            "relation class is 'references', not 'cites'",
            "persisted lineage.json has 0 reference edges (build_lineage drops the "
            "branch, lineage.py:174-184); re-extracted from corpus text instead",
        ],
        "criteria": {"min_nondegenerate_chunks": MIN_CHUNKS, "min_body_chars": MIN_BODY,
                     "max_pairs_per_source": MAX_PER_SOURCE, "target_candidates": TARGET},
        "corpus_records": len(recs),
        "attrition": dict(stats),
        "candidates_mined": len(pairs),
        "distinct_sources": len(per_source),
        "distinct_targets": len({p["b"] for p in pairs}),
        "meets_target": len(pairs) >= TARGET,
        "pairs": pairs,
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "pairs"}, indent=2))


if __name__ == "__main__":
    main()
