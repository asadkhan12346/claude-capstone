"""
tests/test_todo.py — Automated test suite for the todo package.

Uses unittest exclusively (NFR-004).
All tests run in temporary directories to avoid modifying the user's environment (NFR-004).
Every test class and method cites the FR/NFR/finding ID it covers (NFR-004).
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

from todo.app import (
    StorageError,
    create_task,
    delete_task,
    list_tasks,
    load,
    mark_completed,
    mark_pending,
    save,
    update_task,
)
from todo.cli import DEFAULT_STORAGE_PATH


# ---------------------------------------------------------------------------
# TestStorageLoad — FR-016, FR-017, F-04
# ---------------------------------------------------------------------------


class TestStorageLoad(unittest.TestCase):
    """Storage load() function — covers FR-016, FR-017, F-04."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = pathlib.Path(self.tmp_dir.name)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_missing_file_returns_default(self) -> None:
        """FR-017: load() on a non-existent path returns the default empty state."""
        nonexistent = self.tmp_path / "does_not_exist.json"
        result = load(nonexistent)
        self.assertEqual(result, {"next_id": 1, "tasks": []})

    def test_empty_file_returns_default(self) -> None:
        """FR-017: load() on an empty file returns the default empty state."""
        empty_file = self.tmp_path / "empty.json"
        empty_file.write_text("", encoding="utf-8")
        result = load(empty_file)
        self.assertEqual(result, {"next_id": 1, "tasks": []})

    def test_whitespace_only_file_returns_default(self) -> None:
        """FR-017: load() on a whitespace-only file returns the default empty state."""
        ws_file = self.tmp_path / "ws.json"
        ws_file.write_text("   \n\t  ", encoding="utf-8")
        result = load(ws_file)
        self.assertEqual(result, {"next_id": 1, "tasks": []})

    def test_valid_json_returns_data(self) -> None:
        """FR-016: load() on a valid JSON file returns the parsed dict."""
        data = {"next_id": 3, "tasks": [{"id": 1, "title": "t", "description": "", "status": "pending"}]}
        valid_file = self.tmp_path / "valid.json"
        valid_file.write_text(json.dumps(data), encoding="utf-8")
        result = load(valid_file)
        self.assertEqual(result["next_id"], 3)
        self.assertEqual(len(result["tasks"]), 1)

    def test_malformed_json_raises_storage_error(self) -> None:
        """F-04: load() on malformed JSON raises StorageError."""
        bad_file = self.tmp_path / "bad.json"
        bad_file.write_text("not valid json {", encoding="utf-8")
        with self.assertRaises(StorageError):
            load(bad_file)


# ---------------------------------------------------------------------------
# TestStorageSave — FR-016, NFR-002, F-02
# ---------------------------------------------------------------------------


class TestStorageSave(unittest.TestCase):
    """Storage save() function — covers FR-016, NFR-002, F-02."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = pathlib.Path(self.tmp_dir.name)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_save_creates_file(self) -> None:
        """FR-016: save() creates the target file with valid JSON content."""
        target = self.tmp_path / "todo.json"
        data = {"next_id": 1, "tasks": []}
        save(target, data)
        self.assertTrue(target.exists())
        loaded = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(loaded, data)

    def test_save_no_tmp_file_remains(self) -> None:
        """F-02: No .tmp file remains after a successful save()."""
        target = self.tmp_path / "todo.json"
        data = {"next_id": 1, "tasks": []}
        save(target, data)
        tmp_file = pathlib.Path(str(target) + ".tmp")
        self.assertFalse(tmp_file.exists())

    def test_save_utf8_encoding(self) -> None:
        """NFR-002: save() writes UTF-8; non-ASCII characters round-trip correctly."""
        target = self.tmp_path / "todo.json"
        data = {
            "next_id": 2,
            "tasks": [{"id": 1, "title": "Compra leche — café", "description": "naïve résumé", "status": "pending"}],
        }
        save(target, data)
        loaded = load(target)
        self.assertEqual(loaded["tasks"][0]["title"], "Compra leche — café")
        self.assertEqual(loaded["tasks"][0]["description"], "naïve résumé")


# ---------------------------------------------------------------------------
# TestCreateTask — FR-001, FR-002, FR-013, FR-014, FR-015
# ---------------------------------------------------------------------------


class TestCreateTask(unittest.TestCase):
    """create_task() — covers FR-001, FR-002, FR-013, FR-014, FR-015."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage = pathlib.Path(self.tmp_dir.name) / "todo.json"

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_fr001_create_basic(self) -> None:
        """FR-001: Basic create returns success, id=1, status=pending."""
        result = create_task(self.storage, "Buy milk")
        self.assertTrue(result["success"])
        self.assertEqual(result["task"]["id"], 1)
        self.assertEqual(result["task"]["title"], "Buy milk")
        self.assertEqual(result["task"]["status"], "pending")

    def test_fr001_title_trimmed(self) -> None:
        """FR-001: Title is trimmed of surrounding whitespace before storage."""
        result = create_task(self.storage, "  Buy milk  ")
        self.assertTrue(result["success"])
        self.assertEqual(result["task"]["title"], "Buy milk")

    def test_fr001_internal_whitespace_preserved(self) -> None:
        """FR-001: Internal whitespace in title is preserved."""
        result = create_task(self.storage, "  Buy   milk  ")
        self.assertTrue(result["success"])
        self.assertEqual(result["task"]["title"], "Buy   milk")

    def test_fr002_description_defaults_empty(self) -> None:
        """FR-002: When description is omitted, stored description is empty string."""
        result = create_task(self.storage, "Buy milk")
        self.assertEqual(result["task"]["description"], "")

    def test_fr002_description_provided(self) -> None:
        """FR-002: When description is provided, it is stored as-is."""
        result = create_task(self.storage, "Buy milk", "From the corner shop")
        self.assertEqual(result["task"]["description"], "From the corner shop")

    def test_fr013_empty_title_rejected(self) -> None:
        """FR-013: Empty title is rejected; storage file is not created."""
        result = create_task(self.storage, "")
        self.assertFalse(result["success"])
        self.assertIsNone(result["task"])
        self.assertFalse(self.storage.exists())

    def test_fr013_whitespace_title_rejected(self) -> None:
        """FR-013: Whitespace-only title is rejected; storage file is not created."""
        result = create_task(self.storage, "   ")
        self.assertFalse(result["success"])
        self.assertIsNone(result["task"])
        self.assertFalse(self.storage.exists())

    def test_fr013_message_nonempty_on_rejection(self) -> None:
        """FR-013, FR-018: Rejected create returns a non-empty error message."""
        result = create_task(self.storage, "")
        self.assertIsInstance(result["message"], str)
        self.assertGreater(len(result["message"]), 0)

    def test_fr014_duplicate_titles_allowed(self) -> None:
        """FR-014: Two tasks with the same title both succeed with distinct IDs."""
        r1 = create_task(self.storage, "Buy milk")
        r2 = create_task(self.storage, "Buy milk")
        self.assertTrue(r1["success"])
        self.assertTrue(r2["success"])
        self.assertNotEqual(r1["task"]["id"], r2["task"]["id"])

    def test_fr015_ids_auto_increment(self) -> None:
        """FR-015: IDs start at 1 and increment by 1 per creation."""
        r1 = create_task(self.storage, "First")
        r2 = create_task(self.storage, "Second")
        self.assertEqual(r1["task"]["id"], 1)
        self.assertEqual(r2["task"]["id"], 2)

    def test_fr015_id_not_reused_after_delete(self) -> None:
        """FR-015: After deleting task 2, the next created task receives ID 3, not 2."""
        create_task(self.storage, "First")
        create_task(self.storage, "Second")
        delete_task(self.storage, 2)
        r3 = create_task(self.storage, "Third")
        self.assertEqual(r3["task"]["id"], 3)

    def test_fr015_next_id_persists_across_restarts(self) -> None:
        """FR-015, FR-016: next_id persists; re-loading the same file gives correct next ID."""
        create_task(self.storage, "Task A")
        create_task(self.storage, "Task B")
        # Simulate restart by calling create_task again on the same file
        r3 = create_task(self.storage, "Task C")
        self.assertEqual(r3["task"]["id"], 3)


# ---------------------------------------------------------------------------
# TestListTasks — FR-003, FR-004, FR-005, F-06
# ---------------------------------------------------------------------------


class TestListTasks(unittest.TestCase):
    """list_tasks() — covers FR-003, FR-004, FR-005, F-06."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage = pathlib.Path(self.tmp_dir.name) / "todo.json"

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_fr003_all_tasks_in_creation_order(self) -> None:
        """FR-003: Tasks are returned in ascending ID (creation) order."""
        create_task(self.storage, "First")
        create_task(self.storage, "Second")
        result = list_tasks(self.storage)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["tasks"]), 2)
        self.assertLess(result["tasks"][0]["id"], result["tasks"][1]["id"])

    def test_fr004_empty_list_message(self) -> None:
        """FR-004: list_tasks on a missing file returns success with empty tasks and a message."""
        result = list_tasks(self.storage)
        self.assertTrue(result["success"])
        self.assertEqual(result["tasks"], [])
        self.assertIsInstance(result["message"], str)
        self.assertGreater(len(result["message"]), 0)

    def test_fr004_existing_empty_storage(self) -> None:
        """FR-004: list_tasks on an empty storage file returns 'no tasks' message."""
        # Create and delete a task so the file exists but has no tasks
        create_task(self.storage, "Temp")
        delete_task(self.storage, 1)
        result = list_tasks(self.storage)
        self.assertTrue(result["success"])
        self.assertEqual(result["tasks"], [])

    def test_fr005_filter_by_completed(self) -> None:
        """FR-005: Filter by 'completed' returns only completed tasks."""
        create_task(self.storage, "Pending task")
        create_task(self.storage, "To complete")
        create_task(self.storage, "Also pending")
        mark_completed(self.storage, 2)
        result = list_tasks(self.storage, status_filter="completed")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["tasks"]), 1)
        self.assertEqual(result["tasks"][0]["status"], "completed")

    def test_fr005_filter_by_pending(self) -> None:
        """FR-005: Filter by 'pending' returns only pending tasks."""
        create_task(self.storage, "First")
        create_task(self.storage, "Second")
        mark_completed(self.storage, 1)
        result = list_tasks(self.storage, status_filter="pending")
        self.assertTrue(result["success"])
        for task in result["tasks"]:
            self.assertEqual(task["status"], "pending")

    def test_fr005_filter_no_match(self) -> None:
        """FR-005: Filter with no matching tasks returns empty tasks list and success."""
        create_task(self.storage, "Pending only")
        result = list_tasks(self.storage, status_filter="completed")
        self.assertTrue(result["success"])
        self.assertEqual(result["tasks"], [])
        self.assertGreater(len(result["message"]), 0)

    def test_f06_return_shape_has_tasks_key(self) -> None:
        """F-06: list_tasks always returns a dict with a 'tasks' key of type list."""
        result = list_tasks(self.storage)
        self.assertIn("tasks", result)
        self.assertIsInstance(result["tasks"], list)

    def test_f06_return_shape_with_data(self) -> None:
        """F-06: 'tasks' key present and is a list even when tasks exist."""
        create_task(self.storage, "Something")
        result = list_tasks(self.storage)
        self.assertIn("tasks", result)
        self.assertIsInstance(result["tasks"], list)
        self.assertGreater(len(result["tasks"]), 0)


# ---------------------------------------------------------------------------
# TestUpdateTask — FR-006, FR-012, FR-013, F-03
# ---------------------------------------------------------------------------


class TestUpdateTask(unittest.TestCase):
    """update_task() — covers FR-006, FR-012, FR-013, F-03."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage = pathlib.Path(self.tmp_dir.name) / "todo.json"
        create_task(self.storage, "Original title", "Original description")

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_fr006_update_title_only(self) -> None:
        """FR-006: Updating title only changes title; description and status unchanged."""
        update_task(self.storage, 1, title="New title")
        data = load(self.storage)
        task = data["tasks"][0]
        self.assertEqual(task["title"], "New title")
        self.assertEqual(task["description"], "Original description")
        self.assertEqual(task["status"], "pending")

    def test_fr006_update_description_only(self) -> None:
        """FR-006: Updating description only changes description; title and status unchanged."""
        update_task(self.storage, 1, description="New description")
        data = load(self.storage)
        task = data["tasks"][0]
        self.assertEqual(task["title"], "Original title")
        self.assertEqual(task["description"], "New description")
        self.assertEqual(task["status"], "pending")

    def test_fr006_update_both_fields(self) -> None:
        """FR-006: Updating both title and description changes both; status unchanged."""
        update_task(self.storage, 1, title="New title", description="New desc")
        data = load(self.storage)
        task = data["tasks"][0]
        self.assertEqual(task["title"], "New title")
        self.assertEqual(task["description"], "New desc")
        self.assertEqual(task["status"], "pending")

    def test_fr006_title_trimmed_on_update(self) -> None:
        """FR-006: Title is trimmed of surrounding whitespace on update."""
        update_task(self.storage, 1, title="  New  ")
        data = load(self.storage)
        self.assertEqual(data["tasks"][0]["title"], "New")

    def test_fr006_status_not_changed_by_update(self) -> None:
        """FR-006: update_task does not modify the status field."""
        mark_completed(self.storage, 1)
        update_task(self.storage, 1, title="Updated")
        data = load(self.storage)
        self.assertEqual(data["tasks"][0]["status"], "completed")

    def test_fr012_update_not_found(self) -> None:
        """FR-012: Updating a non-existent task ID returns success=False with 'not found' message."""
        result = update_task(self.storage, 99, title="x")
        self.assertFalse(result["success"])
        self.assertIn("not found", result["message"].lower())

    def test_fr013_update_empty_title_rejected(self) -> None:
        """FR-013: Empty title on update is rejected; storage is unchanged."""
        before = load(self.storage)
        result = update_task(self.storage, 1, title="")
        self.assertFalse(result["success"])
        after = load(self.storage)
        self.assertEqual(before["tasks"][0]["title"], after["tasks"][0]["title"])

    def test_fr013_update_whitespace_title_rejected(self) -> None:
        """FR-013: Whitespace-only title on update is rejected."""
        result = update_task(self.storage, 1, title="   ")
        self.assertFalse(result["success"])

    def test_f03_none_title_leaves_title_unchanged(self) -> None:
        """F-03: Passing title=None leaves the title field unchanged."""
        update_task(self.storage, 1, title=None, description="new desc")
        data = load(self.storage)
        self.assertEqual(data["tasks"][0]["title"], "Original title")

    def test_f03_none_description_leaves_description_unchanged(self) -> None:
        """F-03: Passing description=None leaves the description field unchanged."""
        update_task(self.storage, 1, title="new title", description=None)
        data = load(self.storage)
        self.assertEqual(data["tasks"][0]["description"], "Original description")

    def test_f03_both_none_returns_error(self) -> None:
        """F-03: Calling update_task with both title=None and description=None returns success=False."""
        result = update_task(self.storage, 1)
        self.assertFalse(result["success"])
        self.assertIsInstance(result["message"], str)
        self.assertGreater(len(result["message"]), 0)

    def test_f03_empty_string_description_is_valid(self) -> None:
        """F-03: An empty string is a valid description value (not a sentinel)."""
        result = update_task(self.storage, 1, description="")
        self.assertTrue(result["success"])
        data = load(self.storage)
        self.assertEqual(data["tasks"][0]["description"], "")


# ---------------------------------------------------------------------------
# TestDeleteTask — FR-007, FR-012
# ---------------------------------------------------------------------------


class TestDeleteTask(unittest.TestCase):
    """delete_task() — covers FR-007, FR-012."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage = pathlib.Path(self.tmp_dir.name) / "todo.json"
        create_task(self.storage, "Task one")
        create_task(self.storage, "Task two")

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_fr007_delete_removes_task(self) -> None:
        """FR-007: delete_task removes the task and reports success."""
        result = delete_task(self.storage, 1)
        self.assertTrue(result["success"])
        data = load(self.storage)
        ids = [t["id"] for t in data["tasks"]]
        self.assertNotIn(1, ids)

    def test_fr007_task_absent_from_subsequent_list(self) -> None:
        """FR-007: After delete, list_tasks does not include the deleted task."""
        delete_task(self.storage, 2)
        result = list_tasks(self.storage)
        ids = [t["id"] for t in result["tasks"]]
        self.assertNotIn(2, ids)

    def test_fr007_next_id_not_decremented(self) -> None:
        """FR-015: delete_task does not decrement next_id."""
        delete_task(self.storage, 2)
        data = load(self.storage)
        self.assertEqual(data["next_id"], 3)

    def test_fr012_delete_not_found(self) -> None:
        """FR-012: Deleting a non-existent task ID returns success=False."""
        result = delete_task(self.storage, 99)
        self.assertFalse(result["success"])
        self.assertIsInstance(result["message"], str)
        self.assertGreater(len(result["message"]), 0)


# ---------------------------------------------------------------------------
# TestMarkCompleted — FR-008, FR-009, FR-012
# ---------------------------------------------------------------------------


class TestMarkCompleted(unittest.TestCase):
    """mark_completed() — covers FR-008, FR-009, FR-012."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage = pathlib.Path(self.tmp_dir.name) / "todo.json"
        create_task(self.storage, "My task")

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_fr008_pending_becomes_completed(self) -> None:
        """FR-008: mark_completed sets status to 'completed' for a pending task."""
        result = mark_completed(self.storage, 1)
        self.assertTrue(result["success"])
        data = load(self.storage)
        self.assertEqual(data["tasks"][0]["status"], "completed")

    def test_fr009_already_completed_noop(self) -> None:
        """FR-009: mark_completed on an already-completed task returns success=True with already_set=True; no write."""
        mark_completed(self.storage, 1)
        content_before = self.storage.read_bytes()
        result = mark_completed(self.storage, 1)
        content_after = self.storage.read_bytes()
        self.assertTrue(result["success"])
        self.assertTrue(result.get("already_set"))
        self.assertEqual(content_before, content_after)

    def test_fr012_mark_completed_not_found(self) -> None:
        """FR-012: mark_completed for a non-existent task ID returns success=False."""
        result = mark_completed(self.storage, 99)
        self.assertFalse(result["success"])
        self.assertIsInstance(result["message"], str)
        self.assertGreater(len(result["message"]), 0)


# ---------------------------------------------------------------------------
# TestMarkPending — FR-010, FR-011, FR-012
# ---------------------------------------------------------------------------


class TestMarkPending(unittest.TestCase):
    """mark_pending() — covers FR-010, FR-011, FR-012."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage = pathlib.Path(self.tmp_dir.name) / "todo.json"
        create_task(self.storage, "My task")
        mark_completed(self.storage, 1)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_fr010_completed_becomes_pending(self) -> None:
        """FR-010: mark_pending sets status to 'pending' for a completed task."""
        result = mark_pending(self.storage, 1)
        self.assertTrue(result["success"])
        data = load(self.storage)
        self.assertEqual(data["tasks"][0]["status"], "pending")

    def test_fr011_already_pending_noop(self) -> None:
        """FR-011: mark_pending on an already-pending task returns success=True with already_set=True; no write."""
        mark_pending(self.storage, 1)  # Now pending
        content_before = self.storage.read_bytes()
        result = mark_pending(self.storage, 1)
        content_after = self.storage.read_bytes()
        self.assertTrue(result["success"])
        self.assertTrue(result.get("already_set"))
        self.assertEqual(content_before, content_after)

    def test_fr012_mark_pending_not_found(self) -> None:
        """FR-012: mark_pending for a non-existent task ID returns success=False."""
        result = mark_pending(self.storage, 99)
        self.assertFalse(result["success"])
        self.assertIsInstance(result["message"], str)
        self.assertGreater(len(result["message"]), 0)


# ---------------------------------------------------------------------------
# TestMessages — FR-018
# ---------------------------------------------------------------------------


class TestMessages(unittest.TestCase):
    """Every operation returns a non-empty message string — covers FR-018."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage = pathlib.Path(self.tmp_dir.name) / "todo.json"

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def _assert_nonempty_message(self, result: dict) -> None:
        self.assertIsInstance(result["message"], str)
        self.assertGreater(len(result["message"]), 0)

    def test_fr018_every_operation_returns_nonempty_message(self) -> None:
        """FR-018: All six operations (success and error paths) return non-empty message strings."""
        # create — success
        r = create_task(self.storage, "Test task")
        self._assert_nonempty_message(r)

        # create — error (empty title)
        r = create_task(self.storage, "")
        self._assert_nonempty_message(r)

        # list — success (tasks exist)
        r = list_tasks(self.storage)
        self._assert_nonempty_message(r)

        # list — success (empty)
        tmp_storage = pathlib.Path(self.tmp_dir.name) / "empty.json"
        r = list_tasks(tmp_storage)
        self._assert_nonempty_message(r)

        # update — success
        r = update_task(self.storage, 1, title="Updated")
        self._assert_nonempty_message(r)

        # update — error (not found)
        r = update_task(self.storage, 99, title="x")
        self._assert_nonempty_message(r)

        # update — error (both None)
        r = update_task(self.storage, 1)
        self._assert_nonempty_message(r)

        # delete — success
        r = delete_task(self.storage, 1)
        self._assert_nonempty_message(r)

        # delete — error (not found)
        r = delete_task(self.storage, 99)
        self._assert_nonempty_message(r)

        # mark_completed — success
        create_task(self.storage, "Another task")
        r = mark_completed(self.storage, 2)
        self._assert_nonempty_message(r)

        # mark_completed — idempotent
        r = mark_completed(self.storage, 2)
        self._assert_nonempty_message(r)

        # mark_completed — not found
        r = mark_completed(self.storage, 99)
        self._assert_nonempty_message(r)

        # mark_pending — success
        r = mark_pending(self.storage, 2)
        self._assert_nonempty_message(r)

        # mark_pending — idempotent
        r = mark_pending(self.storage, 2)
        self._assert_nonempty_message(r)

        # mark_pending — not found
        r = mark_pending(self.storage, 99)
        self._assert_nonempty_message(r)


# ---------------------------------------------------------------------------
# TestNFR002UTF8 — NFR-002
# ---------------------------------------------------------------------------


class TestNFR002UTF8(unittest.TestCase):
    """Non-ASCII character preservation via UTF-8 encoding — covers NFR-002."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage = pathlib.Path(self.tmp_dir.name) / "todo.json"

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_nfr002_non_ascii_title_preserved(self) -> None:
        """NFR-002: A non-ASCII title round-trips through save()/load() without corruption."""
        title = "Compra leche — café 中文"
        create_task(self.storage, title)
        data = load(self.storage)
        self.assertEqual(data["tasks"][0]["title"], title)

    def test_nfr002_non_ascii_description_preserved(self) -> None:
        """NFR-002: A non-ASCII description round-trips through save()/load() without corruption."""
        description = "naïve résumé über Straße"
        create_task(self.storage, "Task", description)
        data = load(self.storage)
        self.assertEqual(data["tasks"][0]["description"], description)


# ---------------------------------------------------------------------------
# TestCLIIntegration — F-01, FR-018, NFR-004, F-05
# ---------------------------------------------------------------------------


class TestCLIIntegration(unittest.TestCase):
    """CLI integration via subprocess — covers F-01, FR-018, NFR-004, F-05."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage = str(pathlib.Path(self.tmp_dir.name) / "todo.json")
        # Use the same Python executable that is running these tests
        self.python = sys.executable

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        """Run the CLI with the given args, capturing stdout and stderr."""
        return subprocess.run(
            [self.python, "-m", "todo.cli", "--storage", self.storage, *args],
            capture_output=True,
            text=True,
        )

    def test_f01_invocation_python_m_todo_cli(self) -> None:
        """F-01, NFR-004: 'python -m todo.cli --help' exits 0 without __main__.py error."""
        proc = subprocess.run(
            [self.python, "-m", "todo.cli", "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("No module named todo.__main__", proc.stderr)

    def test_cli_create_success_exit_0(self) -> None:
        """FR-018, NFR-004: Successful create exits 0 and stdout contains the task ID."""
        proc = self._run("create", "Test task")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("1", proc.stdout)

    def test_cli_create_empty_title_exit_1(self) -> None:
        """FR-013, FR-018: Create with empty title exits 1 and stderr is non-empty."""
        proc = self._run("create", "")
        self.assertEqual(proc.returncode, 1)
        self.assertGreater(len(proc.stderr.strip()), 0)

    def test_cli_list_empty_exit_0(self) -> None:
        """FR-004, FR-018: list on fresh storage exits 0."""
        proc = self._run("list")
        self.assertEqual(proc.returncode, 0)

    def test_cli_list_with_tasks_exit_0(self) -> None:
        """FR-003, FR-018: list with tasks exits 0 and stdout shows task info."""
        self._run("create", "CLI task")
        proc = self._run("list")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("CLI task", proc.stdout)

    def test_cli_complete_not_found_exit_1(self) -> None:
        """FR-012, FR-018: complete on non-existent task exits 1."""
        proc = self._run("complete", "99")
        self.assertEqual(proc.returncode, 1)
        self.assertGreater(len(proc.stderr.strip()), 0)

    def test_cli_update_no_flags_exit_1(self) -> None:
        """F-03, FR-018: update with no --title or --description exits 1."""
        self._run("create", "A task")
        proc = self._run("update", "1")
        self.assertEqual(proc.returncode, 1)

    def test_cli_delete_success_exit_0(self) -> None:
        """FR-007: delete of existing task exits 0."""
        self._run("create", "To delete")
        proc = self._run("delete", "1")
        self.assertEqual(proc.returncode, 0)

    def test_cli_pending_success_exit_0(self) -> None:
        """FR-010: pending on a completed task exits 0."""
        self._run("create", "To pend")
        self._run("complete", "1")
        proc = self._run("pending", "1")
        self.assertEqual(proc.returncode, 0)

    def test_cli_filter_by_status(self) -> None:
        """FR-005: list --status completed only shows completed tasks."""
        self._run("create", "Task A")
        self._run("create", "Task B")
        self._run("complete", "1")
        proc = self._run("list", "--status", "completed")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Task A", proc.stdout)
        self.assertNotIn("Task B", proc.stdout)

    def test_cli_default_storage_is_home(self) -> None:
        """F-05: DEFAULT_STORAGE_PATH equals pathlib.Path.home() / '.todo.json'."""
        self.assertEqual(DEFAULT_STORAGE_PATH, pathlib.Path.home() / ".todo.json")


if __name__ == "__main__":
    unittest.main()
