"""
Utility to generate a sample media library under the repository's data/ folder for season renamer tests.

It will create the following structure (if missing):

data/
  library-s/
    <TV Show Name with {tvdb-...}>/
      Season 01/
        <Show Name> - s01e01.mp4
        ...
      Season 02/
        ...

This script only creates TV shows (no movies) in library-s, using the same TV show list and episode structure as in generate_merge_test_libraries.py.

Re-running is safe and will skip copies that already exist.
"""

from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Iterable
import shutil
import sys
import importlib.util

# When executed directly, ensure repository root is on sys.path so
# `scripts.shared.tvshows` can be imported the same way other generators do.
if __name__ == "__main__" and __package__ is None:
    _repo_root = Path(__file__).resolve().parents[2]
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))

from scripts.generators.base_test_library_generator import BaseTestLibraryGenerator
from scripts.shared import get_tvdb_id_from_name
from scripts.shared.tvshows import tvshows as shared_tvshows, get_tvshow_episodes


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def create_seasons_and_episodes(base: Path, show_names: Iterable[str], *, seed: int | None = 42) -> None:
    rng = random.Random(seed)

    # Season folder name variants (with typos, casing, and language variants)
    season_variants = [
        "Season {num:02d}",
        "season {num:02d}",
        "SEASON {num:02d}",
        "Staffel {num:02d}",
        "staffel {num:02d}",
        "STAFFEL {num:02d}",
        "Saison {num:02d}",
        "saison {num:02d}",
        "SAISON {num:02d}",
        "Seazon {num:02d}",  # typo
        "Sesaon {num:02d}",  # typo
        "Seasn {num:02d}",   # typo
        "Saffel {num:02d}",  # typo
        "Stafel {num:02d}",  # typo
        "Seson {num:02d}",   # typo
        "Sesn {num:02d}",    # typo
        "Szn {num:02d}",     # typo/short
        "S {num:02d}",       # short
        "S-{num:02d}",       # short/alt
    ]

    # Assign a random variant per show, but keep it consistent for all seasons of that show
    show_to_variant: dict[str, str] = {}
    for show in show_names:
        show_to_variant[show] = rng.choice(season_variants)

    for show in show_names:
        tvdb = get_tvdb_id_from_name(show)
        show_dir = base / show
        show_dir.mkdir(parents=True, exist_ok=True)
        print(f"mkdir: {show_dir}")
        if not tvdb:
            continue

        seasons = get_tvshow_episodes(tvdb)
        if seasons is None:
            continue

        title_prefix = show.split(" {")[0].strip()
        season_fmt = show_to_variant[show]
        for season_num in sorted(seasons.keys()):
            season_folder = season_fmt.format(num=season_num)
            season_dir = show_dir / season_folder
            season_dir.mkdir(parents=True, exist_ok=True)
            print(f"mkdir: {season_dir}")
            for ep_num in range(1, seasons[season_num] + 1):
                dst = season_dir / \
                    f"{title_prefix} - s{season_num:02d}e{ep_num:02d}.mp4"
                if dst.exists():
                    print(f"skip (exists): {dst}")
                    continue
                dst.write_bytes(b"")
                print(f"touch: {dst}")


def main(argv: list[str] | None = None) -> int:
    gen = SeasonRenamerTestLibraryGenerator()
    return gen.run(argv)


class SeasonRenamerTestLibraryGenerator(BaseTestLibraryGenerator):
    """Generator for season renamer test library (library-s)."""

    # type: ignore[override]
    def execute(self, argv: list[str] | None = None) -> int:
        base = self.repo_root / "data" / "library-s"
        if argv is None:
            argv = sys.argv[1:]
        force = False
        if '--force' in argv:
            force = True
        if '-f' in argv:
            force = True

        if base.exists() and not force:
            resp = input(
                f"Target {base} exists. Delete it and recreate? [y/N]: ")
            if resp.strip().lower() not in ("y", "yes"):
                print("Aborted — target not removed.")
                return 1
            shutil.rmtree(base)

        base.mkdir(parents=True, exist_ok=True)

        # Use the centralized list of shows
        all_tvshows = [s["name"]
                       for s in shared_tvshows if isinstance(s.get("name"), str)]
        create_seasons_and_episodes(base, all_tvshows, seed=789)
        print("Done.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
