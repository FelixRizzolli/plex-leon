# plex-leon

A tiny CLI to manage media libraries: migrate by TVDB IDs, rename seasons and episodes.

Given three folders:
- library-a: source library (files/folders to consider)
- library-b: reference library (whose TVDB IDs authorize moves). This library can be bucketed under A–Z and a single non-letter bucket `0-9`.
- library-c: destination library

The tool will move any entry in library-a whose name contains a TVDB tag like `{tvdb-12345}` when the same ID also appears anywhere under library-b (recursively scanned, including within A–Z/`0-9` buckets).

## How it works (migrate)

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
- For TV shows (folders), the tool compares episodes individually by matching season and episode numbers (e.g., s01e01) between library-a and library-b. Each episode is moved to the appropriate categorization folder in library-c (`better-resolution/`, `greater-filesize/`, or `to-delete/`) based on the same resolution and size logic as for movies. The show/season/episode folder structure is preserved under the categorization folder. The show folder itself is not moved, only its episodes.
  The tool will move any entry in library-a whose name contains a TVDB tag like `{tvdb-12345}` when the same ID also appears anywhere under library-b (recursively scanned, including within A–Z/`0-9` buckets).
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

The CLI entry point is `plex-leon` with subcommands. Current commands:

- `migrate` — move items from library-a to library-c when the TVDB ID exists in library-b
	- Options:
		- `--lib-a PATH`  Source library (default: `./data/library-a`)
		- `--lib-b PATH`  Reference library (default: `./data/library-b`)
		- `--lib-c PATH`  Destination library (default: `./data/library-c`)
		- `--overwrite`   Replace existing files/folders in library-c
		- `--dry-run`     Show planned moves without changing the filesystem
- `season-renamer` — renames season folders in a library to the canonical 'Season NN' form (e.g., 'season 01', 'Staffel 01', 'Satffel 01', or any folder with a single number will be renamed to 'Season NN'). Supports --dry-run and works recursively. Typos and numbers >= 100 are supported.
	- For case-only renames (e.g., 'season 01' → 'Season 01'), a two-step swap is performed: first, the folder is renamed to `.plexleon_swap_Season NN`, then to `Season NN`. If a canonical `Season NN` already exists, contents are merged non-destructively (conflicts are moved to a `.plexleon_conflicts` subfolder). No folders or files are deleted or overwritten by default.
- `episode-renamer` — renames episode files to `<Show (Year)> - sNNeMM[ -ePP].ext`.
	- The show title and year are taken from the parent show folder (e.g., `Code Geass (2006) {tvdb-79525}` → `Code Geass (2006)`).
	- The episode id is parsed from the original filename (supports `s01e01`, `S01E01`, and double-episodes like `S01E01-E02`) and normalized to lowercase.
	- Any additional episode title text in the filename is removed.
	- Case-only changes (e.g., `S01E01` → `s01e01`) are performed via a safe two-step rename using a hidden swap file to avoid filesystem issues.
- `episode-check` — placeholder

### Examples (optional commands)

```bash
# Optional: run migrate with defaults against the sample data folder
poetry run plex-leon migrate --dry-run

# Optional: specify custom paths and actually move files
poetry run plex-leon migrate --lib-a /path/a --lib-b /path/b --lib-c /path/c --overwrite

# Optional: rename all season folders in a library (dry run)
poetry run plex-leon season-renamer --lib ./data/library-b --dry-run

# Actually rename all season folders in a library
poetry run plex-leon season-renamer --lib ./data/library-b

# Optional: rename all episode files to canonical form (dry run)
poetry run plex-leon episode-renamer --lib ./data/library-e --dry-run

# Actually rename episodes
poetry run plex-leon episode-renamer --lib ./data/library-e

# The two-step swap logic for case-only renames (e.g., 'season 01' to 'Season 01') ensures safe renaming even on case-insensitive filesystems and merges contents if the canonical folder already exists. No data is lost; conflicts are preserved in a `.plexleon_conflicts` folder.
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
- `plex_leon/migrate.py` — extraction, scanning, and move logic
- `plex_leon/season_renamer.py` — season folder renaming utility
- `plex_leon/episode_renamer.py` — episode file renaming utility
- `plex_leon/utils.py` — shared helpers (regex, parsing, formatting, safe renames)
- `plex_leon/cli.py` — subcommands and argument parsing

## Notes on CLI compatibility

- The CLI is subcommand-based (e.g., `migrate`, `season-renamer`, `episode-renamer`). For backward compatibility, running without a subcommand defaults to `migrate`.


### Build standalone executables (CI)

A GitHub Actions workflow builds single-file executables for Linux, macOS, and Windows using PyInstaller. It runs on tag pushes matching `v*` and on manual dispatch.

- Workflow: `.github/workflows/build-binaries.yml`
- Artifacts uploaded per-OS as `plex-leon-<OS>` (or `.exe` on Windows)

To trigger manually, use the Actions tab → build-binaries → Run workflow.
