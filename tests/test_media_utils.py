from __future__ import annotations

from pathlib import Path

from plex_leon import file_size, read_video_resolution


def test_file_size_returns_correct_size(tmp_path: Path):
    p = tmp_path / "a.bin"
    data = b"hello world" * 123
    p.write_bytes(data)
    assert file_size(p) == len(data)


def test_file_size_on_missing_or_dir(tmp_path: Path):
    missing = tmp_path / "nope.bin"
    assert file_size(missing) == 0
    d = tmp_path / "folder"
    d.mkdir()
    assert file_size(d) == 0


def test_read_video_resolution_handles_missing_tools_gracefully(tmp_path: Path):
    p = tmp_path / "dummy.mp4"
    p.write_bytes(b"not a real video")
    res = read_video_resolution(p)
    assert res is None or (isinstance(res, tuple) and len(res) == 2)
