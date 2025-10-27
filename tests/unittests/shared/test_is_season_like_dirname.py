import pytest

from plex_leon.shared import is_season_like_dirname


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Season 01", True),
        ("Season 1 Part 2", False),
    ],
)
def test_is_season_like_dirname(name: str, expected: bool) -> None:
    assert is_season_like_dirname(name) is expected
