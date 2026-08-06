# Diagnosis + Remediation: Golden-v7 Eval "Critical Issues"

**Date:** 2026-08-03
**Status:** Diagnosis complete, decisions locked. Option A no-op confirmed; B′ deferred pending implementation
**Method:** systematic-debugging (root cause before fix) + live MLX probe

## TL;DR

All three "critical issues" are **measurement artifacts**, not retrieval/generation
quality defects. Issues 1 & 2 share one root cause. Issue 3's fix-in-progress
(Option A) is a **100% no-op in production**, proven by probe.

---

## Issue 1 — Low κ across 6 strata (numeric_table 0%, title_direct 8%, multi_hop 7.7%, lineage 21%, body_paraphrase 27%, repealed_basis 31%)

- **Root cause:** κ scored on the WRONG unit. `cohen_kappa()` (`scripts/golden_v7/agreement.py:101`)
  and `_stratum_kappas()` (`:304`) compare **exact `frozenset(governing)` chunk-id sets**
  (`_label`, `:34`). The pipeline's real agreement unit is the **provision** —
  `_confirms_claude()` (`:60`) accepts exact-set OR containment OR span-quote match.
  Master circulars repeat a clause across body/annexure/FAQ chunks; the harness grades
  every quote-containing chunk as gold, so same-provision / different-chunk-copy reads as
  total disagreement. Docstring (`:68-71`): exact-set ~10% vs provision-level ~60% for BOTH
  external families. Compounded by the **kappa base-rate paradox** (skewed strata like
  numeric_table → pe inflates → κ→0 despite high raw agreement). `_render_report()` (`:358-363`)
  already documents κ is *deliberately* stricter than promotion.
- **Not a bug in retrieval/labeling** — a reporting-unit choice.

## Issue 2 — Claude-label accuracy 28.9% (48/166 vs externals)

- **Root cause:** SAME as Issue 1. `_claude_accuracy_ci()` (`agreement.py:310-329`) counts
  success only on exact frozenset equality (`:327`), ignoring `_confirms_claude()`.
  Proof it's an artifact: 150/150 external rows PROMOTED at provision level (status.md:149)
  while exact-set accuracy reads 28.9%. The gap IS the artifact.

## Issue 3 — Citation precision 0.177 → 0.119 after top_k 5→10

- **3a (documented tradeoff):** mechanical "cite every context" + more slots = more noise.
- **3b (live defect):** Option A (selective citations) is implemented uncommitted
  (`generate.py:446-455`) but DEFEATED two ways:
  - `ExtractiveStubGenerator.generate()` (`generate.py:99-102`) bracket-cites ALL contexts
    → eval parser re-extracts all → identical to mechanical. Every golden-eval script uses
    the stub. Eval-parity spec (`2026-08-03-eval-parity-research.md:54-64`) prescribed the
    stub cite only the TOP context; implementation did the opposite.
  - **PROBE (real MLXGenerator, 50 golden rows, top_k=10): 48/48 answered rows emit ZERO
    parseable bracket citations → 100% fallback to `[c.id for c in contexts]`
    (`generate.py:455`).** Qwen2.5-1.5B-Instruct-4bit does not self-cite despite the prompt
    asking (`_grounded_prompt`, `generate.py:295`). Option A is a no-op in production too.
    (Probe: `scratchpad/probe_fallback.py`.)
- **3c (coherence defect):** code has Option A live; `selective-citations-design.md` says
  "implemented"; status.md:193 + `citation-precision-drop-analysis.md` say "deferred."

---

## Decisions (locked 2026-08-03)

- **Issues 1+2:** ADD provision-level agreement (reuse `_confirms_claude`) AND a
  prevalence-robust coefficient (Gwet AC1 or PABAK) per stratum; KEEP exact-set κ as a
  secondary honesty column. Report-only, no pipeline/gate change.
- **Issue 3 → Option B′ (post-hoc NLI filtering).** Prompt-based self-citation (Option A)
  cannot work at 1.5B (100% fallback). Use the existing `CrossEncoderReranker` to score each
  context vs the answer text and drop low-entailment citations. **Model-agnostic** → stub and
  MLX behave identically → eval matches production. Then re-derive gate floors and re-arm.
| # | Task | Files | Effort | Gate |
|---|---|---|---|---|
| ~~1~~ | ~~Reconcile κ: score on provision-level containment, not exact chunk-id sets~~ | ~~`scripts/golden_v7/agreement.py` (`_stratum_kappas`, `_label`)~~ | ~~~0.5d~~ | ~~None (measurement fix)~~ |
| 2 | Implement B′: post-hoc cross-encoder citation filter in `answer_with_abstention()` | ~~`src/sebi_rag/generate.py`, `scripts/golden_v7/derive_thresholds.py`~~ | ~~~1.5d~~ | **med** (re-arms gate) |
| ~~3~~ | ~~Reconcile docs: Option A was a no-op; record B′ as the real fix~~ | ~~`docs/status.md`, `2026-08-03-selective-citations-design.md`~~ | ~~~0.25d~~ | **none** |
| 4 | Implement B′: update `ExtractiveStubGenerator` for cross-encoder scoring parity | `src/sebi_rag/generate.py`, `scripts/eval_json.py` | ~0.5d | none (measurement parity) |
| 5 | Re-run `make eval-asof golden_v7` after B′ to verify gate still passes | `eval/runs/`, `eval/golden/gate_v7.json` | ~0.25d | **high** (gate re-arm) |

**Order rationale:** #1 removes 2/3 of the alarm at zero risk. #2 is the only substantive
code fix and perturbs the armed gate. #3 is bookkeeping gated on #2.

## Constraints honored
- No CircularMeta fields added. No `*_spaces.py` touched. B′ reuses existing cross-encoder
  (no new model). 640 tests must stay green; #1 and #2 add tests.
