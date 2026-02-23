"""
Utility to generate a sample media library under the repository's data/ folder for season renamer tests.

It will create the following structure (if missing):

data/
  library-s/
    <TV Show Name with {tvdb-...}>/
      Season 01/          ← folder name varies (staffel, saison, typos, …)
        <Show Name> - s01e01.mp4
        ...
      Season 02/
        ...

This script only creates TV shows (no movies) in library-s, using the same TV show list and episode structure as in generate_merge_test_libraries.py.

Season folder name variants are randomised per show (see `season_variants` list):
casing variants, language variants (Staffel, Saison), and deliberate typos are all
represented so that the season-renamer can be exercised against diverse inputs.

Episode filenames inside each season folder occasionally use multi-episode range tags
(e.g. ``s01e01-e03``) to represent files that span several episodes.  The season
renamer itself only touches directory names, so these files are expected to survive
the rename untouched.

Re-running is safe and will skip copies that already exist.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Iterable
import shutil
import sys

# When executed directly, ensure repository root is on sys.path so
# `tests.integration.shared.tvshows` can be imported the same way other generators do.
if __name__ == "__main__" and __package__ is None:
    _repo_root = Path(__file__).resolve().parents[3]
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))

from tests.integration.generators.base_test_library_generator import BaseTestLibraryGenerator
from tests.integration.shared import get_tvdb_id_from_name
from tests.integration.shared.tvshows import tvshows as shared_tvshows, get_tvshow_episodes


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def create_seasons_and_episodes(
    base: Path,
    show_names: Iterable[str],
    *,
    generator: BaseTestLibraryGenerator,
    seed: int | None = 42,
) -> None:
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
        generator.log_info(f"mkdir: {show_dir}")
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
            generator.log_info(f"mkdir: {season_dir}")
            ep_total = seasons[season_num]
            ep_num = 1
            while ep_num <= ep_total:
                # ~1 in 8 chance of a multi-episode range file (2–4 eps, capped at remaining)
                remaining = ep_total - ep_num + 1
                max_range = min(4, remaining)
                is_range = max_range >= 2 and rng.random() < 0.125
                if is_range:
                    range_len = rng.randint(2, max_range)
                    ep_end = ep_num + range_len - 1
                    dst = season_dir / f"{title_prefix} - s{season_num:02d}e{ep_num:02d}-e{ep_end:02d}.mp4"
                    if not dst.exists():
                        dst.write_bytes(b"")
                        generator.log_info(f"touch: {dst}")
                    else:
                        generator.log_info(f"skip (exists): {dst}")
                    ep_num += range_len
                else:
                    dst = season_dir / f"{title_prefix} - s{season_num:02d}e{ep_num:02d}.mp4"
                    if not dst.exists():
                        dst.write_bytes(b"")
                        generator.log_info(f"touch: {dst}")
                    else:
                        generator.log_info(f"skip (exists): {dst}")
                    ep_num += 1


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
                self.log_info("Aborted — target not removed.")
                return 1
            shutil.rmtree(base)

        base.mkdir(parents=True, exist_ok=True)

        # Use the centralized list of shows
        all_tvshows = [s["name"]
                       for s in shared_tvshows if isinstance(s.get("name"), str)]
        create_seasons_and_episodes(base, all_tvshows,
                                    generator=self, seed=789)
        self.log_info("Done.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
