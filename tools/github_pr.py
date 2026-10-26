"""GitHub PR guardrail helper for the SDLC pipeline PR phase.

Subcommands
-----------
preflight   --owner ORG --repo REPO --head BRANCH [--base BASE]
            Checks: head is not main/master, remote is reachable, no open PR
            already exists for this head branch.
            Exit 0 = safe to proceed.  Exit 1 = blocker found.

check-files --files FILE [FILE ...]
            Checks: every file is on the approved staging list; no file looks
            like a credential or secret by name.
            Exit 0 = safe.  Exit 1 = blocked file found.

verify-pr   --url URL
            Confirms the PR URL is accessible and the PR is OPEN via gh api.
            Exit 0 = confirmed.  Exit 1 = not confirmed.

Authentication
--------------
Never stores or prints credentials.  Delegates all GitHub API calls to the
``gh`` CLI, which reads GITHUB_TOKEN or its own credential store.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence

# ---------------------------------------------------------------------------
# Allowed staging list — must match PR agent instructions exactly.
# Prefixes are matched: "artifacts" covers all files under artifacts/.
# ---------------------------------------------------------------------------
_ALLOWED_PREFIXES: tuple[str, ...] = (
    "artifacts/",
    "notes/",
    "tests/test_notes.py",
    "CHANGELOG.md",
    "sdlc/state.json",
    "sdlc/audit.log.jsonl",
)

# Filename patterns that suggest credentials or secrets.
_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\.env$", re.IGNORECASE),
    re.compile(r"^\.env\.", re.IGNORECASE),
    re.compile(r"credentials", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"\.pem$", re.IGNORECASE),
    re.compile(r"\.pfx$", re.IGNORECASE),
    re.compile(r"\.p12$", re.IGNORECASE),
    re.compile(r"^id_rsa", re.IGNORECASE),
    re.compile(r"^id_dsa", re.IGNORECASE),
    re.compile(r"^id_ecdsa", re.IGNORECASE),
    re.compile(r"^id_ed25519", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
)

_PROTECTED_BRANCHES: frozenset[str] = frozenset({"main", "master"})


# ---------------------------------------------------------------------------
# Subprocess helper
# ---------------------------------------------------------------------------


def _run(
    args: list[str], *, capture: bool = True
) -> tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        args,
        capture_output=capture,
        text=True,
    )
    return result.returncode, result.stdout or "", result.stderr or ""


# ---------------------------------------------------------------------------
# Guardrail: preflight
# ---------------------------------------------------------------------------


def cmd_preflight(owner: str, repo: str, head: str, base: str) -> int:
    """Check branch name and duplicate-PR status before staging.

    Returns 0 (safe) or 1 (blocked).
    """
    head_short = head.split("/")[-1] if "/" in head else head

    # Block protected branch names.
    if head_short.lower() in _PROTECTED_BRANCHES:
        print(
            f"BLOCKED: head branch {head!r} is a protected branch name. "
            "Create a feature branch (e.g. sdlc/<slug>) instead.",
            file=sys.stderr,
        )
        return 1

    # Check for an existing open PR with the same head branch.
    rc, stdout, stderr = _run([
        "gh", "pr", "list",
        "--repo", f"{owner}/{repo}",
        "--head", head,
        "--state", "open",
        "--json", "number,url,title",
    ])
    if rc != 0:
        # gh auth failure or network error — stop safely.
        print(
            f"BLOCKED: gh pr list failed (exit {rc}). "
            "Check gh authentication and network connectivity.\n"
            f"stderr: {stderr.strip()}",
            file=sys.stderr,
        )
        return 1

    try:
        prs: list[dict[str, object]] = json.loads(stdout) if stdout.strip() else []
    except json.JSONDecodeError:
        print(
            f"BLOCKED: could not parse gh pr list output: {stdout[:200]!r}",
            file=sys.stderr,
        )
        return 1

    if prs:
        first = prs[0]
        print(
            f"BLOCKED: an open PR already exists for branch {head!r}.\n"
            f"  PR #{first.get('number')} — {first.get('title')}\n"
            f"  URL: {first.get('url')}\n"
            "Close or merge the existing PR before creating a new one.",
            file=sys.stderr,
        )
        return 1

    print(f"preflight OK: no open PR for {head!r} against {owner}/{repo}.")
    return 0


# ---------------------------------------------------------------------------
# Guardrail: check-files
# ---------------------------------------------------------------------------


def _is_allowed(relative_path: str) -> bool:
    """Return True if relative_path is on the approved staging list."""
    norm = relative_path.replace("\\", "/").lstrip("/")
    for prefix in _ALLOWED_PREFIXES:
        if prefix.endswith("/"):
            if norm.startswith(prefix):
                return True
        else:
            if norm == prefix:
                return True
    return False


def _looks_like_secret(relative_path: str) -> re.Pattern[str] | None:
    """Return the matching pattern if the filename looks like a credential file."""
    name = Path(relative_path).name
    for pattern in _SECRET_PATTERNS:
        if pattern.search(name):
            return pattern
    return None


def cmd_check_files(files: list[str]) -> int:
    """Validate a list of files before staging.

    Returns 0 (all safe) or 1 (at least one file blocked).
    """
    blocked: list[str] = []

    for file_path in files:
        secret_pat = _looks_like_secret(file_path)
        if secret_pat:
            blocked.append(
                f"  {file_path!r} — filename matches secret pattern "
                f"{secret_pat.pattern!r}"
            )
            continue
        if not _is_allowed(file_path):
            blocked.append(
                f"  {file_path!r} — not on the approved staging list"
            )

    if blocked:
        print(
            "BLOCKED: the following files must not be staged:\n"
            + "\n".join(blocked),
            file=sys.stderr,
        )
        return 1

    print(f"check-files OK: {len(files)} file(s) approved for staging.")
    return 0


# ---------------------------------------------------------------------------
# Guardrail: verify-pr
# ---------------------------------------------------------------------------


def cmd_verify_pr(url: str) -> int:
    """Confirm a PR URL is accessible and the PR is open.

    Returns 0 (confirmed) or 1 (not confirmed).
    """
    rc, stdout, stderr = _run([
        "gh", "pr", "view", url,
        "--json", "url,state,number,title",
    ])
    if rc != 0:
        print(
            f"UNCONFIRMED: gh pr view failed (exit {rc}).\n"
            f"stderr: {stderr.strip()}\n"
            "Do not report a successful PR until this check passes.",
            file=sys.stderr,
        )
        return 1

    try:
        data: dict[str, object] = json.loads(stdout)
    except json.JSONDecodeError:
        print(
            f"UNCONFIRMED: could not parse gh pr view output: {stdout[:200]!r}",
            file=sys.stderr,
        )
        return 1

    state = str(data.get("state", "")).upper()
    if state != "OPEN":
        print(
            f"UNCONFIRMED: PR state is {state!r}, expected OPEN.\n"
            f"URL: {url}",
            file=sys.stderr,
        )
        return 1

    print(
        f"verify-pr CONFIRMED: PR #{data.get('number')} is OPEN.\n"
        f"  Title: {data.get('title')}\n"
        f"  URL:   {data.get('url')}"
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="GitHub PR guardrail helper for the SDLC pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pf = sub.add_parser("preflight", help="Check branch and duplicate-PR status.")
    pf.add_argument("--owner", required=True, help="GitHub org or user name.")
    pf.add_argument("--repo", required=True, help="Repository name (no org prefix).")
    pf.add_argument("--head", required=True, help="Feature branch to push.")
    pf.add_argument("--base", default="main", help="Target branch (default: main).")

    cf = sub.add_parser("check-files", help="Validate staged file list.")
    cf.add_argument(
        "--files", nargs="+", required=True, metavar="FILE",
        help="Relative paths of files about to be staged.",
    )

    vp = sub.add_parser("verify-pr", help="Confirm a PR URL is open.")
    vp.add_argument("--url", required=True, help="GitHub PR URL to verify.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "preflight":
        return cmd_preflight(args.owner, args.repo, args.head, args.base)
    if args.command == "check-files":
        return cmd_check_files(args.files)
    if args.command == "verify-pr":
        return cmd_verify_pr(args.url)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
