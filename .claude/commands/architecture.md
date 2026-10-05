---
description: Design the system for the approved requirements.
argument-hint: Produce the architecture for the active story.
---
# Phase 2: architecture (agent: architecture)

STEP 1: Run `python orchestrator.py status`. If architecture is not ACTIVE, STOP and tell the human.

## Read
Read approved `artifacts/requirements.md` and `docs/CONTRACT.md`.

## Write (only these files)
- `artifacts/architecture.md`

## Scope
Delegate to the `architecture` subagent (Task tool). No code. Map every FR/NFR to components, explain data/control flow and decisions, and include a fenced Mermaid diagram. If the subagent returns questions instead of an artifact, ask the human those questions, wait for answers, and re-invoke the subagent with the answers. Never edit `sdlc/`, `orchestrator.py`, `.claude/hooks/`, or `.claude/settings.json`; never run approve/reject/reopen or begin phase 3.

## Finish
After the subagent returns, run its self-check, run `python orchestrator.py submit architecture`, print exactly `Awaiting human approval. Run: python orchestrator.py approve architecture --by <your-name>`, and stop.
