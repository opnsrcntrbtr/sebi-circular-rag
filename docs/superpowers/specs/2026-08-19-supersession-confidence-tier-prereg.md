# Supersession Confidence Tiering — Preregistered Analysis

**Written:** 2026-08-19, **before** the tiering is implemented or run.
**Status:** analysis plan frozen. Deviations get recorded as deviations, not edited away.
**Related:** `2026-08-13-superseded-penalty-sweep-prereg.md` (penalty *magnitude*, not adopted),
`2026-08-13-superseded-penalty-decision.md`. This spec varies the penalty's **shape**, not its value.

---

## 0. The exploratory finding — and why it cannot be the result

`demote_superseded` is the single largest measured cause of wrong citations: **6 of the 19**
zero-cite rows, ahead of B′ (4) and the reranker (3) (`docs/status.md`, 2026-08-13).

Measured 2026-08-19 over `data/index/lineage.json` (read-only, no pipeline change):

```
supersedes edges:      4476 explicit_text  |  60 inferred
circulars marked superseded:               1350
  ...with >=1 explicit_text edge:          1313
  ...ONLY inferred (master_topic):           37   (2.7%)
```

Of the 6 demotion-caused zero-cite rows, **4 have a relevant circular whose superseded status
rests only on an inferred edge**:

| Row | stratum | relevant circular | edge provenance |
|---|---|---|---|
| v7-bp-036 | body_paraphrase | SEBI/HO/ISD/ISD/CIR/P/2021/22 | **only inferred** |
| v7-ls-005 | lineage_supersession | SEBI/HO/MIRSD/POD-1/P/CIR/2023/70 | **only inferred** |
| v7-mh-020 | multi_hop | SEBI/HO/AFD-1/AFD-1-PoD/P/CIR/2024/39 | **only inferred** |
| v7-nt-014 | numeric_table | CIR/IMD/DF/14/2013 | **only inferred** |
| v7-bp-017 | body_paraphrase | SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110 | explicit_text |
| v7-ls-006 | lineage_supersession | SEBI/HO/MIRSD-PoD-2/P/CIR/2023/90 | explicit_text |

2.7% of superseded circulars account for ~67% of the demotion-caused failures.

⚠️ **This is post-hoc and is not evidence.** Those 6 rows were selected *because* they failed;
testing a property of them afterwards is precisely the analysis the iv11 confirmatory run
existed to guard against. It is recorded here as the **motivation** for a hypothesis. Per §4 the
4 rows are **excluded from the primary endpoint** and reported separately, so the number that
decides adoption is not the number that generated the hypothesis.

## 1. Why

### 1.1 The penalty is blind to provenance

`lineage.py:206-215`:

```python
out = [(c, s * penalty if c.doc_id in lineage.superseded_by else s) for c, s in reranked]
```

Binary membership in `superseded_by`, times one scalar. It consults none of the primitives this
repo has already built and tested:

| Primitive | Location | Consulted by demotion? |
|---|---|---|
| `Lineage.governing_on(cn, as_of, issue_dates)` | `lineage.py:96` | no |
| `Lineage.explicit_superseded_by(cn)` | `lineage.py:109` | no |
| edge `confidence` (`explicit_text` / `inferred`) | `lineage.py:168-172` | no |

### 1.2 The two edge classes are not equally trustworthy

`build_lineage` produces supersession edges two ways:

1. **`explicit_text`** — a supersession clause detected in the circular's own text
   (`detect_relations_ex`, regex `SUPERSEDE_RE`), with the matching text retained as `evidence`.
2. **`inferred`** — master-circular re-issue detection (`lineage.py:187-201`): group records by
   `mc_topic(subject)`, sort by currency, newest supersedes all the rest.

`mc_topic` (`lineage.py:132-147`) normalises a title to **at most four words** after stripping
`sebi`, punctuation, and stopwords, cutting at the first section marker. Two master circulars on
related-but-distinct subjects can collide on that key, and the whole group is then chained to a
single "newest".

Supersession false-positives are a demonstrated class in this corpus, not a hypothetical: the
2026-07-25 repair removed **90 false-positive supersession pairs** (2850→2760), the entire delta
traced to 12 defective records.

### 1.3 Why magnitude tuning already failed, and why shape is a different question

The 2026-08-13 sweep varied the scalar and was **not adopted**:

| penalty | context_miss | stale@3 | stale@1 |
|---|---|---|---|
| 0.15 | 17 | 70 | 1 |
| **0.30 (current)** | **15** | **83** | **1** |
| 0.50 | 13 | 101 | 1 |
| 0.70 | 12 | 122 | 4 |
| 1.00 | 9 | 188 | 68 |

Every value trades citation correctness against surfacing repealed law, because a uniform scalar
cannot distinguish a circular that *is* superseded from one the heuristic *believes* is
superseded. **Tiering by provenance is not a point on that curve** — it moves only the 37
circulars whose supersession is unevidenced, leaving all 1,313 evidenced ones at 0.3.

## 2. The trade this is measuring

Weakening demotion on inferred edges **surfaces more superseded law by construction**, which is
the harm the penalty exists to prevent, and which for a legal tool is the worse failure.

- **Benefit:** governing circulars wrongly demoted by a title-collision heuristic return to the
  context window.
- **Risk:** a genuinely superseded circular whose supersession clause was simply not detected
  (a false negative in `explicit_text` extraction) is promoted to top rank.

The second risk is real: `explicit_text` extraction is itself regex-based. A circular superseded
in fact but only caught by `mc_topic` would, under T1, receive no penalty at all. **That is what
the guardrail measures**, and it is why the guardrail is zero-tolerance rather than a budget.

## 3. Method

Single variable. `demote_superseded` gains an optional second tier; every other stage — retrieval,
pool size, RRF, reranking, B′, top_k, the gate — is untouched.

```python
def demote_superseded(reranked, lineage, penalty=0.3, inferred_penalty=None):
    """inferred_penalty=None reproduces current behaviour exactly."""
```

Tier assignment reuses the existing accessor rather than adding a lookup:

```
p = penalty if lineage.explicit_superseded_by(c.doc_id) else inferred_penalty
```

Frozen properties:

- **Backward-compatible default.** `inferred_penalty=None` → every superseded circular demotes at
  `penalty`, byte-identical to today. The flag is off until §6 says otherwise.
- **The persisted graph is not modified.** `build_lineage` still emits inferred edges;
  `Lineage.status()` still reports those 37 circulars as `superseded`; `superseded_citations`
  still flags them in the answer text. Only the *rerank weight* is tiered. Other consumers of
  lineage semantics are unaffected.
- **The `as_of` branch is untouched.** `pipeline._apply_lineage` lines 77-102 use exclusion, not
  demotion, and pass `eval-asof` 13/13. This spec changes only the `elif` branch (`pipeline.py:104`).
- **Deterministic.** No model call is added. Re-runs must be byte-identical.

## 4. Endpoints

**Cohort.** The perfect-retrieval subset — answerable golden_v7 rows where every relevant document
is retrieved — the same *definition* used by both prior B′ arms and the 2026-08-13 zero-cite
composition.

⚠️ **The cohort is not a stored artifact and its membership is index-dependent.** It was derived
inline in the 2026-08-12/13 analyses and never persisted. Those runs used the **724-circular /
78,523-chunk** index and produced 206 rows; the current index is **730 / 78,630**, so the subset
must be **recomputed** and may not be 206 rows. **Row ids are computed and written to
`reports/supersession-tier-cohort-2026-08-19.json` before the treatment arm runs**, and that file
is the cohort of record for this experiment.

⚠️ **All control values below are prior-index reference figures, not this experiment's baseline.**
They are recorded to show the expected order of magnitude and to make an unexplained divergence
visible. **The Control arm (§5) is re-measured on the current index and is the only baseline the
§6 decision rule may use.** Comparing T1 against a figure from a different index is exactly the
frame-mixing error `rescore_runs.py` raises `IncomparableFramesError` to prevent.

- **PRIMARY — `zero_cite`**: rows citing nothing relevant. Reported over the cohort **excluding**
  the 4 rows named in §0, so the hypothesis is confirmed on data that did not generate it.
  *(prior-index reference: 19 over 206 rows)*
- **GUARDRAIL — `stale@1`**: rows whose **top-ranked context chunk** is from a circular superseded
  at corpus head. *(prior-index reference: 1 over 204 answerable non-as_of rows at penalty 0.3)*
- **GUARDRAIL — `stale@3`**: same within top-3. *(prior-index reference: 83)*
- **SECONDARY** — `citation_recall`, `citation_precision`, `context_recall`, `context_miss`
  *(prior-index reference: 15)*.
- **EXPLORATORY, reported separately and binding on nothing** — the 4 §0 rows.

### On the guardrail metric

The 2026-08-13 sweep's guardrail was **"any superseded circular anywhere in top-10"**, which sits
at 192-203 of 204 — near-ceiling, and structurally blind to the harm it existed to detect, since
the corpus contains 1350 superseded circulars. That mis-specification is why the sweep's selected
value (0.7) was recorded but not adopted. **`stale@1` and `stale@3` are rank-sensitive and are the
correction.** Inheriting that fix is the main methodological point of this spec.

## 5. Arms

| Arm | explicit_text edges | inferred edges |
|---|---|---|
| **Control** | 0.3 | 0.3 (production today) |
| **T1** | 0.3 | **1.0** (no penalty) |

Single treatment arm, at the extreme value. If T1 does not improve the primary, no intermediate
value will, and the hypothesis is dead in one run rather than a grid.

**Rejected in advance**, recorded so they are not silently reintroduced:

- **Sweeping `inferred_penalty` over a grid.** Refits to the observed set — the exact failure of
  the `superseded_penalty` sweep, whose rule selected a value its guardrail could not price.
- **Dropping inferred edges from `build_lineage`.** Changes the persisted graph and the `status()`
  of 37 circulars, contaminating `superseded_citations`, the answer-text warnings, corpus
  annotation, and `regulatory_basis_status`. Different, larger experiment.
- **Improving `mc_topic`.** Tuning the heuristic against the 37 circulars it currently produces is
  fitting the extractor to the eval set.
- **Tiering by `amends` as well.** `amends` edges do not trigger demotion at all today. Out of scope.

## 6. Decision rule — fixed in advance

1. **Discard T1 if `stale@1` > 1** (any increase over control). Surfacing repealed law as the
   top-ranked context is the failure the penalty exists to prevent; zero tolerance, consistent
   with the hybrid-gate and rescue preregs.
2. **Discard T1 if `stale@3` > 83** by more than 5 rows. A modest rise is expected and acceptable;
   a large one means the inferred edges were mostly correct.
3. **Adopt only if `zero_cite` improves by ≥ 2 rows** against the **Control arm measured in this
   run** on the identical cohort (§4), not against any prior-index figure. A 1-row gain does not
   qualify — the repo rejected `superseded_penalty` 0.5 on exactly that (1 row, p=1.000).
4. If 1-3 are met → proceed to §7. Otherwise record the null, leave `inferred_penalty=None`, and
   the 37 circulars keep the flat penalty.

## 7. Confirmation required before adoption

Cohort behaviour on 202 rows is not a shipping verdict. Any arm selected by §6 must be confirmed
by a full `eval_json_full` run (MLX generator, B′ on) against the armed floors in
`eval/golden/gate_v7.json`:

| Metric | Floor |
|---|---|
| recall_at_k | 0.906 |
| context_recall | 0.874 |
| ndcg_at_10 | 0.6512 |
| citation_recall | 0.8169 |
| abstention_accuracy | 0.9412 |
| citation_precision | 0.1577 |

`floors_ok: true` required. Floors are read from `gate_v7.json`, not transcribed from
`docs/status.md` — the 2026-08-19 sweep found stale floors propagated that way.

Additionally: `make eval-asof` must remain **13/13**. The as_of path is not modified by this
change, so any movement there indicates an unintended coupling and blocks adoption.

## 8. Not permitted after seeing the result

- Relaxing the `stale@1` zero-tolerance guardrail to admit a qualifying arm.
- Introducing an intermediate `inferred_penalty` after T1 fails, then reporting it as
  preregistered. A new value is a **new arm**, recorded alongside this one.
- Moving the primary to the full 206 rows (including the 4 exploratory rows) to reach adoption.
- Swapping the primary to a continuous measure (mean rank of the relevant doc) in place of the
  row count.
- Editing `mc_topic` in the same experiment. Single variable.
- Re-deriving gate floors under T1 to make the §7 comparison pass.
- Reporting the 4 §0 rows as confirmation of anything.

## 9. Implementation notes

| File | Change |
|---|---|
| `src/sebi_rag/lineage.py` | `demote_superseded(..., inferred_penalty=None)`; tier via `explicit_superseded_by`. Default path unchanged |
| `src/sebi_rag/settings.py` | `inferred_supersession_penalty: float \| None = None` |
| `config.toml` `[service]` | `# inferred_supersession_penalty` — commented out until §6/§7 pass |
| `src/sebi_rag/pipeline.py:104` | pass-through only |
| `scripts/analysis/supersession_tier_cohort.py` | measurement harness; §4 endpoints; freezes cohort ids first |

`explicit_superseded_by` is O(len(edges)) per call (`lineage.py:110-113` scans `self.edges`, 4577
entries). Called per chunk per query this is a hot path — the harness must precompute the
explicit-superseded set once per run. **This is a measurement-harness concern, not a semantics
change**; if adopted, the same precomputation goes into `demote_superseded`.

Hard constraints this change must respect:

- **No new field on `CircularMeta`** (`segment.py:131` does `asdict(meta)` → 78,630 chunks).
- **No edit to `*_spaces.py` or root `app.py`** — CPU-only HF Spaces demo, separate path.
- **No change to the persisted `lineage.json`** — no reindex, no re-annotation.
- Config lives under `[service]`, not `[spaces]`.

## 10. OUTCOME (recorded after execution)

**Run:** 2026-08-19, `scripts/analysis/supersession_tier_cohort.py`,
`reports/supersession-tier-cohort-2026-08-19.json`. 2259 s (37.7 min), MLX
`Qwen2.5-1.5B-Instruct-4bit`, B′ on at margin 0.35, `superseded_penalty=0.3`.

### Cohort, recomputed as §4 requires

| | value |
|---|---|
| eligible (answerable, non-as_of, gold citations) | **204** |
| perfect-retrieval cohort | **201** *(prior-index reference: 206)* |
| primary set (cohort − 4 exploratory) | **197** |
| lineage | superseded 1350, explicit 1313, **only_inferred 37** |

The §4 patch was load-bearing. Every prior-index reference figure was wrong on the
current index: `stale@1` 1 → **7**, `stale@3` 83 → **100**, `zero_cite` 19 → **14**.
Had T1 been compared against the status.md values it would have looked even worse than
it is, for the wrong reason.

### §4 endpoints

| Endpoint | Control | T1 | Δ | Rule |
|---|---|---|---|---|
| **PRIMARY `zero_cite`** | 14 | **19** | **+5 worse** | §6.3 needs ≤ 12 |
| **GUARDRAIL `stale@1`** | 7 | **61** | **+54** | §6.1 needs ≤ 7 |
| **GUARDRAIL `stale@3`** | 100 | **163** | **+63** | §6.2 needs ≤ 105 |
| `context_miss` | 8 | 12 | +4 | — |
| `citation_recall` | 0.9188 | 0.8934 | −0.0254 | — |
| `citation_precision` | 0.1854 | 0.1735 | −0.0119 | — |
| `context_recall` | 0.9569 | 0.9315 | −0.0254 | — |
| abstained | 2 | 2 | 0 | — |

### Decision: **T1 REJECTED** — all three rules fire

Worse on every measured quantity. `stale@1` rose **8.7×**: in 61 of 197 rows the
top-ranked context became a superseded circular.

### The hypothesis was confounded, and the confound is measurable

**All 4 exploratory rows flipped to cited (`exploratory_zero_cite` 4 → 0).** The rows that
generated the hypothesis were fixed exactly as predicted — while the 197 that did not
generate it got worse. Reporting the exploratory rows as the result would have read as a
clean 4-of-4 success. **§4's exclusion is the only reason this is not recorded as an
adoption.**

Root cause, measured after the run:

| | value |
|---|---|
| only-inferred circulars that are **master circulars** | **37 of 37 (100%)** |
| their share of circulars | 5.07% |
| their share of **chunk mass** | **24.40%** (19,183 of 78,630) |
| mean chunks/circular — only-inferred vs corpus | **518 vs 108 (4.8×)** |

`confidence="inferred"` is not an independent signal about edge reliability — it is a
**proxy for "is a master circular"**, because `mc_topic` only ever fires on master-circular
titles. Master circulars are 4.8× larger than the average circular and occupy a quarter of
the index, so they saturate any candidate pool.

That inverts §0. The enrichment (2.7% of superseded circulars → ~67% of demotion-caused
failures) is a **size effect, not a provenance-reliability effect**: these circulars are hit
hardest by demotion because they are everywhere in the pool, not because their supersession
is wrongly inferred. Removing their penalty does not restore governing law — it floods the
context window with superseded master circulars.

### What this establishes, and what it does not

- **Establishes:** the flat `superseded_penalty=0.3` is correct for master-circular re-issues.
  Master-circular supersession inferred by `mc_topic` is **behaving as if reliable** — the
  demotion it triggers is load-bearing, and removing it is severely harmful.
- **Establishes:** provenance tiering as specified in §3 is dead. Not a magnitude question —
  T1 was the extreme, and it fails in the same direction at every intermediate value, since
  any `inferred_penalty > 0.3` moves `stale@1` upward monotonically.
- **Does not establish** that the 6 demotion-caused zero-cite rows are unfixable. It
  establishes that *this* lever is the wrong one: the problem is that a superseded master
  circular can be simultaneously the best topical match and the wrong law, and a single
  rerank multiplier cannot express that.
- **Does not establish** anything about `explicit_text` edge quality, which was not varied.

### Per §8, not done

No intermediate `inferred_penalty` was tried after T1 failed. `mc_topic` was not edited. The
primary was not moved to the full 201 rows to reach adoption. The 4 exploratory rows are
reported above and bind nothing.

### Disposition

`inferred_supersession_penalty` defaults to `None` in `RAGPipeline`, so **production
behaviour is unchanged and the code ships inert**. `demote_superseded`'s new parameter is
backward-compatible by default (guarded by
`test_inferred_penalty_default_none_demotes_both_tiers_identically`). No `Settings` or
`config.toml` wiring was added — deliberately deferred to adoption, which did not happen.
**8 tests added** (6 in `tests/test_lineage.py`, 2 in `tests/test_pipeline.py`); suite
**867 passed**, 2 skipped.

### If a next arm is attempted

The finding points away from rerank weighting entirely. A superseded master circular is
often the best *topical* match and the wrong *law*; that is a two-dimensional fact and a
scalar multiplier collapses it. Candidate directions, each needing its own prereg:

1. **Chunk-level rather than document-level demotion.** A superseded master circular's
   individual provisions may be unchanged in the successor; penalising all 1,595 chunks
   uniformly is what makes demotion so blunt on these documents.
2. **Redirect rather than demote.** Where a superseded master circular chunk is the best
   match, retrieve the *corresponding* provision from its successor — `governing_on`
   (`lineage.py:96`, currently unused by the demotion path) already computes which circular
   governs.
3. Note the size confound generalises: any future intervention keyed on a document-level
   property must check whether that property is a proxy for chunk mass.
