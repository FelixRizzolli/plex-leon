from __future__ import annotations

import re
from pathlib import Path
import builtins
import pytest
from plex_leon.shared.utils import (
    extract_tvdb_id,
    collect_tvdb_ids,
    move_file,
    strip_tvdb_suffix,
    parse_episode_tag,
    normalize_episode_tag,
    is_season_like_dirname,
    get_season_number_from_dirname,
    iter_nonhidden_entries,
    format_bytes,
    format_resolution,
    two_step_case_rename,
    merge_directory_contents,
    remove_dir_if_empty,
)
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
        "[REC] (2007) {tvdb-12345}.mp4",
        ".hidden {tvdb-9999}.mp4",
        "No id.mp4",
    ]
    make_files(tmp_path, names)
    ids = collect_tvdb_ids(tmp_path)
    assert ids == {"155", "121361", "12345"}


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


def test_strip_tvdb_suffix():
    assert strip_tvdb_suffix(
        "Code Geass (2006) {tvdb-79525}") == "Code Geass (2006)"
    assert strip_tvdb_suffix("Show {TVDB-42}") == "Show"
    assert strip_tvdb_suffix("No id here") == "No id here"


@pytest.mark.parametrize(
    "name,parsed,normalized",
    [
        ("s1e2", (1, 2, None), "s01e02"),
        ("S01E02", (1, 2, None), "s01e02"),
        ("Title - S01E02-E03.mkv", (1, 2, 3), "s01e02-e03"),
        ("no tag", None, None),
    ],
)
def test_episode_tag_parsing_and_normalization(name, parsed, normalized):
    assert parse_episode_tag(name) == parsed
    assert normalize_episode_tag(name) == normalized


@pytest.mark.parametrize(
    "name,is_like,season",
    [
        ("Season 01", True, 1),
        ("season 1", True, 1),
        ("Staffel 02", True, 2),
        ("S-3", True, 3),
        ("Not a season", False, None),
        ("Two 1 numbers 2", False, None),
    ],
)
def test_season_dir_helpers(name, is_like, season):
    assert is_season_like_dirname(name) == is_like
    assert get_season_number_from_dirname(name) == season


def test_iter_nonhidden_entries(tmp_path: Path):
    # Create structure with hidden dir and file
    (tmp_path / ".hidden").mkdir()
    (tmp_path / ".hidden" / "a.txt").write_text("x")
    (tmp_path / "pub").mkdir()
    (tmp_path / "pub" / "b.txt").write_text("y")
    (tmp_path / ".root_hidden.txt").write_text("z")
    entries = list(iter_nonhidden_entries(tmp_path))
    names = sorted([e.relative_to(tmp_path).as_posix() for e in entries])
    assert "pub" in names
    assert "pub/b.txt" in names
    assert ".hidden" not in names and ".root_hidden.txt" not in names


def test_formatters():
    assert format_bytes(0) == "0 B"
    assert format_bytes(1023) == "1023 B"
    assert format_bytes(2048) == "2.0 KB"
    assert format_resolution((1920, 1080)) == "1920x1080"
    assert format_resolution(None) == "unknown"


def test_two_step_case_rename_real(tmp_path: Path):
    src = tmp_path / "File.TXT"
    src.write_text("data")
    dst = tmp_path / "file.txt"
    ok = two_step_case_rename(src, dst, dry_run=False)
    assert ok and dst.exists() and not src.exists()


def test_merge_directory_contents_and_remove(tmp_path: Path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    # conflict on a.txt
    (dst / "a.txt").write_text("dst")
    (src / "a.txt").write_text("src")
    (src / "b.txt").write_text("b")

    merge_directory_contents(src, dst)

    # a.txt should be under conflicts, b.txt should be in dst
    assert (dst / "b.txt").exists()
    conflicts = list((dst / ".plexleon_conflicts").glob("a*.txt"))
    assert conflicts, "Expected conflict file for a.txt"

    # src should now be empty and removable
    assert remove_dir_if_empty(src) is True
