"""Agreement, promotion, and arbitration for the golden-v7 external
annotation slice (spec 2026-07-23 sec 7). Consumes votes.jsonl (claude +
gemini + human), computes Cohen's kappa per annotator-pair per stratum,
applies the promotion rules, and writes the updated golden_v7.jsonl, the
arbitration queue, and a markdown agreement report.

Real run (writes golden_v7.jsonl + arbitration_queue.jsonl + the report):
    make golden-v7-agree
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.benchmark import write_jsonl  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.stats import clopper_pearson_ci  # noqa: E402

DEFAULT_GOLDEN_PATH = ROOT / "eval" / "golden" / "golden_v7.jsonl"
DEFAULT_VOTES_PATH = ROOT / "eval" / "golden" / "v7_annotations" / "votes.jsonl"
DEFAULT_POOLS_PATH = ROOT / "eval" / "golden" / "v7_annotations" / "pools.jsonl"
DEFAULT_SAMPLE_PATH = ROOT / "eval" / "golden" / "v7_annotations" / "external_sample.json"
DEFAULT_QUEUE_PATH = ROOT / "eval" / "golden" / "v7_annotations" / "arbitration_queue.jsonl"
DEFAULT_REPORT_PATH = ROOT / "reports" / "golden_v7_agreement.md"

_QUOTE_LEN = 60


def _label(governing) -> frozenset:
    return frozenset(governing)


def cohen_kappa(a: list[list[str]], b: list[list[str]]) -> float:
    """Categorical Cohen's kappa over paired labels (row-aligned). Each raw
    element is a `governing` list (chunk ids); the label compared is
    `frozenset(governing)` (empty == "none"). Chance agreement `pe` is
    computed from each rater's marginal label distribution. Returns 1.0 for
    empty input (no rows to disagree on) and when both raters are constant
    and identical (`pe` can only reach 1.0 in that exact case, since it is a
    dot product of two probability distributions bounded by 1 with equality
    only at matching one-hot distributions - so `po` is necessarily 1.0
    there too; guarding it directly avoids a 0/0 division).
    """
    n = len(a)
    if n == 0:
        return 1.0
    labels_a = [_label(x) for x in a]
    labels_b = [_label(x) for x in b]
    po = sum(1 for x, y in zip(labels_a, labels_b) if x == y) / n

    count_a = Counter(labels_a)
    count_b = Counter(labels_b)
    cats = set(count_a) | set(count_b)
    pe = sum((count_a.get(c, 0) / n) * (count_b.get(c, 0) / n) for c in cats)

    if pe >= 1.0 - 1e-9:
        return 1.0
    return (po - pe) / (1.0 - pe)


def decide(row: dict, votes_by_annotator: dict[str, list[str]],
          dated_ids: set[str]) -> tuple[str, list[str] | None]:
    """Spec sec7 promotion rules for one row.

    `votes_by_annotator` is this row's votes only, keyed by annotator name
    present iff that annotator voted on this row: {"claude": [...],
    "gemini": [...], "human": [...]}.

    Dated `as_of` rows always queue regardless of agreement (spec sec7
    exception - the gate cannot inherit a known-broken as_of behavior).

    Rows with no explicit claude vote are exactly the abstain rows (Task 8
    only judged the 207 answerable/pooled rows - abstain rows never got a
    claude vote at all). Their implicit claude label is `frozenset()`,
    matching the row's own authored `abstain: True` / `relevant_chunks: []`
    state, so the same truth table below applies uniformly: two externals
    confirming abstain (`governing: []`) is three-way agreement against that
    implicit label; two externals independently finding something governs
    after all is a genuine disagreement from it, handled as any other flip.

    Returns (decision, new_governing) with decision in {"promote",
    "flip_promote", "queue"}; new_governing is the winning chunk-id list
    for "flip_promote", else None.
    """
    if row["id"] in dated_ids:
        return "queue", None

    claude = votes_by_annotator.get("claude", [])
    gemini_governing = votes_by_annotator.get("gemini")
    human_governing = votes_by_annotator.get("human")

    claude_label = _label(claude)
    gemini_label = _label(gemini_governing) if gemini_governing is not None else None
    human_label = _label(human_governing) if human_governing is not None else None

    if gemini_label is not None and human_label is not None:
        if claude_label == gemini_label == human_label:
            return "promote", None
        if gemini_label == human_label and gemini_label != claude_label:
            return "flip_promote", list(gemini_label)
        return "queue", None

    if gemini_label is not None:
        if gemini_label == claude_label:
            return "promote", None
        return "queue", None

    return "queue", None


def apply(golden_rows: list[dict],
         decisions: dict[str, tuple[str, list[dict] | None]]) -> list[dict]:
    """Applies each row's `(decision, new_governing_spans)` from `decisions`
    (keyed by row id; rows absent from `decisions` are never touched - they
    weren't in the external sample this run). `new_governing_spans` (for
    "flip_promote" only) is already-resolved `{"doc", "quote"}` spans, not
    raw chunk ids - see `_resolve_governing_spans`.

    Promoted and flipped rows get `review_status: "adjudicated"`. Flipped
    rows additionally get `relevant_chunks` replaced by the winning spans and
    `label_source: "external-flip"`. "queue" decisions and rows with no
    decision at all are left completely unchanged.
    """
    out = []
    for row in golden_rows:
        row = dict(row)
        entry = decisions.get(row["id"])
        if entry is not None:
            decision, new_spans = entry
            if decision in ("promote", "flip_promote"):
                row["review_status"] = "adjudicated"
            if decision == "flip_promote":
                row["relevant_chunks"] = new_spans
                row["label_source"] = "external-flip"
        out.append(row)
    return out


def _body(chunk_text: str) -> str:
    lines = chunk_text.split("\n", 1)
    return lines[1] if len(lines) > 1 else lines[0]


def _resolve_governing_spans(chunk_ids: list[str], pool: dict) -> list[dict]:
    """Winning chunk ids (from a flip_promote decision) -> {doc, quote}
    spans, looked up from the row's own pool record - every chunk id a vote
    could ever choose came from that row's `pool["candidates"]` in the first
    place (Task 9/10's letter->chunk_id mapping is built from it), so no
    live-corpus lookup is needed. `quote` is the first 60 chars of the
    chunk's BODY text (never the `"<doc> | subject | section"` header line),
    or the whole body when it is shorter than 60 chars. Dedupes by chunk id
    while preserving first-seen order.
    """
    by_id = {c["chunk_id"]: c for c in pool["candidates"]}
    spans = []
    seen = set()
    for cid in chunk_ids:
        if cid in seen:
            continue
        seen.add(cid)
        if cid not in by_id:
            raise ValueError(
                f"chunk {cid!r} is not a candidate in pool {pool['id']!r} - "
                "every winning chunk id must come from that row's own pool")
        cand = by_id[cid]
        body = _body(cand["text"])
        spans.append({"doc": cand["doc"], "quote": body[:_QUOTE_LEN]})
    return spans


def _votes_by_row(votes: list) -> dict:
    out: dict = defaultdict(dict)
    for v in votes:
        out[v["id"]][v["annotator"]] = v["governing"]
    return out


def _stratum_kappas(rows_by_id: dict, votes_by_row: dict, external_ids: list) -> list:
    """κ + raw agreement %, per annotator-pair per stratum, over rows in
    `external_ids` that have votes from BOTH annotators in the pair."""
    pairs = [("claude", "gemini"), ("claude", "human"), ("gemini", "human")]
    by_stratum_pair: dict = defaultdict(lambda: defaultdict(list))
    for rid in external_ids:
        row = rows_by_id.get(rid)
        if row is None:
            continue
        stratum = row["task_type"]
        row_votes = votes_by_row.get(rid, {})
        claude = row_votes.get("claude", [])  # implicit [] for abstain rows
        available = {"claude": claude, **{k: v for k, v in row_votes.items() if k != "claude"}}
        for a, b in pairs:
            if a in available and b in available:
                by_stratum_pair[stratum][(a, b)].append((available[a], available[b]))

    out = []
    for stratum in sorted(by_stratum_pair):
        for pair in pairs:
            paired = by_stratum_pair[stratum].get(pair)
            if not paired:
                continue
            a_list = [p[0] for p in paired]
            b_list = [p[1] for p in paired]
            kappa = cohen_kappa(a_list, b_list)
            raw = sum(1 for x, y in zip(a_list, b_list) if _label(x) == _label(y)) / len(paired)
            out.append({"stratum": stratum, "pair": pair, "n": len(paired),
                        "kappa": kappa, "raw_agreement": raw})
    return out


def _claude_accuracy_ci(rows_by_id: dict, votes_by_row: dict, external_ids: list):
    """Clopper-Pearson 95% CI on claude-label accuracy vs externals: every
    (row, external annotator) pair where both voted is one trial; success is
    an exact label match. Abstain rows use the same implicit frozenset()
    claude label as `decide()`."""
    successes = 0
    n = 0
    for rid in external_ids:
        row = rows_by_id.get(rid)
        if row is None:
            continue
        row_votes = votes_by_row.get(rid, {})
        claude_label = _label(row_votes.get("claude", []))
        for annotator in ("gemini", "human"):
            if annotator in row_votes:
                n += 1
                if _label(row_votes[annotator]) == claude_label:
                    successes += 1
    return clopper_pearson_ci(successes, n)


def _render_report(kappa_rows: list, ci, counts: dict) -> str:
    lines = [
        "# Golden v7 external-annotation agreement",
        "",
        "Cohen's kappa and raw agreement per annotator pair per stratum, over "
        "rows in the external-100 sample where both annotators in the pair "
        "voted. Abstain rows (no claude label in Task 8) compare against an "
        "implicit `frozenset()` claude label matching their authored "
        "`abstain: true` state.",
        "",
        "| stratum | pair | n | kappa | raw agreement |",
        "|---|---|---|---|---|",
    ]
    for r in kappa_rows:
        lines.append(
            f"| {r['stratum']} | {r['pair'][0]}-{r['pair'][1]} | {r['n']} | "
            f"{r['kappa']:.3f} | {r['raw_agreement'] * 100:.1f}% |")
    lines += [
        "",
        "## Claude-label accuracy vs externals",
        "",
        f"{ci.successes}/{ci.n} matched ({ci.point * 100:.1f}%), "
        f"95% CI {ci.lo * 100:.1f}–{ci.hi * 100:.1f}% ({ci.method}).",
        "",
        "## Promotion outcomes",
        "",
        f"- promoted: {counts.get('promote', 0)}",
        f"- flipped: {counts.get('flip_promote', 0)}",
        f"- queued: {counts.get('queue', 0)}",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rows = load_golden(DEFAULT_GOLDEN_PATH)
    rows_by_id = {r["id"]: r for r in rows}
    votes = [json.loads(line) for line in
             DEFAULT_VOTES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    votes_by_row = _votes_by_row(votes)
    pools = [json.loads(line) for line in
             DEFAULT_POOLS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    pools_by_id = {p["id"]: p for p in pools}
    sample = json.loads(DEFAULT_SAMPLE_PATH.read_text(encoding="utf-8"))
    external_ids = sample["external"]
    dated_ids = {r["id"] for r in rows if r.get("as_of") is not None}

    decisions: dict = {}
    queue_records = []
    counts = Counter()
    for rid in external_ids:
        row = rows_by_id[rid]
        row_votes = votes_by_row.get(rid, {})
        decision, new_governing = decide(row, row_votes, dated_ids)
        counts[decision] += 1
        if decision == "flip_promote":
            spans = _resolve_governing_spans(new_governing, pools_by_id[rid])
            decisions[rid] = (decision, spans)
        else:
            decisions[rid] = (decision, None)
        if decision == "queue":
            queue_records.append({"row": row, "votes": row_votes})

    updated_rows = apply(rows, decisions)
    write_jsonl(DEFAULT_GOLDEN_PATH, updated_rows)

    with DEFAULT_QUEUE_PATH.open("w", encoding="utf-8") as f:
        for rec in queue_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    kappa_rows = _stratum_kappas(rows_by_id, votes_by_row, external_ids)
    ci = _claude_accuracy_ci(rows_by_id, votes_by_row, external_ids)
    DEFAULT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_REPORT_PATH.write_text(_render_report(kappa_rows, ci, counts), encoding="utf-8")

    print(f"promoted={counts.get('promote', 0)} flipped={counts.get('flip_promote', 0)} "
          f"queued={counts.get('queue', 0)} -> {DEFAULT_GOLDEN_PATH}")


if __name__ == "__main__":
    main()
