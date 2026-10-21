# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- **`todo/app.py` — Application layer** (US-001, FR-001 through FR-018, NFR-001 through NFR-003)
  - `StorageError` exception class for unrecoverable storage failures (F-04)
  - `load(path)` — reads JSON storage file; handles missing file, empty file, malformed JSON, and
    unexpected I/O errors; always uses UTF-8 encoding (FR-016, FR-017, NFR-002)
  - `save(path, data)` — writes JSON atomically via a temp file and `os.replace()`; ensures parent
    directory exists; cleans up temp file on failure (FR-016, NFR-002, F-02)
  - `create_task(storage_path, title, description)` — creates a task with trimmed title, optional
    description (defaults to `""`), status `pending`, and auto-incremented unique ID (FR-001, FR-002,
    FR-013, FR-014, FR-015)
  - `list_tasks(storage_path, status_filter)` — returns all tasks in creation (ascending ID) order
    with an optional `pending`/`completed` filter; returns no-tasks message for empty list
    (FR-003, FR-004, FR-005, F-06)
  - `update_task(storage_path, task_id, title, description)` — updates title and/or description
    using `None` as sentinel for "leave unchanged"; trims title; leaves ID and status untouched
    (FR-006, FR-012, FR-013, F-03)
  - `delete_task(storage_path, task_id)` — removes a task by ID; does not decrement the ID counter
    (FR-007, FR-012, FR-015)
  - `mark_completed(storage_path, task_id)` — sets task status to `completed`; idempotent guard
    returns informational result without writing when already completed (FR-008, FR-009, FR-012)
  - `mark_pending(storage_path, task_id)` — sets task status to `pending`; idempotent guard
    returns informational result without writing when already pending (FR-010, FR-011, FR-012)

- **`todo/__init__.py` — Package initializer** (NFR-001)
  - Marks `todo/` as a Python package
  - Re-exports the full public API (`StorageError`, `create_task`, `list_tasks`, `update_task`,
    `delete_task`, `mark_completed`, `mark_pending`) from `todo.app`

- **`todo/cli.py` — CLI entry point** (FR-018, NFR-001, F-01, F-05)
  - `main()` function using `argparse` with six sub-commands: `create`, `list`, `update`,
    `delete`, `complete`, `pending`
  - `DEFAULT_STORAGE_PATH` constant: `~/.todo.json` (F-05)
  - Canonical invocation: `python -m todo.cli <subcommand> [args]` (F-01)
  - Success and informational messages printed to stdout (exit code 0)
  - Error messages printed to stderr (exit code 1)
  - `--storage` flag accepted by all sub-commands for custom storage file path

- **`tests/test_todo.py` — Automated test suite** (NFR-004)
  - 11 test classes covering all FRs, NFRs, and design findings F-01 through F-06:
    `TestStorageLoad`, `TestStorageSave`, `TestCreateTask`, `TestListTasks`, `TestUpdateTask`,
    `TestDeleteTask`, `TestMarkCompleted`, `TestMarkPending`, `TestMessages`, `TestNFR002UTF8`,
    `TestCLIIntegration`
  - 57 todo-specific tests; all method names cite FR/NFR IDs
  - All tests use `tempfile.TemporaryDirectory` for isolation; no test writes to `~/.todo.json`
  - CLI integration tests invoke `python -m todo.cli` via `subprocess`

### Changed

- `user_story.md` — source story US-001 ingested from Confluence (page 12550145,
  fetched 2026-10-21T19:37:30Z); no content change to the story itself
- `artifacts/requirements.md`, `artifacts/architecture.md`, `artifacts/design-review.md`,
  `artifacts/implementation-plan.md`, `artifacts/review.md`, `artifacts/verify.md` — SDLC
  pipeline artifacts produced and approved across phases 1-7; recorded in `sdlc/state.json`
  and `sdlc/audit.log.jsonl`

### Fixed

- Design finding F-01: canonical invocation is `python -m todo.cli` (no `__main__.py` needed)
- Design finding F-02: `save()` uses atomic write via temp file + `os.replace()` to prevent
  partial-write corruption
- Design finding F-03: `update_task()` uses `None` sentinel to distinguish "leave unchanged"
  from an empty-string description
- Design finding F-04: `load()` raises `StorageError` (not bare `OSError`) on malformed JSON
  or unexpected I/O, allowing all callers to catch a single named exception
- Design finding F-05: default storage path changed from CWD-relative `todo.json` to
  `~/.todo.json` (user home directory)
- Design finding F-06: `list_tasks()` return shape always contains a `"tasks": list` key
