import os
from pathlib import Path
from .utils import (
    extract_tvdb_id,
    collect_tvdb_ids,
    move_file,
    file_size,
    read_video_resolution,
)


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

    # Recursively collect TVDB ids from library-b to support bucketed layout (A-Z, 0-9)
    def _iter_nonhidden(root: Path):
        for dirpath, dirnames, filenames in os.walk(root):
            # prune hidden directories
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            # yield directories (TV shows) and files (movies)
            for d in dirnames:
                yield Path(dirpath) / d
            for f in filenames:
                if f.startswith("."):
                    continue
                yield Path(dirpath) / f

    b_ids: set[str] = set()
    b_index: dict[str, list[Path]] = {}
    for b_entry in _iter_nonhidden(lib_b):
        b_tvdb = extract_tvdb_id(b_entry.name)
        if not b_tvdb:
            continue
        b_ids.add(b_tvdb)
        b_index.setdefault(b_tvdb, []).append(b_entry)

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
            # Movies are files; TV shows are folders. Only apply extra logic for movies.
            if entry.is_file():
                # Find a counterpart in lib_b with the same tvdb id that is a file (movie)
                candidates = [p for p in b_index.get(tvdb, []) if p.is_file()]
                b_match: Path | None = candidates[0] if candidates else None

                # Compare resolution if both can be read
                better_resolution = False
                res_a = read_video_resolution(entry)
                res_b = read_video_resolution(
                    b_match) if b_match is not None else None
                if res_a and res_b:
                    pixels_a = res_a[0] * res_a[1]
                    pixels_b = res_b[0] * res_b[1]
                    better_resolution = pixels_a > pixels_b

                # Always compute sizes for details in logs
                size_a = file_size(entry)
                size_b = file_size(b_match) if b_match is not None else 0

                # Decide destination and reason
                if better_resolution:
                    dest_base = lib_c / "better-resolution"
                    reason = "better-resolution"
                else:
                    # Fall back to file size comparison
                    if size_a > size_b:
                        dest_base = lib_c / "greater-filesize"
                        reason = "greater-filesize"
                    else:
                        dest_base = lib_c / "to-delete"
                        reason = "to-delete"

                # Pretty formatting helpers
                def _fmt_res(res: tuple[int, int] | None) -> str:
                    return f"{res[0]}x{res[1]}" if res else "unknown"

                def _fmt_size(num_bytes: int) -> str:
                    units = ["B", "KB", "MB", "GB", "TB"]
                    size = float(num_bytes)
                    unit = 0
                    while size >= 1024 and unit < len(units) - 1:
                        size /= 1024.0
                        unit += 1
                    if unit == 0:
                        return f"{int(size)} {units[unit]}"
                    return f"{size:.1f} {units[unit]}"

                # Log the decision with details
                b_name = b_match.name if b_match is not None else "<missing>"
                print(
                    "DECISION:",
                    entry.name,
                    "->",
                    dest_base.name,
                    f"reason={reason}",
                    f"A[res={_fmt_res(res_a)}, size={_fmt_size(size_a)}]",
                    f"B(name={b_name})[res={_fmt_res(res_b)}, size={_fmt_size(size_b)}]",
                )

                dest = dest_base / entry.name
                move_file(entry, dest, overwrite=overwrite, dry_run=dry_run)
            else:
                # For folders (TV shows), keep the existing behavior
                dest = lib_c / entry.name
                move_file(entry, dest, overwrite=overwrite, dry_run=dry_run)
            moved += 1
        else:
            skipped += 1

    return moved, skipped
