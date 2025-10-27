import pytest

from plex_leon.shared import (
    EPISODE_TAG_REGEX,
    normalize_episode_tag,
    parse_episode_tag,
    parse_season_episode,
)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("S10E02", {"season": "10", "range_end": None}),
        ("s01e02-e03", {"season": "01", "range_end": "03"}),
    ],
)
def test_episode_tag_regex(text: str, expected: dict[str, str | None]) -> None:
    match = EPISODE_TAG_REGEX.search(text)
    assert match
    assert match.group(1) == expected["season"]
    assert match.group(3) == expected["range_end"]


@pytest.mark.parametrize(
    "text,expected",
    [
        ("S1E2", "s01e02"),
        ("Show s01e02-e03", "s01e02-e03"),
        ("No tag", None),
    ],
)
def test_normalize_episode_tag(text: str, expected: str | None) -> None:
    assert normalize_episode_tag(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("S02E05.mp4", (2, 5, None)),
        ("Episode s3e04-e05", (3, 4, 5)),
        ("Season 1", None),
    ],
)
def test_parse_episode_tag(text: str, expected: tuple[int, int, int | None] | None) -> None:
    assert parse_episode_tag(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("S02E05.mkv", (2, 5)),
        ("S02E05-E06", (2, 5)),
        ("Nope", None),
    ],
)
def test_parse_season_episode(text: str, expected: tuple[int, int] | None) -> None:
    assert parse_season_episode(text) == expected
