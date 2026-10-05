# Implementation Plan

## Ordered tasks

### T-01 - Define task model and validated JSON storage

- **Goal:** Implement `Task`, the `TodoError` hierarchy, and the storage boundary in `todo/app.py`. Validate schema, field types, unique IDs, and that `next_id` is a positive integer greater than every stored ID. Treat inconsistent ID state as corrupt storage and leave its bytes unchanged. Implement UTF-8/two-space JSON and same-directory atomic replacement with flush, fsync, mode preservation, and temporary-file cleanup.
- **Files touched:** `todo/__init__.py`, `todo/app.py`, `tests/test_todo.py`.
- **FR/NFR IDs:** FR-020, FR-021, FR-022, FR-023, FR-024; NFR-001, NFR-002, NFR-003, NFR-004, NFR-005, NFR-006.
- **Done when:** Missing/empty files load as an empty list; invalid JSON/schema/duplicate IDs/inconsistent `next_id` raise `CorruptStorageError` without changing bytes; other I/O failures raise `StorageError`; successful saves meet NFR-003; focused unittests pass.

### T-02 - Implement task operations and transitions

- **Goal:** Implement add, list, complete, reopen, and delete operations in `TodoApp`. Enforce blank-title rejection, edge trimming, interior whitespace preservation, duplicate-title acceptance, monotonic IDs, not-found behavior, and no writes for no-op/failure cases.
- **Files touched:** `todo/app.py`, `tests/test_todo.py`.
- **FR/NFR IDs:** FR-002, FR-003, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013, FR-016, FR-017, FR-018, FR-019, FR-024; NFR-004, NFR-006.
- **Done when:** Each operation returns deterministic domain results/errors, task order remains creation order, IDs are not reused after deletion, and tests compare file bytes for no-op/error paths.

### T-03 - Implement the injectable CLI adapter

- **Goal:** Implement `main(argv, stdout, stderr, app) -> int` in `todo/cli.py`. Parse the five commands, format specified messages and exit codes, keep app logic free of printing/argv access, and preserve stored titles while escaping line breaks and terminal control characters in rendered output. This rendering choice follows the human's 2026-10-05 selection for F-02.
- **Files touched:** `todo/cli.py`, `tests/test_todo.py`.
- **FR/NFR IDs:** FR-001, FR-002, FR-004, FR-005, FR-006, FR-008, FR-010, FR-012, FR-013, FR-014, FR-015, FR-017; NFR-001, NFR-005, NFR-006.
- **Done when:** CLI tests verify exact stdout/stderr and return values for all commands, including usage/errors and escaped display of control characters, without modifying stored title text.

### T-04 - Complete requirement-tagged regression coverage

- **Goal:** Complete integration coverage for every FR and NFR in the single implementation test file, using `unittest` and temporary directories only. Do not weaken tests to make implementation pass.
- **Files touched:** `tests/test_todo.py`.
- **FR/NFR IDs:** FR-001 through FR-024; NFR-001 through NFR-006.
- **Done when:** Every requirement ID appears in at least one test name or test comment; full `python -m unittest discover -s tests -v` passes; `python -m compileall -q .` exits 0.

## File-level change list

| File | Planned responsibility |
|---|---|
| `todo/__init__.py` | Non-empty package docstring. |
| `todo/app.py` | Task model, typed error hierarchy, domain operations, schema validation, storage reads, and atomic saves. |
| `todo/cli.py` | Injectable command parsing, presentation escaping, stdout/stderr formatting, and integer exit results. |
| `tests/test_todo.py` | FR/NFR-tagged unit and integration tests using temporary directories. |

No other implementation file is planned; this matches the ownership manifest.

## Test plan

| ID | Named check |
|---|---|
| FR-001 | `test_cli_commands_and_usage` |
| FR-002 | `test_add_returns_created_task` |
| FR-003 | `test_new_task_starts_open` |
| FR-004 | `test_cli_add_output` |
| FR-005 | `test_list_preserves_creation_order` |
| FR-006 | `test_list_empty_message` |
| FR-007 | `test_complete_open_task` |
| FR-008 | `test_complete_done_noop_preserves_bytes` |
| FR-009 | `test_reopen_done_task` |
| FR-010 | `test_reopen_open_noop_preserves_bytes` |
| FR-011 | `test_delete_removes_task` |
| FR-012 | `test_missing_task_error_and_unchanged_storage` |
| FR-013 | `test_invalid_ids_are_not_found` |
| FR-014 | `test_usage_error_returns_two` |
| FR-015 | `test_operation_errors_use_stderr_and_error_exit` |
| FR-016 | `test_blank_title_rejected_without_write` |
| FR-017 | `test_title_trim_and_display_escape` |
| FR-018 | `test_duplicate_titles_get_distinct_ids` |
| FR-019 | `test_long_title_and_many_tasks_have_no_product_limit` |
| FR-020 | `test_storage_schema_and_current_directory` |
| FR-021 | `test_missing_and_empty_storage` |
| FR-022 | `test_corrupt_storage_and_inconsistent_next_id_preserve_bytes` |
| FR-023 | `test_storage_io_failure_raises_storage_error` |
| FR-024 | `test_ids_increase_and_are_not_reused_after_delete` |
| NFR-001 | Manual: `python --version`; static check that runtime imports are standard-library only; `python -m compileall -q .`. |
| NFR-002 | `test_json_encoding_and_indentation`. |
| NFR-003 | `test_atomic_save_mode_and_temp_cleanup`. |
| NFR-004 | `test_read_noop_error_paths_preserve_bytes`. |
| NFR-005 | Manual code review: verify no network APIs or secret handling; supported by `test_cli_operations_are_local`. |
| NFR-006 | `python -m unittest discover -s tests -v`; each FR test uses a temporary directory and cites its ID. |

All stateful tests use `tempfile.TemporaryDirectory`; none writes `tasks.json` into the real repository working directory.

## Rollback notes

If the implementation needs to be rolled back after commit, use `git revert <implementation-commit>` only. Do not reset, rewrite history, or manually restore files from an unrelated revision.