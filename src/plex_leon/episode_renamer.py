from __future__ import annotations

import os
import re
from pathlib import Path


# Matches s01e01 or S01E01-E02 (double episodes). Captures season, ep1, optional ep2
_EP_RE = re.compile(r"(?i)s(\d{1,2})e(\d{1,2})(?:-e(\d{1,2}))?")
_TVDB_RE = re.compile(r"\s*\{tvdb-\d+}\s*", re.IGNORECASE)
_DIGITS_RE = re.compile(r"(\d+)")


def _extract_show_title_from_folder(show_folder_name: str) -> str:
    """Return the show title with year, stripping any trailing " {tvdb-...}".

    Example: "Code Geass (2006) {tvdb-79525}" -> "Code Geass (2006)"
    """
    return _TVDB_RE.sub("", show_folder_name).strip()


def _normalize_episode_tag(name: str) -> str | None:
    """Extract and normalize an episode tag to lowercase sNNeMM[-ePP].

    Returns None if no tag is found.
    """
    m = _EP_RE.search(name)
    if not m:
        return None
    try:
        s = int(m.group(1))
        e1 = int(m.group(2))
        e2 = m.group(3)
        if e2 is not None:
            e2i = int(e2)
            return f"s{s:02d}e{e1:02d}-e{e2i:02d}"
        return f"s{s:02d}e{e1:02d}"
    except ValueError:
        return None


def _two_step_case_rename(old_path: Path, new_path: Path, *, dry_run: bool) -> bool:
    """Perform a two-step rename to handle case-only changes reliably.

    Returns True on success, False otherwise. Prints actions.
    """
    parent = old_path.parent
    swap_name = f".plexleon_swap_{new_path.name}"
    swap_path = parent / swap_name
    i = 1
    while swap_path.exists():
        swap_path = parent / f"{swap_name}.{i}"
        i += 1

    if dry_run:
        print(f"RENAME: {old_path} -> {swap_path}")
        print(f"RENAME: {swap_path} -> {new_path}")
        return True

    try:
        old_path.rename(swap_path)
        # If destination exists now, abort and try to move back
        if new_path.exists():
            print(f"SKIP exists: {new_path}")
            try:
                swap_path.rename(old_path)
            except OSError:
                pass
            return False
        swap_path.rename(new_path)
        return True
    except OSError as e:
        print(f"ERROR: two-step rename failed {old_path} -> {new_path}: {e}")
        # Best effort: try to roll back if swap exists
        try:
            if swap_path.exists():
                swap_path.rename(old_path)
        except OSError:
            pass
        return False


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

    def _is_season_like(name: str) -> bool:
        # Heuristic: one number sequence in the name (e.g., "Season 01", "Staffel 02", "S-3").
        return len(_DIGITS_RE.findall(name)) == 1

    for dirpath, _, filenames in os.walk(library):
        parent = Path(dirpath)
        for fn in filenames:
            if fn.startswith('.'):
                continue
            old_path = parent / fn
            se_tag = _normalize_episode_tag(fn)
            if not se_tag:
                continue

            # Expect structure: <lib>/<Show Folder>/Season XX/<file>
            # Fallback to the immediate parent's parent as show folder when available
            show_dir = parent.parent if _is_season_like(
                parent.name) else parent
            # If library root reached, skip
            if show_dir == library or show_dir.parent == show_dir:
                continue
            show_title = _extract_show_title_from_folder(show_dir.name)

            new_name = f"{show_title} - {se_tag}{old_path.suffix}"
            new_path = old_path.with_name(new_name)

            if old_path.name == new_name:
                continue

            # Case-only change requires two-step rename
            if old_path.name.lower() == new_name.lower():
                ok = _two_step_case_rename(old_path, new_path, dry_run=dry_run)
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
