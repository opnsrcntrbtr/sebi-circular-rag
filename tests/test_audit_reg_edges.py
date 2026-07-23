"""Sampling + scoring for the regulation-edge precision audit."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_reg_edges as A  # noqa: E402

TIERS = ("subject_line", "powers_clause", "body_text")


def _edges(per_tier=40):
    out = []
    for t in TIERS:
        for i in range(per_tier):
            out.append({"source": f"C/{t}/{i}", "target": f"reg-{i}-2020",
                        "relation": "cites", "confidence": "explicit_text",
                        "evidence": t, "clause": None, "count": 1})
    return out


def test_sample_size_is_respected():
    assert len(A.stratified_sample(_edges(), 50, seed=7)) == 50


def test_sample_covers_every_evidence_tier():
    got = {e["evidence"] for e in A.stratified_sample(_edges(), 50, seed=7)}
    assert got == set(TIERS)


def test_sample_is_deterministic_for_a_fixed_seed():
    a = A.stratified_sample(_edges(), 50, seed=7)
    b = A.stratified_sample(_edges(), 50, seed=7)
    assert [e["source"] for e in a] == [e["source"] for e in b]


def test_sample_smaller_than_requested_returns_everything():
    small = _edges(per_tier=3)
    assert len(A.stratified_sample(small, 50, seed=7)) == len(small)


def test_sample_has_no_duplicates():
    s = A.stratified_sample(_edges(), 50, seed=7)
    assert len({(e["source"], e["target"]) for e in s}) == len(s)


def test_thin_tier_gives_its_remainder_to_the_others():
    """A tier with only 2 edges must not cap the sample at 6."""
    edges = [e for e in _edges() if e["evidence"] != "subject_line"]
    edges += [e for e in _edges() if e["evidence"] == "subject_line"][:2]
    assert len(A.stratified_sample(edges, 50, seed=7)) == 50


def test_score_computes_a_clopper_pearson_interval():
    ci = A.score({"a": True, "b": True, "c": False, "d": True})
    assert ci.successes == 3 and ci.n == 4
    assert ci.method == "clopper-pearson"
    assert 0.0 <= ci.lo <= ci.point <= ci.hi <= 1.0


def test_score_with_no_labels_is_vacuous_not_an_error():
    ci = A.score({})
    assert ci.n == 0 and ci.lo == 0.0 and ci.hi == 1.0


def test_perfect_precision_lower_bound_is_below_one():
    ci = A.score({str(i): True for i in range(50)})
    assert ci.point == 1.0
    assert ci.lo < 1.0  # Clopper-Pearson is conservative by design
