from __future__ import annotations

from pathlib import Path
import builtins
import pytest

from plex_leon.utils.season_renamer import process_library as season_process
from utils import make_files


def test_season_renamer_variants(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
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

    outputs: list[str] = []

    def fake_print(*args, **kwargs):
        outputs.append(" ".join(map(str, args)))

    monkeypatch.setattr(builtins, "print", fake_print)

    # dry run shows planned ops
    renamed_count, = season_process(tmp_path / "library-s", dry_run=True)
    assert renamed_count == 3
    assert any("RENAME:" in ln for ln in outputs)

    # execute
    outputs.clear()
    renamed_count, = season_process(tmp_path / "library-s", dry_run=False)
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

    renamed_count, = season_process(root, dry_run=False)
    # Only the season folder should be processed, not the top-level show dir
    assert renamed_count == 1
    assert (show_dir.exists())
    assert (show_dir / "Season 01").exists()
