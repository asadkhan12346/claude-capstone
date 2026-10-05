---
description: Independently review the approved design and record a verdict.
argument-hint: Review the active architecture without editing it.
---
# Phase 3: design-review (agent: design-review)

STEP 1: Run `python orchestrator.py status`. If design-review is not ACTIVE, STOP and tell the human.

## Read
Read approved requirements and architecture, plus the contract.

## Write (only these files)
- `artifacts/design-review.md`

## Scope
Delegate to the `design-review` subagent (Task tool). Do not edit the architecture or source. Review coverage, alternatives, security, usability, and accessibility. A High finding or uncovered requirement means REVISE. Never edit `sdlc/`, `orchestrator.py`, `.claude/hooks/`, or `.claude/settings.json`; never run approve/reject/reopen or begin planning.

## Finish
After the subagent returns, run its self-check, run `python orchestrator.py submit design-review`, print exactly `Awaiting human approval. Run: python orchestrator.py approve design-review --by <your-name>`, and stop.
