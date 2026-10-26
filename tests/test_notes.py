"""Tests for the Notes CLI application (T-05 unit tests, T-06 CLI integration).

Every FR-xxx and NFR-xxx cited in a method name matches the requirement ID
defined in artifacts/requirements.md.  Design-review finding IDs (F-xx) are
also cited where applicable.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

from notes.app import (
    NoteNotFoundError,
    StorageError,
    ValidationError,
    _load,
    _save,
    create_note,
    delete_note,
    get_note,
    list_notes,
    update_note,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_temp_path() -> str:
    """Return a unique temporary file path that does not yet exist.

    Uses NamedTemporaryFile to claim a unique OS-assigned name, then deletes
    the empty file so _load sees the path as absent (returning default state)
    rather than an empty-and-corrupt JSON file.
    """
    fh = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    path = fh.name
    fh.close()
    os.unlink(path)
    return path


def _cleanup(storage_path: str) -> None:
    """Remove the storage file and its .tmp sentinel if either exists."""
    for candidate in (storage_path, storage_path + ".tmp"):
        try:
            os.unlink(candidate)
        except FileNotFoundError:
            pass


# ---------------------------------------------------------------------------
# T-05: Unit tests
# ---------------------------------------------------------------------------


class TestCreateNote(unittest.TestCase):
    """Unit tests for FR-001 and FR-007."""

    def setUp(self) -> None:
        self.storage_path = _make_temp_path()

    def tearDown(self) -> None:
        _cleanup(self.storage_path)

    def test_fr001_create_returns_note(self) -> None:
        """FR-001: create_note returns a dict with id, title, content keys."""
        note = create_note("Hello", "World", self.storage_path)
        self.assertIn("id", note)
        self.assertIn("title", note)
        self.assertIn("content", note)
        self.assertEqual(note["title"], "Hello")
        self.assertEqual(note["content"], "World")

    def test_fr001_id_auto_increments(self) -> None:
        """FR-001, NFR-003: successive creates yield IDs 1 and 2."""
        note1 = create_note("First", "Content 1", self.storage_path)
        note2 = create_note("Second", "Content 2", self.storage_path)
        self.assertEqual(note1["id"], 1)
        self.assertEqual(note2["id"], 2)

    def test_fr001_data_persists_across_load(self) -> None:
        """FR-001, NFR-001: a created note survives a subsequent list_notes call."""
        create_note("Persistent", "Data", self.storage_path)
        notes = list_notes(self.storage_path)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["title"], "Persistent")

    def test_fr007_empty_title_raises(self) -> None:
        """FR-007, NFR-005: empty string title raises ValidationError."""
        with self.assertRaises(ValidationError):
            create_note("", "content", self.storage_path)

    def test_fr007_whitespace_only_title_raises(self) -> None:
        """FR-007, NFR-005, F-05: whitespace-only title raises ValidationError."""
        with self.assertRaises(ValidationError):
            create_note("   ", "content", self.storage_path)

    def test_fr007_empty_content_raises(self) -> None:
        """FR-007, NFR-005: empty string content raises ValidationError."""
        with self.assertRaises(ValidationError):
            create_note("title", "", self.storage_path)

    def test_fr007_whitespace_only_content_raises(self) -> None:
        """FR-007, NFR-005, F-05: whitespace-only content raises ValidationError."""
        with self.assertRaises(ValidationError):
            create_note("title", "   ", self.storage_path)


class TestListNotes(unittest.TestCase):
    """Unit tests for FR-002."""

    def setUp(self) -> None:
        self.storage_path = _make_temp_path()

    def tearDown(self) -> None:
        _cleanup(self.storage_path)

    def test_fr002_returns_empty_list_when_no_notes(self) -> None:
        """FR-002: list_notes returns [] on a freshly initialised store."""
        result = list_notes(self.storage_path)
        self.assertEqual(result, [])

    def test_fr002_returns_all_created_notes(self) -> None:
        """FR-002: list_notes returns all notes after two successive creates."""
        create_note("Note 1", "Content 1", self.storage_path)
        create_note("Note 2", "Content 2", self.storage_path)
        notes = list_notes(self.storage_path)
        self.assertEqual(len(notes), 2)


class TestGetNote(unittest.TestCase):
    """Unit tests for FR-003, FR-006."""

    def setUp(self) -> None:
        self.storage_path = _make_temp_path()

    def tearDown(self) -> None:
        _cleanup(self.storage_path)

    def test_fr003_returns_correct_note(self) -> None:
        """FR-003: get_note returns the note whose id matches the argument."""
        created = create_note("My Note", "My Content", self.storage_path)
        fetched = get_note(created["id"], self.storage_path)
        self.assertEqual(fetched["id"], created["id"])
        self.assertEqual(fetched["title"], "My Note")
        self.assertEqual(fetched["content"], "My Content")

    def test_fr006_raises_not_found_for_absent_id(self) -> None:
        """FR-006, NFR-005: get_note raises NoteNotFoundError for a missing ID."""
        with self.assertRaises(NoteNotFoundError):
            get_note(999, self.storage_path)


class TestUpdateNote(unittest.TestCase):
    """Unit tests for FR-004, FR-006, FR-007."""

    def setUp(self) -> None:
        self.storage_path = _make_temp_path()

    def tearDown(self) -> None:
        _cleanup(self.storage_path)

    def test_fr004_replaces_title_and_content(self) -> None:
        """FR-004: update_note changes both title and content of the note."""
        note = create_note("Original", "Old content", self.storage_path)
        updated = update_note(note["id"], "Updated", "New content", self.storage_path)
        self.assertEqual(updated["title"], "Updated")
        self.assertEqual(updated["content"], "New content")

    def test_fr004_full_replace_both_fields(self) -> None:
        """FR-004: get_note after update_note returns both new field values."""
        note = create_note("A", "B", self.storage_path)
        update_note(note["id"], "X", "Y", self.storage_path)
        fetched = get_note(note["id"], self.storage_path)
        self.assertEqual(fetched["title"], "X")
        self.assertEqual(fetched["content"], "Y")

    def test_fr007_empty_title_raises(self) -> None:
        """FR-007, NFR-005: update_note with empty title raises ValidationError."""
        note = create_note("Title", "Content", self.storage_path)
        with self.assertRaises(ValidationError):
            update_note(note["id"], "", "content", self.storage_path)

    def test_fr007_whitespace_only_title_raises(self) -> None:
        """FR-007, NFR-005, F-05: whitespace-only title raises ValidationError."""
        note = create_note("Title", "Content", self.storage_path)
        with self.assertRaises(ValidationError):
            update_note(note["id"], "  ", "content", self.storage_path)

    def test_fr007_empty_content_raises(self) -> None:
        """FR-007, NFR-005: update_note with empty content raises ValidationError."""
        note = create_note("Title", "Content", self.storage_path)
        with self.assertRaises(ValidationError):
            update_note(note["id"], "title", "", self.storage_path)

    def test_fr006_raises_not_found_for_absent_id(self) -> None:
        """FR-006, NFR-005: update_note raises NoteNotFoundError for a missing ID."""
        with self.assertRaises(NoteNotFoundError):
            update_note(999, "t", "c", self.storage_path)


class TestDeleteNote(unittest.TestCase):
    """Unit tests for FR-005, FR-006, NFR-003."""

    def setUp(self) -> None:
        self.storage_path = _make_temp_path()

    def tearDown(self) -> None:
        _cleanup(self.storage_path)

    def test_fr005_removes_note_from_storage(self) -> None:
        """FR-005: after delete_note, get_note raises NoteNotFoundError."""
        note = create_note("To delete", "Content", self.storage_path)
        delete_note(note["id"], self.storage_path)
        with self.assertRaises(NoteNotFoundError):
            get_note(note["id"], self.storage_path)

    def test_fr006_raises_not_found_for_absent_id(self) -> None:
        """FR-006, NFR-005: delete_note raises NoteNotFoundError for a missing ID."""
        with self.assertRaises(NoteNotFoundError):
            delete_note(999, self.storage_path)

    def test_nfr003_id_not_reused_after_delete(self) -> None:
        """NFR-003: create note (id=1), delete it, create again -> new id=2."""
        note1 = create_note("First", "Content", self.storage_path)
        delete_note(note1["id"], self.storage_path)
        note2 = create_note("Second", "Content", self.storage_path)
        self.assertEqual(note1["id"], 1)
        self.assertEqual(note2["id"], 2)


class TestStorage(unittest.TestCase):
    """Unit tests for NFR-001, F-01, F-02."""

    def setUp(self) -> None:
        self.storage_path = _make_temp_path()

    def tearDown(self) -> None:
        _cleanup(self.storage_path)

    def test_nfr001_absent_file_returns_default(self) -> None:
        """NFR-001: _load on a non-existent path returns the default empty state."""
        result = _load(self.storage_path)
        self.assertEqual(result, {"next_id": 1, "notes": []})

    def test_nfr001_data_survives_process_reload(self) -> None:
        """NFR-001: data written by _save is fully recovered by a subsequent _load."""
        data = {
            "next_id": 5,
            "notes": [{"id": 1, "title": "T", "content": "C"}],
        }
        _save(data, self.storage_path)
        loaded = _load(self.storage_path)
        self.assertEqual(loaded, data)

    def test_f02_corrupt_json_raises_storage_error(self) -> None:
        """NFR-001, NFR-005, F-02: _load on corrupt JSON raises StorageError
        whose message contains the word 'corrupt'."""
        with open(self.storage_path, "w", encoding="utf-8") as fh:
            fh.write("{invalid")
        with self.assertRaises(StorageError) as ctx:
            _load(self.storage_path)
        self.assertIn("corrupt", str(ctx.exception))

    def test_f01_atomic_write_no_tmp_file_remains(self) -> None:
        """NFR-001, F-01: no .tmp file exists on disk after _save returns."""
        _save({"next_id": 1, "notes": []}, self.storage_path)
        self.assertFalse(os.path.exists(self.storage_path + ".tmp"))


# ---------------------------------------------------------------------------
# T-06: CLI integration tests (subprocess-based, F-03)
# ---------------------------------------------------------------------------


class TestCLIIntegration(unittest.TestCase):
    """Subprocess-based CLI integration tests for FR-002, FR-005 (F-03)."""

    def setUp(self) -> None:
        self.storage_path = _make_temp_path()

    def tearDown(self) -> None:
        _cleanup(self.storage_path)

    def _run_cli(self, *args: str) -> subprocess.CompletedProcess:
        """Invoke ``python -m notes.cli`` in a child process.

        Passes *NOTES_PATH* so the child process uses the isolated temp file
        instead of the default ``notes.json`` in the working directory.
        """
        env = {**os.environ, "NOTES_PATH": self.storage_path}
        return subprocess.run(
            [sys.executable, "-m", "notes.cli", *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def test_fr002_empty_list_indication(self) -> None:
        """FR-002, NFR-004, F-03: list on an empty store exits 0 and prints
        'No notes found.' to stdout."""
        result = self._run_cli("list")
        self.assertEqual(result.returncode, 0)
        self.assertIn("No notes found.", result.stdout)

    def test_fr005_delete_confirmation(self) -> None:
        """FR-005, NFR-004, F-03: after creating a note, delete exits 0 and
        stdout contains 'Note 1 deleted.'"""
        create_result = self._run_cli(
            "create", "--title", "Test Note", "--content", "Test body"
        )
        self.assertEqual(create_result.returncode, 0)

        delete_result = self._run_cli("delete", "--id", "1")
        self.assertEqual(delete_result.returncode, 0)
        self.assertIn("Note 1 deleted.", delete_result.stdout)


if __name__ == "__main__":
    unittest.main()
