"""Focused tests for the SDLC orchestrator."""

from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

import orchestrator


class OrchestratorCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        source_root = Path(orchestrator.__file__).resolve().parent
        shutil.copytree(source_root / "sdlc", self.root / "sdlc")
        (self.root / ".claude" / "hooks").mkdir(parents=True)
        (self.root / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
        (self.root / "artifacts").mkdir()
        (self.root / "orchestrator.py").write_text("protected\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_artifacts(self, phase_id: str) -> None:
        manifest = orchestrator.load_manifest(self.root)
        phase = orchestrator._get(manifest, phase_id)
        contents = {
            "requirements": (
                "# Requirements\n## Functional Requirements\nFR-001\n"
                "NFR-001\n## Open Questions\nNone\n"
            ),
            "architecture": "# Architecture\nCovers FR-001 and NFR-001.\n",
            "design-review": "# Design Review\nFR-001 NFR-001\n\nVerdict: APPROVE\n",
            "planning": "# Plan\nFR-001 NFR-001\n",
            "review": "# Review\nFR-001 NFR-001\n",
            "verify": "# Verify\nFR-001 NFR-001\n```text\nPASS\n```\n",
            "pr": "# PR\nFR-001 NFR-001\n",
        }
        for relative_path in phase["owns"]:
            path = self.root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents.get(phase_id, "implementation\n"), encoding="utf-8")

    def approve_phase(self, phase_id: str) -> None:
        orchestrator.approve(self.root, phase_id, "human", confirmed=True)

    def submit_and_approve(self, phase_id: str) -> None:
        self.write_artifacts(phase_id)
        orchestrator.submit(self.root, phase_id)
        self.approve_phase(phase_id)

    def test_initial_state_and_derived_status(self) -> None:
        state = orchestrator.init_state(self.root)
        statuses = [entry["status"] for entry in state["phases"].values()]
        self.assertEqual(statuses, ["ACTIVE"] + ["LOCKED"] * 7)
        derived = orchestrator.derive(orchestrator.load_manifest(self.root), state)
        self.assertEqual(derived["currentPhase"], "requirements")
        self.assertEqual(orchestrator.load_state(self.root), state)

    def test_locked_phase_cannot_be_submitted_and_is_audited(self) -> None:
        orchestrator.init_state(self.root)
        with self.assertRaises(orchestrator.RuleViolation):
            orchestrator.submit(self.root, "architecture")
        audit_path = self.root / "sdlc" / "audit.log.jsonl"
        events = [
            json.loads(line)
            for line in audit_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(events[-1]["result"], "refused")
        self.assertEqual(events[-1]["action"], "submit")

    def test_submit_then_approve_activates_next_phase(self) -> None:
        orchestrator.init_state(self.root)
        self.write_artifacts("requirements")
        submitted = orchestrator.submit(self.root, "requirements")
        self.assertEqual(
            submitted["phases"]["requirements"]["status"], "AWAITING_APPROVAL"
        )
        approved = orchestrator.approve(self.root, "requirements", "human", confirmed=True)
        self.assertEqual(approved["phases"]["requirements"]["status"], "APPROVED")
        self.assertEqual(approved["phases"]["architecture"]["status"], "ACTIVE")

    def test_hash_drift_refuses_approval(self) -> None:
        orchestrator.init_state(self.root)
        self.write_artifacts("requirements")
        orchestrator.submit(self.root, "requirements")
        artifact = self.root / "artifacts" / "requirements.md"
        artifact.write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(orchestrator.RuleViolation, "hash drift"):
            orchestrator.approve(self.root, "requirements", "human", confirmed=True)

    def test_reject_clears_hashes_and_returns_phase_to_active(self) -> None:
        orchestrator.init_state(self.root)
        self.write_artifacts("requirements")
        orchestrator.submit(self.root, "requirements")
        state = orchestrator.reject(
            self.root, "requirements", "Please clarify", confirmed=True
        )
        entry = state["phases"]["requirements"]
        self.assertEqual(entry["status"], "ACTIVE")
        self.assertEqual(entry["hashes"], {})
        self.assertEqual(entry["rejectionReason"], "Please clarify")
        self.assertEqual(state["phases"]["architecture"]["status"], "LOCKED")

    def test_human_approval_requires_tty_confirmation(self) -> None:
        orchestrator.init_state(self.root)
        self.write_artifacts("requirements")
        orchestrator.submit(self.root, "requirements")
        with patch.object(orchestrator.sys.stdin, "isatty", return_value=False):
            with self.assertRaisesRegex(
                orchestrator.RuleViolation, "must be run by a human"
            ):
                orchestrator.approve(self.root, "requirements", "human")

    def test_reopen_refuses_until_later_outputs_are_removed(self) -> None:
        orchestrator.init_state(self.root)
        self.submit_and_approve("requirements")
        self.submit_and_approve("architecture")
        with self.assertRaisesRegex(
            orchestrator.RuleViolation, "later phases still have files"
        ):
            orchestrator.reopen(
                self.root, "requirements", "Revisit", confirmed=True
            )

    def test_check_detects_locked_outputs_and_missing_protected_path(self) -> None:
        orchestrator.init_state(self.root)
        self.write_artifacts("architecture")
        (self.root / "orchestrator.py").unlink()
        failures = orchestrator.check(self.root)
        self.assertTrue(any("LOCKED phase architecture" in failure for failure in failures))
        self.assertTrue(
            any("protected path missing: orchestrator.py" in failure for failure in failures)
        )

    def test_missing_manifest_returns_rule_violation_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            error_output = io.StringIO()

            with redirect_stderr(error_output):
                exit_code = orchestrator.main(["status"], root=root)

        self.assertEqual(exit_code, 1)
        self.assertIn("RULE VIOLATION:", error_output.getvalue())
        self.assertIn("Restore a valid manifest", error_output.getvalue())

    def test_invalid_cli_syntax_returns_usage_exit_code(self) -> None:
        error_output = io.StringIO()
        with redirect_stderr(error_output):
            exit_code = orchestrator.main(["not-a-command"], root=self.root)

        self.assertEqual(exit_code, 2)
        self.assertIn("usage:", error_output.getvalue())

    def test_second_submit_raises_rule_violation(self) -> None:
        """AWAITING_APPROVAL phase cannot be submitted again; orchestrator must check status first."""
        orchestrator.init_state(self.root)
        self.write_artifacts("requirements")
        orchestrator.submit(self.root, "requirements")
        state = orchestrator.load_state(self.root)
        self.assertEqual(state["phases"]["requirements"]["status"], "AWAITING_APPROVAL")
        with self.assertRaisesRegex(orchestrator.RuleViolation, "AWAITING_APPROVAL"):
            orchestrator.submit(self.root, "requirements")
        # Status unchanged after failed second submit
        state_after = orchestrator.load_state(self.root)
        self.assertEqual(state_after["phases"]["requirements"]["status"], "AWAITING_APPROVAL")


if __name__ == "__main__":
    unittest.main()