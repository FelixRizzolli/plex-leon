"""Shared TV show configuration for test library generators."""

import random
import re
from typing import List, Optional, Set, Dict

# Consolidated TV show data with episode counts
tvshows: list[dict[str, object]] = [
    {
        "name": "Game of Thrones (2011) {tvdb-121361}",
        "episodes": {1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10, 7: 7, 8: 6},
    },
    {
        "name": "House of the Dragon (2022) {tvdb-121361}",
        "episodes": {1: 10, 2: 8},
    },
    {
        "name": "The Lord of the Rings - The Rings of Power (2022) {tvdb-367506}",
        "episodes": {1: 8, 2: 8},
    },
    {
        "name": "The Witcher (2019) {tvdb-362696}",
        "episodes": {1: 8, 2: 8, 3: 8, 4: 8},
    },
    {
        "name": "The Witcher - Blood Origin (2022) {tvdb-399987}",
        "episodes": {1: 4},
    },
    {
        "name": "Alien - Earth (2025) {tvdb-458912}",
        "episodes": {1: 8},
    },
    {
        "name": "Fallout (2024) {tvdb-416744}",
        "episodes": {1: 8, 2: 8},
    },
    {
        "name": "The Recruit (2022) {tvdb-425260}",
        "episodes": {1: 8, 2: 6},
    },
    {
        "name": "The Night Agent (2023) {tvdb-407281}",
        "episodes": {1: 10, 2: 10},
    },
    {
        "name": "Alex Rider (2020) {tvdb-370312}",
        "episodes": {1: 8, 2: 8, 3: 8},
    },
    {
        "name": "Hanna (2019) {tvdb-357690}",
        "episodes": {1: 8, 2: 8, 3: 6},
    },
    {
        "name": "Wednesday (2022) {tvdb-397060}",
        "episodes": {1: 8, 2: 8},
    },
    {
        "name": "Reacher (2022) {tvdb-366924}",
        "episodes": {1: 8, 2: 8, 3: 8},
    },
    {
        "name": "Warrior Nun (2020) {tvdb-366924}",
        "episodes": {1: 10, 2: 8},
    },
    {
        "name": "Lupin (2021) {tvdb-375921}",
        "episodes": {1: 10, 2: 7},
    },
    {
        "name": "The Terminal List (2022) {tvdb-399917}",
        "episodes": {1: 8},
    },
    {
        "name": "The Terminal List - Dark Wolf (2025) {tvdb-464185}",
        "episodes": {1: 7},
    },
    {
        "name": "3 Body Problem (2024) {tvdb-411959}",
        "episodes": {1: 8},
    },
    {
        "name": "Prison Break (2005) {tvdb-121361}",
        "episodes": {1: 22, 2: 22, 3: 13, 4: 22, 5: 9},
    },
    {
        "name": "Breaking Bad (2008) {tvdb-81189}",
        "episodes": {1: 7, 2: 13, 3: 13, 4: 13, 5: 16},
    },
    {
        "name": "Better Call Saul (2015) {tvdb-273181}",
        "episodes": {1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 13},
    },
    {
        "name": "Orphan Black (2013) {tvdb-260315}",
        "episodes": {1: 10, 2: 10, 3: 10, 4: 10, 5: 10},
    },
    {
        "name": "The 100 (2014) {tvdb-268592}",
        "episodes": {1: 13, 2: 16, 3: 16, 4: 13, 5: 13, 6: 13, 7: 16},
    },
    {
        "name": "Attack on Titan (2013) {tvdb-267440}",
        "episodes": {1: 25, 2: 12, 3: 22, 4: 28},
    },
    {
        "name": "One Punch Man (2015) {tvdb-293088}",
        "episodes": {1: 12, 2: 12, 3: 12},
    },
    {
        "name": "Overlord (2015) {tvdb-294002}",
        "episodes": {1: 13, 2: 13, 3: 13, 4: 13},
    },
    {
        "name": "Code Geass (2006) {tvdb-79525}",
        "episodes": {1: 25, 2: 25},
    },
    {
        "name": "Death Note (2006) {tvdb-79481}",
        "episodes": {1: 37},
    },
    {
        "name": "Classroom of the Elite (2017) {tvdb-329822}",
        "episodes": {1: 12, 2: 13, 3: 13},
    },
    {
        "name": "My Name (2021) {tvdb-397441}",
        "episodes": {1: 8},
    },
    {
        "name": "Squid Game (2021) {tvdb-383275}",
        "episodes": {1: 9, 2: 7, 3: 6},
    },
    {
        "name": "The Day of the Jackal (2024) {tvdb-426866}",
        "episodes": {1: 10},
    },
]


# Regular expression to extract TVDB id from the show name
_TVDB_RE = re.compile(r"\{tvdb-(\d+)}", re.IGNORECASE)


def random_tvshows(items: int = 1, *, seed: Optional[int] = None, exclude: Optional[Set[str]] = None) -> List[dict[str, object]]:
    """Return a list of unique random TV show entries from `tvshows`.

    Parameters
    - items: number of items to return
    - seed: optional seed for deterministic selection
    - exclude: optional set of strings to exclude; each value may be either
      the full show name (e.g. "Game of Thrones (2011) {tvdb-121361}") or a
      TVDB id string (e.g. "121361").

    The function returns up to `items` unique shows. If `items` is greater
    than the number of available (non-excluded) shows, all available shows
    are returned in a random order.
    """
    rng = random.Random(seed)
    exclude = set(exclude or set())

    # Filter candidates respecting exclude (by full name or tvdb id)
    candidates: List[dict[str, object]] = []
    for show in tvshows:
        name = show.get("name")
        if not isinstance(name, str):
            continue
        # Extract tvdb id if present
        m = _TVDB_RE.search(name)
        tvdb_id = m.group(1) if m else None

        if name in exclude or (tvdb_id and tvdb_id in exclude):
            continue
        candidates.append(show)

    # If not enough candidates, return all in shuffled order
    if items >= len(candidates):
        rng.shuffle(candidates)
        return candidates.copy()

    # Otherwise pick a random sample of unique entries
    picked = rng.sample(candidates, items)
    return picked


def filter_shows(names: list[str]) -> list[dict[str, object]]:
    """Return TV shows matching the given names.

    Backwards-compatible helper used by generator scripts.
    """
    return [show for show in tvshows if show["name"] in names]


def get_tvshow_episodes(tvdb: str) -> dict[int, int] | None:
    """Return the episodes mapping for a TVDB id by looking it up in `tvshows`.

    Returns None if no matching show with episodes is found.
    """
    for s in tvshows:
        name = s.get("name")
        episodes = s.get("episodes")
        if not isinstance(name, str) or not isinstance(episodes, dict):
            continue
        m = _TVDB_RE.search(name)
        if m and m.group(1) == tvdb:
            return episodes
    return None
