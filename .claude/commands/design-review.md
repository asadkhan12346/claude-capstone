---
description: Independently review the approved design and record a verdict.
argument-hint: Review the active architecture without editing it.
---
# Phase 3: design-review (agent: design-review)

STEP 1: Run `python orchestrator.py status`. If design-review is not ACTIVE, STOP and tell the human.

STEP 2: Delegate to the `design-review` subagent with approved requirements, architecture, and contract. Do not edit the architecture or source. After completion, run `python orchestrator.py submit design-review` and stop per CLAUDE.md.
