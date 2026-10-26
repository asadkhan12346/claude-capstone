# Requirements

## Source

- User story: NOTE-101 (`user_story.md`) — "As a user, I want to create, view, update, and delete notes so that I can keep track of important information."
- Human answer 1: Interface is a CLI (command-line interface).
- Human answer 2: Persistence is a local JSON file (`notes.json`).
- Human answer 3: Note IDs are auto-increment integers assigned automatically; both title and content are required (non-empty) to create a note.
- Human answer 4: Update is a full replace — both title and content must be supplied on every update call.

## Functional Requirements

**FR-001 — Create note**
A user must be able to create a new note by supplying a non-empty title and non-empty content. The system assigns the note a unique auto-increment integer ID and persists it.

- Given a user provides a non-empty title and non-empty content,
- When the create command is executed,
- Then a new note with a unique integer ID is saved and its ID is reported to the user.

**FR-002 — View all notes**
A user must be able to retrieve and display all saved notes.

- Given at least zero notes exist,
- When the list command is executed,
- Then all notes (ID, title, content) are displayed; if no notes exist, an empty-list indication is shown.

**FR-003 — View note by ID**
A user must be able to retrieve a single note by its integer ID.

- Given a note with a specific ID exists,
- When the view command is executed with that ID,
- Then the note's ID, title, and content are displayed.

**FR-004 — Update note**
A user must be able to replace the title and content of an existing note by its ID. Both title and content must be supplied; neither may be empty. The update is a full replace.

- Given a note with a specific ID exists and the user supplies a non-empty title and non-empty content,
- When the update command is executed with that ID,
- Then the note's title and content are replaced and the change is persisted.

**FR-005 — Delete note**
A user must be able to delete a note by its integer ID.

- Given a note with a specific ID exists,
- When the delete command is executed with that ID,
- Then the note is removed from storage and a confirmation is shown.

**FR-006 — Error on non-existent note**
When a view, update, or delete command references an ID that does not exist, the system must return an error message indicating the note was not found; it must not modify any data.

- Given no note exists with the supplied ID,
- When a view, update, or delete command is executed with that ID,
- Then an error message is returned and no data is changed.

**FR-007 — Invalid input rejection**
When a create or update command is issued with an empty title or empty content, the system must reject the input with an error message and must not create or modify any note.

- Given a user supplies an empty title or empty content,
- When the create or update command is executed,
- Then an error message is returned and no note is created or modified.

## Non-Functional Requirements

**NFR-001 — JSON persistence**
All notes must be persisted in a local JSON file (`notes.json`). The file must be created automatically if it does not exist. Data must survive process restarts.

**NFR-002 — CLI interface**
All operations must be accessible via a command-line interface. Each CRUD operation must be reachable as a distinct subcommand or flag combination.

**NFR-003 — Auto-increment integer IDs**
Note IDs must be non-negative integers assigned automatically by the system in monotonically increasing order. The system must not reuse an ID after a note is deleted.

**NFR-004 — Automated test coverage**
The implementation must be accompanied by automated tests that exercise every functional requirement (FR-001 through FR-007) and that all pass without error.

**NFR-005 — Informative error messages**
Error messages must identify the nature of the failure (e.g., "Note not found", "Title must not be empty") so the user can correct the input without consulting additional documentation.

**NFR-006 — README documentation**
The repository must include a README that documents setup instructions and usage examples for every CLI operation.

## Constraints

- Interface: command-line only; no web server or API endpoint.
- Persistence mechanism: a single local JSON file; no external database or network storage.
- ID scheme: auto-increment integers; no UUIDs or user-supplied IDs.
- Update semantics: full replace only; partial (patch) updates are out of scope.

## Assumptions

- The `notes.json` file is created in the working directory at first write if it does not already exist.
- IDs are never reused after deletion (the counter only increments).
- Concurrent access by multiple processes is out of scope.
- The title and content fields are plain text strings; no rich-text or attachment support is required.
- No authentication or authorization is required.

## Open Questions

- [x] What interface should be used? — CLI (command-line interface). *(Human answer 1)*
- [x] How should notes be persisted? — Local JSON file (`notes.json`). *(Human answer 2)*
- [x] How are note IDs assigned, and what fields are required to create a note? — Auto-increment integers assigned automatically; both title and content are required (non-empty). *(Human answer 3)*
- [x] What does updating a note mean — full replace or partial update? — Full replace; both title and content must be supplied on every update call. *(Human answer 4)*
