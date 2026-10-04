"""Static extraction of public Python API facts."""

from __future__ import annotations

import ast
from pathlib import Path


def _get_default_value(default: ast.AST | None) -> str:
    if default is None:
        return ""
    return f" = {ast.unparse(default)}"


def _build_function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args: list[str] = []
    positional = list(node.args.posonlyargs) + list(node.args.args)
    for arg in positional:
        annotation = ast.unparse(arg.annotation) if arg.annotation is not None else "Any"
        args.append(f"{arg.arg}: {annotation}")

    if node.args.vararg is not None:
        args.append(f"*{node.args.vararg.arg}: {ast.unparse(node.args.vararg.annotation) if node.args.vararg.annotation is not None else 'Any'}")

    if node.args.kwonlyargs:
        if node.args.vararg is None:
            args.append("*")
        for index, kwarg in enumerate(node.args.kwonlyargs):
            annotation = ast.unparse(kwarg.annotation) if kwarg.annotation is not None else "Any"
            default = node.args.kw_defaults[index]
            args.append(f"{kwarg.arg}: {annotation}{_get_default_value(default)}")

    if node.args.kwarg is not None:
        args.append(f"**{node.args.kwarg.arg}: {ast.unparse(node.args.kwarg.annotation) if node.args.kwarg.annotation is not None else 'Any'}")

    if node.args.defaults:
        defaults_start = len(args) - len(node.args.defaults)
        for index, default in enumerate(node.args.defaults):
            pos = defaults_start + index
            if pos >= 0 and pos < len(args):
                if "=" not in args[pos]:
                    args[pos] = f"{args[pos]} = {ast.unparse(default)}"

    signature = "(" + ", ".join(args) + ")"
    return_annotation = ast.unparse(node.returns) if node.returns is not None else "None"
    return f"{signature} -> {return_annotation}"


def _build_class_signature(node: ast.ClassDef) -> str:
    init = None
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == "__init__":
            init = child
            break
    if init is None:
        return "() -> None"

    args = list(init.args.posonlyargs) + list(init.args.args)
    if args and args[0].arg in {"self", "cls"}:
        args = args[1:]

    formatted: list[str] = []
    for arg in args:
        annotation = ast.unparse(arg.annotation) if arg.annotation is not None else "Any"
        formatted.append(f"{arg.arg}: {annotation}")

    if init.args.vararg is not None:
        formatted.append(f"*{init.args.vararg.arg}: {ast.unparse(init.args.vararg.annotation) if init.args.vararg.annotation is not None else 'Any'}")

    if init.args.kwonlyargs:
        if init.args.vararg is None:
            formatted.append("*")
        for index, kwarg in enumerate(init.args.kwonlyargs):
            annotation = ast.unparse(kwarg.annotation) if kwarg.annotation is not None else "Any"
            default = init.args.kw_defaults[index]
            formatted.append(f"{kwarg.arg}: {annotation}{_get_default_value(default)}")

    if init.args.kwarg is not None:
        formatted.append(f"**{init.args.kwarg.arg}: {ast.unparse(init.args.kwarg.annotation) if init.args.kwarg.annotation is not None else 'Any'}")

    if init.args.defaults:
        defaults_start = len(formatted) - len(init.args.defaults)
        for index, default in enumerate(init.args.defaults):
            pos = defaults_start + index
            if pos >= 0 and pos < len(formatted):
                if "=" not in formatted[pos]:
                    formatted[pos] = f"{formatted[pos]} = {ast.unparse(default)}"

    return f"({', '.join(formatted)}) -> None"


def _literal_string_list(value: ast.AST | None) -> list[str] | None:
    if not isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        return None
    values: list[str] = []
    for item in value.elts:
        if isinstance(item, ast.Constant) and isinstance(item.value, str):
            values.append(item.value)
        else:
            return None
    return values


def extract_public_api(source: str, module_name: str = "__module__") -> list[dict[str, object]]:
    """Extract public functions, classes, and simple static re-exports from a Python module."""

    tree = ast.parse(source)
    exported_all: list[str] | None = None
    defined: dict[str, ast.AST] = {}
    imported: dict[str, str] = {}
    found_order: list[str] = []

    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
                exported_all = _literal_string_list(node.value)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name.startswith("_"):
                continue
            defined[node.name] = node
            found_order.append(node.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                imported_name = alias.asname or alias.name
                if imported_name.startswith("_"):
                    continue
                imported[imported_name] = alias.name
                found_order.append(imported_name)

    if exported_all is not None:
        selected_names = [name for name in exported_all if name in defined or name in imported]
    else:
        selected_names = [name for name in found_order if name in defined or name in imported]

    ordered: list[dict[str, object]] = []
    for stmt in tree.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and stmt.name in selected_names:
            ordered.append(
                {
                    "name": stmt.name,
                    "kind": "function",
                    "signature": _build_function_signature(stmt),
                    "docstring": ast.get_docstring(stmt, clean=True),
                    "module": module_name,
                }
            )
        elif isinstance(stmt, ast.ClassDef) and stmt.name in selected_names:
            ordered.append(
                {
                    "name": stmt.name,
                    "kind": "class",
                    "signature": _build_class_signature(stmt),
                    "docstring": ast.get_docstring(stmt, clean=True),
                    "module": module_name,
                }
            )

    if exported_all is not None:
        final: list[dict[str, object]] = []
        seen: set[str] = set()
        for name in selected_names:
            item = next((entry for entry in ordered if entry["name"] == name), None)
            if item is not None and name not in seen:
                final.append(item)
                seen.add(name)
            elif name in imported and name not in seen:
                final.append(
                    {
                        "name": name,
                        "kind": "reexport",
                        "signature": "()",
                        "docstring": None,
                        "module": module_name,
                    }
                )
                seen.add(name)
        return final

    return ordered


def extract_public_api_from_file(path: str | Path) -> list[dict[str, object]]:
    file_path = Path(path)
    return extract_public_api(file_path.read_text(encoding="utf-8"), module_name=file_path.stem)
