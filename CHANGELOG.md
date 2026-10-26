# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `notes/__init__.py` — Notes package init; re-exports `NoteError`, `NoteNotFoundError`, `ValidationError`, `StorageError` for clean external imports.
- `notes/app.py` — Core business logic for Notes CLI: exception hierarchy (`NoteError`, `NoteNotFoundError`, `ValidationError`, `StorageError`), atomic JSON persistence (`_load`, `_save` via `os.replace`), and CRUD operations (`create_note`, `list_notes`, `get_note`, `update_note`, `delete_note`) with `.strip()` input validation.
- `notes/cli.py` — Command-line interface: `main()` entry point with argparse five-subcommand parser (`create`, `list`, `view`, `update`, `delete`), `NOTES_PATH` environment variable for test isolation, stderr error output and exit code 1 on all application errors.
- `tests/test_notes.py` — 26 automated unit and CLI-integration tests across 7 test classes covering all FR-001–FR-007 and NFR-001–NFR-006 requirements.
- `README.md` — Project documentation: Python 3.11+ setup instructions, `notes.json` auto-creation note, usage examples for all five CLI subcommands, error handling description, and test run instructions.
- `notes/` package directory committed to branch `sdlc/todo-cli` under user story NOTE-101.

### Changed

- `.claude/agents/orchestrator.md` — Introduced hierarchical orchestrator agent with Agent tool support for multi-phase delegation (`/run` entry point).
- `.claude/agents/architecture.md`, `design-review.md`, `implementation.md`, `planning.md`, `pr.md`, `requirements.md`, `review.md`, `verify.md` — Rewrote all phase agent bodies to align with orchestrator-based delegation pipeline and two-master-prompt convention (`CLAUDE.md` + `docs/CONTRACT.md`).
- `.claude/commands/run.md` — New consolidated `/run` command replaces per-phase slash commands; routes to orchestrator agent.
- `.claude/commands/pr.md` — Updated PR command for Stage A/B split with `github_pr.py` safety checks.
- `.claude/skills/pr/SKILL.md` — Updated PR skill with preflight, check-files, and verify-pr steps.
- `.mcp.json` — Updated MCP server configuration (GitHub MCP restricted to PR Stage B only).
- `artifacts/requirements.md`, `architecture.md`, `design-review.md`, `implementation-plan.md`, `review.md`, `verify.md` — All phase artifacts updated and APPROVED for Notes CLI (NOTE-101).
- `docs/CONTRACT.md` — Updated pipeline contract: phase order, file ownership, status model, protected paths, orchestrator CLI specification.
- `docs/RUNBOOK.md` — Updated 14-step runbook for orchestrator-based pipeline.
- `sdlc/phases.json` — Phase manifest updated; all 8 phases present with correct ownership and approval gate configuration.
- `sdlc/state.json` — Pipeline state updated; all 8 phases APPROVED for Notes CLI release.
- `sdlc/audit.log.jsonl` — Audit log updated with all phase submit/approve events.
- `tests/test_config.py` — Updated configuration tests: consolidated commands (2 files only), orchestrator agent has Agent tool, phases reference run.md/pr.md.
- `tests/test_github_pr.py` — Updated GitHub PR safety tool tests.
- `tests/test_orchestrator.py` — Updated orchestrator CLI tests including 8-phase pipeline end-to-end scenario.
- `tools/github_pr.py` — Updated with preflight, check-files, and verify-pr subcommands for PR Stage B safety checks.
- `user_story.md` — Updated to NOTE-101 Notes CLI user story.

### Fixed

- F-01: Replaced non-atomic file write with `os.replace`-based atomic write in `notes/app.py:_save`; eliminates risk of corrupt `notes.json` on interrupted write.
- F-02: Added `StorageError` wrapping around `json.JSONDecodeError` in `notes/app.py:_load`; corrupt JSON now raises a typed exception rather than propagating a raw decode error.
- F-03: Added CLI integration tests (`TestCLIIntegration`) using `subprocess` to exercise FR-002 empty-list indication and FR-005 delete confirmation through the actual CLI entry point.
- F-04: Added `README.md` with setup instructions and all five subcommand usage examples, satisfying NFR-006.
- F-05: Applied `.strip()` to title and content in both `create_note` and `update_note`; whitespace-only inputs now correctly raise `ValidationError`.
