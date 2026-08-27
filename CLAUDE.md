# CLAUDE.md

@AGENTS.md

`AGENTS.md` above is the canonical source for project context, commands, architecture,
refusal criteria, and conventions — edit it, not this file. Claude Code reads it via this
import; other agents read it directly.

## Claude-Code-only notes

- `/graphify` triggers the graphify skill for turning inputs into the knowledge graph — see
  `.claude/CLAUDE.md` / `.claude/skills/graphify/SKILL.md`. The ongoing "query graphify before
  grepping" habit for this codebase is in `AGENTS.md` § graphify.
- Model routing (`AGENTS.md` § Model Routing) maps to Claude Code's `/model` command.
- oh-my-pi tool conventions (`docs/oh-my-pi-tooling.md`) do not apply here — Claude Code has
  no `lsp`/`scout`/`hub` primitives; use its native LSP/Task/Bash tools instead.
