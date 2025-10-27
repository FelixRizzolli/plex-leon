from __future__ import annotations

from pathlib import Path

from plex_leon.utils.season_renamer import SeasonRenamerUtility
from utils import make_files


def test_season_renamer_variants(tmp_path: Path):
    show = tmp_path / "library-s" / "Some Show (2011) {tvdb-12345}"
    # Create variant season folders
    make_files(show, [
        "season 01/",
        "Staffel 02/",
        "S-3/",
    ])

    # Create dummy files inside to simulate content
    for p in (show / "season 01", show / "Staffel 02", show / "S-3"):
        (p / "a.txt").write_text("x")

    original_dirs = sorted(p.name for p in show.iterdir())

    # dry run shows planned ops
    util = SeasonRenamerUtility(dry_run=True)
    renamed_count, = util.process(tmp_path / "library-s")
    assert renamed_count == 3
    # Dry run should not mutate folder names
    assert sorted(p.name for p in show.iterdir()) == original_dirs

    # execute
    util = SeasonRenamerUtility(dry_run=False)
    renamed_count, = util.process(tmp_path / "library-s")
    assert renamed_count == 3

    # verify canonical names
    assert (show / "Season 01").exists()
    assert (show / "Season 02").exists()
    assert (show / "Season 03").exists()


def test_season_renamer_ignores_top_level_show_dirs(tmp_path: Path):
    # Create a show folder at the library root containing digits
    root = tmp_path / "library-s"
    show_dir = root / "Game of Thrones 2011"
    show_dir.mkdir(parents=True)
    # Also add a real season-like subfolder to ensure it still gets renamed
    (show_dir / "season 01").mkdir()
    (show_dir / "season 01" / "file.mp4").write_text("x")

    util = SeasonRenamerUtility(dry_run=False)
    renamed_count, = util.process(root)
    # Only the season folder should be processed, not the top-level show dir
    assert renamed_count == 1
    assert (show_dir.exists())
    assert (show_dir / "Season 01").exists()
