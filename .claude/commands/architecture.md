---
description: Design the system for the approved requirements.
argument-hint: Produce the architecture for the active story.
---
# Phase 2: architecture (agent: architecture)

STEP 1: Run `python orchestrator.py status`. If architecture is not ACTIVE, STOP and tell the human.

STEP 2: Delegate to the `architecture` subagent with approved requirements and contract. If it returns questions instead of an artifact, ask the human, wait for answers, and re-invoke with the answers. After completion, run `python orchestrator.py submit architecture` and stop per CLAUDE.md.
