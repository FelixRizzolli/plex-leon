import pytest

from plex_leon.shared import extract_tvdb_id


@pytest.mark.parametrize(
    "name,expected",
    [
        ("John Wick (2014) {tvdb-155}.mp4", "155"),
        ("The Chronicles of Narnia - The Lion, the Witch and the Wardrobe (2005) {tvdb-232}.mp4", "232"),
        ("[REC] (2007) {tvdb-3331}.mp4", "3331"),
        ("28 Weeks Later (2007).mp4", None),
    ],
)
def test_extract_tvdb_id_behaviour(name: str, expected: str | None) -> None:
    assert extract_tvdb_id(name) == expected
