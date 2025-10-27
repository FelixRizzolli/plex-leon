from __future__ import annotations

from pathlib import Path

from plex_leon.utils.episode_renamer import EpisodeRenamerUtility
from utils import make_files


def test_episode_renamer_basic(tmp_path: Path):
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

    original_names = sorted(p.name for p in base.iterdir())

    # dry run should show planned renames
    util = EpisodeRenamerUtility(dry_run=True)
    renamed_count, = util.process(tmp_path / "library-e")
    assert renamed_count == 4
    # No filesystem changes during dry run
    assert sorted(p.name for p in base.iterdir()) == original_names

    # do it for real
    util = EpisodeRenamerUtility(dry_run=False)
    renamed_count, = util.process(tmp_path / "library-e")
    assert renamed_count == 4

    # Check resulting filenames
    season_dir = base
    names = sorted(p.name for p in season_dir.iterdir())
    assert "Code Geass (2006) - s01e01.mp4" in names
    assert "Code Geass (2006) - s01e02.mp4" in names
    assert "Code Geass (2006) - s01e03.mp4" in names
    assert "Code Geass (2006) - s01e04-e05.mp4" in names
