---
description: Prepare release materials and optionally open a PR after explicit human go-ahead.
argument-hint: Prepare Stage A or carry out explicitly authorized Stage B.
---
# Phase 8: pr (agent: pr)

STEP 1: Run `python orchestrator.py status`. If pr is not ACTIVE, STOP unless all phases are APPROVED and the human has explicitly said `go` for Stage B.

## Read
Read all approved artifacts, especially `artifacts/verify.md`, and inspect Git state read-only.

## Write (only these files)
- `artifacts/pr.md`
- `CHANGELOG.md`

## Scope
Delegate to the `pr` subagent (Task tool). Stage A requires `Result: PASS`, prepares release files, submits, and stops. Stage B is a later invocation after all approvals and explicit `go`; use only the safe sequence in the agent instructions. Never edit `sdlc/`, `orchestrator.py`, `.claude/hooks/`, or `.claude/settings.json`; never approve/reject/reopen. Never force push or use `git add -A`/`.`/`--no-verify`.

## Finish
Stage A: after the subagent returns, run its self-check, run `python orchestrator.py submit pr`, print exactly `Awaiting human approval. Run: python orchestrator.py approve pr --by <your-name>`, and stop. Stage B requires explicit `go` from the human; report real command outcomes and stop at the first error.
