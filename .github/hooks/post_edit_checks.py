"""Run pytest and scan changed files after workspace edits in VS Code Local."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token|token|password|passwd|secret)"
        r"\b\s*[:=]\s*[\"']?([A-Za-z0-9_./+=-]{12,})"
    ),
)
PLACEHOLDERS = {
    "changeme",
    "change_me",
    "dummy",
    "example",
    "not_found",
    "placeholder",
    "redacted",
    "sample",
    "test",
    "your_api_key",
    "your_token",
}
PATH_KEYS = {"file", "filename", "file_name", "filepath", "file_path", "path", "uri"}
EDIT_MARKERS = ("edit", "write", "patch", "replace", "create_file", "createfile")


class CheckError(Exception):
    """A safe-to-report validation setup or execution failure."""


def emit_block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))


def run_git(root: Path, *arguments: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=root,
            capture_output=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise CheckError("Unable to inspect repository changes.") from error
    if result.returncode != 0:
        raise CheckError("Unable to inspect repository changes.")
    return result.stdout


def is_edit_tool(tool_name: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", "_", tool_name.lower())
    return any(marker in normalized for marker in EDIT_MARKERS)


def input_file_paths(value: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower().replace("-", "_") in PATH_KEYS and isinstance(item, str):
                candidate = item
                if candidate.startswith("file://"):
                    parsed = urlparse(candidate)
                    candidate = unquote(parsed.path)
                    if os.name == "nt" and re.match(r"^/[A-Za-z]:", candidate):
                        candidate = candidate[1:]
                paths.append(candidate)
            else:
                paths.extend(input_file_paths(item))
    elif isinstance(value, list):
        for item in value:
            paths.extend(input_file_paths(item))
    return paths


def changed_paths(root: Path, event: dict[str, Any]) -> list[Path]:
    raw_paths: set[str] = set()
    for arguments in (
        ("diff", "--name-only", "--diff-filter=ACMRT", "-z"),
        ("diff", "--cached", "--name-only", "--diff-filter=ACMRT", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ):
        output = run_git(root, *arguments)
        raw_paths.update(os.fsdecode(item) for item in output.split(b"\0") if item)

    if is_edit_tool(str(event.get("tool_name", ""))):
        raw_paths.update(input_file_paths(event.get("tool_input", {})))

    paths: list[Path] = []
    for raw_path in raw_paths:
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = root / candidate
        try:
            resolved = candidate.resolve()
            resolved.relative_to(root)
        except (OSError, ValueError):
            continue
        paths.append(resolved)
    return sorted(set(paths), key=lambda path: str(path).casefold())


def snapshot_digest(paths: list[Path], root: Path) -> str:
    digest = hashlib.sha256()
    for path in paths:
        relative_path = os.fsencode(path.relative_to(root))
        digest.update(relative_path)
        digest.update(b"\0")
        try:
            digest.update(path.read_bytes() if path.is_file() else b"<missing>")
        except OSError as error:
            raise CheckError("Unable to read a changed file for validation.") from error
        digest.update(b"\0")
    return digest.hexdigest()


def scan_secrets(paths: list[Path], root: Path) -> list[str]:
    findings: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            content = path.read_bytes()
        except OSError as error:
            raise CheckError("Unable to scan a changed file.") from error
        if b"\0" in content:
            continue
        text = content.decode("utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern in SECRET_PATTERNS:
                match = pattern.search(line)
                if match is None:
                    continue
                candidate = match.group(1) if match.lastindex else ""
                if candidate.lower() in PLACEHOLDERS:
                    continue
                findings.append(f"{path.relative_to(root).as_posix()}:{line_number}")
                break
    return findings


def run_pytest(root: Path) -> tuple[bool, bool]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=root,
            capture_output=True,
            check=False,
            timeout=100,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, False
    if result.returncode == 5:
        return True, True
    return result.returncode == 0, False


def state_file(root: Path, event: dict[str, Any]) -> Path:
    identity = f"{root}\0{event.get('session_id', 'default')}".encode("utf-8", errors="replace")
    key = hashlib.sha256(identity).hexdigest()
    return Path(tempfile.gettempdir()) / "doc-sync-hook-state" / f"{key}.json"


def main() -> int:
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise CheckError("Invalid hook event; validation could not run.")
        root_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            check=False,
            timeout=15,
        )
        if root_result.returncode != 0:
            raise CheckError("Unable to locate the repository for validation.")
        root = Path(os.fsdecode(root_result.stdout).strip()).resolve()
        paths = changed_paths(root, event)
        if not paths:
            return 0

        digest = snapshot_digest(paths, root)
        saved_state = state_file(root, event)
        try:
            previous = json.loads(saved_state.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
        if previous.get("snapshot") == digest:
            return 0

        tests_passed, no_tests_collected = run_pytest(root)
        findings = scan_secrets(paths, root)
        if not tests_passed or findings:
            reasons: list[str] = []
            if not tests_passed:
                reasons.append("pytest failed or could not complete")
            if findings:
                locations = ", ".join(findings[:20])
                extra = " (more findings omitted)" if len(findings) > 20 else ""
                reasons.append(f"possible hardcoded secret at {locations}{extra}; values suppressed")
            emit_block("Post-edit checks failed: " + "; ".join(reasons) + ".")
            return 0

        saved_state.parent.mkdir(parents=True, exist_ok=True)
        saved_state.write_text(json.dumps({"snapshot": digest}), encoding="utf-8")
        if no_tests_collected:
            print(json.dumps({"systemMessage": "pytest found no tests; the changed-file secret scan passed."}))
        return 0
    except (CheckError, OSError, json.JSONDecodeError) as error:
        reason = str(error) if isinstance(error, CheckError) else "Post-edit checks could not complete."
        emit_block(reason)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())