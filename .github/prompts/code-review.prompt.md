---
description: "Review implementation against the approved plan and produce a Markdown findings report."
argument-hint: "Provide a commit, change set, or files to review."
tools: [read, search, edit]
---
Compare the requested changes and tests with the approved [impl-plan.md](../../docs/impl-plan.md). Review correctness, scope, input validation, secret exposure, error handling, empty or missing inputs, regressions, and test coverage.

Write prioritized findings with file references to [code-review.md](../../docs/code-review.md). If there are no findings, say so and record residual risks. Do not modify implementation or tests; request human approval before verification.