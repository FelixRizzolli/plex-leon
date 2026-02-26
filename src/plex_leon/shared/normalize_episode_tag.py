
from plex_leon.shared import EPISODE_TAG_REGEX, parse_episode_tag


def normalize_episode_tag(text: str) -> str | None:
    """Return the normalized lowercase episode tag or None.

    Examples:
        's01e01', 's01e01-e02', 's01e01 - cd1', 's01e01-e02 - disk1'
    """
    parsed = parse_episode_tag(text)
    if not parsed:
        return None
    s, e1, e2, split = parsed
    tag = f"s{s:02d}e{e1:02d}"
    if e2 is not None:
        tag += f"-e{e2:02d}"
    if split is not None:
        tag += f" - {split}"
    return tag
