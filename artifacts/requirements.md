# Requirements

## Source

- Primary story: `user_story.md` — US-001 "Todo List Management" (fetched from Confluence page 12550145, 2026-10-21T19:37:30Z)
- Clarifications: human answers collected by the main session during the requirements phase on 2026-10-22 (see Open Questions for per-answer attribution)

## Functional Requirements

**FR-001 — Create a task.**
Given the user invokes the create-task operation with a non-empty title and an optional description, when the operation completes successfully, then one task record is persisted with the supplied title (surrounding whitespace trimmed), description (defaulting to empty string when omitted), status `pending`, and a unique auto-incrementing integer ID; a success message identifying the new task ID and title is produced.

- Acceptance: Given `title = "Buy milk"` and no description, when create runs, then a record with `id=1`, `title="Buy milk"`, `description=""`, `status="pending"` exists in storage and a success message is produced.
- Acceptance: Given `title = "  Buy milk  "`, when create runs, then the stored title is `"Buy milk"` (leading and trailing whitespace trimmed; internal whitespace preserved).

**FR-002 — Description field is optional.**
Given a user creates a task without supplying a description, when the task is stored, then the description field defaults to an empty string and the operation succeeds without error.

- Acceptance: Given only a title is provided, when create runs, then the stored description is `""`.

**FR-003 — View all tasks.**
Given one or more tasks exist, when the user invokes the list-all operation, then all tasks are produced in creation order (ascending ID order), each record showing its ID, title, description, and status.

- Acceptance: Given tasks with IDs 1 and 2 exist, when list-all runs, then both records appear with IDs 1 then 2.

**FR-004 — Empty task list.**
Given no tasks exist in storage, when the user invokes the list-all operation, then an appropriate message is produced indicating no tasks are present and no task records are shown.

- Acceptance: Given an empty (or absent) storage file, when list-all runs, then a "no tasks" message is produced and no task records appear.

**FR-005 — Filter tasks by status.**
Given the user invokes the list operation with a status filter of `completed` or `pending`, when the operation runs, then only tasks whose status matches the filter are produced in creation order; if no tasks match, an appropriate empty message is produced.

- Acceptance: Given tasks with statuses `[pending, completed, pending]`, when filtered by `completed`, then only the single completed task is produced.
- Acceptance: Given all tasks are `pending`, when filtered by `completed`, then an appropriate empty message is produced.

**FR-006 — Update task details.**
Given an existing task, when the user invokes the update operation supplying a new title, a new description, or both, then the specified fields are updated in storage (title trimmed of surrounding whitespace), the task ID and status are unchanged, and a success message is produced.

- Acceptance: Given task ID 1 exists, when update supplies a new title, then the stored title changes and the status and ID remain the same.
- Acceptance: Given an update supplies an empty or whitespace-only new title, when the operation runs, then it is rejected (see FR-013) and the stored record is unchanged.

**FR-007 — Delete a task.**
Given an existing task, when the user invokes the delete operation for that task's ID, then the task record is removed from storage and does not appear in any subsequent list operation.

- Acceptance: Given task ID 2 exists, when delete ID 2 runs, then ID 2 is absent from subsequent list results.

**FR-008 — Mark task as completed.**
Given a task with status `pending`, when the user invokes the mark-completed operation for that task's ID, then its status becomes `completed` and a success message is produced.

- Acceptance: Given task ID 1 has status `pending`, when mark-completed runs, then the stored status becomes `completed`.

**FR-009 — Mark already-completed task (idempotent guard).**
Given a task with status `completed`, when the user invokes the mark-completed operation for that task's ID, then an appropriate message indicating the task is already completed is produced, no data is modified, and the operation is treated as a non-error no-op.

- Acceptance: Given task ID 1 has status `completed`, when mark-completed runs again, then the stored record is unchanged and an informational message is produced.

**FR-010 — Mark task as pending.**
Given a task with status `completed`, when the user invokes the mark-pending operation for that task's ID, then its status becomes `pending` and a success message is produced.

- Acceptance: Given task ID 1 has status `completed`, when mark-pending runs, then the stored status becomes `pending`.

**FR-011 — Mark already-pending task (idempotent guard).**
Given a task with status `pending`, when the user invokes the mark-pending operation for that task's ID, then an appropriate message indicating the task is already pending is produced, no data is modified, and the operation is treated as a non-error no-op.

- Acceptance: Given task ID 1 has status `pending`, when mark-pending runs again, then the stored record is unchanged and an informational message is produced.

**FR-012 — Task not found error.**
Given any operation (update, delete, mark-completed, mark-pending) references a task ID that does not exist in storage, when the operation runs, then an appropriate error message is produced indicating the task was not found, no data is modified, and the operation is treated as an error condition.

- Acceptance: Given no task with ID 99 exists, when any task-specific operation targets ID 99, then an error message is produced and no records change.

**FR-013 — Reject empty or whitespace-only title.**
Given a create or update operation supplies a title that is empty or consists entirely of whitespace characters, when the operation is processed, then it is rejected with an error message, no task record is created or modified, and the operation is treated as an error condition.

- Acceptance: Given title = `"   "`, when create runs, then no task is created and an error message is produced.

**FR-014 — Duplicate titles allowed.**
Given an existing task has a particular title, when a new task is created with the same title, then creation succeeds and a distinct new task ID is assigned.

- Acceptance: Given a task with title `"Buy milk"` already exists, when create with title `"Buy milk"` runs, then a second distinct task record is created.

**FR-015 — Auto-incrementing, non-reused task IDs.**
Given tasks are created and some are later deleted, when subsequent tasks are created, then IDs start at 1, increase by exactly 1 per creation, are never reused after deletion, and the next available ID counter persists across process restarts.

- Acceptance: Given tasks 1 and 2 exist and task 2 is deleted, when a new task is created, then it receives ID 3, not 2.
- Acceptance: Given the application restarts after creating tasks, when a new task is created, then the ID continues from the last assigned value.

**FR-016 — File-based persistence.**
Given the application performs any task operation, when it reads or writes task data, then it uses a local JSON file on the filesystem; all task records (ID, title, description, status) and the next available ID counter are preserved in that file and survive process restarts.

- Acceptance: Given a task is created and the process is restarted, when list-all runs in a new process, then the task created in the prior process appears.

**FR-017 — Missing or empty storage file.**
Given the storage JSON file does not exist or contains no content, when a list or create operation runs, then the application treats this as an empty task list and proceeds without error.

- Acceptance: Given no storage file exists, when list-all runs, then the empty-list message (FR-004) is produced without an I/O error.

**FR-018 — Clear success and error messages for every operation.**
Given any operation completes (successfully or with an error condition), when the operation returns, then a human-readable success or error message is produced consistent with the behaviors defined in FR-001 through FR-017; no operation completes silently without feedback.

## Non-Functional Requirements

**NFR-001 — Runtime and dependencies.**
Given the application is run, then it requires Python 3.11 or newer and uses only the Python standard library; no third-party packages are required.

**NFR-002 — Storage encoding.**
Given task data is serialized to the JSON file, then the file is written using UTF-8 encoding; task titles and descriptions containing non-ASCII characters are preserved correctly.

**NFR-003 — No network calls or secrets.**
Given the application runs, then it makes no network calls and does not require, expose, transmit, or persist credentials, tokens, or secrets of any kind.

**NFR-004 — Testability.**
Given automated tests are executed, then they use the `unittest` framework, each FR defined above has at least one test case that cites the corresponding FR ID in its name or docstring, and tests use temporary directories to avoid modifying the user's working environment.

## Constraints

- The application manages a personal todo list; interaction is through a command-line interface.
- Valid task status values are exactly `pending` (initial state on creation) and `completed`.
- Task description defaults to an empty string when not supplied at creation.
- Task IDs are positive integers assigned auto-incrementally starting at 1.
- Persistence uses a single local JSON file; the exact filename and path are a design decision deferred to the architecture phase.
- No concurrent-access guarantee is defined; behavior under simultaneous writes from multiple processes is unspecified.
- No measurable performance target is specified by the source material.
- No upper limit on task count or title length is specified by the source material.

## Assumptions

- "Clear success or error messages" in the acceptance criteria means each operation produces a human-readable confirmation or error statement; the exact wording of those messages is a design decision deferred to later phases.
- "Update task details" (acceptance criterion) covers updating the title, description, or both. Status changes are handled exclusively by the dedicated mark-completed (FR-008) and mark-pending (FR-010) operations; the update operation does not modify status.
- Tasks are produced in creation order (ascending ID order) when listed, as no alternative ordering is specified by the source material.
- A missing storage file and a storage file with no content are both treated equivalently as an empty task list (FR-017).
- The idempotent no-op responses in FR-009 and FR-011 are informational, not error conditions; they do not cause a non-zero exit code.

## Open Questions

- [x] Q: Should task data persist between application runs, and where should it be stored? A: Yes — file-based persistence using a local JSON file; tasks survive process restarts. (source: human clarification 1, 2026-10-22)
- [x] Q: Is the description field required when creating a task? A: No — description is optional; it defaults to an empty string when omitted. (source: human clarification 2, 2026-10-22)
- [x] Q: Should the list operation support filtering by status? A: Yes — filter by `completed` or `pending` is supported in addition to listing all tasks. (source: human clarification 3, 2026-10-22)
- [x] Q: How are task IDs assigned and do they persist? A: Auto-incrementing integers starting at 1; IDs are never reused after deletion and the counter persists across process restarts. (source: human clarification 4, 2026-10-22)
- [x] Q: What are the valid task status values? A: `pending` (initial state) and `completed`, as stated directly in the acceptance criteria of US-001. (source: user_story.md, US-001)
- [x] Q: Should empty or whitespace-only titles be rejected? A: Yes — rejecting empty or whitespace-only titles avoids creating meaningless records; no contradicting instruction appears in the source material. (source: bounded from source material; no title-length upper bound specified)
- [x] Q: Are duplicate task titles allowed? A: Yes — the source material imposes no uniqueness constraint on titles; creation with a duplicate title succeeds and receives a distinct ID. (source: user_story.md does not forbid duplicates)
- [x] Q: In what order are tasks produced when listed? A: Creation order (ascending ID order); no alternative ordering is specified by the source material. (source: not specified by source material; defaulted to creation order)
- [x] Q: What concurrency behavior applies? A: No concurrent-writer guarantee is defined; behavior under simultaneous writes from multiple processes is unspecified. (source: not specified by source material)
- [x] Q: What performance targets apply? A: None — no measurable performance threshold is specified by the source material. (source: not specified by source material)
