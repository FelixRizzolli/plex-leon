"""
Utility to generate a sample media library under the repository's data/ folder for episode renamer tests.

It will create the following structure (if missing):

data/
  library-e/
    <TV Show Name with {tvdb-...}>/
      Season 01/
        <Show Name [(Year, sometimes omitted)]> - s01e01|S01E01[ - <Episode Title (with occasional typos)>].mp4
        ...
      Season 02/
        ...

Differences to the season generator:
- Keeps season folder names standard ("Season XX") and varies the EPISODE filenames instead.
- Variations include:
  - For some shows, the year in the show name is omitted in the episode filename.
  - For some shows, the SxxExx tag is uppercase (e.g., S01E01) instead of lowercase.
  - For some shows/episodes, an episode title is appended (and sometimes includes small typos).

Re-running is safe and will skip copies that already exist.
"""

from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Iterable
import sys
import shutil

# --- TV show config (copied from generate_merge_test_libraries.py) ---
library_a_tvshows = [
    "Classroom of the Elite (2017) {tvdb-329822}",
    "Code Geass (2006) {tvdb-79525}",
    "Game of Thrones (2011) {tvdb-121361}",
    "Attack on Titan (2013) {tvdb-267440}",
    "Death Note (2006) {tvdb-79434}",
    "Overlord (2015) {tvdb-295068}",
    "Breaking Bad (2008) {tvdb-81189}",
    "The Day of the Jackal (1973) {tvdb-80379}",
]
library_b_tvshows = [
    "Game of Thrones (2011) {tvdb-121361}",
    "Attack on Titan (2013) {tvdb-267440}",
    "My Name (2021) {tvdb-410235}",
    "Squid Game (2021) {tvdb-407183}",
    "One Punch Man (2015) {tvdb-299880}",
    "Breaking Bad (2008) {tvdb-81189}",
]

# Known season/episode counts for the sample shows we generate
EPISODE_MAP: dict[str, dict[int, int]] = {
    "121361": {1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10, 7: 7, 8: 6},
    "79525": {1: 25, 2: 25},
    "329822": {1: 12, 2: 13, 3: 13},
    "267440": {1: 25, 2: 12, 3: 22, 4: 28},
    "79434": {1: 37},
    "295068": {1: 13, 2: 13, 3: 13, 4: 13},
    "81189": {1: 7, 2: 13, 3: 13, 4: 13, 5: 16},
    "80379": {1: 1},
    "410235": {1: 8},
    "407183": {1: 9},
    "299880": {1: 12, 2: 12},
}

_TVDB_RE = re.compile(r"\{tvdb-(\d+)}", re.IGNORECASE)
_YEAR_RE = re.compile(r"\s*\((\d{4})\)")


def _tvdb_id_from_name(name: str) -> str | None:
    m = _TVDB_RE.search(name)
    return m.group(1) if m else None


def _strip_year(title_with_year: str) -> str:
    return _YEAR_RE.sub("", title_with_year).strip()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _random_title(rng: random.Random, tvdb: str, season: int, ep: int) -> str:
    # Always generate a plausible synthetic title
    words1 = ["Dark", "New", "Last", "First", "Broken",
              "Lost", "Silent", "Hidden", "Fallen", "Rising"]
    words2 = ["Path", "Secret", "Empire", "Deal", "Code",
              "Game", "Name", "Power", "Throne", "Note"]
    words3 = ["Begins", "Returns", "Awakening", "Legacy", "Gambit",
              "Oath", "Trial", "Reckoning", "Echoes", "Horizon"]
    return f"{rng.choice(words1)} {rng.choice(words2)} {rng.choice(words3)}"


def _introduce_typos(text: str, rng: random.Random, intensity: float = 0.15) -> str:
    """Introduce a few gentle typos into the text.

    intensity ~ probability per operation; will apply up to 2 small edits.
    """
    if not text:
        return text
    s = list(text)
    ops = ["swap", "drop", "dup", "replace"]
    applied = 0
    max_ops = 2 if len(s) >= 6 else 1
    vowels = "aeiou"
    while applied < max_ops and rng.random() < intensity:
        if len(s) == 0:
            break
        op = rng.choice(ops)
        i = rng.randrange(len(s))
        # avoid spaces for destructive ops
        if s[i] == " ":
            continue
        if op == "swap" and i + 1 < len(s) and s[i + 1] != " ":
            s[i], s[i + 1] = s[i + 1], s[i]
            applied += 1
        elif op == "drop" and len(s) > 1:
            s.pop(i)
            applied += 1
        elif op == "dup":
            s.insert(i, s[i])
            applied += 1
        elif op == "replace":
            ch = s[i]
            if ch.lower() in vowels:
                alt = rng.choice(vowels.replace(ch.lower(), "") or vowels)
                s[i] = alt.upper() if ch.isupper() else alt
            else:
                s[i] = ch.upper() if ch.islower() else ch.lower()
            applied += 1
    return "".join(s)


def create_seasons_and_episodes(base: Path, show_names: Iterable[str], *, seed: int | None = 987) -> None:
    rng = random.Random(seed)

    for show in show_names:
        tvdb = _tvdb_id_from_name(show)
        show_dir = base / show
        show_dir.mkdir(parents=True, exist_ok=True)
        print(f"mkdir: {show_dir}")
        if not tvdb or tvdb not in EPISODE_MAP:
            continue

        # Decide per-show filename variations
        include_year = rng.random() < 0.6  # some shows keep year, some omit
        upper_se_tag = rng.random() < 0.5  # some shows use S01E01
        include_titles = rng.random() < 0.65  # many shows include titles

        # e.g., "Code Geass (2006)"
        title_with_year = show.split(" {")[0].strip()
        title_no_year = _strip_year(title_with_year)

        seasons = EPISODE_MAP[tvdb]
        for season_num in sorted(seasons.keys()):
            season_dir = show_dir / f"Season {season_num:02d}"
            season_dir.mkdir(parents=True, exist_ok=True)
            print(f"mkdir: {season_dir}")

            ep_total = seasons[season_num]
            ep_num = 1
            while ep_num <= ep_total:
                # Randomly decide if this file should be a double-episode file (about 1 in 8 chance, and only if next ep exists)
                is_double = ep_num < ep_total and rng.random() < 0.125
                if is_double:
                    # S01E01-E02 style
                    ep_start = ep_num
                    ep_end = ep_num + 1
                    # Choose per-file whether to add a title and whether to add a tiny typo
                    add_title = include_titles and rng.random() < 0.85
                    episode_title = _random_title(
                        rng, tvdb, season_num, ep_start) if add_title else ""
                    if episode_title and rng.random() < 0.35:
                        episode_title = _introduce_typos(episode_title, rng)

                    # Build S/E tag
                    s_tag = f"s{season_num:02d}e{ep_start:02d}-e{ep_end:02d}"
                    if upper_se_tag:
                        s_tag = s_tag.upper()  # S01E01-E02

                    # Build show part (maybe omit year)
                    show_part = title_with_year if include_year else title_no_year

                    # Assemble filename
                    parts = [show_part, s_tag]
                    if episode_title:
                        parts.append(episode_title)
                    filename = " - ".join(parts) + ".mp4"
                    dst = season_dir / filename

                    if dst.exists():
                        print(f"skip (exists): {dst}")
                        ep_num += 2
                        continue
                    dst.write_bytes(b"")
                    print(f"touch: {dst}")
                    ep_num += 2
                else:
                    # Single episode file as before
                    add_title = include_titles and rng.random() < 0.85
                    episode_title = _random_title(
                        rng, tvdb, season_num, ep_num) if add_title else ""
                    if episode_title and rng.random() < 0.35:
                        episode_title = _introduce_typos(episode_title, rng)

                    s_tag = f"s{season_num:02d}e{ep_num:02d}"
                    if upper_se_tag:
                        s_tag = s_tag.upper()

                    show_part = title_with_year if include_year else title_no_year

                    parts = [show_part, s_tag]
                    if episode_title:
                        parts.append(episode_title)
                    filename = " - ".join(parts) + ".mp4"
                    dst = season_dir / filename

                    if dst.exists():
                        print(f"skip (exists): {dst}")
                        ep_num += 1
                        continue
                    dst.write_bytes(b"")
                    print(f"touch: {dst}")
                    ep_num += 1


def main(argv: list[str] | None = None) -> int:
    base = repo_root() / "data" / "library-e"
    if argv is None:
        argv = sys.argv[1:]
    force = False
    if '--force' in argv:
        force = True
    if '-f' in argv:
        force = True

    if base.exists() and not force:
        resp = input(f"Target {base} exists. Delete it and recreate? [y/N]: ")
        if resp.strip().lower() not in ("y", "yes"):
            print("Aborted — target not removed.")
            return 1
        shutil.rmtree(base)

    base.mkdir(parents=True, exist_ok=True)
    # Use all unique TV shows from both libraries
    all_tvshows = sorted(set(library_a_tvshows + library_b_tvshows))
    create_seasons_and_episodes(base, all_tvshows, seed=1337)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
