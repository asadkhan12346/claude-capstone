"""
todo — Personal todo-list CLI package.

Standard library only; requires Python 3.11+ (NFR-001).
Re-exports the public API from todo.app for convenient access.
"""

from todo.app import (  # noqa: F401
    StorageError,
    create_task,
    delete_task,
    list_tasks,
    mark_completed,
    mark_pending,
    update_task,
)

__all__ = [
    "StorageError",
    "create_task",
    "list_tasks",
    "update_task",
    "delete_task",
    "mark_completed",
    "mark_pending",
]
