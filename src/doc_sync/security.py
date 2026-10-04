"""Secret detection and sanitization for repository scanning."""

from __future__ import annotations

import re
from pathlib import Path

_SECRET_KEY_PATTERN = re.compile(
    r"(?i)(token|password|passwd|api[_-]?key|secret(?:[_-]?key)?|private[_-]?key|access[_-]?key|authorization)\s*[:=]\s*([^\s\"'`]+)"
)


def contains_secret_value(text: str | None) -> bool:
    """Return True when the content contains a secret-like assignment."""
    if text is None:
        return False
    return bool(_SECRET_KEY_PATTERN.search(text))

_SECRET_PATH_TOKENS = (
    "credentials",
    "secret",
    "token",
    "password",
    "passwd",
    "privatekey",
    "apikey",
    "auth",
)

_SECRET_SUFFIXES = (".key", ".pem", ".crt", ".pfx", ".p12")


def is_secret_path(path: str | Path) -> bool:
    """Return True when a path should never be opened for documentation ingestion."""

    candidate = Path(path)
    lower_name = candidate.name.lower()
    lower_parts = {part.lower() for part in candidate.parts}

    if lower_name == ".env":
        return True
    if lower_name in {".envrc"}:
        return True
    if lower_name.startswith(".env") and lower_name not in {".env.example", ".env.local"}:
        return True
    if candidate.suffix.lower() in _SECRET_SUFFIXES:
        return True
    if any(token in lower_name for token in _SECRET_PATH_TOKENS):
        return True
    if any(token in lower_parts for token in _SECRET_PATH_TOKENS):
        return True
    return False


def sanitize_text(text: str) -> str:
    """Replace sensitive assignments with a redacted placeholder.

    A text without any recognized secret assignment is treated as uncertain and raises
    so callers fail closed rather than silently assume no secrets are present.
    """

    if not text:
        raise ValueError("No secret-bearing content was provided for sanitization.")

    matches = list(_SECRET_KEY_PATTERN.finditer(text))
    if not matches:
        raise ValueError("No recognized secret assignment found; sanitization is uncertain.")

    sanitized = _SECRET_KEY_PATTERN.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)
    return sanitized


class SecretGuard:
    """Guard used to block secret files and redact secret values before parsing."""

    @staticmethod
    def should_skip(path: str | Path) -> bool:
        return is_secret_path(path)

    @staticmethod
    def sanitize_text(text: str) -> str:
        return sanitize_text(text)
