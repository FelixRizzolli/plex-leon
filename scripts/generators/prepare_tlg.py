"""Generate test library for the `prepare` script (library-p).

This script creates a test dataset under `data/library-p` with three group
folders ("anime sub", "anime dub", "serien"). Each group contains several
TV show folders named using the repository convention "Title (YYYY) {tvdb-...}".
All episode files are generated directly inside their show folder (no
`Season XX` directories) so the `prepare.process` function can discover loose
episode files, create season folders, and move and rename them.

Naming patterns used by the generator:
- Most shows: German-style filenames like
    "Episode {ep} Staffel {season} von <Show> K to - Serien Online.mp4".
- Classroom of the Elite: uses the SxxExx pattern across all seasons:
    "Watch Classroom of the Elite S{SS}E{EE} German 720p WEB h264-WvF - OWE Content.mp4".

To simulate real-world duplicate/conflict cases this generator will create a
single "-01" duplicate file, but only for Game of Thrones season 1 episode
5. This is intentional: duplicate creation was restricted to the GOT show so
the `prepare` command can be tested against a focused conflict scenario.

Behavior notes:
- Running the script will remove the destination `data/library-p` folder (if
    present) before creating the test dataset. Use with caution: this is a
    destructive operation and will delete any existing files under that path.

- The generator will then create files from a clean slate. It is therefore
    deterministic and safe to rely on for reproducible test datasets.

Season/episode counts are driven from the `SEASON_EP_COUNTS` mapping so the
generator produces multiple seasons per show where configured.
"""

from __future__ import annotations

from pathlib import Path
import sys
import shutil
from base_test_library_generator import BaseTestLibraryGenerator


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

SEASON_EP_COUNTS: dict[str, list[tuple[int, int]]] = {
    "Attack on Titan": [(1, 25), (2, 12), (3, 22), (4, 30)],
    "Classroom of the Elite": [(1, 12), (2, 13), (3, 13)],
    "Overlord": [(1, 13), (2, 13), (3, 13), (4, 13)],
    "Death Note": [(1, 37)],
    "Game of Thrones": [(1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 7), (8, 6)],
    "My Name": [(1, 8)],
    "The Day of the Jackal": [(1, 10)],
}


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
    if root.exists():
        shutil.rmtree(root)

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

            # Naming Pattern S01E01
            if base_name == "Classroom of the Elite":
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

            # Naming Pattern Episode 1 Staffel 1
            for season, ep_count in SEASON_EP_COUNTS.get(base_name, []):
                for ep in range(1, ep_count + 1):
                    filename = f"Episode {ep} Staffel {season} von {base_name} K to - Serien Online.mp4"
                    fp = show_dir / filename
                    if fp.exists():
                        print(f"skip (exists): {fp}")
                        continue
                    fp.write_bytes(b"")
                    print(f"touch: {fp}")

                    # Create a '-01' variant only for Game of Thrones season 1 episode 5
                    if base_name == "Game of Thrones" and season == 1 and ep == 5:
                        dup = fp.with_name(fp.stem + "-01" + fp.suffix)
                        if not dup.exists():
                            dup.write_bytes(b"")
                            print(f"touch: {dup}")


def main(argv: list[str] | None = None) -> int:
    gen = PrepareTestLibraryGenerator()
    return gen.run(argv)


class PrepareTestLibraryGenerator(BaseTestLibraryGenerator):
    """Generator for prepare test library (library-p)."""

    # type: ignore[override]
    def execute(self, argv: list[str] | None = None) -> int:
        if argv is None:
            argv = sys.argv[1:]
        # simple arg handling: optional dest path and optional --force / -f flag
        force = False
        args = [a for a in argv]
        if '--force' in args:
            force = True
            args.remove('--force')
        if '-f' in args:
            force = True
            args.remove('-f')

        dest = ROOT_REL if not args else Path(args[0])

        if dest.exists() and not force:
            resp = input(
                f"Target {dest} exists. Delete it and recreate? [y/N]: ")
            if resp.strip().lower() not in ("y", "yes"):
                print("Aborted — target not removed.")
                return 1

        create_library(dest)
        print("Done generating library-p test data.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
