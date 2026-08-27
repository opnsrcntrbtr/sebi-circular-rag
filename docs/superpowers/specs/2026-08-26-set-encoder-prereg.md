# Preregistration — Set-Encoder Reranker Benchmark (webis/set-encoder-base via lightning-ir)

**Written before execution.** Decision rule in §3 and the not-permitted list in §4 are fixed as of
this document's commit. No golden_v7 query has been scored by any arm at the time of this commit —
§0 documents environment/API verification only (whether the tool under test can load and run at
all), which is a qualitatively different thing from observing a recall/ndcg comparison result, and
is disclosed here for the same reason `2026-08-26-hybrid-gate-prereg.md` §0 disclosed a stale-value
correction before its own decision rule: verify, don't assume, and record what was checked before
locking the rule that governs the actual measurement. Task 2 of
`docs/superpowers/plans/2026-08-26-hybrid-gate-and-set-encoder.md` (also
`.superpowers/sdd/2026-08-26-hybrid-gate-and-set-encoder/task-2-brief.md`).

Report/results artifact (not this doc): this document's own §5, plus
`docs/status.md` entry and the diagnostic transcript captured during §0.

## 0. Environment verification (performed before writing §3's decision rule)

**Model and package, as specified:** `webis/set-encoder-base` (Schlatt et al., ECIR 2025,
arXiv:2404.06912; Apache 2.0; 0.1B params, electra-base-discriminator backbone), via the vendor's
own inference package `lightning-ir` (`pip install lightning-ir`, github.com/webis-de/lightning-ir).

**API shape, verified by inspection** (not assumed from the brief's sketch): `CrossEncoderModule`
does not expose a `.score()` that returns a plain list of floats. Its actual signature is
`score(queries: Sequence[str] | str, docs: Sequence[Sequence[str]] | Sequence[str]) ->
LightningIROutput`, where `LightningIROutput.scores` is a `torch.Tensor`. `SetEncoderReranker`
(`src/sebi_rag/rerank.py`) calls `.detach().to("cpu").float().tolist()` on that tensor before
pairing with candidates — the brief's sketch (`scores = model.score(...)` as if it were already a
list) does not match the real API and was corrected here, not shipped as written.

**Load failure — verified, reproduced twice, through two independent code paths:**

1. `PYTHONPATH=src python3 -c "from lightning_ir import CrossEncoderModule;
   CrossEncoderModule('webis/set-encoder-base')"` — direct API probe.
2. `PYTHONPATH=src python3 scripts/bench_retrieval.py --reranker set-encoder --rerank
   --index-dir <main-repo>/data/index --golden <main-repo>/eval/golden/golden_v7.jsonl` — the actual
   shipped code path (`SetEncoderReranker.__init__`, `rerank.py:271`).

Both raise the identical traceback at model-construction time (before any query is scored):

```
File ".../lightning_ir/models/cross_encoders/mono.py", line 90, in __init__
    if self.config.scoring_strategy == "mono":
File ".../transformers/integrations/heterogeneity/configuration_utils.py", line 280, in __getattribute__
    return super().__getattribute__(key)
AttributeError: 'SetEncoderElectraConfig' object has no attribute 'scoring_strategy'.
```

**Root cause, isolated by inspection of `lightning_ir`'s source:** `webis/set-encoder-base`'s
published `config.json` records `"transformers_version": "4.41.2"` and does not contain a
`scoring_strategy` key (nor `_bert_pool`, `use_adapter`, `adapter_config`,
`pretrained_adapter_name_or_path` — all attributes `lightning_ir`'s `MonoConfig.__init__` /
`LightningIRConfig.__init__` set as Python instance attributes, with defaults, but never persist to
`config.json` when they equal the default). `transformers` is not a direct dependency of this
project -- it is pulled in transitively via `sentence-transformers>=5.6.0` (`pyproject.toml`), and
resolves to `5.14.1` in `uv.lock` (not an explicit/direct pin). Under that resolved 5.14.1, the
dynamically-composed config class for a custom `model_type` + `backbone_model_type` pair
(`SetEncoderElectraConfig`) is built through
`transformers.integrations.heterogeneity.configuration_utils` — a mechanism that reconstructs the
object from the raw JSON dict without re-running `MonoConfig.__init__`'s Python-level default
assignments, so any attribute set only inside `__init__` (not serialized to `config.json`) is
simply absent on the resulting object. Patching the five known-missing config attributes as class
defaults (a narrow experiment, not shipped) gets the model itself to construct, but the identical
class of bug recurs one layer down in tokenizer loading:
`lightning_ir/base/tokenizer.py:104: BackboneTokenizer = BackboneTokenizers[1]` assumes
`transformers.TOKENIZER_MAPPING[...]` returns a `(slow_cls, fast_cls)` tuple; under the resolved
transformers 5.14.1 it returns a single class, raising `TypeError: type 'BertTokenizer' is not
subscriptable`.
Two independent subsystems (config composition, tokenizer registry) both break — this is a
structural `lightning-ir` × `transformers 5.x` incompatibility, not a single missing kwarg.

**Reproduced on both releases — not a stale-pip-version issue:** identical failure on PyPI
`lightning-ir==0.0.6` and on `github.com/webis-de/lightning-ir@03e8def` (main, installed via
`pip install git+https://github.com/webis-de/lightning-ir`, same version tag 0.0.6 — main has not
cut a newer release addressing this).

**Why no monkeypatch ships:** the config-attribute gap alone is patchable (five class-level
defaults), but the tokenizer-registry break requires patching `transformers`' own internal
`TOKENIZER_MAPPING` lookup protocol, which is functionality this project does not own and a
different resolved `transformers` major version could change again without notice. Shipping a chain
of version-pinned monkeypatches into `rerank.py` to work around an upstream library's incompatibility
with the `transformers` version this project resolves transitively (via `sentence-transformers`,
locked at 5.14.1 in `uv.lock` — not a direct/explicit pin) — for a report-only, non-adopted benchmark
candidate — was judged disproportionate and fragile; `SetEncoderReranker` is implemented correctly
against the documented/verified API contract instead, so it is ready to run unmodified once
`lightning-ir` ships a `transformers`-5.x-compatible release (or this project's `sentence-transformers`
version changes and pulls in a different transitive `transformers` resolution, itself a separate,
unrelated decision).

**This changes the preregistered outcome space, decided here before any golden_v7 query is
scored:** §3 below adds a third outcome branch, BLOCKED, alongside the usual ADOPT/NULL, for exactly
this situation — a candidate that cannot complete a single inference call in this project's current
environment. This is a method-verification finding (can the tool run at all), not a peek at the
comparison's result (which requires the tool to run first).

## 1. Method

**Pipeline under test:** `SetEncoderReranker` (`src/sebi_rag/rerank.py`), wrapping
`lightning_ir.CrossEncoderModule("webis/set-encoder-base")`, CPU by default (mirrors
`CrossEncoderReranker`'s own documented reason — MPS segfaults CrossEncoder-family models on this
hardware; MPS was not independently verified stable for lightning-ir here since load never reached
inference, so CPU stays the safe default per the brief's instruction).

**Comparator:** current-prod pool-ordering reranker, `jina-reranker-v3-mlx` (ADR-004,
`config.toml reranker_model="jina"`).

**Run mechanism (if unblocked):** `scripts/bench_retrieval.py --golden eval/golden/golden_v7.jsonl
--reranker {jina,set-encoder} --rerank`, unmodified except for the new `--reranker set-encoder` arm
added in this task — end-to-end exactly like the existing `crossencoder`/`jina` arms, no separate
analysis script. n=260 (golden_v7), matching Turn 5's own confirmation-run methodology in
`2026-08-26-retrieval-param-sweep-prereg.md`.

**Explicitly not a re-derivation of ADR-004** (already run 2026-08-24, jina vs bge, adopted). This
benchmark only asks whether Set-Encoder beats the *already-adopted* jina baseline — it does not
reopen the jina-vs-bge decision, and per `.claude/rules/refusal-criteria.md` its result is never
compared against `eval/golden/gate_v7.json` floors (those floors are model-dependent, derived under
a fixed reranker/generator stack; a different reranker candidate is a category error to gate against
them without re-deriving via `derive_thresholds.py`, which this task does not do).

**Out of scope** (per brief): fine-tuning Set-Encoder on SEBI data; MLX porting; wiring into the
`B'` citation-scorer role. Retrieval-ordering benchmark only.

## 2. Endpoints

| role | metric | source |
|---|---|---|
| PRIMARY | `recall_at_10` (circular-level; matches `run_retrieval_benchmark`'s own field name — not `doc_recall_at_10`, which is a different, unrelated script's naming) | `bench_retrieval.py --reranker {arm} --rerank`, `results.json` |
| PRIMARY | `ndcg_at_10` | same source |
| PRIMARY (significance) | paired per-query delta, set-encoder arm vs jina arm, same golden_v7 queries | `stats.py:paired_delta` over per-query recall/ndcg vectors (`benchmark.py:per_query_recall` plus the equivalent per-query ndcg, both computed from each run's `run.trec`) |
| GUARDRAIL | `make test` | must stay green; no `config.toml` change ships from this task regardless of outcome |

## 3. Decision rule — fixed in advance

**Step 0 — can both arms complete a run at all?** If either arm's reranker cannot construct or
score without error in this project's pinned environment, the outcome is **BLOCKED**, recorded in
§5 with the exact failure, and Steps 1–2 below do not apply (there is nothing to compare). This is
not a deviation invented after the fact — it is registered here, in advance, because §0 already
found this to be the case for the set-encoder arm before this document was committed.

**Step 1 (only reached if Step 0 clears both arms).** A candidate is **adopt-recommended** only if
both hold, per `stats.py:PairedResult.significant` (permutation p < 0.05 **and** paired bootstrap
CI excludes 0):
1. `|Δ|` ≥ 0.01 (1pp absolute) on `recall_at_10` **or** `ndcg_at_10` vs the jina baseline, in
   set-encoder's favor.
2. `PairedResult.significant is True` for that metric.

If Step 1's bar is not cleared → **NULL**, current prod (jina) unchanged.

**Adoption is a recommendation only** — per the brief, no `config.toml` change ships from this task
regardless of outcome (ADOPT, NULL, or BLOCKED). Wiring a new pool-ordering reranker into
`retrieval_reranker_for`/`config.toml` requires a separate, explicitly-approved follow-up.

## 4. Not permitted after seeing a result

- Lowering the 1pp/significance bar because a candidate is close but under it (matches
  `2026-08-26-retrieval-param-sweep-prereg.md` §4 / `2026-08-26-hybrid-gate-prereg.md` §4
  discipline).
- Treating this benchmark as a re-derivation of ADR-004, or its result as grounds to revisit the
  jina-vs-bge decision — out of scope for this task.
- Reporting this run's `recall_at_10`/`ndcg_at_10` against `eval/golden/gate_v7.json` floors — those
  floors are model-dependent (`.claude/rules/refusal-criteria.md`) and were derived under the
  current reranker; a different reranker candidate is a category error to gate against them.
- Shipping any `config.toml` change from this task, adopted or not.
- Patching around the §0 load failure with version-pinned monkeypatches to force a number out of a
  broken environment path, rather than reporting BLOCKED honestly. (This is the fabrication risk
  this document exists to foreclose in advance: fabricating a working benchmark result off a
  monkeypatched, likely-invalid inference path would violate this project's explicit no-fabrication
  refusal criterion.)

## 5. Recorded outcome

**BLOCKED (environment) — anticipated and disclosed in §0, not a deviation.**

`SetEncoderReranker` could not construct `lightning_ir.CrossEncoderModule("webis/set-encoder-base")`
under `transformers==5.14.1` (not a direct/explicit pin — resolved transitively via
`sentence-transformers>=5.6.0` and locked at that version in `uv.lock`), on either
`lightning-ir==0.0.6` (PyPI) or `lightning-ir@03e8def` (GitHub main, same version tag) — verified via
both a direct API probe and the real `bench_retrieval.py --reranker set-encoder --rerank` code path
(§0). No golden_v7 query was scored by either arm; `recall_at_10`/`ndcg_at_10`/paired-delta are **not
measured, not estimated, not reported** — there is no result to report per §3 Step 0, and none is
fabricated to fill the gap.

**Recommendation:** do not adopt Set-Encoder now. Re-attempt this benchmark if/when `lightning-ir`
publishes a release compatible with `transformers>=5.x` (tracked upstream, not in this project), or
if a project decision separately changes `sentence-transformers` (or otherwise constrains
`transformers` directly) such that the transitively-resolved `transformers` version drops below 5.x
(its own, unrelated tradeoff against `sentence-transformers>=5.6.0` and the rest of the stack — not
something this task is authorized to do). `SetEncoderReranker` and `bench_retrieval.py --reranker
set-encoder` are
implemented and committed against the verified-correct API contract (§0), so re-running requires no
further code changes once the environment blocker lifts — only `pip install lightning-ir` (or
`uv pip install -e '.[rerank-experimental]'`) into a compatible environment.

**No `config.toml` change ships.** `make test`: see `docs/status.md` entry and PR/commit for the
exact pass/fail counts recorded alongside this task's implementation commit.
