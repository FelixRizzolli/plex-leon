
from pathlib import Path
from .utils import extract_tvdb_id, collect_tvdb_ids, move_file


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
