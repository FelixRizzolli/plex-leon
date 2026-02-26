from plex_leon.shared import parse_episode_tag


def parse_season_episode(text: str) -> tuple[int, int] | None:
    """Return (season, episode) from text or None.

    For double-episode tags, returns the first episode number.
    Split names are ignored.
    """
    parsed = parse_episode_tag(text)
    if not parsed:
        return None
    s, e1, _e2, _split = parsed
    return (s, e1)