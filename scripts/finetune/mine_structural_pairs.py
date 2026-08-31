"""Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-
bright-dawn.md): mine deterministic, zero-LLM training pairs from corpus
structure. This is the kill-switch phase's entire training signal - if
per-stratum retrieval doesn't move on pairs this cheap, the ~8h LLM
synthesis pass in Phase 1 isn't worth funding.

Four templates, each producing (query, positive_text) rows stamped with
`template` (the stratum proxy - NEVER inferred by a model; see the
metadata-leakage / self-assigned-label defects recorded in the plan's
"Measured facts" section) and `source_doc` (provenance, for the eventual
Phase 2 reranker reuse and for debugging a bad pair back to its origin):

  subject_body        circular `subject` -> a sample of its own body chunks
  heading_section      a detected numbered heading line -> the rest of that
                        chunk's text (same heading regex the chunker itself
                        uses, segment.py's hierarchical_chunk - not a new
                        heuristic)
  citation_context     REF_RE citation context window -> the CITED doc's
                        subject (reuses export_datasets.build_citation_pairs
                        verbatim; only kept when the cited doc resolves
                        in-corpus and is not held out)
  lineage_pair          the superseding/amending circular's subject -> the
                        superseded/amended circular's subject (reuses
                        export_datasets.build_supersession_pairs verbatim;
                        "unrelated" label rows are dropped - not reused as
                        negatives here to keep mining and negative-selection
                        logic decoupled)

Volume is deliberately capped per doc (not "every chunk") to keep this a
cheap spike: subject_body max 3 chunks/circular, heading_section max 5
headings/circular, both seeded samples. citation_context and lineage_pair
are naturally bounded by how many citations/lineage edges exist.

Every template excludes the ~30% holdout slice from
data/finetune/holdout_docs.json (Phase -1's contamination boundary) BOTH as
a query source and as a positive target - a pair citing a held-out doc as
its positive would leak eval-relevant text into training just as much as
one built FROM a held-out doc.

Hard negatives (FlagEmbedding hn_mine.py's range_for_sampling convention):
batch-embed every query against the FROZEN base bge-m3 index (data/index,
pre-fine-tune - this step must run before training, using the base model's
own retrieval geometry), batch-search FAISS for the top ~250 per query,
then for each query keep candidates that are (a) not from the positive's
own document and (b) ranked 2-200 (skip the top-2 - too likely to BE the
positive's paraphrase). One batched embed + one batched FAISS call for the
whole set, not a per-query round trip.

An earlier version also rejected candidates scoring above 95% of the
POSITIVE's own score (an NVIDIA-recipe-style denoise filter, borrowed from
a setting where queries are LLM-synthesized FROM their positive and so are
naturally strong matches under any embedder). Measured on this corpus's
structural pairs (scripts/finetune/_diag_negatives.py) that premise didn't
hold: positive<->query cosine under the UNTRAINED base model is often
modest (median 0.54, some as low as 0.23) precisely because the base model
hasn't learned the relationship yet - that IS what fine-tuning is for. The
filter rejected ~85% of otherwise-valid candidates as "suspiciously close
to the positive" when the real story was a weak positive, and the ~18%
that survived were biased toward cases the base model already handled
well - the opposite of useful training signal. Dropped; see
mine_hard_negatives's own docstring.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/finetune/mine_structural_pairs.py
Output:
    data/finetune/pairs_structural.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from export_datasets import build_citation_pairs, build_supersession_pairs  # noqa: E402
from sebi_rag.ingest_pdf import normalize_circular_number  # noqa: E402

DEFAULT_CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
DEFAULT_CHUNKS = ROOT / "data" / "index" / "chunks.jsonl"
DEFAULT_LINEAGE = ROOT / "data" / "index" / "lineage.json"
DEFAULT_HOLDOUT = ROOT / "data" / "finetune" / "holdout_docs.json"
DEFAULT_OUT = ROOT / "data" / "finetune" / "pairs_structural.jsonl"
DEFAULT_INDEX_DIR = ROOT / "data" / "index"

SEED = 42
MIN_CHUNK_CHARS = 200  # corpus quality floor: 3.1% of chunks are shorter,
                        # degenerate heading-only fragments (nominee-count-
                        # chunker-bug memory) - never use these as positives
MAX_SUBJECT_BODY_PER_DOC = 3
MAX_HEADING_SECTION_PER_DOC = 5

# Same detector the chunker itself uses (segment.py:144, hierarchical_chunk,
# a local variable there - not exported, so mirrored here rather than
# imported). A numbered clause line: "2. Applicability", "5.1) ...".
_HEADING_RE = re.compile(r"^\s*(\d+(\.\d+)*)[.)]\s+\S")

METADATA_LEAK_RE = re.compile(
    r"\b\d{4}-\d{2}-\d{2}\b"                       # ISO dates
    r"|\bSEBI/[A-Z0-9/._()-]+/\d{4}\b"              # SEBI/.../2024-style ids
    r"|\bCIR/[A-Z0-9/._()-]+/\d{4}\b"               # CIR/.../2024-style ids
    r"|\bHO/[A-Z0-9/._()-]+/\d{4}\b",               # HO/.../2024-style ids
    re.IGNORECASE,
)

# Sign-off boilerplate: dry-run on the real corpus found ~9% of
# heading_section positives were pure signature blocks ("Yours faithfully /
# Deputy General Manager / Email id: ...") - real text, zero regulatory
# content, no relation to the paired heading beyond both being the tail end
# of the same document. Checked only against the START of a candidate
# positive (a substantive passage that happens to MENTION a manager's title
# mid-paragraph must not be rejected).
_SIGNOFF_RE = re.compile(
    r"^\s*(Yours (faithfully|sincerely)|(Deputy |Chief |General )*"
    r"(General Manager|Manager)\b|Email\s*id\s*:)",
    re.IGNORECASE,
)


def _is_signoff_boilerplate(text: str) -> bool:
    return bool(_SIGNOFF_RE.match(text))


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def load_corpus_records(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def load_chunks_by_doc(path: Path) -> dict[str, list[dict]]:
    by_doc: dict[str, list[dict]] = defaultdict(list)
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            by_doc[c["doc_id"]].append(c)
    return dict(by_doc)


def load_minable_docs(corpus_records: list[dict], holdout_path: Path) -> set[str]:
    """corpus minus the holdout slice - the full minable universe. NOT the
    same as holdout_docs.json's own "minable_gold_docs" field, which is only
    the golden-adjacent subset of that; structural mining draws from the
    whole corpus."""
    holdout = json.loads(holdout_path.read_text(encoding="utf-8"))
    excluded = set(holdout["holdout_docs"])
    return {r["circular_number"] for r in corpus_records} - excluded


def _leaks_metadata(text: str) -> bool:
    return bool(METADATA_LEAK_RE.search(text))


def _strip_context_header(text: str, doc_id: str) -> str:
    """Every chunk's text is `"{doc_id} | {subject[:120]} | {section}\\n{body}"`
    - F1/ADR-001 contextual enrichment baked in unconditionally by
      hierarchical_chunk (segment.py:130), deliberate for production
      retrieval. Reused verbatim as a training POSITIVE it is exactly the
      metadata-leakage shortcut the plan's live probe flagged: the header
      restates the doc's own subject/circular-number right next to
      whatever query points at it, teaching a string-match shortcut instead
      of semantic retrieval. First line only, matched by doc_id (always
      known per-chunk) rather than reconstructing the full header - a
      missing/reformatted header just leaves text unchanged (safe no-op)."""
    first, _, rest = text.partition("\n")
    if first.startswith(f"{doc_id} | "):
        return rest
    return text


# ---------------------------------------------------------------------------
# template 1: subject <-> body
# ---------------------------------------------------------------------------

def mine_subject_body(corpus_records: list[dict], chunks_by_doc: dict[str, list[dict]],
                      minable: set[str], seed: int = SEED,
                      max_per_doc: int = MAX_SUBJECT_BODY_PER_DOC) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for r in corpus_records:
        doc_id = r["circular_number"]
        subject = (r.get("subject") or "").strip()
        if doc_id not in minable or not subject or _leaks_metadata(subject):
            continue
        candidates = []
        for c in chunks_by_doc.get(doc_id, []):
            if c["section"].endswith("/preamble"):
                continue
            body = _strip_context_header(c["text"], doc_id)
            if len(body) >= MIN_CHUNK_CHARS and not _is_signoff_boilerplate(body):
                candidates.append(body)  # length re-checked AFTER stripping -
                                          # header bulk must not count
        if not candidates:
            continue
        sample = candidates if len(candidates) <= max_per_doc else \
            rng.sample(candidates, max_per_doc)
        for body in sample:
            rows.append({"query": subject, "positive": body,
                        "template": "subject_body", "source_doc": doc_id})
    return rows


# ---------------------------------------------------------------------------
# template 2: heading <-> section
# ---------------------------------------------------------------------------

def _split_heading(text: str) -> tuple[str, str] | None:
    """First line matching the numbered-clause pattern -> (heading, rest).
    None if no heading line is found (e.g. preamble chunks)."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if _HEADING_RE.match(line):
            rest = "\n".join(lines[:i] + lines[i + 1:]).strip()
            return line.strip(), rest
    return None


def mine_heading_section(chunks_by_doc: dict[str, list[dict]], minable: set[str],
                         seed: int = SEED,
                         max_per_doc: int = MAX_HEADING_SECTION_PER_DOC) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for doc_id, chunks in chunks_by_doc.items():
        if doc_id not in minable:
            continue
        pairs = []
        for c in chunks:
            body = _strip_context_header(c["text"], doc_id)  # before heading
            if len(body) < MIN_CHUNK_CHARS:                  # detection, or
                continue                                     # the header
            split = _split_heading(body)                     # line itself
            if split is None:                                # can land in
                continue                                      # "rest"
            heading, rest = split
            if (len(rest) < MIN_CHUNK_CHARS or _leaks_metadata(heading)
                    or _is_signoff_boilerplate(rest)):
                continue
            pairs.append((heading, rest))
        if not pairs:
            continue
        sample = pairs if len(pairs) <= max_per_doc else rng.sample(pairs, max_per_doc)
        for heading, rest in sample:
            rows.append({"query": heading, "positive": rest,
                        "template": "heading_section", "source_doc": doc_id})
    return rows


# ---------------------------------------------------------------------------
# template 3: citation context <-> cited doc
# ---------------------------------------------------------------------------

def mine_citation_context(corpus_records: list[dict], minable: set[str]) -> list[dict]:
    by_norm = {normalize_circular_number(r["circular_number"]): r
               for r in corpus_records}
    raw_pairs = build_citation_pairs(corpus_records)  # reused verbatim
    rows = []
    for p in raw_pairs:
        source, target_norm = p["source_doc_id"], p["normalized_circular_number"]
        target = by_norm.get(target_norm)
        if target is None:
            continue  # cites a doc outside the corpus - nothing to pair against
        target_id = target["circular_number"]
        subject = (target.get("subject") or "").strip()
        # NOTE: the query (context_window) is NOT leak-checked here - unlike
        # subject_body/heading_section, this template's whole point is a
        # window of text that names the cited circular; that citation is
        # the signal, not noise. Only the POSITIVE (the cited doc's own
        # subject) is checked - it should read as a subject line, not
        # itself carry an administrative reference.
        if (source not in minable or target_id not in minable
                or not subject or _leaks_metadata(subject)):
            continue
        rows.append({"query": p["context_window"], "positive": subject,
                    "template": "citation_context", "source_doc": source})
    return rows


# ---------------------------------------------------------------------------
# template 4: lineage (supersedes / amends)
# ---------------------------------------------------------------------------

def mine_lineage_pairs(corpus_records: list[dict], lineage: dict,
                       minable: set[str]) -> list[dict]:
    raw_pairs = build_supersession_pairs(corpus_records, lineage)  # reused verbatim
    rows = []
    for p in raw_pairs:
        if p["label"] == "unrelated":
            continue  # kept only as hard-negative pool material, not here
        a, b = p["circular_a_number"], p["circular_b_number"]
        subj_a, subj_b = (p.get("circular_a_subject") or "").strip(), \
            (p.get("circular_b_subject") or "").strip()
        if a not in minable or b not in minable or not subj_a or not subj_b:
            continue
        rows.append({"query": subj_a, "positive": subj_b,
                    "template": "lineage_pair", "source_doc": a})
    return rows


# ---------------------------------------------------------------------------
# hard-negative mining: batched, vectorized, frozen base index
# ---------------------------------------------------------------------------

def mine_hard_negatives(rows: list[dict], retriever, embedder, *,
                        k: int = 250, rank_lo: int = 2, rank_hi: int = 200,
                        n_neg: int = 5, doc_key: str = "source_doc") -> list[dict]:
    """One batched embed + one batched FAISS search for the whole set - not
    a per-query round trip. Mutates nothing; returns new dicts with `neg`
    populated (rows a query can't find 5 valid negatives for are dropped,
    never silently padded with weak ones).

    doc_key names the field holding "the document the positive text
    actually belongs to", for the same-document exclusion below. Defaults
    to "source_doc" (correct for every mine_structural_pairs.py template -
    positive and source_doc are always the same document there). Phase 1's
    multi_hop rows are the reason this is a parameter, not hardcoded:
    synthesize_queries.py's source_doc is the CITING document, but the
    positive is drawn from the CITED one (positive_doc) - callers over
    synthesized rows must pass doc_key="positive_doc" or same-document
    negatives would silently slip through unexcluded.

    Rank window (2-200) + doc-exclusion only - matches FlagEmbedding's own
    hn_mine.py range_for_sampling convention, cited as this design's source.
    An earlier version also rejected any candidate scoring above 95% of the
    POSITIVE's own score (an NVIDIA-recipe-style denoise filter, borrowed
    from a setting where queries are LLM-synthesized FROM their positive and
    so are naturally strong matches under any embedder). On this corpus's
    structural pairs that premise doesn't hold: query<->positive similarity
    under the UNTRAINED base model is often modest (median cosine 0.54,
    some as low as 0.23 - measured via scripts/finetune/_diag_negatives.py)
    precisely because the base model hasn't learned the relationship yet -
    that's what fine-tuning is for. The relative filter rejected ~85% of
    otherwise-valid candidates as "suspiciously close to the positive" when
    the real story was a weak positive, not a false negative - and the
    ~18% of rows that survived were biased toward cases the base model
    ALREADY handled well, the opposite of useful training signal."""
    if not rows:
        return []
    queries = [r["query"] for r in rows]
    doc_ids = [r[doc_key] for r in rows]

    q_vecs = embedder.encode(queries).astype("float32")
    k = min(k, retriever.dense.index.ntotal)
    _, idx = retriever.dense.index.search(q_vecs, k)  # one batched call

    out = []
    for i, r in enumerate(rows):
        picked: list[str] = []
        for rank, ci in enumerate(idx[i]):
            if ci == -1 or rank < rank_lo or rank > rank_hi:
                continue
            chunk = retriever.chunks[ci]
            if chunk.doc_id == doc_ids[i]:
                continue
            picked.append(_strip_context_header(chunk.text, chunk.doc_id))
            if len(picked) == n_neg:
                break
        if len(picked) == n_neg:
            out.append({**r, "neg": picked})
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    ap.add_argument("--chunks", default=str(DEFAULT_CHUNKS))
    ap.add_argument("--lineage", default=str(DEFAULT_LINEAGE))
    ap.add_argument("--holdout", default=str(DEFAULT_HOLDOUT))
    ap.add_argument("--index-dir", default=str(DEFAULT_INDEX_DIR),
                    help="frozen BASE index for hard-negative mining (must "
                         "predate any fine-tuning)")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--skip-negatives", action="store_true",
                    help="emit positives only, for a fast dry-run / test")
    args = ap.parse_args()

    corpus_records = load_corpus_records(Path(args.corpus))
    chunks_by_doc = load_chunks_by_doc(Path(args.chunks))
    lineage = json.loads(Path(args.lineage).read_text(encoding="utf-8"))
    minable = load_minable_docs(corpus_records, Path(args.holdout))

    rows = []
    rows += mine_subject_body(corpus_records, chunks_by_doc, minable, args.seed)
    rows += mine_heading_section(chunks_by_doc, minable, args.seed)
    rows += mine_citation_context(corpus_records, minable)
    rows += mine_lineage_pairs(corpus_records, lineage, minable)

    by_template = defaultdict(int)
    for r in rows:
        by_template[r["template"]] += 1
    print(f"positives mined: {len(rows)}  by template: {dict(by_template)}")

    if args.skip_negatives:
        final = rows
    else:
        from sebi_rag.api import _embed_kwargs
        from sebi_rag.embeddings import BGEM3Embedder
        from sebi_rag.retrieve import HybridRetriever
        from sebi_rag.settings import Settings

        embedder = BGEM3Embedder(**_embed_kwargs(Settings.load()))
        retriever = HybridRetriever.load(args.index_dir, embedder)
        final = mine_hard_negatives(rows, retriever, embedder)
        print(f"pairs with 5 valid negatives: {len(final)} "
              f"(dropped {len(rows) - len(final)} for insufficient negatives)")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in final:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"-> {out_path}")


if __name__ == "__main__":
    main()
