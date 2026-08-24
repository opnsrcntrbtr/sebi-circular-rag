# Preregistration — jina-reranker-v3-mlx vs bge-reranker-v2-m3 (ADR-004)

**Written before execution.** Decision rule in §3 and the not-permitted list in §5 are fixed as
of this document's commit. No arm has been run.

ADR: `docs/adr-004-reranker-candidate-reassessment-2026-08.md` — full rationale, verified sources,
and the Arm 1/Arm 2 decoupling justification live there. This document is the operational
preregistration.

---

## 1. Method

**Single variable per arm.** Arm 1 changes only `pipeline.reranker`; citation scoring, the
generator, the embedder, and the retriever are untouched. Arm 2 (exploratory) changes only the
citation scorer; `pipeline.reranker` stays on the production cross-encoder.

**Arm 1 (primary, decisive):**
```
PYTHONPATH=src python scripts/bench_retrieval.py --rerank --reranker crossencoder \
    --golden eval/golden/golden_v7.jsonl --out eval/runs/reranker-jina-v3-control
PYTHONPATH=src python scripts/bench_retrieval.py --rerank --reranker jina \
    --golden eval/golden/golden_v7.jsonl --out eval/runs/reranker-jina-v3-treatment
```
Endpoints: `recall_at_10`, `ndcg_at_10` (both already emitted by `bench_retrieval.py`'s standard
result artifact). Same golden set, same pool (`--top-n 50` default), same index.

**Arm 2 (exploratory, non-decisive):** if Arm 1 clears §3, a follow-up cohort measurement
(`citation_precision`/`zero_cite`/`citation_recall`) with Jina as `citation_scorer`, modeled on
`scripts/analysis/warrant_scorer_cohort.py`'s three-phase structure. Not run unless Arm 1 passes —
building it before Arm 1 has a result would be spending effort on a question that may not matter.

## 2. Endpoints

| role | metric | source |
|---|---|---|
| PRIMARY | `recall_at_10` | `bench_retrieval.py --rerank` result artifact |
| PRIMARY | `ndcg_at_10` | `bench_retrieval.py --rerank` result artifact |
| GUARDRAIL | `make test` / `eval-asof` / `validate-corpus` | must stay green before any config change |

## 3. Decision rule — fixed in advance

Adopt (proceed to wiring `citation_scorer_backend`/`config.toml` changes) only if **both** hold:

1. **≥10% relative improvement** on `recall_at_10` **or** `ndcg_at_10` over the control arm
   (D1's own bar, `docs/adr-001-architecture-review-2026-07.md`).
2. **No recall regression** — `recall_at_10` does not fall below the control arm's value.

If 1 holds on one metric but 2 fails → **REJECT**. If neither metric clears 10% → **REJECT**,
recorded as rejected, not as "promising, needs tuning" (matching R1's §6 discipline).

## 4. Not permitted after seeing the result

- Lowering the 10% bar because the measured gain is close but under it.
- Reporting Arm 2 (if run) as decisive for Arm 1's adoption — it is exploratory by design (ADR-004
  §Method), because R1 already showed the citation-scoring role can fail independently of the
  retrieval-reranking role.
- Adopting on the paper's BEIR number instead of this benchmark's golden_v7 measurement.
- Skipping the `make test` / `eval-asof` / `validate-corpus` guardrail because Arm 1's numbers look
  good — the guardrail is unconditional, not contingent on the primary endpoint.

## 5. Recorded outcome

Arm 1 ran 2026-08-24: recall@10 +2.42%, nDCG@10 +6.76%, both positive, no regression, neither
clears §3's ≥10% bar. Per §3/§4 as written, this is a **REJECT** (`docs/status.md` 2026-08-24,
"ADR-004 Arm 1: jina-reranker-v3 REJECTED"). Full table there.

## 6. Addendum (2026-08-24, after the §5 result — owner override)

**§3/§4 above are left exactly as preregistered; they are not rewritten.** This addendum records
what happened *after* seeing the §5 result, which §4 itself lists as not permitted for the
analysis to do on its own — the owner did it explicitly, as the project's decider, not as a
finding this document generated.

The owner directed adopting jina-reranker-v3-mlx despite the §3 REJECT, on the rationale recorded
in full in `docs/adr-004-reranker-candidate-reassessment-2026-08.md` §Owner override: the result
is a real, non-regressive, primary-source-verified positive delta, just below a self-imposed
discipline bar rather than a negative or ambiguous one. New criterion in force going forward:
positive delta on recall@10 or nDCG@10, no regression on either — recorded in the ADR, not here,
since it governs future candidates generally and this document is scoped to Jina v3 specifically.

**What this addendum does not do:** it does not retroactively claim §3's bar was met (it wasn't),
does not apply to Arm 2 (still not run — adoption proceeded on Arm 1 alone, by owner decision, not
because Arm 2 became unnecessary), and does not authorize skipping the guardrail (§3's `make test`
/ `eval-asof` / `validate-corpus` requirement is unconditional and was run before this adoption
shipped — see `docs/status.md` 2026-08-24).
