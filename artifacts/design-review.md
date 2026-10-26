# Design Review

## Summary

This review evaluates the architecture for the Notes CLI against `artifacts/requirements.md` (FR-001 – FR-007, NFR-001 – NFR-006) and the user story NOTE-101. The three-module Python package design is structurally sound and cleanly separates CLI, domain logic, and storage. Seven out of thirteen requirements are well-addressed; however, four medium findings and three low findings were raised, including one uncovered requirement (NFR-006 README ownership is unassigned in the pipeline) that requires revision before proceeding to planning.

---

## Findings

| ID | Severity | Area | Finding | Related IDs | Suggested Change |
|----|----------|------|---------|-------------|-----------------|
| F-01 | Med | Persistence | `_save` is described as performing an "atomic write" but no mechanism is specified. Without a write-to-tempfile-then-rename (`os.replace`) pattern, a process interruption mid-write silently corrupts `notes.json` and permanently destroys all stored data. | NFR-001 | Specify `_save` as: write to `<path>.tmp`, flush, then `os.replace("<path>.tmp", path)`. Callers cannot detect the corruption without this guarantee. |
| F-02 | Med | Error Handling | Corrupt JSON propagates as an unhandled `json.JSONDecodeError` Python traceback. The architecture labels this "out of scope per constraints" but the constraints only exclude network/database storage — they do not exclude error reporting for malformed files. The user receives no actionable message. | NFR-001, NFR-005 | Add a `try/except json.JSONDecodeError` in `_load`; raise a new `StorageError(NoteError)` with a message like `"notes.json is corrupt; delete or repair the file."` |
| F-03 | Med | Test Coverage | The test strategy explicitly excludes CLI-layer testing. FR-002 requires "an empty-list indication is shown" and FR-005 requires "a confirmation is shown" — both are presentation behaviors implemented exclusively in `cli.py` that cannot be verified by calling app functions directly. NFR-004 mandates tests that exercise every functional requirement. | NFR-004, FR-002, FR-005 | Add a small set of subprocess or `argparse`-based CLI integration tests for the empty-list path (FR-002) and delete-confirmation path (FR-005), or explicitly document in the architecture that these display strings are verified by inspection only and accepted as a known gap. |
| F-04 | Med | Requirement Coverage | NFR-006 requires a README with setup instructions and usage examples for every CLI operation. The architecture defers this as "owned outside this phase" without specifying which phase, agent, or file assumes ownership. Inspection of `sdlc/phases.json` confirms no phase lists `README.md` in its `owns` array. The acceptance criteria of NOTE-101 also lists "README includes setup and usage instructions." This is an uncovered requirement. | NFR-006, NOTE-101 | Assign README.md ownership to a named phase (e.g., implementation or pr). If the planning phase creates an implementation plan, it can task the implementation agent to write `README.md`. Alternatively, add `README.md` to the implementation phase `owns` list in `sdlc/phases.json`. |
| F-05 | Low | Validation | The architecture states `ValidationError` is raised for "empty title or content" but does not specify that `.strip()` is applied before the emptiness check. A title of `"   "` (whitespace only) passes `if not title` as `True`, allowing a note with a blank-looking title. The intent of FR-007 and NFR-005 covers this case by implication. | FR-007, NFR-005 | Explicitly specify in the architecture that validation uses `if not title.strip()` (and equivalently for content) so the implementation is unambiguous. |
| F-06 | Low | CLI UX | When a user passes a non-integer to `--id` (e.g., `notes view --id abc`), argparse emits a generic error: `argument --id: invalid int value: 'abc'`. This is acceptable but the architecture does not specify the exact format, leaving NFR-005 compliance for this case implicit. | NFR-005 | Document that argparse's built-in type error for `--id` is accepted as satisfying NFR-005, or customize the `type=` callable to emit a friendlier message. |
| F-07 | Low | Packaging | The architecture mentions `console_scripts` as an entry point option for `main()` but references no `setup.py`, `pyproject.toml`, or equivalent. Without a packaging manifest the entry point cannot be registered, and NFR-006's "setup instructions" cannot include `pip install -e .` or an equivalent install step. | NFR-006 | Either specify that `python -m notes.cli` is the sole supported invocation (and document this) or add a minimal `pyproject.toml` to the list of files the implementation phase creates. |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Silent data loss on interrupted write (F-01) | Low on fast local disk; non-trivial on NFS or if process is killed mid-write | High — all notes destroyed | Atomic rename pattern in `_save` |
| NFR-006 README never written (F-04) | High — no phase owns it | Med — pipeline passes but acceptance criterion of NOTE-101 is unmet | Explicit phase ownership assignment |
| Corrupt file renders tool unusable permanently (F-02) | Low | Med — user data inaccessible until manual repair | Catch `json.JSONDecodeError` in `_load` |
| CLI presentation behaviors undetected during testing (F-03) | Med | Low — app logic works; display regressions could go unnoticed | Minimal CLI integration tests |

---

## Alternatives Considered and Why Rejected

### Alternative A: SQLite via `sqlite3` (stdlib) instead of JSON flat file

**Pros:**
- Transactional writes guarantee atomicity without a manual temp-file pattern (addresses F-01 directly).
- Built-in concurrent read support (though concurrency is out of scope).
- Schema-enforced integer IDs and non-null constraints replace hand-coded validation.
- Better performance for large note collections.

**Cons:**
- NFR-001 and Human answer 2 explicitly mandate a JSON file. This alternative is not permitted by the approved requirements.
- Binary format is not human-inspectable with a text editor, reducing debuggability.
- `sqlite3` API is more verbose than `json.load`/`json.dump` for a five-operation CRUD tool.

**Decision:** Correctly rejected. Constraints prohibit any storage mechanism other than a local JSON file.

---

### Alternative B: Separate `notes/storage.py` module for file I/O, leaving `notes/app.py` for domain logic only

**Pros:**
- Cleaner separation of concerns; domain logic and storage are independently testable.
- Swapping the storage backend (e.g., switching from JSON to SQLite in a future story) requires only replacing `storage.py`, not touching domain logic.
- Easier to mock storage in unit tests without `tempfile`.

**Cons:**
- The implementation phase owns exactly four files (`notes/__init__.py`, `notes/app.py`, `notes/cli.py`, `tests/test_notes.py`). Adding `notes/storage.py` would require a pipeline contract change.
- For a five-operation CRUD application the split provides marginal benefit; storage and domain logic are tightly coupled in this scope.
- The `storage_path` dependency injection parameter already enables test isolation without a separate module.

**Decision:** Reasonable rejection given the file-count constraint. The `storage_path` parameter achieves the primary testing goal without adding a new file. Revisit if the application grows.

---

### Alternative C: `click` library for CLI instead of `argparse`

**Pros:**
- More concise command and argument declarations.
- Automatic help text with coloring and better formatting out of the box.
- Decorator-based API reduces boilerplate.

**Cons:**
- `click` is a third-party dependency; CLAUDE.md and the constraints prohibit external dependencies — "standard library only."
- `argparse` already satisfies NFR-002 (distinct subcommands) and NFR-005 (help text per subcommand) without any additional dependency.

**Decision:** Correctly rejected. Standard library constraint is binding.

---

## Security Review

**Threat surface:** Local process, local file, no network, no authentication required (per requirements).

| Threat | Analysis | Verdict |
|--------|----------|---------|
| Path traversal via `storage_path` | The CLI does not expose `storage_path` as a flag; the parameter is internal, defaulting to `"notes.json"` in the CWD. An attacker with local shell access could pass an arbitrary path only by modifying source code, not by normal CLI usage. | Acceptable — not exploitable via published interface. |
| Symlink attack on `notes.json` | If `notes.json` is a symlink to another file, `_save` will overwrite the target. Relevant only if an attacker can plant a symlink before the first write. On a single-user workstation this is an acceptable residual risk. | Low risk — no mitigation required for scope. |
| Malformed/crafted JSON in `notes.json` | `json.load` never calls `eval` or `exec`; parsing untrusted JSON is safe from injection. A crafted file can cause `json.JSONDecodeError` (covered in F-02) but not code execution. | Safe. Add `StorageError` per F-02 recommendation for user-facing resilience. |
| Secrets or credentials | The data model stores only user-authored plain-text titles and content. No authentication tokens, passwords, or API keys are defined. | No concern. |
| Unbounded file growth | There is no maximum note count or content-size limit. A `notes.json` with millions of entries would be loaded into memory on every operation. Acceptable for a personal local CLI. | Low risk — out of scope. |

**Overall security posture:** Appropriate for the stated scope (local CLI, single user, no network). No critical security issues identified.

---

## Usability and Accessibility Review

**Strengths:**

- The five subcommands (`create`, `list`, `view`, `update`, `delete`) are named with common English verbs, consistent with user expectations (NFR-002).
- `argparse` subparsers automatically generate per-subcommand `--help` text, satisfying discoverability without additional implementation effort.
- Named `--title`, `--content`, `--id` flags are self-documenting at the shell prompt.
- Errors route to stderr with exit code 1 (domain errors) or 2 (usage errors), following POSIX conventions and supporting shell scripting.
- NFR-005 message examples ("Note not found", "Title must not be empty") are specific and actionable without consulting documentation.
- FR-002 includes an empty-list indication, preventing silent no-output confusion.
- FR-005 specifies a confirmation message on delete, preventing silent success ambiguity.

**Weaknesses / concerns:**

- The `view` subcommand uses `--id INT` rather than a positional argument. Positional arguments (`notes view 3`) are more ergonomic for frequent single-argument commands. This is a minor UX preference and not a requirement violation.
- No output formatting (columns, separators) is specified for the `list` subcommand. With many notes, the output could be visually difficult to parse. Acceptable at this scope; worth documenting as a known limitation.
- No paging or truncation is defined for `list` with a large note set. Acceptable for a personal local CLI.
- The whitespace-only validation gap (F-05) could produce confusing notes visible in list output as blank titles.
- No color, no terminal width adaptation, no accessibility-specific formatting defined. These are out of scope for a plain-text local CLI and acceptable per the constraints.

**Accessibility:** A text-based CLI with plain-text stdout/stderr output is inherently compatible with screen readers and terminal assistive technologies. No accessibility concerns specific to this design.

---

## Requirement Coverage Check

| Requirement | Architecture Coverage | Status |
|-------------|----------------------|--------|
| FR-001 Create note | `create_note` in `app.py`; `create` subcommand in `cli.py` | Covered |
| FR-002 View all notes | `list_notes` in `app.py`; `list` subcommand with empty-list indication in `cli.py` | Covered — presentation layer test gap noted (F-03) |
| FR-003 View note by ID | `get_note` in `app.py`; `view` subcommand in `cli.py` | Covered |
| FR-004 Update note | `update_note` in `app.py`; `update` subcommand in `cli.py`; full-replace semantics match Human answer 4 | Covered |
| FR-005 Delete note | `delete_note` in `app.py`; `delete` subcommand in `cli.py`; confirmation message specified | Covered — presentation layer test gap noted (F-03) |
| FR-006 Error on non-existent note | `NoteNotFoundError` raised in `get_note`, `update_note`, `delete_note`; caught in CLI; no data mutation before error | Covered |
| FR-007 Invalid input rejection | `ValidationError` raised at top of `create_note`, `update_note`; whitespace-only ambiguity noted (F-05) | Covered with caveat |
| NFR-001 JSON persistence | `_load`/`_save` in `app.py`; auto-created on first write; `next_id` survives restarts | Covered — atomicity unspecified (F-01), corrupt file unhandled (F-02) |
| NFR-002 CLI interface | `argparse` subparsers: `create`, `list`, `view`, `update`, `delete` | Covered |
| NFR-003 Auto-increment IDs | `next_id` field persisted in JSON; incremented on create, never decremented | Covered |
| NFR-004 Automated tests | `tests/test_notes.py` with `unittest` and `tempfile` isolation | Covered with gap — CLI presentation untested (F-03) |
| NFR-005 Informative error messages | `NoteNotFoundError` and `ValidationError` carry descriptive messages; stderr + exit 1 in CLI | Covered — corrupt-file message missing (F-02) |
| NFR-006 README documentation | Architecture defers to "outside this phase"; no phase in `sdlc/phases.json` owns `README.md` | **UNCOVERED** (F-04) |

---

Verdict: REVISE
