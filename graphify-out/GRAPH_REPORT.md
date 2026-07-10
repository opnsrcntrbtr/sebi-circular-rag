# Graph Report - SEBI circular RAG  (2026-07-10)

## Corpus Check
- 99 files · ~59,940 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 481 nodes · 969 edges · 36 communities (25 shown, 11 thin omitted)
- Extraction: 69% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 196 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6645d396`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Evaluation & Benchmarking
- Embeddings & Grounding
- Indexing & Performance
- API & Data Ingestion
- Safety Gates & Abstention
- Architecture & Design
- Reranker Evaluation
- Configuration & Deployment
- Judgement Models
- Qwen3 Reranking
- Retrieval Metrics
- Operations Server
- Dataset Export
- Retrieval Enhancement
- Hybrid Search Infrastructure
- Settings Management
- Cross-encoder Ranking
- Environment Setup
- Health Monitoring
- Corpus Refresh
- Injection Testing
- Confidence & Advisory
- Encoding Operations
- PDF Ingestion
- Safety & Generation
- Discovery Scripts
- UI Dashboard
- Health Checks
- Operational Scripts
- Data Sourcing
- Notifications
- Data Renumbering
- Test Setup
- Model Strategy
- Project Root
- Runtime Environment

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 56 edges
2. `RAGPipeline` - 25 edges
3. `HashEmbedder` - 21 edges
4. `answer_with_abstention()` - 21 edges
5. `SubjectSimJudge` - 20 edges
6. `build_lineage()` - 18 edges
7. `HybridRetriever` - 16 edges
8. `hierarchical_chunk()` - 16 edges
9. `build_default_pipeline()` - 15 edges
10. `ExtractiveStubGenerator` - 15 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `load_golden()`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/eval_harness.py
- `main()` --calls--> `build_lineage()`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/lineage.py
- `main()` --calls--> `demote_superseded()`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/lineage.py
- `main()` --calls--> `Qwen3MLXReranker`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/rerank.py
- `contexts_for()` --calls--> `demote_superseded()`  [INFERRED]
  scripts/eval_gate.py → src/sebi_rag/lineage.py

## Import Cycles
- None detected.

## Communities (36 total, 11 thin omitted)

### Community 0 - "Evaluation & Benchmarking"
Cohesion: 0.10
Nodes (30): BaseModel, main(), build_default_pipeline(), _citation_meta(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline.  Run (real stack; loads the (+22 more)

### Community 1 - "Embeddings & Grounding"
Cohesion: 0.07
Nodes (30): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Build the dense+sparse index once and persist it (run after corpus changes)., Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Embedder, ndarray, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, _tokens(), DenseIndex (+22 more)

### Community 2 - "Indexing & Performance"
Cohesion: 0.08
Nodes (25): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Emit one JSON line listing SEBI circulars newer than previously seen. Uses a sta, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Answer, build_lineage(), _currency(), demote_superseded() (+17 more)

### Community 3 - "API & Data Ingestion"
Cohesion: 0.09
Nodes (35): FastAPI, create_app(), load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, RAGPipeline (+27 more)

### Community 4 - "Safety Gates & Abstention"
Cohesion: 0.06
Nodes (46): Protocol, answer_with_abstention(), ExtractiveStubGenerator, faithfulness(), Generator, _grounded_prompt(), Judge, _judge_prompt() (+38 more)

### Community 5 - "Architecture & Design"
Cohesion: 0.10
Nodes (22): ADR-001 Architecture Review Findings, Chunk Enrichment, Corpus Ingestion, Corpus Metadata, Corpus Validation, Dataset Export Pipeline, Hierarchical Chunking, Ingest Hardening (+14 more)

### Community 6 - "Reranker Evaluation"
Cohesion: 0.14
Nodes (17): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t, evaluate(), Calibrate top_k and the abstention threshold against the citation-precision sign (+9 more)

### Community 7 - "Configuration & Deployment"
Cohesion: 0.11
Nodes (19): Apple Silicon, Citation Generation, config.toml, Faithfulness Check, FastAPI Service, Gradio UI, HuggingFace Hub, launchd Agent (+11 more)

### Community 8 - "Judgement Models"
Cohesion: 0.20
Nodes (10): BEIR Export Format, Corpus Refresh Workflow, Eval Canary Workflow, golden_v5 Evaluation Set, Golden v6 Benchmark, Health Monitor Workflow, n8n Automation, Ops HTTP Server (+2 more)

### Community 9 - "Qwen3 Reranking"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 10 - "Retrieval Metrics"
Cohesion: 0.16
Nodes (13): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), _ollama_up(), Step 12 — end-to-end RAG integration test with the REAL stack.  bge-m3 (MPS) + b, _build_chunks(), _build_pipeline() (+5 more)

### Community 11 - "Operations Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 12 - "Dataset Export"
Cohesion: 0.20
Nodes (10): AIKosh Submission, CC-BY-4.0 License, Chunks Config, Citation-Normalization Dataset, Export Pipeline, Hugging Face Dataset, Kaggle Dataset, Lineage Config (+2 more)

### Community 13 - "Retrieval Enhancement"
Cohesion: 0.25
Nodes (8): BGE-M3 Embedding Model, BM25 Sparse Index, FAISS Dense Index, Incremental Encode, Incremental Indexing, PyTorch MPS, Retrieval Quality Ceiling, Validation Roadmap

### Community 14 - "Hybrid Search Infrastructure"
Cohesion: 0.25
Nodes (8): BM25, Ground Truth Answer Generation, Hybrid Retrieval, Lineage Graph, Query Endpoint, Reciprocal Rank Fusion, Reciprocal Rank Fusion, Successor Expansion

### Community 15 - "Settings Management"
Cohesion: 0.22
Nodes (7): Current Handoffs, Environment, graphify, Graphify (Optional), Project, Quick Start, Source Structure (`src/sebi_rag/`)

### Community 16 - "Cross-encoder Ranking"
Cohesion: 0.20
Nodes (10): Abstention Gate, Advisory Mode, Confidence Bands, Cross-encoder Reranking, Per-Chunk Cross-References, Qwen3-Reranker, Subject-Similarity Threshold, SubjectSimJudge (+2 more)

### Community 17 - "Environment Setup"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 18 - "Health Monitoring"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 19 - "Corpus Refresh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 20 - "Injection Testing"
Cohesion: 0.33
Nodes (3): _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule()

### Community 21 - "Confidence & Advisory"
Cohesion: 0.25
Nodes (7): Current Handoffs, Environment, graphify, Graphify (Optional), Project, Quick Start, Source Structure (`src/sebi_rag/`)

### Community 22 - "Encoding Operations"
Cohesion: 0.33
Nodes (6): BGE-M3 Embedder, Citation Precision, Contextual Chunk Enrichment, FAISS, Index Building, LanceDB

### Community 23 - "PDF Ingestion"
Cohesion: 0.50
Nodes (3): _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., test_ingest_extracts_metadata_and_lineage()

### Community 25 - "Safety & Generation"
Cohesion: 0.50
Nodes (4): Faithfulness Metric, Groundedness Gate, MLX Generator, Qwen 3B Model

## Knowledge Gaps
- **37 isolated node(s):** `Project`, `Quick Start`, `Environment`, `Source Structure (`src/sebi_rag/`)`, `Graphify (Optional)` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Safety Gates & Abstention` to `Evaluation & Benchmarking`, `Embeddings & Grounding`, `Indexing & Performance`, `API & Data Ingestion`, `Qwen3 Reranking`, `Injection Testing`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `API & Data Ingestion` to `Evaluation & Benchmarking`, `Embeddings & Grounding`, `Indexing & Performance`, `Safety Gates & Abstention`, `Reranker Evaluation`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `HybridRetriever` connect `Embeddings & Grounding` to `Evaluation & Benchmarking`, `Indexing & Performance`, `API & Data Ingestion`, `Safety Gates & Abstention`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `Chunk` (e.g. with `Answer` and `ExtractiveStubGenerator`) actually correct?**
  _`Chunk` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `HashEmbedder` (e.g. with `_offline_pipeline()` and `_slow_pipeline()`) actually correct?**
  _`HashEmbedder` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `answer_with_abstention()` (e.g. with `.score()` and `.section_score()`) actually correct?**
  _`answer_with_abstention()` has 12 INFERRED edges - model-reasoned connections that need verification._