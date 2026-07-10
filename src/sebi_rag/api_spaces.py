"""Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).

Parallel to api.build_default_pipeline() but with no MLX, no Ollama and no
"mps" device anywhere. The Apple-Silicon path is untouched.

Index strategy: a free CPU Space (2 vCPU) cannot BGE-M3-encode the 36k-chunk
corpus at startup (hours). Instead the locally built data/index artifacts
(dense.faiss, bm25, chunks.jsonl, embeddings.npy, lineage.json) are published
to settings.spaces.index_repo (see scripts/upload_spaces_index.py) and
downloaded here via snapshot_download — cold start in minutes, retrieval
numerically identical to the local system. Building from the raw HF dataset
remains as a fallback for small subsets and CI.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from .lineage import Lineage, build_lineage
from .pipeline import RAGPipeline
from .settings import Settings

log = logging.getLogger(__name__)

# The published prebuilt index was built from these (see upload script).
PREBUILT_CONFIG, PREBUILT_SUBSET = "chunks", "full"


def _cpu_env() -> None:
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("OMP_NUM_THREADS", "2")
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")


def build_spaces_pipeline(
    config_name: str = PREBUILT_CONFIG,
    subset: str = PREBUILT_SUBSET,
) -> RAGPipeline:
    _cpu_env()
    from .corpus_spaces import load_circulars_from_hf, load_corpus_records_from_hf
    from .embeddings import BGEM3Embedder
    from .generate import SubjectSimJudge
    from .generate_spaces import HybridGenerator
    from .rerank import CrossEncoderReranker
    from .retrieve import HybridRetriever

    s = Settings.load_spaces()
    assert s.spaces is not None
    embedder = BGEM3Embedder(device="cpu")

    lineage: Lineage | None = None
    retriever = None
    use_prebuilt = (
        s.spaces.index_repo
        and config_name == PREBUILT_CONFIG
        and subset == PREBUILT_SUBSET
    )
    if use_prebuilt:
        from huggingface_hub import snapshot_download

        local = snapshot_download(s.spaces.index_repo, repo_type="dataset")
        if HybridRetriever.index_exists(local):
            retriever = HybridRetriever.load(local, embedder)
            lin_path = Path(local) / "lineage.json"
            if lin_path.exists():
                lineage = Lineage.load(lin_path)
        else:
            log.warning("index_repo %r has no index artifacts; building from "
                        "the HF dataset instead", s.spaces.index_repo)
    if retriever is None:
        # Fallback: encode on CPU — fine for tests/small subsets, hours for
        # the full 36k-chunk corpus. Deploys should set spaces.index_repo.
        log.warning("building %s/%s index from the HF dataset on CPU; this "
                    "is slow for the full corpus", config_name, subset)
        chunks = load_circulars_from_hf(s, config_name=config_name, subset=subset)
        retriever = HybridRetriever.build(chunks, embedder)
    if lineage is None:
        lineage = build_lineage(load_corpus_records_from_hf(s, subset=subset))

    # Same near-domain abstention gate as build_default_pipeline (adopted
    # thresholds; zero extra models — reuses the embedder).
    judge = SubjectSimJudge(embedder, threshold=0.42, section_threshold=0.60)

    return RAGPipeline(
        retriever=retriever,
        reranker=CrossEncoderReranker(device="cpu"),
        generator=HybridGenerator(s.spaces),
        lineage=lineage,
        abstain_threshold=s.spaces.abstain_threshold,
        superseded_penalty=s.spaces.superseded_penalty,
        judge=judge,
    )
