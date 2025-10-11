from __future__ import annotations

import os
from pathlib import Path
import sys

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
    renamed_per_show: dict[str, int] = {}
    skipped_per_show: dict[str, int] = {}
    error_per_show: dict[str, int] = {}

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
                    renamed_per_show.setdefault(show_title, 0)
                    renamed_per_show[show_title] += 1
                    suffix = " (dry-run)" if dry_run else ""
                    print(
                        f"✅ RENAMED (case-only): {old_path} -> {new_path}{suffix}")
                continue

            # Non-case change: direct rename if destination doesn't exist
            if new_path.exists():
                skipped_per_show.setdefault(show_title, 0)
                skipped_per_show[show_title] += 1
                print(f"⚠️ SKIP exists: {old_path} -> {new_path}")
                continue

            if dry_run:
                renamed += 1
                renamed_per_show.setdefault(show_title, 0)
                renamed_per_show[show_title] += 1
                print(f"🔁 RENAME (dry-run): {old_path} -> {new_path}")
                continue

            try:
                old_path.rename(new_path)
                renamed += 1
                renamed_per_show.setdefault(show_title, 0)
                renamed_per_show[show_title] += 1
                print(f"✅ RENAMED: {old_path} -> {new_path}")
            except OSError as e:
                # write errors to stderr and count per-show
                print(
                    f"❌ ERROR: failed to rename {old_path} -> {new_path}: {e}", file=sys.stderr)
                error_per_show.setdefault(show_title, 0)
                error_per_show[show_title] += 1

    # Print per-show summaries (RENAMED / SKIPPED / ERRORS)
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

    # If there were any file-level errors, print a short stderr summary
    total_errors = sum(error_per_show.values())
    if total_errors:
        print(
            f"❌ ERROR: {total_errors} file(s) failed to rename; see stderr for details.", file=sys.stderr)

    return (renamed,)
