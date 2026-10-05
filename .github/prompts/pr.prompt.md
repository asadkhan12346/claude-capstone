---
name: pr
description: Prepare release materials and optionally open a PR after explicit human go-ahead.
agent: pr
---
# Phase 8: pr (agent: pr)

STEP 1: Run `python orchestrator.py status`. If pr is not ACTIVE, STOP unless all phases are APPROVED and the human has explicitly said `go` for Stage B.

## Read
Read all approved artifacts, especially `artifacts/verify.md`, and inspect Git state read-only.

## Write (only these files)
- `artifacts/pr.md`
- `CHANGELOG.md`

## Scope
Stage A requires `Result: PASS`, prepares release files, submits, and stops. Stage B is a later invocation after all approvals and explicit `go`; use only the safe sequence in the agent instructions. Never edit `sdlc/`, `orchestrator.py`, `hooks/`, `.github/hooks/`; never approve/reject/reopen. Never force push or use `git add -A`/`.`/`--no-verify`.

## Finish
Follow the agent procedure and self-check. Stage A runs `python orchestrator.py submit pr` then prints exactly `Awaiting human approval. Run: python orchestrator.py approve pr --by <your-name>` and stops. Stage B asks for `go` if not already given, then reports real command outcomes and stops at the first error.
