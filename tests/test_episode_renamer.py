from __future__ import annotations

from pathlib import Path
import builtins
import pytest

from plex_leon.utils.episode_renamer import process_library as ep_process
from utils import make_files


def test_episode_renamer_basic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    base = tmp_path / "library-e" / \
        "Code Geass (2006) {tvdb-79525}" / "Season 01"
    base.mkdir(parents=True)
    files = [
        "Code Geass - s01e01.mp4",
        "Code Geass (2006) - S01E02 - Title.mp4",
        "Code Geass (2006) - S01E03.mp4",
        "Code Geass (2006) - S01E04-E05.mp4",
    ]
    make_files(base, files)

    outputs: list[str] = []

    def fake_print(*args, **kwargs):
        outputs.append(" ".join(map(str, args)))

    monkeypatch.setattr(builtins, "print", fake_print)

    # dry run should show planned renames
    renamed_count, = ep_process(tmp_path / "library-e", dry_run=True)
    assert renamed_count == 4
    assert any("RENAME:" in ln for ln in outputs)

    # do it for real
    outputs.clear()
    renamed_count, = ep_process(tmp_path / "library-e", dry_run=False)
    assert renamed_count == 4

    # Check resulting filenames
    season_dir = base
    names = sorted(p.name for p in season_dir.iterdir())
    assert "Code Geass (2006) - s01e01.mp4" in names
    assert "Code Geass (2006) - s01e02.mp4" in names
    assert "Code Geass (2006) - s01e03.mp4" in names
    assert "Code Geass (2006) - s01e04-e05.mp4" in names
