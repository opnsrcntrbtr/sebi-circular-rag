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
