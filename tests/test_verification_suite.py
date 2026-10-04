from __future__ import annotations

from pathlib import Path

import pytest

from doc_sync.cli import main
from doc_sync.extractors.project_config import extract_project_config
from doc_sync.pipeline import generate_documentation
from doc_sync.security import is_secret_path


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"


def test_unit_smoke_for_public_functions() -> None:
    result = extract_project_config(FIXTURE_ROOT / "normal")
    assert result["project_name"] == "fixture-normal"
    assert "doc-sync" in result["entry_points"]
    assert is_secret_path(".env") is True


def test_integration_normal_fixture(tmp_path: Path) -> None:
    source = FIXTURE_ROOT / "normal"
    target = tmp_path / "normal-copy"
    target.mkdir()
    for path in source.rglob("*"):
        if path.is_file():
            rel = path.relative_to(source)
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    result = generate_documentation(target, yes=True)

    assert result["status"] == "ok"
    readme = (target / "README.md").read_text(encoding="utf-8")
    assert "# Fixture Normal" in readme or "fixture-normal" in readme
    assert "## Usage" in readme
    assert "Not Found" in readme or "hello" in readme


def test_integration_empty_fixture(tmp_path: Path) -> None:
    source = FIXTURE_ROOT / "empty"
    target = tmp_path / "empty-copy"
    target.mkdir()
    for path in source.rglob("*"):
        if path.is_file():
            rel = path.relative_to(source)
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    result = generate_documentation(target, yes=True)

    assert result["status"] == "ok"
    readme = (target / "README.md").read_text(encoding="utf-8")
    assert "Repository is empty or contains no supported files" in readme


def test_integration_missing_file_fixture(tmp_path: Path) -> None:
    source = FIXTURE_ROOT / "missing"
    target = tmp_path / "missing-copy"
    target.mkdir()
    for path in source.rglob("*"):
        if path.is_file():
            rel = path.relative_to(source)
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    result = generate_documentation(target, yes=True)

    assert result["status"] == "ok"
    assert "Not Found" in (target / "README.md").read_text(encoding="utf-8")


def test_integration_simulated_failure_fixture(tmp_path: Path) -> None:
    source = FIXTURE_ROOT / "broken"
    target = tmp_path / "broken-copy"
    target.mkdir()
    for path in source.rglob("*"):
        if path.is_file():
            rel = path.relative_to(source)
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    result = generate_documentation(target, yes=True)

    assert result["status"] == "ok"
    assert "Not Found" in (target / "README.md").read_text(encoding="utf-8")


def test_secrets_are_not_leaked_into_output(tmp_path: Path) -> None:
    root = tmp_path / "secret-project"
    root.mkdir()
    (root / "pyproject.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")
    (root / ".env").write_text("TOKEN=super-secret-value\n", encoding="utf-8")
    (root / "README.md").write_text("# Demo\n\n## Usage\nRun locally.\n", encoding="utf-8")

    result = generate_documentation(root, yes=True)
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert result["status"] == "ok"
    assert "super-secret-value" not in readme
    assert "TOKEN" not in readme


def test_cli_main_runs_end_to_end_on_fixture_repo() -> None:
    target = FIXTURE_ROOT / "normal"
    exit_code = main([str(target), "--yes"])
    readme = (target / "README.md").read_text(encoding="utf-8")

    assert exit_code == 0
    assert (target / "README.md").exists()
    assert "fixture-normal" in readme.lower()
    assert "## Installation" in readme
    assert "## Usage" in readme
