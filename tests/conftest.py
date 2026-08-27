"""Test-time environment guards.

Set before torch / FlagEmbedding / faiss initialize their thread pools. Running
bge-m3 (FlagEmbedding) and the cross-encoder (sentence-transformers) together on
MPS segfaults without these — FlagEmbedding's process pool clashes with Metal
once it is already initialized. Reproducibility note mirrored in
docs/project_context.md.

KMP_DUPLICATE_LIB_OK: separate, unrelated crash class (2026-08-27, found while
adding tests/test_rerank_set_encoder.py). faiss-cpu and torch both bundle their
own OpenMP runtime; once faiss has been imported anywhere in the process (many
test modules import it transitively via sebi_rag.retrieve) the *first* real
`import torch` in the same process -- not a mocked/stubbed one -- segfaults
inside torch's own init (observed at torch/__init__.py:445) because two
copies of libomp end up loaded. No prior offline test triggered a real torch
import (existing reranker tests all bypass __init__ via a stub), so this was
latent until SetEncoderReranker got its first real-`rerank()` test. Confirmed:
full suite crashes without this var, passes (904 passed, same 4 pre-existing
failures) with it. Standard, documented workaround for this OpenMP-duplicate
class of crash -- not a correctness-affecting override.
"""
import os

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
