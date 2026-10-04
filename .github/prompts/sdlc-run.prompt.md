---
name: sdlc-run
description: "Read the SDLC state table, validate approval gates, and delegate the next pending stage to the orchestrator."
agent: sdlc-orchestrator
argument-hint: "Optional: provide feedback or say which approved stage to resume."
---
Read [docs/sdlc-state.md](../../docs/sdlc-state.md) and follow the [SDLC orchestrator](../agents/sdlc-orchestrator.agent.md).

Determine the earliest stage that is not Approved. Verify that its predecessor's output file exists and its state is Approved before delegating. Run only that stage using the matching specialist agent and its prepared handoff prompt. If a stage is awaiting approval, stop and ask the user to type `APPROVE` or provide feedback; do not proceed. Do not skip, combine, or reorder stages, and do not write code or stage documents yourself. Update only status tracking in `docs/sdlc-state.md`.