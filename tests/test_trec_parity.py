"""Prove the internal retrieval metrics are the standard ones.

Skips unless the optional `eval` extra is installed:
    uv pip install -e '.[eval]'    # or: make trec-parity
"""
import pytest

ir_measures = pytest.importorskip(
    "ir_measures",
    reason="optional [eval] extra not installed; run `make trec-parity`",
)

from sebi_rag.autoresearch.trecio import write_run_doc, write_trec_qrels  # noqa: E402
from sebi_rag.eval import mrr, ndcg_at_k, recall_at_k  # noqa: E402

GOLDEN = [
    {"id": "q1", "abstain": False, "relevant_circulars": ["SEBI/A/2023/1", "SEBI/D/2023/4"]},
    {"id": "q2", "abstain": False, "relevant_circulars": ["SEBI/C/2023/3"]},
    {"id": "q3", "abstain": True, "relevant_circulars": []},
]

RANKINGS = {
    "q1": [
        ("SEBI/B/2023/2#h#0", 0.90),
        ("SEBI/A/2023/1#h#1", 0.80),
        ("SEBI/E/2023/5#h#2", 0.70),
    ],
    "q2": [
        ("SEBI/C/2023/3#h#0", 0.95),
        ("SEBI/B/2023/2#h#1", 0.60),
    ],
}


@pytest.fixture
def artifacts(tmp_path):
    run = tmp_path / "run.doc.trec"
    qrels = tmp_path / "test.qrels"
    write_run_doc(run, "parity", RANKINGS)
    write_trec_qrels(qrels, GOLDEN)
    return qrels, run


def _standard(qrels, run, measure_str):
    measure = ir_measures.parse_measure(measure_str)
    return ir_measures.calc_aggregate(
        [measure],
        ir_measures.read_trec_qrels(str(qrels)),
        ir_measures.read_trec_run(str(run)),
    )[measure]


def _internal(fn):
    vals = []
    for row in GOLDEN:
        if row["abstain"]:
            continue
        ranked = [c.split("#", 1)[0] for c, _ in RANKINGS[row["id"]]]
        seen, docs = set(), []
        for d in ranked:
            if d not in seen:
                seen.add(d)
                docs.append(d)
        vals.append(fn(docs, set(row["relevant_circulars"])))
    return sum(vals) / len(vals)


def test_recall_at_10_matches_ir_measures(artifacts):
    qrels, run = artifacts
    assert _internal(lambda d, r: recall_at_k(d, r, 10)) == pytest.approx(
        _standard(qrels, run, "R@10"), abs=1e-9
    )


def test_mrr_matches_ir_measures(artifacts):
    qrels, run = artifacts
    assert _internal(mrr) == pytest.approx(_standard(qrels, run, "RR"), abs=1e-9)


def test_ndcg_at_10_matches_ir_measures(artifacts):
    qrels, run = artifacts
    assert _internal(lambda d, r: ndcg_at_k(d, r, 10)) == pytest.approx(
        _standard(qrels, run, "nDCG@10"), abs=1e-9
    )
