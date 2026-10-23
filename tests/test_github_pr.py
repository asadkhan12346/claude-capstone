"""Tests for tools/github_pr.py guardrail helper.

Covers: auth failure, duplicate PR, invalid branch, unauthorized files,
secret filenames, failed verification, and successful PR confirmation.
All GitHub API calls are mocked via unittest.mock so no real credentials
or network access are required.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Load tools/github_pr.py without installing it as a package.
# ---------------------------------------------------------------------------
_TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
_spec = importlib.util.spec_from_file_location("github_pr", _TOOLS_DIR / "github_pr.py")
github_pr = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(github_pr)  # type: ignore[union-attr]


def _mock_run(returncode: int, stdout: str = "", stderr: str = "") -> MagicMock:
    """Return a patch for github_pr._run that yields fixed outputs."""
    mock = MagicMock(return_value=(returncode, stdout, stderr))
    return mock


class PreflightTests(unittest.TestCase):
    """github_pr.cmd_preflight guardrails."""

    def test_blocks_main_branch(self) -> None:
        rc = github_pr.cmd_preflight("org", "repo", "main", "main")
        self.assertEqual(rc, 1)

    def test_blocks_master_branch(self) -> None:
        rc = github_pr.cmd_preflight("org", "repo", "master", "main")
        self.assertEqual(rc, 1)

    def test_blocks_duplicate_open_pr(self) -> None:
        existing = json.dumps([{"number": 42, "url": "https://github.com/org/repo/pull/42", "title": "Old PR"}])
        with patch.object(github_pr, "_run", _mock_run(0, existing)):
            rc = github_pr.cmd_preflight("org", "repo", "sdlc/todo-cli", "main")
        self.assertEqual(rc, 1)

    def test_blocks_on_gh_auth_failure(self) -> None:
        with patch.object(github_pr, "_run", _mock_run(1, "", "authentication required")):
            rc = github_pr.cmd_preflight("org", "repo", "sdlc/todo-cli", "main")
        self.assertEqual(rc, 1)

    def test_blocks_on_malformed_gh_output(self) -> None:
        with patch.object(github_pr, "_run", _mock_run(0, "not json")):
            rc = github_pr.cmd_preflight("org", "repo", "sdlc/todo-cli", "main")
        self.assertEqual(rc, 1)

    def test_passes_clean_feature_branch(self) -> None:
        with patch.object(github_pr, "_run", _mock_run(0, "[]")):
            rc = github_pr.cmd_preflight("org", "repo", "sdlc/todo-cli", "main")
        self.assertEqual(rc, 0)

    def test_passes_empty_pr_list_response(self) -> None:
        # gh can return empty string instead of []
        with patch.object(github_pr, "_run", _mock_run(0, "")):
            rc = github_pr.cmd_preflight("org", "repo", "sdlc/feature", "main")
        self.assertEqual(rc, 0)


class CheckFilesTests(unittest.TestCase):
    """github_pr.cmd_check_files guardrails."""

    def test_passes_approved_artifacts(self) -> None:
        rc = github_pr.cmd_check_files([
            "artifacts/pr.md",
            "CHANGELOG.md",
            "todo/app.py",
            "tests/test_todo.py",
            "sdlc/state.json",
            "sdlc/audit.log.jsonl",
        ])
        self.assertEqual(rc, 0)

    def test_blocks_env_file(self) -> None:
        rc = github_pr.cmd_check_files([".env"])
        self.assertEqual(rc, 1)

    def test_blocks_dotenv_variant(self) -> None:
        rc = github_pr.cmd_check_files([".env.production"])
        self.assertEqual(rc, 1)

    def test_blocks_credentials_file(self) -> None:
        rc = github_pr.cmd_check_files(["config/credentials.json"])
        self.assertEqual(rc, 1)

    def test_blocks_token_file(self) -> None:
        rc = github_pr.cmd_check_files(["auth_token.txt"])
        self.assertEqual(rc, 1)

    def test_blocks_pem_file(self) -> None:
        rc = github_pr.cmd_check_files(["certs/server.pem"])
        self.assertEqual(rc, 1)

    def test_blocks_file_outside_allowed_list(self) -> None:
        rc = github_pr.cmd_check_files(["orchestrator.py"])
        self.assertEqual(rc, 1)

    def test_blocks_sdlc_phases_json_unauthorized(self) -> None:
        rc = github_pr.cmd_check_files(["sdlc/phases.json"])
        self.assertEqual(rc, 1)

    def test_blocks_mixed_list_with_one_unauthorized(self) -> None:
        rc = github_pr.cmd_check_files([
            "artifacts/pr.md",
            "CHANGELOG.md",
            ".env",
        ])
        self.assertEqual(rc, 1)

    def test_passes_all_sdlc_allowed_files(self) -> None:
        rc = github_pr.cmd_check_files([
            "artifacts/requirements.md",
            "artifacts/architecture.md",
            "artifacts/pr.md",
            "todo/__init__.py",
            "todo/app.py",
            "todo/cli.py",
            "tests/test_todo.py",
            "CHANGELOG.md",
            "sdlc/state.json",
            "sdlc/audit.log.jsonl",
        ])
        self.assertEqual(rc, 0)


class VerifyPrTests(unittest.TestCase):
    """github_pr.cmd_verify_pr guardrails."""

    def test_confirms_open_pr(self) -> None:
        data = json.dumps({
            "number": 7,
            "state": "OPEN",
            "title": "feat: Todo CLI SDLC capstone",
            "url": "https://github.com/org/repo/pull/7",
        })
        with patch.object(github_pr, "_run", _mock_run(0, data)):
            rc = github_pr.cmd_verify_pr("https://github.com/org/repo/pull/7")
        self.assertEqual(rc, 0)

    def test_rejects_closed_pr(self) -> None:
        data = json.dumps({
            "number": 7,
            "state": "CLOSED",
            "title": "feat: old",
            "url": "https://github.com/org/repo/pull/7",
        })
        with patch.object(github_pr, "_run", _mock_run(0, data)):
            rc = github_pr.cmd_verify_pr("https://github.com/org/repo/pull/7")
        self.assertEqual(rc, 1)

    def test_rejects_merged_pr(self) -> None:
        data = json.dumps({"number": 3, "state": "MERGED", "title": "x", "url": "u"})
        with patch.object(github_pr, "_run", _mock_run(0, data)):
            rc = github_pr.cmd_verify_pr("https://github.com/org/repo/pull/3")
        self.assertEqual(rc, 1)

    def test_rejects_gh_command_failure(self) -> None:
        with patch.object(github_pr, "_run", _mock_run(1, "", "not found")):
            rc = github_pr.cmd_verify_pr("https://github.com/org/repo/pull/99")
        self.assertEqual(rc, 1)

    def test_rejects_malformed_output(self) -> None:
        with patch.object(github_pr, "_run", _mock_run(0, "not-json")):
            rc = github_pr.cmd_verify_pr("https://github.com/org/repo/pull/1")
        self.assertEqual(rc, 1)


class MainCliTests(unittest.TestCase):
    """CLI entry-point integration."""

    def test_preflight_main_exits_1_for_main_branch(self) -> None:
        rc = github_pr.main(["preflight", "--owner", "o", "--repo", "r", "--head", "main"])
        self.assertEqual(rc, 1)

    def test_check_files_main_exits_0_for_approved_file(self) -> None:
        rc = github_pr.main(["check-files", "--files", "artifacts/pr.md"])
        self.assertEqual(rc, 0)

    def test_check_files_main_exits_1_for_env_file(self) -> None:
        rc = github_pr.main(["check-files", "--files", ".env"])
        self.assertEqual(rc, 1)

    def test_verify_pr_main_exits_1_on_gh_failure(self) -> None:
        with patch.object(github_pr, "_run", _mock_run(1, "", "not found")):
            rc = github_pr.main(["verify-pr", "--url", "https://github.com/o/r/pull/1"])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
