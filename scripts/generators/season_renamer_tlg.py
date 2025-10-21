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
from base_test_library_generator import BaseTestLibraryGenerator

# --- TV show config (copied from generate_merge_test_libraries.py) ---
library_a_tvshows = [
    "Classroom of the Elite (2017) {tvdb-329822}",
    "Code Geass (2006) {tvdb-79525}",
    "Game of Thrones 2011 {tvdb-121361}",
    "Attack on Titan (2013) {tvdb-267440}",
    "Death Note (2006) {tvdb-79434}",
    "Overlord (2015) {tvdb-295068}",
    "Breaking Bad (2008) {tvdb-81189}",
    "The Day of the Jackal (1973) {tvdb-80379}",
]
library_b_tvshows = [
    "Game of Thrones 2011 {tvdb-121361}",
    "Attack on Titan (2013) {tvdb-267440}",
    "My Name (2021) {tvdb-410235}",
    "Squid Game (2021) {tvdb-407183}",
    "One Punch Man (2015) {tvdb-299880}",
    "Breaking Bad (2008) {tvdb-81189}",
]

# Known season/episode counts for the sample shows we generate
EPISODE_MAP = {
    "121361": {1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10, 7: 7, 8: 6},
    "79525": {1: 25, 2: 25},
    "329822": {1: 12, 2: 13, 3: 13},
    "267440": {1: 25, 2: 12, 3: 22, 4: 28},
    "79434": {1: 37},
    "295068": {1: 13, 2: 13, 3: 13, 4: 13},
    "81189": {1: 7, 2: 13, 3: 13, 4: 13, 5: 16},
    "80379": {1: 1},
    "410235": {1: 8},
    "407183": {1: 9},
    "299880": {1: 12, 2: 12},
}

_TVDB_RE = re.compile(r"\{tvdb-(\d+)}", re.IGNORECASE)


def _tvdb_id_from_name(name: str) -> str | None:
    m = _TVDB_RE.search(name)
    return m.group(1) if m else None


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
    show_to_variant = {}
    for show in show_names:
        show_to_variant[show] = rng.choice(season_variants)

    for show in show_names:
        tvdb = _tvdb_id_from_name(show)
        show_dir = base / show
        show_dir.mkdir(parents=True, exist_ok=True)
        print(f"mkdir: {show_dir}")
        if not tvdb or tvdb not in EPISODE_MAP:
            continue
        seasons = EPISODE_MAP[tvdb]
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
        # Use all unique TV shows from both libraries
        all_tvshows = sorted(set(library_a_tvshows + library_b_tvshows))
        create_seasons_and_episodes(base, all_tvshows, seed=789)
        print("Done.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
