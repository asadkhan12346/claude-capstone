---
description: Run the active pipeline phase (requirements through verify) through the central orchestrator. Use /pr for the PR phase.
argument-hint: Optionally pass human answers or context for the active phase.
---
# /run — Execute the Active Phase

Entry point for pipeline phases 1–7. Phase 8 (pr) uses `/pr`.

## Step 1 — Check status
Run `python orchestrator.py status`. Stop and report if:
- Active phase is `pr` — tell the human to use `/pr` instead
- `phaseStatus` is `AWAITING_APPROVAL` — print the approval command and stop
- `phaseStatus` is `COMPLETE` — report and stop

## Step 2 — Gather human input (two phases require it)
- **requirements**: read `user_story.md`, list every ambiguity as numbered questions, ask the human, and WAIT for answers before delegating
- **planning**: if the design-review verdict is REVISE or any High/Med finding is unresolved, ask which findings to incorporate and WAIT

All other active phases proceed immediately.

## Step 3 — Delegate to the orchestrator agent
Invoke the `orchestrator` subagent (Agent tool) and pass:
- The active phase name
- All required prior approved artifacts
- Human-provided answers or arguments from Step 2

The orchestrator owns the full lifecycle: routes to the execution agent, optionally spawns a verification subagent, submits, and returns a consolidated report.

## Step 4 — Relay the report
Relay the orchestrator's consolidated report to the human verbatim. If the orchestrator reports an error, relay it and stop.
