"""Unit tests for EpisodeRenamerUtility, focusing on multi-episode range (S01E01-E04) handling."""
from __future__ import annotations

from pathlib import Path

import pytest

from plex_leon.utils.episode_renamer import EpisodeRenamerUtility


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_show(tmp_path: Path, show_folder: str, season: str, filenames: list[str]) -> Path:
    """Create a show/<season>/<files> structure under tmp_path and return the library root."""
    season_dir = tmp_path / show_folder / season
    season_dir.mkdir(parents=True)
    for fn in filenames:
        (season_dir / fn).write_bytes(b"")
    return tmp_path


# ---------------------------------------------------------------------------
# Tests for single-episode renaming (baseline)
# ---------------------------------------------------------------------------

class TestSingleEpisodeRenaming:
    def test_normalizes_uppercase_tag(self, tmp_path):
        """S01E01 (uppercase) is normalized to s01e01 in the target filename."""
        lib = _make_show(
            tmp_path,
            show_folder="My Show (2020) {tvdb-1}",
            season="Season 01",
            filenames=["My Show S01E01.mp4"],
        )
        util = EpisodeRenamerUtility(dry_run=True)
        (count,) = util.process(lib)
        assert count == 1

    def test_already_correct_name_skipped(self, tmp_path):
        """A file already named correctly is not counted as renamed."""
        lib = _make_show(
            tmp_path,
            show_folder="My Show (2020) {tvdb-1}",
            season="Season 01",
            filenames=["My Show (2020) - s01e01.mp4"],
        )
        util = EpisodeRenamerUtility(dry_run=True)
        (count,) = util.process(lib)
        assert count == 0

    def test_renames_file_on_disk(self, tmp_path):
        """Without dry_run the file is actually renamed on disk."""
        lib = _make_show(
            tmp_path,
            show_folder="My Show (2020) {tvdb-1}",
            season="Season 01",
            filenames=["My Show S01E05.mkv"],
        )
        util = EpisodeRenamerUtility(dry_run=False)
        (count,) = util.process(lib)
        assert count == 1
        expected = lib / "My Show (2020) {tvdb-1}" / "Season 01" / "My Show (2020) - s01e05.mkv"
        assert expected.exists()


# ---------------------------------------------------------------------------
# Tests for multi-episode (range) renaming — the main bug fix
# ---------------------------------------------------------------------------

class TestMultiEpisodeRangeRenaming:
    """Verify that S01E01-E04 style tags are preserved in the output filename."""

    @pytest.mark.parametrize("input_name, expected_name", [
        # Uppercase range tag
        (
            "ShowName S01E01-E04 - Some Title.mp4",
            "My Show (2020) - s01e01-e04.mp4",
        ),
        # Lowercase range tag (already normalized form)
        (
            "My Show (2020) - s02e03-e05.mkv",
            "My Show (2020) - s02e03-e05.mkv",
        ),
        # Two-digit episode numbers
        (
            "Show S03E10-E12.avi",
            "My Show (2020) - s03e10-e12.avi",
        ),
    ])
    def test_dry_run_preserves_range(self, tmp_path, input_name, expected_name):
        """Dry-run: range end is included in the planned target name."""
        # Use a fixed show folder so expected_name always uses "My Show (2020)"
        lib = _make_show(
            tmp_path,
            show_folder="My Show (2020) {tvdb-1}",
            season="Season 01",
            filenames=[input_name],
        )
        util = EpisodeRenamerUtility(dry_run=True)
        (count,) = util.process(lib)
        # When already correct, count is 0; otherwise 1
        season_dir = lib / "My Show (2020) {tvdb-1}" / "Season 01"
        current_file = season_dir / input_name
        target_file = season_dir / expected_name
        if current_file.name == target_file.name:
            assert count == 0
        else:
            assert count == 1
            # Dry-run must NOT have renamed the file
            assert current_file.exists()
            assert not target_file.exists()

    def test_range_file_renamed_on_disk(self, tmp_path):
        """Without dry_run, S01E01-E04 file is renamed to include -e04 suffix."""
        lib = _make_show(
            tmp_path,
            show_folder="My Show (2020) {tvdb-1}",
            season="Season 01",
            filenames=["ShowName S01E01-E04.mp4"],
        )
        util = EpisodeRenamerUtility(dry_run=False)
        (count,) = util.process(lib)
        assert count == 1
        expected = lib / "My Show (2020) {tvdb-1}" / "Season 01" / "My Show (2020) - s01e01-e04.mp4"
        assert expected.exists(), f"Expected renamed file not found: {expected}"

    def test_range_end_not_stripped(self, tmp_path):
        """Regression: the -E04 part must NOT be stripped from the output name."""
        lib = _make_show(
            tmp_path,
            show_folder="Breaking Bad (2008) {tvdb-81189}",
            season="Season 02",
            filenames=["Breaking Bad S02E01-E03 - Pilot.mp4"],
        )
        util = EpisodeRenamerUtility(dry_run=False)
        (count,) = util.process(lib)
        assert count == 1
        season_dir = lib / "Breaking Bad (2008) {tvdb-81189}" / "Season 02"
        # Must contain -e03
        renamed = list(season_dir.glob("*.mp4"))
        assert len(renamed) == 1
        assert "-e03" in renamed[0].name, (
            f"Range end '-e03' missing from renamed file: {renamed[0].name}"
        )
        # Must NOT just end in -e01 (old broken behavior: strip range)
        assert renamed[0].name != "Breaking Bad (2008) - s02e01.mp4"

    def test_mixed_single_and_range_in_same_season(self, tmp_path):
        """Single-episode and multi-episode files in the same season are both handled."""
        lib = _make_show(
            tmp_path,
            show_folder="Code Geass (2006) {tvdb-79525}",
            season="Season 01",
            filenames=[
                "Code Geass S01E01 - Intro.mp4",
                "Code Geass S01E02-E03 - Double.mp4",
                "Code Geass S01E04.mp4",
            ],
        )
        util = EpisodeRenamerUtility(dry_run=False)
        (count,) = util.process(lib)
        assert count == 3
        season_dir = lib / "Code Geass (2006) {tvdb-79525}" / "Season 01"
        names = {f.name for f in season_dir.iterdir() if f.suffix == ".mp4"}
        assert "Code Geass (2006) - s01e01.mp4" in names
        assert "Code Geass (2006) - s01e02-e03.mp4" in names
        assert "Code Geass (2006) - s01e04.mp4" in names


# ---------------------------------------------------------------------------
# Tests for TVDB suffix stripping
# ---------------------------------------------------------------------------

class TestTvdbSuffixStripping:
    def test_tvdb_suffix_removed_from_show_title(self, tmp_path):
        """The {tvdb-NNNNN} part is stripped from the show title in the output."""
        lib = _make_show(
            tmp_path,
            show_folder="Death Note (2006) {tvdb-79481}",
            season="Season 01",
            filenames=["Death Note S01E01.mp4"],
        )
        util = EpisodeRenamerUtility(dry_run=False)
        util.process(lib)
        season_dir = lib / "Death Note (2006) {tvdb-79481}" / "Season 01"
        renamed = list(season_dir.glob("*.mp4"))
        assert len(renamed) == 1
        assert "tvdb" not in renamed[0].name
        assert renamed[0].name == "Death Note (2006) - s01e01.mp4"

