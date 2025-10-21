"""Shared movie configuration: single unique `movies` list."""
from __future__ import annotations

import random
import re
from typing import List, Optional, Set


"""Consolidated, unique list of movie titles (no file extension)."""
movies: list[str] = [
    "John Wick (2014) {tvdb-155}",
    "John Wick 2 (2017) {tvdb-511}",
    "John Wick 3 (2019) {tvdb-6494}",
    "John Wick 4 (2023) {tvdb-131523}",
    "Ballerina (2025) {tvdb-158074}",
    "Sisu (2022) {tvdb-201233}",
    "The Accountant (2016) {tvdb-940}",
    "The Accountant 2 (2025) {tvdb-357993}",
    "Extraction (2020) {tvdb-134279}",
    "Extraction 2 (2023) {tvdb-135342}",
    "The Equalizer (2014) {tvdb-136}",
    "The Equalizer 2 (2018) {tvdb-101}",
    "The Equalizer 3 (2023) {tvdb-342756}",
    "Taken (2008) {tvdb-525}",
    "Taken (2012) {tvdb-1148}",
    "Taken (2014) {tvdb-254}",
    "The Beekeeper (2024) {tvdb-349405}",
    "A Working Man (2025) {tvdb-358159}",
    "Army of the Dead (2021)",
    "Army of Thieves (2021)",
    "300 (2006) {tvdb-807}",
    "300 - Rise of an Empire (2014) {tvdb-459}",
    "Blade (1998) {tvdb-1651}",
    "Blade II (2002) {tvdb-2004}",
    "Blade - Trinity (2004) {tvdb-1700}",
    "I Am Legend (2007) {tvdb-587}",
    "Mr. No Pain (2025) {tvdb-358969}",
    "World War Z (2013) {tvdb-700}",
    "Edge of Tomorrow (2014) {tvdb-868}",
    "Dracula Untold (2014) {tvdb-443}",
    "Dune - Part One (2021) {tvdb-6187}",
    "Dune - Part Two (2024) {tvdb-290272}",
    "Blood & Sinners (2025) {tvdb-358595}",
    "Baby Driver (2017) {tvdb-342}",
    "Barry Seal (2017) {tvdb-1106}",
    "Barbie (2023) {tvdb-16612}",
    "Battleship (2012) {tvdb-972}",
    "American Sniper (2014) {tvdb-792}",
    "After Earth (2013) {tvdb-1990}",
    "Avatar (2009) {tvdb-165}",
    "Avatar - The Way of Water {tvdb-5483}",
    "The Matrix (1999) {tvdb-169}",
    "The Matrix Reloaded (2003) {tvdb-553}",
    "The Matrix Revolutions (2003) {tvdb-687}",
    "The Matrix Resurrections (2021) {tvdb-131590}",
    "The Chronicles of Narnia - The Lion, the Witch and the Wardrobe (2005) {tvdb-232}",
    "The Chronicles of Narnia - Prince Caspian (2008) {tvdb-483}",
    "The Chronicles of Narnia - The Voyage of the Dawn Treader (2010) {tvdb-550}",
    "Forrest Gump (1994) {tvdb-294}",
    "Fight Club (1999) {tvdb-247}",
    "Pulp Fiction (1994) {tvdb-228}",
    "The Godfather (1972) {tvdb-275}",
    "The Godfather - Part II (1974) {tvdb-1974}",
    "The Godfather - Part III (1990) {tvdb-2270}",
    "Inception (2010) {tvdb-113}",
    "Interstellar (2014) {tvdb-131079}",
    "Parasite (2019) {tvdb-41517}",
    "Tenet (2020) {tvdb-131281}",
    "The Wolf of Wall Street (2013) {tvdb-389}",
    "Catch Me If You Can (2002) {tvdb-312}",
    "Baywatch (2017) {tvdb-660}",
    "[REC] (2007) {tvdb-3331}",
    "[REC] 2 (2009) {tvdb-9259}",
    "28 Days Later (2002) {tvdb-871}",
    "28 Weeks Later (2007) {tvdb-835}",
    "28 Years Later (2025) {tvdb-307356}",
]


# Regular expression to extract TVDB id from a title like '{tvdb-12345}'
_TVDB_RE = re.compile(r"\{tvdb-(\d+)}", re.IGNORECASE)


def random_movies(items: int = 1, *, seed: Optional[int] = None, exclude: Optional[Set[str]] = None) -> List[str]:
    """Return up to `items` unique random movie titles from `movies`.

    Parameters
    - items: number of items to return
    - seed: optional seed for deterministic selection
    - exclude: optional set of strings to exclude; each value may be either
      the full movie title (e.g. "John Wick (2014) {tvdb-155}") or a TVDB id
      string (e.g. "155").

    If `items` is greater than available candidates, all candidates are
    returned in shuffled order.
    """
    rng = random.Random(seed)
    exclude = set(exclude or set())

    candidates: List[str] = []
    for title in movies:
        if title in exclude:
            continue
        m = _TVDB_RE.search(title)
        tvdb_id = m.group(1) if m else None
        if tvdb_id and tvdb_id in exclude:
            continue
        candidates.append(title)

    if items >= len(candidates):
        rng.shuffle(candidates)
        return candidates.copy()

    return rng.sample(candidates, items)


def filter_movies(names: List[str]) -> List[str]:
    """Return movie titles that exactly match names (backwards compatibility)."""
    return [m for m in movies if m in names]
