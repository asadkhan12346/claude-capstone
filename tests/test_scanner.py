from pathlib import Path

from doc_sync.scanner import ScanResult, scan_repository


def test_scan_repository_prunes_ignored_directories(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git" / "hooks").mkdir(parents=True)
    (repo / "tests" / "unit").mkdir(parents=True)
    (repo / "ci").mkdir(parents=True)
    (repo / "src").mkdir()

    (repo / "src" / "app.py").write_text("print('hello')\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (repo / "README.md").write_text("# demo\n", encoding="utf-8")
    (repo / ".git" / "config").write_text("[core]\n", encoding="utf-8")
    (repo / "tests" / "test_example.py").write_text("assert True\n", encoding="utf-8")
    (repo / "ci" / "pipeline.yml").write_text("steps: []\n", encoding="utf-8")

    result = scan_repository(repo)

    relative_paths = {path.relative_to(repo).as_posix() for path in result.files}
    assert {"src/app.py", "pyproject.toml", "README.md"} <= relative_paths
    assert ".git/config" not in relative_paths
    assert "tests/test_example.py" not in relative_paths
    assert "ci/pipeline.yml" not in relative_paths


def test_scan_repository_skips_symlinks_and_budget_overruns(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    source_dir = repo / "src"
    source_dir.mkdir()

    (source_dir / "safe.py").write_text("print('ok')\n", encoding="utf-8")
    (repo / "big.txt").write_text("x" * (6 * 1024 * 1024), encoding="utf-8")

    outside = tmp_path / "outside.py"
    outside.write_text("print('outside')\n", encoding="utf-8")
    link = repo / "escape.py"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        return

    result = scan_repository(repo)

    assert source_dir.joinpath("safe.py") in result.files
    assert link not in result.files
    assert any("out-of-root" in warning.lower() for warning in result.warnings)
    assert any("over" in warning.lower() or "budget" in warning.lower() for warning in result.warnings)
    assert isinstance(result, ScanResult)
