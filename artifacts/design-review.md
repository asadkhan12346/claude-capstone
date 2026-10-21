# Design Review

## Summary

This review independently evaluates `artifacts/architecture.md` against `artifacts/requirements.md` (18 FRs, 4 NFRs) for the Todo CLI application (US-001). All 22 requirement IDs are addressed by the architecture, and the overall two-layer design (`app.py` + `cli.py`) is sound and well-reasoned. However, one High-severity finding and four Medium-severity findings require revisions before the architecture can safely be handed to the implementation phase.

The High finding (F-01) is a concrete implementation blocker: the architecture documents `python -m todo` as the canonical invocation path, but the phase 5 contract-owned file list does not include `todo/__main__.py`, which Python requires for that invocation to work with a package. Absent this file, the documented invocation will raise `No module named todo.__main__; 'todo' is a package and cannot be directly executed.`

---

## Findings

| ID | Severity | Area | Finding | Related IDs | Suggested Change |
|---|---|---|---|---|---|
| F-01 | High | Architecture / CLI invocation | The architecture (Overview, Components, Control/data flow section "Invocation path") documents `python -m todo` as the canonical way to run the tool. Python packages require `todo/__main__.py` for this to work. That file is absent from the phase 5 contract-owned list (`todo/__init__.py`, `todo/app.py`, `todo/cli.py`, `tests/test_todo.py`). The implementation agent can only write those four files, so the documented invocation will fail at runtime and in any integration test that uses `subprocess`. | NFR-004, FR-018 | Either (a) add `todo/__main__.py` to the phase 5 owned files in the contract and architecture, or (b) change all documented and tested invocations to `python -m todo.cli` (no extra file needed). Option (b) requires no contract change and is fully within the four-file scope. |
| F-02 | Medium | Data integrity / Write strategy | The "Write strategy" section uses the word "atomically" (`apply the in-memory mutation, then write back atomically`), yet the Decisions table entry explicitly states "No atomic file-swap or file-locking mechanism". The contradiction is dangerous: a standard `open(path, 'w')` truncates the file immediately and then fills it. A disk-full condition or OS crash after truncation but before completion will leave `todo.json` empty or partially written — triggering the malformed-JSON unrecoverable error path (Error handling table, row 6) and causing data loss. | FR-016, FR-017 | Remove the word "atomically" from the write strategy text, or — preferred — specify a write-to-temp-then-`os.replace()` approach (standard library, no platform-specific APIs, true atomicity). This would also eliminate the self-contradiction. |
| F-03 | Medium | Architecture / `app.py` | `update_task(storage_path, task_id, title, description)` has no specification for partial-update semantics. FR-006 explicitly states the user may supply "a new title, a new description, or both". If both parameters are always required, CLI users who only want to change the title must also re-supply the description (or lose it). The architecture does not say what value signals "do not modify this field". | FR-006 | Specify that `None` (or a dedicated sentinel) for `title` or `description` means "leave unchanged". Document the default values in the function signature and in the Components section. The CLI layer must then declare those args as `--title` / `--description` optional flags rather than positional arguments. |
| F-04 | Medium | Architecture / `StorageManager` | The return contract for `load(path) -> dict` covers only the happy path and the absent/empty-file case. When the file contains malformed JSON, the architecture says "surface an error message and do not overwrite" (Data model, Missing/empty file handling), and the Error handling table lists it as exit code 1. However, it is not specified whether `load()` raises an exception or returns a sentinel dict in that case. Every one of the six operation functions must handle this error uniformly; without a defined contract, implementations will diverge. | FR-017, FR-018 | Add to the Components section for `StorageManager` a specification that `load()` raises a named exception (e.g., `StorageError`) on malformed JSON or unexpected I/O errors. Each operation function catches it and returns `{"success": False, "message": "..."}`. Alternatively, define a sentinel return value, but document it explicitly. |
| F-05 | Medium | Usability / Storage path default | The architecture defaults the storage file to `todo.json` in the current working directory. A personal todo-list CLI tool is typically invoked from many different directories (home, project roots, temp directories). With a CWD-relative default, the user sees a different (or empty) list depending on where they are in the shell, which is confusing and effectively loses data from the user's perspective. | FR-016, Constraints ("exact filename and path are a design decision") | Consider defaulting to a user-home-relative path such as `pathlib.Path.home() / ".todo.json"`, which gives a single consistent list regardless of CWD. The path-as-parameter architecture supports this change without modifying `app.py`. If CWD is intentional (e.g., per-project lists), that rationale should be documented in the Decisions table. |
| F-06 | Low | Architecture / Return contract | The Components section states every callable returns "at minimum a boolean `success` flag, a string `message`, and (where applicable) the affected task dict." The phrase "affected task dict" applies well to single-task operations but is undefined for `list_tasks`, which must return multiple task records for `cli.py` to print them. FR-003 and FR-005 require the CLI to show ID, title, description, and status for each task — impossible if the return shape only carries a single optional task. | FR-003, FR-004, FR-005 | Add an explicit return shape for `list_tasks` in the Components section, e.g.: `{"success": bool, "message": str, "tasks": list[dict]}`. This removes ambiguity and gives the implementation and test authors a concrete contract. |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Implementation agent uses `python -m todo` in integration tests and cannot make them pass | High (F-01 unresolved) | High — test suite fails to submit | Resolve F-01 before planning/implementation |
| Disk-full or crash during write corrupts `todo.json`, triggering the unrecoverable JSON error path on all future runs | Low | High — full data loss with no user recovery other than deleting the file | Write atomically via temp file + `os.replace()` (F-02) |
| `update_task` partial-update ambiguity causes divergent CLI and app implementations | Medium | Medium — FR-006 acceptance criteria fail | Resolve F-03 before planning |
| `load()` error-propagation ambiguity causes inconsistent error handling across the six operations | Medium | Medium — some error paths produce unhandled exceptions instead of clean exit-1 messages | Resolve F-04 before implementation |
| CWD-relative default storage creates "lost list" user-confusion bug reports | High | Low-Medium — no data loss, but significant usability regression | Document rationale or change default (F-05) |

---

## Alternatives considered and why rejected

### Alternative 1: SQLite instead of JSON file for persistence

FR-016 explicitly specifies "a local JSON file" as the storage medium. SQLite (also standard library via `sqlite3`) would offer ACID transactions, atomic writes, and efficient queries, eliminating F-02 and the partial-write risk entirely. However, adopting SQLite would directly contradict FR-016 and the human clarification recorded in requirements Open Questions (Q1: "file-based persistence using a local JSON file"). The JSON approach is the correct choice given the requirements; the write-atomicity risk should be mitigated within the JSON approach via `os.replace()`.

### Alternative 2: Raising exceptions from `app.py` vs returning result dicts

The architecture chose to return plain `dict` result objects from every `app.py` operation instead of raising custom exceptions for error conditions. The alternative — raising `TaskNotFoundError`, `InvalidTitleError`, etc. — is idiomatic Python and would make error paths explicit in type signatures. The result-dict approach was chosen because it simplifies unit test assertions (check `result["success"]` without a try/except) and avoids designing an exception hierarchy for a small application. This is a defensible choice for this scope; no finding is raised. The exception model would become preferable if the application grew into a library consumed by other code.

### Alternative 3: Module-level `STORAGE_PATH` constant vs path-as-parameter

A module-level constant or a `StorageManager` class instance holding the path would simplify every function call signature. The architecture correctly rejected this in favor of path injection as a parameter, citing testability (NFR-004): injecting a `tempfile.TemporaryDirectory` path requires no monkey-patching and no module reload between tests. This is the right choice and directly enables the test isolation requirement.

### Alternative 4: Single-file vs two-module (`app.py` + `cli.py`) split

Combining all logic into one file (`cli.py` or `app.py`) would reduce indirection. The architecture correctly rejected this because mixing presentation (argparse, print, exit codes) with business logic destroys the testability seam: unit tests would have to capture stdout or mock print, rather than asserting on return values. The two-module split is the correct structural decision for NFR-004.

---

## Security review

The architecture is secure within the scope defined by the requirements.

- **NFR-003 (no network calls, no secrets):** The Decisions table and Components sections make no reference to `urllib`, `http.client`, `socket`, `requests`, or any credential fields. This is addressed correctly.
- **NFR-001 (standard library only):** All identified dependencies (`argparse`, `json`, `os`, `pathlib`, `tempfile`, `unittest`) are standard library. No third-party packages are introduced.
- **Input handling:** JSON deserialization uses Python's standard `json` module, which does not execute arbitrary code. No `eval()`, `exec()`, or `pickle` is used. Whitespace-stripped title validation (FR-013) provides a minor defense against empty-key injection into the JSON structure.
- **File path exposure:** The storage path is accepted as a CLI parameter (default CWD-relative). This means a user can point the CLI at any file on the filesystem. For a single-user personal tool this is acceptable; no multi-user or privilege-boundary concern exists. If a future version exposes a `--storage-path` option, implementors should document that it writes the file at the given path without further sanitization.
- **No path-traversal amplification:** The `load()`/`save()` functions operate on a path provided by the caller. There is no recursive expansion, glob resolution, or include mechanism that could traverse outside the intended directory.
- **Malformed-JSON handling:** The architecture explicitly refuses to overwrite a corrupt but present file, preventing silent data destruction. This is the correct security-conservative choice.

No security findings are raised.

---

## Usability and accessibility review

The architecture makes correct high-level choices for a CLI tool:

- Success and informational messages route to `stdout`; error messages route to `stderr`. This allows shell pipelines and scripts to distinguish output from errors (`2>/dev/null`, `if todo list 2>&1 | grep ...`). Correct.
- Exit code `0` for success and idempotent no-ops, exit code `1` for errors, is the POSIX convention. Correct.
- `argparse` provides `--help` automatically for every sub-command. No explicit help text is mandated, but implementors should add `help=` strings to each argument parser.
- FR-018 ensures no operation completes silently. All paths produce a human-readable message. Good.

Usability concern (F-05, Medium): The CWD-relative default for the storage file is the most significant usability issue in the architecture. A user who runs `todo create "Buy milk"` from `~/projects/foo` and then runs `todo list` from `~` will see an empty list. This is unexpected behavior for a "personal" todo list and is likely to result in users believing their data was lost. See F-05 for the recommended fix.

Accessibility note: The architecture does not mandate ANSI color codes or terminal-specific formatting. Plain-text output is screen-reader-compatible and works in all terminal emulators, CI log viewers, and non-interactive pipes. This is the correct default for a CLI tool.

---

## Requirement coverage check

| ID | Covered? | Architecture reference | Notes |
|---|---|---|---|
| FR-001 | Yes | `app.py` → `create_task`; Decisions table row 1 | Trimmed title, default description, `pending` status, assigned ID, success message |
| FR-002 | Yes | `app.py` → `create_task`; Data model table (`description` defaults to `""`) | Description parameter defaults to empty string |
| FR-003 | Yes | `app.py` → `list_tasks`; Data model (`tasks` array in creation order) | Ascending-ID order by append semantics; F-06 (Low) flags underspecified return shape |
| FR-004 | Yes | `app.py` → `list_tasks`; Control/data flow | Empty-tasks case returns informational message |
| FR-005 | Yes | `app.py` → `list_tasks` with `status_filter` | In-memory filter; empty-match case returns appropriate message |
| FR-006 | Partial | `app.py` → `update_task` | Functional coverage present; F-03 (Medium) flags undefined partial-update semantics |
| FR-007 | Yes | `app.py` → `delete_task` | Removes task from array and saves |
| FR-008 | Yes | `app.py` → `mark_completed` | Sets `status="completed"`, returns success |
| FR-009 | Yes | `app.py` → `mark_completed`; Error handling table; Control/data flow "Idempotent no-op" | Already-completed guard, no write, exit 0 |
| FR-010 | Yes | `app.py` → `mark_pending` | Sets `status="pending"`, returns success |
| FR-011 | Yes | `app.py` → `mark_pending`; Error handling table | Already-pending guard, no write, exit 0 |
| FR-012 | Yes | `app.py` (all write operations); Error handling table | ID-not-found returns `success=False`, no write |
| FR-013 | Yes | `app.py` → `create_task`, `update_task`; Decisions table | Title stripped and checked before storage read |
| FR-014 | Yes | `app.py` → `create_task` (no uniqueness check) | Duplicate titles accepted; distinct ID assigned |
| FR-015 | Yes | `app.py` → `create_task`; Data model `next_id` field; Decisions table | Counter persists in JSON, never decremented |
| FR-016 | Yes | `app.py` → `StorageManager`; Data model | All reads/writes through `load()`/`save()`; UTF-8 JSON file |
| FR-017 | Yes | `app.py` → `StorageManager` `load()`; Data model "Missing / empty file handling" | Absent or empty file returns default empty state |
| FR-018 | Yes | `app.py` return contract + `cli.py` print; Error handling table | Every operation returns a non-empty message; CLI always prints it |
| NFR-001 | Yes | Decisions table (`argparse`, `json`, `os`, `tempfile`, `unittest`) | Standard library only; Python 3.11+ |
| NFR-002 | Yes | `app.py` → `StorageManager`; Decisions table | `open(..., encoding="utf-8")` on all file handles |
| NFR-003 | Yes | Decisions table; Components sections | No network calls, no credential fields |
| NFR-004 | Yes | `app.py` return contract; `tests/test_todo.py`; Decisions table (path injection) | Injectable path; result dicts for assertion; `tempfile` isolation; FR-ID citation in tests |

Coverage summary: All 18 FRs and 4 NFRs have explicit architecture references. FR-006 is functionally present but requires clarification on partial-update semantics (F-03). FR-003/FR-005 are functionally present but the return contract for multi-task results is underspecified (F-06).

---

Verdict: REVISE
