# Implementation Plan

## Overview

This plan delivers the Notes CLI as a three-module Python package (`notes/`) backed by `notes.json`, satisfying FR-001 through FR-007 and NFR-001 through NFR-006. It resolves all six mandatory design-review findings: F-01 (atomic writes), F-02 (StorageError for corrupt JSON), F-03 (CLI integration tests), F-04 (README.md), F-05 (whitespace-only validation), and F-07 (document `python -m notes.cli` as sole invocation).

---

## Ordered Tasks

### T-01 — Exception hierarchy
- **Goal**: Define the complete exception hierarchy (`NoteError`, `NoteNotFoundError`, `ValidationError`, `StorageError`) in `notes/app.py` and re-export all four from `notes/__init__.py`. This unblocks every subsequent task that raises or imports these types.
- **Files**: `notes/__init__.py` (create), `notes/app.py` (create, exception section only)
- **FR/NFR IDs**: FR-006, FR-007, NFR-005; design-review F-02 (StorageError addition)
- **Done-when**: `from notes import NoteError, NoteNotFoundError, ValidationError, StorageError` executes without error; `issubclass(NoteNotFoundError, NoteError)`, `issubclass(ValidationError, NoteError)`, and `issubclass(StorageError, NoteError)` all return `True`; `python -m compileall -q notes/` reports no syntax errors.

---

### T-02 — Storage helpers: `_load` and `_save`
- **Goal**: Implement the two private storage helpers in `notes/app.py`. `_load` must return the default empty-state dict when the file is absent and must catch `json.JSONDecodeError`, re-raising it as `StorageError` with the message `"notes.json is corrupt; delete or repair the file."`. `_save` must write to `<path>.tmp`, call `file.flush()` and `os.fsync()`, then call `os.replace("<path>.tmp", path)` to guarantee atomic replacement (F-01, F-02).
- **Files**: `notes/app.py` (add `_load` and `_save` implementations)
- **FR/NFR IDs**: NFR-001, NFR-005; design-review F-01, F-02
- **Done-when**: A unit test calling `_load` on a non-existent path returns `{"next_id": 1, "notes": []}`; a unit test calling `_load` on a file containing `"{invalid"` raises `StorageError`; a unit test calling `_save` then `_load` round-trips the data correctly; no `.tmp` file remains after `_save` completes; `python -m compileall -q notes/` passes.

---

### T-03 — Application functions: create, list, get, update, delete
- **Goal**: Implement the five public functions in `notes/app.py`: `create_note`, `list_notes`, `get_note`, `update_note`, `delete_note`. Validation in `create_note` and `update_note` must use `if not title.strip()` and `if not content.strip()` — not bare `if not title` — to reject whitespace-only input (F-05). `create_note` assigns `next_id`, increments it, and persists. `delete_note` never decrements `next_id`. `get_note`, `update_note`, and `delete_note` raise `NoteNotFoundError` for an absent ID.
- **Files**: `notes/app.py` (add five public functions)
- **FR/NFR IDs**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, NFR-001, NFR-003, NFR-005; design-review F-05
- **Done-when**: Each function has a complete type-annotated signature; `python -m compileall -q notes/` passes; `list_notes` on an empty store returns `[]`; `create_note` followed by `get_note` with the returned ID returns the same note; `delete_note` does not decrement `next_id`; `create_note("  ", "content", ...)` raises `ValidationError`; `create_note("title", "  ", ...)` raises `ValidationError`.

---

### T-04 — CLI layer: `main()` and five subparsers
- **Goal**: Implement `notes/cli.py` with `main() -> None` as the sole entry point. Build an `argparse.ArgumentParser` with five subparsers (`create`, `list`, `view`, `update`, `delete`). When `list_notes` returns `[]`, print an empty-list indication to stdout (e.g., `"No notes found."`). When `delete_note` succeeds, print a confirmation message to stdout (e.g., `"Note <id> deleted."`). Catch all `NoteError` subclasses, print `str(e)` to `sys.stderr`, and call `sys.exit(1)`. Do not catch `StorageError` separately — it is a `NoteError` subclass and is handled uniformly.
- **Files**: `notes/cli.py` (create)
- **FR/NFR IDs**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, NFR-002, NFR-005
- **Done-when**: `python -m notes.cli --help` lists all five subcommands without error; `python -m notes.cli list` on an empty `notes.json` prints the empty-list indication to stdout; `python -m notes.cli delete --id 999` exits with code 1 and prints an error to stderr; `python -m compileall -q notes/` passes.

---

### T-05 — Unit tests for FR-001 through FR-007
- **Goal**: Write `tests/test_notes.py` with `unittest.TestCase` subclasses that call application functions directly. Each test method creates its own isolated temporary file via `tempfile.NamedTemporaryFile(suffix=".json", delete=False)` and removes it in `tearDown`. Test method names embed the FR/NFR IDs they cover. Cover FR-001 through FR-007 including whitespace-only validation (F-05), ID non-reuse after deletion (NFR-003), atomic write round-trip (F-01/NFR-001), and `StorageError` on corrupt JSON (F-02/NFR-001).
- **Files**: `tests/test_notes.py` (create, unit-test section)
- **FR/NFR IDs**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, NFR-001, NFR-003, NFR-004, NFR-005; design-review F-01, F-02, F-05
- **Done-when**: `python -m unittest discover -s tests -v` runs all unit-test methods with zero failures and zero errors; each FR-001 through FR-007 maps to at least one named test method; no test shares a tempfile with another test.

---

### T-06 — CLI integration tests for FR-002 and FR-005
- **Goal**: Add a `TestCLIIntegration` class to `tests/test_notes.py` with subprocess-based integration tests that invoke `python -m notes.cli` as a child process. Write at minimum: `test_fr002_empty_list_indication` (asserts the empty-list string appears in stdout when no notes exist) and `test_fr005_delete_confirmation` (creates a note, deletes it, asserts the confirmation string appears in stdout). Each integration test uses its own temporary directory passed via `NOTES_PATH` environment variable or a writable temp path. (F-03)
- **Files**: `tests/test_notes.py` (add `TestCLIIntegration` class)
- **FR/NFR IDs**: FR-002, FR-005, NFR-004; design-review F-03
- **Done-when**: `python -m unittest tests.test_notes.TestCLIIntegration -v` passes with zero failures; `test_fr002_empty_list_indication` asserts on stdout content; `test_fr005_delete_confirmation` asserts on stdout content; neither test reads from the default `notes.json` in the working directory.

---

### T-07 — README.md
- **Goal**: Write `README.md` with setup instructions and CLI usage examples for every operation (`create`, `list`, `view`, `update`, `delete`). Document `python -m notes.cli` as the sole supported invocation. Do not add `pyproject.toml` or any packaging configuration. (F-04, F-07)
- **Files**: `README.md` (create)
- **FR/NFR IDs**: NFR-006; design-review F-04, F-07
- **Done-when**: `README.md` exists at the repository root; it contains a setup section, at least one example invocation per subcommand using `python -m notes.cli`, and no reference to `pip install` or `console_scripts`; the file is plain text with no broken Markdown.

---

## File-Level Change List

| File | Action | Key changes |
|------|--------|-------------|
| `notes/__init__.py` | Create | Package marker; re-exports `NoteError`, `NoteNotFoundError`, `ValidationError`, `StorageError` from `notes.app` |
| `notes/app.py` | Create | Exception hierarchy (T-01); `_load` with absent-file default and `json.JSONDecodeError` → `StorageError` (T-02, F-02); `_save` with atomic write via `os.replace` (T-02, F-01); `create_note`, `list_notes`, `get_note`, `update_note`, `delete_note` with `.strip()` validation (T-03, F-05); all functions have full type annotations |
| `notes/cli.py` | Create | `main() -> None`; argparse with five subparsers (`create`, `list`, `view`, `update`, `delete`); empty-list indication on `list` (FR-002); delete confirmation message (FR-005); `NoteError` → stderr + `sys.exit(1)` (T-04) |
| `tests/test_notes.py` | Create | Unit tests for FR-001–FR-007 with per-test `tempfile` isolation (T-05); `TestCLIIntegration` with subprocess-based tests for FR-002 empty-list and FR-005 confirmation (T-06, F-03) |
| `README.md` | Create | Setup instructions; five subcommand usage examples; `python -m notes.cli` as sole invocation; no packaging artifacts (T-07, F-04, F-07) |

---

## Test Plan

| Test class / method name | Requirement(s) | Type | Pass criterion |
|--------------------------|----------------|------|----------------|
| `TestCreateNote.test_fr001_create_returns_note` | FR-001, NFR-003 | Unit | `create_note` returns a dict with `"id"`, `"title"`, `"content"` keys |
| `TestCreateNote.test_fr001_id_auto_increments` | FR-001, NFR-003 | Unit | Two successive creates yield IDs `1` and `2` |
| `TestCreateNote.test_fr001_data_persists_across_load` | FR-001, NFR-001 | Unit | Note created in one call is present after `_load` in a second call to `list_notes` |
| `TestCreateNote.test_fr007_empty_title_raises` | FR-007, NFR-005 | Unit | `create_note("", "content", ...)` raises `ValidationError` |
| `TestCreateNote.test_fr007_whitespace_only_title_raises` | FR-007, NFR-005, F-05 | Unit | `create_note("   ", "content", ...)` raises `ValidationError` |
| `TestCreateNote.test_fr007_empty_content_raises` | FR-007, NFR-005 | Unit | `create_note("title", "", ...)` raises `ValidationError` |
| `TestCreateNote.test_fr007_whitespace_only_content_raises` | FR-007, NFR-005, F-05 | Unit | `create_note("title", "   ", ...)` raises `ValidationError` |
| `TestListNotes.test_fr002_returns_empty_list_when_no_notes` | FR-002 | Unit | `list_notes(...)` on a new tempfile returns `[]` |
| `TestListNotes.test_fr002_returns_all_created_notes` | FR-002 | Unit | After two creates, `list_notes` returns a list of length two |
| `TestGetNote.test_fr003_returns_correct_note` | FR-003 | Unit | `get_note(id, ...)` returns the note with matching `"id"` |
| `TestGetNote.test_fr006_raises_not_found_for_absent_id` | FR-006, NFR-005 | Unit | `get_note(999, ...)` raises `NoteNotFoundError` |
| `TestUpdateNote.test_fr004_replaces_title_and_content` | FR-004 | Unit | After `update_note`, `get_note` returns updated fields |
| `TestUpdateNote.test_fr004_full_replace_both_fields` | FR-004 | Unit | Both `title` and `content` in the stored note match the new values |
| `TestUpdateNote.test_fr007_empty_title_raises` | FR-007, NFR-005 | Unit | `update_note(id, "", "content", ...)` raises `ValidationError` |
| `TestUpdateNote.test_fr007_whitespace_only_title_raises` | FR-007, NFR-005, F-05 | Unit | `update_note(id, "  ", "content", ...)` raises `ValidationError` |
| `TestUpdateNote.test_fr007_empty_content_raises` | FR-007, NFR-005 | Unit | `update_note(id, "title", "", ...)` raises `ValidationError` |
| `TestUpdateNote.test_fr006_raises_not_found_for_absent_id` | FR-006, NFR-005 | Unit | `update_note(999, "t", "c", ...)` raises `NoteNotFoundError` |
| `TestDeleteNote.test_fr005_removes_note_from_storage` | FR-005 | Unit | After `delete_note(id, ...)`, `get_note(id, ...)` raises `NoteNotFoundError` |
| `TestDeleteNote.test_fr006_raises_not_found_for_absent_id` | FR-006, NFR-005 | Unit | `delete_note(999, ...)` raises `NoteNotFoundError` |
| `TestDeleteNote.test_nfr003_id_not_reused_after_delete` | NFR-003 | Unit | Create note (id=1), delete it, create again → new note has id=2 |
| `TestStorage.test_nfr001_absent_file_returns_default` | NFR-001 | Unit | `_load` on a non-existent path returns `{"next_id": 1, "notes": []}` |
| `TestStorage.test_nfr001_data_survives_process_reload` | NFR-001 | Unit | Data written by `_save` is fully recovered by a subsequent `_load` call |
| `TestStorage.test_f02_corrupt_json_raises_storage_error` | NFR-001, NFR-005, F-02 | Unit | `_load` on a file containing `"{invalid"` raises `StorageError` with message containing `"corrupt"` |
| `TestStorage.test_f01_atomic_write_no_tmp_file_remains` | NFR-001, F-01 | Unit | After `_save` returns, no `<path>.tmp` file exists on disk |
| `TestCLIIntegration.test_fr002_empty_list_indication` | FR-002, NFR-004, F-03 | CLI integration (subprocess) | `python -m notes.cli list` on an empty store exits 0 and stdout contains the empty-list indicator string |
| `TestCLIIntegration.test_fr005_delete_confirmation` | FR-005, NFR-004, F-03 | CLI integration (subprocess) | After creating a note, `python -m notes.cli delete --id 1` exits 0 and stdout contains a confirmation string referencing the deleted ID |

Manual verification command (run after all unit tests pass):

```
python -m unittest discover -s tests -v
python -m compileall -q .
```

---

## Rollback Notes

All rollback uses `git revert` only. No force pushes, history rewrites, or `--no-verify` flags are permitted.

- **T-01 (exception hierarchy)**: `git revert <commit-sha-for-T-01>` removes `notes/__init__.py` and the exception-class definitions from `notes/app.py`. No downstream state is affected because no data file exists yet.
- **T-02 (storage helpers)**: `git revert <commit-sha-for-T-02>` removes `_load` and `_save` from `notes/app.py`. Any `notes.json` files created during local testing must be removed manually from the working directory (`del notes.json` on Windows, `rm notes.json` on POSIX). The `.tmp` sentinel file will not exist after a clean `_save`, but check for `notes.json.tmp` and remove if present.
- **T-03 (application functions)**: `git revert <commit-sha-for-T-03>` removes the five public functions from `notes/app.py`. No persistent side effects beyond `notes.json` (handled in T-02 rollback).
- **T-04 (CLI layer)**: `git revert <commit-sha-for-T-04>` removes `notes/cli.py`. No persistent side effects.
- **T-05 (unit tests)**: `git revert <commit-sha-for-T-05>` removes the unit-test class(es) from `tests/test_notes.py`. Temporary files created by tests are cleaned up by each test's `tearDown`; any orphaned tempfiles can be deleted from the OS temp directory.
- **T-06 (CLI integration tests)**: `git revert <commit-sha-for-T-06>` removes `TestCLIIntegration` from `tests/test_notes.py`. Integration tests write to temporary directories; clean up any orphaned temp directories created under `%TEMP%` or `/tmp`.
- **T-07 (README.md)**: `git revert <commit-sha-for-T-07>` removes `README.md`. No side effects.

If multiple tasks were committed together, use `git revert <sha1> <sha2> ...` to revert each commit individually in reverse order (most recent first), resolving any conflicts that arise before proceeding.
