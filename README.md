# plex-leon

A tiny CLI that moves media from one library to another based on TVDB IDs.

Given three folders:
- library-a: source library (files/folders to consider)
- library-b: reference library (whose TVDB IDs authorize moves). This library can be bucketed under A–Z and a single non-letter bucket `0-9`.
- library-c: destination library

The tool will move any entry in library-a whose name contains a TVDB tag like `{tvdb-12345}` when the same ID also appears anywhere under library-b (recursively scanned, including within A–Z/`0-9` buckets).

## How it works

- TVDB IDs are extracted with a case-insensitive pattern: `{tvdb-<digits>}`. Examples:
	- `John Wick (2014) {tvdb-155}.mp4` → `155`
	- `Game of Thrones (2011) {TVDB-121361}` → `121361`
- Hidden entries (starting with `.`) are ignored.
- Library-b is scanned recursively to support a production-like, bucketed layout under A–Z and `0-9` (non-letter starters). Examples:
	- `library-b/A/Avatar (2009) {tvdb-19995}.mp4`
	- `library-b/0-9/[REC] (2007) {tvdb-12345}.mp4`
	- `library-b/0-9/2001 A Space Odyssey (1968) {tvdb-...}.mp4`
- Library-a is still scanned at the top level only (both files and folders).
- If an item in library-a has a TVDB ID that also exists anywhere under library-b, it’s considered eligible and moved to library-c.
- For movies (files), the destination inside library-c depends on a comparison with the matching item in library-b:
	- `better-resolution/` when the source has a higher pixel count (width×height)
	- `greater-filesize/` when resolution isn't higher but the source file is larger
	- `to-delete/` when neither is true (i.e., the library-b item is as good or better)
	Resolution is read via ffprobe (FFmpeg) first, then mediainfo. If both resolutions are unknown, the tool falls back to file-size comparison only.
- For TV shows (folders), the tool preserves the original behavior and moves the folder directly under library-c (no categorization subfolder).
- Moves print what would or did happen and end with a summary line: `Done. Eligible files/folders moved: X; skipped: Y.`

## Requirements

- Python 3.13+
- External tools on PATH (validated at startup): ffprobe (from FFmpeg) and mediainfo

On Debian/Ubuntu you can install them with:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg mediainfo
```

If you use Poetry, the project is already configured. Otherwise you can install it as a regular package in editable mode.

## Usage

The CLI entry point is `plex-leon`.

Options:
- `--lib-a PATH`  Source library (default: `./data/library-a`)
- `--lib-b PATH`  Reference library (default: `./data/library-b`)
- `--lib-c PATH`  Destination library (default: `./data/library-c`)
- `--overwrite`   Replace existing files/folders in library-c
- `--dry-run`     Show planned moves without changing the filesystem

### Examples (optional commands)

```bash
# Optional: run with defaults against the sample data folder
poetry run plex-leon --dry-run

# Optional: specify custom paths and actually move files
poetry run plex-leon --lib-a /path/a --lib-b /path/b --lib-c /path/c --overwrite
```

## Sample data

This repository includes a `data/` directory with illustrative entries you can use for quick trials with `--dry-run`.
Inside `data/library-c/` you'll see the categorization folders used for movies:
- `better-resolution/`
- `greater-filesize/`
- `to-delete/`

Note: `data/library-b/` uses the bucketed layout described above (A–Z and a single `0-9` bucket for items that don’t start with a letter).

## Exit code and logs

- Returns `0` on normal completion.
- Returns `2` if required external tools are missing (preflight check fails).
- Prints the number of discovered IDs in library-b, detailed DECISION lines for eligible items (including resolution and size of A vs B), and a final summary.

## Development

Run tests (optional):

```bash
poetry run pytest -q
```

Key modules:
- `plex_leon/core.py` — extraction, scanning, and move logic
- `plex_leon/cli.py` — argument parsing and wiring to the core

### Build standalone executables (CI)

A GitHub Actions workflow builds single-file executables for Linux, macOS, and Windows using PyInstaller. It runs on tag pushes matching `v*` and on manual dispatch.

- Workflow: `.github/workflows/build-binaries.yml`
- Artifacts uploaded per-OS as `plex-leon-<OS>` (or `.exe` on Windows)

To trigger manually, use the Actions tab → build-binaries → Run workflow.
