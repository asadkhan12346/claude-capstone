# Implementation Plan

## Design-review findings resolutions

All six findings from `artifacts/design-review.md` (verdict: REVISE) are resolved by this plan. The
answers were supplied by the orchestrator (main session) before this plan was written.

| Finding | Severity | Decision passed in | Resolved in task |
|---|---|---|---|
| F-01 | High | Use `python -m todo.cli` as the canonical invocation; no `__main__.py` needed or owned | T-09 |
| F-02 | Medium | `save()` uses write-to-temp-file + `os.replace()` for atomic writes | T-02 |
| F-03 | Medium | `update_task()` uses `None` as sentinel meaning "do not change this field"; both `title` and `description` are optional kwargs | T-05 |
| F-04 | Medium | `load()` raises a named `StorageError` on malformed JSON or unexpected I/O; every operation catches it and returns `{"success": False, "message": "..."}` | T-02 through T-08 |
| F-05 | Medium | Default storage path is `pathlib.Path.home() / ".todo.json"` (not CWD-relative) | T-09 |
| F-06 | Low | `list_tasks()` return shape is `{"success": bool, "message": str, "tasks": list[dict]}` | T-04 |

---

## Ordered tasks

Tasks must be implemented in the order listed. Each task depends on all previous tasks being
complete before it can be verified.

---

### T-01: Initialize `todo/__init__.py`

**Goal:** Mark `todo/` as a Python package and re-export the public API from `todo/app.py` so that
tests can import from `todo` directly.

**Files:** `todo/__init__.py`

**FR/NFR IDs:** NFR-001

**Specification:**
- File imports and re-exports: `StorageError`, `create_task`, `list_tasks`, `update_task`,
  `delete_task`, `mark_completed`, `mark_pending` from `todo.app`.
- No business logic, no I/O, no side effects at import time.
- Comment citing NFR-001: standard library only, Python 3.11+.

**Done when:**
- `python -c "from todo import create_task, StorageError"` exits with code 0.
- `python -m compileall -q todo/__init__.py` reports no errors.

---

### T-02: Implement `StorageError`, `load()`, and `save()` in `todo/app.py`

**Goal:** Build the complete storage layer: a named exception, a `load()` function that handles
missing/empty/malformed files, and a `save()` function that writes atomically via
`os.replace()`. Resolves F-02 and F-04.

**Files:** `todo/app.py`

**FR/NFR IDs:** FR-016, FR-017, FR-018, NFR-002, F-02, F-04

**Specification:**

**Module-level imports required:** `import json`, `import os`, `import pathlib`

**`StorageError(Exception)`**
- Custom exception subclassing `Exception`.
- No additional attributes beyond the message string.
- Raised by `load()` and `save()` on all unrecoverable errors.

**`load(path: pathlib.Path) -> dict`**
- If `path` does not exist (`FileNotFoundError`) → return a fresh `{"next_id": 1, "tasks": []}` dict (FR-017).
- If `path` exists and its content is empty or all-whitespace after `.read_text(encoding="utf-8")` →
  return a fresh `{"next_id": 1, "tasks": []}` dict (FR-017).
- If `path` exists and content is valid JSON → return the parsed dict.
- If `path` exists but content raises `json.JSONDecodeError` → raise
  `StorageError(f"Storage file contains malformed JSON: {path}")` (F-04).
- If any other `OSError` occurs reading the file → raise `StorageError(str(exc))` (F-04).
- File must be opened with `encoding="utf-8"` (NFR-002).
- Do NOT return a module-level mutable constant; always return a fresh dict to prevent accidental
  mutation of the default state.

**`save(path: pathlib.Path, data: dict) -> None`**
- Call `path.parent.mkdir(parents=True, exist_ok=True)` before writing (handles first-run case).
- Compute `tmp_path = pathlib.Path(str(path) + ".tmp")`.
- Open `tmp_path` with `open(tmp_path, "w", encoding="utf-8")` and write
  `json.dump(data, fh, ensure_ascii=False, indent=2)` (NFR-002, F-02).
- After a successful write, call `os.replace(tmp_path, path)` to atomically rename (F-02).
- On any `OSError` during the write or replace:
  - Attempt `tmp_path.unlink(missing_ok=True)` to clean up.
  - Raise `StorageError(str(exc))`.

**Done when:**
- `load(path)` returns `{"next_id": 1, "tasks": []}` when `path` does not exist.
- `load(path)` returns `{"next_id": 1, "tasks": []}` when `path` points to an empty file.
- `load(path)` raises `StorageError` when `path` contains `"not valid json {"`.
- `save(path, {"next_id": 1, "tasks": []})` creates `path` with valid UTF-8 JSON content.
- No `.tmp` file remains at `str(path) + ".tmp"` after a successful `save()`.
- `python -m compileall -q todo/app.py` reports no errors.

---

### T-03: Implement `create_task()` in `todo/app.py`

**Goal:** Create a task record with auto-incremented ID, trimmed title, optional description, and
persistent `next_id` counter.

**Files:** `todo/app.py`

**FR/NFR IDs:** FR-001, FR-002, FR-013, FR-014, FR-015

**Specification:**

```
def create_task(
    storage_path: pathlib.Path,
    title: str,
    description: str = "",
) -> dict:
```

Return shape: `{"success": bool, "message": str, "task": dict | None}`

Step-by-step behavior:
1. Strip `title` of surrounding whitespace; if the result is empty → return
   `{"success": False, "message": "Title cannot be empty.", "task": None}` without touching
   storage (FR-013). No `load()` or `save()` call occurs.
2. Wrap all remaining logic in:
   ```
   try:
       ...
   except StorageError as exc:
       return {"success": False, "message": str(exc), "task": None}
   ```
3. Call `load(storage_path)` → `data`.
4. Assign `task_id = data["next_id"]`.
5. Build `task = {"id": task_id, "title": stripped_title, "description": description, "status": "pending"}`.
6. Append `task` to `data["tasks"]`.
7. Increment `data["next_id"]` by 1.
8. Call `save(storage_path, data)`.
9. Return `{"success": True, "message": f"Task {task_id} created: '{stripped_title}'.", "task": task}`.

No uniqueness check on title is performed (FR-014).

**Done when:**
- `create_task(path, "Buy milk")` returns `{"success": True, "task": {"id": 1, "title": "Buy milk", "description": "", "status": "pending"}}`.
- `create_task(path, "  Buy milk  ")` stores title `"Buy milk"` (trimmed) (FR-001).
- Omitting description stores `""` (FR-002).
- `create_task(path, "  ")` returns `{"success": False}` and the storage file is not created (FR-013).
- Two sequential calls get IDs 1 and 2; after `delete_task` on ID 2, next create gets ID 3 (verified by T-06 integration) (FR-015).
- Two calls with identical titles both succeed with distinct IDs (FR-014).

---

### T-04: Implement `list_tasks()` in `todo/app.py`

**Goal:** Return all tasks in creation order with an optional status filter. Resolves F-06 by
specifying the exact return shape including a `"tasks"` key.

**Files:** `todo/app.py`

**FR/NFR IDs:** FR-003, FR-004, FR-005, F-06

**Specification:**

```
def list_tasks(
    storage_path: pathlib.Path,
    status_filter: str | None = None,
) -> dict:
```

Return shape: `{"success": bool, "message": str, "tasks": list[dict]}` (F-06)

Step-by-step behavior:
1. Wrap all logic in:
   ```
   try:
       ...
   except StorageError as exc:
       return {"success": False, "message": str(exc), "tasks": []}
   ```
2. Call `load(storage_path)` → `data`.
3. Start with `tasks = list(data["tasks"])` — already in creation/ascending-ID order (FR-003).
4. If `status_filter` is not `None` → filter: `tasks = [t for t in tasks if t["status"] == status_filter]` (FR-005).
5. If `tasks` is empty → return `{"success": True, "message": "No tasks found.", "tasks": []}` (FR-004).
6. Otherwise → return `{"success": True, "message": f"{len(tasks)} task(s) found.", "tasks": tasks}`.

**Done when:**
- Returns all tasks in ascending `id` order for an unfiltered call with multiple tasks (FR-003).
- Returns `{"tasks": [], "message": "No tasks found.", "success": True}` for a missing file (FR-004).
- Returns only tasks with `status == "completed"` when `status_filter="completed"` (FR-005).
- Returns `{"tasks": []}` when filter matches nothing (FR-005).
- Return dict always contains the key `"tasks"` of type `list` (F-06).

---

### T-05: Implement `update_task()` in `todo/app.py`

**Goal:** Update title and/or description of an existing task using `None` as the sentinel for
"do not change this field". Resolves F-03.

**Files:** `todo/app.py`

**FR/NFR IDs:** FR-006, FR-012, FR-013, F-03

**Specification:**

```
def update_task(
    storage_path: pathlib.Path,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
) -> dict:
```

Return shape: `{"success": bool, "message": str}`

Step-by-step behavior:
1. If both `title is None` and `description is None` → return
   `{"success": False, "message": "At least one of title or description must be provided."}` without
   touching storage (F-03).
2. If `title` is not `None`: strip it; if the stripped value is empty → return
   `{"success": False, "message": "Title cannot be empty."}` without touching storage (FR-013).
   Store the stripped value as `stripped_title` for later use.
3. Wrap remaining logic in:
   ```
   try:
       ...
   except StorageError as exc:
       return {"success": False, "message": str(exc)}
   ```
4. Call `load(storage_path)` → `data`.
5. Search `data["tasks"]` for a task where `task["id"] == task_id`. If not found → return
   `{"success": False, "message": f"Task {task_id} not found."}` without writing (FR-012).
6. If `title` is not `None` → set `task["title"] = stripped_title` (F-03).
7. If `description` is not `None` → set `task["description"] = description` (F-03).
8. Call `save(storage_path, data)`.
9. Return `{"success": True, "message": f"Task {task_id} updated."}`.

Neither `task["id"]` nor `task["status"]` is modified by this function (FR-006).

**Done when:**
- `update_task(path, 1, title="New title")` changes only the title; description and status are
  unchanged in storage.
- `update_task(path, 1, description="New desc")` changes only the description; title and status
  are unchanged.
- `update_task(path, 1, title="New", description="New desc")` changes both fields.
- `update_task(path, 1, title="  ")` returns `{"success": False}` and storage is not modified.
- `update_task(path, 99, title="x")` returns `{"success": False, "message": "Task 99 not found."}`.
- `update_task(path, 1)` (both `None`) returns `{"success": False}` without storage access.
- `update_task(path, 1, title=None, description="")` changes only description (empty string is a
  valid description, not a sentinel) (F-03).

---

### T-06: Implement `delete_task()` in `todo/app.py`

**Goal:** Remove a task by ID from storage.

**Files:** `todo/app.py`

**FR/NFR IDs:** FR-007, FR-012

**Specification:**

```
def delete_task(
    storage_path: pathlib.Path,
    task_id: int,
) -> dict:
```

Return shape: `{"success": bool, "message": str}`

Step-by-step behavior:
1. Wrap all logic in:
   ```
   try:
       ...
   except StorageError as exc:
       return {"success": False, "message": str(exc)}
   ```
2. Call `load(storage_path)` → `data`.
3. Find a task where `task["id"] == task_id`. If not found → return
   `{"success": False, "message": f"Task {task_id} not found."}` without writing (FR-012).
4. Rebuild `data["tasks"]` as `[t for t in data["tasks"] if t["id"] != task_id]`.
5. Call `save(storage_path, data)`.
6. Return `{"success": True, "message": f"Task {task_id} deleted."}`.

**Done when:**
- After `delete_task(path, 1)`, a subsequent `list_tasks(path)` contains no task with `id == 1`.
- `delete_task(path, 99)` returns `{"success": False, "message": "Task 99 not found."}` (FR-012).
- `data["next_id"]` is not decremented by delete (FR-015).

---

### T-07: Implement `mark_completed()` in `todo/app.py`

**Goal:** Set task status to `"completed"`; detect and handle the already-completed idempotent case
without writing to storage.

**Files:** `todo/app.py`

**FR/NFR IDs:** FR-008, FR-009, FR-012

**Specification:**

```
def mark_completed(
    storage_path: pathlib.Path,
    task_id: int,
) -> dict:
```

Return shape: `{"success": bool, "message": str}` — plus `"already_set": True` on the idempotent case.

Step-by-step behavior:
1. Wrap all logic in:
   ```
   try:
       ...
   except StorageError as exc:
       return {"success": False, "message": str(exc)}
   ```
2. Call `load(storage_path)` → `data`.
3. Find task where `task["id"] == task_id`. If not found → return
   `{"success": False, "message": f"Task {task_id} not found."}` (FR-012).
4. If `task["status"] == "completed"` → return
   `{"success": True, "message": f"Task {task_id} is already completed.", "already_set": True}`
   without calling `save()` (FR-009).
5. Set `task["status"] = "completed"`.
6. Call `save(storage_path, data)`.
7. Return `{"success": True, "message": f"Task {task_id} marked as completed."}`.

**Done when:**
- `mark_completed` on a `pending` task stores `status == "completed"` (FR-008).
- `mark_completed` on an already-`completed` task returns `{"success": True, "already_set": True}`
  and the storage file's modification time does not change (FR-009).
- `mark_completed(path, 99)` returns `{"success": False}` (FR-012).

---

### T-08: Implement `mark_pending()` in `todo/app.py`

**Goal:** Set task status to `"pending"`; detect and handle the already-pending idempotent case
without writing to storage.

**Files:** `todo/app.py`

**FR/NFR IDs:** FR-010, FR-011, FR-012

**Specification:**

```
def mark_pending(
    storage_path: pathlib.Path,
    task_id: int,
) -> dict:
```

Return shape: `{"success": bool, "message": str}` — plus `"already_set": True` on the idempotent case.

Step-by-step behavior:
1. Wrap all logic in:
   ```
   try:
       ...
   except StorageError as exc:
       return {"success": False, "message": str(exc)}
   ```
2. Call `load(storage_path)` → `data`.
3. Find task where `task["id"] == task_id`. If not found → return
   `{"success": False, "message": f"Task {task_id} not found."}` (FR-012).
4. If `task["status"] == "pending"` → return
   `{"success": True, "message": f"Task {task_id} is already pending.", "already_set": True}`
   without calling `save()` (FR-011).
5. Set `task["status"] = "pending"`.
6. Call `save(storage_path, data)`.
7. Return `{"success": True, "message": f"Task {task_id} marked as pending."}`.

**Done when:**
- `mark_pending` on a `completed` task stores `status == "pending"` (FR-010).
- `mark_pending` on an already-`pending` task returns `{"success": True, "already_set": True}`
  without writing (FR-011).
- `mark_pending(path, 99)` returns `{"success": False}` (FR-012).

---

### T-09: Implement `main()` in `todo/cli.py`

**Goal:** Provide the argparse-based CLI entry point; default storage path resolves to
`~/.todo.json`; messages route to stdout (success) or stderr (error); exit codes are 0/1.
Resolves F-01 (invocation) and F-05 (default storage path).

**Files:** `todo/cli.py`

**FR/NFR IDs:** FR-018, NFR-001, NFR-004, F-01, F-05

**Specification:**

**Module-level imports required:** `argparse`, `pathlib`, `sys`; from `todo.app` import all six
operation functions and `StorageError`.

**Module-level constant (F-05):**
```
DEFAULT_STORAGE_PATH: pathlib.Path = pathlib.Path.home() / ".todo.json"
```

**`main() -> None`:**

Top-level parser:
- `prog="todo"`, `description="Personal todo list manager"`.
- `--storage` flag: `type=pathlib.Path`, `default=DEFAULT_STORAGE_PATH`,
  `help="Path to the JSON storage file (default: ~/.todo.json)"`.
- `subparsers = parser.add_subparsers(dest="command", required=True)`.

Sub-commands and their arguments:

| Sub-command | Positional | Optional flags |
|---|---|---|
| `create` | `title` (str) | `--description` (str, default `""`) |
| `list` | none | `--status` (choices `["pending", "completed"]`, default `None`) |
| `update` | `task_id` (int) | `--title` (str, default `None`), `--description` (str, default `None`) |
| `delete` | `task_id` (int) | none |
| `complete` | `task_id` (int) | none |
| `pending` | `task_id` (int) | none |

All sub-commands accept `help=` strings (usability, FR-018).

**Dispatch logic:**
```
storage = args.storage

if args.command == "create":
    result = create_task(storage, args.title, args.description)
elif args.command == "list":
    result = list_tasks(storage, args.status)
elif args.command == "update":
    result = update_task(storage, args.task_id, title=args.title, description=args.description)
elif args.command == "delete":
    result = delete_task(storage, args.task_id)
elif args.command == "complete":
    result = mark_completed(storage, args.task_id)
elif args.command == "pending":
    result = mark_pending(storage, args.task_id)
```

**Output and exit codes (FR-018):**

For the `list` sub-command:
- If `result["success"]` is True and `result["tasks"]` is non-empty:
  - For each task in `result["tasks"]`: print `f"[{task['id']}] {task['title']} ({task['status']})"` followed by `f"    {task['description']}"` to stdout.
  - Then print `result["message"]` to stdout.
  - Exit with code 0.
- If `result["success"]` is True and `result["tasks"]` is empty:
  - Print `result["message"]` to stdout. Exit 0.
- If `result["success"]` is False:
  - Print `result["message"]` to `sys.stderr`. Exit 1.

For all other sub-commands:
- `result["success"]` True → print `result["message"]` to stdout; call `sys.exit(0)`.
- `result["success"]` False → print `result["message"]` to `sys.stderr`; call `sys.exit(1)`.

**Entry-point guard at end of file:**
```
if __name__ == "__main__":
    main()
```

**Canonical invocation (F-01):** `python -m todo.cli <subcommand> [args]`

**Done when:**
- `python -m todo.cli --help` exits 0 and prints usage.
- `python -m todo.cli create "Test" --storage /tmp/x.json` exits 0 and prints a success message.
- `python -m todo.cli create "" --storage /tmp/x.json` exits 1 and message appears on stderr.
- `python -m todo.cli list --storage /tmp/x.json` exits 0.
- `python -m todo.cli complete 99 --storage /tmp/x.json` exits 1.
- `python -m todo.cli update 1 --storage /tmp/x.json` (no --title or --description) exits 1.
- `python -m compileall -q todo/cli.py` reports no errors.

---

### T-10: Write `tests/test_todo.py`

**Goal:** Full automated test suite using `unittest` and `tempfile.TemporaryDirectory` isolation.
Every test class or method cites its FR/NFR/finding IDs.

**Files:** `tests/test_todo.py`

**FR/NFR IDs:** NFR-004, FR-001 through FR-018, NFR-002, F-01 through F-06

**Specification:**

Required imports: `json`, `os`, `pathlib`, `subprocess`, `sys`, `tempfile`, `unittest`.
From `todo.app` import: `StorageError`, `create_task`, `list_tasks`, `update_task`, `delete_task`,
`mark_completed`, `mark_pending`.
From `todo.app` import: `load`, `save` (for storage-layer tests).

All test classes subclass `unittest.TestCase`.
All test methods that need a storage file use `self.tmp_dir = tempfile.TemporaryDirectory()` in
`setUp()` and `self.tmp_dir.cleanup()` in `tearDown()`.
No test writes to `pathlib.Path.home() / ".todo.json"` or any path outside the temp directory.

**Required test classes and methods:**

**`TestStorageLoad`** — covers FR-016, FR-017, F-04
- `test_missing_file_returns_default`: `load(nonexistent_path)` returns `{"next_id": 1, "tasks": []}`.
- `test_empty_file_returns_default`: `load(path_to_empty_file)` returns `{"next_id": 1, "tasks": []}`.
- `test_valid_json_returns_data`: `load(path_to_valid_json)` returns the parsed dict.
- `test_malformed_json_raises_storage_error`: `load(path_to_bad_json)` raises `StorageError`.

**`TestStorageSave`** — covers FR-016, NFR-002, F-02
- `test_save_creates_file`: after `save(path, data)`, `path.exists()` is True and content is valid JSON.
- `test_save_no_tmp_file_remains`: after `save(path, data)`, no file at `str(path) + ".tmp"` exists.
- `test_save_utf8_encoding`: saving a task with a non-ASCII title round-trips correctly via `load()`.

**`TestCreateTask`** — covers FR-001, FR-002, FR-013, FR-014, FR-015
- `test_fr001_create_basic`: creates a task; asserts `id==1`, `status=="pending"`, `success==True`.
- `test_fr001_title_trimmed`: `create_task(path, "  Buy milk  ")` stores `"Buy milk"`.
- `test_fr002_description_defaults_empty`: no description arg → stored `description == ""`.
- `test_fr013_empty_title_rejected`: `create_task(path, "")` returns `success==False`; no file created.
- `test_fr013_whitespace_title_rejected`: `create_task(path, "   ")` returns `success==False`.
- `test_fr014_duplicate_titles_allowed`: two creates with same title both return `success==True` with distinct IDs.
- `test_fr015_ids_auto_increment`: first create → ID 1; second → ID 2.
- `test_fr015_id_not_reused_after_delete`: create ID 1, create ID 2, delete ID 2, create → ID 3.

**`TestListTasks`** — covers FR-003, FR-004, FR-005, F-06
- `test_fr003_all_tasks_in_creation_order`: two tasks returned with `tasks[0]["id"] < tasks[1]["id"]`.
- `test_fr004_empty_list_message`: `list_tasks` on missing file → `tasks == []`, `success == True`, `message` is non-empty.
- `test_fr005_filter_by_completed`: only completed tasks returned when `status_filter="completed"`.
- `test_fr005_filter_by_pending`: only pending tasks returned when `status_filter="pending"`.
- `test_fr005_filter_no_match`: `tasks == []` when filter matches nothing.
- `test_f06_return_shape_has_tasks_key`: return dict always contains key `"tasks"` of type `list`.

**`TestUpdateTask`** — covers FR-006, FR-012, FR-013, F-03
- `test_fr006_update_title_only`: only title changes; description and status unchanged.
- `test_fr006_update_description_only`: only description changes; title and status unchanged.
- `test_fr006_update_both_fields`: both title and description change; status unchanged.
- `test_fr006_title_trimmed_on_update`: `title="  New  "` stores `"New"`.
- `test_fr006_status_not_changed_by_update`: status field is unaffected.
- `test_fr012_update_not_found`: `update_task(path, 99, title="x")` → `success==False`, message contains "not found".
- `test_fr013_update_empty_title_rejected`: `update_task(path, 1, title="")` → `success==False`, storage unchanged.
- `test_f03_none_title_leaves_title_unchanged`: `update_task(path, 1, title=None, description="new")` → title unchanged.
- `test_f03_none_description_leaves_description_unchanged`: `update_task(path, 1, title="new", description=None)` → description unchanged.
- `test_f03_both_none_returns_error`: `update_task(path, 1)` → `success==False`.
- `test_f03_empty_string_description_is_valid`: `update_task(path, 1, description="")` succeeds and stores `""`.

**`TestDeleteTask`** — covers FR-007, FR-012
- `test_fr007_delete_removes_task`: after delete, `list_tasks` has no task with that ID.
- `test_fr007_task_absent_from_subsequent_list`: round-trip verification via `list_tasks`.
- `test_fr012_delete_not_found`: `delete_task(path, 99)` → `success==False`.

**`TestMarkCompleted`** — covers FR-008, FR-009, FR-012
- `test_fr008_pending_becomes_completed`: status changes to `"completed"`.
- `test_fr009_already_completed_noop`: returns `success==True`, `already_set==True`; storage unchanged.
- `test_fr012_mark_completed_not_found`: `mark_completed(path, 99)` → `success==False`.

**`TestMarkPending`** — covers FR-010, FR-011, FR-012
- `test_fr010_completed_becomes_pending`: status changes to `"pending"`.
- `test_fr011_already_pending_noop`: returns `success==True`, `already_set==True`; storage unchanged.
- `test_fr012_mark_pending_not_found`: `mark_pending(path, 99)` → `success==False`.

**`TestMessages`** — covers FR-018
- `test_fr018_every_operation_returns_nonempty_message`: calls all six operations on valid and invalid
  inputs; asserts `isinstance(result["message"], str)` and `len(result["message"]) > 0` in all cases.

**`TestNFR002UTF8`** — covers NFR-002
- `test_nfr002_non_ascii_title_preserved`: creates a task with a title containing non-ASCII characters
  (e.g., `"Compra leche — café"`); reloads via `load()` and asserts the title round-trips identically.
- `test_nfr002_non_ascii_description_preserved`: same check for description field.

**`TestCLIIntegration`** — covers F-01, FR-018, NFR-004
- All methods in this class invoke `subprocess.run(["python", "-m", "todo.cli", ..., "--storage", str(tmp_path)], ...)`.
- `test_f01_invocation_python_m_todo_cli`: `subprocess.run(["python", "-m", "todo.cli", "--help"])` → `returncode == 0`.
- `test_cli_create_success_exit_0`: create with valid title → `returncode == 0`, stdout contains task ID.
- `test_cli_create_empty_title_exit_1`: create with `""` → `returncode == 1`, stderr is non-empty.
- `test_cli_list_empty_exit_0`: list on fresh storage → `returncode == 0`.
- `test_cli_complete_not_found_exit_1`: `complete 99` → `returncode == 1`.
- `test_cli_default_storage_is_home`: verifies `DEFAULT_STORAGE_PATH == pathlib.Path.home() / ".todo.json"` (imports constant, no subprocess needed).

**Done when:** `python -m unittest discover -s tests -v` completes with 0 errors and 0 failures.

---

## File-level change list

| File | Action | Defines |
|---|---|---|
| `todo/__init__.py` | Create | Re-exports: `StorageError`, `create_task`, `list_tasks`, `update_task`, `delete_task`, `mark_completed`, `mark_pending` |
| `todo/app.py` | Create | `StorageError`; `load()`; `save()`; `create_task()`; `list_tasks()`; `update_task()`; `delete_task()`; `mark_completed()`; `mark_pending()` |
| `todo/cli.py` | Create | `DEFAULT_STORAGE_PATH`; `main()` with argparse sub-commands `create`, `list`, `update`, `delete`, `complete`, `pending`; `if __name__ == "__main__"` guard |
| `tests/test_todo.py` | Create | `TestStorageLoad`, `TestStorageSave`, `TestCreateTask`, `TestListTasks`, `TestUpdateTask`, `TestDeleteTask`, `TestMarkCompleted`, `TestMarkPending`, `TestMessages`, `TestNFR002UTF8`, `TestCLIIntegration` |

No file outside these four paths is modified. `sdlc/`, `orchestrator.py`, `.claude/hooks/`, and
`.claude/settings.json` are not touched.

---

## Test plan

Each row maps a requirement or finding ID to the named `unittest` method that verifies it, and
states the observable outcome the test must assert.

| ID | Test class | Test method | Observable outcome |
|---|---|---|---|
| FR-001 | `TestCreateTask` | `test_fr001_create_basic` | `result["task"]["id"] == 1`, `result["task"]["status"] == "pending"`, `result["success"] == True` |
| FR-001 | `TestCreateTask` | `test_fr001_title_trimmed` | `result["task"]["title"] == "Buy milk"` when input is `"  Buy milk  "` |
| FR-002 | `TestCreateTask` | `test_fr002_description_defaults_empty` | `result["task"]["description"] == ""` when `description` arg is omitted |
| FR-003 | `TestListTasks` | `test_fr003_all_tasks_in_creation_order` | `tasks[0]["id"] < tasks[1]["id"]` for two created tasks |
| FR-004 | `TestListTasks` | `test_fr004_empty_list_message` | `result["tasks"] == []`, `result["success"] == True`, `result["message"]` non-empty |
| FR-005 | `TestListTasks` | `test_fr005_filter_by_completed` | All items in `result["tasks"]` have `status == "completed"` |
| FR-005 | `TestListTasks` | `test_fr005_filter_no_match` | `result["tasks"] == []` when no task matches filter |
| FR-006 | `TestUpdateTask` | `test_fr006_update_title_only` | Stored title changed; description and status unchanged |
| FR-006 | `TestUpdateTask` | `test_fr006_update_description_only` | Stored description changed; title and status unchanged |
| FR-006 | `TestUpdateTask` | `test_fr006_status_not_changed_by_update` | `task["status"]` is identical before and after update |
| FR-007 | `TestDeleteTask` | `test_fr007_task_absent_from_subsequent_list` | `list_tasks` returns no task with the deleted ID |
| FR-008 | `TestMarkCompleted` | `test_fr008_pending_becomes_completed` | Stored `status == "completed"` after call |
| FR-009 | `TestMarkCompleted` | `test_fr009_already_completed_noop` | `result["success"] == True`, `result.get("already_set") == True`, storage file mtime unchanged |
| FR-010 | `TestMarkPending` | `test_fr010_completed_becomes_pending` | Stored `status == "pending"` after call |
| FR-011 | `TestMarkPending` | `test_fr011_already_pending_noop` | `result["success"] == True`, `result.get("already_set") == True`, storage file mtime unchanged |
| FR-012 | `TestUpdateTask` | `test_fr012_update_not_found` | `result["success"] == False`, `"not found"` in `result["message"]` |
| FR-012 | `TestDeleteTask` | `test_fr012_delete_not_found` | `result["success"] == False` |
| FR-012 | `TestMarkCompleted` | `test_fr012_mark_completed_not_found` | `result["success"] == False` |
| FR-012 | `TestMarkPending` | `test_fr012_mark_pending_not_found` | `result["success"] == False` |
| FR-013 | `TestCreateTask` | `test_fr013_empty_title_rejected` | `result["success"] == False`; storage file not created |
| FR-013 | `TestCreateTask` | `test_fr013_whitespace_title_rejected` | `result["success"] == False`; storage file not created |
| FR-013 | `TestUpdateTask` | `test_fr013_update_empty_title_rejected` | `result["success"] == False`; storage content unchanged |
| FR-014 | `TestCreateTask` | `test_fr014_duplicate_titles_allowed` | Both calls return `success == True`; IDs differ |
| FR-015 | `TestCreateTask` | `test_fr015_ids_auto_increment` | First create → `id == 1`; second → `id == 2` |
| FR-015 | `TestCreateTask` | `test_fr015_id_not_reused_after_delete` | After delete of ID 2, third create → `id == 3` |
| FR-016 | `TestStorageSave` | `test_save_creates_file` | `path.exists() == True`; content parses as valid JSON |
| FR-017 | `TestStorageLoad` | `test_missing_file_returns_default` | `load(nonexistent)` returns `{"next_id": 1, "tasks": []}` |
| FR-017 | `TestStorageLoad` | `test_empty_file_returns_default` | `load(empty_file)` returns `{"next_id": 1, "tasks": []}` |
| FR-018 | `TestMessages` | `test_fr018_every_operation_returns_nonempty_message` | `isinstance(result["message"], str) and len(result["message"]) > 0` for all six operations |
| NFR-002 | `TestNFR002UTF8` | `test_nfr002_non_ascii_title_preserved` | Title with non-ASCII chars round-trips via `save()`/`load()` without corruption |
| NFR-002 | `TestStorageSave` | `test_save_utf8_encoding` | Non-ASCII content verifiable in raw file bytes |
| NFR-004 | `TestCLIIntegration` | `test_f01_invocation_python_m_todo_cli` | `subprocess.run(["python", "-m", "todo.cli", "--help"]).returncode == 0` |
| F-01 | `TestCLIIntegration` | `test_f01_invocation_python_m_todo_cli` | Exit code 0; no `No module named todo.__main__` error |
| F-02 | `TestStorageSave` | `test_save_no_tmp_file_remains` | No file at `str(path) + ".tmp"` after successful `save()` |
| F-03 | `TestUpdateTask` | `test_f03_none_title_leaves_title_unchanged` | Title field in storage is identical before and after call |
| F-03 | `TestUpdateTask` | `test_f03_both_none_returns_error` | `result["success"] == False` when both kwargs are `None` |
| F-04 | `TestStorageLoad` | `test_malformed_json_raises_storage_error` | `assertRaises(StorageError, load, bad_path)` passes |
| F-05 | `TestCLIIntegration` | `test_cli_default_storage_is_home` | `DEFAULT_STORAGE_PATH == pathlib.Path.home() / ".todo.json"` |
| F-06 | `TestListTasks` | `test_f06_return_shape_has_tasks_key` | `"tasks" in result` and `isinstance(result["tasks"], list)` |

**Run command:** `python -m unittest discover -s tests -v`

---

## Rollback notes

Rollback is performed exclusively via `git revert`. No force-push, history rewrite, or
`--no-verify` flags are permitted.

- Each task (T-01 through T-10) must be committed separately with a conventional-commit message,
  for example `feat(todo): implement storage layer (T-02)`, so any single task can be reverted
  cleanly without disturbing others.
- To revert a single task: `git revert <commit-sha>` and push the revert commit.
- To revert the entire implementation phase: `git revert <sha-T-10> <sha-T-09> ... <sha-T-01>` (in
  reverse order) or `git revert <oldest-sha>..<newest-sha>` using the range syntax.
- Because all four implementation files (`todo/__init__.py`, `todo/app.py`, `todo/cli.py`,
  `tests/test_todo.py`) are new in this branch, a full rollback returns the branch to the state
  where none of those files exist, which is also a valid clean state.
- Never amend a published commit.
