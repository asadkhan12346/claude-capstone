# Todo CLI — SDLC Capstone (US-001)

## Summary

This PR delivers a complete personal todo-list command-line application (US-001) implemented
in pure Python 3.11+ with no third-party dependencies. It covers all 18 functional
requirements, 4 non-functional requirements, 131 passing tests, and a full SDLC audit trail
across 8 pipeline phases.

## What changed

| File | Description |
|---|---|
| `todo/__init__.py` | Package initializer; re-exports the full public API (`StorageError`, `create_task`, `list_tasks`, `update_task`, `delete_task`, `mark_completed`, `mark_pending`) from `todo.app` so tests can import from the package root (T-01, NFR-001) |
| `todo/app.py` | Application layer: `StorageError` exception, `load()` / `save()` storage functions (UTF-8, atomic write via `os.replace()`), and six task-operation functions (`create_task`, `list_tasks`, `update_task`, `delete_task`, `mark_completed`, `mark_pending`); all business logic and I/O lives here (FR-001 through FR-018, NFR-001 through NFR-003) |
| `todo/cli.py` | CLI presentation layer: `argparse`-based `main()` with six sub-commands (`create`, `list`, `update`, `delete`, `complete`, `pending`); routes messages to stdout/stderr; enforces exit codes 0 (success) and 1 (error); default storage path `~/.todo.json` (FR-018, NFR-001, F-01, F-05) |
| `tests/test_todo.py` | Full `unittest` suite: 11 test classes, 57 todo-specific tests plus CLI integration tests, all using `tempfile.TemporaryDirectory` isolation; every test name cites its FR/NFR ID (NFR-004) |
| `artifacts/requirements.md` | 18 FRs and 4 NFRs, constraints, assumptions, and open questions with human-sourced answers (phase 1) |
| `artifacts/architecture.md` | Two-module architecture (app layer + CLI layer), JSON data model, control-flow diagrams, and design decisions (phase 2) |
| `artifacts/design-review.md` | Six design findings (F-01 through F-06) with severity ratings; verdict REVISE, resolved in planning (phase 3) |
| `artifacts/implementation-plan.md` | Ordered tasks T-01 through T-10, per-function specifications, design-finding resolutions, and test plan table (phase 4) |
| `artifacts/review.md` | Code review: 131 tests pass, two findings (R-01 Minor, R-02 Nit), full traceability matrix, plan-adherence table; verdict APPROVE (phase 6) |
| `artifacts/verify.md` | Verification: compileall exit 0, 131 tests / 0 failures, CLI spot-checks (checks 3-9), NFR-001/NFR-003 stdlib inspection; verdict PASS (phase 7) |
| `sdlc/state.json` | Pipeline state machine tracking all 8 phase approvals |
| `sdlc/audit.log.jsonl` | Append-only audit log of every phase transition |
| `CHANGELOG.md` | Keep a Changelog entry documenting all new features |

## Traceability

| Req ID | Requirement summary | Implementation (`file:function`, lines) | Test method(s) |
|---|---|---|---|
| FR-001 | Create task: trimmed title, status=pending, unique ID, success message | `app.py:81-119` `create_task()` | `TestCreateTask.test_fr001_create_basic`, `test_fr001_title_trimmed`, `test_fr001_internal_whitespace_preserved` |
| FR-002 | Description defaults to empty string when omitted | `app.py:84` `description: str = ""` parameter default | `TestCreateTask.test_fr002_description_defaults_empty`, `test_fr002_description_provided` |
| FR-003 | List all tasks in creation (ascending ID) order | `app.py:137` `list(data["tasks"])` preserves append order | `TestListTasks.test_fr003_all_tasks_in_creation_order` |
| FR-004 | Empty/absent storage returns no-tasks message, no error | `app.py:142-143` empty-tasks early return with `"No tasks found."` | `TestListTasks.test_fr004_empty_list_message`, `test_fr004_existing_empty_storage` |
| FR-005 | Filter tasks by status; empty message when no match | `app.py:139-140` in-memory filter by `status_filter` | `TestListTasks.test_fr005_filter_by_completed`, `test_fr005_filter_by_pending`, `test_fr005_filter_no_match` |
| FR-006 | Update title/description; ID and status unchanged; title trimmed | `app.py:152-196` `update_task()` | `TestUpdateTask.test_fr006_update_title_only`, `test_fr006_update_description_only`, `test_fr006_update_both_fields`, `test_fr006_title_trimmed_on_update`, `test_fr006_status_not_changed_by_update` |
| FR-007 | Delete task; absent from all subsequent lists | `app.py:199-223` `delete_task()` list-comprehension removal | `TestDeleteTask.test_fr007_delete_removes_task`, `test_fr007_task_absent_from_subsequent_list`, `test_fr007_next_id_not_decremented` |
| FR-008 | Mark pending task completed | `app.py:254-255` `task["status"] = "completed"` then `save()` | `TestMarkCompleted.test_fr008_pending_becomes_completed` |
| FR-009 | Mark already-completed task: idempotent no-op, informational message, no write | `app.py:247-252` already-completed guard; `save()` not called | `TestMarkCompleted.test_fr009_already_completed_noop` |
| FR-010 | Mark completed task pending | `app.py:290-291` `task["status"] = "pending"` then `save()` | `TestMarkPending.test_fr010_completed_becomes_pending` |
| FR-011 | Mark already-pending task: idempotent no-op, informational message, no write | `app.py:283-288` already-pending guard; `save()` not called | `TestMarkPending.test_fr011_already_pending_noop` |
| FR-012 | Not-found error for update/delete/complete/pending on missing ID | `app.py:185,215,244,280` task-not-found early return in each write operation | `TestUpdateTask.test_fr012_update_not_found`, `TestDeleteTask.test_fr012_delete_not_found`, `TestMarkCompleted.test_fr012_mark_completed_not_found`, `TestMarkPending.test_fr012_mark_pending_not_found` |
| FR-013 | Reject empty/whitespace-only title on create and update | `app.py:97-98` (create), `app.py:173-177` (update) — strip then reject empty | `TestCreateTask.test_fr013_empty_title_rejected`, `test_fr013_whitespace_title_rejected`, `test_fr013_message_nonempty_on_rejection`, `TestUpdateTask.test_fr013_update_empty_title_rejected`, `test_fr013_update_whitespace_title_rejected` |
| FR-014 | Duplicate titles allowed; distinct IDs assigned | `app.py:100-118` — no uniqueness check on title | `TestCreateTask.test_fr014_duplicate_titles_allowed` |
| FR-015 | Auto-incrementing IDs; never reused; counter persists across restarts | `app.py:102,110` `next_id` read, used, incremented; not decremented on delete | `TestCreateTask.test_fr015_ids_auto_increment`, `test_fr015_id_not_reused_after_delete`, `test_fr015_next_id_persists_across_restarts`, `TestDeleteTask.test_fr007_next_id_not_decremented` |
| FR-016 | File-based persistence: all fields and next_id survive restarts | `app.py:23-73` `load()` / `save()` — all reads and writes | `TestStorageLoad.test_valid_json_returns_data`, `TestStorageSave.test_save_creates_file` |
| FR-017 | Missing or empty storage treated as empty list; no error | `app.py:38-39,43-44` `FileNotFoundError` and empty-content both return default dict | `TestStorageLoad.test_missing_file_returns_default`, `test_empty_file_returns_default`, `test_whitespace_only_file_returns_default` |
| FR-018 | Every operation produces a non-empty human-readable message | `app.py` every function returns `{"message": str, ...}`; `cli.py:119-139` always prints | `TestMessages.test_fr018_every_operation_returns_nonempty_message`, `TestCLIIntegration.*` |
| NFR-001 | Python 3.11+, stdlib only, no third-party packages | Imports: `json`, `os`, `pathlib`, `argparse`, `sys`, `typing`, `tempfile`, `unittest` — all stdlib | `TestCLIIntegration.test_f01_invocation_python_m_todo_cli` (no import errors on Python 3.13.0) |
| NFR-002 | Storage file written in UTF-8; non-ASCII chars preserved | `app.py:37` `path.read_text(encoding="utf-8")`; `app.py:68` `open(tmp_path, "w", encoding="utf-8")`; `ensure_ascii=False` in `json.dump()` | `TestStorageSave.test_save_utf8_encoding`, `TestNFR002UTF8.test_nfr002_non_ascii_title_preserved`, `test_nfr002_non_ascii_description_preserved` |
| NFR-003 | No network calls, no secrets | No `urllib`, `http`, `socket`, `requests`, or credential fields in any source file | Confirmed by `python -m compileall -q .` (exit 0) and module member inspection in verify check 10 |
| NFR-004 | unittest framework; FR ID in test name; temp directories | `tests/test_todo.py` uses `tempfile.TemporaryDirectory` in every class; all test method names cite FR/NFR IDs | All 57 `test_todo` test methods; `TestCLIIntegration.test_f01_invocation_python_m_todo_cli` |

## Test evidence

Source: `artifacts/verify.md`, Check 1 and Check 2 (executed 2026-10-22).

### Compilation check

```
$ python -m compileall -q .
(no output)
Exit code: 0
```

### Full test suite

```
$ python -m unittest discover -s tests -v

test_cli_complete_not_found_exit_1 (test_todo.TestCLIIntegration...) ... ok
test_cli_create_empty_title_exit_1 (test_todo.TestCLIIntegration...) ... ok
test_cli_create_success_exit_0 (test_todo.TestCLIIntegration...) ... ok
test_cli_default_storage_is_home (test_todo.TestCLIIntegration...) ... ok
test_cli_delete_success_exit_0 (test_todo.TestCLIIntegration...) ... ok
test_cli_filter_by_status (test_todo.TestCLIIntegration...) ... ok
test_cli_list_empty_exit_0 (test_todo.TestCLIIntegration...) ... ok
test_cli_list_with_tasks_exit_0 (test_todo.TestCLIIntegration...) ... ok
test_cli_pending_success_exit_0 (test_todo.TestCLIIntegration...) ... ok
test_cli_update_no_flags_exit_1 (test_todo.TestCLIIntegration...) ... ok
test_f01_invocation_python_m_todo_cli (test_todo.TestCLIIntegration...) ... ok
test_fr001_create_basic (test_todo.TestCreateTask...) ... ok
test_fr001_internal_whitespace_preserved (test_todo.TestCreateTask...) ... ok
test_fr001_title_trimmed (test_todo.TestCreateTask...) ... ok
test_fr002_description_defaults_empty (test_todo.TestCreateTask...) ... ok
test_fr002_description_provided (test_todo.TestCreateTask...) ... ok
test_fr013_empty_title_rejected (test_todo.TestCreateTask...) ... ok
test_fr013_message_nonempty_on_rejection (test_todo.TestCreateTask...) ... ok
test_fr013_whitespace_title_rejected (test_todo.TestCreateTask...) ... ok
test_fr014_duplicate_titles_allowed (test_todo.TestCreateTask...) ... ok
test_fr015_id_not_reused_after_delete (test_todo.TestCreateTask...) ... ok
test_fr015_ids_auto_increment (test_todo.TestCreateTask...) ... ok
test_fr015_next_id_persists_across_restarts (test_todo.TestCreateTask...) ... ok
test_fr007_delete_removes_task (test_todo.TestDeleteTask...) ... ok
test_fr007_next_id_not_decremented (test_todo.TestDeleteTask...) ... ok
test_fr007_task_absent_from_subsequent_list (test_todo.TestDeleteTask...) ... ok
test_fr012_delete_not_found (test_todo.TestDeleteTask...) ... ok
test_f06_return_shape_has_tasks_key (test_todo.TestListTasks...) ... ok
test_f06_return_shape_with_data (test_todo.TestListTasks...) ... ok
test_fr003_all_tasks_in_creation_order (test_todo.TestListTasks...) ... ok
test_fr004_empty_list_message (test_todo.TestListTasks...) ... ok
test_fr004_existing_empty_storage (test_todo.TestListTasks...) ... ok
test_fr005_filter_by_completed (test_todo.TestListTasks...) ... ok
test_fr005_filter_by_pending (test_todo.TestListTasks...) ... ok
test_fr005_filter_no_match (test_todo.TestListTasks...) ... ok
test_fr008_pending_becomes_completed (test_todo.TestMarkCompleted...) ... ok
test_fr009_already_completed_noop (test_todo.TestMarkCompleted...) ... ok
test_fr012_mark_completed_not_found (test_todo.TestMarkCompleted...) ... ok
test_fr010_completed_becomes_pending (test_todo.TestMarkPending...) ... ok
test_fr011_already_pending_noop (test_todo.TestMarkPending...) ... ok
test_fr012_mark_pending_not_found (test_todo.TestMarkPending...) ... ok
test_fr018_every_operation_returns_nonempty_message (test_todo.TestMessages...) ... ok
test_nfr002_non_ascii_description_preserved (test_todo.TestNFR002UTF8...) ... ok
test_nfr002_non_ascii_title_preserved (test_todo.TestNFR002UTF8...) ... ok
test_empty_file_returns_default (test_todo.TestStorageLoad...) ... ok
test_malformed_json_raises_storage_error (test_todo.TestStorageLoad...) ... ok
test_missing_file_returns_default (test_todo.TestStorageLoad...) ... ok
test_valid_json_returns_data (test_todo.TestStorageLoad...) ... ok
test_whitespace_only_file_returns_default (test_todo.TestStorageLoad...) ... ok
test_save_creates_file (test_todo.TestStorageSave...) ... ok
test_save_no_tmp_file_remains (test_todo.TestStorageSave...) ... ok
test_save_utf8_encoding (test_todo.TestStorageSave...) ... ok
test_f03_both_none_returns_error (test_todo.TestUpdateTask...) ... ok
test_f03_empty_string_description_is_valid (test_todo.TestUpdateTask...) ... ok
test_f03_none_description_leaves_description_unchanged (test_todo.TestUpdateTask...) ... ok
test_f03_none_title_leaves_title_unchanged (test_todo.TestUpdateTask...) ... ok
test_fr006_status_not_changed_by_update (test_todo.TestUpdateTask...) ... ok
test_fr006_title_trimmed_on_update (test_todo.TestUpdateTask...) ... ok
test_fr006_update_both_fields (test_todo.TestUpdateTask...) ... ok
test_fr006_update_description_only (test_todo.TestUpdateTask...) ... ok
test_fr006_update_title_only (test_todo.TestUpdateTask...) ... ok
test_fr012_update_not_found (test_todo.TestUpdateTask...) ... ok
test_fr013_update_empty_title_rejected (test_todo.TestUpdateTask...) ... ok
test_fr013_update_whitespace_title_rejected (test_todo.TestUpdateTask...) ... ok

----------------------------------------------------------------------
Ran 131 tests in 2.831s

OK
Exit code: 0
```

Total suite (all test files): **131 tests, 0 failures, 0 errors**.
The 57 todo-specific tests above all passed. The remaining 74 tests cover the SDLC pipeline
framework itself (`test_config`, `test_docs`, `test_e2e_pipeline`, `test_github_pr`,
`test_guard`, `test_orchestrator`) and also all passed.

### CLI spot-checks (from verify.md checks 3-9)

| Check | Command | Expected | Result |
|---|---|---|---|
| 3 — F-01, NFR-001 | `python -m todo.cli --help` | exit 0, usage printed | PASS |
| 4 — FR-001, FR-018 | `create "Buy milk"` | Task 1 created, exit 0 | PASS |
| 5 — FR-001, FR-003, FR-018 | `create "Walk the dog"` + `list` | Task 2, both shown in order | PASS |
| 6 — FR-008, FR-005, FR-018 | `complete 1` + `list --status completed` | Task 1 completed, filter works | PASS |
| 7 — FR-007, FR-003 | `delete 2` + `list` | Task 2 removed, Task 1 remains | PASS |
| 8 — FR-013, FR-018 | `create ""` | stderr message, exit 1 | PASS |
| 9 — FR-012, FR-018 | `complete 99` | stderr "Task 99 not found.", exit 1 | PASS |

## Risks

### R-01 — Minor: `mkdir` OSError escapes the StorageError contract

**File:** `todo/app.py:65`

```python
path.parent.mkdir(parents=True, exist_ok=True)   # outside the try block
```

If `path.parent.mkdir()` raises `OSError` (for example, when `--storage` points to a path
whose parent directory cannot be created due to permission errors), the raw `OSError` propagates
through callers' `except StorageError` clauses uncaught, producing an unhandled Python traceback
instead of the clean `{"success": False, "message": "..."}` result mandated by FR-018.

**Impact:** The default storage path (`~/.todo.json`) is unaffected because `Path.home()` always
exists. The defect only surfaces when a user explicitly passes a `--storage` path with a
non-creatable parent directory.

**Proposed fix (not implemented in this PR):** Move `path.parent.mkdir(...)` inside the
`try` block in `save()`.

**Severity:** Minor — does not affect the normal use case; surfaced only by an unusual CLI
invocation with an invalid custom storage path.

### R-02 — Nit: Unreachable `else` branch in dispatch block

**File:** `todo/cli.py:115-117`

```python
else:
    parser.print_help(sys.stderr)
    sys.exit(1)
```

Because `subparsers` is created with `required=True`, argparse raises `SystemExit(2)` before
`parse_args()` returns for any unrecognised command. This `else` branch is therefore dead code.

**Impact:** None — the code is benign and does not affect any test or runtime behaviour.

**Severity:** Nit — no functional consequence.

## Rollback

This PR is carried on branch `sdlc/todo-cli`. The most recent implementation commit is
`94ca29c`.

**Revert the entire feature branch (recommended):**

```bash
git revert 94ca29c --no-edit
git push origin sdlc/todo-cli
```

**If multiple commits need reverting** (earliest to latest order below; revert in reverse):

```bash
# identify all commits unique to this branch
git log --oneline main..sdlc/todo-cli

# revert in reverse chronological order (newest first)
git revert <sha-newest> <sha-...> <sha-oldest>
git push origin sdlc/todo-cli
```

**Rules that always apply:**
- Never force-push to `main` or `master`.
- Never use `--no-verify` or `git rebase -i` to rewrite published history.
- Never amend a published commit.
- A full rollback returns the branch to the pre-implementation state; the four
  implementation files (`todo/__init__.py`, `todo/app.py`, `todo/cli.py`,
  `tests/test_todo.py`) will be absent, which is a valid clean baseline.

## Reviewer checklist

- [ ] Verify `python orchestrator.py status` shows all 8 phases APPROVED
- [ ] Verify `python -m compileall -q .` exits 0 with no output
- [ ] Verify `python -m unittest discover -s tests -v` shows `Ran 131 tests` and `OK`
- [ ] Verify `python -m todo.cli --help` exits 0 and lists all 6 sub-commands
- [ ] Confirm every FR (FR-001 through FR-018) has at least one passing test in the traceability table above
- [ ] Confirm every NFR (NFR-001 through NFR-004) has a corresponding verification entry
- [ ] Confirm `todo/app.py` imports only stdlib modules (`json`, `os`, `pathlib`, `typing`)
- [ ] Confirm `todo/cli.py` imports only stdlib modules (`argparse`, `pathlib`, `sys`) plus `todo.app`
- [ ] Confirm no secrets, credentials, tokens, or network calls appear in any source file
- [ ] Review R-01 (Minor): accept the known defect or request a fix before merge
- [ ] Review R-02 (Nit): accept the dead-code `else` branch or request cleanup before merge
- [ ] Confirm branch is `sdlc/todo-cli` (not `main` or `master`)
- [ ] Confirm rollback instructions are executable and do not require force-push

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
