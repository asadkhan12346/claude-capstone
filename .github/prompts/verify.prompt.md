---
description: "Verify approved acceptance criteria and tests, recording evidence and gaps."
argument-hint: "Name any additional verification required for this change."
tools: [read, search, execute, edit]
---
Use the approved [requirements.md](../../docs/requirements.md), [impl-plan.md](../../docs/impl-plan.md), and [code-review.md](../../docs/code-review.md) as the verification basis. Run pytest and other relevant checks; record commands, results, unmet criteria, and limitations in [test-report.md](../../docs/test-report.md).

Never claim a check passed unless it ran successfully. Do not change implementation while verifying. Stop for human approval before PR preparation.