# Graph Report - src  (2026-07-12)

## Corpus Check
- 19 files · ~10,667 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 267 nodes · 628 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 71 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `39529202`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Chunk
- RAGPipeline
- benchmark.py
- ingest_pdf.py
- api_spaces.py
- HybridRetriever
- generate_spaces.py
- embeddings.py
- eval.py
- ui.py

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 61 edges
2. `RAGPipeline` - 25 edges
3. `SubjectSimJudge` - 16 edges
4. `HybridRetriever` - 16 edges
5. `build_default_pipeline()` - 15 edges
6. `build_spaces_pipeline()` - 15 edges
7. `Lineage` - 15 edges
8. `Embedder` - 14 edges
9. `Settings` - 13 edges
10. `CitationMeta` - 12 edges

## Surprising Connections (you probably didn't know these)
- `QueryRequest` --uses--> `SubjectSimJudge`  [INFERRED]
  src/sebi_rag/api.py → src/sebi_rag/generate.py
- `QueryRequest` --uses--> `HybridRetriever`  [INFERRED]
  src/sebi_rag/api.py → src/sebi_rag/retrieve.py
- `QueryRequest` --uses--> `Settings`  [INFERRED]
  src/sebi_rag/api.py → src/sebi_rag/settings.py
- `CitationMeta` --uses--> `SubjectSimJudge`  [INFERRED]
  src/sebi_rag/api.py → src/sebi_rag/generate.py
- `CitationMeta` --uses--> `HybridRetriever`  [INFERRED]
  src/sebi_rag/api.py → src/sebi_rag/retrieve.py

## Import Cycles
- None detected.

## Communities (10 total, 2 thin omitted)

### Community 0 - "Chunk"
Cohesion: 0.07
Nodes (36): Protocol, Answer, answer_with_abstention(), ExtractiveStubGenerator, faithfulness(), Generator, Judge, _judge_prompt() (+28 more)

### Community 1 - "RAGPipeline"
Cohesion: 0.11
Nodes (30): BaseModel, FastAPI, build_default_pipeline(), _citation_meta(), CitationMeta, create_app(), QueryRequest, QueryResponse (+22 more)

### Community 2 - "benchmark.py"
Cohesion: 0.13
Nodes (32): Any, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), dir_fingerprint(), enrich_golden_item(), export_beir() (+24 more)

### Community 3 - "ingest_pdf.py"
Cohesion: 0.11
Nodes (32): Pattern, _existing_numbers(), extract_text(), _header(), ingest(), injection_scan(), _iso_date(), _labeled_date() (+24 more)

### Community 4 - "api_spaces.py"
Cohesion: 0.12
Nodes (26): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., _keep(), load_circulars_from_hf() (+18 more)

### Community 5 - "HybridRetriever"
Cohesion: 0.14
Nodes (14): Embedder, DenseIndex, _doc_checksum(), HybridRetriever, ndarray, Path, Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF.  Mandatory, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding (+6 more)

### Community 6 - "generate_spaces.py"
Cohesion: 0.15
Nodes (11): _grounded_prompt(), F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug (+3 more)

### Community 7 - "embeddings.py"
Cohesion: 0.24
Nodes (5): HashEmbedder, ndarray, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, _tokens()

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `RAGPipeline`, `benchmark.py`, `api_spaces.py`, `HybridRetriever`, `generate_spaces.py`?**
  _High betweenness centrality (0.432) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `Chunk`, `benchmark.py`, `api_spaces.py`, `HybridRetriever`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `DenseIndex` connect `HybridRetriever` to `Chunk`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SubjectSimJudge` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`SubjectSimJudge` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `HybridRetriever` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`HybridRetriever` has 6 INFERRED edges - model-reasoned connections that need verification._