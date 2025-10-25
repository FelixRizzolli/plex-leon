import importlib
import re
from typing import Dict

# Additional regex/utilities for episode and folder handling
EPISODE_TAG_REGEX = re.compile(r"(?i)s(\d{1,2})e(\d{1,2})(?:-e(\d{1,2}))?")
TVDB_SUFFIX_REGEX = re.compile(r"\s*\{tvdb-\d+}\s*", re.IGNORECASE)
_SEASON_DIGITS_RE = re.compile(r"(\d+)")

# Compiled regex used to extract TVDB ids like "{tvdb-12345}" from filenames
TVDB_REGEX = re.compile(r"\{tvdb-(\d+)\}", re.IGNORECASE)

# Re-export commonly used helpers from individual modules so callers can
# import them directly from `plex_leon.shared` (e.g. ``from plex_leon.shared
# import parse_episode_tag``).
# Implementation note: to avoid circular import problems we perform lazy
# imports — symbols are loaded from their implementation modules on first
# attribute access via `__getattr__`.

# Map exported symbol name -> implementation module (relative to this package)
_EXPORTS: Dict[str, str] = {
    "assert_required_tools_installed": "assert_required_tools_installed",
    "collect_tvdb_ids": "collect_tvdb_ids",
    "extract_tvdb_id": "extract_tvdb_id",
    "file_size": "file_size",
    "find_episode_in_dirs": "find_episode_in_dirs",
    "format_bytes": "format_bytes",
    "format_resolution": "format_resolution",
    "get_season_number_from_dirname": "get_season_number_from_dirname",
    "is_season_like_dirname": "is_season_like_dirname",
    "iter_nonhidden_entries": "iter_nonhidden_entries",
    "merge_directory_contents": "merge_directory_contents",
    "move_file": "move_file",
    "normalize_episode_tag": "normalize_episode_tag",
    "parse_episode_tag": "parse_episode_tag",
    "parse_season_episode": "parse_season_episode",
    "read_video_resolution": "read_video_resolution",
    "remove_dir_if_empty": "remove_dir_if_empty",
    "strip_tvdb_suffix": "strip_tvdb_suffix",
    "two_step_case_rename": "two_step_case_rename",
    "unique_swap_path": "unique_swap_path",
}


def __getattr__(name: str):
    """Lazily import and return exported symbols from submodules.

    This keeps import-time costs low and avoids many circular import
    problems when submodules import package-level constants from here.
    """
    # Return constants defined in this module immediately
    if name in globals():
        return globals()[name]

    mod_name = _EXPORTS.get(name)
    if mod_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    mod = importlib.import_module(f"{__name__}.{mod_name}")
    value = getattr(mod, name)
    # Cache on module for subsequent access
    globals()[name] = value
    return value


def __dir__():
    return sorted(list(globals().keys()) + list(_EXPORTS.keys()))


__all__ = [
    "EPISODE_TAG_REGEX",
    "TVDB_SUFFIX_REGEX",
    "TVDB_REGEX",
] + sorted(_EXPORTS.keys())
