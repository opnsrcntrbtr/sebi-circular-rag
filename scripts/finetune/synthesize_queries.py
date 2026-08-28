"""Phase 1 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-
bright-dawn.md): LLM-synthesized queries for the strata Phase 0 showed are
weak or need more signal - numeric_table, multi_hop, lineage_supersession.
Phase 0's gate found numeric_table (+3.3pp) and multi_hop (+5.0pp) recall@10
positive on structural pairs alone; lineage_supersession was the one
negative gate stratum (-2.7pp) - all three get LLM enrichment here, not
just the failing one, since Phase 0's own honest-prior section names
per-stratum lift (not aggregate) as the real target, and two positive
strata are exactly where more, better-targeted signal is likely to compound.

Three source generators, one per stratum, each run as its own SEQUENTIAL
block (never interleaved) so the fixed instruction preamble stays
byte-identical across many consecutive calls within a block - that is what
makes `preserve_mid_system_cache` actually pay off; switching strata
invalidates the prefix cache once per switch (3 times total), not per call:

  numeric_table          one chunk containing a number/%/deadline/amount
                          (regex-filtered candidate pool, ~12.7k available)
                          -> query about that specific figure
  multi_hop               a citation_context pair (citing passage + cited
                          doc) -> a question needing BOTH to answer
  lineage_supersession     a lineage pair (current + superseded/amended)
                          -> a question about which rule currently governs

Every source respects the holdout boundary exactly as mine_structural_
pairs.py does (reuses its load_minable_docs / _strip_context_header /
_leaks_metadata directly - one contamination boundary, one leak filter,
not two independently-maintained copies that could drift).

Transport: OpenAI-compatible POST to oMLX, single user-role message
(preamble + trailing content) - the SAME shape verified live in this
session's earlier probe (17.7 tok/s, no <think> leakage) and the same
shape Phase -2's local_adjudicate.py uses, not a new untested one.
Sampling is the model's own pinned config: temperature 0.6, top_p 0.9,
min_p 0.01, repetition_penalty 1.05 (oMLX config, not a guess).

Two real defects from this session's live probe drive the two filters
here (see the plan's "Measured facts" section):
  1. metadata leakage - reuses mine_structural_pairs.METADATA_LEAK_RE
  2. self-assigned stratum labels are unreliable - the model's own `type`
     field (if it emits one) is discarded; stratum comes ONLY from which
     source generator/preamble produced the call, never from model output

Resumable: on-disk cache keyed by (stratum, source_id, model_id) under
data/finetune/synth_cache/<stratum>/. An interrupted 8h run picks back up
without re-paying for already-answered chunks.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/finetune/synthesize_queries.py
Output:
    data/finetune/pairs_synth_raw.jsonl (query, positive, template,
    source_doc, model rows - same shape mine_structural_pairs.py emits,
    minus `neg`, which roundtrip_filter.py + a later negative-mining pass
    add)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
for k, v in {
    "TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(k, v)

from export_datasets import build_citation_pairs, build_supersession_pairs  # noqa: E402
from finetune.mine_structural_pairs import (  # noqa: E402
    MIN_CHUNK_CHARS,
    _leaks_metadata,
    _strip_context_header,
    load_chunks_by_doc,
    load_corpus_records,
    load_minable_docs,
)
from sebi_rag.ingest_pdf import normalize_circular_number  # noqa: E402

DEFAULT_CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
DEFAULT_CHUNKS = ROOT / "data" / "index" / "chunks.jsonl"
DEFAULT_LINEAGE = ROOT / "data" / "index" / "lineage.json"
DEFAULT_HOLDOUT = ROOT / "data" / "finetune" / "holdout_docs.json"
DEFAULT_OUT = ROOT / "data" / "finetune" / "pairs_synth_raw.jsonl"
DEFAULT_CACHE_DIR = ROOT / "data" / "finetune" / "synth_cache"

DEFAULT_BASE_URL = "http://127.0.0.1:8001"
DEFAULT_MODEL = "Qwen3.8-27B-oQ4e-mtp"
SEED = 42

# oMLX's own pinned sampling config for this model (not a guess - the
# server's model config this plan's "Measured facts" section is built on).
TEMPERATURE = 0.6
TOP_P = 0.9
MIN_P = 0.01
REPETITION_PENALTY = 1.05
MAX_TOKENS = 300  # a one-sentence question; generous headroom over what
                  # the live probe actually produced

# Target volume per stratum, capped by whatever's actually available.
# ~10k total (plan's budget) split across three strata, skewed slightly
# toward lineage_supersession (Phase 0's one negative gate stratum) and
# away from multi_hop (fewer natural source pairs exist for it anyway).
TARGETS = {"numeric_table": 3500, "multi_hop": 3000, "lineage_supersession": 3500}

_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)
_MAX_ATTEMPTS = 4

NUMERIC_RE = re.compile(
    r"%|₹|Rs\.|INR|\bnot exceeding\b|\bat least\b|\bwithin\s+\d+\s+(day|month|year)"
    r"|\d+\s*(day|month|year)s?\b",
    re.IGNORECASE,
)

PREAMBLES = {
    "numeric_table": (
        "You are indexing Indian securities regulations (SEBI circulars) for "
        "a search system. Read the provision below, which contains a "
        "specific number, percentage, amount, or deadline. Write ONE "
        "natural-language question a compliance professional might type "
        "into a search box to find this exact provision. The question must "
        "be answerable using ONLY the number, amount, or deadline in this "
        "text. Do not mention any circular number, date, or reference id in "
        "your question - ask about the RULE, not the document. Reply with "
        'ONLY a JSON object: {"query": "your question here"}\n\n'
        "Provision:\n"
    ),
    "multi_hop": (
        "You are indexing Indian securities regulations (SEBI circulars) "
        "for a search system. Below are two related passages: Passage A "
        "cites or references Passage B. Write ONE natural-language question "
        "that requires understanding BOTH passages together to answer "
        "fully - a question a user could NOT answer from either passage "
        "alone. Do not mention any circular number, date, or reference id "
        'in your question. Reply with ONLY a JSON object: {"query": "your '
        'question here"}\n\n'
    ),
    "lineage_supersession": (
        "You are indexing Indian securities regulations (SEBI circulars) "
        "for a search system. Below are two related passages: the CURRENT "
        "passage governs a topic today; the EARLIER passage is a prior "
        "provision on the same topic that it superseded or amended. Write "
        "ONE natural-language question a user might ask when trying to "
        "find the CURRENT, governing rule on this topic. Do not mention any "
        "circular number, date, or reference id in your question. Reply "
        'with ONLY a JSON object: {"query": "your question here"}\n\n'
    ),
}


# ---------------------------------------------------------------------------
# source candidate generators - one per stratum
# ---------------------------------------------------------------------------

def numeric_table_candidates(chunks_by_doc: dict[str, list[dict]],
                             minable: set[str], seed: int) -> list[dict]:
    """Each candidate: {"source_id", "prompt_body", "positive", "source_doc"}."""
    rng = random.Random(seed)
    pool = []
    for doc_id, chunks in chunks_by_doc.items():
        if doc_id not in minable:
            continue
        for c in chunks:
            body = _strip_context_header(c["text"], doc_id)
            if len(body) < MIN_CHUNK_CHARS or not NUMERIC_RE.search(body):
                continue
            pool.append({"source_id": c["id"], "prompt_body": body,
                        "positive": body, "source_doc": doc_id})
    rng.shuffle(pool)
    return pool


def multi_hop_candidates(corpus_records: list[dict], chunks_by_doc: dict[str, list[dict]],
                         minable: set[str], seed: int) -> list[dict]:
    """Reuses build_citation_pairs verbatim - same source as Phase 0's
    citation_context template, but here BOTH the citing context AND the
    cited doc's body (not just its subject line) go to the LLM, so it can
    write a genuinely two-passage question."""
    rng = random.Random(seed)
    by_norm = {normalize_circular_number(r["circular_number"]): r for r in corpus_records}
    raw_pairs = build_citation_pairs(corpus_records)
    pool = []
    for p in raw_pairs:
        source, target_norm = p["source_doc_id"], p["normalized_circular_number"]
        target = by_norm.get(target_norm)
        if target is None or source not in minable:
            continue
        target_id = target["circular_number"]
        if target_id not in minable:
            continue
        target_chunks = [c for c in chunks_by_doc.get(target_id, [])
                         if not c["section"].endswith("/preamble")]
        if not target_chunks:
            continue
        target_chunk = rng.choice(target_chunks)
        target_body = _strip_context_header(target_chunk["text"], target_id)
        if len(target_body) < MIN_CHUNK_CHARS:
            continue
        prompt_body = (f"Passage A (citing):\n{p['context_window']}\n\n"
                       f"Passage B (cited):\n{target_body}\n")
        pool.append({"source_id": f"{source}->{target_id}#{p['raw_reference']}",
                    "prompt_body": prompt_body, "positive": target_body,
                    "source_doc": source})
    rng.shuffle(pool)
    return pool


def lineage_supersession_candidates(corpus_records: list[dict],
                                    chunks_by_doc: dict[str, list[dict]],
                                    lineage: dict, minable: set[str],
                                    seed: int) -> list[dict]:
    """Reuses build_supersession_pairs verbatim (Phase 0's lineage_pair
    source) - unrelated-label rows already excluded by that function's own
    contract, mirrored here the same way mine_structural_pairs.py does it."""
    rng = random.Random(seed)
    raw_pairs = build_supersession_pairs(corpus_records, lineage)
    pool = []
    for p in raw_pairs:
        if p["label"] == "unrelated":
            continue
        a, b = p["circular_a_number"], p["circular_b_number"]  # a supersedes/amends b
        if a not in minable or b not in minable:
            continue
        a_chunks = [c for c in chunks_by_doc.get(a, []) if not c["section"].endswith("/preamble")]
        b_chunks = [c for c in chunks_by_doc.get(b, []) if not c["section"].endswith("/preamble")]
        if not a_chunks or not b_chunks:
            continue
        a_body = _strip_context_header(rng.choice(a_chunks)["text"], a)
        b_body = _strip_context_header(rng.choice(b_chunks)["text"], b)
        if len(a_body) < MIN_CHUNK_CHARS or len(b_body) < MIN_CHUNK_CHARS:
            continue
        prompt_body = f"Current passage:\n{a_body}\n\nEarlier passage:\n{b_body}\n"
        pool.append({"source_id": f"{a}<-{b}", "prompt_body": prompt_body,
                    "positive": a_body, "source_doc": a})
    rng.shuffle(pool)
    return pool


# ---------------------------------------------------------------------------
# transport + parsing
# ---------------------------------------------------------------------------

def cache_path(cache_dir: Path, stratum: str, source_id: str, model: str) -> Path:
    key = hashlib.sha256(f"{source_id}|{model}".encode()).hexdigest()[:32]
    return cache_dir / stratum / f"{key}.json"


def _strip_thinking(text: str) -> str:
    return _THINK_RE.sub("", text).strip()


def _extract_json_query(text: str) -> str | None:
    """Defensive parse (guided_grammar_enabled is off - no server-side JSON
    schema). Tries a direct parse of the first {...} span, then a raw
    "query": "..." regex fallback for a model that wrapped the JSON in
    prose or a markdown fence."""
    text = _strip_thinking(text)
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            obj = json.loads(text[start:end + 1])
            q = obj.get("query")
            if isinstance(q, str) and q.strip():
                return q.strip()
        except (json.JSONDecodeError, AttributeError):
            pass
    m = re.search(r'"query"\s*:\s*"([^"]+)"', text)
    return m.group(1).strip() if m else None


def _should_retry(status: int) -> bool:
    return status == 429 or 500 <= status < 600


def call_omlx(prompt: str, base_url: str, model: str, timeout_s: float) -> str:
    """Optional auth (skip_api_key_verification is on for this server -
    same transport this session verified live and used for local_
    adjudicate.py's Phase -2 repoint)."""
    token = os.environ.get("SYNTH_AUTH_TOKEN") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    last: Exception | None = None
    for attempt in range(_MAX_ATTEMPTS):
        try:
            resp = httpx.post(
                f"{base_url}/v1/chat/completions", headers=headers,
                json={"model": model, "max_tokens": MAX_TOKENS,
                      "temperature": TEMPERATURE, "top_p": TOP_P,
                      "min_p": MIN_P, "repetition_penalty": REPETITION_PENALTY,
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=timeout_s)
            if _should_retry(resp.status_code) and attempt < _MAX_ATTEMPTS - 1:
                time.sleep(5 * (attempt + 1))
                continue
            resp.raise_for_status()
            choices = resp.json().get("choices") or []
            if not choices:
                return ""
            return (choices[0].get("message", {}).get("content") or "").strip()
        except httpx.TransportError as e:
            last = e
            if attempt == _MAX_ATTEMPTS - 1:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"oMLX call failed after {_MAX_ATTEMPTS} attempts: {last}")


# ---------------------------------------------------------------------------
# per-stratum synthesis loop
# ---------------------------------------------------------------------------

def synthesize_stratum(stratum: str, candidates: list[dict], target: int,
                       base_url: str, model: str, cache_dir: Path,
                       timeout_s: float) -> list[dict]:
    preamble = PREAMBLES[stratum]
    rows = []
    n_calls = n_cached = n_filtered = n_parse_fail = 0
    for cand in candidates:
        if len(rows) >= target:
            break
        cpath = cache_path(cache_dir, stratum, cand["source_id"], model)
        if cpath.exists():
            cached = json.loads(cpath.read_text(encoding="utf-8"))
            n_cached += 1
        else:
            prompt = preamble + cand["prompt_body"]
            reply = call_omlx(prompt, base_url, model, timeout_s)
            query = _extract_json_query(reply)
            cached = {"source_id": cand["source_id"], "model": model,
                     "reply": reply, "query": query}
            cpath.parent.mkdir(parents=True, exist_ok=True)
            cpath.write_text(json.dumps(cached, ensure_ascii=False), encoding="utf-8")
            n_calls += 1

        query = cached.get("query")
        if not query:
            n_parse_fail += 1
            continue
        # Stratum comes from the loop, never the model - the model's own
        # `type` field (if it ever emits one) is never read, matching the
        # plan's "self-assigned stratum labels are unreliable" finding.
        if _leaks_metadata(query):
            n_filtered += 1
            continue
        rows.append({"query": query, "positive": cand["positive"],
                    "template": stratum, "source_doc": cand["source_doc"],
                    "model": cached["model"]})

    print(f"[{stratum}] calls={n_calls} cached={n_cached} "
         f"parse_fail={n_parse_fail} leak_filtered={n_filtered} "
         f"kept={len(rows)}/{target}", flush=True)
    return rows


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    ap.add_argument("--chunks", default=str(DEFAULT_CHUNKS))
    ap.add_argument("--lineage", default=str(DEFAULT_LINEAGE))
    ap.add_argument("--holdout", default=str(DEFAULT_HOLDOUT))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    ap.add_argument("--base-url", default=os.environ.get("SYNTH_BASE_URL", DEFAULT_BASE_URL))
    ap.add_argument("--model", default=os.environ.get("SYNTH_MODEL", DEFAULT_MODEL))
    ap.add_argument("--timeout-s", type=float, default=600.0)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--target-numeric-table", type=int, default=TARGETS["numeric_table"])
    ap.add_argument("--target-multi-hop", type=int, default=TARGETS["multi_hop"])
    ap.add_argument("--target-lineage-supersession", type=int,
                    default=TARGETS["lineage_supersession"])
    ap.add_argument("--strata", nargs="+",
                    default=["numeric_table", "multi_hop", "lineage_supersession"],
                    help="run only a subset (e.g. for a resumed/partial run)")
    args = ap.parse_args()

    corpus_records = load_corpus_records(Path(args.corpus))
    chunks_by_doc = load_chunks_by_doc(Path(args.chunks))
    lineage = json.loads(Path(args.lineage).read_text(encoding="utf-8"))
    minable = load_minable_docs(corpus_records, Path(args.holdout))
    cache_dir = Path(args.cache_dir)

    targets = {"numeric_table": args.target_numeric_table,
              "multi_hop": args.target_multi_hop,
              "lineage_supersession": args.target_lineage_supersession}

    all_rows: list[dict] = []
    # Sequential, never interleaved - see module docstring on prefix caching.
    if "numeric_table" in args.strata:
        cands = numeric_table_candidates(chunks_by_doc, minable, args.seed)
        print(f"[numeric_table] candidate pool: {len(cands)}", flush=True)
        all_rows += synthesize_stratum("numeric_table", cands, targets["numeric_table"],
                                       args.base_url, args.model, cache_dir, args.timeout_s)
    if "multi_hop" in args.strata:
        cands = multi_hop_candidates(corpus_records, chunks_by_doc, minable, args.seed)
        print(f"[multi_hop] candidate pool: {len(cands)}", flush=True)
        all_rows += synthesize_stratum("multi_hop", cands, targets["multi_hop"],
                                       args.base_url, args.model, cache_dir, args.timeout_s)
    if "lineage_supersession" in args.strata:
        cands = lineage_supersession_candidates(corpus_records, chunks_by_doc, lineage,
                                                minable, args.seed)
        print(f"[lineage_supersession] candidate pool: {len(cands)}", flush=True)
        all_rows += synthesize_stratum("lineage_supersession", cands,
                                       targets["lineage_supersession"],
                                       args.base_url, args.model, cache_dir, args.timeout_s)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"total synthesized: {len(all_rows)} -> {out_path}")


if __name__ == "__main__":
    main()
