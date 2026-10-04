from pathlib import Path

import pytest

from doc_sync.security import SecretGuard, is_secret_path, sanitize_text


def test_secret_paths_are_rejected() -> None:
    assert is_secret_path(Path(".env")) is True
    assert is_secret_path(Path("secrets/keys/private.pem")) is True
    assert is_secret_path(Path("settings/credentials.json")) is True
    assert is_secret_path(Path("src/app.py")) is False


def test_secret_guard_redacts_matches_from_allowed_text() -> None:
    text = "TOKEN=abc123\nPASSWORD=letmein\nAPI_KEY=supersecret\n"

    sanitized = sanitize_text(text)

    assert "abc123" not in sanitized
    assert "letmein" not in sanitized
    assert "supersecret" not in sanitized
    assert "TOKEN=" in sanitized
    assert "PASSWORD=" in sanitized
    assert "API_KEY=" in sanitized


def test_secret_guard_fails_closed_on_uncertain_sanitization() -> None:
    guard = SecretGuard()

    with pytest.raises(ValueError):
        guard.sanitize_text("skipped")
