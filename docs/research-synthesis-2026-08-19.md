# Research Synthesis: SEBI RAG Optimization Targets

**Date:** 2026-08-19
**Revised:** 2026-08-19 (corrections applied — see §0)
**Purpose:** Map external literature findings to the live surfaces of the SEBI RAG system.
**Status:** Claims below are verified against primary sources and repo ground truth. Every
external number carries the retrieval date; every repo number carries its source file.

---

## 0. Correction Log

The first draft of this file was produced without checking its sources against their primary
texts or its repo claims against the code. Five load-bearing claims were wrong. They are
recorded here rather than silently deleted, because the failure mode matters more than the
individual errors.

| # | Original claim | Verified reality | Effect |
|---|---|---|---|
| C1 | "Fixed-size chunking wins on tabular data (PoQuAD)" | PoQuAD is a multi-domain **reading-comprehension** set. The survey evaluates **no tabular dataset** and makes **no claim about tables**. | P1's entire cited justification **void** |
| C2 | "PoQuAD: fixed 96.39 vs recursive semantic 97.68 — fixed-size wins" | 96.39 **<** 97.68. Fixed-size *loses* on the quoted line, and on average (87.71 vs 89.36). | Conclusion contradicted by its own evidence |
| C3 | "PTQ weakens RAG; 4-bit models struggle with instruction following" | Paper's headline: *"if a 7B LLM performs the task well, quantization does not impair its performance and long-context reasoning."* Tested **7B/8B only, never 1.5B**. | P0's stated mechanism **inverted** |
| C4 | "BM25 ... via SPLADE ... may be a different sparse encoder" | `retrieve.py:12` `import bm25s`; `:55` `"""BM25 lexical index (bm25s)."""`; `:58` `bm25s.BM25()`. SPLADE is an opt-in **eval-only** third leg with an absent sidecar. | Architecture guessed, not read |
| C5 | "citation precision 0.194 → closer to 0.872 floor" | `citation_precision` floor is **0.1577** (`gate_v7.json`). 0.872 is a citation *recall* figure. **0.194 already passes** (+0.034). | P0 aimed at a metric that is not failing |

**The pattern (C1–C3).** All three are real papers whose findings were bent toward a
pre-formed conclusion. C1/C2 assert a claim the paper does not make *and* quote numbers that
refute it — the numbers were transcribed correctly and then narrated backwards. C3 inverts a
null result into a positive one. This is not citation fabrication; it is worse-behaved than
that, because every ID resolves and every number is checkable, so the errors survive a
spot-check that stops at "does the paper exist."

**Guard adopted:** a cited paper must have (a) its claim quoted from the abstract or results
text, not paraphrased from a title, and (b) its evaluation scope stated — what was tested, on
what data. A claim about tables requires a paper that evaluated tables. A claim about 1.5B
requires a paper that tested 1.5B.

---

## 1. Sources Reviewed

| # | Paper | arXiv | Verified | Scope actually evaluated |
|---|---|---|---|---|
| A | *From BM25 to Corrective RAG: Benchmarking Retrieval Strategies for Text-and-Table Documents* — Akarsu, Karaman, Mierbach | [2604.01733](https://arxiv.org/abs/2604.01733) | ✅ 2026-08-19 | 10 retrieval strategies, financial QA, 23k+ queries / 7.3k docs, text **and tables** |
| B | *Chunking Methods on RAG — Effectiveness Evaluation Against Computational Cost and Limitations* — Śmigielski et al. (Wrocław UST) | [2606.00881](https://arxiv.org/abs/2606.00881) | ✅ 2026-08-19 | 8 chunking methods, 9 **reading-comprehension** datasets. **No tabular data.** |
| C | *The Impact of Quantization on RAG: An Analysis of Small LLMs* — Yazan, Verberne, Situmeang | [2406.10251](https://arxiv.org/abs/2406.10251) | ✅ 2026-08-19 | **7B and 8B only**, FP16 vs INT4, personalization tasks, 3 retrieval models |
| D | *TableRAG: A RAG Framework for Heterogeneous Document Reasoning* — Yu, Jian, Chen (EMNLP 2025) | [2506.10380](https://arxiv.org/abs/2506.10380) | ✅ 2026-08-19 | SQL-based; query decomposition → text retrieval → SQL exec → compositional answer; HeteQA benchmark |

> ⚠️ **Naming.** Paper A is a *benchmark* paper whose title ends at Corrective RAG; it is not
> the CRAG method paper (Yan et al., [2401.15884](https://arxiv.org/abs/2401.15884)). The first
> draft cited it as "Corrective RAG," which misattributes the contribution.

---

## 2. Paper A → Retrieval & Table Surface

### What it actually reports

Recall@5, financial text-and-table corpus:

| Strategy | Recall@5 |
|---|---|
| Dense alone | 0.587 |
| **BM25 alone** | **0.644** |
| Hybrid RRF | 0.695 |
| Hybrid + cross-encoder rerank | **0.816** |

- **r > 0.99** between Recall@5 and *Number Match* — i.e. correlation with **numeric extraction
  accuracy**, not general answer quality. Do not over-generalise it.
- **BM25 (0.644) beats dense (0.587)** on financial documents, "challenging the common
  assumption that semantic search universally dominates."
- Dominant failure mode: **table structure mismatch, 73%** of examined cases. Embedding models
  fail to match *"what was net income in 2019?"* to rows where `net income` and `2019` sit in
  separate cells.
- **TAT-DQA** (table subset) is hardest: **35.6% top-5 failure rate** for hybrid retrieval.
- Query expansion (HyDE, multi-query) and adaptive retrieval give **limited benefit for precise
  numerical queries**; contextual retrieval yields **consistent gains**.

### Mapping to SEBI RAG

- ✅ Cross-encoder reranking already in production (`rerank.py:115`, bge-reranker-v2-m3).
- ✅ **External corroboration of two of our nulls.** The HyDE/multi-query finding independently
  reproduces iv8 (HyDE rejected, Δ −2.31 pp, 41× latency) and iv2 (glossary expansion, exact
  0.000000 no-op). Two nulls that cost real effort are now externally supported.
- ⚠️ **Open tension, unresolved.** "Contextual retrieval yields consistent gains" **contradicts**
  our iv9/iv10 results (headers null at nDCG@10 +0.0033 / +0.0018, R@10 −0.0093 / ±0.0000),
  despite 18,086 chunks — 23% — verifiably changing text. Either the corpora differ in a way
  that matters, or their "contextual retrieval" is not our "contextual headers." **Worth
  resolving before any further chunk-text intervention.**
- ⚠️ **BM25 > dense is a live question for D2/D3.** Our design pins bge-m3 as the dense baseline
  and defers its sparse/ColBERT heads to avoid fusion double-counting. On financial text the
  lexical leg may deserve more RRF weight. Cheap to test — no re-encode required.
- This is the paper that supports **table work**, not paper B.

---

## 3. Paper B → Chunking Surface

### What it actually reports

Average Accuracy@5 across 9 datasets:

| Method | Avg Accuracy@5 |
|---|---|
| **Recursive Semantic** | **89.36** |
| Fixed-Size | 87.71 |
| GraphSeg | 86.85 |
| Max-Min | 85.75 |
| LumberChunker | 85.44 |
| TextTiling | 84.96 |
| Sequential HAC | 80.09 |
| DenseX | 69.10 |

Datasets: GutenQA, LiteraryQA, NovelQA, Qasper, Natural Questions, SQuAD, TriviaQA, PoQuAD,
plus merged stress-test variants. **All reading-comprehension. None tabular.**

PoQuAD specifically: Fixed-Size **96.39**, Recursive Semantic **97.68**.

### Mapping to SEBI RAG

❌ **This paper does not support table-aware or fixed-size chunking.** It never evaluates
tabular data and makes no claim about it. Its actual finding — recursive semantic > fixed-size,
on average and on PoQuAD — argues *against* the change the first draft proposed.

✅ What it does support: DenseX/embedding-based chunking underperforms badly (69.10); GraphSeg
and LumberChunker hit timeouts and memory failures, so they are not production-viable. Our
hierarchical chunker is closer to recursive-semantic than to any rejected method.

**The table-fragmentation hypothesis survives — but on our own measurement (§5), not on this
paper.**

---

## 4. Paper C → Generator Surface

### What it actually reports

Post-training quantization (FP16 vs INT4) on **7B and 8B** models, personalization tasks,
varying retrieved-document counts, 3 retrieval models. Headline:

> *"if a 7B LLM performs the task well, quantization does not impair its performance and
> long-context reasoning capabilities."*

This is close to a **null result for quantization at 7B**. The paper did **not** test 1.5B.

### Mapping to SEBI RAG

❌ **It cannot diagnose our failures as quantization damage.** Our generator is
Qwen2.5-1.5B-Instruct-4bit (`generate.py:408`), below the tested range. The competing and more
parsimonious explanation — 1.5B simply lacks the capability, quantized or not — is untested by
this paper.

✅ **It does de-risk the destination.** It is evidence that a 7B at 4-bit retains grounding and
long-context reasoning. That supports 7B-4bit as the *target*, while saying nothing about the
*cause* at 1.5B.

✅ **The real evidence for a generator upgrade is in-repo**, and it is strong — two independent
instruction-following no-ops:

| Probe | Result | Source |
|---|---|---|
| Option A selective citations | **0 / 48** parseable bracket citations; 100% fallback to mechanical cite-all | `scratchpad/probe_fallback.py`, status.md |
| CE paraphrase rescue (arm R1) | **74.2%** degenerate rewrites (23/31); both targets returned **verbatim** | `reports/ce-rescue-cohort-2026-08-19.json` |

---

## 5. Measured On This Corpus (2026-08-19)

Run against the live index (`data/index/chunks.jsonl`, 78,630 chunks / 730 circulars). Probe:
`scratchpad/table_frag_probe.py`.

```yaml
tabular_chunks:            1579     # 2.01% of index
docs_with_tables:           163     # 22.3% of 730 circulars
fragmented_chunks:          291     # 18.4% of tabular — open or close mid-table
  opens_mid_table:          104
  closes_mid_table:         221
degenerate_bodies:         6736     # 8.57% — body <80 chars after stripping F1 header
multi_space_column_gaps:  0/7986    # of numeric-dense chunks
body_chars_p50:             353
body_chars_p95:            1196
```

**Tables are fragmented — confirmed.** Chunk `#1583` of
`HO/24/13/11(1)2026-IMD-POD-1/I/7602/2026` opens with `5 5-25 0-10`: the tail of a row whose
leading cells are in chunk `#1582`.

**But the proposed fix cannot work.** `multi_space_column_gaps: 0/7986` and no pipe characters:
pdfplumber's `extract_text()` collapses every column gap to a single space **at ingestion**.
Column structure is destroyed before `segment.py` ever runs. A detector keyed on `|` or
whitespace-column patterns finds **zero** tables in this corpus.

Worse, headers are decoupled from data even *within* one chunk:

```
Years to    Investment in Equity   Investment in Debt (%)   Investment in Gold/Silver
Maturity    (%)                    ETFs/ETCDs/InvITs (%)
15-30 Years 65-95                  5-25                     0-10
```

renders as two wrapped header lines followed by bare numeric rows — exactly Paper A's 73%
**table structure mismatch** failure mode.

**Correct fix location:** `ingest_pdf.py`, via pdfplumber `extract_tables()` (or a
structure-preserving serialisation), **not** `segment.py`. Cost is re-ingest of 730 PDFs →
re-chunk → full re-encode (~50 min) ×2 to restore baseline — not "~50–100 lines."

**Also measured: 6,736 degenerate chunks (8.57%)** whose entire body is under 80 characters,
typically a section heading restated. Independently reproduces the ~9.6% heading-only figure
behind the known nominee-count wrong answer.

---

## 6. Revised Priorities

Reprioritised against the repo's own instrumented zero-cite decomposition (19 rows):
**demotion 6, B′ 4, reranker 3, subject_gate 3, score_floor 2, non-SEBI FP 1.**
Chunking does not appear in it.

### P0 — Generator upgrade (1.5B-4bit → 7B-4bit)

- **Why:** two in-repo instruction-following no-ops (§4). Paper C supports the destination.
- **NOT a 1-line change.** `eval_generator = "mlx"` couples floor-derivation
  (`derive_thresholds.py`) and measurement (`eval_json.py`) through
  `generate.eval_generator_for`, enforced by three coupling tests. The stub→MLX precedent moved
  two floors (citation_recall 0.7233→0.8124; citation_precision 0.1896→0.1571). Scope is
  **config change + full gate re-derivation + re-arm.**
- **Cost/risk to check first:** `timeout_s = 30` against 2.1 s warm at 1.5B; eval runtime ~38
  min at 1.5B over 260 rows; bug **B3** (dual-model-on-MPS segfault) with bge-m3 +
  cross-encoder + MLX co-resident on 48 GB.
- **Target the right metric:** zero-cite rows and citation **recall**. `citation_precision`
  0.194 already clears its 0.1577 floor (C5).

### P1 — Supersession-vs-citation conflict *(new — displaces table chunking)*

- **Why:** `demote_superseded` (penalty 0.3) is the **single largest measured cause** of
  zero-cite (6 of 19), ahead of B′ (4). Unaddressed in the first draft.
- The labelled-relevant circular is often itself superseded — which for `lineage_supersession`
  and `repealed_basis` strata is precisely what the question asks about.
- Do **not** simply lower the penalty: the 2026-08-13 sweep showed 0.3→0.7 buys 3 citation rows
  while quadrupling top-rank repealed law (stale@1 1→4). Needs a mechanism that separates
  *"superseded, and that is the answer"* from *"superseded, do not surface."*
- External grounding: §7 below.

### P2 — Table extraction at ingest *(demoted from P1)*

- Premise **confirmed** (§5: 18.4% of tabular chunks fragmented) but cited justification void
  (§3), fix location wrong, and blast radius small (2.01% of chunks, 22.3% of circulars).
- **Gate it behind a diagnostic**: attribute the `numeric_table` zero-cite rows (11/30) to
  fragmentation *before* paying for re-ingestion. If those 11 rows are demotion- or
  B′-caused, this buys nothing.
- If pursued, Paper D (TableRAG) is the relevant design reference, not Paper B.

### P3 — Degenerate chunks *(new — measured 2026-08-19)*

- 6,736 chunks (8.57%) with sub-80-char bodies dilute the candidate pool and have a known
  wrong-answer attached (nominee count).
- Cheap relative to P2: a chunker-level fold of bodyless headings into their subsection. Still
  requires a re-encode, so **bundle with P2** if both proceed.

### P4 — Prompt strengthening

- Retained at low priority, but note it was measured **inert at 1.5B** (0/48 brackets). It
  becomes worth retrying only *after* P0. Sequencing matters: this is not an independent lever.

---

## 7. Rejected Interventions (corrected reasons)

| Intervention | Correct reason for rejection |
|---|---|
| Threshold tuning (gate / score floor) | Measured dead 2026-08-13 and re-confirmed 2026-08-19. Score floor catches **29 of 41** correct abstentions and costs **2 of 204** answerable; the 2 false abstentions (0.0114, 0.0296) sit **inside** the true-positive band (0.0001–0.0462), first correct abstention above floor at 0.0578. Subject-sim interleaves at 0.4062–0.4148. No threshold separates either. |
| NLI attribution scorer (B′ backend) | **Not** "latency without precision gain" — precision *rose* 0.1948→0.2204. Rejected because zero-cite went **19→54**, citation_recall 0.8981→0.7354, Δ +0.1699 worse, **p = 0.0001**, fixed 2 rows / broke 37. Conclusion: entailment is the wrong criterion — a context can be the governing provision without textually entailing a paraphrase of it. |
| Query expansion (statutory glossary) | iv2 measured **exact 0.000000 no-op**, 0/216 discordant, toggle verified live. Externally corroborated by Paper A (limited benefit for numerical queries). |
| HyDE third leg | iv8: Δ −2.31 pp, p = 0.177, **41× latency**. Corroborated by Paper A. |
| SPLADE third leg | iv11 rejected on **preregistered held-out confirmation** (probes n=25, nDCG@10 Δ −0.0068, p = 0.865) after an exploratory p = 0.032 that did not replicate. |
| Further RRF-fusion legs | Pool R@50 saturates at **0.9861** across three independent arms — ≤1.4 pp headroom. Structural, not incidental. |
| Proposition chunking | Paywalled; unverified. **Do not cite until read.** |

---

## 8. Method Note

Every external claim in this revision was checked against the paper's abstract or full text on
2026-08-19 and is quoted rather than paraphrased. Every repo claim cites a file and line, or an
artifact under `reports/`. §5 numbers are reproducible via `scratchpad/table_frag_probe.py`
against `data/index/chunks.jsonl` at 78,630 chunks.

Claims that could not be verified are marked as such and are not used to justify any priority.
