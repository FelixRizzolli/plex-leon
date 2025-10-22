"""
Utility to generate sample media libraries under the repository's data/ folder.

It will create the following structure (if missing):

data/
  temp/               # cache: downloaded sample videos by resolution
  library-a/
  library-b/
  library-c/

For each movie listed below, a sample clip is copied from the cached downloads
into the corresponding library, using the exact filename provided. TV shows are
created as empty folders only.

Production-like layout note:
- library-a keeps a flat layout (files/folders directly under library-a)
- library-b buckets MOVIES under A/B/C/... based on the first non-space
    character of the filename. Non-letters go into the single bucket '0-9'.
    Example: "Avatar (2009) ..." -> library-b/A/Avatar (2009) ...
    Example: "2001: A Space Odyssey (1968) ..." -> library-b/0-9/2001: A ...
    Example: "[REC] (2007) ..." -> library-b/0-9/[REC] (2007) ...
    Re-running will migrate any previously flat movie files into their correct
    bucket to avoid duplicates.
- TV SHOWS are NOT bucketed in library-b: they live directly under
    library-b/<Show Name with {tvdb-...}>. Re-running will migrate any previously
    bucketed show folders back to flat paths.

This script avoids external dependencies and uses urllib for downloads.
Re-running is safe and will skip downloads and copies that already exist.
"""

from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Iterable
import shutil
import sys

# When executed directly (python scripts/generators/merge_tlg.py) the package
# imports like `scripts.shared` may not be resolvable. Ensure the repo root is
# on sys.path so `import scripts...` works.
if __name__ == "__main__" and __package__ is None:
    _repo_root = Path(__file__).resolve().parents[2]
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))

from scripts.generators.base_test_library_generator import BaseTestLibraryGenerator
from scripts.shared.movies import random_movies
from scripts.shared.tvshows import random_tvshows, tvshows as shared_tvshows


# Configuration ----------------------------------------------------------------

# Note: TV show lists and episode counts are derived from the shared
# `scripts.shared.tvshows` module below. Per-request we do not keep the
# previous hard-coded `library_a_tvshows` / `library_b_tvshows` lists here.


# Helpers ----------------------------------------------------------------------

def build_cache_mapping(temp_dir: Path) -> dict[tuple[str, str], Path]:
    """Build a (resolution, size) -> Path mapping from downloaded files in temp_dir.

    Parses filenames like 'sample_640x480_1.5MB.mp4' to extract resolution and size.
    """
    mapping: dict[tuple[str, str], Path] = {}
    for path in temp_dir.iterdir():
        if not path.is_file() or not path.name.startswith("sample_"):
            continue
        # Parse: sample_640x480_1.5MB.mp4 -> ('640x480', '1.5MB')
        stem = path.stem  # removes extension
        parts = stem.split("_")
        if len(parts) >= 3:
            resolution = parts[1]
            size = "_".join(parts[2:])  # handle cases like "1.5MB" or "10MB"
            mapping[(resolution, size)] = path
    return mapping


def copy_movie(dst: Path, src: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        print(f"skip copy (exists): {dst}")
        return
    print(f"copy: {src.name} -> {dst}")
    shutil.copy2(src, dst)


def movie_dict(title: str, *, resolution: str = "1920x1080", fmt: str = "mp4", size: str = "18MB") -> dict[str, str]:
    """Return a movie dict suitable for the generators.

    `title` should be the plain movie title (no extension). The function
    appends the file extension and returns a dict with the expected keys.
    """
    return {
        "filename": f"{title}.{fmt}",
        "resolution": resolution,
        "format": fmt,
        "size": size,
    }


def make_tv_folders(base: Path, names: Iterable[str]) -> None:
    for name in names:
        p = base / name
        p.mkdir(parents=True, exist_ok=True)
        print(f"mkdir: {p}")


# --- TV episodes generation ---------------------------------------------------

# Minimal TVDB id extractor (local copy to keep this script self-contained)
_TVDB_RE = re.compile(r"\{tvdb-(\d+)\}", re.IGNORECASE)


def _tvdb_id_from_name(name: str) -> str | None:
    m = _TVDB_RE.search(name)
    return m.group(1) if m else None


# Episode map is derived from `scripts.shared.tvshows` (see below). The
# previous hard-coded EPISODE_MAP has been removed to avoid duplication.

def _episodes_for_tvdb(tvdb: str) -> dict[int, int] | None:
    """Return the episodes mapping for a TVDB id by looking it up in
    `scripts.shared.tvshows.tvshows`. Returns None if not found.
    """
    for s in shared_tvshows:
        name = s.get("name")
        episodes = s.get("episodes")
        if not isinstance(name, str) or not isinstance(episodes, dict):
            continue
        m = _TVDB_RE.search(name)
        if m and m.group(1) == tvdb:
            return episodes
    return None


def _distinct_cache_keys(cache: dict[tuple[str, str], Path]) -> list[tuple[str, str]]:
    # Return a stable-ordered list of resolution/size combos
    return sorted(cache.keys())


def _show_dir_for_lib_b(base: Path, show_name: str) -> Path:
    # TV shows in library-b are flat (not bucketed)
    return base / show_name


def create_seasons_and_episodes(
    base: Path,
    show_names: Iterable[str],
    cache: dict[tuple[str, str], Path],
    *,
    bucketed: bool = False,
    seed: int | None = 42,
) -> None:
    """Create Season XX folders and episode files for provided shows.

    - base: library root (e.g., data/library-a or data/library-b)
    - show_names: iterable of show folder names (must include the TVDB tag)
    - cache: mapping from (resolution, size) -> sample clip Path
        - bucketed: when True, place shows under A–Z/0-9 buckets (legacy behavior).
            For library-b in production, this should be False (flat layout for shows).
    - seed: optional RNG seed for reproducible random picks
    """
    rng = random.Random(seed)
    keys = _distinct_cache_keys(cache)
    if not keys:
        print("WARN: no cached sample videos available; skipping episode files")
        # dummy fallback; files will be empty if missing
        keys = [("640x360", "1")]

    for show in show_names:
        tvdb = _tvdb_id_from_name(show)
        seasons = _episodes_for_tvdb(tvdb) if tvdb else None
        if not tvdb or seasons is None:
            # Create the show folder at least (and continue)
            target = (_show_dir_for_lib_b(base, show)
                      if bucketed else (base / show))
            target.mkdir(parents=True, exist_ok=True)
            print(f"mkdir: {target}")
            continue
        # seasons was retrieved via _episodes_for_tvdb
        show_dir = (_show_dir_for_lib_b(base, show)
                    if bucketed else (base / show))
        show_dir.mkdir(parents=True, exist_ok=True)
        print(f"mkdir: {show_dir}")

        # Build a canonical series title prefix for episode filenames
        # Keep the folder name prefix before the tvdb tag
        title_prefix = show.split(" {")[0].strip()

        for season_num in sorted(seasons.keys()):
            season_dir = show_dir / f"Season {season_num:02d}"
            season_dir.mkdir(parents=True, exist_ok=True)
            print(f"mkdir: {season_dir}")

            for ep_num in range(1, seasons[season_num] + 1):
                # Randomly pick a resolution/size combo and get the cached file
                res, size = rng.choice(keys)
                src = cache.get((res, size))
                if src is None:
                    # Shouldn't happen, but guard anyway
                    print(
                        f"WARN: cache miss for {res} {size} while creating {title_prefix} s{season_num:02d}e{ep_num:02d}"
                    )
                    # Create an empty placeholder
                    dst = season_dir / \
                        f"{title_prefix} - s{season_num:02d}e{ep_num:02d}.mp4"
                    if not dst.exists():
                        dst.write_bytes(b"")
                    continue

                dst = season_dir / \
                    f"{title_prefix} - s{season_num:02d}e{ep_num:02d}.mp4"
                copy_movie(dst, src)


# Bucketing helpers for library-b --------------------------------------------

def letter_bucket(name: str) -> str:
    """Return A-Z bucket by first non-space character, else '0-9' for non-letters."""
    s = name.lstrip()
    if not s:
        return "0-9"
    ch = s[0]
    return ch.upper() if ch.isalpha() else "0-9"


def copy_or_move_into_bucket(base: Path, name: str, src: Path) -> None:
    """Place movie file under base/<Bucket>/<name>.

    If a flat or differently-bucketed item exists, migrate it via move to keep
    the operation idempotent and avoid duplicates across script versions.
    """
    def find_bucketed_item(base: Path, name: str) -> Path | None:
        # Search any existing bucket (A-Z and '0-9')
        for b in [*(chr(c) for c in range(ord('A'), ord('Z') + 1)), "0-9"]:
            p = base / b / name
            if p.exists():
                return p
        return None

    bucket = letter_bucket(name)
    dst = base / bucket / name
    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists():
        print(f"skip copy (exists): {dst}")
        return

    flat = base / name
    if flat.exists():
        print(f"move (re-bucket): {flat} -> {dst}")
        shutil.move(str(flat), str(dst))
        return

    other = find_bucketed_item(base, name)
    if other and other != dst:
        print(f"move (re-bucket): {other} -> {dst}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(other), str(dst))
        return

    copy_movie(dst, src)


def ensure_tv_folder_flat(base: Path, name: str) -> None:
    """Create/migrate TV show folder directly under base/<name> (no buckets).

    If the show exists in any bucket (legacy), move it back to flat.
    """
    def find_bucketed_item(base: Path, name: str) -> Path | None:
        for b in [*(chr(c) for c in range(ord('A'), ord('Z') + 1)), "0-9"]:
            p = base / b / name
            if p.exists():
                return p
        return None

    dst = base / name
    if dst.exists():
        print(f"skip mkdir (exists): {dst}")
        return

    bucketed = find_bucketed_item(base, name)
    if bucketed and bucketed != dst:
        print(f"move (unbucket): {bucketed} -> {dst}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(bucketed), str(dst))
        return

    dst.mkdir(parents=True, exist_ok=True)
    print(f"mkdir: {dst}")


def main(argv: list[str] | None = None) -> int:
    gen = MergeTestLibraryGenerator()
    return gen.run(argv)


class MergeTestLibraryGenerator(BaseTestLibraryGenerator):
    """Generator for merge test libraries (library-a/library-b/library-c).

    This class builds three libraries under `data/` for merge testing:
    - `library-a` and `library-b` contain movie files (with intentional
      resolution/format/size mismatches to exercise merge logic).
    - `library-c` is reserved for any downstream tests (not populated here).

    The generator creates deterministic movie selections using the
    `random_movies` helper (seeded) and builds consistent movie dicts via
    `movie_dict`. TV show folders (with seasons/episodes) are created using
    `create_seasons_and_episodes`; episode counts are looked up from the
    centralized `scripts.shared.tvshows` data (not from a local EPISODE_MAP).

    Attributes
    ----------
    library_a_movies, library_b_movies : list[dict]
            Populated by `_create_movie_libraries` before `execute` copies files.
    library_a_tvshows, library_b_tvshows : list[str]
            Populated by `_create_tvshow_libraries` and used by `execute` to
            determine which TV show folders to create for each library.

    Attributes
    ----------
    library_a_movies, library_b_movies : list[dict]
        Populated by `_create_movie_libraries` before `execute` copies files.
    library_a_tvshows, library_b_tvshows : list[str]
        Predefined lists of TV show folder names used by `execute`.
    """

    library_a_movies: list[dict[str, object]]
    library_b_movies: list[dict[str, object]]

    def _create_movie_libraries(self):
        """Populate `self.library_a_movies` and `self.library_b_movies`.

        Uses deterministic, seeded calls to `random_movies` to build disjoint
        title categories (identical in both libraries, better-in-A, better-in-B,
        filesize mismatches, unique-to-A/B). A local `exclude` set is updated
        after each pick to avoid title reuse across categories.

        Each resulting movie entry is built with `movie_dict(...)` so the
        structure matches what `execute` expects: keys `filename`,
        `resolution`, `format`, and `size`.
        """
        exclude: set[str] = set()

        # movies which are present in both libraries (identical)
        movies_in_both = random_movies(5, seed=100)
        exclude.update(movies_in_both)

        # movies where A has better quality than B (better quality in A)
        movies_better_in_a = random_movies(5, seed=101, exclude=exclude)
        exclude.update(movies_better_in_a)

        # movies where B has better quality than A (better quality in B)
        movies_better_in_b = random_movies(5, seed=102, exclude=exclude)
        exclude.update(movies_better_in_b)

        # movies where A has greater filesize but same resolution (or vice versa)
        movies_filesize_a = random_movies(5, seed=103, exclude=exclude)
        exclude.update(movies_filesize_a)
        movies_filesize_b = random_movies(5, seed=104, exclude=exclude)
        exclude.update(movies_filesize_b)

        # movies unique to each library
        movies_only_a = random_movies(5, seed=105, exclude=exclude)
        exclude.update(movies_only_a)
        movies_only_b = random_movies(5, seed=106, exclude=exclude)
        exclude.update(movies_only_b)

        # Build library A
        self.library_a_movies = []
        for title in movies_in_both:
            self.library_a_movies.append(movie_dict(
                title, resolution="1920x1080", fmt="mp4", size="18MB"))
        for title in movies_only_a:
            self.library_a_movies.append(movie_dict(
                title, resolution="1920x1080", fmt="mp4", size="18MB"))
        for title in movies_better_in_a:
            self.library_a_movies.append(movie_dict(
                title, resolution="1920x1080", fmt="mp4", size="18MB"))
        for title in movies_better_in_b:
            self.library_a_movies.append(movie_dict(
                title, resolution="1280x720", fmt="mp4", size="18MB"))
        for title in movies_filesize_a:
            self.library_a_movies.append(movie_dict(
                title, resolution="1920x1080", fmt="mp4", size="10MB"))
        for title in movies_filesize_b:
            self.library_a_movies.append(movie_dict(
                title, resolution="1920x1080", fmt="avi", size="2.3MB"))

        # Build library B
        self.library_b_movies = []
        for title in movies_in_both:
            self.library_b_movies.append(movie_dict(
                title, resolution="1920x1080", fmt="mp4", size="18MB"))
        for title in movies_only_b:
            self.library_b_movies.append(movie_dict(
                title, resolution="1920x1080", fmt="mp4", size="18MB"))
        for title in movies_better_in_b:
            self.library_b_movies.append(movie_dict(
                title, resolution="1920x1080", fmt="mp4", size="18MB"))
        # mirrored lower-res entries for A's better_in_b
        for title in movies_better_in_a:
            self.library_b_movies.append(movie_dict(
                title, resolution="1280x720", fmt="mp4", size="18MB"))
        for title in movies_filesize_b:
            self.library_b_movies.append(movie_dict(
                title, resolution="1920x1080", fmt="mp4", size="18MB"))
        for title in movies_filesize_a:
            self.library_b_movies.append(movie_dict(
                title, resolution="640x480", fmt="mp4", size="1.5MB"))

    def _create_tvshow_libraries(self, *, seed: int | None = None) -> None:
        """Populate `self.library_a_tvshows` and `self.library_b_tvshows`.

        Build disjoint TV-show categories mirroring the movie categories and
        store folder-name strings on the instance:

        - `both`: shows present in both libraries (identical)
        - `better_in_a`: shows where A has better quality than B
        - `better_in_b`: shows where B has better quality than A
        - `filesize_a` / `filesize_b`: shows with filesize mismatches
        - `only_a` / `only_b`: shows unique to each library

        Selections are deterministic when a `seed` is provided. The method
        uses `random_tvshows(...)` and an `exclude` set to ensure categories
        do not overlap.
        """
        exclude: set[str] = set()

        # both libraries
        both = random_tvshows(4, seed=(seed or 200))
        exclude.update([s["name"] for s in both])

        # quality/size variants
        better_in_a = random_tvshows(3, seed=(seed or 201), exclude=exclude)
        exclude.update([s["name"] for s in better_in_a])
        better_in_b = random_tvshows(3, seed=(seed or 202), exclude=exclude)
        exclude.update([s["name"] for s in better_in_b])

        filesize_a = random_tvshows(2, seed=(seed or 203), exclude=exclude)
        exclude.update([s["name"] for s in filesize_a])
        filesize_b = random_tvshows(2, seed=(seed or 204), exclude=exclude)
        exclude.update([s["name"] for s in filesize_b])

        # unique-to-each
        only_a = random_tvshows(3, seed=(seed or 205), exclude=exclude)
        exclude.update([s["name"] for s in only_a])
        only_b = random_tvshows(3, seed=(seed or 206), exclude=exclude)
        exclude.update([s["name"] for s in only_b])

        # Compose instance lists: combine 'both' + appropriate variants
        self.library_a_tvshows = [s["name"] for s in both]
        self.library_a_tvshows += [s["name"] for s in better_in_a]
        self.library_a_tvshows += [s["name"] for s in filesize_a]
        self.library_a_tvshows += [s["name"] for s in only_a]

        self.library_b_tvshows = [s["name"] for s in both]
        self.library_b_tvshows += [s["name"] for s in better_in_b]
        self.library_b_tvshows += [s["name"] for s in filesize_b]
        self.library_b_tvshows += [s["name"] for s in only_b]

    def execute(self, argv: list[str] | None = None) -> int:
        """Generate the `data/` libraries and return an exit code.

        Steps performed:
        1. Create/clean the `data/library-a`, `data/library-b`, and
           `data/library-c` directories (asks before deleting unless
           `--force`/`-f` is passed).
        2. Build a cache mapping from already-downloaded sample clips.
        3. Call `_create_movie_libraries()` to deterministically choose movie
           lists for library-a and library-b.
        4. Copy or move movie files into `library-a` and `library-b` using the
           cache mapping.
        5. Create TV show folders and populate seasons/episodes.

        Parameters
        ----------
        argv : list[str] | None
            Command-line style arguments (supports `--force` / `-f`). When
            None, `sys.argv[1:]` is used.

        Returns
        -------
        int
            0 on success, 1 if the user aborts when asked to delete existing
            targets.
        """
        # Base directory under repo: data/
        base = self.repo_root / "data"
        lib_a = base / "library-a"
        lib_b = base / "library-b"
        lib_c = base / "library-c"

        # Create root and libraries
        if argv is None:
            argv = sys.argv[1:]
        force = False
        if '--force' in argv:
            force = True
        if '-f' in argv:
            force = True

        # Remove and recreate target folders to ensure deterministic generation
        # Note: temp_dir is already created by base class run() method
        for d in (lib_a, lib_b, lib_c):
            if d.exists() and not force:
                resp = input(
                    f"Target {d} exists. Delete it and recreate? [y/N]: ")
                if resp.strip().lower() not in ("y", "yes"):
                    print("Aborted — target not removed.")
                    return 1
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True, exist_ok=True)

        # Build cache mapping from downloaded files (already done by base class)
        cache = build_cache_mapping(self.temp_dir)

        # Populate library A movies (generate lists deterministically)
        self._create_movie_libraries()
        # Populate tvshow lists deterministically as well
        self._create_tvshow_libraries(seed=1234)
        for entry in self.library_a_movies:
            # e.g., "John Wick (2014) {tvdb-155}.mp4"
            fname = str(entry["filename"])
            res = str(entry["resolution"])
            size = str(entry["size"])
            src = cache.get((res, size))
            if src is None:
                print(
                    f"WARN: no cached clip for resolution {res} size {size}, skipping {fname}")
                continue
            copy_movie(lib_a / fname, src)

        # Populate library B movies (bucketed under A/B/C/... like production)
        for entry in self.library_b_movies:
            # e.g., "John Wick 2 (2017) {tvdb-511}.mp4"
            fname = str(entry["filename"])
            res = str(entry["resolution"])
            size = str(entry["size"])
            src = cache.get((res, size))
            if src is None:
                print(
                    f"WARN: no cached clip for resolution {res} size {size}, skipping {fname}")
                continue
            copy_or_move_into_bucket(lib_b, fname, src)

        # Create TV show folders and populate with seasons/episodes
        create_seasons_and_episodes(
            lib_a, self.library_a_tvshows, cache, bucketed=False, seed=123)
        # For library-b, TV shows are flat (no buckets). Migrate any legacy
        # bucketed folders back to flat, then create seasons/episodes.
        for show in self.library_b_tvshows:
            ensure_tv_folder_flat(lib_b, show)
        create_seasons_and_episodes(
            lib_b, self.library_b_tvshows, cache, bucketed=False, seed=456)

        print("Done.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
