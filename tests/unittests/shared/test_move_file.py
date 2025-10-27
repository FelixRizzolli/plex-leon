from pathlib import Path

import pytest

from plex_leon.shared import move_file


def test_move_file_dry_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "src.txt"
    dst = tmp_path / "sub" / "dst.txt"
    src.write_text("data")

    move_file(src, dst, overwrite=True, dry_run=True)

    assert src.exists()
    assert not dst.exists()
    out = capsys.readouterr().out
    assert "MOVE" in out


def test_move_file_respects_overwrite_false(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("new")
    dst.write_text("old")

    move_file(src, dst, overwrite=False, dry_run=False)

    assert src.exists()
    assert dst.read_text() == "old"
    out = capsys.readouterr().out
    assert "SKIP" in out


def test_move_file_overwrites_existing(tmp_path: Path) -> None:
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("new")
    dst.write_text("old")

    move_file(src, dst, overwrite=True, dry_run=False)

    assert not src.exists()
    assert dst.read_text() == "new"
