from __future__ import annotations

import os
from pathlib import Path

from ..shared import (
    get_season_number_from_dirname,
    unique_swap_path,
    merge_directory_contents,
    remove_dir_if_empty,
)


def process_library(
    library: Path | None = None,
    dry_run: bool = False,
) -> tuple[int]:
    """Rename season folders under a single library path.

    Rules:
    - Any subfolder (not the top-level show folders) whose name contains exactly one series of digits is
      considered a season folder, renamed to 'Season NN' (NN zero-padded).
    - For case-only renames (e.g., 'season 01' -> 'Season 01') always perform a
      two-step rename via '.plexleon_swap_Season NN' then to 'Season NN'. If a
      canonical 'Season NN' already exists, merge contents from the swap folder
      into it without overwriting; conflicts are moved into
      'Season NN/.plexleon_conflicts'.
    - Dry-run prints planned operations and makes no changes.
    Returns a 1-tuple with the number of season folders processed (renamed/merged).
    """
    if library is None:
        library = Path("data/library-s")
    if not isinstance(library, Path):
        library = Path(library)

    renamed = 0
    renamed_per_show: dict[str, int] = {}
    skipped_per_show: dict[str, int] = {}
    error_per_show: dict[str, int] = {}

    for dirpath, dirnames, _ in os.walk(library):
        # Work on a copy so we can safely update dirnames for os.walk
        for d in list(dirnames):
            old_path = Path(dirpath) / d
            if not old_path.is_dir():
                continue
            # Skip top-level show folders directly under the library root
            # (only their subfolders should be treated as season folders)
            if Path(dirpath).resolve() == Path(library).resolve():
                continue
            num = get_season_number_from_dirname(d)
            if num is None:
                continue
            new_name = f"Season {num:02d}"
            new_path = Path(dirpath) / new_name

            # Already canonical
            if d == new_name:
                continue

            # Case-only path: season 01 -> .plexleon_swap_Season 01 -> Season 01
            if d.lower() == new_name.lower():
                # Find a unique swap path
                swap_path = unique_swap_path(Path(dirpath), new_name)

                if dry_run:
                    print(f"🔁 RENAME: {old_path} -> {swap_path}")
                    if new_path.exists():
                        print(f"🔀 MERGE: {swap_path} -> {new_path}")
                    else:
                        print(f"🔁 RENAME: {swap_path} -> {new_path}")
                    renamed += 1
                    show = Path(dirpath).name
                    renamed_per_show.setdefault(show, 0)
                    renamed_per_show[show] += 1
                    # Reflect rename so os.walk doesn't traverse old name
                    try:
                        idx = dirnames.index(d)
                        dirnames[idx] = new_name
                    except ValueError:
                        pass
                    continue

                try:
                    # First hop: to swap
                    old_path.rename(swap_path)

                    # Second hop or merge
                    if not new_path.exists():
                        swap_path.rename(new_path)
                    else:
                        merge_directory_contents(swap_path, new_path)
                        # Try to remove empty swap
                        if not remove_dir_if_empty(swap_path):
                            # Best-effort warn, original code warned with details
                            pass

                    # Reflect rename
                    try:
                        idx = dirnames.index(d)
                        dirnames[idx] = new_name
                    except ValueError:
                        pass
                    renamed += 1
                    show = Path(dirpath).name
                    renamed_per_show.setdefault(show, 0)
                    renamed_per_show[show] += 1
                except OSError as e:
                    print(
                        f"❌ ERROR: two-step rename failed {old_path} -> {new_path}: {e}")
                    show = Path(dirpath).name
                    error_per_show.setdefault(show, 0)
                    error_per_show[show] += 1
                continue

            # Non-case-only path: direct rename when target doesn't exist; else skip.
            if new_path.exists():
                print(f"⚠️ SKIP exists: {new_path}")
                show = Path(dirpath).name
                skipped_per_show.setdefault(show, 0)
                skipped_per_show[show] += 1
                continue

            if dry_run:
                print(f"🔁 RENAME: {old_path} -> {new_path}")
                renamed += 1
                show = Path(dirpath).name
                renamed_per_show.setdefault(show, 0)
                renamed_per_show[show] += 1
                try:
                    idx = dirnames.index(d)
                    dirnames[idx] = new_name
                except ValueError:
                    pass
                continue

            try:
                old_path.rename(new_path)
                try:
                    idx = dirnames.index(d)
                    dirnames[idx] = new_name
                except ValueError:
                    pass
                renamed += 1
                show = Path(dirpath).name
                renamed_per_show.setdefault(show, 0)
                renamed_per_show[show] += 1
            except OSError as e:
                print(
                    f"❌ ERROR: failed to rename {old_path} -> {new_path}: {e}")
                show = Path(dirpath).name
                error_per_show.setdefault(show, 0)
                error_per_show[show] += 1

    # Print per-show summaries
    shows = set()
    shows.update(renamed_per_show.keys())
    shows.update(skipped_per_show.keys())
    shows.update(error_per_show.keys())
    for show in sorted(shows, key=lambda x: x.lower()):
        r = renamed_per_show.get(show, 0)
        s = skipped_per_show.get(show, 0)
        e = error_per_show.get(show, 0)

        suffix = "✅"
        if e > 0:
            suffix = "❌"
        elif s > 0:
            suffix = "⚠️"

        print(f"📺 {show}")
        print(f"    — RENAMED: {r}")
        print(f"    - SKIPPED: {s}")
        print(f"    — ERRORS: {e}")

    return (renamed,)
