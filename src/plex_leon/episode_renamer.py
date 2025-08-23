from __future__ import annotations

import os
from pathlib import Path

from .utils import (
    strip_tvdb_suffix,
    normalize_episode_tag,
    is_season_like_dirname,
    two_step_case_rename,
)


def process_library(library: Path | None = None, dry_run: bool = False) -> tuple[int]:
    """Rename episode files to '<Show Title (Year)> - sNNeMM[ -ePP].ext'.

    Rules:
    - Determine the show title (with year) from the show folder name, stripping any ' {tvdb-...}'.
    - Extract the episode id from the filename (supports single or double episodes), normalize to lowercase.
    - Remove any episode title suffixes from filenames.
    - Perform two-step rename for case-only changes via a hidden swap file.
    - Dry-run prints planned operations without changing the filesystem.

    Returns a 1-tuple with the number of episode files renamed.
    """
    if library is None:
        library = Path("data/library-e")
    if not isinstance(library, Path):
        library = Path(library)

    renamed = 0

    for dirpath, _, filenames in os.walk(library):
        parent = Path(dirpath)
        for fn in filenames:
            if fn.startswith('.'):
                continue
            old_path = parent / fn
            se_tag = normalize_episode_tag(fn)
            if not se_tag:
                continue

            # Expect structure: <lib>/<Show Folder>/Season XX/<file>
            # Fallback to the immediate parent's parent as show folder when available
            show_dir = parent.parent if is_season_like_dirname(
                parent.name) else parent
            # If library root reached, skip
            if show_dir == library or show_dir.parent == show_dir:
                continue
            show_title = strip_tvdb_suffix(show_dir.name)

            new_name = f"{show_title} - {se_tag}{old_path.suffix}"
            new_path = old_path.with_name(new_name)

            if old_path.name == new_name:
                continue

            # Case-only change requires two-step rename
            if old_path.name.lower() == new_name.lower():
                ok = two_step_case_rename(old_path, new_path, dry_run=dry_run)
                if ok:
                    renamed += 1
                continue

            # Non-case change: direct rename if destination doesn't exist
            if new_path.exists():
                print(f"SKIP exists: {new_path}")
                continue

            if dry_run:
                print(f"RENAME: {old_path} -> {new_path}")
                renamed += 1
                continue

            try:
                old_path.rename(new_path)
                renamed += 1
            except OSError as e:
                print(f"ERROR: failed to rename {old_path} -> {new_path}: {e}")

    return (renamed,)
