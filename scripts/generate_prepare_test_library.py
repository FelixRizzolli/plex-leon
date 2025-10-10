"""Generate test library for the `prepare` script (library-p).

This script creates an idempotent test dataset under `data/library-p` with
three group folders ("anime sub", "anime dub", "serien"). Each group
contains several TV show folders named using the repository convention
"Title (YYYY) {tvdb-...}". All episode files are generated directly inside
their show folder (no `Season XX` directories) so the `prepare.process`
function can discover loose episode files, create season folders, and move
and rename them.

Naming patterns used by the generator:
- Most shows: German-style filenames like
  "Episode {ep} Staffel {season} von <Show> K to - Serien Online.mp4".
- Classroom of the Elite: uses the SxxExx pattern across all seasons:
  "Watch Classroom of the Elite S{SS}E{EE} German 720p WEB h264-WvF - OWE Content.mp4".

Season/episode counts are driven from the `SEASON_EP_COUNTS` mapping so the
generator produces multiple seasons per show where configured. Re-running the
script is safe; existing files are left untouched.
"""

from __future__ import annotations

from pathlib import Path
import sys


ROOT_REL = Path("data") / "library-p"

SHOW_GROUPS: dict[str, list[str]] = {
    "anime sub": [
        "Attack on Titan (2013) {tvdb-267440}",
        "Classroom of the Elite (2017) {tvdb-329822}",
    ],
    "anime dub": [
        "Overlord (2015) {tvdb-294002}",
        "Death Note (2006) {tvdb-79481}",
    ],
    "serien": [
        "Game of Thrones (2011) {tvdb-121361}",
        "My Name (2021) {tvdb-397441}",
        "The Day of the Jackal (1973) {tvdb-426866}",
    ],
}

# For most shows we create (season, episodes) pairs.
SEASON_EP_COUNTS: dict[str, list[tuple[int, int]]] = {
    "Attack on Titan": [(1, 25), (2, 12), (3, 22), (4, 30)],
    "Classroom of the Elite": [(1, 12), (2, 13), (3, 13)],
    "Overlord": [(1, 13), (2, 13), (3, 13), (4, 13)],
    "Death Note": [(1, 37)],
    "Game of Thrones": [(1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 7), (8, 6)],
    "My Name": [(1, 8)],
    "The Day of the Jackal": [(1, 10)],
}

# Classroom of the Elite uses SxxExx pattern across all seasons (counts from SEASON_EP_COUNTS).


def _base_show_name(folder_name: str) -> str:
    """Return the bare show title without year/TVDB id.

    Examples:
      'Attack on Titan (2013) {tvdb-267440}' -> 'Attack on Titan'
      'The Day of the Jackal (1973) {tvdb-80379}' -> 'The Day of the Jackal'
    """
    # Remove tvdb part
    no_tvdb = folder_name.split(' {tvdb-')[0]
    # Drop trailing year in parens if present
    m = __import__('re').search(r"^(.*) \(\d{4}\)$", no_tvdb)
    return m.group(1) if m else no_tvdb


def create_library(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for group, shows in SHOW_GROUPS.items():
        group_dir = root / group
        group_dir.mkdir(parents=True, exist_ok=True)
        print(f"mkdir: {group_dir}")
        for show in shows:
            show_dir = group_dir / show
            show_dir.mkdir(parents=True, exist_ok=True)
            print(f"mkdir: {show_dir}")
            base_name = _base_show_name(show)

            if base_name == "Classroom of the Elite":
                # Use SEASON_EP_COUNTS for seasons; custom SxxExx naming pattern.
                for season, ep_count in SEASON_EP_COUNTS.get(base_name, []):
                    for ep in range(1, ep_count + 1):
                        filename = (
                            f"Watch Classroom of the Elite S{season:02d}E{ep:02d} "
                            "German 720p WEB h264-WvF - OWE Content.mp4"
                        )
                        fp = show_dir / filename
                        if fp.exists():
                            print(f"skip (exists): {fp}")
                            continue
                        fp.write_bytes(b"")
                        print(f"touch: {fp}")
                continue

            # Standard German pattern shows
            for season, ep_count in SEASON_EP_COUNTS.get(base_name, []):
                for ep in range(1, ep_count + 1):
                    filename = f"Episode {ep} Staffel {season} von {base_name} K to - Serien Online.mp4"
                    fp = show_dir / filename
                    if fp.exists():
                        print(f"skip (exists): {fp}")
                        continue
                    fp.write_bytes(b"")
                    print(f"touch: {fp}")


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    dest = ROOT_REL if not argv else Path(argv[0])
    create_library(dest)
    print("Done generating library-p test data.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
