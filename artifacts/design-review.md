# Design Review

## Summary

The architecture has a clear CLI/application/storage separation within the contract's four implementation files, and its requirement coverage table includes every FR and NFR. The data flow and atomic-write outline are coherent. However, one High data-integrity gap can violate FR-024, and free-text rendering needs an explicit boundary to avoid ambiguous or misleading list output. The verdict is REVISE until the High finding is resolved.

## Findings

| ID | Severity | Area | Finding | Related IDs | Suggested change |
|---|---|---|---|---|---|
| F-01 | High | ID integrity | The design allocates IDs from persisted `next_id` but does not state that it validates the counter against stored task IDs. A type-valid file with `next_id` less than or equal to an existing ID can make the next add reuse an ID or collide, violating the never-reuse and uniqueness behavior. | FR-018, FR-020, FR-022, FR-024 | Require storage validation that `next_id` is a positive integer greater than every stored ID; reject an inconsistent file as corrupt without modifying its bytes, or obtain an explicit human decision for another non-reuse-preserving policy. Add a focused acceptance criterion before implementation. |
| F-02 | Med | Free-text output | The architecture displays titles in one-record-per-line output but does not define treatment of embedded newlines or terminal control characters. A title containing them can split a task across lines or make terminal output misleading, despite the list format. | FR-005, FR-017, FR-020 | Clarify title behavior for line breaks/control characters with the human. Keep stored title fidelity distinct from presentation; specify escaping or rejection only after the requirement decision. Add tests for the chosen display behavior. |

## Risks

- If F-01 is not resolved, malformed-but-parseable storage can break the identity guarantee and make updates target an ambiguous record.
- If F-02 is not resolved, list output may be difficult to scan or spoof visually when titles contain control characters.
- Concurrent writers have no specified guarantee. The architecture appropriately makes no locking or concurrency promise, but concurrent changes could overwrite one another if users run multiple processes; this remains an explicit limitation rather than a design defect against current requirements.
- Same-directory temporary replacement improves atomicity, but filesystem and platform behavior should be exercised by the implementation tests.

## Alternatives considered and why rejected

1. **Put parsing, task rules, persistence, and printing in one CLI module.** Rejected because it would couple domain logic to terminal I/O and argv handling, contradicting the approved application-layer boundary and making injected-stream tests harder (FR-001, FR-015, NFR-006).
2. **Create a separate storage module.** Rejected for this story because the contract explicitly restricts the implementation to `todo/__init__.py`, `todo/app.py`, `todo/cli.py`, and `tests/test_todo.py`. A private storage boundary inside `todo/app.py` preserves responsibility separation without adding an unowned file (FR-020 through FR-024).
3. **Use an embedded database instead of JSON.** Rejected because the approved storage contract specifies `tasks.json`, its schema, and serialization behavior; substituting another persistence format would violate FR-020 and NFR-002.

## Security review

The design stays local, uses no network services, and does not require secrets (NFR-005). Atomic replacement and preserving corrupt input bytes are good safeguards (FR-022, NFR-003). The design should validate all loaded fields and IDs before mutation, including the `next_id` relationship identified in F-01. Because titles are free text, the CLI should not interpret title contents as terminal control instructions; F-02 asks for a requirements-backed presentation policy. The current artifact does not claim protection from concurrent writers or hostile filesystem manipulation.

## Usability and accessibility review

The text CLI has a small, predictable command set, explicit stdout/stderr behavior, and stable status labels, which supports scanning and scripting (FR-001, FR-004 through FR-015). Empty-list and no-op messages are specified. Error messages identify the missing task ID. F-02 needs a human decision so unusual free-text titles remain understandable without breaking the one-task-per-line view. No color-only status signaling is proposed, which avoids making task state depend on color perception.

## Requirement coverage check

The architecture's coverage table contains every approved requirement: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, FR-015, FR-016, FR-017, FR-018, FR-019, FR-020, FR-021, FR-022, FR-023, FR-024, NFR-001, NFR-002, NFR-003, NFR-004, NFR-005, and NFR-006. Coverage is present, but FR-024 is not yet fully protected against an inconsistent persisted `next_id` (F-01), and FR-005 with FR-017 leaves multiline display behavior unresolved (F-02).

Verdict: REVISE