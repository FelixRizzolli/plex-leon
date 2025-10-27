from pathlib import Path

import pytest

from plex_leon.shared import find_episode_in_dirs


@pytest.mark.parametrize(
    "files,season,episode,expected_name",
    [
        (["Game of Thrones (2011) - s01e02.mkv"], 1, 2, "Game of Thrones (2011) - s01e02.mkv"),
        ([".Game of Thrones (2011) - s01e03.mkv"], 1, 3, None),
    ],
    ids=["find-matching-episode", "skip-hidden"],
)
def test_find_episode_in_dirs(
    tmp_path: Path,
    files: list[str],
    season: int,
    episode: int,
    expected_name: str | None,
) -> None:
    show_dir = tmp_path / "show"
    show_dir.mkdir()
    created_files = []
    for name in files:
        file_path = show_dir / name
        file_path.touch()
        created_files.append(file_path)

    result = find_episode_in_dirs([show_dir], season=season, episode=episode)
    if expected_name is None:
        assert result is None
    else:
        assert result == show_dir / expected_name
