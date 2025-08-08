# plex-leon

A tiny CLI that moves media from one library to another based on TVDB IDs.

Given three folders:
- library-a: source library (files/folders to consider)
- library-b: reference library (whose TVDB IDs authorize moves)
- library-c: destination library

The tool will move any entry in library-a whose name contains a TVDB tag like `{tvdb-12345}` when the same ID also appears in any immediate child name of library-b.

## How it works

- TVDB IDs are extracted with a case-insensitive pattern: `{tvdb-<digits>}`. Examples:
	- `John Wick (2014) {tvdb-155}.mp4` → `155`
	- `Game of Thrones (2011) {TVDB-121361}` → `121361`
- Only the top-level children of each library are inspected (both files and folders). Hidden entries (starting with `.`) are ignored.
- If an item in library-a has a TVDB ID that also exists among library-b's children, it is considered eligible and moved to library-c.
- Moves print what would or did happen and end with a summary line: `Done. Eligible files/folders moved: X; skipped: Y.`

## Requirements

- Python 3.13+

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

## Exit code and logs

- Returns `0` on normal completion.
- Prints the number of discovered IDs in library-b, each move/skip decision, and a final summary.

## Development

Run tests (optional):

```bash
poetry run pytest -q
```

Key modules:
- `plex_leon/core.py` — extraction, scanning, and move logic
- `plex_leon/cli.py` — argument parsing and wiring to the core
