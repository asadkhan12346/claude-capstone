"""Helpers for updating content between doc-sync markers."""

from __future__ import annotations

START_MARKER = "<!-- doc-sync:start -->"
END_MARKER = "<!-- doc-sync:end -->"


def _marker_counts(text: str) -> tuple[int, int]:
    return text.count(START_MARKER), text.count(END_MARKER)


def has_markers(text: str) -> bool:
    return START_MARKER in text and END_MARKER in text


def replace_marked_section(text: str, replacement: str) -> str:
    """Replace the content inside a single valid marker pair, or append a new pair."""
    start_count, end_count = _marker_counts(text)
    if start_count > 1 or end_count > 1:
        raise ValueError("duplicate doc-sync markers are not allowed")
    if start_count == 0 and end_count == 0:
        block = f"\n\n{START_MARKER}\n{replacement}\n{END_MARKER}"
        return f"{text.rstrip()}\n{block.strip()}\n" if text else f"{START_MARKER}\n{replacement}\n{END_MARKER}\n"
    if start_count != end_count:
        raise ValueError("unmatched doc-sync markers are not allowed")

    start_index = text.find(START_MARKER)
    end_index = text.find(END_MARKER, start_index + len(START_MARKER))
    if start_index == -1 or end_index == -1 or end_index < start_index:
        raise ValueError("malformed doc-sync marker pair")

    before = text[:start_index]
    after = text[end_index + len(END_MARKER) :]
    return f"{before}{START_MARKER}\n{replacement}\n{END_MARKER}{after}"
