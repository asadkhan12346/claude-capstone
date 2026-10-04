from doc_sync.pipeline import generate_documentation
from doc_sync.reporting import sanitize_warning


def test_generate_documentation_handles_empty_repo(tmp_path) -> None:
    root = tmp_path / "empty-project"
    root.mkdir()

    result = generate_documentation(root, yes=True)

    readme = (root / "README.md").read_text(encoding="utf-8")
    assert result["status"] == "ok"
    assert "Repository is empty or contains no supported files" in readme


def test_sanitize_warning_redacts_sensitive_values() -> None:
    warning = sanitize_warning("Token=abc123 from config.yaml")
    assert "abc123" not in warning
    assert "REDACTED" in warning or "Token" not in warning
