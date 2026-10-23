---
description: Implement one approved plan task at a time in the owned app files.
argument-hint: Execute the next approved plan tasks for the active implementation phase.
---
# Phase 5: implementation (agent: implementation)

STEP 1: Run `python orchestrator.py status`. If implementation is not ACTIVE, STOP and tell the human.

STEP 2: Delegate to the `implementation` subagent with approved requirements, architecture, design review, plan, and contract. After completion, confirm real compileall and unittest output is shown, then run `python orchestrator.py submit implementation` and stop per CLAUDE.md.
