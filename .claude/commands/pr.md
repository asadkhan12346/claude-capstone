---
description: Prepare and submit PR materials (Stage A), then create the pull request after explicit human authorization (Stage B).
argument-hint: Stage A runs automatically when pr is ACTIVE. Stage B requires the human to say "go" after all phases are approved.
---
# /pr — PR Phase (Stage A and Stage B)

## Stage A — prepare release materials
Run when the `pr` phase is ACTIVE.

1. Run `python orchestrator.py status`. Stop if pr is not ACTIVE (unless all phases are APPROVED and the human said `go` for Stage B).
2. Read all approved artifacts, especially `artifacts/verify.md`. Stop if `Result: PASS` is absent.
3. Delegate to the `pr` subagent (Agent tool) with all approved artifacts. The agent writes `artifacts/pr.md` and `CHANGELOG.md`.
4. Check status: run `python orchestrator.py status`. If `pr` is already `AWAITING_APPROVAL` the agent submitted — skip to step 5. If `pr` is still `ACTIVE`, run `python orchestrator.py submit pr`. On refusal (missing artifact or traceability error), relay the exact error and stop.
5. Print exactly: `Awaiting human approval. Run: python orchestrator.py approve pr --by <your-name>`. Stop.

## Stage B — create the pull request
Run only after ALL 8 phases are APPROVED and the human has explicitly said `go`.

1. Confirm all phases are APPROVED via `python orchestrator.py status`.
2. Delegate to the `pr` subagent (Agent tool) with explicit Stage B authorization.
3. The agent runs preflight checks, creates the branch, stages allowed files, commits, pushes, and creates the PR via GitHub MCP (`mcp__github__create_pull_request`) or `gh pr create` as fallback.
4. Relay the agent's final PR URL or first error verbatim. Never claim success without the agent's confirmed output.

## Rules
Never use force push, `git add -A`/`.`, or `--no-verify`. Never edit `sdlc/`, `orchestrator.py`, `.claude/hooks/**`, or `.claude/settings.json`. Never approve, reject, or reopen.
