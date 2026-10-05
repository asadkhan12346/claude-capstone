"""Documentation links, paths, phase tables, and runbook checks."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_documented_files_and_markdown_links_resolve(self) -> None:
        for markdown in (ROOT / "README.md", ROOT / "docs" / "CONTRACT.md", ROOT / "docs" / "RUNBOOK.md", ROOT / ".claude" / "hooks" / "README.md"):
            text = markdown.read_text(encoding="utf-8")
            for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                path_part = target.split("#", 1)[0]
                resolved = (markdown.parent / path_part).resolve()
                with self.subTest(document=markdown.relative_to(ROOT), link=label):
                    self.assertTrue(resolved.exists(), f"broken link target: {target}")

    def test_readme_tree_paths_exist(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        tree = readme.split("## Repository layout", 1)[1].split("## Quick start", 1)[0]
        paths = re.findall(r"(?:├──|└──)\s+([^\s#]+)", tree)
        for path in paths:
            normalized = path.rstrip("/")
            with self.subTest(path=normalized):
                self.assertTrue((ROOT / normalized).exists(), f"missing tree path: {normalized}")

    def test_contract_phase_table_matches_manifest(self) -> None:
        manifest = json.loads((ROOT / "sdlc" / "phases.json").read_text(encoding="utf-8"))
        phases = sorted(manifest["phases"], key=lambda phase: phase["order"])
        contract = (ROOT / "docs" / "CONTRACT.md").read_text(encoding="utf-8")
        for phase in phases:
            with self.subTest(phase=phase["id"]):
                self.assertIn(f"| {phase['order']} | {phase['id']} |", contract)
                self.assertIn(phase["agent"], contract)
                self.assertIn(phase["prompt"], contract)

    def test_readme_has_both_mermaid_diagrams_and_valid_commands(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(readme.count("```mermaid"), 2)
        for command in (
            "python orchestrator.py status [--json]",
            "python orchestrator.py next",
            "python orchestrator.py submit <phase>",
            "python -m unittest discover -s tests -v",
            "python -m compileall -q .",
            "python tools/audit_repo.py",
        ):
            with self.subTest(command=command):
                self.assertIn(f"`{command}`", readme)

    def test_runbook_has_fourteen_steps(self) -> None:
        runbook = (ROOT / "docs" / "RUNBOOK.md").read_text(encoding="utf-8")
        headings = re.findall(r"(?m)^## (\d+)\.", runbook)
        self.assertEqual(headings, [str(number) for number in range(1, 15)])
        for number in range(1, 15):
            with self.subTest(step=number):
                self.assertRegex(runbook, rf"(?m)^## {number}\. .+\n")


if __name__ == "__main__":
    unittest.main()
