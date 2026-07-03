# Validation Roadmap — SEBI Circular RAG

> Matches the Engineering Handbook validation sequence exactly. No additional
> steps. One step at a time; never validate a later stage until the current one
> passes. Any FAIL is a blocker. Last updated: 2026-06-29.

Each step validates only: **Installation**, **Configuration**, **Functionality**.

| # | Step | Installation | Configuration | Functionality |
|---|------|--------------|---------------|---------------|
| 1 | Hardware & macOS | M4 Pro / 48 GB present | macOS version pinned | System meets local-first requirements |
| 2 | Xcode CLT | CLT installed | Active developer dir set | `clang` / `git` toolchain runs |
| 3 | Homebrew | brew installed | On PATH, ARM prefix | `brew` installs/queries a formula |
| 4 | Python + uv | Python 3.12.x + uv installed | venv created, versions pinned | uv resolves and runs a script |
| 5 | Git | git installed | user/identity configured | clone / commit succeeds |
| 6 | MLX | mlx / mlx-lm installed | Metal backend available | mlx-lm loads a model and generates |
| 7 | Ollama | Ollama 0.19+ installed | MLX backend active | model pull + inference responds |
| 8 | PyTorch MPS (only if required) | torch installed | MPS device available | tensor op runs on MPS |
| 9 | FAISS | faiss-cpu installed | import OK on Apple Silicon | build index + query returns neighbors |
| 10 | Embeddings | bge-m3 baseline available | runtime/quant pinned | embed text → vector of expected dim |
| 11 | Repository tests | repo deps installed | test config present | test suite passes |
| 12 | End-to-end RAG | full pipeline wired | retrieval/rerank/gen configured | query → retrieved + reranked + grounded answer (or abstain) |

## Rules

- Validate exactly one step; do not discuss later stages until the current passes.
- Each FAIL: stop, record root cause + exact commands + verification command in
  `docs/status.md`, resolve before proceeding.
- Step 8 is conditional — only executed if a component requires PyTorch MPS.
