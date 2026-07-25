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
import re as _re
import sys
import time
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

# The design spec named gemini-3-flash-preview, but its free tier allows 20
# requests/DAY (measured 2026-07-26) against this task's 100, so it can never
# finish a pass. gemini-2.5-flash is the pinned replacement: non-preview and
# non-alias, so the annotator identity in the eval record stays reproducible -
# `gemini-flash-latest` would silently re-point as Google ships new versions.
DEFAULT_MODEL = "gemini-2.5-flash"


def _current_model() -> str:
    return os.environ.get("GOLDEN_GEMINI_MODEL", DEFAULT_MODEL)

# Same judging bar Task 8 held the claude annotator to (spec sec 6): without
# it the two annotators answer materially different questions - measured
# 2026-07-26 on a 5-row probe, the bare "governing provision" wording drew
# 0/5 exact-set agreement, gemini returning a strict SUPERSET of claude's
# pick on 3 of 5 (topically-relevant excerpts, not the operative provision).
# Deliberately ports the DEFINITION only, never how many chunks typically
# govern: that distribution is derived from claude's own labels, and feeding
# it back would tune this leg toward agreement instead of measuring it.
GOVERNING_INSTRUCTIONS = (
    "An excerpt is GOVERNING only if its own text contains the provision that "
    "answers the query. Topical relatedness is NOT enough - an excerpt that "
    "merely discusses the same subject, cross-references the rule, or lists it "
    "in a heading or table of contents does not govern. Select only the "
    "excerpt(s) whose text carries the operative provision itself.\n"
    "Reply with the letter(s) that contain the governing provision, "
    "comma-separated, or NONE; then on a new line EXPECTED: <short literal>."
)
ABSTAIN_INSTRUCTIONS = (
    "Is this answerable from SEBI circulars? reply YES or NO, then on a new "
    "line EXPECTED: <short literal>. If your answer is NO, leave EXPECTED "
    "blank (write nothing after EXPECTED:)."
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
    ([], "") output directly rather than being omitted). This is safe for
    NON-ABSTAIN rows: every answerable row's claude vote already has
    non-empty `governing`, so a parse-error there always reads as
    "disagreement" downstream, never a false match. It is NOT safe for
    abstain rows: claude never voted on those (no baseline to disagree
    with), so a garbled reply's ([], "") is byte-identical to a well-formed
    confirm-abstain vote there. `main()` mitigates this gap by scanning the
    cache after a run and warning on any parse_error ids - see
    `_parse_error_ids`. Per-row cache at `cache_dir/<id>.json` makes reruns
    free: a cached row is reconstructed from disk with zero calls to `post`.
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

            # `model` is provenance, not plumbing: every row in one leg must
            # come from the SAME annotator or the agreement stats are
            # meaningless, and a cache dir is long-lived enough to outlast a
            # model swap silently. Recording it makes a mixed leg auditable.
            cached = {"id": rid, "model": _current_model(), "reply": reply,
                      "governing": governing, "expected_literal": expected,
                      "parse_error": parse_error}
            cache_path.write_text(
                json.dumps(cached, ensure_ascii=False, indent=2), encoding="utf-8")

        votes.append({"id": rid, "annotator": "gemini",
                      "governing": cached["governing"],
                      "expected_literal": cached["expected_literal"]})
    return votes


_RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
_MAX_ATTEMPTS = 5
_MAX_BACKOFF_S = 90


def _should_retry(status: int) -> bool:
    """Transient-failure predicate for the real Gemini call: rate limiting
    (429) and the 5xx family are worth another attempt, everything else
    (401/403 bad key, 404 unknown model, 400 malformed request) is a hard
    error no amount of waiting fixes."""
    return status in _RETRY_STATUSES


def _daily_quota_exhausted(body: str) -> bool:
    """True when a 429 is the per-DAY free-tier cap rather than a per-minute
    burst limit. The two are not the same failure: a per-minute limit clears
    in under a minute and is worth waiting out, while the daily cap does not
    reset until tomorrow, so retrying only burns wall-clock and hides the
    real reason the run stopped. Measured 2026-07-26: gemini-3-flash-preview
    caps the free tier at 20 requests/day, far under this task's 100."""
    return "PerDay" in body


def _retry_delay_s(body: str) -> float | None:
    """Google advises its own wait in the 429 body (`retryDelay: "54s"`).
    Honouring it beats a fixed local backoff, which is either wastefully long
    or too short to clear the window."""
    m = _re.search(r'"retryDelay":\s*"(\d+(?:\.\d+)?)s"', body)
    return min(float(m.group(1)), _MAX_BACKOFF_S) if m else None


def _post_gemini(prompt: str) -> str:
    """Real Gemini call (not exercised by unit tests - those inject a fake
    `post`). model from GOLDEN_GEMINI_MODEL, default gemini-3-flash-preview;
    GEMINI_API_KEY is required - plain env access, no config abstraction.

    The key travels in the `x-goog-api-key` HEADER, never the query string:
    httpx echoes the full URL into HTTPStatusError, so a query-string key
    leaks verbatim into any traceback, log, or CI output on the first 503.

    Retries transient failures with linear backoff - a 100-row run hits the
    free tier's per-minute limit and the occasional 503, and without this a
    single blip aborts the whole pass (rows already cached still survive).
    """
    model = _current_model()
    api_key = os.environ["GEMINI_API_KEY"]
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model}:generateContent")
    last: Exception | None = None
    for attempt in range(_MAX_ATTEMPTS):
        try:
            resp = httpx.post(url, headers={"x-goog-api-key": api_key},
                               json={"contents": [{"parts": [{"text": prompt}]}]},
                               timeout=90.0)
            if resp.status_code == 429 and _daily_quota_exhausted(resp.text):
                raise RuntimeError(
                    f"{model}: free-tier DAILY quota exhausted - rows already "
                    "cached are kept, so rerunning tomorrow resumes where this "
                    "stopped. Set GOLDEN_GEMINI_MODEL to a model with a larger "
                    "free daily allowance to finish sooner.")
            if _should_retry(resp.status_code) and attempt < _MAX_ATTEMPTS - 1:
                time.sleep(_retry_delay_s(resp.text) or 2 * (attempt + 1))
                continue
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except httpx.TransportError as e:  # connect/read timeouts, DNS blips
            last = e
            if attempt == _MAX_ATTEMPTS - 1:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"gemini call failed after {_MAX_ATTEMPTS} attempts: {last}")


def _parse_error_ids(ids: list[str], cache_dir: str | Path) -> list[str]:
    """Scans the per-row cache for `ids` and returns the ones flagged
    parse_error: true. The vote record itself doesn't carry this flag (its
    shape is pinned to 4 keys), so without this, parse errors are only
    visible by hand-grepping the cache directory - this is what lets
    main() print a visible warning instead, which matters most for abstain
    rows (see adjudicate()'s docstring: a parse-error there is byte-
    identical to a legitimate confirm-abstain vote, so the count is the
    only signal something needs a human look)."""
    cache_dir = Path(cache_dir)
    bad = []
    for rid in ids:
        cache_path = cache_dir / f"{rid}.json"
        if cache_path.exists():
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if cached.get("parse_error"):
                bad.append(rid)
    return bad


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

    bad_ids = _parse_error_ids(ids, DEFAULT_CACHE_DIR)
    if bad_ids:
        print(f"WARNING: {len(bad_ids)} of {len(ids)} row(s) had an "
              f"unparseable Gemini reply (parse_error=true in cache), "
              f"needs a human look: {bad_ids}")

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
