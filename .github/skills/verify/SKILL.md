---
name: verify
description: Execute a traceable verification run and report authentic evidence.
user-invocable: false
---
# Verification Method

## Check selection
Choose one check per FR/NFR: unit test first, then CLI command, then manual check. Use a temporary directory for any command that mutates state or data.

## Evidence protocol
Write expected result before running the command. Paste the real output unedited in a fenced block and show its exit code. `[... trimmed ...]` is the only permitted output omission marker. Do not claim or infer results. Do not rerun a failing check until the failure has been recorded and explained.

## Failure handling
Record failures, environment limits, and unexpected behavior under Failures and notes. Never alter code, tests, or expected results. Submit the report even on FAIL; do not approve the phase.

## Artifact template
Use `# Verification`, `## Environment` (including `python --version`), `## Checks`, `## Results table`, `## Failures and notes`, and a final `Result: PASS` or `Result: FAIL` line. Mention every FR/NFR and include fenced command/output evidence.

## Validation checklist
- Every requirement has one named, actually executed check.
- Each expected result precedes its check.
- Output and exit code match observed command results.
- PASS is used only when every result row passes.
- `git status --short` confirms the real repository was not modified by stateful tests.

## Stop condition
Submit the report regardless of result, then stop and print the exact human-approval instruction.
