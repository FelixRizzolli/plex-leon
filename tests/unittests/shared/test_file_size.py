from pathlib import Path

import pytest

from plex_leon.shared import file_size


@pytest.mark.parametrize(
    "filename,content,expected",
    [
        ("John Wick (2014) {tvdb-155}.mp4", b"hello", 5),
        ("Ballerina (2025) {tvdb-158074}.mkv", None, 0),
    ],
)
def test_file_size_handles_cases(
    tmp_path: Path, filename: str, content: bytes | None, expected: int
) -> None:
    path = tmp_path / filename
    if content is not None:
        path.write_bytes(content)

    assert file_size(path) == expected
