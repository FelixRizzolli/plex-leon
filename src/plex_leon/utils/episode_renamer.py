from __future__ import annotations

import os
from pathlib import Path

from plex_leon.shared import (
    strip_tvdb_suffix,
    normalize_episode_tag,
    is_season_like_dirname,
    two_step_case_rename,
)
from plex_leon.utils.base_utility import BaseUtility


def process_library(library: Path | None = None, dry_run: bool = False) -> tuple[int]:
    """Compatibility shim that delegates to EpisodeRenamerUtility.process so
    callers (including the CLI) can continue to call `process_library(...)`.
    """
    util = EpisodeRenamerUtility(dry_run=dry_run)
    return util.process(library)


class EpisodeRenamerUtility(BaseUtility):
    """Class wrapper for episode renaming that exposes `process()` using the
    BaseUtility logging helpers.

    Example:
        EpisodeRenamerUtility(dry_run=True).run(library)
    """

    def process(self, library: Path | None = None) -> tuple[int]:
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
                    ok = two_step_case_rename(
                        old_path, new_path, dry_run=self.dry_run)
                    if ok:
                        renamed += 1
                        renamed_per_show.setdefault(show_title, 0)
                        renamed_per_show[show_title] += 1
                        suffix = " (dry-run)" if self.dry_run else ""
                        self.log_info(
                            f"✅ RENAMED (case-only): {old_path} -> {new_path}{suffix}")
                    continue

                # Non-case change: direct rename if destination doesn't exist
                if new_path.exists():
                    skipped_per_show.setdefault(show_title, 0)
                    skipped_per_show[show_title] += 1
                    self.log_warning(f"SKIP exists: {old_path} -> {new_path}")
                    continue

                if self.dry_run:
                    renamed += 1
                    renamed_per_show.setdefault(show_title, 0)
                    renamed_per_show[show_title] += 1
                    self.log_info(
                        f"RENAME (dry-run): {old_path} -> {new_path}")
                    continue

                try:
                    old_path.rename(new_path)
                    renamed += 1
                    renamed_per_show.setdefault(show_title, 0)
                    renamed_per_show[show_title] += 1
                    self.log_info(f"✅ RENAMED: {old_path} -> {new_path}")
                except OSError as e:
                    # log and count per-show
                    self.log_error(
                        f"failed to rename {old_path} -> {new_path}: {e}")
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

            self.log_info(f"📺 {show} {suffix}")
            self.log_info(f"    — RENAMED: {r}")
            self.log_info(f"    - SKIPPED: {s}")
            self.log_info(f"    — ERRORS: {e}")

        total_errors = sum(error_per_show.values())
        if total_errors:
            self.log_error(
                f"{total_errors} file(s) failed to rename; see above for details.")

        return (renamed,)
