---
description: "Prepare a PR description, changelog entry, and reviewer checklist from verified work."
agent: pr-author
argument-hint: "Identify the verified change set and release context."
tools: [read, search, edit]
---
After human approval to enter the PR stage, use [requirements.md](../../docs/requirements.md), [impl-plan.md](../../docs/impl-plan.md), [code-review.md](../../docs/code-review.md), and [test-report.md](../../docs/test-report.md) to draft [pr-description.md](../../docs/pr-description.md) and update the root [CHANGELOG.md](../../CHANGELOG.md) with the change and reviewer checklist.

Do not invent test results, edit source code, commit, or open a PR. Mark unknown details `Not Found` and return the drafts for human approval.