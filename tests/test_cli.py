from __future__ import annotations

import re
from pathlib import Path

import builtins

import pytest

from plex_leon import main
from utils import make_files


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
        "[REC] (2007) {tvdb-12345}.mp4",
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

    # emulate CLI by passing argv to plex_leon.main (defaults to 'migrate')
    main(argv)

    # Only the item with tvdb-155 should be considered eligible
    moved_msgs = [m for m in outputs if m.startswith("MOVE:")]
    assert len(moved_msgs) == 1
    assert "tvdb-155" in "\n".join(outputs)
    assert any("Found" in m for m in outputs)
    assert any("Done." in m for m in outputs)
