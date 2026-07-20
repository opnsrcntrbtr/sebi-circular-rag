"""Selection of targeted headers (iv10): filter iv9's reused headers down
to 3 failure-adjacent documents, plus one fresh override for probe-sup-04's
out-of-scope chunk. Offline only — generation is an injected callable.
"""
from __future__ import annotations

from sebi_rag.context_headers import HeaderGenerator, filter_targeted_rows


def test_filter_keeps_only_target_doc_rows():
    rows = [
        {"chunk_id": "DOC/A#4.1.1.2. body#3", "header": "h-a", "model": "m"},
        {"chunk_id": "DOC/B#5.1. other#0", "header": "h-b", "model": "m"},
        {"chunk_id": "DOC/A#4.1.1.3. body#4", "header": "h-a2", "model": "m"},
    ]
    out = filter_targeted_rows(rows, {"DOC/A"})
    assert [r["chunk_id"] for r in out] == [
        "DOC/A#4.1.1.2. body#3", "DOC/A#4.1.1.3. body#4",
    ]


def test_filter_with_no_matches_returns_empty():
    rows = [{"chunk_id": "DOC/Z#1#0", "header": "h", "model": "m"}]
    assert filter_targeted_rows(rows, {"DOC/A"}) == []


def test_sup04_override_generated_via_injected_callable():
    calls: list[str] = []

    def fake(prompt: str) -> str:
        calls.append(prompt)
        return "Describes circulars rescinded by serial number on issuance."

    gen = HeaderGenerator(fake)
    header = gen.describe(
        "Master circular for LODR compliance",
        "",
        "4. The circulars issued by SEBI listed at Sl.No. 68-74 in the "
        "Appendix shall stand rescinded with the issuance of this Master "
        "Circular.",
    )
    assert header == "Describes circulars rescinded by serial number on issuance."
    assert len(calls) == 1
