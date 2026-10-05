---
name: review
description: Read-only implementation review for the approved plan.
agent: review
---
# Phase 6: review (agent: review)

STEP 1: Run `python orchestrator.py status`. If review is not ACTIVE, STOP and tell the human.

## Read
Read all approved artifacts, implementation files, and tests.

## Write (only these files)
- `artifacts/review.md`

## Scope
Review only; never fix code. Run unittest and compileall and report real evidence. Include every FR/NFR in traceability. Never edit `sdlc/`, `orchestrator.py`, `hooks/`, `.github/hooks/`; never run approve/reject/reopen or begin verify.

## Finish
Follow the review agent procedure and self-check, run `python orchestrator.py submit review`, print exactly `Awaiting human approval. Run: python orchestrator.py approve review --by <your-name>`, and stop.
