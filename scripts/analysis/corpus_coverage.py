"""Is the eval set measuring retrieval, or measuring its own construction?

Read-only. No model, no index build. Reproduces every figure in
docs/corpus-coverage-2026-08-20.md.

Motivation: R3 (2026-08-20) went void because 374 of 507 cross-references point at
circulars outside the 730-record corpus. That raised a larger question — golden_v7's
gold documents are corpus members by construction, so an eval built from the corpus
can only ask questions the corpus can answer.

⚠️ Master circulars dominate raw reference counts (they rescind long schedules), so
every figure here is reported BOTH raw and non-master. The non-master cut is the
honest one; the raw counts overstate the substantive gap by roughly 10x.

Usage: PYTHONPATH=src python scripts/analysis/corpus_coverage.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
DEST = ROOT / "reports" / "corpus-coverage-2026-08-20.json"


def is_master(rec: dict) -> bool:
    return "master" in (rec.get("subject") or "").lower()


def main() -> None:
    from sebi_rag.lineage import REF_RE, load_records
    from sebi_rag.settings import Settings

    recs = load_records(Settings.load().corpus_path)
    by = {r["circular_number"]: r for r in recs}
    held = set(by)

    refs, m_mentions, o_mentions, m_missing, o_missing = Counter(), 0, 0, 0, 0
    o_targets, all_targets = set(), set()
    for r in recs:
        cn = r["circular_number"]
        master = is_master(r)
        for mt in REF_RE.finditer(r.get("text", "")):
            t = mt.group(0)
            if t == cn:
                continue
            refs[t] += 1
            all_targets.add(t)
            if master:
                m_mentions += 1
                m_missing += t not in held
            else:
                o_mentions += 1
                o_missing += t not in held
                if t not in held:
                    o_targets.add(t)

    golden = [json.loads(l) for l in GOLDEN.read_text().splitlines() if l.strip()]
    gold_docs: set[str] = set()
    for g in golden:
        gold_docs.update(g.get("relevant_circulars") or [])
    gold_in = gold_docs & held
    ordinary_gold = {g for g in gold_in if not is_master(by[g])}

    dangling = {}
    for g in ordinary_gold:
        outs = {m.group(0) for m in REF_RE.finditer(by[g].get("text", ""))} - {g} - held
        if outs:
            dangling[g] = sorted(outs)
    rows_aff = [g for g in golden
                if set(g.get("relevant_circulars") or []) & set(dangling)]

    pre2022 = sum(1 for r in recs if (r.get("issue_date") or "") < "2022-01-01")
    out = {
        "note": "read-only; measures eval-set construction, not system quality. "
                "Exposure, NOT demonstrated harm — see the memo's 'what this does not show'.",
        "corpus": {
            "circulars": len(recs),
            "issued_before_2022": pre2022,
            "pct_before_2022": round(100 * pre2022 / len(recs), 1),
        },
        "references_raw": {
            "distinct_referenced": len(all_targets),
            "held": len(all_targets & held),
            "absent": len(all_targets - held),
            "pct_absent": round(100 * len(all_targets - held) / len(all_targets), 1),
            "total_mentions": sum(refs.values()),
        },
        "by_document_class": {
            "master": {"mentions": m_mentions, "unresolvable": m_missing,
                       "pct": round(100 * m_missing / max(m_mentions, 1), 1)},
            "ordinary": {"mentions": o_mentions, "unresolvable": o_missing,
                         "pct": round(100 * o_missing / max(o_mentions, 1), 1),
                         "distinct_missing_targets": len(o_targets)},
            "caveat": "master circulars rescind long schedules; their citations are "
                      "bookkeeping, not substantive cross-reference. The ordinary row "
                      "is the one that matters.",
        },
        "eval_conditioning": {
            "gold_circulars": len(gold_docs),
            "gold_in_corpus": len(gold_in),
            "pct_in_corpus": round(100 * len(gold_in) / len(gold_docs), 1),
            "implication": "gold documents are corpus members by construction, so the "
                           "eval can only ask questions the corpus can answer",
        },
        "in_eval_exposure_non_master": {
            "ordinary_gold_docs": len(ordinary_gold),
            "with_dangling_citation": len(dangling),
            "pct": round(100 * len(dangling) / max(len(ordinary_gold), 1), 1),
            "distinct_unresolvable_targets": len({t for v in dangling.values() for t in v}),
            "golden_rows_resting_on_one": len(rows_aff),
            "pct_of_260": round(100 * len(rows_aff) / len(golden), 1),
            "by_stratum": dict(Counter(g.get("task_type") for g in rows_aff)),
        },
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
