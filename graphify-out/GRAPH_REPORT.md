# Graph Report - .  (2026-07-10)

## Corpus Check
- 100 files · ~59,940 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 464 nodes · 954 edges · 38 communities (25 shown, 13 thin omitted)
- Extraction: 68% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 196 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

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
- ML Infrastructure
- Safety & Generation
- Discovery Scripts
- UI Dashboard
- Health Checks
- Design Principles
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
- `main()` --calls--> `BGEM3Embedder`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/embeddings.py
- `main()` --calls--> `build_lineage()`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/lineage.py
- `main()` --calls--> `demote_superseded()`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/lineage.py
- `main()` --calls--> `load_records()`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/lineage.py
- `main()` --calls--> `CrossEncoderReranker`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/rerank.py

## Import Cycles
- None detected.

## Communities (38 total, 13 thin omitted)

### Community 0 - "Evaluation & Benchmarking"
Cohesion: 0.07
Nodes (43): BaseModel, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Emit one JSON line listing SEBI circulars newer than previously seen. Uses a sta, build_default_pipeline(), _citation_meta(), CitationMeta, QueryRequest, QueryResponse (+35 more)

### Community 1 - "Embeddings & Grounding"
Cohesion: 0.08
Nodes (26): Embedder, _grounded_prompt(), F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, DenseIndex, _doc_checksum(), HybridRetriever, ndarray, Path (+18 more)

### Community 2 - "Indexing & Performance"
Cohesion: 0.08
Nodes (25): Protocol, Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks. (+17 more)

### Community 3 - "API & Data Ingestion"
Cohesion: 0.11
Nodes (29): FastAPI, create_app(), load_circulars(), Path, HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, RAGPipeline, LexicalReranker (+21 more)

### Community 4 - "Safety Gates & Abstention"
Cohesion: 0.12
Nodes (25): answer_with_abstention(), ExtractiveStubGenerator, ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., Deterministic: returns the top context text. No model required., SubjectSimJudge, _chunk() (+17 more)

### Community 5 - "Architecture & Design"
Cohesion: 0.06
Nodes (32): ADR-001 Architecture Review Findings, BEIR Export Format, Chunk Enrichment, Corpus Ingestion, Corpus Metadata, Corpus Refresh Workflow, Corpus Validation, Dataset Export Pipeline (+24 more)

### Community 6 - "Reranker Evaluation"
Cohesion: 0.15
Nodes (18): auroc(), best_threshold(), evaluate(), main(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t, evaluate() (+10 more)

### Community 7 - "Configuration & Deployment"
Cohesion: 0.12
Nodes (17): Apple Silicon, Citation Generation, config.toml, Faithfulness Check, FastAPI Service, Gradio UI, HuggingFace Hub, launchd Agent (+9 more)

### Community 8 - "Judgement Models"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), True iff the reply names a valid excerpt number. 'none' or anything     unparsea, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the     gat, Deterministic groundedness judge on MLX (greedy decode, temp 0).      Pass share (+3 more)

### Community 9 - "Qwen3 Reranking"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 10 - "Retrieval Metrics"
Cohesion: 0.26
Nodes (11): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed, test_abstention_on_out_of_domain_query() (+3 more)

### Community 11 - "Operations Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 12 - "Dataset Export"
Cohesion: 0.20
Nodes (10): AIKosh Submission, CC-BY-4.0 License, Chunks Config, Citation-Normalization Dataset, Export Pipeline, Hugging Face Dataset, Kaggle Dataset, Lineage Config (+2 more)

### Community 13 - "Retrieval Enhancement"
Cohesion: 0.25
Nodes (8): BGE-M3 Embedder, BM25 Sparse Index, Citation Precision, Contextual Chunk Enrichment, Incremental Encode, Incremental Indexing, Index Building, Retrieval Quality Ceiling

### Community 14 - "Hybrid Search Infrastructure"
Cohesion: 0.25
Nodes (8): BM25, FAISS, Hybrid Retrieval, LanceDB, Lineage Graph, Reciprocal Rank Fusion, Reciprocal Rank Fusion, Successor Expansion

### Community 15 - "Settings Management"
Cohesion: 0.43
Nodes (6): Path, _clear(), Settings: defaults, config.toml, and env-override precedence., test_defaults_when_no_file(), test_env_overrides(), test_toml_then_env_precedence()

### Community 16 - "Cross-encoder Ranking"
Cohesion: 0.29
Nodes (7): Cross-encoder Reranking, Ground Truth Answer Generation, Per-Chunk Cross-References, Query Endpoint, Qwen3-Reranker, Supersession Tracking, top_k Calibration

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
Cohesion: 0.40
Nodes (5): Abstention Gate, Advisory Mode, Confidence Bands, Subject-Similarity Threshold, SubjectSimJudge

### Community 23 - "PDF Ingestion"
Cohesion: 0.50
Nodes (3): _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., test_ingest_extracts_metadata_and_lineage()

### Community 24 - "ML Infrastructure"
Cohesion: 0.50
Nodes (4): BGE-M3 Embedding Model, FAISS Dense Index, PyTorch MPS, Validation Roadmap

### Community 25 - "Safety & Generation"
Cohesion: 0.50
Nodes (4): Faithfulness Metric, Groundedness Gate, MLX Generator, Qwen 3B Model

## Knowledge Gaps
- **23 isolated node(s):** `sebi-rag`, `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Embeddings & Grounding` to `Evaluation & Benchmarking`, `Indexing & Performance`, `API & Data Ingestion`, `Safety Gates & Abstention`, `Judgement Models`, `Qwen3 Reranking`, `Injection Testing`?**
  _High betweenness centrality (0.177) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `API & Data Ingestion` to `Evaluation & Benchmarking`, `Embeddings & Grounding`, `Indexing & Performance`, `Reranker Evaluation`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `HybridRetriever` connect `Embeddings & Grounding` to `Evaluation & Benchmarking`, `Indexing & Performance`, `API & Data Ingestion`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `Chunk` (e.g. with `Answer` and `ExtractiveStubGenerator`) actually correct?**
  _`Chunk` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `HashEmbedder` (e.g. with `_offline_pipeline()` and `_slow_pipeline()`) actually correct?**
  _`HashEmbedder` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `answer_with_abstention()` (e.g. with `.score()` and `.section_score()`) actually correct?**
  _`answer_with_abstention()` has 12 INFERRED edges - model-reasoned connections that need verification._