"""CLI entry point for the Notes application (T-04).

Invoke as::

    python -m notes.cli <subcommand> [options]

The storage path defaults to ``notes.json`` in the current working directory
and can be overridden with the ``NOTES_PATH`` environment variable (used by
integration tests).
"""

from __future__ import annotations

import argparse
import os
import sys

from notes.app import (
    NoteError,
    create_note,
    delete_note,
    get_note,
    list_notes,
    update_note,
)


def _build_parser() -> argparse.ArgumentParser:
    """Construct and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="notes",
        description="A command-line notes manager.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    # create
    create_p = subparsers.add_parser("create", help="Create a new note.")
    create_p.add_argument("--title", required=True, help="Note title (non-empty).")
    create_p.add_argument("--content", required=True, help="Note content (non-empty).")

    # list
    subparsers.add_parser("list", help="List all notes.")

    # view
    view_p = subparsers.add_parser("view", help="View a single note by ID.")
    view_p.add_argument(
        "--id", type=int, required=True, dest="note_id", help="Note ID."
    )

    # update
    update_p = subparsers.add_parser("update", help="Update an existing note (full replace).")
    update_p.add_argument(
        "--id", type=int, required=True, dest="note_id", help="Note ID."
    )
    update_p.add_argument("--title", required=True, help="New title (non-empty).")
    update_p.add_argument("--content", required=True, help="New content (non-empty).")

    # delete
    delete_p = subparsers.add_parser("delete", help="Delete a note by ID.")
    delete_p.add_argument(
        "--id", type=int, required=True, dest="note_id", help="Note ID."
    )

    return parser


def main() -> None:
    """Entry point; invoked via ``python -m notes.cli`` (NFR-002, F-07).

    Reads ``NOTES_PATH`` from the environment to locate the JSON store so
    integration tests can redirect storage to a temporary file without
    patching source code.

    All :class:`~notes.app.NoteError` subclasses are caught, their message
    printed to stderr, and the process exits with code 1 (NFR-005).
    """
    storage_path: str = os.environ.get("NOTES_PATH", "notes.json")
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "create":
            note = create_note(args.title, args.content, storage_path)
            print(f"Note {note['id']} created: {note['title']}")

        elif args.command == "list":
            notes = list_notes(storage_path)
            if not notes:
                print("No notes found.")
            else:
                for note in notes:
                    print(f"[{note['id']}] {note['title']}: {note['content']}")

        elif args.command == "view":
            note = get_note(args.note_id, storage_path)
            print(f"[{note['id']}] {note['title']}: {note['content']}")

        elif args.command == "update":
            note = update_note(args.note_id, args.title, args.content, storage_path)
            print(f"Note {note['id']} updated: {note['title']}")

        elif args.command == "delete":
            delete_note(args.note_id, storage_path)
            print(f"Note {args.note_id} deleted.")

    except NoteError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
