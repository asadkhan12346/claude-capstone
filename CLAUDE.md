# Agentic SDLC Project Instructions

## Master Prompts
This project uses exactly two master prompt files:
1. `CLAUDE.md` (this file) — project-wide rules, shared conventions, orchestration protocol, and security controls. All agents and commands inherit these rules.
2. `docs/CONTRACT.md` — the authoritative pipeline specification: phase order, file ownership, status model, protected paths, orchestrator CLI, and traceability rules.

Agent files (`.claude/agents/`) and slash commands (`.claude/commands/`) are Claude Code conventions — thin, phase-specific definitions that derive their rules from these two masters. Skills (`.claude/skills/`) provide reusable methods for verify and pr phases.

## Pipeline
- Read `docs/CONTRACT.md` and run `python orchestrator.py status` before work.
- Work only when your phase is ACTIVE and only in files it owns.
- Submit with `python orchestrator.py submit <phase>` and stop for human approval.

## Orchestration — six-step delegation flow

The preferred entry point is `/run`. It implements this hierarchy:

1. **User → Orchestrator Agent** (`orchestrator`): receives the task, runs `python orchestrator.py status`, and creates a delegation plan.
2. **Orchestrator → Execution Agent**: routes to the active phase's agent (`requirements`, `architecture`, …, `pr`) via the Agent tool.
3. **Execution Agent → Orchestrator**: returns files written, test output, errors, and whether submit was already run.
4. **Orchestrator → Specialized Subagents** (when needed): e.g., a read-only test runner after implementation, or a verify-pass check before PR Stage A.
5. **Subagents → Orchestrator**: return findings; orchestrator consolidates.
6. **Orchestrator → User**: reports phase result, files changed, subagent findings, approval gate instruction, and any unresolved issues.

**Rules for the orchestrator:**
- Never delegate to a phase that is not ACTIVE.
- Human approval gates are preserved — stop after submit, print the exact instruction.
- Never run `approve`, `reject`, or `reopen`.
- Delegate specialized subagents only when genuinely useful; avoid unnecessary delegation.
- Delegate downward only — never back to the calling session or laterally.
- The existing individual phase commands (`/requirements`, `/architecture`, etc.) remain available for direct delegation without the orchestrator layer.

GitHub MCP is used only in PR Stage B (`mcp__github__create_pull_request`). No other phase uses GitHub MCP.

## Requirements
- Ask the human about ambiguities; never assume answers.
- Record each answer with its source. Keep the pipeline story-agnostic.

## Scope
- Make minimal changes only to phase-owned files. Never create later-phase artifacts.
- Never edit `sdlc/`, `orchestrator.py`, `.claude/hooks/`, or `.claude/settings.json` during a phase.

## Code quality
- Python 3.11+, standard library only, PEP 8, type hints on every function signature.
- No bare `except:` clauses, network calls in application code, or secrets.

## Security
- No secrets, credentials, or tokens in any file. No network calls in application code.

## Testing
- Use `unittest` only. Run `python -m unittest discover -s tests -v` after code changes.
- Run `python -m compileall -q .` before implementation submission.

## Traceability
- Define FR-/NFR- IDs in requirements and cite them in later artifacts and tests.

## Human approval
- Agents never run `approve`, `reject`, or `reopen`.
- After submit, stop and print exactly: `Awaiting human approval. Run: python orchestrator.py approve <phase> --by <your-name>`.
- Never edit `sdlc/`, `orchestrator.py`, `.claude/hooks/`, or `.claude/settings.json`.

## Question protocol (main session only)
- For requirements, architecture, design-review, and planning phases: the main session (slash command) asks the human numbered clarifying questions with AskUserQuestion or a plain chat message, waits for answers, then passes the answers to the subagent.
- Subagents only read inputs, write their owned files, and return a short report. They never ask the human directly.
- If a subagent receives a delegation without answers to required questions, it returns the question list and writes nothing.

## Git
- No force push, history rewrite, `--no-verify`, or push to main/master.
- Use conventional commits. Never amend published commits.

## Auditability
- Report only observed facts and real command output. Never claim an unrun check passed.
- Do not hand-edit `sdlc/state.json`, `sdlc/audit.log.jsonl`, or `sdlc/phases.json`.
