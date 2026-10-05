---
name: verify
description: Run explicit, requirement-by-requirement release verification.
agent: verify
---
# Phase 7: verify (agent: verify)

STEP 1: Run `python orchestrator.py status`. If verify is not ACTIVE, STOP and tell the human.

## Read
Read approved requirements, implementation, tests, plan, and review.

## Write (only these files)
- `artifacts/verify.md`

## Scope
For each FR/NFR state expected output before running its check. Paste actual output and exit codes. Use temporary paths for state-changing checks, finish with `git status --short`, and never fix code. Never edit `sdlc/`, `orchestrator.py`, `hooks/`, `.github/hooks/`; never run approve/reject/reopen.

## Finish
Follow the verify agent procedure and self-check even when reporting FAIL, run `python orchestrator.py submit verify`, print exactly `Awaiting human approval. Run: python orchestrator.py approve verify --by <your-name>`, and stop.
