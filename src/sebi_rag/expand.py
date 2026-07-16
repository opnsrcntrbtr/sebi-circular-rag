"""Query-side lexical expansion for BM25 (intervention #2, glossary variant).

SEBI circulars use statutory vocabulary (freeze, dematerialised, rescinded)
where users ask in lay terms (block, electronic, replaced). Appending
statutory synonyms to the sparse-leg query closes the vocabulary gap without
touching the index; the dense leg keeps the raw query. Entries are grounded
in the sparse_vocabulary_miss failures of eval/runs/ft-traces/buckets.md.
"""
from __future__ import annotations

import re

# lay token -> statutory synonyms appended to the BM25 query.
# Keys are single lowercase tokens; values may be multi-word phrases.
GLOSSARY: dict[str, tuple[str, ...]] = {
    # para-freeze: "block all outgoing transactions" vs corpus "freeze"
    "block": ("freeze",),
    "blocked": ("frozen", "freeze"),
    "blocking": ("freezing", "freeze"),
    "unblock": ("unfreeze",),
    "re-enable": ("unfreeze",),
    # probe-par-02: "electronic form" vs corpus "dematerialised"
    "electronic": ("dematerialised", "dematerialized", "demat"),
    "paper": ("physical",),
    "fraction": ("percentage", "per cent"),
    # probe-sup-01: "replaced ... made them void" vs corpus "rescinded"
    "replaced": ("rescinded", "superseded"),
    "replaces": ("rescinds", "supersedes"),
    "void": ("rescinded",),
    "withdrawn": ("rescinded",),
    # probe-tbl-05: "template contract" vs corpus "Model ... Agreement"
    "template": ("model",),
    "contract": ("agreement",),
    # probe-par-01: "papers ... broking licence" vs corpus
    # "documents ... certificate of registration"
    "papers": ("documents",),
    "licence": ("registration", "certificate"),
    "license": ("registration", "certificate"),
    "broking": ("broker", "brokers"),
}

_TOKEN = re.compile(r"[a-z][a-z0-9-]*")


def expand_query(
    query: str, glossary: dict[str, tuple[str, ...]] = GLOSSARY
) -> str:
    """Append statutory synonyms for lay tokens present in `query`.

    Deterministic and additive: the original query is always preserved as a
    prefix, so expansion can only add BM25 candidate terms, never remove any.
    """
    tokens = _TOKEN.findall(query.lower())
    present = set(tokens)
    extra: list[str] = []
    for t in tokens:
        for syn in glossary.get(t, ()):
            for w in syn.lower().split():
                if w not in present:
                    present.add(w)
                    extra.append(w)
    return f"{query} {' '.join(extra)}" if extra else query
