"""
todo.app — Application layer: all business logic and storage I/O.

Standard library only; requires Python 3.11+ (NFR-001).
No network calls or secrets (NFR-003).
"""

import json
import os
import pathlib
from typing import Any


class StorageError(Exception):
    """Raised by load() and save() on unrecoverable storage errors (F-04)."""


# ---------------------------------------------------------------------------
# Storage layer (FR-016, FR-017, NFR-002, F-02, F-04)
# ---------------------------------------------------------------------------


def load(path: pathlib.Path) -> dict:
    """
    Load task data from *path* (FR-016, FR-017, NFR-002, F-04).

    - Missing file          → returns fresh ``{"next_id": 1, "tasks": []}`` (FR-017).
    - Empty / whitespace    → returns fresh ``{"next_id": 1, "tasks": []}`` (FR-017).
    - Valid JSON            → returns the parsed dict.
    - Malformed JSON        → raises :exc:`StorageError` (F-04).
    - Unexpected OSError    → raises :exc:`StorageError` (F-04).

    The file is read with UTF-8 encoding (NFR-002).
    A fresh dict is returned each time to prevent accidental mutation of shared state.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"next_id": 1, "tasks": []}
    except OSError as exc:
        raise StorageError(str(exc)) from exc

    if not text.strip():
        return {"next_id": 1, "tasks": []}

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise StorageError(
            f"Storage file contains malformed JSON: {path}"
        ) from exc


def save(path: pathlib.Path, data: dict) -> None:
    """
    Write *data* to *path* atomically via a temp file + ``os.replace()`` (F-02, NFR-002).

    Steps:
    1. Ensure parent directory exists.
    2. Write to ``<path>.tmp``.
    3. Atomically rename to *path* with ``os.replace()``.

    Raises :exc:`StorageError` on any :exc:`OSError`; the temp file is cleaned up.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = pathlib.Path(str(path) + ".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except OSError as exc:
        tmp_path.unlink(missing_ok=True)
        raise StorageError(str(exc)) from exc


# ---------------------------------------------------------------------------
# Business logic — task operations
# ---------------------------------------------------------------------------


def create_task(
    storage_path: pathlib.Path,
    title: str,
    description: str = "",
) -> dict:
    """
    Create a new task (FR-001, FR-002, FR-013, FR-014, FR-015).

    The title is stripped of surrounding whitespace; an empty or whitespace-only
    title is rejected before any storage access (FR-013).
    Duplicate titles are permitted (FR-014).
    The ``next_id`` counter is read, used, and incremented atomically (FR-015).

    Returns ``{"success": bool, "message": str, "task": dict | None}``.
    """
    stripped_title = title.strip()
    if not stripped_title:
        return {"success": False, "message": "Title cannot be empty.", "task": None}

    try:
        data = load(storage_path)
        task_id: int = data["next_id"]
        task: dict[str, Any] = {
            "id": task_id,
            "title": stripped_title,
            "description": description,
            "status": "pending",
        }
        data["tasks"].append(task)
        data["next_id"] += 1
        save(storage_path, data)
    except StorageError as exc:
        return {"success": False, "message": str(exc), "task": None}

    return {
        "success": True,
        "message": f"Task {task_id} created: '{stripped_title}'.",
        "task": task,
    }


def list_tasks(
    storage_path: pathlib.Path,
    status_filter: str | None = None,
) -> dict:
    """
    Return all tasks in creation order with an optional status filter (FR-003, FR-004, FR-005, F-06).

    Returns ``{"success": bool, "message": str, "tasks": list[dict]}``.
    The ``"tasks"`` key is always present and always a ``list`` (F-06).
    """
    try:
        data = load(storage_path)
    except StorageError as exc:
        return {"success": False, "message": str(exc), "tasks": []}

    tasks: list[dict] = list(data["tasks"])

    if status_filter is not None:
        tasks = [t for t in tasks if t["status"] == status_filter]

    if not tasks:
        return {"success": True, "message": "No tasks found.", "tasks": []}

    return {
        "success": True,
        "message": f"{len(tasks)} task(s) found.",
        "tasks": tasks,
    }


def update_task(
    storage_path: pathlib.Path,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
) -> dict:
    """
    Update title and/or description of an existing task (FR-006, FR-012, FR-013, F-03).

    ``None`` for *title* or *description* means "do not change this field" (F-03).
    An empty string is a valid description value (F-03).
    The task's ``id`` and ``status`` are never modified by this function (FR-006).

    Returns ``{"success": bool, "message": str}``.
    """
    if title is None and description is None:
        return {
            "success": False,
            "message": "At least one of title or description must be provided.",
        }

    stripped_title: str | None = None
    if title is not None:
        stripped_title = title.strip()
        if not stripped_title:
            return {"success": False, "message": "Title cannot be empty."}

    try:
        data = load(storage_path)
        task: dict | None = next(
            (t for t in data["tasks"] if t["id"] == task_id), None
        )
        if task is None:
            return {"success": False, "message": f"Task {task_id} not found."}

        if stripped_title is not None:
            task["title"] = stripped_title
        if description is not None:
            task["description"] = description

        save(storage_path, data)
    except StorageError as exc:
        return {"success": False, "message": str(exc)}

    return {"success": True, "message": f"Task {task_id} updated."}


def delete_task(
    storage_path: pathlib.Path,
    task_id: int,
) -> dict:
    """
    Remove a task by ID from storage (FR-007, FR-012).

    The ``next_id`` counter is not decremented; IDs are never reused (FR-015).

    Returns ``{"success": bool, "message": str}``.
    """
    try:
        data = load(storage_path)
        task: dict | None = next(
            (t for t in data["tasks"] if t["id"] == task_id), None
        )
        if task is None:
            return {"success": False, "message": f"Task {task_id} not found."}

        data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
        save(storage_path, data)
    except StorageError as exc:
        return {"success": False, "message": str(exc)}

    return {"success": True, "message": f"Task {task_id} deleted."}


def mark_completed(
    storage_path: pathlib.Path,
    task_id: int,
) -> dict:
    """
    Set task status to ``"completed"`` (FR-008, FR-009, FR-012).

    If the task is already completed, returns an informational result without
    writing to storage (FR-009, idempotent no-op).

    Returns ``{"success": bool, "message": str}``; the idempotent case also
    includes ``"already_set": True``.
    """
    try:
        data = load(storage_path)
        task: dict | None = next(
            (t for t in data["tasks"] if t["id"] == task_id), None
        )
        if task is None:
            return {"success": False, "message": f"Task {task_id} not found."}

        if task["status"] == "completed":
            return {
                "success": True,
                "message": f"Task {task_id} is already completed.",
                "already_set": True,
            }

        task["status"] = "completed"
        save(storage_path, data)
    except StorageError as exc:
        return {"success": False, "message": str(exc)}

    return {"success": True, "message": f"Task {task_id} marked as completed."}


def mark_pending(
    storage_path: pathlib.Path,
    task_id: int,
) -> dict:
    """
    Set task status to ``"pending"`` (FR-010, FR-011, FR-012).

    If the task is already pending, returns an informational result without
    writing to storage (FR-011, idempotent no-op).

    Returns ``{"success": bool, "message": str}``; the idempotent case also
    includes ``"already_set": True``.
    """
    try:
        data = load(storage_path)
        task: dict | None = next(
            (t for t in data["tasks"] if t["id"] == task_id), None
        )
        if task is None:
            return {"success": False, "message": f"Task {task_id} not found."}

        if task["status"] == "pending":
            return {
                "success": True,
                "message": f"Task {task_id} is already pending.",
                "already_set": True,
            }

        task["status"] = "pending"
        save(storage_path, data)
    except StorageError as exc:
        return {"success": False, "message": str(exc)}

    return {"success": True, "message": f"Task {task_id} marked as pending."}
