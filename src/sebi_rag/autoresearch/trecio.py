"""Standards-compliant TREC run and qrels emission.

The archived runfiles are not valid TREC: chunk ids embed a section heading
containing spaces, so a run line splits into ~15 fields instead of 6 and
trec_eval cannot read it. `benchmark.read_trec_run` recovers those legacy
files; this module is the forward path that stops producing them.

Circular ids are not automatically whitespace-free either: 3 of 724 are
`SEBI/IMD/MC No.N/...` master circulars carrying a literal space. They are
percent-encoded so a doc id is always exactly one TREC field. The same
encoding MUST be applied to runs and qrels alike — if a run says
`SEBI/IMD/MC%20No.3/10554/2012` and its qrels say `SEBI/IMD/MC No.3/...`,
the pair silently scores zero instead of failing.
"""
from __future__ import annotations

from pathlib import Path

from ..eval_harness import _doc

Rankings = dict[str, list[tuple[str, float]]]


class MalformedChunkId(ValueError):
    """Raised when an id cannot yield a whitespace-free TREC doc id."""


def circular_docid(circular_id: str) -> str:
    """Percent-encode whitespace so a circular id is a single TREC field.

    Reversible because no circular id in the corpus contains `%`; that
    precondition is asserted rather than assumed, so a future corpus that
    breaks it fails loudly instead of producing ambiguous doc ids.
    """
    if "%" in circular_id:
        raise MalformedChunkId(
            f"circular id contains '%', which would make percent-encoding "
            f"ambiguous: {circular_id!r}"
        )
    return "".join(
        f"%{ord(ch):02X}" if ch.isspace() else ch for ch in circular_id
    )


def chunk_docid(chunk_id: str) -> str:
    """Map a chunk id to a whitespace-free TREC doc id.

    `<circular>#<heading with spaces>#<ordinal>` -> `<circular>#<ordinal>`.
    The heading is dropped; `docids.tsv` preserves the full id for reversal.
    """
    if "#" not in chunk_id:
        docid = circular_docid(chunk_id)
    else:
        circular = circular_docid(chunk_id.split("#", 1)[0])
        ordinal = chunk_id.rsplit("#", 1)[1]
        docid = f"{circular}#{ordinal}"
    if any(ch.isspace() for ch in docid):
        raise MalformedChunkId(
            f"doc id still contains whitespace after encoding: {docid!r}"
        )
    return docid


def _write_lines(path: str | Path, lines: list[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(lines), encoding="utf-8")


def write_run_chunk(path: str | Path, run_name: str, rankings: Rankings) -> None:
    """Valid 6-field TREC run at chunk granularity."""
    lines = []
    for qid, ranked in rankings.items():
        for rank, (chunk_id, score) in enumerate(ranked, start=1):
            lines.append(
                f"{qid} Q0 {chunk_docid(chunk_id)} {rank} {score:.8f} {run_name}\n"
            )
    _write_lines(path, lines)


def write_run_doc(path: str | Path, run_name: str, rankings: Rankings) -> None:
    """Valid 6-field TREC run collapsed to circular level.

    Keeps each circular once, at its best (lowest) chunk rank, carrying that
    chunk's score. Ranks are renumbered 1..n so the file is well-formed.
    Relevance judgments in golden_v7 are circular-level, so this — not the
    chunk-level run — is what trec_eval should consume.
    """
    lines = []
    for qid, ranked in rankings.items():
        best: dict[str, float] = {}
        for chunk_id, score in ranked:
            circular = circular_docid(_doc(chunk_id))
            if circular not in best:
                best[circular] = score
        for rank, (circular, score) in enumerate(best.items(), start=1):
            lines.append(f"{qid} Q0 {circular} {rank} {score:.8f} {run_name}\n")
    _write_lines(path, lines)


def write_docids(path: str | Path, rankings: Rankings) -> None:
    """Reverse map `docid -> full chunk id`, so nothing is lost."""
    mapping: dict[str, str] = {}
    for ranked in rankings.values():
        for chunk_id, _ in ranked:
            mapping[chunk_docid(chunk_id)] = chunk_id
    _write_lines(path, [f"{d}\t{c}\n" for d, c in mapping.items()])


def write_trec_qrels(path: str | Path, golden: list[dict]) -> int:
    """Write TREC qrels (`qid 0 docid rel`) at circular level.

    Binary relevance: golden_v7 carries no graded judgments and none are
    invented. Abstain rows contribute nothing, matching per_query_recall.
    Doc ids go through `circular_docid` so they are byte-identical to what
    `write_run_doc` emits. Returns the number of lines written.

    Distinct from `benchmark.write_qrels`, which emits BEIR TSV with a header
    for `export_benchmark`. Both formats are needed; neither replaces the other.
    """
    lines = []
    for row in golden:
        if row.get("abstain"):
            continue
        qid = row["id"]
        for circular in row.get("relevant_circulars", []):
            lines.append(f"{qid} 0 {circular_docid(circular)} 1\n")
    if not lines:
        raise ValueError(
            f"no qrels to write for {path}: every row was abstain or empty"
        )
    _write_lines(path, lines)
    return len(lines)
