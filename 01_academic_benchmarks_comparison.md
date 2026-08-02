# Academic Benchmarks & SOTA RAG Systems: Comparison for SEBI Circular RAG Gap Analysis

> **Date:** 2026-07-31
> **Purpose:** Baseline existing financial/legal RAG systems against SEBI Circular RAG for gap analysis
> **Scope:** Academic benchmarks, arXiv papers (2024–2026), open-source systems

---

## 1. Academic Benchmarks — Financial & Legal QA/Retrieval

### 1.1 Financial Domain Benchmarks

| Benchmark | Year | Size | Source Corpus | Task Type | Retrieval Metrics | RAG-Focused? | Temporal/Supersession Handling |
|-----------|------|------|---------------|-----------|-------------------|--------------|-------------------------------|
| **FiQA 2018** (BEIR) | 2018 | ~3,000 queries | Financial news headlines + microblog posts | Aspect-based sentiment + opinion QA | nDCG@10, Recall@k (BEIR standard) | No — IR benchmark only | ❌ None |
| **FinQA** (Chen et al.) | 2021 | 8,376 QA pairs over 2,849 financial reports | SEC 10-K/10-Q earnings reports | Numerical reasoning QA (code generation) | Accuracy, Execution Match | No — focuses on code execution | ❌ None |
| **ConvFinQA** (Zhu et al.) | 2022 | ~14,000 multi-turn QA pairs | Financial reports (same as FinQA) | Conversational numerical reasoning | Accuracy, Execution Match | No — multi-turn QA only | ❌ None |
| **TAT-QA** (Zhu et al.) | 2021 | 16,552 QA pairs over 2,757 hybrid contexts | Real-world financial reports (text + tables) | Hybrid tabular+textual QA with numerical reasoning | Exact Match, Execution Accuracy | No — focuses on table-text fusion | ❌ None |
| **FinanceBench** (Islam et al.) | 2023 | 10,231 QA triplets (Q+A+evidence) | U.S. SEC filings (10-K, 10-Q, 8-K) | Open-book financial QA with evidence strings | LLM-as-judge pairwise accuracy, hallucination rate | Partial — provides evidence strings but no retrieval evaluation framework | ❌ None |
| **FinDER** (Choi et al.) | 2025 | 5,703 query-evidence-answer triplets | Real-world financial inquiries (expert-annotated) | RAG evaluation — expert-generated ambiguous queries with evidence spans | Retrieval precision, LLM answer accuracy | ✅ Yes — explicitly designed for RAG evaluation | ❌ None |
| **FinRetrieval** (Kim & Huang) | 2026 | 500 financial retrieval questions + tool traces | Structured databases (APIs, web search) | AI agent retrieval from structured data | Accuracy by tool type (structured API vs. web search) | ✅ Yes — agent retrieval benchmark | ❌ None |
| **SEC-QA** (Lai et al.) | 2024 | Continuous generation framework | SEC filings (continuously refreshed) | Multi-document financial QA with program-of-thought reasoning | Accuracy on multi-document questions | Partial — focuses on multi-doc reasoning, not retrieval metrics | ❌ None |
| **FinRED** (Sharma et al.) | 2023 | Relation extraction triples from financial news/earnings calls | Financial news + earnings call transcripts | Relation extraction (not QA/retrieval) | F1 for relation classification | ❌ Not a retrieval benchmark | ❌ None |

### 1.2 Legal Domain Benchmarks

| Benchmark | Year | Size | Source Corpus | Task Type | Retrieval Metrics | RAG-Focused? | Temporal/Supersession Handling |
|-----------|------|------|---------------|-----------|-------------------|--------------|-------------------------------|
| **LegalBench** (Guha et al.) | 2023 | 162 tasks, collaboratively built | Legal reasoning tasks from 40 contributors | LLM legal reasoning (rule application, case comparison, statutory interpretation) | Accuracy per task type | ❌ Evaluates generation only, not retrieval | ❌ None — static legal reasoning tasks |
| **CaseHOLD** (Zheng & Guha) | 2021 | 53,000+ multiple-choice questions | Harvard Law case corpus (3.7M cases) | Legal holdings prediction (cite matching) | Accuracy, F1 | ❌ Classification task, not retrieval | ❌ None — case citation matching only |
| **LegalBench-RAG** (Pipitone & Alami) | 2024 | 6,858 query-answer pairs over 79M chars | Legal corpus (human-annotated by legal experts) | **Precise snippet retrieval** in legal documents | Retrieval precision, citation accuracy | ✅ Yes — first benchmark for legal RAG retrieval step | ❌ None — focuses on snippet precision, not temporal logic |
| **Legal RAG Bench** (Butler & Butler) | 2026 | 4,876 passages + 100 complex questions | Victorian Criminal Charge Book | End-to-end legal RAG evaluation with hierarchical error decomposition | Correctness, groundedness, retrieval accuracy (full factorial design) | ✅ Yes — end-to-end RAG benchmark with retrieval+reasoning separation | ❌ None — static legal corpus |

### 1.3 General IR Benchmarks (with Financial/Legal subsets)

| Benchmark | Year | Datasets Included | Key Metrics | Relevance to SEBI Circular RAG |
|-----------|------|-------------------|-------------|-------------------------------|
| **BEIR** (Thakur et al.) | 2021 | 18 heterogeneous datasets including **FiQA** (financial), NFCorpus (medical) | nDCG@10, Recall@k, MRR | ✅ FiQA subset is directly relevant for financial QA retrieval evaluation |
| **NFCorpus** (BEIR subset) | 2016 | 3,244 queries over 169K medical documents | nDCG@10, ΔnDCG@10 | ⚠️ Medical domain — structural similarity to legal documents (long, jargon-heavy) |

---

## 2. Key arXiv Papers (2024–2026) — Financial/Legal RAG Systems

### 2.1 Financial Filings RAG

| Paper | Year | Key Innovation | Retrieval Architecture | Metrics Used | Temporal Handling |
|-------|------|----------------|------------------------|--------------|-------------------|
| **FinSage** (Wang et al., arXiv:2504.14493) | 2025 | Multi-aspect RAG for multi-modal financial filings (text + tables + diagrams) | Multi-path sparse-dense retrieval + HyDE query expansion + metadata-aware semantic search + DPO fine-tuned re-ranker | Recall: **92.51%** on 75 expert questions; accuracy +24.06% over FinanceBench baseline | ❌ None — no temporal/supersession modeling |
| **PwC: Rethinking Retrieval** (Lumer et al., arXiv:2511.18177) | 2025 | Systematic comparison of vector-based vs. hierarchical node-based RAG for SEC filings | Vector-based agentic RAG with hybrid search + metadata filtering; cross-encoder reranking (+59% MRR@5); small-to-big chunk retrieval | MRR, Recall@5, LLM-as-judge pairwise accuracy, latency (5.2s), cost | ❌ None — no temporal modeling |
| **Citation-Enforced RAG for Fiscal Documents** (Shanivendra, arXiv:2603.14170) | 2026 | Multimodal citation-enforced RAG for tax compliance with source-first ingestion, page-level provenance | Source-first ingestion + citation enforcement during generation + **abstention when evidence insufficient** | Citation fidelity, hallucination reduction, analyst-usable explanations | ⚠️ Partial — handles jurisdiction-specific guidance but no explicit temporal versioning |

### 2.2 Legal RAG Systems

| Paper | Year | Key Innovation | Retrieval Architecture | Metrics Used | Temporal Handling |
|-------|------|----------------|------------------------|--------------|-------------------|
| **LegalBench-RAG** (Pipitone & Alami, arXiv:2408.10343) | 2024 | First benchmark for legal RAG retrieval — precise snippet-level retrieval over document IDs/chunks | Evaluates any IR system; focuses on minimal relevant snippets (not doc-level) | Retrieval precision, citation accuracy | ❌ None |
| **Towards Reliable Retrieval in Legal RAG** (Reuter et al., arXiv:2510.06999) | 2025 | **Summary-Augmented Chunking (SAC)** to reduce Document-Level Retrieval Mismatch (DRM) in legal datasets | Standard chunking + synthetic document-level summary appended to each chunk; generic summarization outperforms legal-expert targeting | DRM rate, text-level precision/recall | ❌ None — addresses chunking mismatch, not temporal logic |
| **Legal RAG Bench** (Butler & Butler, arXiv:2603.01710) | 2026 | End-to-end legal RAG benchmark with full factorial design + hierarchical error decomposition separating retrieval vs. reasoning contributions | Evaluates 3 embedding models (Kanon 2, Gemini Embedding 001, Text Embedding 3 Large) + 2 LLMs (Gemini 3.1 Pro, GPT-5.2) | Correctness, groundedness, retrieval accuracy (factorial design) | ❌ None — static Victorian Criminal Charge Book corpus |
| **Ontology-Driven Graph RAG for Legal Norms** (de Martim, arXiv:2505.00039) | 2025 | **SAT-Graph RAG** — explicitly models hierarchical, diachronic (temporal), and causal structure of legal norms using ontology-driven knowledge graph | Knowledge graph with: abstract Works vs. versioned Expressions; temporal states as aggregations of versioned expressions (CTVs); legislative events as first-class Action nodes; planner-guided query strategy | Case study on Brazilian Constitution — qualitative demonstration of temporal correctness, provenance reconstruction | ✅ **YES** — explicit temporal versioning (point-in-time retrieval, amendment tracking, supersession resolution) |

### 2.3 Regulated-Domain RAG (Open Source)

| System | Year | Key Innovation | Retrieval Architecture | Metrics Used | Temporal Handling |
|--------|------|----------------|------------------------|--------------|-------------------|
| **regulated-rag** (RZ-Logic, GitHub) | 2026 | Citation-grounded + refusal-bounded RAG for regulated domains (FDCPA corpus) | **Hybrid: Vector + BM25 → RRF (k=60) → Cross-encoder rerank (Cohere v3.5)**; deterministic refusal at 0.30 threshold; post-generation set-membership citation validator | Retrieval precision@5: 100%; Citation recall: 0.833; Faithfulness: 84% | ❌ None — single-version corpus, no temporal modeling |

---

## 3. Gap Analysis: What SEBI Circular RAG Does Uniquely vs. Baselines

### 3.1 Comparison Matrix by Capability Dimension

| Capability Dimension | SEBI Circular RAG (assumed) | FinSage | LegalBench-RAG | SAT-Graph RAG | regulated-rag | FinanceBench/FinDER |
|---------------------|----------------------------|---------|----------------|---------------|---------------|---------------------|
| **Hybrid dense+sparse+RRF retrieval** | ✅ (assumed) | ✅ Sparse-dense multi-path | ❌ Not specified | ❌ Graph-based, not hybrid vector+BM25 | ✅ Vector + BM25 → RRF (k=60) → reranker | ❌ Not retrieval-focused |
| **Chronological supersession handling** (circulars that amend/repeal earlier ones) | ✅ **UNIQUE** | ❌ None | ❌ None | ✅ Explicit temporal versioning (CTVs, Action nodes) | ❌ None | ❌ None |
| **Domain-specific citation-grounded evaluation** for financial regulation | ✅ (assumed) | ⚠️ DPO fine-tuned re-ranker for compliance content | ✅ Snippet-level citation accuracy | ⚠️ Provenance reconstruction via graph | ✅ Deterministic set-membership validator + abstention | ⚠️ Evidence strings provided, no evaluation framework |
| **Abstention gates** (refusing when evidence insufficient) | ✅ (assumed) | ❌ None | ❌ None | ❌ None | ✅ Pre-generation threshold (0.30) + post-generation grounding check | ❌ None |
| **Hierarchical legal clause structures** (annexures, numbered sub-clauses) | ✅ (assumed — SEBI circulars have this structure) | ⚠️ Multi-modal pre-processing for tables/diagrams | ✅ Snippet-level precision in legal text | ✅ Explicit hierarchical structure (Works → Expressions) | ⚠️ DOM-based chunking for legal sections | ❌ Flat evidence strings |
| **Multi-modal document processing** (PDFs with tables, annexures) | ⚠️ Partial (circular PDFs) | ✅ Full multi-modal (text + tables + diagrams) | ❌ Text only | ❌ Text/norm structure only | ⚠️ DOM-based HTML chunking | ❌ Text + evidence strings |
| **Evaluation framework** (retrieval metrics: MRR, nDCG) | ⚠️ Assumed | Recall@75 questions | Retrieval precision, citation accuracy | Qualitative case study | Precision@5, recall, faithfulness | LLM-as-judge accuracy, hallucination rate |

### 3.2 Unique Capabilities of SEBI Circular RAG (vs. All Baselines)

| # | Capability | Why It's Unique | Which Systems Share This? |
|---|-----------|-----------------|--------------------------|
| 1 | **Chronological supersession for regulatory circulars** (amend → repeal → re-amend chains) | SEBI circulars have explicit amendment/repeal chains (e.g., "Circular X is hereby superseded by Circular Y dated Z"). No existing benchmark or system handles this for **Indian financial regulation**. | SAT-Graph RAG handles temporal versioning but for general legal norms (Brazilian Constitution), not regulatory circulars with amendment chains. |
| 2 | **Indian regulatory domain specificity** (SEBI, RBI, Ministry of Finance) | All benchmarks focus on U.S. (SEC filings, IRS tax docs, Victorian criminal law). No benchmark covers Indian financial regulation. | None — complete gap in the literature. |
| 3 | **Hybrid retrieval + temporal filtering combined** | Combining hybrid dense+sparse+RRF retrieval with date-aware temporal filtering (only return circulars in force on target date). | regulated-rag has hybrid retrieval but no temporal filtering. SAT-Graph RAG has temporal filtering but not hybrid vector+BM25 retrieval. |
| 4 | **Citation-grounded evaluation for Indian regulatory text** | No existing benchmark provides ground-truth evidence spans for SEBI/RBI circular queries. | FinDER provides evidence spans but for U.S. financial markets, not Indian regulation. |
| 5 | **Abstention gates for regulatory compliance** | Refusing to answer when no circular is in force on the queried date, or when evidence contradicts itself. | regulated-rag has abstention gates but for U.S. consumer debt regulation (FDCPA). |

### 3.3 What Existing Systems Do Better Than SEBI Circular RAG (Likely)

| Capability | Which System Wins | Why |
|-----------|-------------------|-----|
| **Multi-modal financial document processing** (tables, charts in filings) | FinSage | Full multi-modal pipeline with table extraction + diagram processing + DPO fine-tuned re-ranker |
| **Systematic retrieval evaluation** (MRR, nDCG across diverse models) | BEIR/FiQA + LegalBench-RAG | Standardized evaluation protocols with 18+ datasets, leaderboard infrastructure |
| **End-to-end RAG benchmarking** (retrieval + reasoning separation) | Legal RAG Bench | Full factorial design separating retrieval quality from LLM reasoning quality |
| **Deterministic citation grounding** (code-enforced, not prompt-enforced) | regulated-rag | Post-generation set-membership validator; refusal baked into pipeline architecture |
| **Cross-encoder re-ranking** (domain-specific) | PwC paper + FinSage | Cross-encoder reranking achieves 59% absolute MRR improvement; DPO fine-tuned re-ranker |

---

## 4. Recommended Evaluation Framework for SEBI Circular RAG

Based on the SOTA analysis, we recommend a **three-layer evaluation** combining approaches from multiple benchmarks:

### Layer 1: Retrieval Metrics (borrowed from BEIR/FiQA + LegalBench-RAG)
- **nDCG@10, nDCG@5** — standard IR ranking quality
- **MRR@5, MRR@10** — mean reciprocal rank for first-relevant-document
- **Recall@k (k=5, 10)** — fraction of relevant circulars retrieved
- **DRM (Document-Level Retrieval Mismatch)** — from Reuter et al. 2025; measures whether the retriever selects from entirely incorrect source documents

### Layer 2: Temporal Correctness (borrowed from SAT-Graph RAG)
- **Point-in-time accuracy** — does the system return circulars that were in force on the queried date?
- **Supersession chain fidelity** — does the system correctly identify which circular superseded which?
- **Amendment traceability** — can the system reconstruct the full amendment history of a rule?

### Layer 3: Generation Quality (borrowed from regulated-rag + FinanceBench)
- **Citation grounding** — deterministic set-membership validator (every cited chunk_id must be in retrieved top-5)
- **Abstention rate** — fraction of queries correctly refused when evidence is insufficient
- **Hallucination rate** — fraction of claims not supported by retrieved evidence

---

## 5. Key References (arXiv Papers)

| Paper | arXiv ID | Year | Venue |
|-------|----------|------|-------|
| FinSage: Multi-aspect RAG for Financial Filings | 2504.14493 | 2025 | arXiv |
| Towards Reliable Retrieval in Legal RAG (SAC) | 2510.06999 | 2025 | NLLP 2025 (ACL) |
| Citation-Enforced RAG for Fiscal Documents | 2603.14170 | 2026 | arXiv (cs.IR) |
| Ontology-Driven Graph RAG for Legal Norms (SAT-Graph) | 2505.00039 | 2025 | arXiv |
| Rethinking Retrieval: Traditional → Agentic in Finance (PwC) | 2511.18177 | 2025 | arXiv (cs.CL) |
| LegalBench-RAG: Benchmark for Legal RAG Retrieval | 2408.10343 | 2024 | arXiv (cs.AI) |
| Legal RAG Bench: End-to-End Legal RAG Benchmark | 2603.01710 | 2026 | arXiv (cs.CL) |
| FinDER: Financial Dataset for RAG Evaluation | 2504.15800 | 2025 | ICLR 2025 (cs.IR) |
| FinRetrieval: Benchmark for Financial Data Retrieval by AI Agents | 2603.04403 | 2026 | arXiv (cs.IR) |
| FinanceBench: New Benchmark for Financial QA | 2311.11944 | 2023 | arXiv (cs.CL) |
| SEC-QA: Systematic Evaluation Corpus for Financial QA | 2406.14394 | 2024 | arXiv (cs.CL) |
| CaseHOLD: Legal Holdings Dataset | 2104.08671 | 2021 | ICAIL 2021 |
| LegalBench: Collaborative Legal Reasoning Benchmark | 2308.11462 | 2023 | arXiv (cs.CL) |
| FiQA 2018: Financial Opinion Mining & QA | — | 2018 | WWW 2018 Open Challenge |
| FinQA: Numerical Reasoning over Financial Data | — | 2021 | EMNLP 2021 |
| ConvFinQA: Conversational Financial QA | 2210.03849 | 2022 | EMNLP 2022 |
| TAT-QA: Tabular and Textual QA in Finance | — | 2021 | ACL 2021 |
| Case-Aware LLM-as-a-Judge for Enterprise RAG | 2602.20379 | 2026 | arXiv (cs.CL) |

---

## 6. Key Open-Source Repositories

| Repository | URL | Description |
|-----------|-----|-------------|
| regulated-rag | github.com/RZ-Logic/regulated-rag | Citation-grounded, refusal-bounded RAG for regulated domains (FDCPA) — hybrid vector+BM25→RRF→reranker |
| FinSage | github.com/sujangongati/FinSage | Multi-aspect RAG for financial filings (multi-modal, sparse-dense retrieval) |
| legalbenchrag | github.com/zeroentropy-ai/legalbenchrag | LegalBench-RAG benchmark for legal retrieval evaluation |
| casehold | github.com/reglab/casehold | CaseHOLD dataset + Legal-BERT models for legal holdings prediction |
| FinanceBench | github.com/patronus-ai/financebench | 10,231 expert-annotated financial QA triplets from SEC filings |
| BEIR | github.com/beir-cellar/beir | 18-dataset heterogeneous IR benchmark (includes FiQA) |

---

## 7. Summary: The Gap in One Sentence

> **No existing benchmark or open-source system handles chronological supersession (amend/repeal chains) for Indian financial regulatory circulars with hybrid dense+sparse+RRF retrieval, temporal filtering, and deterministic abstention gates — this is the unique value proposition of SEBI Circular RAG.**
