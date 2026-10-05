---
name: planning
description: Turn approved design decisions into ordered implementation tasks.
agent: planning
---
# Phase 4: planning (agent: planning)

STEP 1: Run `python orchestrator.py status`. If planning is not ACTIVE, STOP and tell the human.

## Read
Read requirements, architecture, design review, and `docs/CONTRACT.md`.

## Write (only these files)
- `artifacts/implementation-plan.md`

## Scope
Write a dependency-ordered plan, not code. If design review is REVISE or a High/Med finding is unresolved, ask the human which findings to incorporate and wait. Never edit `sdlc/`, `orchestrator.py`, `hooks/`, `.github/hooks/`; never run approve/reject/reopen or begin implementation.

## Finish
Follow the planning agent procedure and self-check, run `python orchestrator.py submit planning`, print exactly `Awaiting human approval. Run: python orchestrator.py approve planning --by <your-name>`, and stop.
