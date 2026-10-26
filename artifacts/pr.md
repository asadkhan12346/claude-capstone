# Pull Request: Notes CLI — NOTE-101

## Summary

This PR delivers a complete Notes CLI application implementing user story NOTE-101: "As a user, I want to create, view, update, and delete notes so that I can keep track of important information." The implementation provides full CRUD operations backed by atomic JSON persistence, a five-subcommand argparse CLI, and a dedicated exception hierarchy — all using Python standard library only. All 8 SDLC phases are APPROVED and 97 automated tests pass with zero failures.

---

## What Changed

### New files (Notes CLI application)

| File | Description |
|------|-------------|
| `notes/__init__.py` | Package init; re-exports `NoteError`, `NoteNotFoundError`, `ValidationError`, `StorageError` |
| `notes/app.py` | Core business logic: exception hierarchy, atomic `_load`/`_save`, `create_note`, `list_notes`, `get_note`, `update_note`, `delete_note` with `.strip()` validation |
| `notes/cli.py` | `main()` entry point with argparse five-subparser CLI (`create`, `list`, `view`, `update`, `delete`); `NOTES_PATH` env var for test isolation |
| `tests/test_notes.py` | 26 notes-specific unit and CLI-integration tests across 7 test classes |
| `README.md` | Setup instructions (Python 3.11+, notes.json auto-creation) and usage examples for all five subcommands |

### Modified files (pipeline infrastructure)

| File | Description |
|------|-------------|
| `.claude/agents/architecture.md` | Updated for orchestrator-based delegation pipeline |
| `.claude/agents/design-review.md` | Updated for orchestrator-based delegation pipeline |
| `.claude/agents/implementation.md` | Updated for orchestrator-based delegation pipeline |
| `.claude/agents/orchestrator.md` | Added hierarchical orchestrator agent with Agent tool delegation |
| `.claude/agents/planning.md` | Updated for orchestrator-based delegation pipeline |
| `.claude/agents/pr.md` | Updated Stage A/B procedures for new pipeline |
| `.claude/agents/requirements.md` | Updated for orchestrator-based delegation pipeline |
| `.claude/agents/review.md` | Updated for orchestrator-based delegation pipeline |
| `.claude/agents/verify.md` | Updated for orchestrator-based delegation pipeline |
| `.claude/commands/pr.md` | Updated PR command for new pipeline |
| `.claude/commands/run.md` | New `/run` orchestrator entry-point command |
| `.claude/skills/pr/SKILL.md` | Updated PR skill for Stage A/B |
| `.mcp.json` | Updated MCP server configuration |
| `artifacts/architecture.md` | Notes CLI architecture artifact (APPROVED) |
| `artifacts/design-review.md` | Design review findings and resolutions (APPROVED) |
| `artifacts/implementation-plan.md` | Implementation plan tasks T-01 through T-07 (APPROVED) |
| `artifacts/requirements.md` | FR-001–FR-007 and NFR-001–NFR-006 (APPROVED) |
| `artifacts/review.md` | Code review verdict APPROVE with traceability matrix (APPROVED) |
| `artifacts/verify.md` | Verification report; all 97 tests PASS (APPROVED) |
| `docs/CONTRACT.md` | Updated pipeline contract specification |
| `docs/RUNBOOK.md` | Updated 14-step runbook |
| `sdlc/audit.log.jsonl` | Audit log entries for all 8 phases |
| `sdlc/phases.json` | Phase manifest with all 8 phases |
| `sdlc/state.json` | Pipeline state tracking all approvals |
| `tests/test_config.py` | Updated config tests for consolidated commands |
| `tests/test_github_pr.py` | Updated GitHub PR safety tool tests |
| `tests/test_orchestrator.py` | Updated orchestrator CLI tests |
| `tools/github_pr.py` | Updated GitHub PR safety and verification tool |
| `user_story.md` | NOTE-101 user story |

### Deleted files (superseded)

| File | Description |
|------|-------------|
| `.claude/commands/architecture.md` | Superseded by consolidated `/run` command |
| `.claude/commands/design-review.md` | Superseded by consolidated `/run` command |
| `.claude/commands/implementation.md` | Superseded by consolidated `/run` command |
| `.claude/commands/planning.md` | Superseded by consolidated `/run` command |
| `.claude/commands/requirements.md` | Superseded by consolidated `/run` command |
| `.claude/commands/review.md` | Superseded by consolidated `/run` command |
| `.claude/commands/verify.md` | Superseded by consolidated `/run` command |
| `tests/test_todo.py` | Replaced by tests/test_notes.py for Notes CLI |
| `todo/__init__.py` | Todo CLI superseded by Notes CLI |
| `todo/app.py` | Todo CLI superseded by Notes CLI |
| `todo/cli.py` | Todo CLI superseded by Notes CLI |

---

## Traceability

### FR-001 — Create note (non-empty title + content, auto-increment ID, persisted)

- **Code**: `notes/app.py:create_note` (lines 84–116) — validates stripped title and content, assigns `next_id`, appends note dict, increments and persists `next_id`
- **Tests**: `TestCreateNote.test_fr001_create_returns_note`, `test_fr001_id_auto_increments`, `test_fr001_data_persists_across_load`

### FR-002 — View all notes (list all or show empty-list indication)

- **Code**: `notes/app.py:list_notes` (lines 119–129); `notes/cli.py:main` (lines 88–93) — returns list of all notes; CLI prints "No notes found." when list is empty
- **Tests**: `TestListNotes.test_fr002_returns_empty_list_when_no_notes`, `test_fr002_returns_all_created_notes`, `TestCLIIntegration.test_fr002_empty_list_indication`

### FR-003 — View note by ID (retrieve single note by integer ID)

- **Code**: `notes/app.py:get_note` (lines 132–151); `notes/cli.py:main` (lines 95–97) — looks up note by integer ID, raises `NoteNotFoundError` if absent
- **Tests**: `TestGetNote.test_fr003_returns_correct_note`

### FR-004 — Update note (full replace; both title and content required; non-empty)

- **Code**: `notes/app.py:update_note` (lines 154–187); `notes/cli.py:main` (lines 99–101) — validates both fields with `.strip()`, replaces title and content in-place, persists
- **Tests**: `TestUpdateNote.test_fr004_replaces_title_and_content`, `test_fr004_full_replace_both_fields`

### FR-005 — Delete note (remove by ID; confirmation shown)

- **Code**: `notes/app.py:delete_note` (lines 190–209); `notes/cli.py:main` (lines 103–105) — removes note by ID, CLI prints "Note N deleted."
- **Tests**: `TestDeleteNote.test_fr005_removes_note_from_storage`, `TestCLIIntegration.test_fr005_delete_confirmation`

### FR-006 — Error on non-existent note (NoteNotFoundError, no data mutation)

- **Code**: `notes/app.py:get_note` (line 151), `update_note` (line 187), `delete_note` (line 208) — each raises `NoteNotFoundError` when ID not found; no store modification occurs
- **Tests**: `TestGetNote.test_fr006_raises_not_found_for_absent_id`, `TestUpdateNote.test_fr006_raises_not_found_for_absent_id`, `TestDeleteNote.test_fr006_raises_not_found_for_absent_id`

### FR-007 — Invalid input rejection (ValidationError for empty/whitespace inputs)

- **Code**: `notes/app.py:create_note` (lines 102–105), `update_note` (lines 175–178) — `.strip()` applied; raises `ValidationError` with descriptive message for empty or whitespace-only title or content
- **Tests**: `TestCreateNote.test_fr007_empty_title_raises`, `test_fr007_whitespace_only_title_raises`, `test_fr007_empty_content_raises`, `test_fr007_whitespace_only_content_raises`; `TestUpdateNote.test_fr007_empty_title_raises`, `test_fr007_whitespace_only_title_raises`, `test_fr007_empty_content_raises`

### NFR-001 — JSON persistence (notes.json, auto-created, survives restarts)

- **Code**: `notes/app.py:_load` (lines 38–58), `_save` (lines 61–76) — `_load` returns default when file absent; `_save` uses `os.replace` for atomic write; `json.JSONDecodeError` wrapped as `StorageError`
- **Tests**: `TestStorage.test_nfr001_absent_file_returns_default`, `test_nfr001_data_survives_process_reload`, `test_f01_atomic_write_no_tmp_file_remains`, `test_f02_corrupt_json_raises_storage_error`

### NFR-002 — CLI interface (argparse with 5 subcommands)

- **Code**: `notes/cli.py:_build_parser` (lines 28–65) — argparse with subparsers for `create`, `list`, `view`, `update`, `delete`
- **Tests**: `TestCLIIntegration.test_fr002_empty_list_indication`, `test_fr005_delete_confirmation` (subprocess integration)

### NFR-003 — Auto-increment integer IDs (next_id persisted; never reused after delete)

- **Code**: `notes/app.py:create_note` (line 113), `delete_note` (lines 203–208) — `next_id` incremented on create and persisted; delete does not decrement `next_id`
- **Tests**: `TestCreateNote.test_fr001_id_auto_increments`, `TestDeleteNote.test_nfr003_id_not_reused_after_delete`

### NFR-004 — Automated test coverage (unittest, all FRs exercised, all pass)

- **Code**: `tests/test_notes.py` — 26 test methods covering all 7 FRs and all NFRs
- **Tests**: All 26 test methods in `tests/test_notes.py`; full suite of 97 tests passes

### NFR-005 — Informative error messages ("Note not found: N", "Title must not be empty.", stderr + exit 1)

- **Code**: `notes/app.py:NoteNotFoundError` (lines 21–22), `ValidationError` (lines 25–26), `StorageError` (lines 29–30); `notes/cli.py:main` (lines 107–109) — exceptions carry message strings; CLI handler prints to stderr and exits 1
- **Tests**: `TestStorage.test_f02_corrupt_json_raises_storage_error`; all `test_fr006_*` and `test_fr007_*` methods

### NFR-006 — README documentation (setup + all 5 subcommand examples)

- **Code**: `README.md` (lines 1–67) — Python 3.11+ setup, notes.json auto-creation, usage examples for all five subcommands, error handling description, test instructions
- **Tests**: N/A (documentation artifact; verified by manual inspection in verify phase)

---

## Test Evidence

All numbers are drawn from the live `python -m unittest discover -s tests -v` run captured in `artifacts/verify.md`.

**Full suite**: Ran 97 tests in 0.741s — OK (0 failures, 0 errors)

**Notes-specific breakdown** (tests/test_notes.py — 26 tests):

| Class | Tests |
|-------|-------|
| TestCreateNote | 7 |
| TestListNotes | 2 |
| TestGetNote | 2 |
| TestUpdateNote | 6 |
| TestDeleteNote | 3 |
| TestStorage | 4 |
| TestCLIIntegration | 2 |
| **Total** | **26** |

**Compile check**: `python -m compileall -q .` — no output, zero compilation errors.

**Per-requirement results**: FR-001 PASS, FR-002 PASS, FR-003 PASS, FR-004 PASS, FR-005 PASS, FR-006 PASS, FR-007 PASS, NFR-001 PASS, NFR-002 PASS, NFR-003 PASS, NFR-004 PASS, NFR-005 PASS, NFR-006 PASS.

---

## Risks

**R-01 (Minor — accepted)**: No schema validation in `notes/app.py:_load` for structurally-invalid JSON (e.g., a file that is valid JSON but not the expected dict structure). Impact: `StorageError` would not be raised for structural corruption; a `KeyError` or `TypeError` could surface instead. Accepted: the CLI scope is local single-user; structural corruption is extremely unlikely and the existing `StorageError` on `json.JSONDecodeError` covers the common corruption case.

**R-02 (Nit — accepted)**: No `--version` flag in the CLI. No user impact.

**R-03 (Nit — accepted)**: `list` subcommand output is plain text; no formatting options. Acceptable for a single-user CLI.

**R-04 (Nit — accepted)**: `notes.json` path defaults to the current working directory. Acceptable for the local CLI scope; `NOTES_PATH` env var provides override capability for tests and advanced users.

**Security**: No credentials, tokens, or secrets introduced. No network calls. No file permission escalation. Risk level: none for the local CLI scope.

---

## Rollback

All notes package files (`notes/`, `tests/test_notes.py`, `README.md`) were added in this branch and do not exist on `main`. A full rollback is:

```
git revert <merge-commit>
```

Or, if reverting individual commits in reverse task order:

1. Revert T-07 — Remove README.md
2. Revert T-06 — Remove tests/test_notes.py
3. Revert T-05 — Remove CLI integration tests
4. Revert T-04 — Remove notes/cli.py
5. Revert T-03 — Remove notes/app.py
6. Revert T-02 — Remove notes/__init__.py
7. Revert T-01 — Remove notes/ package directory

All pipeline infrastructure changes (agent files, command files, docs) are independent of the Notes CLI and can be reverted separately without affecting core functionality.

No database migrations, external service changes, or persistent side effects exist; a revert leaves the repository in a clean pre-branch state.

---

## Reviewer Checklist

- [ ] All 97 tests pass: `python -m unittest discover -s tests -v` exits 0 with "Ran 97 tests"
- [ ] Compile clean: `python -m compileall -q .` produces no output
- [ ] FR-001 through FR-007 each have at least one passing test in `tests/test_notes.py`
- [ ] NFR-001: atomic write confirmed — `test_f01_atomic_write_no_tmp_file_remains` passes
- [ ] NFR-001: `StorageError` on corrupt JSON confirmed — `test_f02_corrupt_json_raises_storage_error` passes
- [ ] NFR-002: `python -m notes.cli --help` lists exactly five subcommands: create, list, view, update, delete
- [ ] NFR-003: `test_nfr003_id_not_reused_after_delete` passes (ID not reused after delete)
- [ ] NFR-005: CLI prints to stderr and exits 1 for both `NoteNotFoundError` and `ValidationError`
- [ ] NFR-006: README.md documents Python 3.11+ requirement and all five subcommand examples
- [ ] No secrets, credentials, tokens, or `.env` files present in the diff
- [ ] No network calls in application code (`notes/app.py`, `notes/cli.py`)
- [ ] Branch is not `main` or `master`
- [ ] All 8 SDLC phases are APPROVED in `sdlc/state.json`
- [ ] `sdlc/`, `orchestrator.py`, `.claude/hooks/`, `.claude/settings.json` were not hand-edited
