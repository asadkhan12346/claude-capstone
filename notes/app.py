"""Notes application — domain logic and storage helpers.

Covers T-01 (exception hierarchy), T-02 (storage helpers), T-03 (CRUD functions).
"""

from __future__ import annotations

import json
import os


# ---------------------------------------------------------------------------
# T-01: Exception hierarchy
# ---------------------------------------------------------------------------


class NoteError(Exception):
    """Base class for all notes domain errors (FR-006, FR-007, NFR-005)."""


class NoteNotFoundError(NoteError):
    """Raised when a note with the requested ID does not exist (FR-006)."""


class ValidationError(NoteError):
    """Raised when title or content is empty or whitespace-only (FR-007)."""


class StorageError(NoteError):
    """Raised when the notes.json file contains corrupt / unreadable data (F-02)."""


# ---------------------------------------------------------------------------
# T-02: Storage helpers
# ---------------------------------------------------------------------------


def _load(storage_path: str) -> dict:
    """Load notes data from *storage_path*.

    Returns ``{"next_id": 1, "notes": []}`` when the file does not exist.
    Raises :class:`StorageError` when the file exists but contains invalid JSON.

    Args:
        storage_path: Filesystem path to the JSON store.

    Returns:
        The parsed data dictionary.
    """
    try:
        with open(storage_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {"next_id": 1, "notes": []}
    except json.JSONDecodeError as exc:
        raise StorageError(
            "notes.json is corrupt; delete or repair the file."
        ) from exc


def _save(data: dict, storage_path: str) -> None:
    """Atomically persist *data* to *storage_path* (F-01).

    Writes to ``<storage_path>.tmp``, flushes and fsyncs, then replaces the
    target with ``os.replace`` so the write is atomic on POSIX and Windows.

    Args:
        data: The data dictionary to serialise.
        storage_path: Destination JSON file path.
    """
    tmp_path = storage_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp_path, storage_path)


# ---------------------------------------------------------------------------
# T-03: Public application functions
# ---------------------------------------------------------------------------


def create_note(
    title: str,
    content: str,
    storage_path: str = "notes.json",
) -> dict:
    """Create a new note, assign it an auto-increment ID, and persist it.

    Raises :class:`ValidationError` if *title* or *content* is empty or
    whitespace-only (FR-007, F-05).

    Args:
        title: Non-empty note title.
        content: Non-empty note body.
        storage_path: Path to the JSON store.

    Returns:
        The newly created note dict with ``"id"``, ``"title"``, ``"content"``.
    """
    if not title.strip():
        raise ValidationError("Title must not be empty.")
    if not content.strip():
        raise ValidationError("Content must not be empty.")

    data = _load(storage_path)
    note: dict = {
        "id": data["next_id"],
        "title": title,
        "content": content,
    }
    data["next_id"] += 1
    data["notes"].append(note)
    _save(data, storage_path)
    return note


def list_notes(storage_path: str = "notes.json") -> list[dict]:
    """Return all notes as a list; returns ``[]`` when no notes exist (FR-002).

    Args:
        storage_path: Path to the JSON store.

    Returns:
        List of note dicts, possibly empty.
    """
    data = _load(storage_path)
    return data["notes"]


def get_note(
    note_id: int,
    storage_path: str = "notes.json",
) -> dict:
    """Return the note whose ``"id"`` equals *note_id* (FR-003).

    Raises :class:`NoteNotFoundError` if no such note exists (FR-006).

    Args:
        note_id: The integer ID to look up.
        storage_path: Path to the JSON store.

    Returns:
        The matching note dict.
    """
    data = _load(storage_path)
    for note in data["notes"]:
        if note["id"] == note_id:
            return note
    raise NoteNotFoundError(f"Note not found: {note_id}")


def update_note(
    note_id: int,
    title: str,
    content: str,
    storage_path: str = "notes.json",
) -> dict:
    """Replace the title and content of an existing note (FR-004, full replace).

    Validation runs before the lookup so no data is mutated on invalid input.
    Raises :class:`ValidationError` for empty/whitespace inputs (FR-007, F-05).
    Raises :class:`NoteNotFoundError` if *note_id* does not exist (FR-006).

    Args:
        note_id: ID of the note to update.
        title: New title (non-empty).
        content: New content (non-empty).
        storage_path: Path to the JSON store.

    Returns:
        The updated note dict.
    """
    if not title.strip():
        raise ValidationError("Title must not be empty.")
    if not content.strip():
        raise ValidationError("Content must not be empty.")

    data = _load(storage_path)
    for index, note in enumerate(data["notes"]):
        if note["id"] == note_id:
            updated: dict = {"id": note_id, "title": title, "content": content}
            data["notes"][index] = updated
            _save(data, storage_path)
            return updated
    raise NoteNotFoundError(f"Note not found: {note_id}")


def delete_note(
    note_id: int,
    storage_path: str = "notes.json",
) -> None:
    """Remove the note with *note_id* from storage (FR-005).

    ``next_id`` is never decremented so IDs are not reused (NFR-003).
    Raises :class:`NoteNotFoundError` if *note_id* does not exist (FR-006).

    Args:
        note_id: ID of the note to delete.
        storage_path: Path to the JSON store.
    """
    data = _load(storage_path)
    for index, note in enumerate(data["notes"]):
        if note["id"] == note_id:
            data["notes"].pop(index)
            _save(data, storage_path)
            return
    raise NoteNotFoundError(f"Note not found: {note_id}")
