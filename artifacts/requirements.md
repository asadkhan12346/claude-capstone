# Requirements

## Source

- Primary story: `user_story.md` (Todo List).
- Product details and constraints: user-provided master prompt, Section 8, “The Sample Story and the App It Produces,” plus its repository-wide hard rules.
- Clarification source: the human delegated resolution with “u do yourself” on 2026-10-05. Where the master prompt is silent, this artifact records the behavior as unspecified rather than assuming it.

## Functional Requirements

1. **FR-001 - Command-line operations.** Given a user invokes the module, when they provide `add "<title>"`, `list`, `done <id>`, `reopen <id>`, or `delete <id>`, then the corresponding task operation is performed; invalid command forms produce a usage error.
2. **FR-002 - Create a task.** Given a valid title, when the user runs `add`, then one task is created and the command reports its identifier, title, and `open` status.
3. **FR-003 - Initial task status.** Given a task is created, when its record is stored or displayed, then its initial status is `open`.
4. **FR-004 - Add output.** Given task creation succeeds, when the command returns, then stdout contains `Added: <id> [open] <title>` for the created task.
5. **FR-005 - List tasks.** Given one or more tasks exist, when the user runs `list`, then stdout contains one `<id> [open|done] <title>` record per task in creation order.
6. **FR-006 - Empty list.** Given no tasks exist, when the user runs `list`, then stdout contains `No tasks.`.
7. **FR-007 - Complete an open task.** Given an existing task has status `open`, when the user runs `done <id>`, then its status becomes `done`.
8. **FR-008 - Complete an already-done task.** Given an existing task has status `done`, when the user runs `done <id>`, then stdout contains `Task <id> is already done.` and the task data is unchanged.
9. **FR-009 - Reopen a done task.** Given an existing task has status `done`, when the user runs `reopen <id>`, then its status becomes `open`.
10. **FR-010 - Reopen an already-open task.** Given an existing task has status `open`, when the user runs `reopen <id>`, then stdout contains `Task <id> is already open.` and the task data is unchanged.
11. **FR-011 - Delete a task.** Given an existing task, when the user runs `delete <id>`, then that task is absent from subsequent lists.
12. **FR-012 - Unknown task ID.** Given a task-changing command refers to an ID not in storage, when the command runs, then stderr contains `Error: task <id> not found.`, the exit code is 1, and stored task data is unchanged.
13. **FR-013 - Invalid task ID.** Given an ID is non-numeric, zero, or negative, when a task operation uses it, then it is handled as not found with the behavior in FR-012.
14. **FR-014 - Usage error.** Given a command or its arguments do not match the supported CLI forms, when the CLI handles the request, then it prints usage text beginning with `USAGE` and returns exit code 2.
15. **FR-015 - Error stream and exit status.** Given an operation fails because of invalid task data or storage, when the CLI reports the failure, then the error is written to stderr and the command returns a non-zero error exit status (1 for task-not-found errors).
16. **FR-016 - Empty title rejection.** Given an add request contains an empty or whitespace-only title, when the request is processed, then it is rejected as an error and no task is created.
17. **FR-017 - Title whitespace.** Given a title has surrounding whitespace and internal whitespace, when it is added, then surrounding whitespace is trimmed and internal whitespace is preserved.
18. **FR-018 - Duplicate titles.** Given a title matches an existing task title, when it is added, then creation is allowed and a distinct task ID is assigned.
19. **FR-019 - No count or title-length limit.** Given a title or task count grows, when the application accepts the data, then it imposes no product-defined title-length or task-count limit.
20. **FR-020 - Persistent storage contract.** Given the application reads or changes tasks, when it accesses persistent data, then it uses `tasks.json` in the current working directory with the top-level shape `{"next_id": N, "tasks": [...]}` and task records containing `id`, `title`, and `status`.
21. **FR-021 - Missing or empty storage.** Given `tasks.json` is missing or empty, when the user lists tasks or adds a task, then it is treated as an empty task list.
22. **FR-022 - Corrupt storage.** Given `tasks.json` contains invalid JSON, invalid field types, or duplicate task IDs, when storage is loaded, then a `CorruptStorageError` is raised and the original file bytes remain unchanged.
23. **FR-023 - Other storage I/O failures.** Given a storage operation fails for an I/O reason other than corrupt content, when the application reports the failure, then it raises `StorageError`.
24. **FR-024 - Monotonic, non-reused IDs.** Given tasks are created and later deleted, when subsequent tasks are added, then IDs start at 1, increase by 1, are never reused, and the next ID persists across runs.

## Non-Functional Requirements

1. **NFR-001 - Runtime and dependencies.** Given the application is run, then it supports Python 3.11 or newer and uses only the Python standard library.
2. **NFR-002 - Storage encoding and representation.** Given task data is serialized, then `tasks.json` is UTF-8 JSON, uses `ensure_ascii=False`, and is indented by two spaces.
3. **NFR-003 - Atomic saves.** Given a successful change is saved, then the write uses a temporary file in the same directory, flushes and fsyncs it, preserves the existing file mode, replaces the destination atomically, and cleans up the temporary file on failure.
4. **NFR-004 - No unintended writes.** Given a list, no-op, invalid request, or failed operation runs, then `tasks.json` bytes remain unchanged; the file is modified only after a successful task change.
5. **NFR-005 - Local privacy.** Given the application runs, then it makes no network calls and does not require, expose, or store secrets.
6. **NFR-006 - Testability.** Given automated tests run, then they use `unittest` and temporary directories, and each FR has at least one test that cites its FR ID.

## Constraints

- The application is a command-line Todo list with free-text task titles.
- CLI operations are `python -m todo.cli add "<title>"`, `list`, `done <id>`, `reopen <id>`, and `delete <id>`.
- The application layer exposes a `Task` data class, the specified `TodoError` hierarchy, and `TodoApp` task operations; it does not print output or read command-line arguments.
- The CLI exposes `main(argv, stdout, stderr, app) -> int`, does not call `sys.exit`, and uses exit codes 0 (success), 1 (operation error), and 2 (usage error).
- No concurrency guarantee or simultaneous-writer behavior is specified by the source material.
- No measurable performance target is specified by the source material.

## Assumptions

- “Clear error” and “clear message” in the story are made concrete using the exact output strings in the user-provided master prompt.
- The detailed master prompt's Section 8 supplies the human-delegated decisions for command syntax, title handling, persistence, IDs, limits, output, and storage failures.
- Concurrent access and performance remain unspecified; this artifact makes no guarantee about them.

## Open Questions

- [x] Q: What command forms perform create, view, complete, reopen, and delete? A: `add "<title>"`, `list`, `done <id>`, `reopen <id>`, and `delete <id>`. (source: user-provided master prompt, Section 8; human delegated resolution on 2026-10-05)
- [x] Q: What are the required success, empty-list, no-op, not-found, and usage outputs and exit codes? A: Use the exact strings in FR-004 through FR-014; usage errors print `USAGE` and return 2, task-not-found errors go to stderr and return 1. (source: user-provided master prompt, Section 8; human delegated resolution on 2026-10-05)
- [x] Q: How are empty, whitespace, duplicate, and long titles handled? A: Empty and whitespace-only titles are rejected; trim surrounding whitespace, preserve internal whitespace, allow duplicates, and impose no title-length limit. (source: user-provided master prompt, Section 8; human delegated resolution on 2026-10-05)
- [x] Q: How are IDs assigned and persisted? A: Start at 1, increase by 1, never reuse IDs after deletion, and persist `next_id`. (source: user-provided master prompt, Section 8; human delegated resolution on 2026-10-05)
- [x] Q: Should task data persist, and where? A: Yes; use `tasks.json` in the current working directory with the schema in FR-020. (source: user-provided master prompt, Section 8; human delegated resolution on 2026-10-05)
- [x] Q: What should happen for missing, empty, corrupt, or inaccessible storage? A: Missing/empty storage is an empty list; corrupt JSON, wrong types, or duplicate IDs raise `CorruptStorageError` without modifying bytes; other I/O failures raise `StorageError`. (source: user-provided master prompt, Section 8; human delegated resolution on 2026-10-05)
- [x] Q: Are there task-count limits or concurrency requirements? A: There are no task-count limits; concurrency behavior is unspecified, with no concurrent-writer guarantee. (source: user-provided master prompt, Section 8; human delegated resolution on 2026-10-05)
- [x] Q: What performance targets apply? A: None are specified; no performance threshold is added. (source: human delegation, 2026-10-05)