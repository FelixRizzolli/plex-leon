#!/usr/bin/env python3
import argparse
import re
import shutil
from pathlib import Path

TVDB_REGEX = re.compile(r"\{tvdb-(\d+)\}", re.IGNORECASE)


def extract_tvdb_id(name: str) -> str | None:
    media = TVDB_REGEX.search(name)
    return media.group(1) if media else None


def collect_tvdb_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    for entry in path.iterdir():
        # consider both files and top-level folders
        if not entry.name.startswith("."):
            tvdb = extract_tvdb_id(entry.name)
            if tvdb:
                ids.add(tvdb)
    return ids


def move_file(src: Path, dst: Path, *, overwrite: bool, dry_run: bool) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        print(f"SKIP exists: {dst}")
        return
    print(f"MOVE: {src} -> {dst}")
    if dry_run:
        return
    if dst.exists():
        if dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)
    shutil.move(src.as_posix(), dst.as_posix())


def main():
    parser = argparse.ArgumentParser(
        description="Move files and folders from library-a to library-c if their tvdb-id exists in library-b."
    )
    parser.add_argument("--lib-a", type=Path, default=Path("./data/library-a"),
                        help="Path to library-a (default: ./data/library-a)")
    parser.add_argument("--lib-b", type=Path, default=Path("./data/library-b"),
                        help="Path to library-b (default: ./data/library-b)")
    parser.add_argument("--lib-c", type=Path, default=Path("./data/library-c"),
                        help="Path to library-c (default: ./data/library-c)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing files in library-c")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be moved, but do not actually move files.")
    args = parser.parse_args()

    lib_a: Path = args.lib_a
    lib_b: Path = args.lib_b
    lib_c: Path = args.lib_c

    if not lib_a.is_dir():
        print(f"ERROR: library-a not found: {lib_a}")
        return
    if not lib_b.is_dir():
        print(f"ERROR: library-b not found: {lib_b}")
        return

    b_ids = collect_tvdb_ids(lib_b)
    print(f"Found {len(b_ids)} tvdb-ids in library-b")

    moved = 0
    skipped = 0

    for entry in lib_a.iterdir():
        if entry.name.startswith("."):
            continue
        tvdb = extract_tvdb_id(entry.name)
        if not tvdb:
            skipped += 1
            continue
        if tvdb in b_ids:
            dest = lib_c / entry.name
            move_file(entry, dest, overwrite=args.overwrite,
                      dry_run=args.dry_run)
            moved += 1
        else:
            skipped += 1

    print(f"Done. Eligible files/folders moved: {moved}; skipped: {skipped}.")


if __name__ == "__main__":
    main()
