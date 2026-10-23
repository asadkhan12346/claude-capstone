---
description: Read-only implementation review for the approved plan.
argument-hint: Review the active implementation against its approved plan.
---
# Phase 6: review (agent: review)

STEP 1: Run `python orchestrator.py status`. If review is not ACTIVE, STOP and tell the human.

STEP 2: Delegate to the `review` subagent with all approved artifacts, implementation files, and tests. Review only; never fix code. After completion, run `python orchestrator.py submit review` and stop per CLAUDE.md.
