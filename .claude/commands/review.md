---
description: Read-only implementation review for the approved plan.
argument-hint: Review the active implementation against its approved plan.
---
# Phase 6: review (agent: review)

STEP 1: Run `python orchestrator.py status`. If review is not ACTIVE, STOP and tell the human.

## Read
Read all approved artifacts, implementation files, and tests.

## Write (only these files)
- `artifacts/review.md`

## Scope
Delegate to the `review` subagent (Task tool). Review only; never fix code. Run unittest and compileall and report real evidence. Include every FR/NFR in traceability. Never edit `sdlc/`, `orchestrator.py`, `.claude/hooks/`, or `.claude/settings.json`; never run approve/reject/reopen or begin verify.

## Finish
After the subagent returns, run its self-check, run `python orchestrator.py submit review`, print exactly `Awaiting human approval. Run: python orchestrator.py approve review --by <your-name>`, and stop.
