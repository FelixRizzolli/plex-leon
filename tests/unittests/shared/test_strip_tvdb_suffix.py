import pytest

from plex_leon.shared import strip_tvdb_suffix


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Code Geass {tvdb-123}", "Code Geass"),
        ("Show {tvdb-1} Extra {tvdb-2}", "ShowExtra"),
    ],
)
def test_strip_tvdb_suffix(name: str, expected: str) -> None:
    assert strip_tvdb_suffix(name) == expected
