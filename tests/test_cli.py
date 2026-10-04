from pathlib import Path
import sys

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from doc_sync.cli import build_parser, main


def test_help_displays_usage(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])

    assert exit_info.value.code == 0
    assert "usage: doc-sync" in capsys.readouterr().out


def test_valid_directory_is_accepted(tmp_path: Path) -> None:
    assert main([str(tmp_path)]) == 0


def test_missing_directory_is_rejected(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    missing_directory = tmp_path / "missing"

    with pytest.raises(SystemExit) as exit_info:
        main([str(missing_directory)])

    assert exit_info.value.code == 2
    assert "does not exist" in capsys.readouterr().err


def test_file_target_is_rejected(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file_target = tmp_path / "project.txt"
    file_target.write_text("not a directory", encoding="utf-8")

    with pytest.raises(SystemExit) as exit_info:
        main([str(file_target)])

    assert exit_info.value.code == 2
    assert "not a directory" in capsys.readouterr().err


def test_yes_flag_is_parsed(tmp_path: Path) -> None:
    args = build_parser().parse_args(["--yes", str(tmp_path)])

    assert args.target == tmp_path
    assert args.yes is True