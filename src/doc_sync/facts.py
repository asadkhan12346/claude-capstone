"""Fact model and conflict resolution for repository-derived documentation."""

from __future__ import annotations

from collections.abc import Iterable

NotFound = "Not Found"


def _looks_sensitive(value: object) -> bool:
    if value is None:
        return False
    text = str(value).strip().lower()
    if not text:
        return False
    secret_markers = (
        "token",
        "password",
        "passwd",
        "secret",
        "api_key",
        "api-key",
        "authorization",
        "private key",
        "private_key",
    )
    return any(marker in text for marker in secret_markers)


class FactModel:
    """Collect and resolve repository-derived facts with provenance."""

    def __init__(self) -> None:
        self._values: dict[str, list[str]] = {}

    def add(self, key: str, value: object) -> None:
        if not key:
            raise ValueError("fact key cannot be empty")
        if value is None:
            self._values.setdefault(key, []).append(NotFound)
            return
        if isinstance(value, str) and not value.strip():
            self._values.setdefault(key, []).append(NotFound)
            return
        if _looks_sensitive(value):
            self._values.setdefault(key, []).append(NotFound)
            return
        self._values.setdefault(key, []).append(str(value).strip())

    def resolve(self) -> dict[str, object]:
        resolved: dict[str, object] = {}
        conflicts: dict[str, list[str]] = {}
        for key, values in self._values.items():
            normalized = [value for value in values if value != NotFound]
            if not normalized:
                resolved[key] = NotFound
                continue
            unique_values = list(dict.fromkeys(normalized))
            if len(unique_values) > 1:
                conflicts[key] = unique_values
            resolved[key] = unique_values[0]
        resolved["conflicts"] = conflicts
        return resolved


def merge_values(existing: dict[str, object] | None, incoming: Iterable[tuple[str, object]]) -> dict[str, object]:
    """Merge resolved facts while preserving first-seen values and exposing conflicts."""
    model = FactModel()
    if existing:
        for key, value in existing.items():
            if key == "conflicts":
                continue
            model.add(key, value)
    for key, value in incoming:
        model.add(key, value)
    return model.resolve()
