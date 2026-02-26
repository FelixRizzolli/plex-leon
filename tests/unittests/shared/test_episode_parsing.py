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
        ("S10E02-CD1", {"season": "10", "range_end": None, "split_prefix": "CD", "split_num": "1"}),
        ("s01e02-e03 disc2", {"season": "01", "range_end": "03", "split_prefix": "disc", "split_num": "2"}),
        ("S01E01-E02-disk3", {"season": "01", "range_end": "02", "split_prefix": "disk", "split_num": "3"}),
        ("S01E01 dvd1", {"season": "01", "range_end": None, "split_prefix": "dvd", "split_num": "1"}),
        ("S01E01 part2", {"season": "01", "range_end": None, "split_prefix": "part", "split_num": "2"}),
        ("S01E01-pt1", {"season": "01", "range_end": None, "split_prefix": "pt", "split_num": "1"}),
    ],
)
def test_episode_tag_regex_with_split(text: str, expected: dict[str, str | None]) -> None:
    match = EPISODE_TAG_REGEX.search(text)
    assert match
    assert match.group(1) == expected["season"]
    assert match.group(3) == expected["range_end"]
    assert match.group(4) == expected["split_prefix"]
    assert match.group(5) == expected["split_num"]


@pytest.mark.parametrize(
    "text,expected",
    [
        ("S1E2", "s01e02"),
        ("Show s01e02-e03", "s01e02-e03"),
        ("No tag", None),
        # Split names
        ("S01E01-CD1", "s01e01 - cd1"),
        ("s01e01-e02 disc1", "s01e01-e02 - disc1"),
        ("S01E03 disk2", "s01e03 - disk2"),
        ("S02E01-dvd1", "s02e01 - dvd1"),
        ("S01E01-part1", "s01e01 - part1"),
        ("S01E01-pt3", "s01e01 - pt3"),
        ("S01E01-E02-CD1", "s01e01-e02 - cd1"),
    ],
)
def test_normalize_episode_tag(text: str, expected: str | None) -> None:
    assert normalize_episode_tag(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("S02E05.mp4", (2, 5, None, None)),
        ("Episode s3e04-e05", (3, 4, 5, None)),
        ("Season 1", None),
        # Split names
        ("S01E01-CD1.mp4", (1, 1, None, "cd1")),
        ("s1e1-disc1.mkv", (1, 1, None, "disc1")),
        ("S01E01-disk1.mp4", (1, 1, None, "disk1")),
        ("S01E01-dvd1.mp4", (1, 1, None, "dvd1")),
        ("S01E01-part1.mp4", (1, 1, None, "part1")),
        ("S01E01-pt1.mp4", (1, 1, None, "pt1")),
        ("S01E01 CD1.mp4", (1, 1, None, "cd1")),
        ("s1e1 disc1.mkv", (1, 1, None, "disc1")),
        # Range + split
        ("S01E01-E02-CD1.mp4", (1, 1, 2, "cd1")),
        ("s1e1-e2-disc1.mkv", (1, 1, 2, "disc1")),
        ("S01E01-E02 disk1.mp4", (1, 1, 2, "disk1")),
        ("S01E01-E02 dvd1.mp4", (1, 1, 2, "dvd1")),
        ("S01E01-E02-part1.mp4", (1, 1, 2, "part1")),
        ("S01E01-E02-pt1.mp4", (1, 1, 2, "pt1")),
    ],
)
def test_parse_episode_tag(text: str, expected: tuple[int, int, int | None, str | None] | None) -> None:
    assert parse_episode_tag(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("S02E05.mkv", (2, 5)),
        ("S02E05-E06", (2, 5)),
        ("Nope", None),
        # Split names — still returns (season, ep1) only
        ("S02E05-CD1.mkv", (2, 5)),
        ("S02E05-E06 disc2", (2, 5)),
    ],
)
def test_parse_season_episode(text: str, expected: tuple[int, int] | None) -> None:
    assert parse_season_episode(text) == expected
