# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog and follows semantic versioning.

## [3.0.1] - 2025-10-28
### Fixed
- `prepare`: corrected episode renaming pattern to use `s01e01` (season then episode) instead of the previously documented `eEE sSS`; updated README and module docstrings to match.


## [3.0.0] - 2025-10-28
### Added
- Detailed statistics reporting to each utility: utilities now collect and display operation counts (e.g., RENAMED, SKIPPED, ERRORS) per show/category in table or steps format via `log_statistics()`.
- `BaseUtility` class: abstract base class providing shared functionality for all utilities including logging helpers, dry-run/forced options, and statistics tracking via `increment_stat()`.
- `BaseTestLibraryGenerator` class: abstract base class for test data generators with shared download logic and consistent structure.
- Coverage script accessible via `poetry run coverage`: generates HTML, lcov, xml, and json coverage reports in `data/coverage/`.
- New `help` subcommand: `plex-leon help <command>` prints a detailed, human-friendly description and parameter list for a specific utility.
- Each subcommand now exposes detailed usage via the familiar argparse flag (e.g. `plex-leon migrate --help`).
- Dynamic command discovery: utilities are auto-discovered from their classes (no hardcoded command registry). Utility metadata (command name, brief description, parameters, result label and preflight/tool requirements) is provided by the utility classes themselves.
- New interactive `menu` subcommand: `plex-leon menu` launches a prompt-driven interface to pick a discovered utility and supply its arguments interactively.
- CLI default behavior: calling `plex-leon` with no subcommand now launches the interactive `menu` automatically.

### Changed
- **Logging system**: migrated from Python's standard `logging` to `loguru` for enhanced logging capabilities with colored output and structured formatting. All utilities now use consistent log levels (TRACE, DEBUG, INFO, WARNING, ERROR) with emoji prefixes (ℹ️, ⚠️, ❌, 🐛, 🔍).
- **Architecture refactoring**: all utility scripts (`migrate`, `season-renamer`, `episode-renamer`, `prepare`) converted to class-based approach inheriting from `BaseUtility`, sharing common code and reducing duplication.
- **README.md**: comprehensive update with better utility descriptions, improved structure, detailed development guidelines (commit conventions, semantic versioning), devcontainer documentation, and expanded Requirements & Installation instructions.
- **Test structure**: reorganized test directories into `/tests/integration` (for generators) and `/tests/unittests` (for unit tests of helper functions).
- **CLI entrypoint**: the main CLI entrypoint moved from `cli.py` to `main.py`. The new `main.py` no longer uses a hardcoded command registry — commands are discovered dynamically from utility classes at runtime.

### Tests
- Removed old/obsolete tests and reorganized test structure with clear separation between unit and integration tests.
- Moved test library generator scripts to `/tests/integration/generators/` with standardized naming (`*_tlg.py`).
- Added comprehensive unit tests for helper functions in `/tests/unittests/shared/` covering:
  - Episode parsing and normalization
  - TVDB ID extraction and collection
  - Season detection and validation
  - File operations (move, merge, rename)
  - Resolution and filesize formatting
  - Video metadata reading
- Refactored generator scripts using `BaseTestLibraryGenerator` class for consistent structure and shared video download functionality.

## [2.4.0] - 2025-10-10
### Added
- New `prepare` utility: scans a library for TV show folders, validates shows (ensures `{tvdb-...}` suffix and detects duplicate episode files), creates canonical `Season NN` folders, and moves/renames loose episode files to the `Show (Year) - eEE sSS.ext` format. If validation reports ERROR-level issues for a show, processing for that show is skipped.
- Test-data generator (`scripts/generate_prepare_test_library.py`) updated to remove and recreate the `data/library-p` test library and to produce a focused duplicate (Game of Thrones S01E05) for exercising `prepare`'s conflict handling.


## [2.3.1] - 2025-08-25
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
