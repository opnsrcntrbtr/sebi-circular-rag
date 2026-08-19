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
| 7B-4bit | 8.91 GB | 12.36 s | **38.20 s** | **3 of 20** | 69.9 min |

- ✅ **Bug B3 retired** — no segfault at any size; 8.91 GB peak of 48 GB.
- ✅ **Gate cost is 69.9 min at 7B, not 2–3 h.** The earlier estimate was wrong by ~2.5×.
- ❌ **`timeout_s = 30` is breached at 7B** on 15% of rows, and it is *not* an output-length
  effect (corr(chars, latency) = 0.154), so `max_tokens` will not fix it.
- **Revised target: 3B first.** Clears the timeout with margin at 1.45× cost. The open
  question — does it follow citation instructions where 1.5B scored 0/48? — is answerable by a
  ~50-row screen before any gate work.

**Decision rule (preregister).** Primary = zero-cite rows on the perfect-retrieval cohort,
**recomputed on the live index and persisted with its corpus hash** — the cohort is not a stored
artifact and is index-dependent (R2 measured 201 of 204 eligible where the prior index gave 206;
every prior-index reference value was wrong). Guardrails: **zero rows over `timeout_s`** (not a
p95 estimate — at n=20 the p95 equals the max by construction); `citation_precision` ≥ 0.1577;
`abstention_accuracy` ≥ 0.9412. Target `citation_recall` / zero-cite — **not**
`citation_precision`, which already clears its floor at 0.194.

**Sequence.** Screen 3B for mechanism-firing (~50 rows, ~10 min) *before* any gate work — the
documented failure is total (0/48 brackets), so a screen kills or licenses the arm cheaply. Only
if 3B fails to fire does 7B become worth its timeout problem.

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
