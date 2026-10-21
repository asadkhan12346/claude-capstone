# Code Review

## Summary

Implementation of the Todo CLI application (US-001) across four files (`todo/__init__.py`,
`todo/app.py`, `todo/cli.py`, `tests/test_todo.py`) was reviewed against 18 FRs, 4 NFRs, and
6 design-review findings (F-01 through F-06).

**Compilation:** `python -m compileall -q .` — completed with no output (no errors).

**Test run:** `python -m unittest discover -s tests -v` — **131 tests ran, 0 failures, 0 errors**.

The overall design is sound, all requirement IDs are implemented, all design-review findings are
resolved in code, and the test suite is comprehensive. Two findings are raised: one Minor and one
Nit. Neither blocks functionality, but the Minor finding creates a gap in the error-handling
contract under an uncommon filesystem condition.

---

## Findings

### R-01 — Minor | `mkdir` OSError escapes the StorageError contract

**File:** `todo/app.py:65`

```python
path.parent.mkdir(parents=True, exist_ok=True)   # line 65 — outside the try block
tmp_path = pathlib.Path(str(path) + ".tmp")
try:
    ...
except OSError as exc:
    ...
    raise StorageError(str(exc)) from exc
```

The `path.parent.mkdir(...)` call sits outside the `try/except OSError` block. If it raises
`OSError` (e.g., a custom `--storage` path whose parent directory cannot be created due to
permission errors), the raw `OSError` propagates through every caller's
`except StorageError` clause uncaught, producing an unhandled Python traceback instead of the
clean `{"success": False, "message": "..."}` result mandated by FR-018 and the architecture's
error-handling table row "Unexpected I/O error (permissions, disk full) → exit 1 via CLI".

The default storage path (`~/.todo.json`) is unaffected because `Path.home()` always exists.
The bug only surfaces when a user passes `--storage /nonexistent/dir/todo.json`.

**Fix (not implemented by this review):** Move `path.parent.mkdir(...)` inside the
`try` block.

---

### R-02 — Nit | Unreachable `else` branch in dispatch block

**File:** `todo/cli.py:115-117`

```python
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
```

Because `subparsers` is created with `required=True` (line 44) and argparse enforces that
`args.command` is always one of the six registered sub-command names, this `else` branch can
never be reached at runtime. Argparse raises `SystemExit(2)` before `parse_args()` returns for
any unrecognised command. The code is benign dead code.

---

## Traceability matrix

| Req ID | Implementation reference | Test method(s) |
|---|---|---|
| FR-001 | `app.py:81-119` `create_task()` — strips title, assigns id, status=pending, appends | `TestCreateTask.test_fr001_create_basic`, `test_fr001_title_trimmed`, `test_fr001_internal_whitespace_preserved` |
| FR-002 | `app.py:84` `description: str = ""` default | `TestCreateTask.test_fr002_description_defaults_empty`, `test_fr002_description_provided` |
| FR-003 | `app.py:137` `list(data["tasks"])` — preserves append order | `TestListTasks.test_fr003_all_tasks_in_creation_order` |
| FR-004 | `app.py:142-143` empty-tasks early return with "No tasks found." | `TestListTasks.test_fr004_empty_list_message`, `test_fr004_existing_empty_storage` |
| FR-005 | `app.py:139-140` in-memory filter by `status_filter` | `TestListTasks.test_fr005_filter_by_completed`, `test_fr005_filter_by_pending`, `test_fr005_filter_no_match` |
| FR-006 | `app.py:152-196` `update_task()` — updates title/description only, leaves id/status | `TestUpdateTask.test_fr006_update_title_only`, `test_fr006_update_description_only`, `test_fr006_update_both_fields`, `test_fr006_title_trimmed_on_update`, `test_fr006_status_not_changed_by_update` |
| FR-007 | `app.py:199-223` `delete_task()` — list comprehension removes task | `TestDeleteTask.test_fr007_delete_removes_task`, `test_fr007_task_absent_from_subsequent_list`, `test_fr007_next_id_not_decremented` |
| FR-008 | `app.py:254-255` `task["status"] = "completed"` then save | `TestMarkCompleted.test_fr008_pending_becomes_completed` |
| FR-009 | `app.py:247-252` already-completed guard, no save, `already_set=True` | `TestMarkCompleted.test_fr009_already_completed_noop` |
| FR-010 | `app.py:290-291` `task["status"] = "pending"` then save | `TestMarkPending.test_fr010_completed_becomes_pending` |
| FR-011 | `app.py:283-288` already-pending guard, no save, `already_set=True` | `TestMarkPending.test_fr011_already_pending_noop` |
| FR-012 | `app.py:185,215,244,280` — task-not-found early return in each write operation | `TestUpdateTask.test_fr012_update_not_found`, `TestDeleteTask.test_fr012_delete_not_found`, `TestMarkCompleted.test_fr012_mark_completed_not_found`, `TestMarkPending.test_fr012_mark_pending_not_found` |
| FR-013 | `app.py:97-98` (create), `app.py:173-177` (update) — strip then reject empty | `TestCreateTask.test_fr013_empty_title_rejected`, `test_fr013_whitespace_title_rejected`, `TestUpdateTask.test_fr013_update_empty_title_rejected`, `test_fr013_update_whitespace_title_rejected` |
| FR-014 | `app.py:138` (no uniqueness check) | `TestCreateTask.test_fr014_duplicate_titles_allowed` |
| FR-015 | `app.py:102,110` — `next_id` read, used, incremented; not decremented on delete | `TestCreateTask.test_fr015_ids_auto_increment`, `test_fr015_id_not_reused_after_delete`, `test_fr015_next_id_persists_across_restarts`, `TestDeleteTask.test_fr007_next_id_not_decremented` |
| FR-016 | `app.py:23-73` `load()`/`save()` — all reads/writes go through these | `TestStorageLoad.test_valid_json_returns_data`, `TestStorageSave.test_save_creates_file` |
| FR-017 | `app.py:38-39,43-44` — `FileNotFoundError` and empty-content both return default dict | `TestStorageLoad.test_missing_file_returns_default`, `test_empty_file_returns_default`, `test_whitespace_only_file_returns_default` |
| FR-018 | `app.py` — every function returns `{"message": str, ...}`; `cli.py:119-139` always prints | `TestMessages.test_fr018_every_operation_returns_nonempty_message`, `TestCLIIntegration.*` |
| NFR-001 | Imports: `json`, `os`, `pathlib`, `argparse`, `sys`, `typing`, `tempfile`, `unittest` — all stdlib | `TestCLIIntegration.test_f01_invocation_python_m_todo_cli` (no import errors) |
| NFR-002 | `app.py:37,68` — `encoding="utf-8"` on `read_text()` and `open()`; `ensure_ascii=False` on `json.dump()` | `TestStorageSave.test_save_utf8_encoding`, `TestNFR002UTF8.test_nfr002_non_ascii_title_preserved`, `test_nfr002_non_ascii_description_preserved` |
| NFR-003 | No `urllib`, `http`, `socket`, `requests`, or credential fields anywhere in codebase | Confirmed by code inspection; `python -m compileall` clean |
| NFR-004 | `app.py` path-injectable functions; `tests/test_todo.py` uses `tempfile.TemporaryDirectory`; all test names cite FR/NFR IDs | All 57 `test_todo` tests; `TestCLIIntegration.test_f01_invocation_python_m_todo_cli` |

---

## Plan adherence

| Task | Status | Notes |
|---|---|---|
| T-01: `todo/__init__.py` — re-exports public API | Done | `__init__.py:8-16` re-exports all 7 symbols; `__all__` declared |
| T-02: `StorageError`, `load()`, `save()` | Done | F-02 resolved via `os.replace()`; F-04 resolved via `StorageError` raise; see R-01 (Minor) for `mkdir` placement |
| T-03: `create_task()` | Done | All spec steps implemented; signature matches plan |
| T-04: `list_tasks()` | Done | F-06 resolved; return shape includes `"tasks": list[dict]` |
| T-05: `update_task()` | Done | F-03 resolved; `None` sentinel; empty-string description accepted |
| T-06: `delete_task()` | Done | `next_id` not decremented; confirmed by test |
| T-07: `mark_completed()` | Done | Idempotent guard with `already_set=True`; no save on no-op |
| T-08: `mark_pending()` | Done | Idempotent guard with `already_set=True`; no save on no-op |
| T-09: `main()` in `todo/cli.py` | Done | F-01 resolved (invocation `python -m todo.cli`); F-05 resolved (`DEFAULT_STORAGE_PATH = Path.home() / ".todo.json"`); all 6 sub-commands present; stdout/stderr routing correct; exit codes correct |
| T-10: `tests/test_todo.py` | Done | All 11 required test classes present; 57 todo-specific tests; all pass |

### Design-review finding resolution

| Finding | Severity | Resolved in code | Evidence |
|---|---|---|---|
| F-01 — `python -m todo.cli` invocation | High | Yes | `cli.py:7` docstring; `TestCLIIntegration.test_f01_invocation_python_m_todo_cli` passes |
| F-02 — Atomic write via temp + `os.replace()` | Medium | Yes | `app.py:66-70`; `TestStorageSave.test_save_no_tmp_file_remains` passes |
| F-03 — `update_task()` `None` sentinel | Medium | Yes | `app.py:152-157`; `TestUpdateTask.test_f03_*` all pass |
| F-04 — `load()` raises `StorageError` on malformed JSON | Medium | Yes | `app.py:48-51`; `TestStorageLoad.test_malformed_json_raises_storage_error` passes |
| F-05 — Default storage path `~/.todo.json` | Medium | Yes | `cli.py:24`; `TestCLIIntegration.test_cli_default_storage_is_home` passes |
| F-06 — `list_tasks()` return shape has `"tasks"` key | Low | Yes | `app.py:144-148`; `TestListTasks.test_f06_return_shape_has_tasks_key` passes |

---

Verdict: APPROVE
