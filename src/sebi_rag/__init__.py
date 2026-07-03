"""SEBI Circular RAG — local-first, Apple Silicon.

Pipeline: ingest -> segment -> retrieve (dense FAISS + sparse BM25 + RRF) ->
rerank (cross-encoder) -> generate (with abstention) -> eval.

Heavy models (bge-m3, bge-reranker-v2-m3) are injected via the Embedder /
Reranker protocols so the core pipeline is testable without model downloads.
"""

__version__ = "0.1.0"
