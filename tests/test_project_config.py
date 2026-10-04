from pathlib import Path

from doc_sync.extractors.project_config import extract_project_config


def test_extract_project_config_reads_supported_files(tmp_path: Path) -> None:
    root = tmp_path / "demo"
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
    (root / "requirements.txt").write_text("requests>=2.0\nPyYAML>=6.0\n", encoding="utf-8")
    (root / ".env.example").write_text("API_URL=https://example.com\nDEBUG=false\n", encoding="utf-8")
    (root / "config.yaml").write_text("database:\n  host: localhost\n", encoding="utf-8")
    (root / "settings.json").write_text('{"feature": "enabled"}\n', encoding="utf-8")
    (root / "README.md").write_text(
        "# Demo App\n\nThis project syncs docs.\n\n## Usage\nRun the tool locally.\n",
        encoding="utf-8",
    )

    facts = extract_project_config(root)

    assert facts["project_name"] == "demo-app"
    assert facts["description"] == "A demo package"
    assert facts["dependencies"] == ["requests>=2.0", "PyYAML>=6.0"]
    assert facts["entry_points"] == {"doc-sync": "demo.cli:main"}
    config_vars = set(facts["config_variables"])
    assert {"API_URL", "DEBUG"}.issubset(config_vars)
    assert facts["overview"] == "This project syncs docs."
    assert facts["usage"] == "Run the tool locally."
    assert facts["warnings"] == []


def test_extract_project_config_skips_malformed_files_without_stopping(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    root.mkdir()

    (root / "pyproject.toml").write_text("[project\nname = 'broken'\n", encoding="utf-8")
    (root / "requirements.txt").write_text("packaging>=24\n", encoding="utf-8")
    (root / "README.md").write_text("# Broken\n\nIntro line.\n", encoding="utf-8")

    facts = extract_project_config(root)

    assert facts["dependencies"] == ["packaging>=24"]
    assert facts["project_name"] is None
    assert facts["warnings"]
