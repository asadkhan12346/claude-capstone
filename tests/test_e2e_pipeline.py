"""End-to-end pipeline lifecycle tests using isolated temporary repositories."""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import orchestrator

_guard_spec = importlib.util.spec_from_file_location(
    "guard",
    Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "guard.py",
)
guard = importlib.util.module_from_spec(_guard_spec)  # type: ignore[arg-type]
_guard_spec.loader.exec_module(guard)  # type: ignore[union-attr]

ROOT = Path(__file__).resolve().parents[1]
PHASE_IDS = [
    "requirements", "architecture", "design-review", "planning",
    "implementation", "review", "verify", "pr",
]
ARTIFACTS = {
    "requirements": "# Requirements\n## Functional Requirements\nFR-001\n## Non-Functional Requirements\nNFR-001\n## Open Questions\nNone\n",
    "architecture": "# Architecture\nFR-001 NFR-001\n",
    "design-review": "# Design Review\nFR-001 NFR-001\nVerdict: APPROVE\n",
    "planning": "# Implementation Plan\nFR-001 NFR-001\n",
    "review": "# Review\nFR-001 NFR-001\n",
    "verify": "# Verification\nFR-001 NFR-001\n```text\nPASS\n```\n",
    "pr": "# PR\nFR-001 NFR-001\n",
}


class PipelineEndToEndTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        for directory in ("sdlc", "artifacts", ".claude/hooks"):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "sdlc" / "phases.json", self.root / "sdlc" / "phases.json")
        (self.root / "orchestrator.py").write_text("protected\n", encoding="utf-8")
        (self.root / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
        orchestrator.init_state(self.root)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_phase(self, phase_id: str) -> None:
        manifest = orchestrator.load_manifest(self.root)
        phase = orchestrator._get(manifest, phase_id)
        for relative_path in phase["owns"]:
            path = self.root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            content = ARTIFACTS.get(phase_id, f"implementation for {phase_id}\n")
            if phase_id == "pr" and relative_path.endswith("CHANGELOG.md"):
                content = "# Changelog\n\n## [Unreleased]\n\n### Added\n- Sample\n"
            path.write_text(content, encoding="utf-8")

    def submit_and_approve(self, phase_id: str) -> None:
        self.write_phase(phase_id)
        orchestrator.submit(self.root, phase_id)
        orchestrator.approve(self.root, phase_id, "human", confirmed=True)

    def test_complete_eight_phase_pipeline(self) -> None:
        for phase_id in PHASE_IDS:
            with self.subTest(phase=phase_id):
                self.submit_and_approve(phase_id)
        state = orchestrator.load_state(self.root)
        self.assertTrue(all(entry["status"] == "APPROVED" for entry in state["phases"].values()))
        self.assertEqual(orchestrator.derive(orchestrator.load_manifest(self.root), state)["approvalStatus"], "COMPLETE")
        self.assertEqual(orchestrator.check(self.root), [])

    def test_skip_ahead_is_blocked(self) -> None:
        with self.assertRaises(orchestrator.RuleViolation):
            orchestrator.submit(self.root, "architecture")

    def test_reject_returns_phase_to_active_for_resubmission(self) -> None:
        self.write_phase("requirements")
        orchestrator.submit(self.root, "requirements")
        state = orchestrator.reject(self.root, "requirements", "Clarify title rules", confirmed=True)
        self.assertEqual(state["phases"]["requirements"]["status"], "ACTIVE")
        self.assertEqual(state["phases"]["requirements"]["rejectionReason"], "Clarify title rules")
        self.submit_and_approve("requirements")
        self.assertEqual(orchestrator.load_state(self.root)["phases"]["architecture"]["status"], "ACTIVE")

    def test_reopen_requires_later_outputs_to_be_removed(self) -> None:
        self.submit_and_approve("requirements")
        self.write_phase("architecture")
        with self.assertRaisesRegex(orchestrator.RuleViolation, "later phases still have files"):
            orchestrator.reopen(self.root, "requirements", "Revisit", confirmed=True)

    def test_approved_artifact_tamper_is_detected(self) -> None:
        self.submit_and_approve("requirements")
        (self.root / "artifacts" / "requirements.md").write_text("tampered\n", encoding="utf-8")
        self.assertTrue(any("hash drift" in failure for failure in orchestrator.check(self.root)))

    def test_edit_between_submit_and_approval_is_refused(self) -> None:
        self.write_phase("requirements")
        orchestrator.submit(self.root, "requirements")
        (self.root / "artifacts" / "requirements.md").write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(orchestrator.RuleViolation, "hash drift"):
            orchestrator.approve(self.root, "requirements", "human", confirmed=True)

    def test_future_phase_artifact_fails_check(self) -> None:
        self.write_phase("architecture")
        failures = orchestrator.check(self.root)
        self.assertTrue(any("LOCKED phase architecture" in failure for failure in failures))

    def test_guard_tracks_active_phase_changes(self) -> None:
        self.assertIsNone(guard.evaluate(self.root, "Write", None, ["artifacts/requirements.md"]))
        self.assertIn("[R08]", guard.evaluate(self.root, "Write", None, ["artifacts/architecture.md"]) or "")
        self.submit_and_approve("requirements")
        self.assertIn("[R08]", guard.evaluate(self.root, "Write", None, ["artifacts/requirements.md"]) or "")
        self.assertIsNone(guard.evaluate(self.root, "Write", None, ["artifacts/architecture.md"]))


if __name__ == "__main__":
    unittest.main()
