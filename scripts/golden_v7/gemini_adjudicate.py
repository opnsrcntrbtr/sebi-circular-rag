"""External annotation slice: second-family LLM leg via the Gemini API
(spec 2026-07-23 sec 7).

Runs the same blind protocol as `make_packet.py`'s human packet - shuffled,
lettered excerpts, no scores/ranks/system hints - but over an LLM instead of
a human, for all 100 ids in `external_sample.json`'s "external" list. Each
row is answered once and cached to disk (`v7_annotations/gemini/<id>.json`)
so reruns are free and resumable; `main()` treats its own gemini output as
authoritative on every run, replacing any prior "gemini" vote records in
votes.jsonl while leaving "claude"/"human" records untouched.

Real run (writes v7_annotations/gemini/*.json + appends to votes.jsonl):
    make golden-v7-gemini          # needs GEMINI_API_KEY in the environment
"""
from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.eval_harness import load_golden  # noqa: E402

DEFAULT_CACHE_DIR = ROOT / "eval" / "golden" / "v7_annotations" / "gemini"
DEFAULT_VOTES_PATH = ROOT / "eval" / "golden" / "v7_annotations" / "votes.jsonl"
DEFAULT_POOLS_PATH = ROOT / "eval" / "golden" / "v7_annotations" / "pools.jsonl"
DEFAULT_SAMPLE_PATH = ROOT / "eval" / "golden" / "v7_annotations" / "external_sample.json"
DEFAULT_GOLDEN_PATH = ROOT / "eval" / "golden" / "golden_v7.jsonl"

GOVERNING_INSTRUCTIONS = (
    "Reply with the letter(s) that contain the governing provision, "
    "comma-separated, or NONE; then on a new line EXPECTED: <short literal>."
)
ABSTAIN_INSTRUCTIONS = (
    "Is this answerable from SEBI circulars? reply YES or NO, then on a new "
    "line EXPECTED: <short literal>."
)


def _shuffled_candidates(row_id: str, pool: dict | None) -> list[dict]:
    """Same per-row deterministic shuffle as make_packet.py's write_packet:
    random.Random(row_id) (the id string, never hash(row_id))."""
    candidates = list(pool["candidates"]) if pool else []
    random.Random(row_id).shuffle(candidates)
    return candidates


def build_prompt(row: dict, pool: dict | None) -> str:
    """Blind-protocol prompt text (plain text, not HTML - no html.escape).
    Non-abstain rows get shuffled, lettered excerpts and the letter-choice
    reply format; abstain rows (and any row whose pool has zero candidates,
    which can't offer a lettered choice either) get the no-excerpt YES/NO
    protocol instead. No scores, ranks, or hints about which excerpt the
    system favors - letters are the only ordering signal, same anti-leakage
    bar as Task 9's human packet."""
    query = row.get("query", "")
    candidates = _shuffled_candidates(row["id"], pool)

    if not candidates:
        return f"Query: {query}\n\n{ABSTAIN_INSTRUCTIONS}"

    lines = [f"Query: {query}", "", "Excerpts from SEBI circulars:"]
    for i, cand in enumerate(candidates):
        letter = chr(ord("A") + i)
        lines.append(f"{letter}. [{cand['doc']}] {cand['text']}")
    lines.append("")
    lines.append(GOVERNING_INSTRUCTIONS)
    return "\n".join(lines)


def _parse_letter_choice(text: str, letters: list[str]) -> tuple[list[str], str, bool]:
    """Letter-choice protocol: first non-blank line is the choice (comma or
    semicolon separated letters, or NONE); a later 'EXPECTED:' line carries
    the literal. Fails CLOSED - a reply naming any letter outside `letters`
    invalidates the WHOLE reply (never silently drops just the bad token),
    since this parses an unattended API response and must never raise."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        return [], "", True

    expected = ""
    for line in lines[1:]:
        if line.upper().startswith("EXPECTED"):
            expected = line.partition(":")[2].strip()
            break

    choice_line = lines[0].rstrip(".")
    if choice_line.upper() == "NONE":
        return [], expected, False

    tokens = [t.strip().rstrip(".").upper()
              for t in choice_line.replace(";", ",").split(",")]
    tokens = [t for t in tokens if t]
    if not tokens:
        return [], "", True

    valid = set(letters)
    chosen: list[str] = []
    for tok in tokens:
        if tok not in valid:
            return [], "", True  # fail closed: whole reply is unparseable
        if tok not in chosen:
            chosen.append(tok)
    return chosen, expected, False


def _parse_yes_no(text: str) -> tuple[list[str], str, bool]:
    """Abstain-protocol reply parser. governing is always [] - no excerpts
    were ever offered, so nothing can be "governing" regardless of the
    YES/NO answer; only the (optional) EXPECTED literal is informative,
    mirroring Task 9's human-abstain-protocol semantics (blank confirms
    abstain, non-blank text disputes it)."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        return [], "", True

    first_tokens = lines[0].split()
    first = first_tokens[0].strip(".,:;!?").upper() if first_tokens else ""
    if first not in ("YES", "NO"):
        return [], "", True

    expected = ""
    for line in lines[1:]:
        if line.upper().startswith("EXPECTED"):
            expected = line.partition(":")[2].strip()
            break
    return [], expected, False


def _parse_reply(text: str, letters: list[str]) -> tuple[list[str], str, bool]:
    """Full parse result including the parse_error flag cached per row.
    letters=[] is how adjudicate() signals an abstain/zero-candidate row,
    which dispatches to the YES/NO protocol instead of the letter-choice one."""
    if not letters:
        return _parse_yes_no(text)
    return _parse_letter_choice(text, letters)


def parse_reply(text: str, letters: list[str]) -> tuple[list[str], str]:
    """Public letter-choice-protocol parser: (chosen letters, expected
    literal). Unparseable input -> ([], "") (see adjudicate() for how the
    parse_error flag that accompanies this gets recorded in the cache)."""
    chosen, expected, _parse_error = _parse_reply(text, letters)
    return chosen, expected


def adjudicate(rows: list[dict], pools: list[dict], ids: list[str], post,
               cache_dir: str | Path = DEFAULT_CACHE_DIR) -> list[dict]:
    """Runs the blind protocol over every id in `ids`, calling `post(prompt)
    -> str` once per row not already cached. Returns one "gemini" vote
    record per id (parse-error rows included, using parse_reply's literal
    ([], "") output directly rather than being omitted - safe, since every
    answerable row's claude vote already has non-empty `governing`, so a
    parse-error always reads as "disagreement" downstream, never a false
    match). Per-row cache at `cache_dir/<id>.json` makes reruns free: a
    cached row is reconstructed from disk with zero calls to `post`.
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    rows_by_id = {r["id"]: r for r in rows}
    pools_by_id = {p["id"]: p for p in pools}

    votes: list[dict] = []
    for rid in ids:
        cache_path = cache_dir / f"{rid}.json"
        if cache_path.exists():
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            row = rows_by_id[rid]
            pool = pools_by_id.get(rid)
            prompt = build_prompt(row, pool)
            reply = post(prompt)

            shuffled = _shuffled_candidates(rid, pool)
            letters = [chr(ord("A") + i) for i in range(len(shuffled))]
            letter_to_chunk = {l: c["chunk_id"] for l, c in zip(letters, shuffled)}

            chosen, expected, parse_error = _parse_reply(reply, letters)
            governing = [letter_to_chunk[l] for l in chosen]

            cached = {"id": rid, "reply": reply, "governing": governing,
                      "expected_literal": expected, "parse_error": parse_error}
            cache_path.write_text(
                json.dumps(cached, ensure_ascii=False, indent=2), encoding="utf-8")

        votes.append({"id": rid, "annotator": "gemini",
                      "governing": cached["governing"],
                      "expected_literal": cached["expected_literal"]})
    return votes


def _post_gemini(prompt: str) -> str:
    """Real Gemini call (not exercised by unit tests - those inject a fake
    `post`). model from GOLDEN_GEMINI_MODEL, default gemini-3-flash-preview;
    GEMINI_API_KEY is required - plain env access, no config abstraction."""
    model = os.environ.get("GOLDEN_GEMINI_MODEL", "gemini-3-flash-preview")
    api_key = os.environ["GEMINI_API_KEY"]
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model}:generateContent")
    resp = httpx.post(url, params={"key": api_key},
                       json={"contents": [{"parts": [{"text": prompt}]}]},
                       timeout=60.0)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _replace_annotator_votes(existing: list[dict], new_votes: list[dict],
                              annotator: str) -> list[dict]:
    """Rerun-safety for votes.jsonl itself (plan Task 10 decision #7): drops
    every existing record for `annotator`, appends the freshly computed
    `new_votes`, and leaves every other annotator's records untouched and in
    their original relative order. Running the adjudication leg twice must
    not duplicate or corrupt votes.jsonl - the freshly computed set is
    authoritative on every run."""
    kept = [v for v in existing if v.get("annotator") != annotator]
    return kept + new_votes


def main() -> None:
    rows = load_golden(DEFAULT_GOLDEN_PATH)
    pools = [json.loads(line) for line in
             DEFAULT_POOLS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    sample = json.loads(DEFAULT_SAMPLE_PATH.read_text(encoding="utf-8"))
    ids = sample["external"]

    gemini_votes = adjudicate(rows, pools, ids, _post_gemini)

    existing = []
    if DEFAULT_VOTES_PATH.exists():
        existing = [json.loads(line) for line in
                    DEFAULT_VOTES_PATH.read_text(encoding="utf-8").splitlines()
                    if line.strip()]
    all_votes = _replace_annotator_votes(existing, gemini_votes, "gemini")

    with DEFAULT_VOTES_PATH.open("w", encoding="utf-8") as f:
        for v in all_votes:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")

    print(f"gemini votes: {len(gemini_votes)} (of {len(ids)} ids) -> {DEFAULT_VOTES_PATH}")


if __name__ == "__main__":
    main()
