# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog and follows semantic versioning.

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
