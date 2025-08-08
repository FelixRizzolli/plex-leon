from __future__ import annotations

import re
from pathlib import Path

import builtins

import pytest

from plex_leon import extract_tvdb_id, collect_tvdb_ids, move_file, main
from utils import make_files


@pytest.mark.parametrize(
    "name,expected",
    [
        ("John Wick (2014) {tvdb-155}.mp4", "155"),
        ("Game of Thrones (2011) {tvdb-121361}/", "121361"),
        ("No ID here.mp4", None),
        ("Lower {TVDB-42} case", "42"),
        ("{tvdb-000123}", "000123"),
    ],
)
def test_extract_tvdb_id(name: str, expected: str | None):
    assert extract_tvdb_id(name) == expected


def test_collect_tvdb_ids(tmp_path: Path):
    names = [
        "John Wick (2014) {tvdb-155}.mp4",
        "Game of Thrones (2011) {tvdb-121361}",
        ".hidden {tvdb-9999}.mp4",
        "No id.mp4",
    ]
    make_files(tmp_path, names)
    ids = collect_tvdb_ids(tmp_path)
    assert ids == {"155", "121361"}


@pytest.mark.parametrize("overwrite", [False, True])
@pytest.mark.parametrize("dry_run", [False, True])
def test_move_file_basic(tmp_path: Path, overwrite: bool, dry_run: bool, monkeypatch: pytest.MonkeyPatch):
    src = tmp_path / "a.txt"
    src.write_text("hello")
    dst = tmp_path / "sub" / "a.txt"

    # capture prints
    lines: list[str] = []

    def fake_print(*args, **kwargs):  # type: ignore[no-redef]
        lines.append(" ".join(map(str, args)))

    monkeypatch.setattr(builtins, "print", fake_print)

    move_file(src, dst, overwrite=overwrite, dry_run=dry_run)

    assert any("MOVE:" in ln for ln in lines)
    if dry_run:
        assert src.exists() and not dst.exists()
    else:
        assert not src.exists() and dst.exists()


def test_move_file_skip_when_exists_without_overwrite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    src = tmp_path / "a.txt"
    src.write_text("data")
    dst = tmp_path / "a.txt"
    dst.write_text("existing")

    msgs: list[str] = []

    def fake_print(*args, **kwargs):
        msgs.append(" ".join(map(str, args)))

    monkeypatch.setattr(builtins, "print", fake_print)

    move_file(src, dst, overwrite=False, dry_run=False)

    # source should remain; destination unchanged
    assert src.exists() and dst.read_text() == "existing"
    assert any(re.search(r"SKIP exists:", m) for m in msgs)


def test_main_end_to_end_basic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    lib_a = tmp_path / "library-a"
    lib_b = tmp_path / "library-b"
    lib_c = tmp_path / "library-c"
    lib_a.mkdir()
    lib_b.mkdir()
    lib_c.mkdir()

    # setup libraries
    make_files(lib_a, [
        "John Wick (2014) {tvdb-155}.mp4",
        "John Wick 2 (2017) {tvdb-511}.mp4",
        "No ID.mp4",
    ])
    make_files(lib_b, [
        "Other (2000) {tvdb-42}.mp4",
        "Game of Thrones (2011) {tvdb-121361}",
        "John Wick (2014) {tvdb-155}.mp4",
    ])

    outputs: list[str] = []

    def fake_print(*args, **kwargs):
        outputs.append(" ".join(map(str, args)))

    # Patch print and argparse arguments
    monkeypatch.setattr(builtins, "print", fake_print)
    monkeypatch.setenv("PYTHONWARNINGS", "ignore")

    argv = [
        "prog",
        "--lib-a", str(lib_a),
        "--lib-b", str(lib_b),
        "--lib-c", str(lib_c),
        "--dry-run",
    ]

    # emulate CLI by patching sys.argv
    monkeypatch.setattr("sys.argv", argv)
    main()

    # Only the item with tvdb-155 should be considered eligible
    moved_msgs = [m for m in outputs if m.startswith("MOVE:")]
    assert len(moved_msgs) == 1
    assert "tvdb-155" in "\n".join(outputs)
    assert any("Found" in m for m in outputs)
    assert any("Done." in m for m in outputs)
