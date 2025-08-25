# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog and follows semantic versioning.

# [2.3.1] - 2025-08-25
### Fixed
- `season-renamer` no longer renames top-level show folders in the library, even if their names contain digits (e.g., 'Game of Thrones 2011'). Only subfolders (season folders) are considered for renaming.
- Test data generator now always creates a show folder without a TVDB id or year (e.g., 'Game of Thrones 2011') with a season subfolder, ensuring this edge case is always present for testing.

## [2.3.0] - 2025-08-23
### Added
- CLI now reports wall-clock duration for each command:
  - `migrate`: `Done. Eligible files/folders moved: X; skipped: Y. Took Z.ZZs.`
  - `season-renamer`: `Done. Season folders renamed: N. Took Z.ZZs.`
  - `episode-renamer`: `Done. Episode files renamed: N. Took Z.ZZs.`

### Changed
- Migrate performance improvements and tuning:
  - Optional concurrency for metadata reads via `--threads <N>` (I/O bound).
  - `--no-resolution` to skip resolution comparisons when you want size-only heuristics.
  - Avoid resolution probing when the counterpart in library-b is missing (saves ffprobe/mediainfo calls).
- README updated to document timing output and new migrate flags.

## [2.2.0] - 2025-08-23
### Added
- New `episode-renamer` utility that renames episode files to `<Show (Year)> - sNNeMM[ -ePP].ext`.
  - Show title/year is taken from the show folder; TVDB suffix is stripped.
  - Episode ids parsed from filenames (supports lowercase/uppercase and double episodes) and normalized to lowercase.
  - Case-only renames are done via a safe two-step swap to avoid filesystem issues.
- CLI subcommand `episode-renamer` with `--lib` and `--dry-run`.

### Changed
- Refactored shared logic into `utils.py` (episode parsing/normalization, season detection, two-step renames, iterators, formatting helpers, directory merge utilities).
- `migrate` and `season-renamer` now use the shared helpers, reducing duplication and improving readability.
- README updated with episode-renamer docs and clarified CLI compatibility notes.

### Tests
- Added tests for episode renamer and season renamer.
- Expanded tests for migrate and CLI.
- Added comprehensive tests for new utilities and regex behavior.

## [2.1.0] - 2025-08-22
### Added
- `season-renamer` now uses a robust two-step swap logic for case-only renames (e.g., 'season 01' → '.plexleon_swap_Season 01' → 'Season 01').
- If a canonical 'Season NN' folder already exists, contents are merged non-destructively; any conflicts are moved to a '.plexleon_conflicts' subfolder. No folders or files are deleted or overwritten by default.
- Dry-run output now clearly shows all planned swap/merge operations.

## [2.0.0] - 2025-08-17

### Added
- New utility: `season-renamer` for renaming season folders in a library to the canonical 'Season NN' form. Handles typos (e.g., 'Satffel'), different languages (e.g., 'Staffel'), and any folder with a single number. Supports dry-run and works recursively. Numbers >= 100 are supported.

### Changed
- CLI is now subcommand-based. You must use `poetry run plex-leon migrate ...` instead of `poetry run plex-leon ...`.
- Improved regex for parsing season and episode numbers in the migrate script, now supports numbers >= 100.

### Breaking
- The CLI no longer defaults to migration. You must specify a subcommand (e.g., `migrate`, `season-renamer`).

## [1.3.0] - 2025-08-17

### Added
- TV show episodes are now compared and moved individually: for each episode in a show present in both libraries, the tool matches by season and episode number (e.g., s01e01) and applies the same resolution and size logic as for movies. Each episode is categorized under `better-resolution/`, `greater-filesize/`, or `to-delete/` in library-c, preserving the show/season/episode folder structure. The show folder itself is not moved, only its episodes.

### Changed
- README updated to clarify the per-episode comparison and categorization logic for TV shows.

## [1.2.0] - 2025-08-10

### Added
- Support for a bucketed reference library-b layout under A–Z and a single non-letter bucket `0-9`.
- Recursive scanning of library-b so TVDB IDs and matches are discovered inside bucket folders (not just top-level).
- Sample data generator updated with titles starting with special characters (e.g., `[REC] …`) that land in the `0-9` bucket.

### Changed
- README updated to document the bucketed layout and recursive scanning behavior for library-b.
- Backward compatible: a flat, top-level-only library-b still works.

## [1.1.0] - 2025-08-09

### Added
- Preflight check to ensure required external tools are installed on PATH. The CLI now exits with code 2 and a clear message when `ffprobe` (FFmpeg) or `mediainfo` are missing.
- Movie categorization when moving from library-a to library-c based on comparison with the matching entry in library-b:
  - `better-resolution/` when the source video has higher pixel count (width×height).
  - `greater-filesize/` when resolution is not higher but the source file is larger.
  - `to-delete/` when neither is true.
- Resolution probing using `ffprobe` first, then `mediainfo` as a fallback; if resolution is unknown on both sides, the tool falls back to file-size comparison only.
- Detailed decision logs for eligible items (resolution and size of A vs B), plus a final summary of moved/skipped counts.

### Changed
- README updated to document the new behavior, requirements, and exit codes.

## [1.0.0] - 2025-08-08

Initial release.

### Features
- CLI `plex-leon` that moves items from library-a to library-c when their TVDB ID exists in library-b.
- TVDB ID parsing from names using case-insensitive pattern `{tvdb-<digits>}` (e.g., `{tvdb-155}`).
- Only considers top-level children of each library; ignores hidden entries.
- Supports both files (movies) and folders (TV shows); logs each move/skip and prints a final summary.
- Options:
  - `--lib-a` path to source library (default `./data/library-a`)
  - `--lib-b` path to reference library (default `./data/library-b`)
  - `--lib-c` path to destination library (default `./data/library-c`)
  - `--overwrite` to replace existing files/folders in library-c
  - `--dry-run` to preview actions without modifying the filesystem
