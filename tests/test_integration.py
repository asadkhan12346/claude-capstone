from pathlib import Path

from doc_sync.pipeline import generate_documentation


def test_generate_documentation_end_to_end(tmp_path: Path) -> None:
    root = tmp_path / "demo-project"
    root.mkdir()
    (root / "pyproject.toml").write_text(
        """
[project]
name = "demo-app"
description = "A demo package"

[project.scripts]
doc-sync = "demo.cli:main"
""".strip(),
        encoding="utf-8",
    )
    (root / "README.md").write_text("# Demo App\n\n## Usage\nRun the tool locally.\n", encoding="utf-8")
    (root / "demo").mkdir()
    (root / "demo" / "__init__.py").write_text("__all__ = ['main']\n\n\ndef main() -> None:\n    \"\"\"Run the demo.\"\"\"\n    return None\n", encoding="utf-8")

    result = generate_documentation(root, yes=True)

    assert result["status"] == "ok"
    assert "demo-app" in (root / "README.md").read_text(encoding="utf-8")
    assert (root / "docs" / "api.md").exists()
