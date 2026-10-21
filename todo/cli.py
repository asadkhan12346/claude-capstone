"""
todo.cli — CLI entry point for the personal todo-list manager.

Standard library only; requires Python 3.11+ (NFR-001).
No network calls or secrets (NFR-003).

Canonical invocation (F-01): ``python -m todo.cli <subcommand> [args]``
"""

import argparse
import pathlib
import sys

from todo.app import (
    create_task,
    delete_task,
    list_tasks,
    mark_completed,
    mark_pending,
    update_task,
)

# Default storage path in user's home directory (F-05)
DEFAULT_STORAGE_PATH: pathlib.Path = pathlib.Path.home() / ".todo.json"


def main() -> None:
    """
    CLI entry point — parse arguments and dispatch to the app layer (FR-018).

    Success and informational messages are printed to stdout (exit 0).
    Error messages are printed to stderr (exit 1).
    """
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Personal todo list manager",
    )
    parser.add_argument(
        "--storage",
        type=pathlib.Path,
        default=DEFAULT_STORAGE_PATH,
        help="Path to the JSON storage file (default: ~/.todo.json)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- create ---
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("title", type=str, help="Task title (required, non-empty)")
    create_parser.add_argument(
        "--description",
        type=str,
        default="",
        help="Task description (default: empty string)",
    )

    # --- list ---
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument(
        "--status",
        choices=["pending", "completed"],
        default=None,
        help="Filter tasks by status (pending or completed)",
    )

    # --- update ---
    update_parser = subparsers.add_parser(
        "update", help="Update a task's title or description"
    )
    update_parser.add_argument("task_id", type=int, help="ID of the task to update")
    update_parser.add_argument(
        "--title", type=str, default=None, help="New title (optional)"
    )
    update_parser.add_argument(
        "--description", type=str, default=None, help="New description (optional)"
    )

    # --- delete ---
    delete_parser = subparsers.add_parser("delete", help="Delete a task by ID")
    delete_parser.add_argument("task_id", type=int, help="ID of the task to delete")

    # --- complete ---
    complete_parser = subparsers.add_parser(
        "complete", help="Mark a task as completed"
    )
    complete_parser.add_argument(
        "task_id", type=int, help="ID of the task to mark as completed"
    )

    # --- pending ---
    pending_parser = subparsers.add_parser(
        "pending", help="Mark a task as pending"
    )
    pending_parser.add_argument(
        "task_id", type=int, help="ID of the task to mark as pending"
    )

    args = parser.parse_args()
    storage = args.storage

    # Dispatch to app layer
    if args.command == "create":
        result = create_task(storage, args.title, args.description)
    elif args.command == "list":
        result = list_tasks(storage, args.status)
    elif args.command == "update":
        result = update_task(
            storage, args.task_id, title=args.title, description=args.description
        )
    elif args.command == "delete":
        result = delete_task(storage, args.task_id)
    elif args.command == "complete":
        result = mark_completed(storage, args.task_id)
    elif args.command == "pending":
        result = mark_pending(storage, args.task_id)
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Output and exit codes (FR-018)
    if args.command == "list":
        if result["success"] and result["tasks"]:
            for task in result["tasks"]:
                print(f"[{task['id']}] {task['title']} ({task['status']})")
                print(f"    {task['description']}")
            print(result["message"])
            sys.exit(0)
        elif result["success"]:
            print(result["message"])
            sys.exit(0)
        else:
            print(result["message"], file=sys.stderr)
            sys.exit(1)
    else:
        if result["success"]:
            print(result["message"])
            sys.exit(0)
        else:
            print(result["message"], file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
