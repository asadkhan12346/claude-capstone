"""Requirement-tagged tests for Todo storage and application behavior."""

from __future__ import annotations

import json
import os
import socket
import stat
import tempfile
import unittest
from pathlib import Path
from urllib import request
from unittest.mock import patch

from todo.app import (
    CorruptStorageError,
    EmptyTitleError,
    StorageError,
    Task,
    TaskNotFoundError,
    TodoApp,
)
from todo.cli import EXIT_ERROR, EXIT_OK, EXIT_USAGE, main


class TodoStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.storage_path = self.directory / "tasks.json"
        self.app = TodoApp(self.storage_path)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_missing_and_empty_storage(self) -> None:
        """FR-020, FR-021: missing and empty storage use the defined empty state."""
        self.assertEqual(self.app._load_state(), (1, []))
        self.storage_path.write_bytes(b"")
        self.assertEqual(self.app._load_state(), (1, []))

    def test_json_encoding_and_indentation(self) -> None:
        """FR-020, NFR-002: persist the exact JSON schema and encoding."""
        task = Task(1, "caf\u00e9", "open")
        self.app._save_state(2, [task])
        data = self.storage_path.read_bytes()
        self.assertIn("caf\u00e9".encode("utf-8"), data)
        self.assertNotIn(b"\\u00e9", data)
        self.assertEqual(json.loads(data.decode("utf-8")), {
            "next_id": 2,
            "tasks": [{"id": 1, "title": "caf\u00e9", "status": "open"}],
        })
        self.assertIn(b'\n  "next_id"', data)

    def test_corrupt_storage_and_inconsistent_next_id_preserve_bytes(self) -> None:
        """FR-022, FR-024: reject corrupt records and unsafe ID counters unchanged."""
        invalid_payloads = (
            b"{broken",
            b'{"next_id":true,"tasks":[]}',
            b'{"next_id":1,"tasks":[{"id":1,"title":"a","status":[]}]}',
            b'{"next_id":2,"tasks":[{"id":1,"title":"a","status":"open"},{"id":1,"title":"b","status":"done"}]}',
            b'{"next_id":1,"tasks":[{"id":1,"title":"a","status":"open"}]}',
        )
        for raw in invalid_payloads:
            with self.subTest(raw=raw):
                self.storage_path.write_bytes(raw)
                with self.assertRaises(CorruptStorageError):
                    self.app._load_state()
                self.assertEqual(self.storage_path.read_bytes(), raw)

    def test_storage_io_failure_raises_storage_error(self) -> None:
        """FR-023: map non-corruption read failures to StorageError."""
        with patch.object(Path, "read_bytes", side_effect=PermissionError("denied")):
            with self.assertRaises(StorageError):
                self.app._load_state()

    def test_atomic_save_mode_and_temp_cleanup(self) -> None:
        """NFR-003: preserve destination bytes and clean temp files on failed replacement."""
        original = b'{"next_id":1,"tasks":[]}'
        self.storage_path.write_bytes(original)
        with patch("todo.app.os.replace", side_effect=OSError("replace failed")):
            with self.assertRaises(StorageError):
                self.app._save_state(2, [Task(1, "one", "open")])
        self.assertEqual(self.storage_path.read_bytes(), original)
        self.assertEqual(list(self.directory.iterdir()), [self.storage_path])

    def test_existing_file_mode_is_preserved(self) -> None:
        """NFR-003: preserve an existing storage file's mode on replacement."""
        self.storage_path.write_text('{"next_id":1,"tasks":[]}', encoding="utf-8")
        mode = stat.S_IMODE(self.storage_path.stat().st_mode)
        self.app._save_state(1, [])
        self.assertEqual(stat.S_IMODE(self.storage_path.stat().st_mode), mode)


class TodoOperationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.storage_path = self.directory / "tasks.json"
        self.app = TodoApp(self.storage_path)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_add_returns_created_task(self) -> None:
        """FR-002: return the newly created task and its ID."""
        self.assertEqual(self.app.add_task("first").id, 1)

    def test_new_task_starts_open(self) -> None:
        """FR-003: new task status is open."""
        self.assertEqual(self.app.add_task("first").status, "open")

    def test_list_preserves_creation_order(self) -> None:
        """FR-005: list tasks in creation order."""
        self.app.add_task("first")
        self.app.add_task("second")
        self.assertEqual([task.title for task in self.app.list_tasks()], ["first", "second"])

    def test_complete_open_task(self) -> None:
        """FR-007: complete transitions open to done."""
        task = self.app.add_task("transition")
        completed, changed = self.app.complete_task(task.id)
        self.assertEqual(completed.status, "done")
        self.assertTrue(changed)

    def test_complete_done_noop_preserves_bytes(self) -> None:
        """FR-008: completing a done task is a byte-preserving no-op."""
        task = self.app.add_task("transition")
        self.app.complete_task(task.id)
        before_done_noop = self.storage_path.read_bytes()
        same_done, changed = self.app.complete_task(str(task.id))
        self.assertEqual(same_done.status, "done")
        self.assertFalse(changed)
        self.assertEqual(self.storage_path.read_bytes(), before_done_noop)

    def test_reopen_done_task(self) -> None:
        """FR-009: reopen transitions done to open."""
        task = self.app.add_task("transition")
        self.app.complete_task(task.id)
        reopened, changed = self.app.reopen_task(task.id)
        self.assertEqual(reopened.status, "open")
        self.assertTrue(changed)

    def test_reopen_open_noop_preserves_bytes(self) -> None:
        """FR-010: reopening an open task is a byte-preserving no-op."""
        task = self.app.add_task("transition")
        before_open_noop = self.storage_path.read_bytes()
        same_open, changed = self.app.reopen_task(task.id)
        self.assertEqual(same_open.status, "open")
        self.assertFalse(changed)
        self.assertEqual(self.storage_path.read_bytes(), before_open_noop)

    def test_delete_removes_task(self) -> None:
        """FR-011: delete removes the selected task."""
        first = self.app.add_task("first")
        second = self.app.add_task("second")
        self.assertEqual(self.app.delete_task(first.id), first)
        self.assertEqual(self.app.list_tasks(), [second])

    def test_missing_task_error_and_unchanged_storage(self) -> None:
        """FR-012: missing IDs fail without modifying stored bytes."""
        self.app.add_task("present")
        original = self.storage_path.read_bytes()
        with self.assertRaises(TaskNotFoundError):
            self.app.complete_task("missing")
        self.assertEqual(self.storage_path.read_bytes(), original)

    def test_invalid_ids_are_not_found(self) -> None:
        """FR-013: malformed, zero, and negative IDs are not found."""
        self.app.add_task("present")
        original = self.storage_path.read_bytes()
        for task_id in ("0", "-1", "1.0"):
            with self.subTest(task_id=task_id):
                with self.assertRaises(TaskNotFoundError):
                    self.app.complete_task(task_id)
                self.assertEqual(self.storage_path.read_bytes(), original)

    def test_extremely_long_numeric_id_is_not_found(self) -> None:
        """FR-013: oversized numeric input is treated as not found."""
        with self.assertRaises(TaskNotFoundError):
            self.app.complete_task("9" * 5000)

    def test_blank_title_rejected_without_write(self) -> None:
        """FR-016: reject blank titles without creating storage."""
        with self.assertRaises(EmptyTitleError):
            self.app.add_task(" \t ")
        self.assertFalse(self.storage_path.exists())

    def test_title_trim_and_interior_whitespace(self) -> None:
        """FR-017: trim only title edges and preserve internal whitespace."""
        task = self.app.add_task("  keep  inner spacing  ")
        self.assertEqual(task.title, "keep  inner spacing")

    def test_duplicate_titles_get_distinct_ids(self) -> None:
        """FR-018: duplicate titles remain allowed with unique IDs."""
        first = self.app.add_task("same")
        second = self.app.add_task("same")
        self.assertEqual(first.title, second.title)
        self.assertNotEqual(first.id, second.id)

    def test_ids_increase_and_are_not_reused_after_delete(self) -> None:
        """FR-024: IDs increase monotonically and are never reused."""
        first = self.app.add_task("first")
        second = self.app.add_task("second")
        self.app.delete_task(first.id)
        self.assertEqual(self.app.add_task("third").id, second.id + 1)

    def test_read_noop_error_paths_preserve_bytes(self) -> None:
        """NFR-004: reads, no-ops, and invalid mutations never rewrite storage."""
        self.app.add_task("read")
        original = self.storage_path.read_bytes()
        self.app.list_tasks()
        self.assertEqual(self.storage_path.read_bytes(), original)
        with self.assertRaises(EmptyTitleError):
            self.app.add_task(" ")
        with self.assertRaises(TaskNotFoundError):
            self.app.delete_task("unknown")
        self.assertEqual(self.storage_path.read_bytes(), original)

    def test_long_title_and_many_tasks_have_no_product_limit(self) -> None:
        """FR-019: support long titles and no product-defined count limit."""
        large_title = "x" * 8192
        first = self.app.add_task(large_title)
        self.assertEqual(first.title, large_title)
        for index in range(40):
            self.app.add_task(f"task {index}")
        self.assertEqual(len(self.app.list_tasks()), 41)

    def test_storage_schema_and_current_directory(self) -> None:
        """FR-020: use the defined schema in the current working directory."""
        with patch.object(Path, "cwd", return_value=self.directory):
            default_app = TodoApp()
        self.assertEqual(default_app.storage_path, self.directory / "tasks.json")
        default_app.add_task("local")
        self.assertTrue((self.directory / "tasks.json").is_file())
        self.assertEqual(
            set(json.loads((self.directory / "tasks.json").read_text(encoding="utf-8"))),
            {"next_id", "tasks"},
        )

    def test_invalid_title_preserves_existing_bytes(self) -> None:
        """NFR-004: invalid mutations do not rewrite existing bytes."""
        self.app.add_task("existing")
        original = self.storage_path.read_bytes()
        with self.assertRaises(EmptyTitleError):
            self.app.add_task("   ")
        self.assertEqual(self.storage_path.read_bytes(), original)


class TodoCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.storage_path = Path(self.temporary_directory.name) / "tasks.json"
        self.app = TodoApp(self.storage_path)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def invoke(self, arguments: list[str]) -> tuple[int, str, str]:
        from io import StringIO

        stdout = StringIO()
        stderr = StringIO()
        result = main(arguments, stdout, stderr, self.app)
        return result, stdout.getvalue(), stderr.getvalue()

    def test_cli_commands_and_usage(self) -> None:
        """FR-001: expose all five commands and reject unknown commands."""
        self.assertEqual(self.invoke(["add", "one"])[0], EXIT_OK)
        self.assertEqual(self.invoke(["list"])[0], EXIT_OK)
        self.assertEqual(self.invoke(["done", "1"])[0], EXIT_OK)
        self.assertEqual(self.invoke(["reopen", "1"])[0], EXIT_OK)
        self.assertEqual(self.invoke(["delete", "1"])[0], EXIT_OK)
        result, _, error = self.invoke(["unknown"])
        self.assertEqual(result, EXIT_USAGE)
        self.assertTrue(error.startswith("USAGE"))

    def test_cli_add_output(self) -> None:
        """FR-004: print the exact add result."""
        result, output, error = self.invoke(["add", "first task"])
        self.assertEqual((result, error), (EXIT_OK, ""))
        self.assertEqual(output, "Added: 1 [open] first task\n")

    def test_list_empty_message(self) -> None:
        """FR-006: print the empty-list message."""
        self.assertEqual(self.invoke(["list"])[1], "No tasks.\n")

    def test_cli_list_preserves_creation_order(self) -> None:
        """FR-005: format each listed task in creation order."""
        self.app.add_task("first")
        self.app.add_task("second")
        self.assertEqual(self.invoke(["list"])[1], "1 [open] first\n2 [open] second\n")

    def test_complete_done_cli_noop_message(self) -> None:
        """FR-008: print the already-done no-op message."""
        self.app.add_task("task")
        self.invoke(["done", "1"])
        self.assertEqual(self.invoke(["done", "1"])[1], "Task 1 is already done.\n")

    def test_reopen_open_cli_noop_message(self) -> None:
        """FR-010: print the already-open no-op message."""
        self.app.add_task("task")
        self.invoke(["reopen", "1"])
        self.assertEqual(self.invoke(["reopen", "1"])[1], "Task 1 is already open.\n")

    def test_missing_task_cli_error_and_exit(self) -> None:
        """FR-012: report a missing task to stderr and return one."""
        result, output, error = self.invoke(["done", "nope"])
        self.assertEqual(result, EXIT_ERROR)
        self.assertEqual(output, "")
        self.assertEqual(error, "Error: task nope not found.\n")

    def test_invalid_task_id_cli_error_and_exit(self) -> None:
        """FR-013: invalid task IDs use the not-found CLI behavior."""
        for task_id in ("0", "-1"):
            with self.subTest(task_id=task_id):
                result, output, error = self.invoke(["done", task_id])
                self.assertEqual(result, EXIT_ERROR)
                self.assertEqual(output, "")
                self.assertEqual(error, f"Error: task {task_id} not found.\n")

    def test_usage_error_returns_two(self) -> None:
        """FR-014: malformed command forms return usage exit code two."""
        for arguments in ([], ["add"], ["list", "extra"], ["done", "1", "extra"]):
            with self.subTest(arguments=arguments):
                result, _, error = self.invoke(arguments)
                self.assertEqual(result, EXIT_USAGE)
                self.assertTrue(error.startswith("USAGE"))

    def test_operation_errors_use_stderr_and_error_exit(self) -> None:
        """FR-015: storage operation errors use stderr and a nonzero code."""
        self.storage_path.write_bytes(b"broken json")
        result, output, error = self.invoke(["list"])
        self.assertEqual(result, EXIT_ERROR)
        self.assertEqual(output, "")
        self.assertEqual(error, "Error: task storage is corrupt.\n")

    def test_title_trim_and_display_escape(self) -> None:
        """FR-017: preserve title semantics and escape terminal controls for display."""
        original_title = "line one\nline two\u2028line three\u2029line four\t\x1b[31m"
        result, output, error = self.invoke(["add", original_title])
        self.assertEqual((result, error), (EXIT_OK, ""))
        self.assertEqual(
            output,
            "Added: 1 [open] line one\\nline two\\u2028line three\\u2029line four\\t\\x1b[31m\n",
        )
        self.assertEqual(self.app.list_tasks()[0].title, original_title)
        self.assertEqual(
            self.invoke(["list"])[1],
            "1 [open] line one\\nline two\\u2028line three\\u2029line four\\t\\x1b[31m\n",
        )

    def test_cli_operations_are_local(self) -> None:
        """NFR-005: task operations do not open network connections."""
        with (
            patch.object(socket, "create_connection") as connect,
            patch.object(request, "urlopen") as urlopen,
        ):
            self.invoke(["add", "local task"])
            self.invoke(["list"])
        connect.assert_not_called()
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()