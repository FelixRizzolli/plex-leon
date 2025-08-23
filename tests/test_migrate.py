from __future__ import annotations

from pathlib import Path

import builtins

import pytest

from plex_leon import process_libraries
from utils import make_files


def test_process_libraries_integration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from plex_leon.migrate import process_libraries

    lib_a = tmp_path / "library-a"
    lib_b = tmp_path / "library-b"
    lib_c = tmp_path / "library-c"
    lib_a.mkdir()
    lib_b.mkdir()
    lib_c.mkdir()

    make_files(lib_a, [
        "John Wick (2014) {tvdb-155}.mp4",
        "John Wick 2 (2017) {tvdb-511}.mp4",
        "No ID.mp4",
    ])
    # library-b has both a movie and a show folder with episodes
    make_files(lib_b, [
        "Other (2000) {tvdb-42}.mp4",
        "[REC] (2007) {tvdb-12345}.mp4",
        "Game of Thrones (2011) {tvdb-121361}/",
        "Game of Thrones (2011) {tvdb-121361}/Season 01/",
        "Game of Thrones (2011) {tvdb-121361}/Season 01/Game of Thrones (2011) - s01e01.mp4",
        "John Wick (2014) {tvdb-155}.mp4",
    ])

    outputs: list[str] = []

    def fake_print(*args, **kwargs):
        outputs.append(" ".join(map(str, args)))

    monkeypatch.setattr(builtins, "print", fake_print)

    moved, skipped = process_libraries(
        lib_a, lib_b, lib_c, overwrite=False, dry_run=True)
    # We expect at least the matching movie in A to be considered
    assert moved >= 1
    assert any(m.startswith("MOVE:") for m in outputs)
