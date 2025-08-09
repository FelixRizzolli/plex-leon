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


# Configuration ----------------------------------------------------------------

downloads: list[dict[str, object]] = [
    {"resolution": 1920, "url": "https://file-examples.com/storage/fe79eba60468962519bf772/2017/04/file_example_MP4_1920_18MG.mp4"},
    {"resolution": 480, "url": "https://file-examples.com/storage/fe79eba60468962519bf772/2017/04/file_example_MP4_480_1_5MG.mp4"},
    {"resolution": 640, "url": "https://file-examples.com/storage/fe79eba60468962519bf772/2017/04/file_example_MP4_640_3MG.mp4"},
    {"resolution": 1280, "url": "https://file-examples.com/storage/fe79eba60468962519bf772/2017/04/file_example_MP4_1280_10MG.mp4"},
]

library_a_movies: list[dict[str, object]] = [
    {"filename": "John Wick (2014) {tvdb-155}.mp4", "resolution": 1920},
    {"filename": "John Wick 2 (2017) {tvdb-511}.mp4", "resolution": 480},
    {"filename": "John Wick 3 (2019) {tvdb-6494}.mp4", "resolution": 640},
    {"filename": "John Wick 4 (2023) {tvdb-131523}.mp4", "resolution": 1280},
]

library_b_movies: list[dict[str, object]] = [
    {"filename": "John Wick (2014) {tvdb-155}.mp4", "resolution": 1280},
    {"filename": "John Wick 2 (2017) {tvdb-511}.mp4", "resolution": 480},
    {"filename": "John Wick 3 (2019) {tvdb-6494}.mp4", "resolution": 1920},
    {"filename": "John Wick 4 (2023) {tvdb-131523}.mp4", "resolution": 1280},
    {"filename": "The Beekeeper (2024) {tvdb-349405}.mp4", "resolution": 1280},
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
    resolution: int
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


def ensure_download_cache(temp_dir: Path, specs: Iterable[DownloadSpec]) -> dict[int, Path]:
    """Ensure sample videos are present in temp_dir, keyed by resolution.

    Returns a mapping: resolution -> file path
    """
    mapping: dict[int, Path] = {}
    for spec in specs:
        # preserve extension from URL if present
        ext = ".mp4"
        url_path = spec.url.split("?")[0]
        if "." in url_path.rsplit("/", 1)[-1]:
            ext = "." + url_path.rsplit(".", 1)[-1]
        dest = temp_dir / f"sample_{spec.resolution}{ext}"
        download_to(dest, spec.url)
        mapping[spec.resolution] = dest
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
    specs = [DownloadSpec(int(d["resolution"]), str(d["url"]))
             for d in downloads]
    cache = ensure_download_cache(temp, specs)

    # Populate library A movies
    for entry in library_a_movies:
        # e.g., "John Wick (2014) {tvdb-155}.mp4"
        fname = str(entry["filename"])
        res = int(entry["resolution"])   # e.g., 1920
        src = cache.get(res)
        if src is None:
            print(
                f"WARN: no cached clip for resolution {res}, skipping {fname}")
            continue
        copy_movie(lib_a / fname, src)

    # Populate library B movies
    for entry in library_b_movies:
        # e.g., "John Wick 2 (2017) {tvdb-511}.mp4"
        fname = str(entry["filename"])
        res = int(entry["resolution"])   # e.g., 480
        src = cache.get(res)
        if src is None:
            print(
                f"WARN: no cached clip for resolution {res}, skipping {fname}")
            continue
        copy_movie(lib_b / fname, src)

    # Create TV show folders only
    make_tv_folders(lib_a, library_a_tvshows)
    make_tv_folders(lib_b, library_b_tvshows)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
