# oh-my-pi Tool Conventions

> On-demand reference. Not injected per turn. Applies only to agent runtimes that provide
> the oh-my-pi tool surface (`lsp`, `scout`/`task` subagents, `hub`). Claude Code does not
> expose these primitives — do not attempt to invoke them from a Claude Code session; use
> the LSP/Grep/Task/Bash tools it actually has instead. See `plans/lsp-task-browser-hub-optimization.md`
> for the adoption plan this reference implements.

## LSP-First (symbol-aware over text search)
- **Rename/refactor:** Always use `lsp references` before renaming any exported symbol. Text grep misses cross-file callsites, re-exports, and dynamic dispatch targets.
- **Pre-edit check:** Run `lsp diagnostics` on the target file before editing to surface existing type errors or unused imports.
- **Code actions:** Prefer `lsp code_actions` for import fixes, quick-fixes, and server-known refactors over hand edits.
- **Definition/type:** Use `lsp definition` / `lsp type_definition` for navigation; never guess symbol locations.

## Subagent Parallelism
- **Multi-file changes:** Dispatch parallel `scout` agents for independent file discovery (e.g., find all callers of a symbol, locate test files).
- **Independent tasks:** Use `task` with parallel subagents for truly independent work slices — no serialization unless data dependency exists.
- **No overhead:** Each task must skip formatters, linters, and project-wide test suites. Validate once at the end.

## Hub Dev Server Lifecycle
- **FastAPI/Gradio:** Use `hub start` for long-running services (dev server, watcher, debugger). Never use raw `bash` for persistent processes.
- **Pattern:** `hub start name="api" application="make" args=["serve"] ready={log: "Uvicorn running", port: 8000, timeout: 30}`
- **Teardown:** `hub stop api` before killing terminal; `hub restart api` for config changes.
