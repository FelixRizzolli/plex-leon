"""Unit tests for SeasonRenamerUtility.

Season renaming is not affected by episode range tags (it renames season
*folders*, not episode files).  These tests verify the core functionality
and serve as a baseline so any future regression is caught.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from plex_leon.utils.season_renamer import SeasonRenamerUtility


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_season_dir(tmp_path: Path, show: str, season_name: str) -> Path:
    """Create <tmp_path>/<show>/<season_name>/ and return the library root."""
    d = tmp_path / show / season_name
    d.mkdir(parents=True)
    return tmp_path


# ---------------------------------------------------------------------------
# Core season-folder renaming
# ---------------------------------------------------------------------------

class TestSeasonRenaming:
    @pytest.mark.parametrize("raw_name, expected_name", [
        ("season 01", "Season 01"),
        ("Season 01", "Season 01"),   # already canonical
        ("Staffel 02", "Season 02"),
        ("staffel 3", "Season 03"),
        ("SEASON 05", "Season 05"),
    ])
    def test_renames_season_folder(self, tmp_path, raw_name, expected_name):
        lib = _make_season_dir(tmp_path, "My Show (2020) {tvdb-1}", raw_name)
        util = SeasonRenamerUtility(dry_run=False)
        (count,) = util.process(lib)
        show_dir = lib / "My Show (2020) {tvdb-1}"
        if raw_name == expected_name:
            assert count == 0
        else:
            assert count == 1
            assert (show_dir / expected_name).is_dir()
            assert not (show_dir / raw_name).is_dir()

    def test_dry_run_does_not_rename(self, tmp_path):
        lib = _make_season_dir(tmp_path, "My Show (2020) {tvdb-1}", "staffel 01")
        util = SeasonRenamerUtility(dry_run=True)
        (count,) = util.process(lib)
        assert count == 1
        # Dry-run: original folder must still exist unchanged
        assert (lib / "My Show (2020) {tvdb-1}" / "staffel 01").is_dir()

    def test_multiple_seasons_renamed(self, tmp_path):
        show_dir = tmp_path / "My Show (2020) {tvdb-1}"
        for s in ["staffel 01", "staffel 02", "staffel 03"]:
            (show_dir / s).mkdir(parents=True)
        util = SeasonRenamerUtility(dry_run=False)
        (count,) = util.process(tmp_path)
        assert count == 3
        for i in range(1, 4):
            assert (show_dir / f"Season {i:02d}").is_dir()


# ---------------------------------------------------------------------------
# Season renamer is unaffected by episode multi-range filenames inside seasons
# ---------------------------------------------------------------------------

class TestSeasonRenamerEpisodeFilesUnaffected:
    """Episode files with range tags (S01E01-E04) inside season folders must
    not confuse the season renamer — it should only touch directory names."""

    def test_range_episode_files_inside_season_untouched(self, tmp_path):
        """Files like 'Show S01E01-E04.mp4' inside a season folder are ignored."""
        show_dir = tmp_path / "Code Geass (2006) {tvdb-79525}"
        season_dir = show_dir / "staffel 01"
        season_dir.mkdir(parents=True)
        ep_file = season_dir / "Code Geass S01E01-E04.mp4"
        ep_file.write_bytes(b"")

        util = SeasonRenamerUtility(dry_run=False)
        (count,) = util.process(tmp_path)

        # Folder renamed
        assert count == 1
        new_season = show_dir / "Season 01"
        assert new_season.is_dir()
        # Episode file is intact (same content, just in the renamed folder)
        assert (new_season / ep_file.name).exists()

    def test_canonical_season_with_range_files_not_counted(self, tmp_path):
        """A 'Season 01' folder that already has correct name contributes 0 renames."""
        show_dir = tmp_path / "Fallout (2024) {tvdb-416744}"
        season_dir = show_dir / "Season 01"
        season_dir.mkdir(parents=True)
        (season_dir / "Fallout S01E01-E02.mp4").write_bytes(b"")
        (season_dir / "Fallout S01E03.mp4").write_bytes(b"")

        util = SeasonRenamerUtility(dry_run=False)
        (count,) = util.process(tmp_path)

        assert count == 0

