import pytest

from plex_leon.shared import get_season_number_from_dirname


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Season 4", 4),
        ("S01 Part 2", None),
    ],
)
def test_get_season_number_from_dirname(name: str, expected: int | None) -> None:
    assert get_season_number_from_dirname(name) == expected
