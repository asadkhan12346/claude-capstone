"""Notes package.

Re-exports the four domain exception classes so callers can use::

    from notes import NoteError, NoteNotFoundError, ValidationError, StorageError

without coupling to the internal ``notes.app`` module path.
"""

from notes.app import NoteError, NoteNotFoundError, StorageError, ValidationError

__all__ = ["NoteError", "NoteNotFoundError", "StorageError", "ValidationError"]
