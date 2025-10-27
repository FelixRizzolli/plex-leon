from pathlib import Path
from typing import Any

import pytest

from plex_leon.shared import collect_tvdb_ids


MEDIA_ENTRIES = [
    {
        "name": "John Wick (2014) {tvdb-155}",
        "kind": "dir",
        "expected": {"155"},
    },
    {
        "name": "300 - Rise of an Empire (2014) {tvdb-459}.mkv",
        "kind": "file",
        "expected": {"459"},
    },
    {
        "name": "plain.txt",
        "kind": "file",
        "expected": set(),
    },
    {
        "name": ".hidden {tvdb-9}",
        "kind": "dir",
        "expected": set(),
    },
]


@pytest.mark.parametrize(
    "entry",
    MEDIA_ENTRIES,
    ids=[entry["name"] for entry in MEDIA_ENTRIES],
)
def test_collect_tvdb_ids_single_entry(
    tmp_path: Path, entry: dict[str, Any]
) -> None:
    target = tmp_path / entry["name"]  # type: ignore[index]
    if entry["kind"] == "dir":
        target.mkdir()
    else:
        target.touch()

    result = collect_tvdb_ids(tmp_path)
    assert result == entry["expected"]


def test_collect_tvdb_ids_multiple_entries(tmp_path: Path) -> None:
    for entry in MEDIA_ENTRIES:
        target = tmp_path / entry["name"]  # type: ignore[index]
        if entry["kind"] == "dir":
            target.mkdir()
        else:
            target.touch()

    result = collect_tvdb_ids(tmp_path)
    
    # Only the visible entries with TVDB ids should be present.
    assert result == {"155", "459"}
