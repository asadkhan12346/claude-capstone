---
name: requirements
description: Elicit and write approved-story requirements for phase 1.
agent: requirements
---
# Phase 1: requirements (agent: requirements)

STEP 1: Run `python orchestrator.py status`. If requirements is not ACTIVE, STOP and tell the human.

STEP 2: Read `user_story.md`, list every ambiguity as one numbered question list in a single message, ask the human, and WAIT for answers before writing.

## Read
Read `user_story.md` and `docs/CONTRACT.md`.

## Write (only these files)
- `artifacts/requirements.md`

## Scope
Use the requirements agent procedure and exact artifact headings. Record human answers with their source, define FR/NFR IDs, and leave no unanswered checkbox. Never edit `sdlc/`, `orchestrator.py`, `hooks/`, or `.github/hooks/`. Never run approve/reject/reopen.

## Finish
Follow the agent procedure, run its self-check, run `python orchestrator.py submit requirements`, then print exactly: `Awaiting human approval. Run: python orchestrator.py approve requirements --by <your-name>`. Stop.
