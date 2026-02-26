from plex_leon.shared import EPISODE_TAG_REGEX


def parse_episode_tag(text: str) -> tuple[int, int, int | None, str | None] | None:
    """Parse an episode tag from text and return (season, ep1, ep2_or_None, split_name_or_None).

    Supports 's01e01', 'S01E01', double episodes like 'S01E01-E02', and split
    names like 'S01E01-CD1', 'S01E01 disc2', 'S01E02-E04-part1'.
    Returns None when no tag is found or parsing fails.

    The split_name is returned as a lowercase string like 'cd1', 'disc2', etc.
    """
    m = EPISODE_TAG_REGEX.search(text)
    if not m:
        return None
    try:
        s = int(m.group(1))
        e1 = int(m.group(2))
        e2s = m.group(3)
        e2 = int(e2s) if e2s is not None else None
        split_prefix = m.group(4)
        split_num = m.group(5)
        if split_prefix is not None and split_num is not None:
            split_name = f"{split_prefix.lower()}{split_num}"
        else:
            split_name = None
        return (s, e1, e2, split_name)
    except ValueError:
        return None
