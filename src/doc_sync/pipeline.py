"""Primary documentation generation pipeline."""

from __future__ import annotations

from pathlib import Path

from doc_sync.approval import build_diff, prepare_approval
from doc_sync.extractors.project_config import extract_project_config
from doc_sync.extractors.python_api import extract_public_api_from_file
from doc_sync.markers import replace_marked_section
from doc_sync.rendering import render_empty_repository_readme, render_readme
from doc_sync.scanner import scan_repository
from doc_sync.security import contains_secret_value, is_secret_path
from doc_sync.writer import safe_write_document


def _read_existing(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _render_api_facts(python_files: list[Path]) -> dict[str, object]:
    modules: list[dict[str, object]] = []
    for file_path in sorted(python_files):
        if is_secret_path(file_path):
            continue
        try:
            entries = extract_public_api_from_file(file_path)
        except Exception:
            continue
        if entries:
            modules.append(
                {
                    "name": file_path.stem,
                    "functions": [entry for entry in entries if entry.get("kind") == "function"],
                    "classes": [entry for entry in entries if entry.get("kind") == "class"],
                }
            )
    return {"modules": modules}


def _apply_approved_document(target: Path, content: str, *, yes: bool) -> dict[str, object]:
    original = _read_existing(target)
    updated = replace_marked_section(original, content)
    if contains_secret_value(original) or contains_secret_value(updated):
        raise ValueError(f"Refusing to update secret-bearing target: {target}")
    diff = build_diff(original, updated)
    approval = prepare_approval(original, updated, approved=yes)
    if yes:
        safe_write_document(target, updated, approved=True)
    return {"approved": bool(approval["approved"]), "diff": diff, "content": updated}


def generate_documentation(root: str | Path, *, yes: bool = False) -> dict[str, object]:
    """Generate README and API docs for a target repository root."""
    target = Path(root).expanduser().resolve()
    if not target.exists() or not target.is_dir():
        raise ValueError(f"target directory is not valid: {target}")

    scan_result = scan_repository(target)
    python_files = scan_result.python_files
    readme_path = target / "README.md"
    docs_dir = target / "docs"
    api_path = docs_dir / "api.md"

    if not python_files:
        content = render_empty_repository_readme()
        result = _apply_approved_document(readme_path, content, yes=yes)
        return {"status": "ok", "warnings": scan_result.warnings, "readme": result["content"], "approval": result}

    facts = extract_project_config(target)
    readme_content = render_readme(facts)
    readme_result = _apply_approved_document(readme_path, readme_content, yes=yes)

    api_facts = _render_api_facts(python_files)
    api_content = (
        "# API Reference\n\n" + "\n".join(f"## {module['name']}" for module in api_facts.get("modules", []))
        if api_facts.get("modules")
        else "# API Reference\n\nNot Found\n"
    )
    docs_dir.mkdir(exist_ok=True)
    api_result = _apply_approved_document(api_path, api_content, yes=yes)

    return {
        "status": "ok",
        "warnings": scan_result.warnings,
        "readme": readme_result["content"],
        "api": api_result["content"],
        "readme_approval": readme_result,
        "api_approval": api_result,
    }
