---
name: pr
description: Prepare traceable release artifacts and follow a human-authorized GitHub PR sequence.
user-invocable: false
---
# PR Release Method

## Stage A: release files
Proceed only when the PR phase is ACTIVE and verify says `Result: PASS`. Write `artifacts/pr.md` with Summary, What changed, Traceability, Test evidence, Risks, Rollback, and Reviewer checklist. Update `CHANGELOG.md` in Keep a Changelog format with Unreleased, Added, Changed, and Fixed. Submit and stop for human approval.

## Stage B: authorized Git sequence
Proceed only in a later invocation after every phase is APPROVED and the human explicitly says `go`. Check `git rev-parse --show-toplevel`, `git remote -v`, and that the current branch is not main/master. Create `sdlc/<slug>` with at most 40 characters. Stage only `artifacts todo tests/test_todo.py CHANGELOG.md sdlc/state.json sdlc/audit.log.jsonl`; inspect `git diff --cached --name-only`; commit conventionally, push the feature branch, then run `gh pr create --title ... --body-file artifacts/pr.md`.

## Safety rules
Never use force push, `git add -A`, `git add .`, `--no-verify`, history rewriting, or push to main/master. Do not stage files outside the allowlist. Do not claim a push or PR succeeded without actual output. Stop on any command error; never retry with a bypass.

## On failure
Report the exact failing command and observed error. Do not change remote settings, authenticate, or edit unrelated files. The human resolves setup problems.

## Templates
PR headings: Summary; What changed; Traceability (each ID to evidence); Test evidence; Risks; Rollback; Reviewer checklist.
Changelog headings: `## [Unreleased]`, then Added, Changed, and Fixed.

## Validation checklist
- Verification PASS and every requirement ID has evidence.
- Stage A outputs match observed changes.
- Stage B has explicit `go`, approved phases, safe branch, expected remote, and exact staged file list.
- No secrets or unrelated files are staged.

## Stop condition
After Stage A submission, stop for the human approval command. After Stage B, stop after reporting the actual PR result or first error.
