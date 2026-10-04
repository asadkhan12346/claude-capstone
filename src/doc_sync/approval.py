"""Diff generation and approval checks for generated documentation."""

from __future__ import annotations

import difflib
import hashlib


def fingerprint_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_diff(original: str, updated: str) -> str:
    lines_original = original.splitlines(keepends=True)
    lines_updated = updated.splitlines(keepends=True)
    return "".join(difflib.unified_diff(lines_original, lines_updated, lineterm=""))


def prepare_approval(original: str, updated: str, *, approved: bool, fingerprint: str | None = None) -> dict[str, object]:
    current_fingerprint = fingerprint_text(original)
    if fingerprint is not None and fingerprint != current_fingerprint:
        raise ValueError("target content changed after the approval diff was generated")
    diff = build_diff(original, updated)
    return {"approved": bool(approved), "diff": diff, "fingerprint": current_fingerprint}
