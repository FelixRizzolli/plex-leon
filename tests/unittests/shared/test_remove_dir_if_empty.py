from pathlib import Path

import pytest

from plex_leon.shared import remove_dir_if_empty


@pytest.mark.parametrize(
    "populate,expected_removed",
    [
        (False, True),
        (True, False),
    ],
    ids=["empty-directory", "non-empty-directory"],
)
def test_remove_dir_if_empty(
    tmp_path: Path, populate: bool, expected_removed: bool
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    if populate:
        (target / "file.txt").write_text("data")

    result = remove_dir_if_empty(target)
    assert result is expected_removed
    assert target.exists() is (not expected_removed)
