---
description: Run explicit, requirement-by-requirement release verification.
argument-hint: Verify the active release candidate without changing code.
---
# Phase 7: verify (agent: verify)

STEP 1: Run `python orchestrator.py status`. If verify is not ACTIVE, STOP and tell the human.

## Read
Read approved requirements, implementation, tests, plan, and review.

## Write (only these files)
- `artifacts/verify.md`

## Scope
Delegate to the `verify` subagent (Task tool). For each FR/NFR state expected output before running its check. Paste actual output and exit codes. Use temporary paths for state-changing checks, finish with `git status --short`, and never fix code. Never edit `sdlc/`, `orchestrator.py`, `.claude/hooks/`, or `.claude/settings.json`; never run approve/reject/reopen.

## Finish
After the subagent returns, run its self-check even when reporting FAIL, run `python orchestrator.py submit verify`, print exactly `Awaiting human approval. Run: python orchestrator.py approve verify --by <your-name>`, and stop.
