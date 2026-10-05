---
description: Elicit and write approved-story requirements for phase 1.
argument-hint: Answer any clarifying questions the agent returns.
---
# Phase 1: requirements (agent: requirements)

STEP 1: Run `python orchestrator.py status`. If requirements is not ACTIVE, STOP and tell the human.

STEP 2: Read `user_story.md`, list every ambiguity as one numbered question list in a single message, ask the human with AskUserQuestion or a plain chat message, and WAIT for answers before delegating.

## Read
Read `user_story.md` and `docs/CONTRACT.md`.

## Write (only these files)
- `artifacts/requirements.md`

## Scope
Delegate to the `requirements` subagent (Task tool), passing all human answers. Use the requirements agent procedure and exact artifact headings. Record human answers with their source, define FR/NFR IDs, and leave no unanswered checkbox. Never edit `sdlc/`, `orchestrator.py`, `.claude/hooks/`, or `.claude/settings.json`. Never run approve/reject/reopen.

## Finish
After the subagent returns, run its self-check, run `python orchestrator.py submit requirements`, then print exactly: `Awaiting human approval. Run: python orchestrator.py approve requirements --by <your-name>`. Stop.
