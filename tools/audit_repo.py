"""Read-only checks for the clean, pre-live-run capstone repository."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import orchestrator
from hooks import guard

EXPECTED_PHASES = [
    "requirements",
    "architecture",
    "design-review",
    "planning",
    "implementation",
    "review",
    "verify",
    "pr",
]


def _agent_owned_files(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^## Allowed files\s*$(.*?)(?=^## |\Z)", text)
    if match is None:
        return []
    return re.findall(r"`([^`]+)`", match.group(1))


def _check(label: str, condition: bool, failures: list[str]) -> None:
    print(f"{'PASS' if condition else 'FAIL'}: {label}")
    if not condition:
        failures.append(label)


def run_audit(root: Path = ROOT) -> int:
    """Run all clean-state checks without creating or modifying files."""
    failures: list[str] = []
    manifest_path = root / "sdlc" / "phases.json"
    contract_path = root / "docs" / "CONTRACT.md"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        phases = sorted(manifest["phases"], key=lambda phase: phase["order"])
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"FAIL: manifest can be read ({type(exc).__name__})")
        return 1

    _check("contract exists", contract_path.is_file(), failures)
    _check("manifest has eight ordered phases", [p["id"] for p in phases] == EXPECTED_PHASES, failures)
    owned = [path for phase in phases for path in phase["owns"]]
    _check("phase ownership does not overlap", len(owned) == len(set(owned)), failures)
    _check("eight agents exist", all((root / p["agent"]).is_file() for p in phases), failures)
    _check("eight prompts exist", all((root / p["prompt"]).is_file() for p in phases), failures)
    skill_names = ["requirements", "verify", "pr"]
    _check("three skills exist", all((root / ".github" / "skills" / name / "SKILL.md").is_file() for name in skill_names), failures)
    _check("shared instructions exist", (root / ".github" / "copilot-instructions.md").is_file(), failures)

    try:
        hooks_config = json.loads((root / ".github" / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        hook_entries = hooks_config["hooks"]["PreToolUse"]
        hook_wired = any("hooks/guard.py" in entry.get("command", "") for entry in hook_entries)
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError):
        hook_wired = False
    _check("hook files exist and registration points to guard", (root / "hooks" / "guard.py").is_file() and hook_wired, failures)
    _check("orchestrator exists", (root / "orchestrator.py").is_file(), failures)
    _check("state exists", (root / "sdlc" / "state.json").is_file(), failures)

    try:
        state = orchestrator.load_state(root, manifest)
        statuses = [state["phases"][phase_id]["status"] for phase_id in EXPECTED_PHASES]
        state_is_initial = statuses == ["ACTIVE"] + ["LOCKED"] * 7
    except orchestrator.RuleViolation:
        state_is_initial = False
    _check("real state is initial", state_is_initial, failures)
    try:
        status_ok = orchestrator.derive(manifest, state)["currentPhase"] == "requirements"
    except (UnboundLocalError, KeyError, TypeError):
        status_ok = False
    _check("orchestrator status derives active phase", status_ok, failures)

    agent_files_match = all(
        _agent_owned_files(root / phase["agent"]) == phase["owns"]
        for phase in phases
        if (root / phase["agent"]).is_file()
    )
    _check("agent Allowed files match manifest", agent_files_match, failures)
    _check("guard blocks R03", "[R03]" in (guard.evaluate(root, "run_in_terminal", "git reset --hard", []) or ""), failures)
    _check("guard blocks R06", "[R06]" in (guard.evaluate(root, "run_in_terminal", "python orchestrator.py approve requirements --by agent", []) or ""), failures)
    _check("guard allows git status", guard.evaluate(root, "run_in_terminal", "git status", []) is None, failures)
    _check("README and runbook exist", (root / "README.md").is_file() and (root / "docs" / "RUNBOOK.md").is_file(), failures)
    _check("hook README exists", (root / "hooks" / "README.md").is_file(), failures)
    _check("no live phase artifacts exist", not any((root / path).exists() for path in owned), failures)
    _check("user story exists", (root / "user_story.md").is_file(), failures)
    _check("audit log file exists", (root / "sdlc" / "audit.log.jsonl").is_file(), failures)

    try:
        completed = subprocess.run(
            [sys.executable, str(root / "orchestrator.py"), "status", "--json"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        command_ok = completed.returncode == 0 and json.loads(completed.stdout)["currentPhase"] == "requirements"
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, KeyError, TypeError):
        command_ok = False
    _check("status CLI runs successfully", command_ok, failures)

    print(f"Audit result: {'PASS' if not failures else 'FAIL'} ({len(failures)} failed checks)")
    return 1 if failures else 0


def main() -> int:
    """Return the audit process status."""
    return run_audit()


if __name__ == "__main__":
    raise SystemExit(main())
