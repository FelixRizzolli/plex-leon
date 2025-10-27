from pathlib import Path

import pytest

from plex_leon.shared import merge_directory_contents


def test_merge_directory_contents_moves_items(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "file.txt").write_text("data")

    merge_directory_contents(src, dst)

    assert not (src / "file.txt").exists()
    assert (dst / "file.txt").exists()


def test_merge_directory_contents_writes_conflicts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "dup.txt").write_text("new")
    (dst / "dup.txt").write_text("old")

    merge_directory_contents(src, dst)

    conflict_dir = dst / ".plexleon_conflicts"
    assert conflict_dir.is_dir()
    conflicts = list(conflict_dir.iterdir())
    assert len(conflicts) == 1
    assert conflicts[0].name.startswith("dup (conflict)")
    captured = capsys.readouterr()
    assert "CONFLICT" in captured.out
