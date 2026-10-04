"""Repository scanning utilities for the documentation sync tool."""

from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

MAX_SUPPORTED_FILES = 1000
MAX_SINGLE_FILE_BYTES = 5 * 1024 * 1024
MAX_TOTAL_SCAN_BYTES = 100 * 1024 * 1024

EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".nox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "__pycache__",
    "build",
    "dist",
    "site-packages",
    "node_modules",
    "tests",
    "ci",
}

SUPPORTED_SUFFIXES = {
    ".py",
    ".toml",
    ".json",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".env",
    ".txt",
    ".md",
}

SUPPORTED_FILE_NAMES = {
    "readme.md",
    "readme.rst",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements.in",
    "setup.cfg",
    "setup.py",
    ".env",
    ".env.example",
    ".env.local",
}


@dataclass(slots=True)
class ScanResult:
    """Collected files and warnings from a repository scan."""

    root: Path
    files: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    total_bytes: int = 0

    @property
    def python_files(self) -> list[Path]:
        return [path for path in self.files if path.suffix.lower() == ".py"]

    @property
    def has_python_files(self) -> bool:
        return bool(self.python_files)

    def __iter__(self) -> Iterator[Path]:
        return iter(self.files)

    def __len__(self) -> int:
        return len(self.files)

    def __bool__(self) -> bool:
        return bool(self.files)


def _should_exclude_directory(name: str) -> bool:
    normalized = name.lower()
    return normalized in EXCLUDED_DIR_NAMES or normalized.startswith(".") and normalized.endswith("cache")


def _is_supported_file(path: Path) -> bool:
    name = path.name.lower()
    if name in SUPPORTED_FILE_NAMES:
        return True
    if path.suffix.lower() in SUPPORTED_SUFFIXES:
        return True
    return name.startswith("requirements") or name.startswith(".env")


def _is_within_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def iter_supported_files(root: str | os.PathLike[str] | Path) -> list[Path]:
    """Return all supported files under a root without following out-of-root symlinks."""

    target = Path(root).expanduser().resolve(strict=True)
    if not target.is_dir():
        raise ValueError(f"Target is not a directory: {target}")

    files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(target, topdown=True, followlinks=False):
        root_dir = Path(current_root)
        dirnames[:] = [
            directory
            for directory in dirnames
            if not _should_exclude_directory(directory)
        ]

        for directory in list(dirnames):
            directory_path = root_dir / directory
            if directory_path.is_symlink() and not _is_within_root(directory_path.resolve(), target):
                dirnames.remove(directory)

        for filename in filenames:
            candidate = root_dir / filename
            if candidate.is_symlink() and not _is_within_root(candidate.resolve(), target):
                continue
            if _is_supported_file(candidate):
                files.append(candidate.resolve())

    return sorted(files)


def scan_repository(root: str | os.PathLike[str] | Path) -> ScanResult:
    """Scan a repository or project folder and return verified supported files with warnings."""

    target = Path(root).expanduser()
    try:
        resolved_root = target.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"target directory is not accessible: {target}") from exc

    if not resolved_root.is_dir():
        raise ValueError(f"target path is not a directory: {resolved_root}")

    files: list[Path] = []
    warnings: list[str] = []
    total_bytes = 0

    for current_root, dirnames, filenames in os.walk(resolved_root, topdown=True, followlinks=False):
        current_path = Path(current_root)
        dirnames[:] = [
            directory
            for directory in dirnames
            if not _should_exclude_directory(directory)
        ]

        for directory in list(dirnames):
            directory_path = current_path / directory
            try:
                if directory_path.is_symlink() and not _is_within_root(directory_path.resolve(), resolved_root):
                    dirnames.remove(directory)
                    warnings.append(f"Skipped out-of-root symlink: {directory_path}")
            except OSError:
                dirnames.remove(directory)
                warnings.append(f"Skipped inaccessible symlink: {directory_path}")

        for filename in filenames:
            candidate = current_path / filename
            try:
                if candidate.is_symlink() and not _is_within_root(candidate.resolve(), resolved_root):
                    warnings.append(f"Skipped out-of-root symlink: {candidate}")
                    continue
                if not _is_supported_file(candidate):
                    continue
                file_size = candidate.stat().st_size
                if file_size > MAX_SINGLE_FILE_BYTES:
                    warnings.append(f"Skipped file over budget: {candidate} ({file_size} bytes)")
                    continue
                if total_bytes + file_size > MAX_TOTAL_SCAN_BYTES:
                    warnings.append(f"Skipped file beyond aggregate budget: {candidate} ({file_size} bytes)")
                    continue
                if len(files) >= MAX_SUPPORTED_FILES:
                    warnings.append(
                        "Stopped scanning because the supported-file budget was reached. "
                        f"Limit: {MAX_SUPPORTED_FILES}."
                    )
                    return ScanResult(root=resolved_root, files=files, warnings=warnings, total_bytes=total_bytes)
                files.append(candidate.resolve())
                total_bytes += file_size
            except OSError as exc:
                warnings.append(f"Skipped unreadable file: {candidate} ({exc})")

    return ScanResult(root=resolved_root, files=sorted(files), warnings=warnings, total_bytes=total_bytes)
