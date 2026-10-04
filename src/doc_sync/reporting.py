"""Sanitized warning reporting for pipeline errors."""

from __future__ import annotations

import re


def sanitize_warning(message: str) -> str:
    if not message:
        return "Not Found"
    redacted = re.sub(r"(?i)(token|password|api[_-]?key|secret)[\s:=]+[^\s\"'`]+", r"\1=[REDACTED]", message)
    return redacted
