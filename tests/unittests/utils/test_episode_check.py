"""Tests for episode_check utility."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plex_leon.utils.episode_check import (
    EpisodeCheckUtility,
    _extract_tvdb_id,
    _get_local_episode_counts,
    _is_media_file,
    _count_episodes_in_season,
)


class TestExtractTvdbId:
    """Tests for _extract_tvdb_id function."""
    
    def test_valid_show_name(self):
        """Test extraction from valid show name."""
        assert _extract_tvdb_id("Attack on Titan (2013) {tvdb-267440}") == 267440
        assert _extract_tvdb_id("Game of Thrones (2011) {tvdb-121361}") == 121361
    
    def test_invalid_show_name(self):
        """Test extraction from invalid show names."""
        assert _extract_tvdb_id("Attack on Titan (2013)") is None
        assert _extract_tvdb_id("Random Folder") is None
        assert _extract_tvdb_id("Show {tvdb-}") is None


class TestIsMediaFile:
    """Tests for _is_media_file function."""
    
    def test_media_extensions(self, tmp_path):
        """Test that media files are correctly identified."""
        media_files = ["video.mp4", "video.mkv", "video.avi"]
        for filename in media_files:
            file_path = tmp_path / filename
            file_path.touch()
            assert _is_media_file(file_path), f"{filename} should be identified as media"
    
    def test_non_media_extensions(self, tmp_path):
        """Test that non-media files are correctly rejected."""
        non_media = ["subtitle.srt", "readme.txt", "image.jpg"]
        for filename in non_media:
            file_path = tmp_path / filename
            file_path.touch()
            assert not _is_media_file(file_path), f"{filename} should not be identified as media"
    
    def test_directory(self, tmp_path):
        """Test that directories are not identified as media files."""
        dir_path = tmp_path / "Season 01"
        dir_path.mkdir()
        assert not _is_media_file(dir_path)


class TestCountEpisodesInSeason:
    """Tests for _count_episodes_in_season function."""
    
    def test_empty_season(self, tmp_path):
        """Test counting in empty season directory."""
        season_dir = tmp_path / "Season 01"
        season_dir.mkdir()
        assert _count_episodes_in_season(season_dir) == 0
    
    def test_season_with_episodes(self, tmp_path):
        """Test counting episodes in season directory."""
        season_dir = tmp_path / "Season 01"
        season_dir.mkdir()
        
        # Create some media files
        (season_dir / "episode1.mp4").touch()
        (season_dir / "episode2.mkv").touch()
        (season_dir / "episode3.avi").touch()
        
        # Create non-media files (should not be counted)
        (season_dir / "subtitle.srt").touch()
        (season_dir / ".hidden").touch()
        
        assert _count_episodes_in_season(season_dir) == 3
    
    def test_nonexistent_directory(self, tmp_path):
        """Test counting in nonexistent directory."""
        nonexistent = tmp_path / "does_not_exist"
        assert _count_episodes_in_season(nonexistent) == 0


class TestGetLocalEpisodeCounts:
    """Tests for _get_local_episode_counts function."""
    
    def test_multiple_seasons(self, tmp_path):
        """Test counting episodes across multiple seasons."""
        show_dir = tmp_path / "Show (2020) {tvdb-12345}"
        show_dir.mkdir()
        
        # Create Season 01 with 3 episodes
        s01 = show_dir / "Season 01"
        s01.mkdir()
        for i in range(3):
            (s01 / f"episode{i}.mp4").touch()
        
        # Create Season 02 with 5 episodes
        s02 = show_dir / "Season 02"
        s02.mkdir()
        for i in range(5):
            (s02 / f"episode{i}.mkv").touch()
        
        counts = _get_local_episode_counts(show_dir)
        assert counts == {1: 3, 2: 5}
    
    def test_skip_season_zero(self, tmp_path):
        """Test that Season 00 (specials) is skipped."""
        show_dir = tmp_path / "Show (2020) {tvdb-12345}"
        show_dir.mkdir()
        
        # Create Season 00
        s00 = show_dir / "Season 00"
        s00.mkdir()
        (s00 / "special.mp4").touch()
        
        # Create Season 01
        s01 = show_dir / "Season 01"
        s01.mkdir()
        (s01 / "episode1.mp4").touch()
        
        counts = _get_local_episode_counts(show_dir)
        assert 0 not in counts
        assert counts == {1: 1}
    
    def test_case_insensitive_season_folders(self, tmp_path):
        """Test that season folders are matched case-insensitively."""
        show_dir = tmp_path / "Show (2020) {tvdb-12345}"
        show_dir.mkdir()
        
        # Create various case variations
        for folder_name in ["Season 01", "season 02", "SEASON 03"]:
            season_dir = show_dir / folder_name
            season_dir.mkdir()
            (season_dir / "episode.mp4").touch()
        
        counts = _get_local_episode_counts(show_dir)
        assert counts == {1: 1, 2: 1, 3: 1}


class TestEpisodeCheckUtility:
    """Tests for EpisodeCheckUtility class."""
    
    def test_utility_metadata(self):
        """Test that utility class has correct metadata."""
        assert EpisodeCheckUtility.command == "episode-check"
        assert EpisodeCheckUtility.brief_description == "Compare local episode counts with TVDB data"
        assert len(EpisodeCheckUtility.parameters) == 1
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self, tmp_path):
        """Test that utility fails gracefully without API key."""
        util = EpisodeCheckUtility()
        count, = util.process(tmp_path)
        assert count == 0
    
    @patch.dict(os.environ, {"TVDB_API_KEY": "fake_key"})
    @patch("plex_leon.utils.episode_check.TVDBClient")
    def test_process_with_matching_counts(self, mock_tvdb_class, tmp_path):
        """Test processing with matching episode counts."""
        # Setup mock TVDB client
        mock_client = MagicMock()
        mock_client.get_series_episodes.return_value = {1: 3, 2: 5}
        mock_tvdb_class.return_value = mock_client
        
        # Create test show structure
        show_dir = tmp_path / "Test Show (2020) {tvdb-12345}"
        show_dir.mkdir()
        
        s01 = show_dir / "Season 01"
        s01.mkdir()
        for i in range(3):
            (s01 / f"episode{i}.mp4").touch()
        
        s02 = show_dir / "Season 02"
        s02.mkdir()
        for i in range(5):
            (s02 / f"episode{i}.mp4").touch()
        
        # Run utility
        util = EpisodeCheckUtility()
        count, = util.process(tmp_path)
        
        assert count == 1  # One show checked
        mock_client.get_series_episodes.assert_called_once_with(12345)
    
    @patch.dict(os.environ, {"TVDB_API_KEY": "fake_key"})
    @patch("plex_leon.utils.episode_check.TVDBClient")
    def test_process_with_mismatched_counts(self, mock_tvdb_class, tmp_path, capsys):
        """Test processing with mismatched episode counts."""
        # Setup mock TVDB client with different counts
        mock_client = MagicMock()
        mock_client.get_series_episodes.return_value = {1: 5, 2: 10}  # Different from local
        mock_tvdb_class.return_value = mock_client
        
        # Create test show structure with fewer episodes
        show_dir = tmp_path / "Test Show (2020) {tvdb-12345}"
        show_dir.mkdir()
        
        s01 = show_dir / "Season 01"
        s01.mkdir()
        for i in range(3):
            (s01 / f"episode{i}.mp4").touch()
        
        s02 = show_dir / "Season 02"
        s02.mkdir()
        for i in range(5):
            (s02 / f"episode{i}.mp4").touch()
        
        # Run utility
        util = EpisodeCheckUtility()
        count, = util.process(tmp_path)
        
        assert count == 1
        
        # Check that differences were printed
        captured = capsys.readouterr()
        assert "Test Show (2020)" in captured.out
        assert "⚠️" in captured.out  # Warning icon for differences
