"""Fail-closed PreToolUse guard for destructive commands and phase writes."""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Any, NamedTuple
from urllib.parse import unquote, urlparse


class MalformedPayload(ValueError):
    """The incoming hook payload cannot be safely interpreted."""


class Rule(NamedTuple):
    id: str
    description: str
    matcher: Any
    reason: str
    safe_alternative: str


def _normalise_tool_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _decode_path(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme == "file":
        value = unquote(parsed.path)
        if re.match(r"^/[A-Za-z]:", value):
            value = value[1:]
        if parsed.netloc:
            value = f"//{parsed.netloc}{value}"
    return value.replace("\\", "/")


def parse_payload(raw: str) -> tuple[str, str | None, list[str]]:
    """Parse Claude Code PreToolUse hook payload.

    Claude Code sends exactly three tool shapes:
      Bash:                  {"tool_name":"Bash","tool_input":{"command":"..."}}
      Write/Edit/MultiEdit:  {"tool_name":"Write|Edit|MultiEdit","tool_input":{"file_path":"..."}}
      NotebookEdit:          {"tool_name":"NotebookEdit","tool_input":{"notebook_path":"..."}}
    Returns (tool_name, command_or_None, [paths]).
    """
    try:
        payload = json.loads(raw.lstrip("﻿"))
    except (json.JSONDecodeError, TypeError) as exc:
        raise MalformedPayload("input is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise MalformedPayload("payload must be a JSON object")
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if not isinstance(tool, str) or not tool:
        raise MalformedPayload("tool name is missing")
    if not isinstance(tool_input, dict):
        raise MalformedPayload("tool input must be an object")

    normalised = _normalise_tool_name(tool)

    # Shell tool: Bash
    if normalised == "bash":
        command = tool_input.get("command")
        if not isinstance(command, str) or not command.strip():
            raise MalformedPayload("shell tool has no command")
        return tool, command, []

    # Write-tool paths: Write, Edit, MultiEdit use file_path; NotebookEdit uses notebook_path
    write_tools = {"write", "edit", "multiedit", "notebookedit"}
    if normalised in write_tools:
        key = "notebook_path" if normalised == "notebookedit" else "file_path"
        path_val = tool_input.get(key)
        if not isinstance(path_val, str) or not path_val.strip():
            raise MalformedPayload("write tool has no target path")
        return tool, None, [_decode_path(path_val)]

    # Unknown tool: pass through (allow)
    return tool, None, []


def _split_commands(command: str) -> list[str]:
    segments: list[str] = []
    current: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(command):
        char = command[index]
        if char == "\\" and quote != "'" and index + 1 < len(command):
            current.extend((char, command[index + 1]))
            index += 2
            continue
        if char in {"'", '"', "`"}:
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
        if quote is None and (char in ";\n&|"):
            segment = "".join(current).strip()
            if segment:
                segments.append(segment)
            current = []
            if char in "&|" and index + 1 < len(command) and command[index + 1] == char:
                index += 2
                continue
        else:
            current.append(char)
        index += 1
    segment = "".join(current).strip()
    if segment:
        segments.append(segment)
    return segments


def _unwrap(command: str) -> str:
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return command.strip()
    while tokens:
        if tokens[0].lower() in {"sudo", "time", "nohup", "command", "exec"}:
            tokens.pop(0)
            continue
        if tokens[0].lower() == "env":
            tokens.pop(0)
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
            tokens.pop(0)
            continue
        break
    if tokens and tokens[0].lower() in {"bash", "sh"} and "-c" in tokens:
        return tokens[tokens.index("-c") + 1]
    if tokens and tokens[0].lower() in {"powershell", "pwsh"}:
        for option in ("-command", "-c"):
            if option in [token.lower() for token in tokens]:
                index = [token.lower() for token in tokens].index(option)
                return " ".join(tokens[index + 1 :])
    if tokens and tokens[0].lower() == "cmd" and "/c" in [token.lower() for token in tokens]:
        lowered = [token.lower() for token in tokens]
        return " ".join(tokens[lowered.index("/c") + 1 :])
    return " ".join(tokens)


def expand(command: str, depth: int = 0) -> list[str]:
    """Split command chains and unwrap common nested shell invocations."""
    if depth > 5:
        return [command]
    expanded: list[str] = []
    for segment in _split_commands(command):
        unwrapped = _unwrap(segment)
        if unwrapped != segment:
            expanded.extend(expand(unwrapped, depth + 1))
        else:
            expanded.append(unwrapped)
    return expanded


def _path_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=os.name != "nt")
    except ValueError:
        return command.split()


def written_paths(command: str) -> list[str]:
    """Extract likely destination paths from common shell write operations."""
    tokens = _path_tokens(command)
    paths: list[str] = []
    redirection = re.compile(r"(?:^|\s)(?:\d?>|>>|1>|2>)\s*([^\s]+)")
    paths.extend(match.group(1).strip("'\"") for match in redirection.finditer(command))
    if not tokens:
        return paths
    executable = Path(tokens[0].replace("\\", "/")).name.lower()
    args = tokens[1:]
    if executable in {"rm", "del", "erase", "remove-item", "rmdir"}:
        paths.extend(token for token in args if not token.startswith("-"))
    elif executable in {"mv", "move", "move-item", "cp", "copy", "copy-item"}:
        candidates = [token for token in args if not token.startswith("-")]
        if len(candidates) >= 2:
            paths.append(candidates[-1])
    elif executable in {"tee", "touch", "set-content", "add-content", "out-file"}:
        paths.extend(token for token in args if not token.startswith("-"))
    elif executable == "sed" and "-i" in args:
        paths.extend(token for token in args if not token.startswith("-"))
    elif executable == "git" and len(args) >= 2:
        operation = args[0].lower()
        if operation in {"rm", "mv", "restore", "checkout"}:
            paths.extend(token for token in args[1:] if not token.startswith("-"))
    elif executable in {"python", "python3", "py"} and "-c" in args:
        code = args[args.index("-c") + 1] if len(args) > args.index("-c") + 1 else ""
        for match in re.finditer(r"(?:open|write_text|write_bytes)\s*\(\s*['\"]([^'\"]+)", code):
            paths.append(match.group(1))
    return [_decode_path(path) for path in paths]


def _relative_path(root: Path, value: str) -> str:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return candidate.resolve(strict=False).relative_to(root.resolve()).as_posix()
    except ValueError:
        return candidate.as_posix()


def _hits(relative_path: str, entry: str) -> bool:
    path = relative_path.replace("\\", "/").strip("/").casefold()
    protected = entry.replace("\\", "/").strip("/").casefold()
    if path == protected:
        return True
    return path.startswith(protected + "/") or protected.startswith(path + "/")


def load_policy(root: Path) -> dict[str, Any]:
    """Load ownership policy; unreadable state leaves all owned paths read-only."""
    manifest_path = root / "sdlc" / "phases.json"
    state_path = root / "sdlc" / "state.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    owners = {
        owned_path: phase["id"]
        for phase in manifest["phases"]
        for owned_path in phase["owns"]
    }
    active_phase = None
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        active = [
            phase_id
            for phase_id, entry in state["phases"].items()
            if entry["status"] == "ACTIVE"
        ]
        if len(active) == 1:
            active_phase = active[0]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError):
        pass
    return {
        "protected": manifest["protected"],
        "owners": owners,
        "active_phase": active_phase,
        "active_files": [
            path for path, owner in owners.items() if owner == active_phase
        ],
    }


def _rule(id_: str, description: str, reason: str, alternative: str) -> Rule:
    return Rule(id_, description, None, reason, alternative)


RULES = (
    _rule("R01", "recursive deletion of a dangerous target", "This can erase the repository or system files.", "Delete only a specific disposable path."),
    _rule("R02", "filesystem destruction or unsafe permissions", "This can destroy a disk or expose files.", "Use a targeted, reversible command."),
    _rule("R03", "destructive Git history or working-tree operation", "This can discard shared or uncommitted work.", "Inspect status and use a narrow, reversible change."),
    _rule("R04", "force push or push to a protected branch", "This can overwrite shared branch history.", "Push a feature branch without force."),
    _rule("R05", "verification or shell safety bypass", "This bypasses checks or runs untrusted code.", "Use reviewed commands and normal hooks."),
    _rule("R06", "agent attempted a human-only approval action", "Only a human may approve, reject, or reopen a phase.", "Ask the human to run the orchestrator command in a terminal."),
    _rule("R07", "write to a protected pipeline file", "Pipeline controls must not be edited by phase agents.", "Write only an owned file in the ACTIVE phase."),
    _rule("R08", "write outside the ACTIVE phase ownership", "Only the active phase may modify its declared outputs.", "Check status and write only an active owned path."),
)


def _dangerous_command(command: str) -> str | None:
    text = command.strip()
    lower = text.lower()
    if re.search(r"\b(?:rm|rmdir|del|remove-item)\b[^\n]*\s-r(?:f|r)?\b", lower):
        targets = re.findall(r"(?<!\S)([^\s]+)", text)
        dangerous = {"/", "~", "$home", ".", "..", "*"}
        if any(target.strip("'\"").lower() in dangerous or ".git" in target.lower() for target in targets[1:]):
            return "R01"
    if re.search(r"\bmkfs(?:\.[\w-]+)?\b|\bdd\b[^\n]*\bof=/dev/(?!null\b)|>\s*/dev/sd\w*|chmod\s+-r\s+777\b", lower):
        return "R02"
    if re.search(r"git\s+reset\s+--hard|git\s+clean\s+[^\n]*-f|git\s+checkout\s+\.|git\s+restore\s+(?![^\n]*--staged)[^\n]*\.|git\s+branch\s+-D\s+(?:main|master)|filter-(?:branch|repo)|git\s+rebase\s+(?:main|master)", lower):
        return "R03"
    if re.search(r"git\s+push\b[^\n]*(?:--force(?!-with-lease)\b|\s-f(?:\s|$)|(?<!\S)\+\S+|\b(?:main|master)(?:\s|$))", lower):
        return "R04"
    if re.search(r"--no-verify|git\s+commit\s+-n\b|core\.hookspath|git\s+config\b[^\n]*hook|curl\b[^\n]*\|\s*(?:sh|bash)|\|\s*iex\b|base64\s+-d\b[^\n]*\|\s*(?:sh|bash)|eval\b[^\n]*\|\s*(?:sh|bash)", lower):
        return "R05"
    if re.search(r"\bpython(?:3)?\b[^\n]*\borchestrator\.py\s+(?:approve|reject|reopen)\b", lower):
        return "R06"
    return None


def _write_targets(command: str, tool_paths: list[str]) -> list[str]:
    targets = list(tool_paths)
    for expanded in expand(command):
        targets.extend(written_paths(expanded))
    return targets


def _format_denial(
    rule: Rule,
    tool: str,
    detail: str,
    policy: dict[str, Any],
    phase_line: bool = False,
) -> str:
    lines = [
        f"BLOCKED by SDLC guard [{rule.id}]",
        f"  Blocked: {tool}: {detail}",
        f"  Rule:    {rule.description}",
        f"  Why:     {rule.reason}",
        f"  Instead: {rule.safe_alternative}",
    ]
    if phase_line:
        active = policy["active_phase"] or "none"
        allowed = ", ".join(policy["active_files"]) or "none"
        lines.append(f"  Phase:   current phase '{active}' may write only: {allowed}")
    return "\n".join(lines)


def evaluate(
    root: Path, tool: str, command: str | None, tool_paths: list[str]
) -> str | None:
    """Return a formatted denial, or None when the operation is allowed."""
    policy = load_policy(root)
    if command:
        for expanded in [command, *expand(command)]:
            rule_id = _dangerous_command(expanded)
            if rule_id:
                rule = next(rule for rule in RULES if rule.id == rule_id)
                return _format_denial(rule, tool, expanded, policy)
    targets = _write_targets(command or "", tool_paths)
    for target in targets:
        relative = _relative_path(root, target)
        protected_match = next(
            (entry for entry in policy["protected"] if _hits(relative, entry)), None
        )
        if protected_match:
            rule = next(rule for rule in RULES if rule.id == "R07")
            return _format_denial(rule, tool, target, policy, phase_line=True)
        owner = next(
            (phase_id for path, phase_id in policy["owners"].items() if _hits(relative, path)),
            None,
        )
        if owner and owner != policy["active_phase"]:
            rule = next(rule for rule in RULES if rule.id == "R08")
            return _format_denial(rule, tool, target, policy, phase_line=True)
    return None


def _deny(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def main(root: Path | None = None) -> int:
    """Read one hook event and fail closed for malformed or unsafe requests."""
    root = root or Path(__file__).resolve().parents[2]
    try:
        raw = sys.stdin.buffer.read().decode("utf-8-sig")
        tool, command, paths = parse_payload(raw)
        denial = evaluate(root, tool, command, paths)
        return _deny(denial) if denial else 0
    except Exception as exc:
        return _deny(f"[FAIL-CLOSED] {type(exc).__name__}: hook input or policy could not be safely evaluated")


if __name__ == "__main__":
    raise SystemExit(main())
