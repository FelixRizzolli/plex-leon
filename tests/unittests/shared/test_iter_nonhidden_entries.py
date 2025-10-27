from pathlib import Path

import pytest

from plex_leon.shared import iter_nonhidden_entries


@pytest.mark.parametrize(
    "entries,expected",
    [
        (
            [
                ("dir", "sub"),
                ("file", "sub/file.txt"),
            ],
            ["sub", "sub/file.txt"],
        ),
        (
            [
                ("dir", ".hidden"),
                ("file", ".hidden/file.txt"),
                ("file", "visible.txt"),
            ],
            ["visible.txt"],
        ),
    ],
    ids=["include-visible", "exclude-hidden"],
)
def test_iter_nonhidden_entries(
    tmp_path: Path, entries: list[tuple[str, str]], expected: list[str]
) -> None:
    for kind, rel_path in entries:
        target = tmp_path / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if kind == "dir":
            target.mkdir(exist_ok=True)
        else:
            target.write_text("data")

    result = sorted(
        str(path.relative_to(tmp_path)) for path in iter_nonhidden_entries(tmp_path)
    )
    assert result == expected
