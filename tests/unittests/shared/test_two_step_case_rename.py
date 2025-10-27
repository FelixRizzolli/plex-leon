from pathlib import Path

import pytest

from plex_leon.shared import two_step_case_rename


def test_two_step_case_rename_dry_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    old = tmp_path / "Old.txt"
    new = tmp_path / "new.txt"
    old.write_text("data")

    assert two_step_case_rename(old, new, dry_run=True) is True
    out = capsys.readouterr().out
    assert out.count("RENAME") == 2
    assert old.exists()


def test_two_step_case_rename_success(tmp_path: Path) -> None:
    old = tmp_path / "Old.txt"
    new = tmp_path / "new.txt"
    old.write_text("data")

    assert two_step_case_rename(old, new, dry_run=False) is True
    assert not old.exists()
    assert new.exists()


def test_two_step_case_rename_conflict(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    old = tmp_path / "Old.txt"
    new = tmp_path / "new.txt"
    old.write_text("data")
    new.write_text("other")

    assert two_step_case_rename(old, new, dry_run=False) is False
    assert old.exists()
    assert new.read_text() == "other"
    out = capsys.readouterr().out
    assert "SKIP" in out
