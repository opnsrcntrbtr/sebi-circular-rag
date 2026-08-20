# Research-Grounded Enhancement Roadmap

**Date:** 2026-08-19
**Companion:** `docs/research-synthesis-2026-08-19.md` (source verification + corrections)
**Standard:** every external claim quoted from primary text with its evaluation scope stated;
every repo claim cites a file, line, or artifact under `reports/`. Unverified claims are marked
and justify nothing.

---

## 1. Three findings that reframe the programme

### 1.1 The B′ root cause has a name, and the repo's conclusion was half right

`status.md` §7 diagnosed B′ correctly: *"bge-reranker-v2-m3, a query↔document relevance model,
used as an attribution/entailment scorer. That is a model-task mismatch."* After NLI was
rejected twice, the conclusion drawn was *"entailment is the wrong criterion — stop pursuing
attribution/NLI scorers."*

[Relevant Is Not Warranted](https://arxiv.org/abs/2605.28044) shows the space is **three-valued,
not two**: topical **relevance** ≠ textual **entailment** ≠ evidentiary **warrant**. They name
the failure *"citation laundering"* — *"a real, topically relevant citation can still
under-warrant the attached wording."* Their FORCEBENCH holds the cited passage constant and
contrasts an evidence-appropriate claim against a strengthened one across five dimensions:

> relation, modality, scope, **temporal validity**, **numeric specificity**

Those last two are `lineage_supersession`/`repealed_basis` and `numeric_table` — **the repo's
two worst strata** (citation_recall 0.725 and 0.633; 11/30 and 7/35 zero-cite). The alignment is
exact.

Their result: standard evaluation prompting scores **47.2%**; warrant-focused prompting
**75.5%**. Overlap-based signals violate expected monotonicity on **32.8–36.4%** of cases —
i.e. the class of scorer B′ currently uses is measurably non-monotone in warrant.

**So B′ needs a third scorer type, not a return to relevance and not another NLI model.** And
because warrant judgement is a prompted task, it is gated on the generator.

### 1.2 The architecture choice was right — keep it

[Generation-Time vs. Post-hoc Citation](https://arxiv.org/abs/2509.21557) evaluates both
paradigms and recommends **post-hoc (P-Cite) for law**, achieving *"high coverage with
competitive correctness and moderate latency"*; generation-time gives *"precision at the cost of
coverage and speed."* B′ **is** P-Cite. Option A was G-Cite, and it measured 0/48 at 1.5B.

The repo's architecture is externally vindicated. **Change B′'s scorer; do not move citation
into generation.** The paper also finds *"retrieval as the main driver of attribution quality in
both paradigms"* — consistent with the repo's own stage-loss analysis.

### 1.3 The iv9/iv10 nulls do not generalise — three different mechanisms were conflated

Paper A reports *"contextual retrieval yields consistent gains,"* contradicting iv9/iv10
(nDCG@10 +0.0033 / +0.0018, null). The contradiction dissolves on inspection — these are three
distinct techniques:

| Technique | Mechanism | Tested here? |
|---|---|---|
| Anthropic contextual retrieval | LLM-generated **50–100 token summary** of the chunk's role in its document, prepended before embedding; reported 5–15% precision gains | ❌ never |
| iv9/iv10 contextual headers | **one lay+statutory sentence** per deep sub-clause | ✅ null |
| [Late chunking](https://arxiv.org/abs/2409.04701) | embed the **whole document**, chunk the token embeddings *after* the transformer, before mean pooling. No added text, no LLM calls, no training | ❌ never |

iv9/iv10 tested the weakest of the three and added ~40 characters of text. The nulls are
evidence against *that header form*, not against contextual enrichment. **The "stop proposing
chunk-text interventions" rule should be narrowed accordingly.**

---

## 2. Ranked roadmap

Ranked by (measured share of failures) × (external support) ÷ (cost). Dependencies are explicit
— **R0 gates R1 and R6.**

---

### R0 — Generator upgrade: 1.5B-4bit → 3B-4bit (revised 2026-08-20; was 7B/8B)  ⟨gates R1, R6⟩

**Claim.** The generator is the binding constraint on every instruction-dependent mechanism.

**Repo evidence.** Two independent no-ops: Option A selective citations **0/48** parseable
brackets (100% fallback to mechanical cite-all); CE rescue arm R1 **74.2%** degenerate rewrites
(23/31), both targets returned verbatim while two hard negatives were rewritten into
floor-clearing questions.

**External.** [Quantization on RAG](https://arxiv.org/abs/2406.10251) — *"if a 7B LLM performs
the task well, quantization does not impair its performance and long-context reasoning
capabilities."* Tested 7B/8B, FP16 vs INT4. **Never tested 1.5B**, so it de-risks the
destination; it does not diagnose the current failure. The in-repo probes do that.

**Real scope — not a config change.** `eval_generator = "mlx"` couples floor-derivation
(`derive_thresholds.py`) and measurement (`eval_json.py`) via `generate.eval_generator_for`,
enforced by three coupling tests. The stub→MLX precedent moved two floors
(citation_recall 0.7233→0.8124, citation_precision 0.1896→0.1571). Scope = **config +
full gate re-derivation + re-arm.**

**Costs — MEASURED 2026-08-20** (`reports/generator-cost-*.json`, 20 rows/model):

| model | peak RSS | query p50 | query max | >30 s | 260-row gate |
|---|---|---|---|---|---|
| 1.5B-4bit | 5.29 GB | 7.28 s | 11.88 s | 0 | 34.0 min |
| **3B-4bit** | 7.72 GB | 11.89 s | 15.34 s | **0** | **49.4 min** |
| 7B-4bit | 8.91 GB | ~10.6 s | **14.10 s** | **0** | **~44 min** |

- ✅ **Bug B3 retired** — no segfault at any size; 8.91 GB peak of 48 GB.
- ✅ **Gate cost is ~44 min at 7B, not 2–3 h.** Two downward corrections: the ~3 h estimate was
  wrong by ~2.5×, and the 69.9 min replacement was itself inflated by the artifact below.
- ⚠️ **The 7B row of this table is a correction.** The original probe reported p50 12.36 s, max
  **38.20 s**, 3 of 20 over `timeout_s`, 69.9 min. That tail was **irreproducible** — see the
  retraction below. The figures above are from `…-forward2.json` (identical row order).
**Instruction-following — SCREENED 2026-08-20** (`reports/mechanism-screen-*.json`,
`eval/probes/screen_v1.jsonl`, n=50 stratified, seed 20260819). Endpoint is mechanism-firing per
`2026-08-19-fast-gate-tier-prereg.md` §2.1 — not a gated metric.

| model | answered | rows w/ bracket | resolved | firing rate |
|---|---|---|---|---|
| 1.5B-4bit | 42 | **0** | 0 | **0.0%** |
| 3B-4bit | 42 | 3 | 2 | **7.1%** |
| 7B-4bit | 42 | **20** | 19 | **47.6%** |

Validity: all three arms answered 42 and abstained 8 — identical, so retrieval and gating are
unchanged and only generation differs. The 1.5B arm reproduces the 2026-08-03 result (0/48) on a
fresh stratified sample, which validates the screen as an instrument before it is trusted on the
others.

- ❌ **The 3B target is falsified.** 7.1% is barely above zero — it clears the spec's binary
  "non-zero licenses T-Cohort" bar on a technicality while providing no working mechanism. The
  1.45× cost buys almost nothing.
- ✅ **Only 7B actually follows the instruction** — 47.6% firing, and **19 of 20** bracket-emitting
  rows produce brackets that resolve to a circular in the context window. When it cites, it cites
  correctly.
- **Instruction-following is sharply nonlinear in size here: 0% → 7% → 48%.** Parameter count is
  not buying a smooth gradient, so intermediate sizes are not a compromise position.

**This reframes R0.** The choice is not "3B is cheaper and adequate" — it is "3B does not work,
and 7B does". There is no countervailing cost: see the retraction immediately below.

**⚠️ RETRACTED 2026-08-20 — the 7B timeout tail was an artifact** (`reports/timeout-tail-disconfound.json`).
This section previously read "7B works but breaches `timeout_s` on 15% of rows", diagnosed the tail
as prefill, and called for a preregistered context bound. All three claims are withdrawn.

The tell: the 3 slow rows occupied run positions **18, 19, 20** consecutively (p = 1/1140), while
the 3B probe — **same rows, same order** — showed no tail at all. Row cost and run position were
aliased, so the forward run could not identify either.

| 7B run (n=20, same rows) | p50 | mean | max | >30 s | corr(pos, lat) | corr(ctx_chars, lat) | gate |
|---|---|---|---|---|---|---|---|
| forward — original | 12.36 | 16.14 | **38.20** | **3** | +0.408 | +0.641 | 69.9 min |
| reverse — disconfounder | 10.54 | 9.99 | 13.81 | **0** | +0.028 | +0.800 | 43.3 min |
| forward — re-run, identical order | 10.71 | 10.40 | 14.10 | **0** | −0.005 | +0.825 | 45.1 min |

`calspread` 33.8 → **12.8 s**, `intraday` 36.3 → **11.8 s**, `disc_doc` 38.2 → **12.1 s** at the
same positions. The tail follows neither rows nor position — it is not reproducible, and reads as
transient external load during the original run.

**What survives.** Prefill genuinely dominates 7B latency, and the evidence *strengthens* once the
artifact is removed (corr 0.641 → **0.800 / 0.825**). But the dynamic range is 6.4 s → 14.1 s
against a 30 s budget, so a context bound is a **mean-latency lever, not a timeout fix** — and not
worth spending a gated metric on today.

**And a per-chunk character cap was the wrong instrument regardless** (`reports/context-composition.json`,
n=67). The chunker already bounds chunk size — corpus max **1,728 chars**, p95 1,395 — so a cap
only bites below ~1,200, where it truncates **23% of all chunks**: an amputation, not a trim. The
count term also dominates the size term (corr(n_contexts, lat) **0.502** vs corr(mean_chunk_chars,
lat) **0.284**), and 48 of 67 rows already sit at the full `top_k=10` after doc_id dedup. ⚠️ `top_k`
remains the wrong lever for a different reason: it was raised 5 → 10 precisely to lift
`citation_recall` 0.772 → 0.888.

**Invariance, for whenever a context experiment is worth running.** Truncating chunk text inside
`_grounded_prompt` (`generate.py:380`) leaves `ans.context_ids` untouched, so `context_recall`
(`scripts/golden_v7/score.py:51`) is invariant **by construction**, as are `recall_at_k` / `ndcg`
(pre-rerank fusion list) and `abstention_accuracy` (`SubjectSimJudge` reads subject/section
metadata, not chunk text). Only `citation_recall` and `citation_precision` can move. Truncating the
`Chunk` objects instead would additionally change what B′ scores (`select_citations` re-ranks the
same list), confounding the arm — so prompt-only is the single-variable choice.

**Decision rule (preregister).** Primary = zero-cite rows on the perfect-retrieval cohort,
**recomputed on the live index and persisted with its corpus hash** — the cohort is not a stored
artifact and is index-dependent (R2 measured 201 of 204 eligible where the prior index gave 206;
every prior-index reference value was wrong). Guardrails: **zero rows over `timeout_s`** (not a
p95 estimate — at n=20 the p95 equals the max by construction); `citation_precision` ≥ 0.1577;
`abstention_accuracy` ≥ 0.9412. Target `citation_recall` / zero-cite — **not**
`citation_precision`, which already clears its floor at 0.194.

**❌ R0 RUN AND REJECTED 2026-08-20.** Full T-Gate, both arms, n=260
(`eval/runs/tgate-2026-08-20-qwen{1.5b,7b}.json`). Control reproduces
`full-eval-2026-08-19.json` exactly; the three retrieval metrics are bit-identical across arms.

| metric | floor | 1.5B | 7B | Δ |
|---|---|---|---|---|
| citation_recall | 0.8169 | 0.872 | **0.879** | **+0.007** |
| citation_precision | 0.1577 | 0.191 | **0.184** | **−0.007** |
| recall_at_k / context_recall / ndcg_at_10 / abstention_accuracy | — | — | — | **0.000** |

2.3× compute and +3.2 GB RSS for +0.007 recall bought at −0.007 precision. That is not a ≥10%
measurable benefit, so it fails the §7.2 performance rule.

**⚠️ The premise of R0 was structurally wrong, and this is the durable finding.**
`answer_with_abstention` (`generate.py:551`) sets `citations` from **either** `select_citations(...)`
with B′ armed **or** `[c.id for c in contexts]` without it. **The model's emitted brackets are never
the source of `ans.citations`** — `select_citations` (`generate.py:90`) scores
`scorer.rerank(answer_text, contexts)` and never parses a bracket. B′ is armed in production.
Brackets feed only `faithfulness()` → `unsupported_citations` and the superseded-flag `_BRACKET.sub`
path.

So the T-Screen's headline — bracket firing 0.0% → 47.6% — **does not touch a single gated metric.**
The generator reaches the citation metrics only indirectly, by producing answer text that shifts
the cross-encoder when it re-ranks contexts against that text. That channel is worth ±0.007.

This retroactively explains two recorded results that were both attributed to model size: the
2026-08-03 "0/48 brackets" finding was never a blocker on citation quality, and Option A was a
100% no-op **structurally**, not merely because Qwen-1.5B is small.

**What the screen actually unlocked is a different question.** 47.6% resolvable bracket firing makes
bracket-*sourced* citation viable for the first time — an **alternative** to B′, not a complement.
R0 never tested it: it held B′ armed and swapped only the generator. Whether `brackets ∩ contexts`
beats B′'s cross-encoder selection **at 7B** is open, testable, and the thing the screen's result
actually bears on. See R0′ below.

---

### R0′ — Bracket-sourced citations at 7B  ⟨new 2026-08-20; supersedes R0⟩

**Claim.** With a generator that emits resolvable brackets on 47.6% of answered rows, the citation
source itself becomes a live design choice. B′ was adopted when the only alternative was cite-all
(brackets fired 0% of the time). That comparison is now stale.

**Arms.** B′ cross-encoder selection (control, production today) vs `brackets ∩ context_ids`
with B′ fallback on the 52.4% of rows that emit none. Both at 7B, so the generator is held constant
and the *citation source* is the single variable — the inverse of R0's design.

**Why it is not obviously a win.** B′ costs 4 zero-cite rows and buys +57% citation_precision
(2026-08-13); brackets could be worse on both. And `citation_precision` sits at 0.184–0.191 against
a 0.1577 floor — thin headroom to spend.

**Preconditions.** Needs the `SEBI_RAG_EVAL_ROWS` per-row dump (landed 2026-08-20) so the arms can be
decomposed by stratum and `label_tier`; and it must carry the CS1 confound check, since 7B's plausible
gains sit in the 85–90% model-labelled strata. Cost ~44 min/arm. **Not yet preregistered.**

---

### R1 — Warrant-calibrated citation scorer for B′  ⟨depends on R0⟩

**Claim.** Replace B′'s relevance scorer with a warrant judge. Keep the post-hoc architecture.

**Repo evidence.** B′ causes 4 of 19 zero-cite rows and buys citation_precision +57%
(0.1240→0.1948). It is not broken; it is scoring the wrong quantity, as §7 already concluded.

**External.** [2605.28044](https://arxiv.org/abs/2605.28044) — warrant ≠ relevance ≠ entailment;
warrant-focused prompting 47.2% → 75.5%; overlap signals non-monotone on 32.8–36.4%; the two
worst-scoring warrant dimensions map onto the two worst strata here.
[2509.21557](https://arxiv.org/abs/2509.21557) — post-hoc is the right paradigm for law.

**Why it failed before.** The NLI attempt substituted one wrong criterion (entailment) for
another (relevance). A context can be the governing provision without entailing a paraphrase of
it — the repo said exactly this. Warrant is the criterion that covers the gap, and it is a
prompted judgement, which is why it needs R0 first.

**Decision rule.** Same frozen 206-row subset, zero-cite as primary, matching the two prior
B′ arms so results are comparable. Guardrail: precision must not fall below floor.

---

### R2 — Supersession as typed temporal retrieval, not a scalar penalty  ⟨independent⟩

**Claim.** `superseded_penalty = 0.3` is a scalar approximation of a temporal-validity
predicate, and it is the single largest measured cause of wrong citations.

**Repo evidence.** **6 of 19** zero-cite rows are demotion-caused — more than B′ (4) or the
reranker (3). Two went from rank 0 to outside the window. The 2026-08-13 sweep showed the
penalty cannot be tuned out: 0.3→0.7 buys 3 citation rows while **quadrupling top-rank repealed
law** (stale@1 1→4); at 1.0 the top context is repealed law in 33% of rows.

**The repo already built the correct mechanism and only wired it to one path.** The 2026-08-15
`as_of` fix **excludes** superseded-on-as-of circulars from the context window rather than
penalising them — and `eval-asof` went 12/13 → **13/13**. The non-`as_of` path
(`pipeline.py:79`) still multiplies by 0.3.

**External.** [Can LLMs Time Travel? / LegalSearch-R1](https://arxiv.org/abs/2605.25920) — a
statute corpus with **13 amendment versions (2000–2025), each provision annotated with a
temporal validity window**; **+57.7–80.3%** on temporal-consistency metrics. Named failure
modes: post-cutoff staleness, and search agents not putting temporal constraints in queries.
[Deterministic Legal Agents / SAT-Graph API](https://arxiv.org/abs/2510.06002) — models legal
material as a **temporal knowledge graph** with typed, atomic, composable primitives for
*point-in-time retrieval, context reconstruction, provenance tracing, impact analysis*; keeps
structural/temporal traversal **deterministic** and confines uncertainty to semantic tasks;
answers grounded in an auditable log.

**The design that follows.** Every query carries an implicit `as_of = today`; "what did the rule
used to be / on what basis was X repealed" is an *explicit temporal intent*, not a scoring
accident. Supersession becomes a typed filter over the existing lineage graph
(`lineage.py`, `reg_lineage.py`, `Lineage`, `regulatory_basis_status`) rather than a rerank
multiplier. The repo has the graph; it is being consulted through a scalar.

**Why this ranks high.** Largest measured cause; strongest external grounding; **no dependency
on R0**; auditability is a first-class property in a legal tool; and the existing `as_of`
result (13/13) is direct in-repo evidence the exclusion semantics work.

---

### R3 — Eval-set validity: is retrieval actually saturated?  ⟨independent, cheap, highest-leverage-if-true⟩

**Claim.** Pool R@50 = 0.9861 across three arms may be a property of **golden_v7**, not of the
retriever. If so, "stop proposing retrieval interventions" is premature.

**External.** [CRAwLeR](https://arxiv.org/abs/2606.21676) builds a legal retrieval benchmark
where queries *genuinely require* cross-reference context (provisions citing provisions),
validated at ~80% construct validity. Best **Recall@10 = 55% (DK) / 59% (PL)** — *"challenging
but unsolved."* And critically: *"even when targets appear in top-ten results, labelled context
chunks routinely outrank it."*

**The contrast.** This repo reports R@10 **0.943** and pool R@50 **0.9861** on golden_v7. Either
SEBI circular retrieval is far easier than Danish/Polish statutory retrieval, or golden_v7
under-samples the cross-reference-dependent queries that make legal retrieval hard.

**Existing signals that it may be the latter.** `multi_hop` is only 20 of 260 rows; label tiers
are `model_single` 114 / human 38 / arbitrated 13; κ is low on `title_direct` (0.077),
`multi_hop` (0.071), `numeric_table` (0.000); 3 rows are unjudged.

**CS1 audited 2026-08-20** (`scripts/analysis/label_provenance.py`,
`reports/label-provenance-2026-08-20.json`) — the signal is stronger than the line above suggests:

- **179 of 260 rows (68.8%)** are model-labelled (`model_single` + `draft_seeded`). `review_status`
  is `adjudicated` for **all** 260, so `adjudicated_n` and the CI gate `adjudicated_n >= 100`
  count rows no human saw. `label_tier` is the field that carries provenance.
- **Verification runs inversely to difficulty.** `multi_hop` and `repealed_basis` are **90%**
  unverified (2 human labels each of 20); `numeric_table` 86.7%; `lineage_supersession` 85.0% —
  while `title_direct`, the easiest stratum, is the best verified at 25.0%.
- **85.4% of the abstain ground truth (35 of 41) was never human-verified**, and
  `abstention_accuracy` carries the gate's strictest floor (0.9412).
- **Null:** on answerable strata, `rerank_top` is indistinguishable between verified and
  unverified rows (0.8656 vs 0.8672). Weak labels cannot be spotted from scores — label quality is
  an independent axis, not a proxy for difficulty.

**This raises the stakes on R3 and folds into R0.** The adjudicator was itself a model
(`local_adjudicate` = Qwen3.6-35B-MLX). Evaluating a *model* against a *model-labelled* set
measures agreement-with-the-labeller alongside correctness, and the strata where a larger
generator should help most are the 85–90% model-labelled ones. Per the CS1 plan this is folded
into the outcome analysis rather than specced separately: **report the R0 delta split by
`label_tier`** — similar on human-verified and model-labelled rows means the gain is real;
concentrated in the latter means it is partly labeller agreement. ⚠️ Blocked on a harness fix —
`eval_json.py` discards its per-row records, so no completed gate run can be decomposed after the
fact (staged opt-in `SEBI_RAG_EVAL_ROWS` dump; not applied while an arm is mid-flight).

**Why it's cheap.** `reg_citations.py` and `reg_lineage.py` **already extract** circular→circular
and circular→regulation edges, and `data/manifests/regulation_edges.jsonl` exists. A
CRAwLeR-style cross-reference stratum can be mined from machinery already built and validated —
no new extraction.

**Why it matters most.** It is the one item that can *invalidate a standing conclusion*. If a
cross-reference stratum drops R@10 substantially, the saturation finding is scoped to
golden_v7 and the retrieval surface reopens. If it doesn't, the saturation finding is
strengthened and R5/R6 can be cut with confidence. Either outcome is decision-relevant, which
is what makes it worth doing first among the independent items.

---

### R4 — Reranker architecture: inter-passage attention  ⟨independent⟩

**Claim.** The reranker lever was declared exhausted on the strength of *combiner* experiments,
never an architecture change.

**Repo evidence.** Reranker ordering causes 3 of 19 zero-cite rows. The 2026-08-13 work tested
RRF variants and rank-caps — all within ±1 of baseline, non-monotonic in the cap parameter. That
is evidence that *fusion combiners* are exhausted, not that bge-reranker-v2-m3 is optimal.
Separately, `doc_id` dedup exists precisely because near-duplicate chunks from one document
stack in the top-k — a pointwise scorer cannot see that.

**External.** [Set-Encoder (ECIR'25)](https://arxiv.org/abs/2404.06912) — permutation-invariant
inter-passage attention in a cross-encoder; matches state-of-the-art listwise effectiveness
while remaining efficient and **invariant to input passage order**, and is *"particularly more
effective when considering inter-passage information, such as novelty."*

**Explicitly not the move:** RankGPT-style listwise LLM reranking. Current evidence is that a
calibrated pointwise cross-encoder matches or beats listwise LLM rerankers at **100–1000× lower
cost/latency** on production RAG benchmarks. Set-Encoder gets the inter-passage signal at
cross-encoder cost, which is the whole point.

**Direct fit.** "Which of these near-identical chunks is the governing one" is an inter-passage
question — the same question `doc_id` dedup and `demote_superseded` are both crudely
approximating.

---

### R5 — Tables at ingest  ⟨gated on a diagnostic⟩

**Measured on this corpus (2026-08-19, `scratchpad/table_frag_probe.py`).**

```yaml
tabular_chunks:           1579   # 2.01% of 78,630
docs_with_tables:          163   # 22.3% of 730 circulars
fragmented_chunks:         291   # 18.4% of tabular — open/close mid-table
multi_space_column_gaps: 0/7986  # column structure destroyed at ingestion
```

**External.** Paper A: **table structure mismatch = 73%** of retrieval failures; TAT-DQA
**35.6%** top-5 failure. [TableRAG (EMNLP'25)](https://arxiv.org/abs/2506.10380): SQL-based —
query decomposition → text retrieval → SQL execution → compositional answer.

**Fix location is `ingest_pdf.py`, not `segment.py`.** pdfplumber's `extract_text()` collapses
column gaps to single spaces before chunking ever runs; a `|`/whitespace detector finds zero
tables here. Cost = re-ingest 730 PDFs → re-chunk → full re-encode (~50 min) ×2.

**Gate it.** Attribute the `numeric_table` zero-cite rows to fragmentation *before* paying.
If those rows are demotion- or B′-caused, this buys nothing — and R2/R1 would already fix them.

---

### R6 — Chunk quality: late chunking + degenerate fold  ⟨partly depends on R0⟩

**Measured.** 6,736 chunks (**8.57%**) have bodies under 80 characters — typically a section
heading restated. Reproduces the ~9.6% figure behind the known nominee-count wrong answer.

**External.** [Late chunking](https://arxiv.org/abs/2409.04701) — embed the full document, chunk
token embeddings after the transformer and before mean pooling. Requires **no training**, adds
**no text**, and is applicable to a range of long-context embedders. Anthropic-style contextual
retrieval (LLM summaries, 5–15% reported gains) is the higher-cost alternative and needs R0.

**Why this is not a repeat of iv9/iv10.** §1.3 — those tested a one-sentence header. Late
chunking changes the *embedding procedure*, not the chunk text, and would give the 6,736
degenerate chunks document context they currently lack entirely.

**Constraint.** bge-m3 supports 8192 tokens, so late chunking is feasible without changing the
embedder. Still a full re-encode; **bundle with R5** if both proceed.

---

### R7 — Calibrated abstention instead of fitted thresholds  ⟨independent⟩

**Repo evidence.** Threshold tuning is measured dead twice. The gate is a conjunction
(`rerank_top ≥ 0.05` **AND** subject gate) so either noisy signal vetoes alone. The repo's own
words on the one surviving lead: *"any threshold picked here is fitted to the observed maximum —
textbook overfitting."*

**External.** Conformal abstention supplies exactly what a fitted threshold cannot: a post-hoc,
distribution-free **coverage guarantee** rather than a point estimate tuned on the observed
maximum. [R2C](https://arxiv.org/abs/2510.11483) reports **>5% AUROC** over SOTA baselines and
**~5%** gains in F1Abstain/AccAbstain by perturbing reasoning steps to capture retrieval- and
generation-side uncertainty jointly — which is the two-signal problem the AND-gate handles
crudely.

**Fit.** A legal tool that must justify refusals benefits more from a calibrated risk level than
from a hand-tuned pair of thresholds. This also gives the 41 abstain rows a principled home
without the held-out data golden_v7 lacks.

---

## 3. What not to do

| Rejected | Reason |
|---|---|
| More RRF fusion legs | Pool R@50 saturates at 0.9861 across three arms — **unless R3 shows this is a golden_v7 artifact** |
| Listwise LLM reranker (RankGPT-style) | 100–1000× cost/latency for parity with a calibrated pointwise cross-encoder |
| Generation-time citations | Post-hoc wins for law ([2509.21557](https://arxiv.org/abs/2509.21557)); and Option A measured 0/48 at 1.5B |
| Another NLI/entailment scorer for B′ | Rejected twice; [2605.28044](https://arxiv.org/abs/2605.28044) explains why — warrant is a third criterion, not entailment |
| Fixed-size chunking | The cited survey finds recursive-semantic **beats** fixed-size (89.36 vs 87.71) and never evaluates tables |
| Lowering `superseded_penalty` | Trades citation correctness for surfacing repealed law; stale@1 quadruples at 0.7. R2 replaces the mechanism instead |

---

## 4. Suggested sequence

```
R3 (eval validity)  ──┬─→ decides whether retrieval surface reopens
R2 (temporal typing) ─┘   both independent, both cheap relative to payoff
        │
R0 (generator) ───────┬─→ R1 (warrant scorer)
                      └─→ R6b (contextual retrieval, if late chunking underdelivers)
R4 (Set-Encoder) ─────── independent
R5 / R6 ──────────────── bundle; gate R5 on its diagnostic
```

**R3 and R2 first** — neither depends on R0, both are cheap, and R3 can invalidate a standing
conclusion. R0 is the largest unlock but also the largest cost (gate re-derivation), so it
should follow the two items that might change what you want from it.

---

## 5. Sources

All verified against primary text on 2026-08-19; evaluation scope stated.

| # | Work | arXiv | Scope evaluated |
|---|---|---|---|
| A | From BM25 to Corrective RAG (benchmark) | [2604.01733](https://arxiv.org/abs/2604.01733) | 10 strategies, financial QA, 23k queries / 7.3k docs, text+tables |
| B | Chunking Methods on RAG | [2606.00881](https://arxiv.org/abs/2606.00881) | 8 methods, 9 reading-comprehension datasets, **no tabular data** |
| C | Impact of Quantization on RAG | [2406.10251](https://arxiv.org/abs/2406.10251) | **7B/8B only**, FP16 vs INT4 |
| D | TableRAG (EMNLP 2025) | [2506.10380](https://arxiv.org/abs/2506.10380) | SQL-based heterogeneous doc reasoning; HeteQA |
| E | Can LLMs Time Travel? / LegalSearch-R1 | [2605.25920](https://arxiv.org/abs/2605.25920) | 13 amendment versions 2000–2025, temporal validity windows, 13 tasks |
| F | Deterministic Legal Agents / SAT-Graph API | [2510.06002](https://arxiv.org/abs/2510.06002) | Temporal knowledge graph, typed primitives, point-in-time retrieval |
| G | Relevant Is Not Warranted (FORCEBENCH) | [2605.28044](https://arxiv.org/abs/2605.28044) | 198 paired items, 5 warrant dimensions |
| H | Generation-Time vs. Post-hoc Citation | [2509.21557](https://arxiv.org/abs/2509.21557) | Both paradigms, high-stakes domains incl. law |
| I | Late Chunking | [2409.04701](https://arxiv.org/abs/2409.04701) | Long-context embedders, no training required |
| J | Set-Encoder (ECIR 2025) | [2404.06912](https://arxiv.org/abs/2404.06912) | TREC DL + TIREx, listwise cross-encoder |
| K | CRAwLeR | [2606.21676](https://arxiv.org/abs/2606.21676) | Danish + Polish legal cross-reference retrieval |
| L | R2C — UQ for Retrieval-Augmented Reasoning | [2510.11483](https://arxiv.org/abs/2510.11483) | 5 RAR systems, abstention + model selection |

**Not used:** Proposition Chunking (MDPI) — paywalled, unread. Cited nowhere above.
