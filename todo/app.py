"""Todo domain operations and local JSON persistence."""

from __future__ import annotations

import json
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class TodoError(Exception):
    """Base class for expected Todo application errors."""


class EmptyTitleError(TodoError):
    """A task title is empty after surrounding whitespace is removed."""


class InvalidTitleError(TodoError):
    """A task title is not text."""


class TaskNotFoundError(TodoError):
    """A requested task ID is invalid or does not exist."""

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(task_id)


class StorageError(TodoError):
    """Task storage could not be read or written."""


class CorruptStorageError(TodoError):
    """Task storage has invalid JSON or an invalid persisted schema."""


@dataclass(frozen=True)
class Task:
    """One persisted task."""

    id: int
    title: str
    status: str


class TodoApp:
    """Manage tasks stored in a JSON file in the current directory."""

    def __init__(self, storage_path: str | Path | None = None) -> None:
        self.storage_path = Path(storage_path) if storage_path is not None else Path.cwd() / "tasks.json"

    @staticmethod
    def _task_id(value: object) -> int:
        if type(value) is int and value > 0:
            return value
        if isinstance(value, str) and re.fullmatch(r"[0-9]+", value):
            try:
                task_id = int(value)
            except ValueError as exc:
                raise TaskNotFoundError(value) from exc
            if task_id > 0:
                return task_id
        raise TaskNotFoundError(str(value))

    @staticmethod
    def _task_title(value: object) -> str:
        if not isinstance(value, str):
            raise InvalidTitleError("Task title must be text.")
        title = value.strip()
        if not title:
            raise EmptyTitleError("Task title must not be empty.")
        return title

    def add_task(self, title: str) -> Task:
        cleaned_title = self._task_title(title)
        next_id, tasks = self._load_state()
        created = Task(next_id, cleaned_title, "open")
        self._save_state(next_id + 1, [*tasks, created])
        return created

    def list_tasks(self) -> list[Task]:
        _, tasks = self._load_state()
        return list(tasks)

    def complete_task(self, task_id: str | int) -> tuple[Task, bool]:
        requested_id = self._task_id(task_id)
        next_id, tasks = self._load_state()
        for index, task in enumerate(tasks):
            if task.id == requested_id:
                if task.status == "done":
                    return task, False
                completed = Task(task.id, task.title, "done")
                updated_tasks = list(tasks)
                updated_tasks[index] = completed
                self._save_state(next_id, updated_tasks)
                return completed, True
        raise TaskNotFoundError(str(task_id))

    def reopen_task(self, task_id: str | int) -> tuple[Task, bool]:
        requested_id = self._task_id(task_id)
        next_id, tasks = self._load_state()
        for index, task in enumerate(tasks):
            if task.id == requested_id:
                if task.status == "open":
                    return task, False
                reopened = Task(task.id, task.title, "open")
                updated_tasks = list(tasks)
                updated_tasks[index] = reopened
                self._save_state(next_id, updated_tasks)
                return reopened, True
        raise TaskNotFoundError(str(task_id))

    def delete_task(self, task_id: str | int) -> Task:
        requested_id = self._task_id(task_id)
        next_id, tasks = self._load_state()
        for index, task in enumerate(tasks):
            if task.id == requested_id:
                self._save_state(next_id, tasks[:index] + tasks[index + 1 :])
                return task
        raise TaskNotFoundError(str(task_id))

    def _load_state(self) -> tuple[int, list[Task]]:
        try:
            raw = self.storage_path.read_bytes()
        except FileNotFoundError:
            return 1, []
        except OSError as exc:
            raise StorageError("Task storage could not be read.") from exc

        if not raw:
            return 1, []

        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CorruptStorageError("Task storage is corrupt.") from exc
        return self._validate_payload(payload)

    @staticmethod
    def _validate_payload(payload: Any) -> tuple[int, list[Task]]:
        if not isinstance(payload, dict) or set(payload) != {"next_id", "tasks"}:
            raise CorruptStorageError("Task storage has an invalid structure.")

        next_id = payload["next_id"]
        records = payload["tasks"]
        if type(next_id) is not int or next_id < 1 or not isinstance(records, list):
            raise CorruptStorageError("Task storage has invalid field types.")

        tasks: list[Task] = []
        seen_ids: set[int] = set()
        for record in records:
            if not isinstance(record, dict) or set(record) != {"id", "title", "status"}:
                raise CorruptStorageError("Task storage has an invalid task record.")
            task_id = record["id"]
            title = record["title"]
            status = record["status"]
            if (
                type(task_id) is not int
                or task_id < 1
                or task_id in seen_ids
                or not isinstance(title, str)
                or not isinstance(status, str)
                or status not in {"open", "done"}
            ):
                raise CorruptStorageError("Task storage has an invalid task record.")
            seen_ids.add(task_id)
            tasks.append(Task(task_id, title, status))

        if next_id <= max(seen_ids, default=0):
            raise CorruptStorageError("Task storage next_id is inconsistent.")
        return next_id, tasks

    def _save_state(self, next_id: int, tasks: list[Task]) -> None:
        destination = self.storage_path
        try:
            try:
                existing_mode: int | None = stat.S_IMODE(destination.stat().st_mode)
            except FileNotFoundError:
                existing_mode = None
        except OSError as exc:
            raise StorageError("Task storage mode could not be read.") from exc

        temporary_name: str | None = None
        open_descriptor: int | None = None
        try:
            open_descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{destination.name}.", dir=destination.parent
            )
            with os.fdopen(open_descriptor, "w", encoding="utf-8", newline="\n") as stream:
                open_descriptor = None
                json.dump(
                    {
                        "next_id": next_id,
                        "tasks": [
                            {"id": task.id, "title": task.title, "status": task.status}
                            for task in tasks
                        ],
                    },
                    stream,
                    ensure_ascii=False,
                    indent=2,
                )
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            if existing_mode is not None:
                os.chmod(temporary_name, existing_mode)
            os.replace(temporary_name, destination)
        except (OSError, UnicodeError, TypeError, ValueError) as exc:
            raise StorageError("Task storage could not be written.") from exc
        finally:
            if open_descriptor is not None:
                try:
                    os.close(open_descriptor)
                except OSError:
                    pass
            if temporary_name is not None and os.path.exists(temporary_name):
                try:
                    os.unlink(temporary_name)
                except OSError:
                    pass