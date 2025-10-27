from pathlib import Path

import pytest

from plex_leon.shared import unique_swap_path


@pytest.mark.parametrize(
    "prepopulate,expected",
    [
        (False, ".plexleon_swap_name"),
        (True, ".plexleon_swap_name.1"),
    ],
)
def test_unique_swap_path(tmp_path: Path, prepopulate: bool, expected: str) -> None:
    if prepopulate:
        (tmp_path / ".plexleon_swap_name").touch()

    result = unique_swap_path(tmp_path, "name")
    assert result.name == expected
