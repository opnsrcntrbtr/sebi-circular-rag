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

from sebi_rag.benchmark import _norm_ws, write_jsonl  # noqa: E402
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


# Annotators with fixed roles in the promotion rules. Anything else is "the
# external LLM leg" - gemini originally, qwen since the 2026-07-26 pivot to
# the local oMLX annotator. Discovering the leg instead of hardcoding a name
# keeps the on-hold gemini leg resumable with zero configuration.
_FIXED_ANNOTATORS = frozenset({"claude", "human"})


def _llm_annotator(names) -> str | None:
    """The single non-claude/non-human annotator among `names`, or None.

    Two at once is an error, never a guess: "the LLM vote" would be
    ambiguous, and silently preferring either leg would corrupt the
    agreement statistics the external pass exists to produce.
    """
    llm = sorted(set(names) - _FIXED_ANNOTATORS)
    if len(llm) > 1:
        raise ValueError(
            f"more than one external LLM annotator voted: {llm} - one leg "
            "at a time; drop one set of votes before running agreement")
    return llm[0] if llm else None


def _confirms_claude(claude_label: frozenset, external_label: frozenset | None,
                     row: dict | None = None, pool: dict | None = None,
                     literal: str = "") -> bool | None:
    """Does this external vote confirm claude's label, at PROVISION level?

    Amendment 2026-07-26 (user-approved after the pilot): the promotion unit
    is the provision, not the chunk-id set. Master circulars repeat the same
    clause across body/annexure/FAQ chunks and the harness itself already
    grades every quote-containing chunk as gold (`resolve_chunk_spans`: all
    overlap matches count) - exact-set agreement measured ~10% for BOTH
    external model families while provision-level measured ~60%, so exact-set
    equality mostly counted chunk-copy choice, not label disagreement.

    Confirmation, in order of strength: exact set equality; containment
    (external marked claude's chunks governing plus extras); or - when the
    row's pool is available - any external-picked chunk whose text contains
    one of the row's span quotes (the span IS the provision, by design).

    Abstain exception: for an abstain row (claude label empty), an empty
    external set with a NON-BLANK expected literal is the protocol's dispute
    signal (no letters were ever offered, so governing can never be
    non-empty there) - that never confirms. Returns None when the external
    did not vote at all.
    """
    if external_label is None:
        return None
    if not claude_label and not external_label:
        return not literal.strip()
    if external_label == claude_label:
        return True
    if claude_label and claude_label <= external_label:
        return True
    if row is not None and pool is not None and external_label:
        quotes = [_norm_ws(s["quote"]) for s in row.get("relevant_chunks", [])
                  if isinstance(s, dict) and s.get("quote")]
        texts = {c["chunk_id"]: c["text"] for c in pool.get("candidates", [])}
        return any(q in _norm_ws(texts.get(cid, ""))
                   for cid in external_label for q in quotes)
    return False


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


def gwet_ac1(a: list[list[str]], b: list[list[str]]) -> float:
    """Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a
    prevalence-robust chance term. Cohen's `pe` is a dot product of the two
    marginal distributions, so a single dominant label (numeric_table:
    almost every row converges on the same governing set) inflates `pe`
    toward `po` and collapses kappa to ~0 even when raw agreement is high -
    the base-rate paradox. AC1 instead estimates chance as
    `1/(L-1) * sum_k pk(1-pk)` over the L observed categories (pk = each
    label's proportion averaged across the two raters), which does not
    over-correct for skew. Reported ALONGSIDE kappa, never replacing it.

    Returns 1.0 for empty input and for a single observed category (both
    raters constant on the same label - no disagreement is possible, so the
    paradoxical 0/0 is resolved to perfect agreement).
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
    L = len(cats)
    if L <= 1:
        return 1.0
    pe = sum(
        ((count_a.get(c, 0) / n) + (count_b.get(c, 0) / n)) / 2.0
        * (1.0 - ((count_a.get(c, 0) / n) + (count_b.get(c, 0) / n)) / 2.0)
        for c in cats
    ) / (L - 1)

    if pe >= 1.0 - 1e-9:
        return 1.0
    return (po - pe) / (1.0 - pe)


def _provision_agree(label_a: frozenset, label_b: frozenset,
                     row: dict | None, pool: dict | None) -> bool:
    """Symmetric provision-level agreement between two governing labels, using
    the same confirmation logic as promotion (`_confirms_claude`): exact set
    equality, containment either way, or - when the row's pool is available -
    both picking a chunk whose text carries the row's span quote. This is the
    unit the pipeline actually promotes on; exact chunk-id equality (the kappa
    unit) is deliberately stricter and undercounts same-provision/different-
    chunk-copy picks. Both-empty (three-way "none") counts as agreement.
    """
    return bool(
        _confirms_claude(label_a, label_b, row, pool) is True
        or _confirms_claude(label_b, label_a, row, pool) is True
    )


def decide(row: dict, votes_by_annotator: dict[str, list[str]],
          dated_ids: set[str], pool: dict | None = None,
          literals: dict[str, str] | None = None) -> tuple[str, list[str] | None]:
    """Spec sec7 promotion rules for one row.

    `votes_by_annotator` is this row's votes only, keyed by annotator name
    present iff that annotator voted on this row: {"claude": [...],
    <llm leg>: [...], "human": [...]}. The LLM leg is discovered via
    `_llm_annotator` - "qwen" (local oMLX leg, primary) or "gemini" (on
    hold) - the truth table is identical either way.

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

    literals = literals or {}
    claude = votes_by_annotator.get("claude", [])
    llm = _llm_annotator(votes_by_annotator)
    llm_governing = votes_by_annotator.get(llm) if llm else None
    human_governing = votes_by_annotator.get("human")

    claude_label = _label(claude)
    llm_label = _label(llm_governing) if llm_governing is not None else None
    human_label = _label(human_governing) if human_governing is not None else None
    llm_ok = _confirms_claude(claude_label, llm_label, row, pool,
                              literals.get(llm, "") if llm else "")
    human_ok = _confirms_claude(claude_label, human_label, row, pool,
                                literals.get("human", ""))

    if llm_label is not None and human_label is not None:
        if llm_ok and human_ok:
            return "promote", None
        # Flip stays conservative: EXACT set agreement between the two
        # externals on a non-empty alternative. Empty is never a flip - the
        # abstain protocol cannot produce non-empty governing, and blanking
        # an answerable row's relevant_chunks is not a label, it is an
        # arbitration case.
        if (llm_label == human_label and llm_label != claude_label
                and llm_label):
            return "flip_promote", list(llm_label)
        return "queue", None

    if llm_label is not None:
        if llm_ok:
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


def _literals_by_row(votes: list) -> dict:
    """rid -> annotator -> expected_literal. Kept separate from
    `_votes_by_row` so decide()'s governing-set plumbing stays unchanged;
    the literal matters only for the abstain protocol, where a non-blank
    literal is the ONLY dispute signal an external can send (no letters are
    ever offered, so its governing set is structurally empty)."""
    out: dict = defaultdict(dict)
    for v in votes:
        out[v["id"]][v["annotator"]] = v.get("expected_literal", "")
    return out


def _tier_kappas(rows_by_id: dict, votes_by_row: dict, external_ids: list,
                 pools_by_id: dict | None = None) -> list:
    """As `_stratum_kappas`, grouped by label provenance tier rather than
    task_type. Reports agreement per tier so no tier is silently pooled into
    a headline figure it does not support. Tiers with n < 2 report None
    rather than a spurious coefficient."""
    llm = _llm_annotator(
        {a for rid in external_ids for a in votes_by_row.get(rid, {})})
    pairs = ([("claude", llm), ("claude", "human"), (llm, "human")]
             if llm else [("claude", "human")])
    by_tier_pair: dict = defaultdict(lambda: defaultdict(list))
    for rid in external_ids:
        row = rows_by_id.get(rid)
        if row is None:
            continue
        tier = row.get("label_tier", "unknown")
        pool = pools_by_id.get(rid) if pools_by_id else None
        row_votes = votes_by_row.get(rid, {})
        claude = row_votes.get("claude", [])
        available = {"claude": claude,
                     **{k: v for k, v in row_votes.items() if k != "claude"}}
        for a, b in pairs:
            if a in available and b in available:
                by_tier_pair[tier][(a, b)].append(
                    (available[a], available[b], row, pool))

    out = []
    for tier in sorted(by_tier_pair):
        for pair in pairs:
            paired = by_tier_pair[tier].get(pair)
            if not paired:
                continue
            a_list = [p[0] for p in paired]
            b_list = [p[1] for p in paired]
            if len(paired) < 2:
                out.append((tier, pair, len(paired), None, None))
                continue
            out.append((tier, pair, len(paired),
                        cohen_kappa(a_list, b_list), gwet_ac1(a_list, b_list)))
    return out


def _stratum_kappas(rows_by_id: dict, votes_by_row: dict, external_ids: list,
                    pools_by_id: dict | None = None) -> list:
    """Per annotator-pair per stratum, over rows in `external_ids` that have
    votes from BOTH annotators in the pair: exact-set kappa + raw agreement,
    Gwet's AC1 (prevalence-robust), and provision-level agreement (the
    promotion unit; needs `pools_by_id` for the span-quote branch). The LLM
    leg's name is discovered from the votes themselves, so the report labels
    its pairs honestly ("claude-qwen", not a hardcoded "gemini")."""
    llm = _llm_annotator(
        {a for rid in external_ids for a in votes_by_row.get(rid, {})})
    pairs = ([("claude", llm), ("claude", "human"), (llm, "human")]
             if llm else [("claude", "human")])
    by_stratum_pair: dict = defaultdict(lambda: defaultdict(list))
    for rid in external_ids:
        row = rows_by_id.get(rid)
        if row is None:
            continue
        stratum = row["task_type"]
        pool = pools_by_id.get(rid) if pools_by_id else None
        row_votes = votes_by_row.get(rid, {})
        claude = row_votes.get("claude", [])  # implicit [] for abstain rows
        available = {"claude": claude, **{k: v for k, v in row_votes.items() if k != "claude"}}
        for a, b in pairs:
            if a in available and b in available:
                by_stratum_pair[stratum][(a, b)].append(
                    (available[a], available[b], row, pool))

    out = []
    for stratum in sorted(by_stratum_pair):
        for pair in pairs:
            paired = by_stratum_pair[stratum].get(pair)
            if not paired:
                continue
            a_list = [p[0] for p in paired]
            b_list = [p[1] for p in paired]
            kappa = cohen_kappa(a_list, b_list)
            ac1 = gwet_ac1(a_list, b_list)
            raw = sum(1 for x, y in zip(a_list, b_list) if _label(x) == _label(y)) / len(paired)
            prov = sum(1 for x, y, row, pool in paired
                       if _provision_agree(_label(x), _label(y), row, pool)) / len(paired)
            out.append({"stratum": stratum, "pair": pair, "n": len(paired),
                        "kappa": kappa, "ac1": ac1, "raw_agreement": raw,
                        "provision_agreement": prov})
    return out


def _claude_accuracy_ci(rows_by_id: dict, votes_by_row: dict, external_ids: list,
                        pools_by_id: dict | None = None):
    """Two Clopper-Pearson 95% CIs on claude-label accuracy vs externals -
    every (row, external annotator) pair where both voted is one trial.
    Returns `(exact_ci, provision_ci)`:

    - exact: success is exact chunk-id-set match (the stricter, historical
      figure - the one that read 28.9%).
    - provision: success is provision-level agreement (`_provision_agree`),
      the unit the pipeline actually promotes on. Reported alongside exact so
      the same over-strict-unit artifact that depresses the kappa table is
      visible here too.

    Abstain rows use the same implicit frozenset() claude label as `decide()`.
    """
    successes = prov_successes = 0
    n = 0
    for rid in external_ids:
        row = rows_by_id.get(rid)
        if row is None:
            continue
        pool = pools_by_id.get(rid) if pools_by_id else None
        row_votes = votes_by_row.get(rid, {})
        claude_label = _label(row_votes.get("claude", []))
        for annotator, governing in row_votes.items():
            if annotator == "claude":
                continue
            n += 1
            ext_label = _label(governing)
            if ext_label == claude_label:
                successes += 1
            if _provision_agree(claude_label, ext_label, row, pool):
                prov_successes += 1
    return clopper_pearson_ci(successes, n), clopper_pearson_ci(prov_successes, n)


def _render_report(kappa_rows: list, ci_pair, counts: dict) -> str:
    exact_ci, prov_ci = ci_pair
    lines = [
        "# Golden v7 external-annotation agreement",
        "",
        "Per annotator pair per stratum, over rows in the external-100 sample "
        "where both annotators in the pair voted. `kappa` and `raw agreement` "
        "are exact chunk-id-set equality (deliberately strict). `AC1` is "
        "Gwet's prevalence-robust coefficient (fixes the base-rate paradox "
        "that collapses kappa on skewed strata like numeric_table). "
        "`provision` is agreement at the PROVISION level - the unit the "
        "pipeline actually promotes on (exact set, containment, or same span "
        "quote). Abstain rows (no claude label in Task 8) compare against an "
        "implicit `frozenset()` claude label matching their authored "
        "`abstain: true` state.",
        "",
        "| stratum | pair | n | kappa | AC1 | raw agreement | provision |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in kappa_rows:
        lines.append(
            f"| {r['stratum']} | {r['pair'][0]}-{r['pair'][1]} | {r['n']} | "
            f"{r['kappa']:.3f} | {r['ac1']:.3f} | "
            f"{r['raw_agreement'] * 100:.1f}% | {r['provision_agreement'] * 100:.1f}% |")
    lines += [
        "",
        "## Claude-label accuracy vs externals",
        "",
        f"Exact chunk-id-set match: {exact_ci.successes}/{exact_ci.n} "
        f"({exact_ci.point * 100:.1f}%), 95% CI {exact_ci.lo * 100:.1f}–"
        f"{exact_ci.hi * 100:.1f}% ({exact_ci.method}).",
        "",
        f"Provision-level match: {prov_ci.successes}/{prov_ci.n} "
        f"({prov_ci.point * 100:.1f}%), 95% CI {prov_ci.lo * 100:.1f}–"
        f"{prov_ci.hi * 100:.1f}% ({prov_ci.method}).",
        "",
        "## Promotion outcomes",
        "",
        "Promotion unit (spec sec7 as amended 2026-07-26): PROVISION-level - "
        "an external confirms claude's label via exact set match, containment, "
        "or picking any chunk whose text contains the row's span quote. The "
        "kappa table above stays at exact-set level, deliberately stricter "
        "than the promotion rule, so the reported agreement is never "
        "flattered by the amendment.",
        "",
        f"- promoted: {counts.get('promote', 0)}",
        f"- flipped: {counts.get('flip_promote', 0)}",
        f"- queued: {counts.get('queue', 0)}",
        "",
    ]
    return "\n".join(lines)


def main(report_only: bool = False, by_tier: bool = False) -> None:
    """Compute agreement + promotion and write the markdown report. When
    `report_only` (CLI `--report-only`), the promotion decisions are still
    computed (the report's outcome counts need them) but the golden set and
    arbitration queue are NOT rewritten - a report refresh must not re-churn
    a fully-adjudicated set (write_jsonl re-serialization + a regenerated raw
    queue that downstream arbitration had already resolved)."""
    rows = load_golden(DEFAULT_GOLDEN_PATH)
    rows_by_id = {r["id"]: r for r in rows}
    votes = [json.loads(line) for line in
             DEFAULT_VOTES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    votes_by_row = _votes_by_row(votes)

    if by_tier:
        # Read-only path: returns before write_jsonl, so it can never drop
        # label_tier. Coverage is the external sample, not all 260 rows.
        pools_ = {p["id"]: p for p in (json.loads(line) for line in
                  DEFAULT_POOLS_PATH.read_text(encoding="utf-8").splitlines()
                  if line.strip())}
        ext = json.loads(DEFAULT_SAMPLE_PATH.read_text(encoding="utf-8"))["external"]
        print(f"{'tier':<14}{'pair':<22}{'n':>5}{'kappa':>9}{'AC1':>9}")
        for tier, pair, n, kappa, ac1 in _tier_kappas(
                rows_by_id, votes_by_row, ext, pools_):
            k = "n/a" if kappa is None else f"{kappa:.3f}"
            a = "n/a" if ac1 is None else f"{ac1:.3f}"
            print(f"{tier:<14}{pair[0] + '-' + pair[1]:<22}{n:>5}{k:>9}{a:>9}")
        print(f"\ncoverage: {len(ext)} external-sample rows of {len(rows)} total")
        return

    literals_by_row = _literals_by_row(votes)
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
        decision, new_governing = decide(row, row_votes, dated_ids,
                                         pool=pools_by_id.get(rid),
                                         literals=literals_by_row.get(rid))
        counts[decision] += 1
        if decision == "flip_promote":
            spans = _resolve_governing_spans(new_governing, pools_by_id[rid])
            decisions[rid] = (decision, spans)
        else:
            decisions[rid] = (decision, None)
        if decision == "queue":
            queue_records.append({"row": row, "votes": row_votes})

    if not report_only:
        updated_rows = apply(rows, decisions)
        write_jsonl(DEFAULT_GOLDEN_PATH, updated_rows)

        with DEFAULT_QUEUE_PATH.open("w", encoding="utf-8") as f:
            for rec in queue_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    kappa_rows = _stratum_kappas(rows_by_id, votes_by_row, external_ids, pools_by_id)
    ci_pair = _claude_accuracy_ci(rows_by_id, votes_by_row, external_ids, pools_by_id)
    DEFAULT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_REPORT_PATH.write_text(_render_report(kappa_rows, ci_pair, counts), encoding="utf-8")

    target = DEFAULT_REPORT_PATH if report_only else DEFAULT_GOLDEN_PATH
    print(f"promoted={counts.get('promote', 0)} flipped={counts.get('flip_promote', 0)} "
          f"queued={counts.get('queue', 0)}"
          f"{' (report-only)' if report_only else ''} -> {target}")


if __name__ == "__main__":
    main(report_only="--report-only" in sys.argv,
         by_tier="--by-tier" in sys.argv)
