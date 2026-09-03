# Preregistration — Gate Stack-Fingerprint Interlock

**Written before implementation.** Design in §1 and decision rule in §3 are fixed as of this
document's commit. No production code has been changed.

## 0. Motivation

`eval/golden/gate_v7.json` currently stores only `{adjudicated_n, derived_at, floors}`
(`scripts/golden_v7/derive_thresholds.py:120-130`). `floors_ok()`
(`scripts/golden_v7/gate_select.py:39`) compares metric values only — it never asks whether the
floors and the measurement being gated describe the same system.

This is not hypothetical: the armed gate is stale *right now*. Floors were derived
`2026-09-02T19:56:21` against chunker `2026-09-01-table-row-merge` (85,131 chunks).
`data/index/meta.json` currently reads `chunker_version: "2026-09-03-toc-long-title-merge"`,
`n: 83752` — two chunker versions and 1,379 chunks later. `retrieve.py:286-295` already warns on
this exact drift at index-load time; the gate has no equivalent, and would report a false
pass/fail against numbers from a system that no longer exists.

`.claude/rules/refusal-criteria.md` states the invalidation rule in prose ("changing the
generator, embedder, corpus, or B′ margin invalidates this table … a category error" — corrected
2026-09-03; reranker is deliberately excluded, see below). `.claude/` is gitignored, so that file
can never be the *enforced* source — this spec generalises the F-01/F-02/F-03 index-identity
interlocks (shipped 2026-09-02, `docs/status.md:1496`) from the index to the gate, using the
tracked `eval/golden/gate_v7.json` as the enforcement point.

**⚠️ Correction to this spec's original draft (2026-09-03, same day):** the design below
originally proposed recording `reranker_model` (from `Settings.load()`) as a fingerprinted axis,
which would have written `"reranker_model": "jina"` into `gate_v7.json` — **factually wrong**,
because `derive_thresholds.py` deliberately never routes through `retrieval_reranker_for` and
always constructs `bge-reranker-v2-m3` regardless of config (`docs/status.md:907`,
`tests/test_rerank_jina_v3.py`). This is an intentional, documented design: the floor baseline is
a fixed, reranker-independent quality bar so a reranker swap in production can't silently lower
the bar it's measured against. §1 below is corrected to record what the script actually
constructs, not the declared config value — repeating the same class of bug this spec exists to
catch, in the spec meant to catch it, would have been exactly backwards.

## 1. Design

**`derive_thresholds.py` writes a `stack` block** into `gate_v7.json` alongside `floors`, sourced
from data the script already loads. Two reranker fields are recorded, deliberately not one: what
the derivation actually constructed (fixed) and what production is configured to run (variable) —
collapsing them into a single field is what caused the 2026-09-02 documentation error this spec
exists partly to prevent a repeat of.

```json
{
  "adjudicated_n": 260,
  "derived_at": "...",
  "floors": { ... },
  "stack": {
    "embed_model": "BAAI/bge-m3",
    "derivation_reranker": "bge-reranker-v2-m3",
    "production_reranker_model": "jina",
    "abstain_threshold": 0.12,
    "chunker_version": "2026-09-01-table-row-merge",
    "corpus_n": 1490,
    "chunk_n": 85131,
    "generator": "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "citation_margin": 0.35,
    "citation_scorer_enabled": true
  }
}
```

`derivation_reranker` is a constant string (`"bge-reranker-v2-m3"`) — it is not read from config,
by design, and `stack_matches()` (below) never compares it against anything: it exists purely as
a self-documenting record so no future reader has to re-derive this fact from the source, the way
this investigation had to. `production_reranker_model` is sourced from `Settings.load().reranker_model`
and recorded for information only — a mismatch between it and what production runs at
*measurement* time is `eval_json.py`'s concern (it already routes through `retrieval_reranker_for`
correctly), not this fingerprint's.

Sources: `data/index/meta.json` (`chunker_version`, chunk `n`), `Settings.load()`
(`embed_model`, `reranker_model`, `abstain_threshold`, `citation_margin`,
`citation_scorer_enabled`, `mlx_model`), `load_records(s.corpus_path)` length (`corpus_n`).

**`stack_matches()` compares only the axes that actually invalidate `derive_thresholds.py`'s
output**: `embed_model`, `chunker_version`, `corpus_n`, `chunk_n`, `generator`, `citation_margin`,
`citation_scorer_enabled`, `abstain_threshold`. **`production_reranker_model` is excluded from the
comparison set on purpose** — the floors are correct precisely when this field differs from
whatever `eval_json.py`'s live stack reports (bge-anchored floor vs. jina-running production is
the intended state, not drift). Comparing it would make this interlock fire a false-positive
"drift" alarm on every single run for as long as production stays on a non-bge reranker, which is
the opposite of what a fingerprint check is for.

**Enforcement lives in the reporting path** (`floors_ok()` / `eval_json.py`), **not**
`select_golden()`. `select_golden` (`gate_select.py:22-36`) fails closed to `golden_v5` on any
parse problem by design — routing a stack mismatch through it would silently swap the *reporting
set* instead of refusing to report pass/fail, which is the opposite of what a fingerprint
mismatch should do. A drifted gate must fail loud, naming the drifted axes, per
`refusal-criteria.md`'s own instruction — not fail quiet into a different golden set.

**New function `stack_matches(gate: dict, live: dict) -> list[str]`** in `gate_select.py`
(alongside `floors_ok`, same import-light module) returning the list of mismatched axis names
(empty = match). `eval_json.py` calls it before reporting pass/fail; on any mismatch it emits the
mismatch list instead of a floors_ok verdict — same "loud refusal" shape the abstention gate
already uses for insufficient evidence.

**Backward compatibility:** a `gate_v7.json` with no `stack` key (i.e. every gate file that
exists today, including the currently-armed one) is treated as **unverifiable**, reported as such
— not as passing. This spec's own landing makes the current armed gate immediately report as
drifted; that is correct behaviour, not a regression introduced by this change. Clearing it
requires a fresh `make golden-v7-gate` run against the live stack (tracked separately as W1.1 in
`docs/superpowers/specs/2026-09-03-architecture-review-w1-diagnostics.md` — see that work's
output before wiring this).

## 2. Endpoints

| role | check | source |
|---|---|---|
| PRIMARY | `stack_matches()` returns `[]` on a gate file just re-derived against the live stack | new unit test in `tests/test_golden_v7_gate.py` |
| PRIMARY | `stack_matches()` returns a non-empty, correctly-named list when one *comparable* axis (e.g. `chunker_version`) is mutated | same test file, synthetic fixture |
| PRIMARY | `stack_matches()` returns `[]` when only `production_reranker_model` differs from the live stack (bge floor vs. jina production is the expected steady state, not drift) | same test file, synthetic fixture |
| GUARDRAIL | `make test` stays green | existing suite |
| GUARDRAIL | `eval_json.py` on the current (stale) `gate_v7.json` reports "unverifiable — no stack fingerprint", not a floors_ok verdict | manual run before/after |

## 3. Decision rule — fixed in advance

Adopt only if **all** hold:
1. `stack_matches()` unit tests pass for both the match and mismatch cases.
2. `eval_json.py`'s reporting path visibly distinguishes three states — verified pass, verified
   fail, and unverifiable (no/mismatched fingerprint) — never collapsing the third into either of
   the first two.
3. `select_golden()` is provably untouched (`git diff` shows no change to `gate_select.py`'s
   `select_golden` function) — the interlock must not alter golden-set resolution.
4. `make test` green.

If any of 1-4 fails → do not wire into `eval_json.py`'s default path; land the `stack`-writing
half of `derive_thresholds.py` alone (harmless, additive) and reopen the enforcement half as its
own follow-up.

## 4. Not permitted after seeing the result

- Routing the fingerprint check through `select_golden()` "for simplicity" — §1 already ruled
  this out with a specific failure mode (silent golden-set swap), not a style preference.
- Treating a `stack`-less gate file as passing "for now" to avoid the immediate drift report this
  spec's own landing causes — that report is the point.
- Widening this spec's scope to also fix the currently-stale gate (that is W1.1, a diagnostic
  re-derivation, tracked separately) — this spec is the detection mechanism only.
