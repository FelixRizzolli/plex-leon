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
- library-b organizes all items under A/B/C/... buckets based on the first
    non-space character of the filename/folder name. If that character is a
    letter, the corresponding uppercase letter bucket is used; otherwise the
    item goes into the '0-9' bucket (single bucket for all non-letters).
    Example: "Avatar (2009) ..." -> library-b/A/Avatar (2009) ...
    Example: "2001: A Space Odyssey (1968) ..." -> library-b/0-9/2001: A ...
    Example: "[REC] (2007) ..." -> library-b/0-9/[REC] (2007) ...
    Re-running will also migrate any previously flat items into their correct
    bucket to avoid duplicates.

This script avoids external dependencies and uses urllib for downloads.
Re-running is safe and will skip downloads and copies that already exist.
"""

from __future__ import annotations


from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import shutil
import sys
import urllib.request

# Import downloads array from downloads.py
import importlib.util
import os

# Dynamically import downloads.py to get the downloads array


def get_downloads():
    script_dir = Path(__file__).parent
    downloads_path = script_dir / "downloads.py"
    spec = importlib.util.spec_from_file_location(
        "downloads", str(downloads_path))
    downloads_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(downloads_mod)  # type: ignore
    return downloads_mod.downloads


# Configuration ----------------------------------------------------------------

downloads = get_downloads()

library_a_movies: list[dict[str, object]] = [
    # in both libraries the same
    {"filename": "John Wick (2014) {tvdb-155}.mp4",
     "resolution": "1280x720", "size": "1"},
    # in both libraries the same
    {"filename": "John Wick 2 (2017) {tvdb-511}.mp4",
     "resolution": "720x480", "size": "2"},
    # better resolution than in library_b
    {"filename": "John Wick 3 (2019) {tvdb-6494}.mp4",
     "resolution": "1280x720", "size": "2"},
    # in both libraries the same
    {"filename": "John Wick 4 (2023) {tvdb-131523}.mp4",
     "resolution": "1280x720", "size": "10"},
    # in both libraries the same
    {"filename": "Inception (2010) {tvdb-27205}.mp4",
     "resolution": "1280x720", "size": "5"},
    # in both libraries the same
    {"filename": "The Matrix (1999) {tvdb-603}.mp4",
     "resolution": "720x480", "size": "2"},
    # in both libraries the same
    {"filename": "The Prestige (2006) {tvdb-1124}.mp4",
     "resolution": "360x240", "size": "2"},
    # in both libraries the same
    {"filename": "The Dark Knight (2008) {tvdb-155}.mp4",
     "resolution": "1280x720", "size": "10"},
    # in both libraries the same
    {"filename": "Forrest Gump (1994) {tvdb-13}.mp4",
     "resolution": "720x480", "size": "1"},
    # in both libraries the same
    {"filename": "Fight Club (1999) {tvdb-550}.mp4",
     "resolution": "640x360", "size": "5"},
    # only in library_a
    {"filename": "Interstellar (2014) {tvdb-157336}.mp4",
     "resolution": "640x360", "size": "2"},
    # only in library_a
    {"filename": "The Prestige (2006) {tvdb-1124}.mp4",
     "resolution": "360x240", "size": "1"},
    # less resolution and smaller filesize than in library_b
    {"filename": "Arrival (2016) {tvdb-329865}.mp4",
     "resolution": "1280x720", "size": "1"},
    # less resolution than in library_b
    {"filename": "Blade Runner 2049 (2017) {tvdb-335984}.mp4",
     "resolution": "720x480", "size": "5"},
    # less resolution and smaller filesize than in library_b
    {"filename": "Whiplash (2014) {tvdb-244786}.mp4",
     "resolution": "640x360", "size": "2"},
    # in both libraries the same
    {"filename": "The Lion King (1994) {tvdb-8587}.mp4",
     "resolution": "360x240", "size": "1"},
    # better resolution and greater filesize than in library_b
    {"filename": "The Shawshank Redemption (1994) {tvdb-278}.mp4",
     "resolution": "1280x720", "size": "10"},
    # less resolution and smaller filesize than in library_b
    {"filename": "Goodfellas (1990) {tvdb-769}.mp4",
     "resolution": "720x480", "size": "2"},
    # better resolution and greater filesize than in library_b
    {"filename": "Parasite (2019) {tvdb-496243}.mp4",
     "resolution": "640x360", "size": "5"},
    # in both libraries the same
    {"filename": "Spirited Away (2001) {tvdb-129}.mp4",
     "resolution": "360x240", "size": "2"},
]

library_b_movies: list[dict[str, object]] = [
    # in both libraries the same
    {"filename": "John Wick (2014) {tvdb-155}.mp4",
     "resolution": "1280x720", "size": "1"},
    # in both libraries the same
    {"filename": "John Wick 2 (2017) {tvdb-511}.mp4",
     "resolution": "720x480", "size": "2"},
    # less resolution than in library_a
    {"filename": "John Wick 3 (2019) {tvdb-6494}.mp4",
     "resolution": "720x480", "size": "2"},
    # in both libraries the same
    {"filename": "John Wick 4 (2023) {tvdb-131523}.mp4",
     "resolution": "1280x720", "size": "10"},
    # in both libraries the same
    {"filename": "Inception (2010) {tvdb-27205}.mp4",
     "resolution": "1280x720", "size": "5"},
    # in both libraries the same
    {"filename": "The Matrix (1999) {tvdb-603}.mp4",
     "resolution": "720x480", "size": "2"},
    # in both libraries the same
    {"filename": "The Prestige (2006) {tvdb-1124}.mp4",
     "resolution": "360x240", "size": "2"},
    # in both libraries the same
    {"filename": "The Dark Knight (2008) {tvdb-155}.mp4",
     "resolution": "1280x720", "size": "10"},
    # in both libraries the same
    {"filename": "Forrest Gump (1994) {tvdb-13}.mp4",
     "resolution": "720x480", "size": "1"},
    # in both libraries the same
    {"filename": "Fight Club (1999) {tvdb-550}.mp4",
     "resolution": "640x360", "size": "5"},
    # special-char starter to exercise 0-9 bucket
    {"filename": "[REC] (2007) {tvdb-12345}.mp4",
     "resolution": "640x360", "size": "5"},
    # another in the series
    {"filename": "[REC] 2 (2009) {tvdb-12346}.mp4",
     "resolution": "720x480", "size": "2"},
    # only in library_b
    {"filename": "The Beekeeper (2024) {tvdb-349405}.mp4",
     "resolution": "1280x720", "size": "1"},
    # only in library_b
    {"filename": "Avatar (2009) {tvdb-19995}.mp4",
     "resolution": "640x360", "size": "10"},
    # only in library_b
    {"filename": "The Godfather (1972) {tvdb-238}.mp4",
     "resolution": "360x240", "size": "2"},
    # only in library_b
    {"filename": "Pulp Fiction (1994) {tvdb-680}.mp4",
     "resolution": "720x480", "size": "5"},
    # greater filesize than in library_a
    {"filename": "Interstellar (2014) {tvdb-157336}.mp4",
     "resolution": "640x360", "size": "10"},
    # better resolution and greater filesize than in library_a
    {"filename": "Arrival (2016) {tvdb-329865}.mp4",
     "resolution": "1920x1080", "size": "5"},
    # better resolution than in library_a
    {"filename": "Blade Runner 2049 (2017) {tvdb-335984}.mp4",
     "resolution": "640x360", "size": "5"},
    # better resolution and greater filesize than in library_a
    {"filename": "Whiplash (2014) {tvdb-244786}.mp4",
     "resolution": "1280x720", "size": "2"},
    # less resolution and smaller filesize than in library_a
    {"filename": "The Shawshank Redemption (1994) {tvdb-278}.mp4",
     "resolution": "720x480", "size": "10"},
    # better resolution and greater filesize than in library_a
    {"filename": "Goodfellas (1990) {tvdb-769}.mp4",
     "resolution": "1280x720", "size": "2"},
    # less resolution and smaller filesize than in library_a
    {"filename": "Parasite (2019) {tvdb-496243}.mp4",
     "resolution": "360x240", "size": "5"},
    # in both libraries the same
    {"filename": "Spirited Away (2001) {tvdb-129}.mp4",
     "resolution": "360x240", "size": "2"},
]

library_a_tvshows: list[str] = [
    "Classroom of the Elite (2017) {tvdb-329822}",
    "Code Geass (2006) {tvdb-79525}",
    "Game of Thrones (2011) {tvdb-121361}",
]

library_b_tvshows: list[str] = [
    "Game of Thrones (2011) {tvdb-121361}",
]


# Helpers ----------------------------------------------------------------------

@dataclass(frozen=True)
class DownloadSpec:
    resolution: str
    size: str
    url: str


def repo_root() -> Path:
    # scripts/ is one level below repo root
    return Path(__file__).resolve().parents[1]


def download_to(path: Path, url: str, *, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0 and not overwrite:
        print(f"skip download (exists): {path}")
        return
    print(f"downloading: {url} -> {path}")
    tmp = path.with_suffix(path.suffix + ".part")
    try:
        with urllib.request.urlopen(url, timeout=60) as resp, open(tmp, "wb") as f:
            while True:
                chunk = resp.read(1024 * 256)
                if not chunk:
                    break
                f.write(chunk)
        tmp.replace(path)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: failed to download {url}: {e}")
        # create a small placeholder so subsequent steps can proceed
        if not path.exists():
            path.write_bytes(b"")


def ensure_download_cache(temp_dir: Path, specs: Iterable[DownloadSpec]) -> dict[tuple[str, str], Path]:
    """Ensure sample videos are present in temp_dir, keyed by (resolution, size)."""
    mapping: dict[tuple[str, str], Path] = {}
    for spec in specs:
        # preserve extension from URL if present
        ext = ".mp4"
        url_path = spec.url.split("?")[0]
        if "." in url_path.rsplit("/", 1)[-1]:
            ext = "." + url_path.rsplit(".", 1)[-1]
        dest = temp_dir / f"sample_{spec.resolution}_{spec.size}{ext}"
        download_to(dest, spec.url)
        mapping[(spec.resolution, spec.size)] = dest
    return mapping


def copy_movie(dst: Path, src: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        print(f"skip copy (exists): {dst}")
        return
    print(f"copy: {src.name} -> {dst}")
    shutil.copy2(src, dst)


def make_tv_folders(base: Path, names: Iterable[str]) -> None:
    for name in names:
        p = base / name
        p.mkdir(parents=True, exist_ok=True)
        print(f"mkdir: {p}")


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


def ensure_tv_folder_in_bucket(base: Path, name: str) -> None:
    """Create/migrate TV show folder under base/<Bucket>/<name>."""
    def find_bucketed_item(base: Path, name: str) -> Path | None:
        for b in [*(chr(c) for c in range(ord('A'), ord('Z') + 1)), "0-9"]:
            p = base / b / name
            if p.exists():
                return p
        return None

    bucket = letter_bucket(name)
    dst = base / bucket / name
    if dst.exists():
        print(f"skip mkdir (exists): {dst}")
        return
    flat = base / name
    if flat.exists():
        print(f"move (re-bucket): {flat} -> {dst}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(flat), str(dst))
        return
    other = find_bucketed_item(base, name)
    if other and other != dst:
        print(f"move (re-bucket): {other} -> {dst}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(other), str(dst))
        return
    dst.mkdir(parents=True, exist_ok=True)
    print(f"mkdir: {dst}")


def main(argv: list[str] | None = None) -> int:
    # Base directory under repo: data/
    base = repo_root() / "data"
    temp = base / "temp"
    lib_a = base / "library-a"
    lib_b = base / "library-b"
    lib_c = base / "library-c"

    # Create root and libraries
    for d in (base, temp, lib_a, lib_b, lib_c):
        d.mkdir(parents=True, exist_ok=True)

    # Prepare download specs and cache
    specs = [DownloadSpec(str(d["resolution"]), str(d["size"]), str(d["url"]))
             for d in downloads]
    cache = ensure_download_cache(temp, specs)

    # Populate library A movies
    for entry in library_a_movies:
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
    for entry in library_b_movies:
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

    # Create TV show folders only
    make_tv_folders(lib_a, library_a_tvshows)
    # For library-b, create TV show folders inside A/B/C/... buckets
    for show in library_b_tvshows:
        ensure_tv_folder_in_bucket(lib_b, show)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
