# Cross-Reference Eval Validity — Preregistered Analysis

**Written:** 2026-08-19, **before** the stratum is mined, generated, or scored.
**Status:** analysis plan frozen. Deviations get recorded as deviations, not edited away.
**Tests a standing conclusion, not an intervention.** Nothing ships from this experiment.

---

## 0. What this puts at risk — read this first

`docs/status.md` records a conclusion that currently governs the programme's direction:

> **Three independent interventions converge on exactly 0.9861.** The retrieval stage already
> delivers 98.6% of relevant documents into the reranker's pool; at most 1.4 pp of headroom
> exists. This is a structural explanation for the five nulls and a prediction that any further
> fusion-level intervention will also be null. **Stop proposing them.**

That conclusion is drawn from **one eval set**. Pool R@50 = 0.9861 is a property of
`baseline`, `iv9`, `iv10` and `iv11` measured on `golden_v7` — and of nothing else. The
inference "retrieval is saturated" requires the additional premise that golden_v7's query mix
is representative of the questions the system must answer. **That premise has never been
tested.**

This preregistration tests it. It is deliberately structured so that **either outcome is
informative**, and so that the more convenient outcome (saturation confirmed) is the one the
design is biased *toward* — see §2.

---

## 1. Why

### 1.1 The external contrast

[CRAwLeR](https://arxiv.org/abs/2606.21676) (Jalocha & Michelsen) builds legal retrieval
benchmarks around **cross-references** — provisions that cite other provisions — on Danish and
Polish statutory material, with a construct-validity check confirming ~80% of queries genuinely
require the referenced context. Reported results:

| | Recall@10 |
|---|---|
| CRAwLeR-DK (best system) | **0.55** |
| CRAwLeR-PL (best system) | **0.59** |
| **This repo, golden_v7** | **0.943** |

They also report a failure shape this repo will recognise:

> *"even when targets appear in top-ten results, labelled context chunks routinely outrank it"*

That is structurally the same complaint as the repo's own cite-wrong-docs diagnosis (the
relevant document is present but outranked by adjacent material), arrived at independently.

Two explanations fit the 0.55–0.59 vs 0.943 gap:

- **H_easy:** SEBI circular retrieval is genuinely easier than Danish/Polish statutory
  retrieval — shorter corpus, stronger lexical anchors (circular numbers), English.
- **H_sample:** golden_v7 under-samples the cross-reference-dependent queries that make legal
  retrieval hard, so 0.9861 describes an easy slice.

These are not exclusive. The experiment estimates how much of the gap H_sample accounts for.

### 1.2 In-repo signals consistent with H_sample

None of these is evidence on its own; together they are enough to justify measuring.

| Signal | Value | Source |
|---|---|---|
| `multi_hop` share of the reporting set | **20 of 260** (7.7%) | status.md §v7 strata |
| Rows labelled by a single model (not human/arbitrated) | **114 of 260** | status.md label tiers |
| κ on `multi_hop` (exact-set) | **0.071** | status.md agreement table |
| κ on `numeric_table` (exact-set) | **0.000** | status.md agreement table |
| Rows answerable but unjudged | **3** (`v7-ls-038/039/040`) | status.md |
| R@10 headroom at baseline | ~4.4 pp (ceiling-limited) | status.md §"recall@10 is the wrong primary metric" |

The repo has already concluded once that a metric choice, not the system, was hiding effects —
switching from R@10 to nDCG@10 turned 8 discordant queries into 95. **This asks the same
question one level up: is the eval *set*, not just the metric, hiding effects?**

### 1.3 The machinery already exists

No new extraction is required. The repo built and validated the citation graph for other
purposes:

- `reg_citations.py` — regulation citations from circular text
- `reg_lineage.py` — circular→regulation edges, `regulatory_basis_status`
- `lineage.py` — circular→circular `supersedes` / `amends` / `cites` relations
  (`detect_relations_ex`, `build_lineage`, `Lineage`)
- `data/manifests/regulation_edges.jsonl` — persisted edges
- `data/index/lineage.json` (2.1 MB)

This is the cheapest high-leverage measurement available, which is the main argument for
running it before R0 (generator upgrade) or R2 (temporal typing).

---

## 2. The trap this design has to avoid

**A validity study that constructs its own hard set can always succeed.** If I mine edges,
generate queries, and keep the ones retrieval fails, I will "prove" retrieval is not saturated
and will have proved nothing. That is the same error as the `ce_query_reform_probe` variants
written with gold knowledge — a ceiling presented as a result.

Four structural guards, fixed here:

1. **Mining is mechanical and blind to retrieval.** Selection criteria (§3.1) are frozen before
   any query is generated. No row is ever added or dropped on the basis of whether the system
   retrieves it.
2. **Query generation never sees retrieval output.** One fixed prompt, one pass, no regeneration
   of failures.
3. **The adversarial filter removes queries that are *too hard for the wrong reason*, and also
   those that are *not actually cross-reference-dependent*** (§3.3). It runs before scoring and
   its effect is reported.
4. **A calibration control on the same harness** (§5) — golden_v7's own `multi_hop` and
   `title_direct` strata. Without it, a low number on a new set is uninterpretable.

**Bias direction, stated in advance:** guards 3 and 4 make it *harder* to reject saturation, not
easier. The adversarial filter discards precisely the queries most likely to fail. If saturation
still breaks under a filter tuned against breaking it, that is a strong result. If it holds, the
standing conclusion is genuinely strengthened and R4/R5/R6 can be de-prioritised with
confidence.

---

## 3. Method

### 3.1 Mining (frozen criteria)

From the persisted lineage graph, select ordered pairs **(A, B)** where:

- A contains an explicit `cites` reference to B (`lineage.detect_relations_ex`, relation class
  `cites` — **not** `supersedes` or `amends`; supersession is R2's subject and is excluded here
  to keep one variable),
- both A and B are present in the 730-record corpus,
- B is `in_force` at corpus head (excludes repealed-basis confounds),
- B contributes ≥ 3 non-degenerate chunks (body ≥ 80 chars, per the 8.57% degenerate measurement
  in `docs/research-synthesis-2026-08-19.md` §5),
- the pair is not already represented in `golden_v7` (`relevant_circulars` overlap = ∅).

Cap at **one pair per (A, B) circular pair** and **at most 3 pairs per source circular A**, to
prevent a single heavily-cross-referencing master circular dominating the stratum.

**Target: ≥ 150 rows surviving §3.3.** Mine to **600** candidate pairs. F2 is expected to be the
dominant filter — a large share of generated queries will turn out answerable from A alone — so
attrition around 70% is the *expected* case, not a warning sign. The void threshold (§6.4) is set
at 80% accordingly, leaving real margin between the design target and the abort condition.

### 3.2 Query generation

The gold document is **B**. The query is generated from **B's provision text**, and must be
answerable from B alone once B is retrieved.

- **Generator:** Qwen3.6-35B-A3B-MLX-4bit via oMLX (127.0.0.1:8001) — the model already
  designated PRIMARY for golden-v7 adjudication. **Explicitly not** Qwen2.5-1.5B, which is
  documented incapable of instruction-following in this project (0/48 citation brackets;
  74.2% degenerate rewrites).
- **One fixed prompt**, frozen in `scripts/analysis/mine_crossref_stratum.py` before execution.
- Greedy decoding, fixed seed. Re-runs must be byte-identical.
- The prompt receives B's provision text and A's *subject line only* — never B's circular
  number, never the corpus, never retrieval results.

**Frozen instruction shape:** generate a question a practitioner would ask having encountered
A's subject matter, whose answer is the provision in B, using the vocabulary a practitioner
would use rather than B's exact wording.

### 3.3 Adversarial filter (runs before any scoring)

A candidate row is **dropped** if any of:

- **F1 — leakage:** the query contains B's circular number, or ≥ 8 consecutive tokens copied
  verbatim from B. (Prevents trivially-solvable rows.)
- **F2 — not cross-reference-dependent:** the query is answerable from **A** alone. Operationalised
  as: an LLM judge (same model, separate fixed prompt) is given **only A's text** and the query,
  and produces an answer; a second call scores that answer against **B's provision text as the
  reference**. If the A-only answer is judged substantively equivalent to the reference, A
  suffices, the row does not test cross-reference retrieval, and it is out. The judge never sees
  B when answering — only when scoring.
- **F3 — degenerate query:** empty, > 40 words, not a question, or unchanged from the prompt.
- **F4 — ambiguous gold:** ≥ 2 distinct in-force circulars contain a provision answering the
  query (checked against the corpus, not against retrieval). Multi-gold rows are out — they
  weaken the single-relevant-doc assumption that pool R@50 rests on.

**Report the attrition at each stage.** A filter that removes > 70% of candidates means the
mining criteria are wrong and the run is void (§6.4).

### 3.4 Construct validity check

On a random sample of **30** surviving rows, a manual pass records for each: is the query
natural, is B genuinely required, is B genuinely sufficient. **Pass threshold ≥ 80%** on all
three, matching CRAwLeR's reported construct validity. Below that, the stratum is not a valid
instrument and §6.4 applies.

### 3.5 Scoring

Existing harness, unchanged: `scripts/bench_retrieval.py --rerank --index-dir data/index`.
Same 730-circular / 78,630-chunk index, same retriever configuration, same RRF, same pool size
50. **No pipeline code is modified by this experiment.**

Corpus + stratum identity recorded as a new frame in `eval/epochs/epochs.jsonl`; cross-frame
comparison raises `IncomparableFramesError`, as designed. TREC convention applies: unjudged
rows are excluded, not scored 0.

---

## 4. Endpoints

- **PRIMARY — pool `Recall@50` on the cross-reference stratum.** This is the exact quantity the
  standing conclusion rests on (0.9861 on golden_v7). One-sided exact binomial test against
  H₀: *p_miss ≤ 0.0139*.
- **SECONDARY — `Recall@10`, `nDCG@10`, `MRR`** on the stratum, with the reranker applied
  (`--rerank`), reported with bootstrap 95% CIs.
- **CALIBRATION — the same four metrics on the two control strata** (§5).
- **DIAGNOSTIC — outranked-by-context rate:** of rows where B is in the pool but outside top-10,
  how many have a chunk from **A** ranked above every chunk from B. This tests CRAwLeR's
  *"labelled context chunks routinely outrank it"* on this corpus directly.
- **COST — mining + generation + filtering wall-clock**, and rows surviving each filter stage.

### Power

Under H₀ (p_miss = 0.0139), at n = 150 the expected miss count is 2.1. Reject H₀ at α = 0.05
when misses ≥ 6 (P(X ≥ 6) ≈ 0.017). Under an alternative of p_miss = 0.10, P(X ≥ 6) ≈ 0.999.
**n = 150 is well powered to detect any pool R@50 at or below ~0.96.** This is the first
measurement in this programme designed against a stated power calculation rather than discovered
to be underpowered afterwards — see the iv-series note in status.md.

---

## 5. Arms

There is no treatment. The comparison is **stratum vs stratum on an identical harness**.

| Arm | Set | n | Purpose |
|---|---|---|---|
| **Treatment** | cross-reference stratum (§3) | ≥150 | the untested query class |
| **Control-A** | `golden_v7` `multi_hop` rows | 20 | the nearest existing analogue |
| **Control-B** | `golden_v7` `title_direct` rows | 40 | the easiest existing stratum — anchors the scale |

Control-B is the harness check: if it comes out low, a low treatment number means nothing,
because the bug is in the measurement. **Operationalised as pool R@50 ≥ 0.95 on `title_direct`.**
That floor is derived, not chosen: overall golden_v7 pool R@50 is 0.9861 and `title_direct` is
the easiest of the eight strata, so it cannot legitimately sit below the whole-set figure by
more than sampling noise at n = 40. There is no previously recorded *per-stratum* pool R@50 to
compare against — this is the first run that produces one, which is why the check is specified
as an absolute floor rather than as reproduction of a prior number.

**Rejected in advance**, recorded so they are not silently reintroduced:

- **Reusing golden_v7 rows in the treatment arm.** Deterministic retrieval would reproduce
  recorded numbers byte-for-byte and confirm nothing — the same reasoning that made the iv11
  confirmatory run use held-out `probes_v1` rather than golden_v7.
- **Human-authored cross-reference queries.** Authoring with knowledge of what the retriever
  misses is the `ce_query_reform_probe` error.
- **Adding the stratum to the reporting set.** This experiment produces a *measurement*, not a
  gate change. Gate floors are not touched (§8).

---

## 6. Decision rule — fixed in advance

Let **R50** be the primary endpoint on the treatment arm.

1. **R50 ≥ 0.95** *and* Control-B reproduces → **saturation confirmed and generalised.** The
   standing conclusion is strengthened beyond golden_v7. Record it; de-prioritise R4/R5/R6 in
   the roadmap; the retrieval surface stays closed.
2. **R50 < 0.90** with H₀ rejected *and* §3.4 construct validity ≥ 80% → **saturation is scoped
   to golden_v7.** The "stop proposing fusion interventions" rule is narrowed to that set, and
   the retrieval surface reopens for preregistered work. This does **not** retroactively adopt
   any rejected iv arm — iv2/iv8/iv11 were rejected on their own endpoints and stay rejected.
3. **0.90 ≤ R50 < 0.95** → **inconclusive.** Record as inconclusive. Do not re-slice the
   stratum to move the number across a boundary (§8).
4. **Void** if any of: filter attrition > **80%** (§3.3), construct validity < 80% (§3.4),
   Control-B pool R@50 < 0.95 (§5), or fewer than 150 rows survive filtering (§3.1). A void run
   is recorded as void and the instrument is fixed before re-running — it is **not** reported as
   a null, and it does not license any §7 conclusion.

**No outcome of this experiment ships code or moves a gate floor.**

---

## 7. What each outcome licenses

| Outcome | Licensed | Not licensed |
|---|---|---|
| §6.1 confirmed | De-prioritising retrieval work; higher confidence in R0/R1/R2 as the real surface | Claiming golden_v7 is representative in *other* respects (citation, abstention) |
| §6.2 scoped | Preregistering new retrieval work; revisiting pool size and fusion weighting | Adopting any previously-rejected arm without its own confirmation |
| §6.3 inconclusive | Nothing. Record and move on | Re-running with adjusted mining criteria and reporting as preregistered |

Note for §6.2: [Paper A](https://arxiv.org/abs/2604.01733) reports BM25 (0.644) outperforming
dense (0.587) on financial documents. If the surface reopens, RRF leg weighting is the cheapest
first probe — no re-encode required. **That is a future prereg, not part of this one.**

---

## 8. Not permitted after seeing the result

- Adjusting §3.1 mining criteria, §3.3 filters, or the §3.2 prompt after seeing R50, then
  re-reporting as preregistered. Any change is a **new stratum**, recorded alongside this one.
- Moving the §6 thresholds (0.90 / 0.95) to reach a cleaner verdict.
- Dropping individual rows from the treatment arm post hoc for any reason not in §3.3.
- Reporting an inconclusive result (§6.3) as evidence for either conclusion.
- Treating a §6.2 result as licence to adopt iv2, iv8, iv9, iv10 or iv11. Those were rejected on
  their own preregistered endpoints; a wider eval set does not reverse them.
- Adding this stratum to `golden_v7`, `gate_v7.json`, or any gated metric.
- Re-deriving gate floors against this stratum.

---

## 9. Implementation notes

New scripts, both under `scripts/analysis/` (not `scripts/golden_v7/` — this is not part of the
adjudication pipeline):

- `mine_crossref_stratum.py` — §3.1 mining, §3.2 generation, §3.3 filtering. Writes
  `eval/probes/crossref_v1.jsonl` + `reports/crossref-stratum-mining-2026-08-19.json`
  (attrition per stage, frozen prompt hash, generator model id, seed).
- `score_crossref_stratum.py` — §4 endpoints over treatment + both controls via the existing
  `bench_retrieval` path. Writes `reports/crossref-eval-validity-2026-08-19.json`.

Hard constraints this change must respect:

- **No new field on `CircularMeta`** (`segment.py:131` does `asdict(meta)` → 78,630 chunks).
- **No edit to `*_spaces.py` or root `app.py`** — CPU-only HF Spaces demo, separate path.
- **No edit to `pipeline.py`, `retrieve.py`, `rerank.py`, or `generate.py`.** This experiment
  measures the existing system; if it needs a code change to run, the design is wrong.
- **No edit to `eval/golden/`.** The stratum lives in `eval/probes/`, alongside `probes_v1.jsonl`.
- New frame recorded in `eval/epochs/epochs.jsonl` with the current corpus hash (730 records /
  78,630 chunks) — **not** E4's `5f626dd9`, which was 78,523 chunks.

Determinism: generator seed fixed, prompt hashed into the mining report, `bench_retrieval`
already deterministic. A re-run must reproduce `crossref_v1.jsonl` byte-for-byte.

---

## 10. OUTCOME (recorded after execution)

### VOID per §6.4 — the stratum is not minable at this corpus size

Executed 2026-08-20, mining stage only (`scripts/analysis/mine_crossref_stratum.py`,
`reports/crossref-mining-2026-08-20.json`). **No query was generated, no arm was scored, no
metric was produced.** §6.4 fires on *"fewer than 150 rows survive filtering (§3.1)"*:

| stage | count |
|---|---|
| raw `references` edges in the 730-record corpus | **507** |
| − target B not in corpus | −374 (**73.8%**) |
| − target B superseded (not in force) | −103 |
| − pair already represented in golden_v7 | −9 |
| **candidates mined** | **21** |
| §3.1 target | 600 |

**21 of a 600 target, against a design that needs ≥150 rows to *survive* a filter expected to
remove ~70%.** Void, and per §6.4 recorded as void — **not** as a null. It licenses no §7
conclusion in either direction: the saturation finding is neither confirmed nor scoped, it is
**unchallenged**.

### Two spec corrections found at execution

1. §3.1 names the relation class `cites`. It is **`references`** (`lineage.detect_relations_ex`).
2. §3.1 says to read the **persisted lineage graph**. That graph contains **zero** such edges —
   `build_lineage` handles the `supersedes` and `amends` branches and silently drops `references`
   (no `else`, `lineage.py:174-184`). `data/index/lineage.json` is 4536 supersedes + 41 amends + 0
   references. §1.3's *"the machinery already exists"* is half-true: the **extractor** exists, the
   **artifact** does not. Pairs were re-extracted from corpus text with the unchanged extractor.

### The dominant cause is corpus coverage, not the criteria

**374 of 507 cross-references (73.8%) point at circulars outside the 730-record corpus.** The
corpus is a *sample* of SEBI's output, and cross-references leave it far more often than they stay
inside it. This is the finding with reach beyond R3: a cross-reference stratum cannot be mined at
this corpus size, and by the same token a real practitioner query that depends on a cross-reference
will frequently need a document the index does not hold.

### ⚠️ A hypothesis raised and REFUTED during execution — recorded so it is not re-raised

`detect_relations_ex` gates the `amends` branch on proximity (`abs(p - a) < 120`) but gates the
`supersedes` branch on **nothing** — any document containing one `SUPERSEDE_RE` match classifies
*every* reference in it as a supersession. Measured: of 4,476 such classifications, only **86
(1.9%)** have the reference within 120 chars of a supersede clause; **98.1%** rest on document-level
presence alone. That looked like an unintended asymmetry inflating the supersession graph that
`demote_superseded` consumes — which status.md 2026-08-13 names the top cause of zero-cite.

**It is not a bug.** 99 of the 175 supersede-clause documents are **Master Circulars**, and they
contribute **94.1%** of the classifications (4,213 of 4,476); the top 12 carry 105–234 references
each. A master circular *is* a consolidation that rescinds a listed schedule, so document-level
attribution is **correct** here and a proximity gate would discard ~98% of legitimate supersessions.
The asymmetry with `amends` is justified: an amendment names its target beside the amending
language; a master circular rescinds an annexure. **No code change is warranted.**

### Disposition

Per §6.4, *"the instrument is fixed before re-running"*. The instrument defect is **corpus
coverage**, not mining criteria — and §8 forbids loosening the criteria and re-reporting as
preregistered. A re-run therefore requires a materially larger corpus, and it would be a **new
stratum recorded alongside this one**, not a continuation. Not scheduled.

**R3 does not answer its question, and the roadmap must not claim it does.** The saturation
conclusion (pool R@50 0.9861) remains exactly as well-supported as it was before this run —
scoped to golden_v7, untested outside it.

---

## 10b. Original outcome placeholder

_Not yet run._
