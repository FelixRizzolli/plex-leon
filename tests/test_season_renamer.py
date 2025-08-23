from __future__ import annotations

from pathlib import Path
import builtins
import pytest

from plex_leon.season_renamer import process_library as season_process
from utils import make_files


def test_season_renamer_variants(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    show = tmp_path / "library-s" / "Some Show (2011) {tvdb-12345}"
    # Create variant season folders
    make_files(show, [
        "season 01/",
        "Staffel 02/",
        "S-3/",
    ])

    # Create dummy files inside to simulate content
    for p in (show / "season 01", show / "Staffel 02", show / "S-3"):
        (p / "a.txt").write_text("x")

    outputs: list[str] = []

    def fake_print(*args, **kwargs):
        outputs.append(" ".join(map(str, args)))

    monkeypatch.setattr(builtins, "print", fake_print)

    # dry run shows planned ops
    renamed_count, = season_process(tmp_path / "library-s", dry_run=True)
    assert renamed_count == 3
    assert any("RENAME:" in ln for ln in outputs)

    # execute
    outputs.clear()
    renamed_count, = season_process(tmp_path / "library-s", dry_run=False)
    assert renamed_count == 3

    # verify canonical names
    assert (show / "Season 01").exists()
    assert (show / "Season 02").exists()
    assert (show / "Season 03").exists()
