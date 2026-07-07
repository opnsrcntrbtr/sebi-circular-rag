# Graph Report - .  (2026-07-08)

## Corpus Check
- Corpus is ~31,482 words - fits in a single context window. You may not need a graph.

## Summary
- 402 nodes · 930 edges · 21 communities (14 shown, 7 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 202 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Answer Generation & Abstention
- Benchmarking & Index Building
- Corpus Loading & Management
- API & FastAPI Integration
- SEBI ID Renumbering
- Golden Dataset & Evaluation
- Discovery & Date Handling
- Reranker Benchmarking
- Evaluation Metrics
- Qwen3 Reranking
- Operations Server
- Run Environment Setup
- Canary Testing
- Corpus Refresh
- Embedding Encoding
- Circular Discovery
- Gradio UI
- Operations Entry Point
- Notification Service
- Test Configuration
- Package Root

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

## Communities (21 total, 7 thin omitted)

### Community 0 - "Answer Generation & Abstention"
Cohesion: 0.06
Nodes (47): Protocol, answer_with_abstention(), ExtractiveStubGenerator, faithfulness(), Generator, _grounded_prompt(), Judge, _judge_prompt() (+39 more)

### Community 1 - "Benchmarking & Index Building"
Cohesion: 0.08
Nodes (27): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Build the dense+sparse index once and persist it (run after corpus changes)., Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Embedder, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, End-to-end wiring: segment -> hybrid retrieve -> rerank -> generate/abstain., DenseIndex, _doc_checksum() (+19 more)

### Community 2 - "Corpus Loading & Management"
Cohesion: 0.09
Nodes (32): load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, LexicalReranker, Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic, Deterministic query-coverage reranker (test/fallback).      Score = fraction of (+24 more)

### Community 3 - "API & FastAPI Integration"
Cohesion: 0.10
Nodes (32): BaseModel, FastAPI, build_default_pipeline(), _citation_meta(), CitationMeta, create_app(), QueryRequest, QueryResponse (+24 more)

### Community 4 - "SEBI ID Renumbering"
Cohesion: 0.10
Nodes (31): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), _header(), ingest(), injection_scan(), _iso_date() (+23 more)

### Community 5 - "Golden Dataset & Evaluation"
Cohesion: 0.10
Nodes (23): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Answer, build_lineage(), _currency(), demote_superseded(), detect_relations() (+15 more)

### Community 6 - "Discovery & Date Handling"
Cohesion: 0.14
Nodes (18): date, Emit one JSON line listing SEBI circulars newer than previously seen. Uses a sta, discover(), fetch(), _listing_url(), main(), _page(), _parse_date() (+10 more)

### Community 7 - "Reranker Benchmarking"
Cohesion: 0.14
Nodes (19): auroc(), best_threshold(), evaluate(), main(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t, evaluate() (+11 more)

### Community 8 - "Evaluation Metrics"
Cohesion: 0.16
Nodes (13): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), _ollama_up(), Step 12 — end-to-end RAG integration test with the REAL stack.  bge-m3 (MPS) + b, _build_chunks(), _build_pipeline() (+5 more)

### Community 9 - "Qwen3 Reranking"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 10 - "Operations Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 11 - "Run Environment Setup"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 12 - "Canary Testing"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 13 - "Corpus Refresh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

## Knowledge Gaps
- **23 isolated node(s):** `sebi-rag`, `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Answer Generation & Abstention` to `Benchmarking & Index Building`, `Corpus Loading & Management`, `API & FastAPI Integration`, `SEBI ID Renumbering`, `Golden Dataset & Evaluation`, `Qwen3 Reranking`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `API & FastAPI Integration` to `Answer Generation & Abstention`, `Benchmarking & Index Building`, `Corpus Loading & Management`, `Golden Dataset & Evaluation`, `Reranker Benchmarking`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `SubjectSimJudge` connect `Answer Generation & Abstention` to `API & FastAPI Integration`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `Chunk` (e.g. with `Answer` and `ExtractiveStubGenerator`) actually correct?**
  _`Chunk` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `HashEmbedder` (e.g. with `_offline_pipeline()` and `_slow_pipeline()`) actually correct?**
  _`HashEmbedder` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `answer_with_abstention()` (e.g. with `.score()` and `.section_score()`) actually correct?**
  _`answer_with_abstention()` has 12 INFERRED edges - model-reasoned connections that need verification._