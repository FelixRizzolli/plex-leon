from __future__ import annotations

import os
import re
from pathlib import Path


_DIGITS_RE = re.compile(r"(\d+)")


def _is_season_dir_name(name: str) -> tuple[bool, int | None]:
    """Return (is_season_like, season_number) based on digits in the name.

    Heuristic:
    - Consider names that contain exactly one sequence of digits as season folders.
    - Extract that number and return it.
    Examples considered season-like: 'season 1', 'Staffel 02', 'Satffel 10', 'S-3'.
    Examples not considered season-like: show folders like 'Title (2011) {tvdb-1234}'.
    """
    digits = _DIGITS_RE.findall(name)
    if len(digits) != 1:
        return (False, None)
    try:
        num = int(digits[0])
        if num < 0:
            return (False, None)
        return (True, num)
    except ValueError:
        return (False, None)


def process_library(
    library: Path,
    dry_run: bool,
) -> tuple[int]:
    """Rename season folders under a single library path.

    Rules:
    - Rename any subfolder whose name contains exactly one series of digits to
      'Season NN' (NN is zero-padded to 2 digits).
    - Works recursively (walks all show folders).
    - Dry-run prints planned renames without touching the filesystem.
    Returns a 1-tuple with the number of renamed folders.
    """
    if not library.is_dir():
        print(f"ERROR: library not found: {library}")
        return (0,)

    renamed = 0

    for dirpath, dirnames, _filenames in os.walk(library):
        # Work on a copy since we might modify names
        for d in list(dirnames):
            old_path = Path(dirpath) / d
            # Only operate on directories
            if not old_path.is_dir():
                continue
            ok, season_num = _is_season_dir_name(d)
            if not ok or season_num is None:
                continue
            new_name = f"Season {season_num:02d}"
            if d == new_name:
                continue
            new_path = Path(dirpath) / new_name
            if new_path.exists() and new_path != old_path:
                print(f"SKIP exists: {new_path}")
                continue
            print(f"RENAME: {old_path} -> {new_path}")
            if not dry_run:
                try:
                    old_path.rename(new_path)
                    # Update dirnames to avoid descending into renamed folder twice
                    try:
                        idx = dirnames.index(d)
                        dirnames[idx] = new_name
                    except ValueError:
                        pass
                except OSError as e:
                    print(f"ERROR: failed to rename {old_path}: {e}")
                    continue
            renamed += 1

    return (renamed,)
