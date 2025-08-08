from __future__ import annotations

import re
import shutil
from pathlib import Path

# Compiled regex used to extract TVDB ids like "{tvdb-12345}" from filenames
TVDB_REGEX = re.compile(r"\{tvdb-(\d+)\}", re.IGNORECASE)


def extract_tvdb_id(name: str) -> str | None:
    """Return the TVDB id embedded in a filename/folder name or None.

    Example: "John Wick (2014) {tvdb-155}.mp4" -> "155"
    """
    media = TVDB_REGEX.search(name)
    return media.group(1) if media else None


def collect_tvdb_ids(path: Path) -> set[str]:
    """Collect TVDB ids from the immediate children of a directory.

    Hidden entries (starting with a dot) are ignored. Both files and folders
    are considered.
    """
    ids: set[str] = set()
    for entry in path.iterdir():
        if not entry.name.startswith("."):
            tvdb = extract_tvdb_id(entry.name)
            if tvdb:
                ids.add(tvdb)
    return ids


def move_file(src: Path, dst: Path, *, overwrite: bool, dry_run: bool) -> None:
    """Move a file/folder from src to dst.

    - Creates destination parent directories as needed.
    - Prints an action message (or a skip message when not overwriting).
    - If dry_run=True, only prints without modifying the filesystem.
    """
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


def process_libraries(
    lib_a: Path,
    lib_b: Path,
    lib_c: Path,
    *,
    overwrite: bool,
    dry_run: bool,
) -> tuple[int, int]:
    """Core operation: move entries from lib_a to lib_c if their TVDB id exists in lib_b.

    Returns a tuple (moved_count, skipped_count).
    """
    if not lib_a.is_dir():
        print(f"ERROR: library-a not found: {lib_a}")
        return (0, 0)
    if not lib_b.is_dir():
        print(f"ERROR: library-b not found: {lib_b}")
        return (0, 0)

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
            move_file(entry, dest, overwrite=overwrite, dry_run=dry_run)
            moved += 1
        else:
            skipped += 1

    return moved, skipped
