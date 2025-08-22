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
    library: Path | None = None,
    dry_run: bool = False,
) -> tuple[int]:
    """Rename season folders under a single library path.

    Rules:
    - Any subfolder whose name contains exactly one series of digits is
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

    for dirpath, dirnames, _ in os.walk(library):
        # Work on a copy so we can safely update dirnames for os.walk
        for d in list(dirnames):
            old_path = Path(dirpath) / d
            if not old_path.is_dir():
                continue
            is_season, num = _is_season_dir_name(d)
            if not is_season or num is None:
                continue
            new_name = f"Season {num:02d}"
            new_path = Path(dirpath) / new_name

            # Already canonical
            if d == new_name:
                continue

            # Case-only path: season 01 -> .plexleon_swap_Season 01 -> Season 01
            if d.lower() == new_name.lower():
                # Find a unique swap path: .plexleon_swap_Season NN[.n]
                swap_path = Path(dirpath) / f".plexleon_swap_{new_name}"
                i = 1
                while swap_path.exists():
                    swap_path = Path(dirpath) / \
                        f".plexleon_swap_{new_name}.{i}"
                    i += 1

                if dry_run:
                    print(f"RENAME: {old_path} -> {swap_path}")
                    if new_path.exists():
                        print(f"MERGE: {swap_path} -> {new_path}")
                    else:
                        print(f"RENAME: {swap_path} -> {new_path}")
                    renamed += 1
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
                        # Merge: move contents from swap into canonical, handle conflicts
                        conflicts_dir = new_path / ".plexleon_conflicts"
                        for item in sorted(swap_path.iterdir()):
                            dest = new_path / item.name
                            if dest.exists():
                                try:
                                    conflicts_dir.mkdir(exist_ok=True)
                                except OSError:
                                    pass
                                base = item.stem
                                suffix = item.suffix
                                n = 1
                                conflict_name = f"{base} (conflict){suffix}"
                                conflict_dest = conflicts_dir / conflict_name
                                while conflict_dest.exists():
                                    conflict_name = f"{base} (conflict {n}){suffix}"
                                    conflict_dest = conflicts_dir / conflict_name
                                    n += 1
                                try:
                                    item.rename(conflict_dest)
                                    print(
                                        f"CONFLICT: moved to {conflict_dest}")
                                except OSError as e:
                                    print(
                                        f"ERROR: conflict move failed {item} -> {conflict_dest}: {e}")
                            else:
                                try:
                                    item.rename(dest)
                                except OSError as e:
                                    print(
                                        f"ERROR: move failed {item} -> {dest}: {e}")
                        # Try to remove empty swap
                        try:
                            next(swap_path.iterdir())
                        except StopIteration:
                            try:
                                swap_path.rmdir()
                            except OSError as e:
                                print(
                                    f"WARN: couldn't remove temp {swap_path}: {e}")

                    # Reflect rename
                    try:
                        idx = dirnames.index(d)
                        dirnames[idx] = new_name
                    except ValueError:
                        pass
                    renamed += 1
                except OSError as e:
                    print(
                        f"ERROR: two-step rename failed {old_path} -> {new_path}: {e}")
                continue

            # Non-case-only path: direct rename when target doesn't exist; else skip.
            if new_path.exists():
                print(f"SKIP exists: {new_path}")
                continue

            if dry_run:
                print(f"RENAME: {old_path} -> {new_path}")
                renamed += 1
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
            except OSError as e:
                print(f"ERROR: failed to rename {old_path} -> {new_path}: {e}")

    return (renamed,)
