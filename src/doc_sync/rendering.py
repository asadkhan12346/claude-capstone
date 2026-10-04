"""Markdown rendering for README and API documentation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def _as_value(value: object, fallback: str = "Not Found") -> str:
    if value is None or value == "":
        return fallback
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value) or fallback
    return str(value)


def _render_list(items: object, fallback: str = "Not Found") -> str:
    if items is None:
        return fallback
    if isinstance(items, (list, tuple, set)):
        values = [str(item) for item in items if str(item).strip()]
        return "\n- " + "\n- ".join(values) if values else fallback
    text = str(items).strip()
    return text or fallback


def render_empty_repository_readme() -> str:
    return """# Project

## Overview

Repository is empty or contains no supported files.

## Usage

Not Found
"""


def render_readme(facts: Mapping[str, object]) -> str:
    project_name = _as_value(facts.get("project_name"), "Project")
    description = _as_value(facts.get("description"), "Not Found")
    dependencies = _as_value(facts.get("dependencies"), "Not Found")
    entry_points = facts.get("entry_points") or {}
    if isinstance(entry_points, Mapping):
        entry_lines = [f"- `{name}`: `{value}`" for name, value in entry_points.items()]
        entry_text = "\n".join(entry_lines) if entry_lines else "Not Found"
    else:
        entry_text = _as_value(entry_points, "Not Found")
    config_variables = _as_value(facts.get("config_variables"), "Not Found")
    overview = _as_value(facts.get("overview"), "Not Found")
    usage = _as_value(facts.get("usage"), "Not Found")
    installation = _as_value(facts.get("installation"), "Not Found")

    lines = [
        f"# {project_name}",
        "",
        description,
        "",
        "## Installation",
        installation,
        "",
        "## Dependencies",
        dependencies,
        "",
        "## Entry Points",
        entry_text,
        "",
        "## Configuration",
        config_variables,
        "",
        "## Overview",
        overview,
        "",
        "## Usage",
        usage,
    ]
    return "\n".join(lines) + "\n"


def render_api_docs(api_facts: Mapping[str, object]) -> str:
    modules = api_facts.get("modules") or []
    lines = ["# API Reference", ""]
    if not modules:
        lines.append("Not Found")
        return "\n".join(lines) + "\n"
    for module in modules:
        module_name = str((module or {}).get("name", "Not Found"))
        lines.append(f"## {module_name}")
        functions = (module or {}).get("functions") or []
        classes = (module or {}).get("classes") or []
        if functions:
            lines.append("### Functions")
            for function in functions:
                name = str((function or {}).get("name", "Not Found"))
                signature = str((function or {}).get("signature", "Not Found"))
                lines.append(f"- `{name}`: `{signature}`")
        if classes:
            lines.append("### Classes")
            for cls in classes:
                name = str((cls or {}).get("name", "Not Found"))
                signature = str((cls or {}).get("signature", "Not Found"))
                lines.append(f"- `{name}`: `{signature}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
