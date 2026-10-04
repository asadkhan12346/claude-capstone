"""Project and configuration fact extraction."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import tomllib
import yaml
from packaging.requirements import InvalidRequirement, Requirement

from doc_sync.scanner import scan_repository
from doc_sync.security import is_secret_path


def _coerce_string(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    return str(value).strip() or None


def _collect_keys(value: object, keys: list[str] | None = None) -> list[str]:
    keys = keys or []
    if isinstance(value, dict):
        for key in value:
            keys.append(str(key))
            keys.extend(_collect_keys(value[key], keys))
    elif isinstance(value, list):
        for item in value:
            keys.extend(_collect_keys(item, keys))
    return keys


def _read_requirements(path: Path) -> list[str]:
    deps: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-"):
            continue
        try:
            Requirement(stripped)
        except InvalidRequirement:
            continue
        deps.append(stripped)
    return deps


def _read_env_file(path: Path) -> list[str]:
    keys: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _ = stripped.split("=", 1)
        keys.append(key.strip())
    return keys


def _extract_readme_facts(path: Path) -> dict[str, str | None]:
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return {"overview": None, "usage": None}

    blocks = [block.strip() for block in re.split(r"\n\s*\n+", normalized) if block.strip()]
    paragraphs: list[str] = []
    usage: str | None = None

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if re.match(r"^#+\s*usage\b", lines[0], flags=re.IGNORECASE):
            usage = " ".join(line.strip() for line in lines[1:] if line.strip())
            continue
        if any(line.lower().startswith("usage") for line in lines[:2]):
            usage = " ".join(line.strip() for line in lines[1:] if line.strip())
            continue
        if lines[0].startswith("#"):
            continue
        paragraphs.append(" ".join(lines))

    overview = paragraphs[0] if paragraphs else None
    return {"overview": overview, "usage": usage}


def extract_project_config(root: str | os.PathLike[str] | Path) -> dict[str, object]:
    """Return project metadata facts discovered in config files."""

    project_root = Path(root).expanduser().resolve()
    result: dict[str, object] = {
        "project_name": None,
        "description": None,
        "dependencies": [],
        "entry_points": {},
        "config_variables": [],
        "overview": None,
        "usage": None,
        "warnings": [],
    }

    for file_path in scan_repository(project_root).files:
        if is_secret_path(file_path):
            continue

        filename = file_path.name.lower()
        try:
            if filename == "pyproject.toml":
                with file_path.open("rb") as handle:
                    data = tomllib.load(handle)
                project = data.get("project", {})
                if "name" in project:
                    result["project_name"] = _coerce_string(project.get("name"))
                if "description" in project:
                    result["description"] = _coerce_string(project.get("description"))
                scripts = project.get("scripts", {}) or {}
                if isinstance(scripts, dict):
                    result["entry_points"] = {str(key): str(value) for key, value in scripts.items()}
                if "dependencies" in project:
                    deps = project.get("dependencies", [])
                    if isinstance(deps, list):
                        result["dependencies"] = [str(item) for item in deps]

            elif filename == "requirements.txt":
                result["dependencies"] = _read_requirements(file_path)

            elif filename.endswith(".json"):
                with file_path.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)
                config_keys = _collect_keys(data)
                result["config_variables"].extend(config_keys)

            elif filename.endswith((".yaml", ".yml")):
                with file_path.open("r", encoding="utf-8") as handle:
                    data = yaml.safe_load(handle) or {}
                config_keys = _collect_keys(data)
                result["config_variables"].extend(config_keys)

            elif filename == ".env.example" or filename.startswith(".env"):
                result["config_variables"].extend(_read_env_file(file_path))

            elif filename.lower().endswith("readme.md") or filename.lower() == "readme.md":
                readme_facts = _extract_readme_facts(file_path)
                result["overview"] = readme_facts.get("overview")
                result["usage"] = readme_facts.get("usage")

        except Exception as exc:  # pragma: no cover - defensive guard
            result["warnings"].append(f"Skipped malformed config file: {file_path} ({exc})")

    result["config_variables"] = list(dict.fromkeys(str(item) for item in result["config_variables"]))
    result["dependencies"] = list(dict.fromkeys(str(item) for item in result["dependencies"]))
    return result
