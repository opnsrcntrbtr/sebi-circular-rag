"""External annotation slice: stratified sampling + blind human packet +
CSV ingest (spec 2026-07-23 sec 7).

Sampling universe is all 260 rows of golden_v7 (carried and new alike),
stratified proportionally across the 8 task_type strata. 100 of those form
the "external" slice (Task 10 will run the Gemini leg over it); 30 of the
100 additionally form the human packet written here as self-contained,
blind HTML plus a CSV the human fills in and `ingest_packet` reads back.

Real run (writes packet_human/ + external_sample.json):
    make golden-v7-packet          # offline, instant — no MPS/heavy models
"""
from __future__ import annotations

import csv
import html
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.benchmark import STRATA_TARGETS_V7  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402

# Fixed stratum order for deterministic remainder tie-breaks (largest-remainder
# apportionment): STRATA_TARGETS_V7's own key order, per plan Task 9.
_CANONICAL_ORDER = list(STRATA_TARGETS_V7)

ABSTAIN_PROMPT = ("Is this answerable from SEBI circulars? "
                   "(yes = flag, no = confirm abstain)")
GOVERNING_PROMPT = "Which excerpt(s) contain the governing provision, or none?"


def _stratum_order(task_types) -> list[str]:
    """Canonical STRATA_TARGETS_V7 order for known types, any others appended
    alphabetically (defensive: real data never hits the fallback)."""
    known = [t for t in _CANONICAL_ORDER if t in task_types]
    extra = sorted(t for t in task_types if t not in _CANONICAL_ORDER)
    return known + extra


def _apportion(counts: dict[str, int], n: int, order: list[str]) -> dict[str, int]:
    """Largest-remainder apportionment of `n` seats across strata, proportional
    to each stratum's `counts` value. Exact integer arithmetic (no floats) so
    it is reproducible bit-for-bit. Ties in the remainder are broken by
    `order` (earlier wins). Guaranteed quota[k] <= counts[k] for every k and
    sum(quota.values()) == n (when 0 <= n <= sum(counts.values())).
    """
    total = sum(counts.values())
    quotas = {k: 0 for k in counts}
    if total == 0 or n <= 0:
        return quotas
    remainders = {}
    for k, c in counts.items():
        numerator = c * n
        quotas[k] = numerator // total
        remainders[k] = numerator % total
    leftover = n - sum(quotas.values())
    ranked = sorted(order, key=lambda k: (-remainders[k], order.index(k)))
    for k in ranked[:leftover]:
        quotas[k] += 1
    return quotas


def sample_external(rows: list[dict], n: int, human_n: int, rng: random.Random
                     ) -> tuple[list[str], list[str]]:
    """Stratified-proportional draw of `n` row ids from ALL of `rows` (carried
    and new alike, abstain rows included — spec sec 7: "negatives included").
    `human_n` of those `n` additionally form the human packet; drawn as a
    prefix of each stratum's already-shuffled external picks, so
    `set(human_ids) <= set(external_ids)` holds by construction.
    """
    by_stratum: dict[str, list[dict]] = {}
    for row in rows:
        by_stratum.setdefault(row["task_type"], []).append(row)
    order = _stratum_order(by_stratum.keys())

    counts = {k: len(v) for k, v in by_stratum.items()}
    ext_quota = _apportion(counts, n, order)

    external_ids: list[str] = []
    ext_ids_by_stratum: dict[str, list[str]] = {}
    for k in order:
        stratum_rows = list(by_stratum[k])
        rng.shuffle(stratum_rows)
        chosen = [r["id"] for r in stratum_rows[:ext_quota[k]]]
        ext_ids_by_stratum[k] = chosen
        external_ids.extend(chosen)

    human_quota = _apportion(ext_quota, human_n, order)
    human_ids: list[str] = []
    for k in order:
        human_ids.extend(ext_ids_by_stratum[k][:human_quota[k]])

    return external_ids, human_ids


def write_packet(rows: list[dict], pools: list[dict], ids: list[str],
                  human_ids: list[str], out_dir: str | Path) -> None:
    """Writes the blind human packet for `human_ids` (a subset of `ids`, the
    full external slice — see plan Task 9 resolved ambiguity #6: the on-disk
    packet covers exactly `human_ids`, `ids` is only the containment check):
      - packet.html: self-contained, HTML-escaped, one <details> per row,
        excerpts shuffled per-row by random.Random(row_id) and lettered
        A, B, C... No scores, ranks, or system answers anywhere — letters are
        the only ordering signal.
      - manifest.json: {row_id: {"A": chunk_id, ...}} — non-abstain rows only.
      - labels_template.csv: columns id,choices,expected_literal. Non-abstain
        rows start blank (human fills both in); abstain rows have nothing to
        choose from so `choices` is pre-set to "none" and only
        expected_literal is the human's to edit (blank confirms abstain, any
        text disputes it).
    """
    assert set(human_ids) <= set(ids), "human_ids must be a subset of ids"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    by_id = {r["id"]: r for r in rows}
    pool_by_id = {p["id"]: p for p in pools}

    manifest: dict[str, dict[str, str]] = {}
    csv_rows: list[dict[str, str]] = []
    parts = [
        "<!doctype html>", "<html>", "<head>", '<meta charset="utf-8">',
        "<title>Golden v7 Human Packet</title>",
        "<style>",
        "body { font-family: sans-serif; max-width: 60rem; margin: 2rem auto; }",
        "details { border: 1px solid #ccc; border-radius: 4px; "
        "margin-bottom: 0.75rem; padding: 0.5rem 0.75rem; }",
        "summary { font-weight: bold; cursor: pointer; }",
        ".prompt { font-style: italic; }",
        ".excerpt { white-space: pre-wrap; border: 1px solid #ddd; "
        "padding: 0.5rem; margin: 0.25rem 0 0.75rem; }",
        ".doc { color: #555; font-size: 0.9em; }",
        "</style>", "</head>", "<body>",
        "<h1>Golden v7 Human Packet</h1>",
    ]

    for rid in human_ids:
        row = by_id[rid]
        query = html.escape(row.get("query", ""))
        parts.append("<details>")
        parts.append(f"<summary>{html.escape(rid)}</summary>")
        parts.append(f'<p class="query">{query}</p>')

        if row.get("abstain"):
            parts.append(f'<p class="prompt">{html.escape(ABSTAIN_PROMPT)}</p>')
            csv_rows.append({"id": rid, "choices": "none", "expected_literal": ""})
        else:
            pool = pool_by_id.get(rid)
            if pool is None:
                raise ValueError(f"no pool record for non-abstain row {rid!r}")
            candidates = list(pool["candidates"])
            random.Random(rid).shuffle(candidates)
            # A..Z only: pools cap at 20 candidates (build_pool.py), well under 26.
            letters = [chr(ord("A") + i) for i in range(len(candidates))]

            parts.append(f'<p class="prompt">{html.escape(GOVERNING_PROMPT)}</p>')
            parts.append('<ul class="options">')
            row_manifest = {}
            for letter, cand in zip(letters, candidates):
                row_manifest[letter] = cand["chunk_id"]
                excerpt = html.escape(cand["text"])
                doc = html.escape(cand["doc"])
                parts.append(
                    f"<li><strong>{letter}.</strong> "
                    f'<span class="doc">{doc}</span>'
                    f'<div class="excerpt">{excerpt}</div></li>')
            parts.append("</ul>")
            manifest[rid] = row_manifest
            csv_rows.append({"id": rid, "choices": "", "expected_literal": ""})

        parts.append("</details>")

    parts.append("</body></html>")

    (out_dir / "packet.html").write_text("\n".join(parts), encoding="utf-8")
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    with (out_dir / "labels_template.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "choices", "expected_literal"])
        writer.writeheader()
        writer.writerows(csv_rows)


def ingest_packet(csv_path: str | Path, manifest_path: str | Path) -> list[dict]:
    """Reads a human-filled labels_template.csv back into vote records
    (`annotator: "human"`), mapping letters to chunk ids via manifest.json.

    A CSV row whose id has no manifest entry is abstain-protocol (no letters
    were ever offered for it, so none can be "unknown"): governing is always
    [] and expected_literal is taken verbatim (blank = confirms abstain, any
    text = disputes it). For a row that DOES have a manifest entry, an
    unrecognized letter in `choices` raises ValueError.
    """
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    votes = []
    with Path(csv_path).open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rid = row["id"]
            expected_literal = (row.get("expected_literal") or "").strip()
            entry = manifest.get(rid)
            if entry is None:
                votes.append({"id": rid, "annotator": "human", "governing": [],
                              "expected_literal": expected_literal})
                continue
            raw = (row.get("choices") or "").strip()
            governing: list[str] = []
            if raw and raw.lower() != "none":
                for letter in [c.strip() for c in raw.split(";") if c.strip()]:
                    if letter not in entry:
                        raise ValueError(
                            f"unknown letter {letter!r} for row {rid!r}")
                    governing.append(entry[letter])
            votes.append({"id": rid, "annotator": "human", "governing": governing,
                          "expected_literal": expected_literal})
    return votes


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default=str(ROOT / "eval" / "golden" / "golden_v7.jsonl"))
    ap.add_argument("--pools", default=str(
        ROOT / "eval" / "golden" / "v7_annotations" / "pools.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "eval" / "golden" / "v7_annotations"))
    args = ap.parse_args()

    rows = load_golden(args.golden)
    pools_path = Path(args.pools)
    pools = [json.loads(line) for line in
             pools_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    rng = random.Random(20260723)
    external_ids, human_ids = sample_external(rows, 100, 30, rng)

    out_root = Path(args.out)
    write_packet(rows, pools, external_ids, human_ids, out_root / "packet_human")

    (out_root / "external_sample.json").write_text(
        json.dumps({"external": external_ids, "human": human_ids},
                   ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"external={len(external_ids)} human={len(human_ids)} -> {out_root}")


if __name__ == "__main__":
    main()
