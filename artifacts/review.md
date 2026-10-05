# Code Review

## Summary

Reviewed the approved implementation against requirements FR-001 through FR-024, NFR-001 through NFR-006, the architecture, design-review decisions F-01/F-02, and plan tasks T-01 through T-04. The `next_id` consistency check and safe title rendering for control, bidi, line, and paragraph separators are implemented. No actionable defects were found in the reviewed scope.

Verification evidence: `python -m unittest discover -s tests -v` completed with 78 tests and `OK` (exit code 0). `python -m compileall -q .` completed with no output (exit code 0).

## Findings

| ID | Severity | Location | Finding | Related IDs |
|---|---|---|---|---|
| None | - | - | No actionable findings. | - |

## Traceability matrix

| ID | Code | Test/evidence |
|---|---|---|
| FR-001 | `todo/cli.py:main` | `test_cli_commands_and_usage` |
| FR-002 | `todo/app.py:TodoApp.add_task` | `test_add_returns_created_task` |
| FR-003 | `todo/app.py:TodoApp.add_task` | `test_new_task_starts_open` |
| FR-004 | `todo/cli.py:main` add branch | `test_cli_add_output` |
| FR-005 | `todo/app.py:TodoApp.list_tasks`, `todo/cli.py:main` list branch | `test_list_preserves_creation_order`, `test_cli_list_preserves_creation_order` |
| FR-006 | `todo/cli.py:main` list branch | `test_list_empty_message` |
| FR-007 | `todo/app.py:TodoApp.complete_task` | `test_complete_open_task` |
| FR-008 | `todo/app.py:TodoApp.complete_task`, `todo/cli.py:main` done branch | `test_complete_done_noop_preserves_bytes`, `test_complete_done_cli_noop_message` |
| FR-009 | `todo/app.py:TodoApp.reopen_task` | `test_reopen_done_task` |
| FR-010 | `todo/app.py:TodoApp.reopen_task`, `todo/cli.py:main` reopen branch | `test_reopen_open_noop_preserves_bytes`, `test_reopen_open_cli_noop_message` |
| FR-011 | `todo/app.py:TodoApp.delete_task` | `test_delete_removes_task` |
| FR-012 | `todo/app.py:TaskNotFoundError`, `todo/cli.py:main` | `test_missing_task_error_and_unchanged_storage`, `test_missing_task_cli_error_and_exit` |
| FR-013 | `todo/app.py:TodoApp._task_id`, `todo/cli.py:main` | `test_invalid_ids_are_not_found`, `test_extremely_long_numeric_id_is_not_found`, `test_invalid_task_id_cli_error_and_exit` |
| FR-014 | `todo/cli.py:main`, `USAGE` | `test_usage_error_returns_two` |
| FR-015 | `todo/cli.py:main` error branches | `test_operation_errors_use_stderr_and_error_exit` |
| FR-016 | `todo/app.py:TodoApp._task_title` | `test_blank_title_rejected_without_write` |
| FR-017 | `todo/app.py:TodoApp._task_title`, `todo/cli.py:_display_title` | `test_title_trim_and_interior_whitespace`, `test_title_trim_and_display_escape` |
| FR-018 | `todo/app.py:TodoApp.add_task` | `test_duplicate_titles_get_distinct_ids` |
| FR-019 | `todo/app.py:TodoApp.add_task` | `test_long_title_and_many_tasks_have_no_product_limit` |
| FR-020 | `todo/app.py:TodoApp._load_state`, `TodoApp._save_state` | `test_storage_schema_and_current_directory` |
| FR-021 | `todo/app.py:TodoApp._load_state` | `test_missing_and_empty_storage` |
| FR-022 | `todo/app.py:TodoApp._validate_payload` | `test_corrupt_storage_and_inconsistent_next_id_preserve_bytes` |
| FR-023 | `todo/app.py:TodoApp._load_state`, `TodoApp._save_state` | `test_storage_io_failure_raises_storage_error` |
| FR-024 | `todo/app.py:TodoApp._validate_payload`, `TodoApp.add_task` | `test_ids_increase_and_are_not_reused_after_delete` |
| NFR-001 | Python 3.11+ syntax and standard-library-only imports | `python -m compileall -q .`; source inspection |
| NFR-002 | `todo/app.py:TodoApp._save_state` | `test_json_encoding_and_indentation` |
| NFR-003 | `todo/app.py:TodoApp._save_state` | `test_atomic_save_mode_and_temp_cleanup`, `test_existing_file_mode_is_preserved`; source inspection confirms flush/fsync |
| NFR-004 | Task operations and `_save_state` call boundaries | `test_read_noop_error_paths_preserve_bytes`, `test_complete_done_noop_preserves_bytes`, `test_reopen_open_noop_preserves_bytes` |
| NFR-005 | Application imports and local storage flow | `test_cli_operations_are_local`; source inspection |
| NFR-006 | `tests/test_todo.py` uses `unittest` and temporary directories | Full unittest suite: 78 tests, `OK` |

## Plan adherence

| Task | Result | Evidence |
|---|---|---|
| T-01 | Done | `todo/app.py` validates schema and `next_id`, distinguishes corrupt storage and I/O errors, and performs atomic writes; storage tests cover these paths. |
| T-02 | Done | `TodoApp` implements add/list/complete/reopen/delete, trimming, status transitions, monotonic IDs, and byte-preserving no-op/error behavior; operation tests cover the cases. |
| T-03 | Done | `todo/cli.py` provides the injectable `main`, command forms, messages/exit codes, and escaped title rendering; CLI tests cover these behaviors. |
| T-04 | Done | `tests/test_todo.py` contains requirement-tagged tests using temporary directories; full unittest discovery passed. |

No deviations from the approved plan were observed. Changes remain within the four implementation-owned files.

Verdict: APPROVE