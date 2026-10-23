"""Structural checks for the phase manifest and Claude Code configuration."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PHASES = [
    "requirements", "architecture", "design-review", "planning",
    "implementation", "review", "verify", "pr",
]


def allowed_files(agent_text: str) -> list[str]:
    match = re.search(r"(?ms)^## Allowed files\s*$(.*?)(?=^## |\Z)", agent_text)
    return re.findall(r"`([^`]+)`", match.group(1)) if match else []


def frontmatter(text: str) -> str:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if match is None:
        raise AssertionError("missing YAML frontmatter")
    return match.group(1)


class ConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / "sdlc" / "phases.json").read_text(encoding="utf-8"))
        cls.phases = sorted(cls.manifest["phases"], key=lambda phase: phase["order"])

    def test_eight_phase_agent_prompt_and_contract_files_exist(self) -> None:
        self.assertEqual([phase["id"] for phase in self.phases], EXPECTED_PHASES)
        self.assertTrue((ROOT / "docs" / "CONTRACT.md").is_file())
        for phase in self.phases:
            with self.subTest(phase=phase["id"]):
                self.assertTrue((ROOT / phase["agent"]).is_file())
                self.assertTrue((ROOT / phase["prompt"]).is_file())
                self.assertIn(phase["id"], (ROOT / "docs" / "CONTRACT.md").read_text(encoding="utf-8"))

    def test_agent_and_prompt_frontmatter_and_phase_names_match(self) -> None:
        for phase in self.phases:
            agent_text = (ROOT / phase["agent"]).read_text(encoding="utf-8")
            prompt_text = (ROOT / phase["prompt"]).read_text(encoding="utf-8")
            with self.subTest(phase=phase["id"]):
                self.assertRegex(frontmatter(agent_text), rf"(?m)^name: {re.escape(phase['id'])}$")
                self.assertRegex(frontmatter(prompt_text), r"(?m)^description: ")

    def test_agent_ownership_and_approval_gate_match_manifest(self) -> None:
        bodies: set[str] = set()
        for phase in self.phases:
            path = ROOT / phase["agent"]
            text = path.read_text(encoding="utf-8")
            body = text.split("---", 2)[-1].strip()
            with self.subTest(phase=phase["id"]):
                self.assertEqual(allowed_files(text), phase["owns"])
                self.assertIn(f"Awaiting human approval. Run: python orchestrator.py approve {phase['id']} --by <your-name>", text)
                for protected in ("sdlc/", "orchestrator.py", ".claude/hooks/**", ".claude/settings.json"):
                    self.assertIn(protected, text)
                self.assertNotIn(body, bodies)
                bodies.add(body)

    def test_tools_are_scoped_to_roles(self) -> None:
        requirements = (ROOT / ".claude" / "agents" / "requirements.md").read_text(encoding="utf-8")
        architecture = (ROOT / ".claude" / "agents" / "architecture.md").read_text(encoding="utf-8")
        implementation = (ROOT / ".claude" / "agents" / "implementation.md").read_text(encoding="utf-8")
        review = (ROOT / ".claude" / "agents" / "review.md").read_text(encoding="utf-8")
        verify = (ROOT / ".claude" / "agents" / "verify.md").read_text(encoding="utf-8")
        pr = (ROOT / ".claude" / "agents" / "pr.md").read_text(encoding="utf-8")
        self.assertNotIn("Bash", frontmatter(requirements))
        self.assertNotIn("Bash", frontmatter(architecture))
        self.assertIn("Bash", frontmatter(implementation))
        self.assertIn("Bash", frontmatter(review))
        self.assertIn("Bash", frontmatter(verify))
        self.assertIn("Bash", frontmatter(pr))

    def test_skills_and_hook_registration(self) -> None:
        for skill in ("verify", "pr"):
            text = (ROOT / ".claude" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertRegex(frontmatter(text), rf"(?m)^name: {re.escape(skill)}$")
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        entry = settings["hooks"]["PreToolUse"][0]
        self.assertIn(".claude/hooks/guard.py", entry["hooks"][0]["command"])

    def test_contract_phase_rows_match_manifest(self) -> None:
        contract = (ROOT / "docs" / "CONTRACT.md").read_text(encoding="utf-8")
        for phase in self.phases:
            with self.subTest(phase=phase["id"]):
                self.assertIn(f"| {phase['order']} | {phase['id']} |", contract)
                self.assertIn(f"`{phase['agent']}`", contract)
                self.assertIn(f"`{phase['prompt']}`", contract)
                for owned in phase["owns"]:
                    self.assertIn(f"`{owned}`", contract)


if __name__ == "__main__":
    unittest.main()
