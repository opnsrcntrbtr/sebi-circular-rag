"""FastAPI service over the SEBI Circular RAG pipeline.

Run (real stack; loads the persisted index on first request):
    SEBI_RAG_API_KEY=secret SEBI_RAG_RATE_PER_MIN=60 \
    HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
    PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src \
    .venv/bin/uvicorn sebi_rag.api:app --host 127.0.0.1 --port 8000

Hardening:
- Auth: if SEBI_RAG_API_KEY is set, /query requires header `X-API-Key` to match.
- Rate limit: SEBI_RAG_RATE_PER_MIN (default 60) requests/min per key-or-IP (429).
- Latency: each /query response includes latency_ms.
- Supersession: citations_meta gives each cited circular's status + superseded_by.
"""
from __future__ import annotations

import os
import secrets
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from pathlib import Path
from typing import Callable, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from .lineage import Lineage
from .pipeline import RAGPipeline
from .settings import Settings

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"  # convenience for tests/scripts


class QueryRequest(BaseModel):
    question: str
    # ADR-002: top_k=0 previously slipped through and caused a silent
    # no-context abstention; degenerate values are now a 422.
    top_k: int | None = Field(default=None, ge=1, le=10)
    advisory: bool = False  # opt-in low-confidence draft on gate failure
    as_of: str | None = None  # date-scoped query: score against law as of date
    mode: Literal["rag", "retrieval_only"] = "rag"  # retrieval_only swaps in the stub generator


class CitationMeta(BaseModel):
    circular: str
    status: str                       # in_force | superseded | amended | unknown
    superseded_by: list[str] = []


class QueryResponse(BaseModel):
    answer: str
    citations: list[str]
    citations_meta: list[CitationMeta]
    abstained: bool
    superseded: dict
    faithfulness: float
    unsupported_citations: list[str]
    retrieved: list[str]
    latency_ms: float
    # ADR-002 certainty architecture
    confidence: dict
    certainty: str          # high | medium | low
    abstention_reason: str  # "" | no_context | score_floor | subject_gate
    draft_answer: str       # advisory mode only; never authoritative


def build_default_pipeline() -> RAGPipeline:
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    from .corpus import load_circulars
    from .embeddings import BGEM3Embedder
    from .lineage import build_lineage, load_records
    from .rerank import CrossEncoderReranker
    from .retrieve import HybridRetriever

    s = Settings.load()
    if s.generator.lower() == "ollama":
        from .generate import OllamaGenerator
        generator = OllamaGenerator()
    else:
        from .generate import MLXGenerator
        generator = MLXGenerator(s.mlx_model)

    embedder = BGEM3Embedder(device="mps")
    judge = None
    if os.environ.get("SEBI_RAG_GATE", "on").lower() not in ("off", "0"):
        from .generate import SubjectSimJudge
        sect_env = os.environ.get("SEBI_RAG_SECT_THRESHOLD", "0.60")
        judge = SubjectSimJudge(
            embedder,
            threshold=float(os.environ.get("SEBI_RAG_SUBJ_THRESHOLD", "0.42")),
            # two-tier default ON (eval_gate 2026-07-02: no hn regression,
            # margin 0.107); "off" disables the section tier
            section_threshold=(None if sect_env.lower() in ("off", "0")
                               else float(sect_env)),
        )
    index = Path(s.index_dir)
    if HybridRetriever.index_exists(index):
        retriever = HybridRetriever.load(index, embedder)
    else:
        retriever = HybridRetriever.build(load_circulars(s.corpus_path), embedder)
    lin_path = index / "lineage.json"
    lineage = (Lineage.load(lin_path) if lin_path.exists()
               else build_lineage(load_records(s.corpus_path)))
    return RAGPipeline(
        retriever=retriever,
        reranker=CrossEncoderReranker(device="mps"),
        generator=generator,
        lineage=lineage,
        abstain_threshold=s.abstain_threshold,
        superseded_penalty=s.superseded_penalty,
        judge=judge,
    )


def _citation_meta(citations: list[str], lineage: Lineage | None) -> list[CitationMeta]:
    seen, out = set(), []
    for c in citations:
        cn = c.split("#", 1)[0]
        if cn in seen:
            continue
        seen.add(cn)
        if lineage is None:
            out.append(CitationMeta(circular=cn, status="unknown"))
        else:
            out.append(CitationMeta(
                circular=cn,
                status=lineage.status(cn),
                superseded_by=lineage.superseded_by.get(cn, []),
            ))
    return out


def create_app(
    pipeline_factory: Callable[[], RAGPipeline] = build_default_pipeline,
    settings: Settings | None = None,
) -> FastAPI:
    cfg = settings or Settings.load()
    app = FastAPI(title="SEBI Circular RAG", version="0.1.0")
    state: dict[str, RAGPipeline] = {}
    hits: dict[str, deque] = defaultdict(deque)
    _request_count: int = 0
    _executor = ThreadPoolExecutor(max_workers=2)

    @app.on_event("shutdown")
    def _shutdown() -> None:
        _executor.shutdown(wait=True)

    def pipe(mode: str = "rag") -> RAGPipeline:
        if "rag" not in state:
            state["rag"] = pipeline_factory()
        if mode == "retrieval_only" and "retrieval_only" not in state:
            import dataclasses

            from .generate import ExtractiveStubGenerator
            state["retrieval_only"] = dataclasses.replace(
                state["rag"], generator=ExtractiveStubGenerator())
        return state[mode if mode == "retrieval_only" else "rag"]

    def guard(request: Request, x_api_key: str | None = Header(default=None)) -> None:
        nonlocal _request_count
        _request_count += 1
        key = os.environ.get("SEBI_RAG_API_KEY")  # secret: env-only
        # F4: constant-time compare — a plain != leaks key prefixes via timing
        if key and not secrets.compare_digest(x_api_key or "", key):
            raise HTTPException(status_code=401, detail="invalid or missing API key")
        ident = x_api_key or (request.client.host if request.client else "anon")
        now = time.time()
        dq = hits[ident]
        while dq and now - dq[0] > 60:
            dq.popleft()
        if len(dq) >= cfg.rate_per_min:
            raise HTTPException(status_code=429, detail="rate limit exceeded")
        dq.append(now)
        # Periodic cleanup: every 60 requests, remove entries with empty deques
        if _request_count % 60 == 0:
            for k in list(hits):
                if not hits[k]:
                    del hits[k]

    @app.get("/ready")
    def ready() -> dict:
        pipe()  # trigger eager pipeline build so readiness probe works immediately
        return {"ready": "rag" in state}

    @app.get("/health")
    def health() -> dict:
        p = pipe()
        docs = {c.doc_id for c in p.retriever.chunks}
        return {
            "status": "ok", "chunks": len(p.retriever.chunks), "circulars": len(docs),
            "generator": cfg.generator, "model": cfg.mlx_model,
            "top_k": cfg.top_k, "rate_per_min": cfg.rate_per_min,
        }

    @app.post("/query", response_model=QueryResponse)
    def query(req: QueryRequest, _: None = Depends(guard)) -> QueryResponse:
        p = pipe(req.mode)  # build (model load) outside the per-query time budget
        t0 = time.perf_counter()
        top_k = req.top_k if req.top_k is not None else cfg.top_k
        budget = cfg.timeout_s
        fut = _executor.submit(p.query, req.question, top_k=top_k,
                              advisory=req.advisory, as_of=req.as_of)
        try:
            ans, retrieved = fut.result(timeout=budget)
        except FutureTimeout:
            raise HTTPException(status_code=504, detail="query exceeded time budget")
        return QueryResponse(
            answer=ans.text,
            citations=ans.citations,
            citations_meta=_citation_meta(ans.citations, p.lineage),
            abstained=ans.abstained,
            superseded=ans.superseded,
            faithfulness=ans.faithfulness,
            unsupported_citations=ans.unsupported_citations,
            retrieved=retrieved[:20],
            latency_ms=round((time.perf_counter() - t0) * 1000, 1),
            confidence=ans.confidence,
            certainty=ans.certainty,
            abstention_reason=ans.abstention_reason,
            draft_answer=ans.draft_answer,
        )

    return app


app = create_app()
