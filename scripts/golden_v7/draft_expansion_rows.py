"""LLM-assisted query drafting for the golden-set-power expansion (2026-09-15).

Reads mined candidates from eval/golden/v7_annotations/candidates_expansion_2026-09-15/,
drafts a golden_v7-schema row per candidate via the local oMLX server (same transport/
calling pattern as scripts/finetune/synthesize_queries.py's call_omlx), and writes to a
NEW staging file - never directly into the live eval/golden/golden_v7.jsonl. Merge into
the live set is a separate, later, explicit step (docs/superpowers/specs/
2026-09-01-golden-set-power.md; approved plan in .claude/plans/ultra-synchronous-pony.md).

Design (approved by user before running, see plan/chat record):
- Per-stratum prompt grounded in the specific mined candidate, not free-generated.
- Output schema matches golden_v7's actual row fields (id, query, relevant_circulars,
  relevant_chunks, answer_contains, must_contain, must_not_contain, abstain, task_type,
  difficulty, expected_citation_level, rationale, label_source, review_status, as_of,
  must_not_cite, label_tier).
- label_source: "27b-single-leg-draft" (single-leg adjudication - gemini_adjudicate.py is
  on hold, no paid API spend authorized per the funding decision).
- review_status: "draft" - NOT "adjudicated". local_adjudicate.py must still score these
  before they carry any weight; this script only drafts the query, it does not adjudicate.

This is a SAMPLE-GENERATION script for review, not the full ~616-row run - see --limit.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.lineage import load_records  # noqa: E402

CANDIDATES_DIR = ROOT / "eval" / "golden" / "v7_annotations" / "candidates_expansion_2026-09-15"
DEFAULT_OUT = ROOT / "eval" / "golden" / "v7_annotations" / "draft_rows_expansion_2026-09-15.jsonl"
DEFAULT_BASE_URL = "http://127.0.0.1:8001"
# Matches local_adjudicate.py's DEFAULT_MODEL constant, not the server's exact model id
# (drifted to "Swift-Qwen3.8-27b-oQ4e-mtp") - overridable via --model for this sample run.
DEFAULT_MODEL = "Qwen3.8-27B-oQ4e-mtp"
TEMPERATURE = 0.4  # lower than synthesize_queries.py's 0.6 - drafting a precise eval
                    # question (with an exact-answer constraint) needs less creative
                    # variance than synthesizing training-pair queries did.
TOP_P = 0.9
MIN_P = 0.01
REPETITION_PENALTY = 1.05
MAX_TOKENS = 2500  # raised 500 -> 1500 -> 2500: the substitute 35B model's untagged
                    # "thinking" preamble alone ran past 800 tokens for a single-doc
                    # prompt, and past 1500 for multi_hop's two-document input
                    # tokens without reaching a terminal answer (see _extract_json)
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)


def _strip_thinking(text: str) -> str:
    return _THINK_RE.sub("", text).strip()


_PLACEHOLDER_RE = re.compile(r"^\.{2,}$|^\.$")


def _is_placeholder(s: str) -> bool:
    """Reject a literal echo of this script's own prompt template - "query": "..." -
    which the second sample round surfaced: the model returned the unfilled template
    verbatim as its "final answer" rather than a real draft. bool("...") is truthy, so
    the earlier "obj.get('query')" truthiness check alone let this through silently."""
    s = s.strip().strip('"').strip()
    return (not s) or bool(_PLACEHOLDER_RE.match(s)) or s.upper() in ("TBD", "TODO", "N/A")


def _extract_json(text: str) -> dict | None:
    """Scan for the LAST balanced {...} span that both parses and has a real (non-
    placeholder) "query" key, scanning right-to-left. Needed because this sample run's
    substitute model (Qwen3.6-35B, not the 27B local_adjudicate.py normally pins) emits
    an untagged "thinking" preamble with repeated draft/self-correction JSON snippets
    before its final answer - a naive first-{-to-last-} span spans the whole messy
    trace and never parses; the model's actual terminal answer is usually the last
    valid one, but "valid" must also exclude a placeholder echo (see _is_placeholder)."""
    text = _strip_thinking(text)
    closes = [i for i, ch in enumerate(text) if ch == "}"]
    for end in reversed(closes):
        depth = 0
        for start in range(end, -1, -1):
            if text[start] == "}":
                depth += 1
            elif text[start] == "{":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start:end + 1])
                    except json.JSONDecodeError:
                        break
                    query = obj.get("query") if isinstance(obj, dict) else None
                    if isinstance(query, str) and not _is_placeholder(query):
                        return obj
                    break
    return None


def call_omlx(prompt: str, base_url: str, model: str, timeout_s: float = 120.0) -> str:
    token = os.environ.get("SYNTH_AUTH_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    for attempt in range(4):
        try:
            resp = httpx.post(
                f"{base_url}/v1/chat/completions", headers=headers,
                json={"model": model, "max_tokens": MAX_TOKENS,
                      "temperature": TEMPERATURE, "top_p": TOP_P,
                      "min_p": MIN_P, "repetition_penalty": REPETITION_PENALTY,
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=timeout_s)
            if resp.status_code in (429,) or 500 <= resp.status_code < 600:
                if attempt < 3:
                    time.sleep(5 * (attempt + 1))
                    continue
            resp.raise_for_status()
            choices = resp.json().get("choices") or []
            return (choices[0].get("message", {}).get("content") or "").strip() if choices else ""
        except httpx.TransportError:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
    return ""


def build_numeric_table_prompt(cand: dict) -> str:
    return (
        "You are drafting one evaluation question for a legal-domain retrieval system "
        "over Indian SEBI (Securities and Exchange Board of India) circulars.\n\n"
        f'Excerpt from circular "{cand["doc"]}" (subject: "{cand["subject"]}"):\n---\n'
        f'{cand["text"][:2000]}\n---\n\n'
        "Draft ONE specific factual question whose answer is a number, percentage, "
        "amount, or time period explicitly stated in this excerpt. The question must be "
        "answerable ONLY from this excerpt's own text (not general knowledge), phrased "
        "the way a compliance professional would ask it, with a short, unambiguous answer.\n\n"
        "Reply as JSON only, no other text:\n"
        '{"query": "...", "answer_contains": "<the specific figure, as it appears in the '
        'text>", "must_contain": ["<key term from the answer>"], '
        '"rationale": "<one sentence: what in the excerpt supports this answer>"}'
    )


def build_lineage_supersession_prompt(cand: dict, old_subject: str, new_subject: str) -> str:
    return (
        "You are drafting one evaluation question for a legal-domain retrieval system "
        "over Indian SEBI circulars, testing correct handling of regulatory supersession.\n\n"
        f'Circular "{cand["old"]}" (issued {cand["old_date"]}, subject: "{old_subject}") '
        f'was later superseded by circular "{cand["new"]}" (issued {cand["new_date"]}, '
        f'subject: "{new_subject}").\n\n'
        "Draft ONE question a practitioner might ask about this topic TODAY, phrased so "
        "that a correct answer must cite the CURRENT governing circular "
        f'("{cand["new"]}"), not the superseded one. Do not name either circular number '
        "in the question itself - ask about the topic/subject, the way a practitioner "
        "who does not already know the citation would.\n\n"
        "Reply as JSON only, no other text:\n"
        '{"query": "...", "rationale": "<one sentence: why the answer must be the '
        'newer circular>"}'
    )


def build_title_direct_prompt(cand: dict) -> str:
    return (
        "You are drafting one evaluation question for a legal-domain retrieval system "
        "over Indian SEBI circulars.\n\n"
        f'Circular "{cand["circular_number"]}" has subject line: "{cand["subject"]}"\n\n'
        "Draft ONE short natural-language query a practitioner would type to find this "
        "circular - paraphrase the subject line, do not copy it verbatim, and do not "
        "include the circular number itself.\n\n"
        "Reply as JSON only, no other text:\n"
        '{"query": "...", "rationale": "<one sentence>"}'
    )


def build_body_paraphrase_prompt(cand: dict) -> str:
    return (
        "You are drafting one evaluation question for a legal-domain retrieval system "
        "over Indian SEBI circulars.\n\n"
        f'Excerpt from circular "{cand["doc"]}":\n---\n{cand["text"][:2000]}\n---\n\n'
        "Draft ONE question whose answer is contained in this excerpt, phrased as a "
        "PARAPHRASE (different wording, not the excerpt's own sentence structure or "
        "key phrases) - testing whether a retrieval system can match meaning, not just "
        "keywords.\n\n"
        "Reply as JSON only, no other text:\n"
        '{"query": "...", "answer_contains": "<short phrase from the excerpt that '
        'answers it>", "rationale": "<one sentence>"}'
    )


def build_multi_hop_prompt(cand: dict) -> str:
    return (
        "You are drafting one evaluation question for a legal-domain retrieval system "
        "over Indian SEBI circulars, testing multi-document synthesis.\n\n"
        f'Circular A ("{cand["a"]}"):\n---\n{cand["subject_a"][:1200]}\n---\n\n'
        f'Circular B ("{cand["b"]}"):\n---\n{cand["subject_b"][:1200]}\n---\n\n'
        "These two circulars are linked (e.g. one supersedes, amends, or extends the "
        "other's provisions). Ignore any letterhead, signature block, or contact "
        "details in the excerpts - focus only on the substantive regulatory content. "
        "Draft ONE question that requires information from BOTH circulars to answer "
        "correctly - a question answerable from only one of them is not multi-hop.\n\n"
        "Reply as JSON only, no other text:\n"
        '{"query": "...", "rationale": "<one sentence: why both circulars are needed>"}'
    )


def build_repealed_basis_prompt(cand: dict) -> str:
    regs = ", ".join(cand.get("regulations") or []) or "an unspecified regulation"
    return (
        "You are drafting one evaluation question for a legal-domain retrieval system "
        "over Indian SEBI circulars, testing correct handling of a REPEALED regulatory "
        "basis.\n\n"
        f'Circular "{cand["circular_number"]}" (subject: "{cand["subject"]}") cites '
        f'{regs} as its regulatory basis, and that basis has since been repealed.\n\n'
        "Draft ONE question that asks whether this circular's underlying regulatory "
        "basis is still in force - phrased the way a practitioner checking current "
        "validity would ask it, not naming the circular number itself.\n\n"
        "Reply as JSON only, no other text:\n"
        '{"query": "...", "rationale": "<one sentence>"}'
    )


def build_hard_negative_prompt(cand: dict) -> str:
    near_docs = ", ".join(h["doc"] for h in cand.get("top_hits", [])) or "none"
    return (
        "You are drafting one evaluation question for a legal-domain retrieval system "
        "over Indian SEBI circulars, testing correct ABSTENTION.\n\n"
        f'Topic: "{cand["topic"]}"\n\n'
        "This topic sounds plausibly SEBI-adjacent but is NOT governed by any circular "
        "in this corpus (the nearest BM25 matches are merely topically related, not "
        f"governing: {near_docs}). Draft ONE question about this topic phrased the way "
        "a practitioner would naturally ask it - the correct system behavior is to "
        "abstain (answer 'I don't know'), not cite one of the near-match documents.\n\n"
        "Reply as JSON only, no other text:\n"
        '{"query": "...", "rationale": "<one sentence: why no circular governs this>"}'
    )


def build_far_negative_prompt(cand: dict) -> str:
    return (
        "Draft ONE natural-language question about this topic, unrelated to Indian "
        f'securities regulation: "{cand["topic"]}"\n\n'
        "This is a negative-control test case for a SEBI-circular retrieval system - "
        "the correct behavior is to abstain, since the topic has nothing to do with "
        "SEBI or securities regulation.\n\n"
        "Reply as JSON only, no other text:\n"
        '{"query": "...", "rationale": "one sentence"}'
    )


def draft_row(row_id: str, stratum: str, query: str, extra: dict) -> dict:
    base = {
        "id": row_id, "query": query,
        "relevant_circulars": [], "relevant_chunks": [],
        "answer_contains": "", "must_contain": [], "must_not_contain": [],
        "abstain": False, "task_type": stratum, "difficulty": "medium",
        "expected_citation_level": "circular",
        "rationale": "", "label_source": "27b-single-leg-draft",
        "review_status": "draft", "as_of": None, "must_not_cite": [], "label_tier": "draft",
    }
    base.update(extra)
    return base


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--strata",
        default=("title_direct,body_paraphrase,numeric_table,lineage_supersession,"
                 "multi_hop,repealed_basis,hard_negative,far_negative"),
        help="comma-separated stratum names to sample from")
    ap.add_argument("--limit", type=int, default=2, help="rows per stratum for this sample")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--corpus", default=str(ROOT / "data" / "corpus" / "circulars.jsonl"))
    args = ap.parse_args()

    strata = [s.strip() for s in args.strata.split(",") if s.strip()]
    out_rows = []

    corpus_by_id: dict[str, dict] = {}
    if "lineage_supersession" in strata:
        recs = load_records(args.corpus)
        corpus_by_id = {r["circular_number"]: r for r in recs}

    for stratum in strata:
        path = CANDIDATES_DIR / f"{stratum}.jsonl"
        cands = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, cand in enumerate(cands[:args.limit]):
            row_id = f"exp-{stratum}-{i:03d}"
            if stratum == "title_direct":
                prompt = build_title_direct_prompt(cand)
            elif stratum == "body_paraphrase":
                prompt = build_body_paraphrase_prompt(cand)
            elif stratum == "numeric_table":
                prompt = build_numeric_table_prompt(cand)
            elif stratum == "lineage_supersession":
                old_subj = corpus_by_id.get(cand["old"], {}).get("subject", "")
                new_subj = corpus_by_id.get(cand["new"], {}).get("subject", "")
                prompt = build_lineage_supersession_prompt(cand, old_subj, new_subj)
            elif stratum == "multi_hop":
                prompt = build_multi_hop_prompt(cand)
            elif stratum == "repealed_basis":
                prompt = build_repealed_basis_prompt(cand)
            elif stratum == "hard_negative":
                prompt = build_hard_negative_prompt(cand)
            elif stratum == "far_negative":
                prompt = build_far_negative_prompt(cand)
            else:
                print(f"skip {stratum}: no prompt builder for this sample run", file=sys.stderr)
                continue

            raw = call_omlx(prompt, args.base_url, args.model)
            parsed = _extract_json(raw)
            if not parsed or not parsed.get("query"):
                print(f"FAILED to parse {row_id}: {raw[:200]!r}", file=sys.stderr)
                continue

            extra = {"query": parsed["query"], "rationale": parsed.get("rationale", "")}
            if stratum == "title_direct":
                extra["relevant_circulars"] = [cand["circular_number"]]
            elif stratum == "body_paraphrase":
                extra["answer_contains"] = parsed.get("answer_contains", "")
                extra["relevant_circulars"] = [cand["doc"]]
                extra["relevant_chunks"] = [{"doc": cand["doc"], "quote": cand["text"][:300]}]
            elif stratum == "numeric_table":
                extra["answer_contains"] = parsed.get("answer_contains", "")
                extra["must_contain"] = parsed.get("must_contain", [])
                extra["relevant_circulars"] = [cand["doc"]]
                extra["relevant_chunks"] = [{"doc": cand["doc"], "quote": cand["text"][:300]}]
            elif stratum == "lineage_supersession":
                extra["relevant_circulars"] = [cand["new"]]
                extra["must_not_cite"] = [cand["old"]]
                extra["as_of"] = None  # "today" framing per the prompt
            elif stratum == "multi_hop":
                extra["relevant_circulars"] = [cand["a"], cand["b"]]
            elif stratum == "repealed_basis":
                extra["relevant_circulars"] = [cand["circular_number"]]
                extra["difficulty"] = "hard"
            elif stratum in ("hard_negative", "far_negative"):
                extra["abstain"] = True
                extra["difficulty"] = "hard" if stratum == "hard_negative" else "easy"
                if stratum == "hard_negative":
                    extra["must_not_cite"] = [h["doc"] for h in cand.get("top_hits", [])]

            row = draft_row(row_id, stratum, parsed["query"], extra)
            out_rows.append(row)
            print(f"{row_id}: {row['query']}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(out_rows)} draft rows to {out_path}")


if __name__ == "__main__":
    main()
