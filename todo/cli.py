"""Command-line adapter for the Todo application."""

from __future__ import annotations

import sys
import unicodedata
from collections.abc import Sequence
from typing import TextIO

from todo.app import (
    CorruptStorageError,
    EmptyTitleError,
    InvalidTitleError,
    StorageError,
    TaskNotFoundError,
    TodoApp,
    TodoError,
)

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
USAGE = (
    'USAGE:\n'
    '  python -m todo.cli add "<title>"\n'
    '  python -m todo.cli list\n'
    '  python -m todo.cli done <id>\n'
    '  python -m todo.cli reopen <id>\n'
    '  python -m todo.cli delete <id>'
)
_BIDI_CONTROLS = {
    0x061C,
    0x200E,
    0x200F,
    *range(0x202A, 0x202F),
    *range(0x2066, 0x206A),
}


def _configure_utf8(stream: TextIO) -> None:
    if (stream is sys.stdout or stream is sys.stderr) and hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


def _display_title(title: str) -> str:
    output: list[str] = []
    for character in title:
        codepoint = ord(character)
        if character == "\n":
            output.append("\\n")
        elif character == "\r":
            output.append("\\r")
        elif character == "\t":
            output.append("\\t")
        elif (
            unicodedata.category(character) in {"Cc", "Zl", "Zp"}
            or codepoint in _BIDI_CONTROLS
        ):
            output.append(f"\\x{codepoint:02x}" if codepoint <= 0xFF else f"\\u{codepoint:04x}")
        else:
            output.append(character)
    return "".join(output)


def _write_usage(stderr: TextIO) -> None:
    print(USAGE, file=stderr)


def main(
    argv: Sequence[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    app: TodoApp | None = None,
) -> int:
    """Run one CLI operation and return its exit status."""
    output_stream = sys.stdout if stdout is None else stdout
    error_stream = sys.stderr if stderr is None else stderr
    _configure_utf8(output_stream)
    _configure_utf8(error_stream)
    arguments = list(sys.argv[1:] if argv is None else argv)
    application = TodoApp() if app is None else app

    if not arguments:
        _write_usage(error_stream)
        return EXIT_USAGE

    command = arguments[0]
    if command == "add" and len(arguments) == 2:
        try:
            task = application.add_task(arguments[1])
        except (EmptyTitleError, InvalidTitleError) as exc:
            print(f"Error: {exc}", file=error_stream)
            return EXIT_ERROR
        except CorruptStorageError:
            print("Error: task storage is corrupt.", file=error_stream)
            return EXIT_ERROR
        except StorageError:
            print("Error: task storage could not be accessed.", file=error_stream)
            return EXIT_ERROR
        print(f"Added: {task.id} [open] {_display_title(task.title)}", file=output_stream)
        return EXIT_OK

    if command == "list" and len(arguments) == 1:
        try:
            tasks = application.list_tasks()
        except CorruptStorageError:
            print("Error: task storage is corrupt.", file=error_stream)
            return EXIT_ERROR
        except StorageError:
            print("Error: task storage could not be accessed.", file=error_stream)
            return EXIT_ERROR
        if not tasks:
            print("No tasks.", file=output_stream)
        else:
            for task in tasks:
                print(
                    f"{task.id} [{task.status}] {_display_title(task.title)}",
                    file=output_stream,
                )
        return EXIT_OK

    if command in {"done", "reopen", "delete"} and len(arguments) == 2:
        try:
            if command == "done":
                _, changed = application.complete_task(arguments[1])
                if not changed:
                    print(f"Task {arguments[1]} is already done.", file=output_stream)
            elif command == "reopen":
                _, changed = application.reopen_task(arguments[1])
                if not changed:
                    print(f"Task {arguments[1]} is already open.", file=output_stream)
            else:
                application.delete_task(arguments[1])
        except TaskNotFoundError as exc:
            print(f"Error: task {exc.task_id} not found.", file=error_stream)
            return EXIT_ERROR
        except CorruptStorageError:
            print("Error: task storage is corrupt.", file=error_stream)
            return EXIT_ERROR
        except StorageError:
            print("Error: task storage could not be accessed.", file=error_stream)
            return EXIT_ERROR
        return EXIT_OK

    _write_usage(error_stream)
    return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())