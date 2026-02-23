"""Unit tests for PrepareUtility, focusing on multi-episode range (S01E01-E04) handling."""
from __future__ import annotations

from pathlib import Path

import pytest

from plex_leon.utils.prepare import PrepareUtility, _parse_season_episode_from_name, _validate_show


# ---------------------------------------------------------------------------
# Tests for _parse_season_episode_from_name
# ---------------------------------------------------------------------------

class TestParseSeasonEpisodeFromName:
    """Tests for the internal parser that extracts season/episode info."""

    @pytest.mark.parametrize("name, expected", [
        # Single episode
        ("Show S01E05.mp4", (1, 5, None)),
        ("show s03e12.mkv", (3, 12, None)),
        # Multi-episode ranges — the key bug fix
        ("Show S01E01-E04.mp4", (1, 1, 4)),
        ("show s02e03-e05.mkv", (2, 3, 5)),
        ("ShowName S03E10-E12 - Title.avi", (3, 10, 12)),
        # Uppercase range
        ("Show S01E01-E04 - Some Title.mp4", (1, 1, 4)),
        # German style (no range support, ep2 always None)
        ("Episode 3 Staffel 2 von Show.mp4", (2, 3, None)),
        ("Staffel 1 Episode 7 von Show.mp4", (1, 7, None)),
        # No tag → None
        ("random_file.mp4", None),
        ("Season 01.mp4", None),
    ])
    def test_parse(self, name: str, expected):
        assert _parse_season_episode_from_name(name) == expected

    def test_range_ep2_is_not_none_for_range_tag(self):
        """ep2 must be set (not None) for range tags like S01E01-E04."""
        result = _parse_season_episode_from_name("MyShow S01E01-E04.mp4")
        assert result is not None
        season, ep1, ep2 = result
        assert ep2 == 4, "Range end must be 4, not None"

    def test_single_ep_ep2_is_none(self):
        """ep2 must be None for plain single-episode tags."""
        result = _parse_season_episode_from_name("MyShow S02E07.mp4")
        assert result is not None
        _, _, ep2 = result
        assert ep2 is None


# ---------------------------------------------------------------------------
# Tests for PrepareUtility.process — multi-episode range in output filename
# ---------------------------------------------------------------------------

def _make_loose_episode(show_dir: Path, filename: str) -> Path:
    show_dir.mkdir(parents=True, exist_ok=True)
    f = show_dir / filename
    f.write_bytes(b"")
    return f


class TestPrepareMultiEpisodeRange:
    """Verify that prepare creates 's01e01-e04' target names for range files."""

    def test_single_episode_target_name(self, tmp_path):
        """Single episode files get target name 's01e01'."""
        show_dir = tmp_path / "My Show (2020) {tvdb-1}"
        _make_loose_episode(show_dir, "My Show S01E05.mp4")

        util = PrepareUtility(dry_run=False)
        (count,) = util.process(tmp_path)

        assert count == 1
        target = show_dir / "Season 01" / "My Show (2020) - s01e05.mp4"
        assert target.exists()

    def test_multi_episode_range_in_target_name(self, tmp_path):
        """Range files like S01E01-E04 must produce 's01e01-e04' target name."""
        show_dir = tmp_path / "My Show (2020) {tvdb-1}"
        _make_loose_episode(show_dir, "My Show S01E01-E04.mp4")

        util = PrepareUtility(dry_run=False)
        (count,) = util.process(tmp_path)

        assert count == 1
        # The range end '-e04' must be in the target filename
        target = show_dir / "Season 01" / "My Show (2020) - s01e01-e04.mp4"
        assert target.exists(), (
            f"Expected {target} to exist — range end was stripped from filename"
        )

    def test_multi_episode_range_not_stripped(self, tmp_path):
        """Regression: the old bug would drop '-E04' from the output name."""
        show_dir = tmp_path / "Breaking Bad (2008) {tvdb-81189}"
        _make_loose_episode(show_dir, "Breaking.Bad.S02E03-E05.mkv")

        util = PrepareUtility(dry_run=False)
        (count,) = util.process(tmp_path)

        assert count == 1
        season_dir = show_dir / "Season 02"
        renamed = list(season_dir.glob("*.mkv"))
        assert len(renamed) == 1
        assert "-e05" in renamed[0].name, (
            f"Range end '-e05' missing — old bug re-introduced. Got: {renamed[0].name}"
        )
        # Must NOT be the old broken single-ep form
        assert renamed[0].name != "Breaking Bad (2008) - s02e03.mkv"

    def test_dry_run_range_not_renamed(self, tmp_path):
        """In dry-run mode the file stays untouched but the count is correct."""
        show_dir = tmp_path / "My Show (2020) {tvdb-1}"
        original = _make_loose_episode(show_dir, "Show S02E01-E03.mp4")

        util = PrepareUtility(dry_run=True)
        (count,) = util.process(tmp_path)

        assert count == 1
        # Dry-run: original still in place
        assert original.exists()
        # Season dir should NOT have been created
        assert not (show_dir / "Season 02").exists()

    def test_mixed_single_and_range(self, tmp_path):
        """Mix of single-episode and multi-episode files in the same show."""
        show_dir = tmp_path / "Fallout (2024) {tvdb-416744}"
        _make_loose_episode(show_dir, "Fallout S01E01.mp4")
        _make_loose_episode(show_dir, "Fallout S01E02-E03.mp4")
        _make_loose_episode(show_dir, "Fallout S01E04.mp4")

        util = PrepareUtility(dry_run=False)
        (count,) = util.process(tmp_path)

        assert count == 3
        season_dir = show_dir / "Season 01"
        names = {f.name for f in season_dir.iterdir()}
        assert "Fallout (2024) - s01e01.mp4" in names
        assert "Fallout (2024) - s01e02-e03.mp4" in names
        assert "Fallout (2024) - s01e04.mp4" in names

    def test_uppercase_range_tag_normalized(self, tmp_path):
        """S01E01-E04 (uppercase) is normalized to s01e01-e04 in the output."""
        show_dir = tmp_path / "Hanna (2019) {tvdb-357690}"
        _make_loose_episode(show_dir, "Hanna S01E01-E02.MP4")

        util = PrepareUtility(dry_run=False)
        (count,) = util.process(tmp_path)

        assert count == 1
        target = show_dir / "Season 01" / "Hanna (2019) - s01e01-e02.mp4"
        assert target.exists()

    def test_places_file_in_correct_season_dir(self, tmp_path):
        """Range file is moved into the correct Season folder."""
        show_dir = tmp_path / "Orphan Black (2013) {tvdb-260315}"
        _make_loose_episode(show_dir, "Orphan.Black.S03E04-E05.mkv")

        util = PrepareUtility(dry_run=False)
        util.process(tmp_path)

        assert (show_dir / "Season 03").is_dir()
        target = show_dir / "Season 03" / "Orphan Black (2013) - s03e04-e05.mkv"
        assert target.exists()


# ---------------------------------------------------------------------------
# Tests for _validate_show with range files
# ---------------------------------------------------------------------------

class TestValidateShowWithRangeFiles:
    def test_range_file_does_not_cause_false_duplicate(self, tmp_path):
        """A range file S01E01-E04 should NOT be flagged as duplicate of s01e01."""
        show_dir = tmp_path / "Test Show (2021) {tvdb-99}"
        show_dir.mkdir()
        (show_dir / "Show S01E01-E04.mp4").write_bytes(b"")

        valid, msgs = _validate_show(show_dir)
        errors = [m for m in msgs if m.startswith("❌ ERROR:")]
        assert valid
        assert not any("duplicate" in m for m in errors)

    def test_genuine_duplicate_still_detected(self, tmp_path):
        """Two files both claiming S01E05 are still detected as duplicates."""
        show_dir = tmp_path / "Test Show (2021) {tvdb-99}"
        show_dir.mkdir()
        (show_dir / "Show S01E05 version1.mp4").write_bytes(b"")
        (show_dir / "Show S01E05 version2.mp4").write_bytes(b"")

        valid, msgs = _validate_show(show_dir)
        assert not valid
        assert any("duplicate" in m for m in msgs)

