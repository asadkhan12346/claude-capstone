---
description: Turn approved design decisions into ordered implementation tasks.
argument-hint: Plan the active implementation work.
---
# Phase 4: planning (agent: planning)

STEP 1: Run `python orchestrator.py status`. If planning is not ACTIVE, STOP and tell the human.

STEP 2: If the design-review verdict is REVISE or any High/Med finding is unresolved, ask the human which findings to incorporate and wait for answers. Delegate to the `planning` subagent with all predecessor artifacts and any human answers. After completion, run `python orchestrator.py submit planning` and stop per CLAUDE.md.
