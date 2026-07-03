"""Test-time environment guards.

Set before torch / FlagEmbedding / faiss initialize their thread pools. Running
bge-m3 (FlagEmbedding) and the cross-encoder (sentence-transformers) together on
MPS segfaults without these — FlagEmbedding's process pool clashes with Metal
once it is already initialized. Reproducibility note mirrored in
docs/project_context.md.
"""
import os

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
