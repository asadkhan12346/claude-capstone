---
description: Run explicit, requirement-by-requirement release verification.
argument-hint: Verify the active release candidate without changing code.
---
# Phase 7: verify (agent: verify)

STEP 1: Run `python orchestrator.py status`. If verify is not ACTIVE, STOP and tell the human.

STEP 2: Delegate to the `verify` subagent with approved requirements, implementation, tests, plan, and review. Run the self-check even when reporting FAIL, then run `python orchestrator.py submit verify` and stop per CLAUDE.md.
