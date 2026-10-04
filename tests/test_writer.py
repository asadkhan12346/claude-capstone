import pytest

from doc_sync.writer import safe_write_document


def test_safe_write_document_creates_backup_and_updates_content(tmp_path) -> None:
    target = tmp_path / "README.md"
    target.write_text("before", encoding="utf-8")

    safe_write_document(target, "after", approved=True)

    assert target.read_text(encoding="utf-8") == "after"
    assert (tmp_path / "README.md.bak").exists()
    assert (tmp_path / "README.md.bak").read_text(encoding="utf-8") == "before"


def test_safe_write_document_refuses_secret_like_targets(tmp_path) -> None:
    target = tmp_path / ".env"
    target.write_text("TOKEN=abc", encoding="utf-8")

    with pytest.raises(ValueError):
        safe_write_document(target, "new", approved=True)
