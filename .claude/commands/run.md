---
description: Auto-detect the active pipeline phase and execute it through the central orchestrator agent. Preferred entry point for all phase work.
argument-hint: Optional human answers, context, or instructions to pass to the orchestrator.
---
# /run — Orchestrator-Driven Phase Execution

This command implements the full six-step delegation flow:
User → Orchestrator → Execution Agent → (Subagents) → Orchestrator → Report.

## STEP 1 — Check status
Run `python orchestrator.py status`. Identify `currentPhase` and `phaseStatus`.
- If `phaseStatus` is `AWAITING_APPROVAL`: tell the human; do not re-delegate.
- If `phaseStatus` is `COMPLETE` or no phase is ACTIVE: tell the human and stop.

## STEP 2 — Gather human input (phases that require it)
- **requirements**: read `user_story.md`, list every ambiguity as numbered questions, ask the human with AskUserQuestion or a plain message, and WAIT for answers.
- **planning**: if the design-review verdict is REVISE or any High/Med finding is unresolved, ask the human which findings to incorporate and wait.
- **pr Stage B**: wait for the human to say `go` explicitly before proceeding.
- All other phases: proceed immediately.

## STEP 3 — Delegate to the orchestrator agent
Delegate to the `orchestrator` subagent (Agent tool) with:
- The active phase name
- All required prior approved artifacts as context
- Any human-provided answers or arguments from Step 2

The orchestrator agent owns the full lifecycle from here: it delegates to the execution agent, optionally spawns verification subagents, submits, and returns a consolidated report.

## STEP 4 — Relay the report
Relay the orchestrator agent's consolidated final report to the human verbatim. Do not re-summarize or drop information. If the orchestrator reported an error, relay it and stop — do not retry independently.
