from __future__ import annotations

"""Library preparation utilities.

This module provides a `process` function that scans a *root* directory for
TV show folders and normalises episode placement & naming:

1. Detect show folders whose name matches the convention:
	  TV Show Name (YYYY) {tvdb-12345}
   (The year is a 4-digit number in parentheses; the TVDB id is in curly braces.)
2. Inside each show folder, locate loose episode media files (i.e. files that
   are direct children of the show directory, not already inside a canonical
   `Season NN` directory.)
3. Derive season & episode numbers from the filename. Supported patterns:
	  - Standard tags: S01E02, s1e2, S01E02-E03 (double episodes -> first used)
	  - German style:  "Episode 12 Staffel 2"  (episode first)
	  - German style:  "Staffel 2 Episode 12"  (season first)
   If none match, the file is skipped silently.
4. Create the target season directory named `Season NN` (NN zero-padded) if it
   does not already exist.
5. Move & rename the file to:
	  <Show Name (YYYY)> - eEE sSS.ext   (per spec: 'e01s01')
   NOTE: The user explicitly requested the format `e01s01` (episode then
   season) even though the more common convention is `s01e01`.
6. Case-only changes are applied via a two-step rename using the existing
   `two_step_case_rename` helper.

Returns a 1-tuple with the count of episode files moved/renamed.

Inspired by logic in `episode_renamer` & `season_renamer` modules.

Validation
----------
Before making any filesystem changes for a show, `process` runs a validation
step that checks each show folder for two common problems:

- Missing TVDB id in the folder name (the folder name must contain
    "{tvdb-<digits>}"), and
- Duplicate episode files for the same season/episode (e.g. two files that
    both parse as S01E05).

Any validation messages are printed. If validation reports any ERROR-level
problems for a show, the renaming and season-folder creation are skipped for
that show; WARN-level issues (unparseable filenames) are reported but are not
fatal by default.
"""

import os
import re
from pathlib import Path

from .utils import (
    strip_tvdb_suffix,
    parse_episode_tag,
    two_step_case_rename,
)

SHOW_DIR_REGEX = re.compile(r"^.+ \(\d{4}\) \{tvdb-\d+}\Z")

# German style patterns (case-insensitive):
#   Episode 12 Staffel 2
#   Staffel 2 Episode 12
GERMAN_EP_FIRST = re.compile(r"(?i)Episode\s+(\d+)\D+Staffel\s+(\d+)")
GERMAN_SEASON_FIRST = re.compile(r"(?i)Staffel\s+(\d+)\D+Episode\s+(\d+)")

# Common media file extensions we care about. (Lowercase, without dot.)
MEDIA_EXTS = {
    "mp4",
    "mkv",
    "avi",
    "mov",
    "m4v",
    "flv",
    "wmv",
    "mpg",
    "mpeg",
}


def _is_show_dir(path: Path) -> bool:
    return path.is_dir() and SHOW_DIR_REGEX.match(path.name) is not None


def _iter_show_dirs(root: Path):
    """Yield show directories beneath root.

    A show directory can appear directly under root or nested one (or more)
    levels deep underneath grouping folders (like 'anime sub', 'serien', etc.).
    We therefore walk the tree and emit any directory whose *name* matches the
    show pattern. We do not recurse *into* detected show folders beyond their
    immediate children; only their top level files are considered, allowing
    existing `Season NN` directories to remain untouched.
    """
    for dirpath, dirnames, _ in os.walk(root):
        parent = Path(dirpath)
        # Work on a copy to be able to prune recursion into show dirs.
        for d in list(dirnames):
            p = parent / d
            if _is_show_dir(p):
                yield p
                # Prevent os.walk from descending further inside; we handle
                # that separately.
                try:
                    dirnames.remove(d)
                except ValueError:
                    pass


def _parse_season_episode_from_name(name: str) -> tuple[int, int] | None:
    """Extract (season, episode) from filename.

    Order in target filename is episode then season per spec, but we return
    (season, episode) for internal consistency with other helpers.
    """
    # 1. Standard SxxExx pattern via existing helper
    tag = parse_episode_tag(name)
    if tag:
        season, ep1, _ = tag
        return (season, ep1)

    # 2. German 'Episode N Staffel M'
    m = GERMAN_EP_FIRST.search(name)
    if m:
        try:
            ep = int(m.group(1))
            season = int(m.group(2))
            return (season, ep)
        except ValueError:
            return None

    # 3. German 'Staffel M Episode N'
    m = GERMAN_SEASON_FIRST.search(name)
    if m:
        try:
            season = int(m.group(1))
            ep = int(m.group(2))
            return (season, ep)
        except ValueError:
            return None

    return None


def _validate_show(show_dir: Path) -> tuple[bool, list[str]]:
    """Validate a show directory.

    Checks performed:
    - presence of a TVDB id in the folder name ("{tvdb-<digits>}")
    - duplicate episode detections among loose media files (same season/episode)

    Returns (is_valid, messages). If is_valid is False the caller should skip
    performing any renames or creating season folders for this show.
    """
    msgs: list[str] = []
    name = show_dir.name
    # TVDB id check
    if __import__("re").search(r"\{tvdb-\d+\}", name) is None:
        msgs.append(f"ERROR: missing tvdb id in show folder name: '{name}'")

    # Collect loose media files and map parsed (season, ep) -> files
    counts: dict[tuple[int, int], list[Path]] = {}
    for entry in sorted(show_dir.iterdir()):
        if entry.is_dir() or entry.name.startswith('.'):
            continue
        ext = entry.suffix.lower().lstrip('.')
        if ext not in MEDIA_EXTS:
            continue
        parsed = _parse_season_episode_from_name(entry.name)
        if not parsed:
            # unparseable files are not considered fatal for validation here,
            # but we log a warning so the user can inspect them.
            msgs.append(
                f"WARN: could not parse season/episode from filename: {entry.name}")
            continue
        season, ep = parsed
        counts.setdefault((season, ep), []).append(entry)

    # Detect duplicates: same season/episode mapped by multiple files
    for (season, ep), files in counts.items():
        if len(files) > 1:
            file_list = ", ".join(str(p.name) for p in files)
            msgs.append(
                f"ERROR: duplicate episode detected S{season:02d}E{ep:02d}: {file_list}")

    return (len([m for m in msgs if m.startswith("ERROR:")]) == 0, msgs)


def process(root: Path | str | None = None, dry_run: bool = False) -> tuple[int]:
    """Process a root folder and normalise loose episode files.

    Parameters
    ----------
    root : Path | str
            Root directory to scan.
    dry_run : bool
            If True, print actions without modifying the filesystem.

    Returns
    -------
    tuple[int]
            A 1-tuple containing the number of episode files moved/renamed.
    """
    if root is None:
        root = Path("data/library-p")
    if not isinstance(root, Path):
        root = Path(root)

    processed = 0

    for show_dir in _iter_show_dirs(root):
        show_title = strip_tvdb_suffix(show_dir.name)  # 'Name (YYYY)'

        # Validate show before making any changes
        valid, messages = _validate_show(show_dir)
        for m in messages:
            print(m)
        if not valid:
            print(f"SKIP show due to validation errors: {show_dir}")
            continue

        # Collect candidate files directly in the show directory (ignore existing Season folders)
        for entry in sorted(show_dir.iterdir()):
            if entry.is_dir():
                # Skip directories (existing Season NN / other folders)
                continue
            if entry.name.startswith('.'):
                continue
            ext = entry.suffix.lower().lstrip('.')
            if ext not in MEDIA_EXTS:
                continue

            parsed = _parse_season_episode_from_name(entry.name)
            if not parsed:
                continue
            season, episode = parsed
            season_dir = show_dir / f"Season {season:02d}"
            target_name = f"{show_title} - e{episode:02d}s{season:02d}{entry.suffix.lower()}"
            target_path = season_dir / target_name

            # Skip if already correct location/name
            if entry == target_path:
                continue

            # Ensure season directory
            if dry_run and not season_dir.exists():
                print(f"MKDIR: {season_dir}")
            elif not dry_run:
                season_dir.mkdir(parents=True, exist_ok=True)

            # If only case differs and same parent, use two-step rename.
            if entry.parent == target_path.parent and entry.name.lower() == target_path.name.lower():
                ok = two_step_case_rename(entry, target_path, dry_run=dry_run)
                if ok:
                    processed += 1
                continue

            # If destination exists (different file), skip.
            if target_path.exists() and target_path != entry:
                print(f"SKIP exists: {target_path}")
                continue

            if dry_run:
                print(f"MOVE+RENAME: {entry} -> {target_path}")
                processed += 1
                continue

            try:
                # If moving across directories we can just rename with new path
                entry.rename(target_path)
                processed += 1
            except OSError as e:
                print(f"ERROR: failed to move {entry} -> {target_path}: {e}")

    return (processed,)


__all__ = ["process"]


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import sys

    ap = argparse.ArgumentParser(
        description="Prepare a media library by organising loose TV episode files into season folders.")
    ap.add_argument("root", type=Path, help="Root directory to scan")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show planned operations without modifying the filesystem")
    ns = ap.parse_args()
    count, = process(ns.root, dry_run=ns.dry_run)
    print(f"Done. Episodes processed: {count}.")
    sys.exit(0)
