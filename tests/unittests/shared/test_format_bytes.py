import pytest

from plex_leon.shared import format_bytes


@pytest.mark.parametrize(
    "size,expected",
    [
        (512, "512 B"),
        (1536, "1.5 KB"),
    ],
)
def test_format_bytes(size: int, expected: str) -> None:
    assert format_bytes(size) == expected
