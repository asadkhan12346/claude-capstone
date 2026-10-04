"""Command-line argument parsing and local target validation."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doc-sync",
        description="Generate documentation from a local Python repository.",
    )
    parser.add_argument("target", type=Path, help="Local repository or project directory")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip interactive approval when applying generated documentation",
    )
    return parser


def validate_target_directory(target: Path) -> Path:
    target = target.expanduser()
    try:
        if not target.exists():
            raise ValueError("target path does not exist")
        if not target.is_dir():
            raise ValueError("target path is not a directory")
        return target.resolve(strict=True)
    except OSError as error:
        raise ValueError("target directory is not accessible") from error


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        validate_target_directory(args.target)
    except ValueError as error:
        parser.error(str(error))
    print("Target directory validated; documentation sync is not yet connected.")
    return 0