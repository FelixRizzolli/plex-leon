import os
from pathlib import Path
from .utils import (
    extract_tvdb_id,
    collect_tvdb_ids,
    move_file,
    file_size,
    read_video_resolution,
    iter_nonhidden_entries,
    parse_season_episode,
    find_episode_in_dirs,
    format_bytes,
    format_resolution,
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
k
    Returns a tuple (moved_count, skipped_count).
    """
    if not lib_a.is_dir():
        print(f"ERROR: library-a not found: {lib_a}")
        return (0, 0)
    if not lib_b.is_dir():
        print(f"ERROR: library-b not found: {lib_b}")
        return (0, 0)

    b_ids: set[str] = set()
    b_index: dict[str, list[Path]] = {}
    # Recursively collect TVDB ids from library-b to support bucketed layout (A-Z, 0-9)
    for b_entry in iter_nonhidden_entries(lib_b):
        b_tvdb = extract_tvdb_id(b_entry.name)
        if not b_tvdb:
            continue
        b_ids.add(b_tvdb)
        b_index.setdefault(b_tvdb, []).append(b_entry)

    print(f"Found {len(b_ids)} tvdb-ids in library-b")

    moved = 0
    skipped = 0

    # Helper lambdas for concise logging
    _fmt_res = format_resolution
    _fmt_size = format_bytes

    for entry in lib_a.iterdir():
        if entry.name.startswith("."):
            continue
        tvdb = extract_tvdb_id(entry.name)
        if not tvdb:
            skipped += 1
            continue
        if tvdb in b_ids:
            # Movies are files; TV shows are folders. Apply per-episode logic for TV shows.
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
                moved += 1
            else:
                # For folders (TV shows), compare and move episodes individually
                show_dirs_in_b = [
                    p for p in b_index.get(tvdb, []) if p.is_dir()]
                # Walk seasons and episodes under this show
                for dirpath, _, filenames in os.walk(entry):
                    for fn in filenames:
                        if fn.startswith("."):
                            continue
                        src_ep = Path(dirpath) / fn
                        # Parse season/episode; skip non-matching files
                        se = parse_season_episode(fn)
                        if not se:
                            skipped += 1
                            continue
                        season_num, ep_num = se
                        b_ep = find_episode_in_dirs(
                            show_dirs_in_b, season_num, ep_num)

                        # Compare resolution when possible
                        better_resolution = False
                        res_a = read_video_resolution(src_ep)
                        res_b = read_video_resolution(
                            b_ep) if b_ep is not None else None
                        if res_a and res_b:
                            pixels_a = res_a[0] * res_a[1]
                            pixels_b = res_b[0] * res_b[1]
                            better_resolution = pixels_a > pixels_b

                        size_a = file_size(src_ep)
                        size_b = file_size(b_ep) if b_ep is not None else 0

                        if better_resolution:
                            dest_base = lib_c / "better-resolution"
                            reason = "better-resolution"
                        else:
                            if size_a > size_b:
                                dest_base = lib_c / "greater-filesize"
                                reason = "greater-filesize"
                            else:
                                dest_base = lib_c / "to-delete"
                                reason = "to-delete"

                        # Pretty formatting helpers (reuse local lambdas)
                        b_name = b_ep.name if b_ep is not None else "<missing>"
                        print(
                            "DECISION:",
                            src_ep.name,
                            "->",
                            dest_base.name,
                            f"reason={reason}",
                            f"A[res={_fmt_res(res_a)}, size={_fmt_size(size_a)}]",
                            f"B(name={b_name})[res={_fmt_res(res_b)}, size={_fmt_size(size_b)}]",
                        )

                        # Preserve show/season structure under destination
                        try:
                            rel_path = src_ep.relative_to(entry)
                        except ValueError:
                            rel_path = Path(src_ep.name)
                        dest = dest_base / entry.name / rel_path
                        move_file(src_ep, dest, overwrite=overwrite,
                                  dry_run=dry_run)
                        moved += 1
                # Do not move the show folder itself
        else:
            skipped += 1

    return moved, skipped
