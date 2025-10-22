

import re


_TVDB_RE = re.compile(r"\{tvdb-(\d+)}", re.IGNORECASE)
_YEAR_RE = re.compile(r"\s*\((\d{4})\)")


def get_tvdb_id_from_name(name: str) -> str | None:
    m = _TVDB_RE.search(name)
    return m.group(1) if m else None


def strip_year_from_name(title_with_year: str) -> str:
    return _YEAR_RE.sub("", title_with_year).strip()
