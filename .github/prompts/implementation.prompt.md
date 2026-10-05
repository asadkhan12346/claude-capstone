---
name: implementation
description: Implement one approved plan task at a time in the owned app files.
agent: implementation
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
Follow plan task order. Stop if the plan is wrong. Every FR needs a requirement-tagged test using temporary files. Do not weaken tests. Run unittest and compileall and show their real output. Summarize `task id -> files -> FR/NFR ids`. Never edit `sdlc/`, `orchestrator.py`, `hooks/`, `.github/hooks/`; never run approve/reject/reopen.

## Finish
Follow the implementation agent procedure and self-check, run `python orchestrator.py submit implementation`, print exactly `Awaiting human approval. Run: python orchestrator.py approve implementation --by <your-name>`, and stop.
