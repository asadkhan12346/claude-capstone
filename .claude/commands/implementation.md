---
description: Implement one approved plan task at a time in the owned app files.
argument-hint: Execute the next approved plan tasks for the active implementation phase.
---
# Phase 5: implementation (agent: implementation)

STEP 1: Run `python orchestrator.py status`. If implementation is not ACTIVE, STOP and tell the human.

## Read
Read approved requirements, architecture, design review, plan, and contract.

## Write (only these files)
- `todo/__init__.py`
- `todo/app.py`
- `todo/cli.py`
- `tests/test_todo.py`

## Scope
Delegate to the `implementation` subagent (Task tool). Follow plan task order. Stop if the plan is wrong. Every FR needs a requirement-tagged test using temporary files. Do not weaken tests. Show real compileall and unittest output. Summarize `task id -> files -> FR/NFR ids`. Never edit `sdlc/`, `orchestrator.py`, `.claude/hooks/`, `.claude/settings.json`; never run approve/reject/reopen.

## Finish
After the subagent returns, confirm actual compileall and unittest output is shown, run `python orchestrator.py submit implementation`, print exactly `Awaiting human approval. Run: python orchestrator.py approve implementation --by <your-name>`, and stop.
