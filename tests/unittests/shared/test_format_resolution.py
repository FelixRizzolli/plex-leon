import pytest

from plex_leon.shared import format_resolution


@pytest.mark.parametrize(
    "resolution,expected",
    [
        ((1920, 1080), "1920x1080"),
        (None, "unknown"),
    ],
)
def test_format_resolution(resolution: tuple[int, int] | None, expected: str) -> None:
    assert format_resolution(resolution) == expected
