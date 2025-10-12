
import re


# Additional regex/utilities for episode and folder handling
EPISODE_TAG_REGEX = re.compile(r"(?i)s(\d{1,2})e(\d{1,2})(?:-e(\d{1,2}))?")
TVDB_SUFFIX_REGEX = re.compile(r"\s*\{tvdb-\d+}\s*", re.IGNORECASE)
_SEASON_DIGITS_RE = re.compile(r"(\d+)")

# Compiled regex used to extract TVDB ids like "{tvdb-12345}" from filenames
TVDB_REGEX = re.compile(r"\{tvdb-(\d+)\}", re.IGNORECASE)
