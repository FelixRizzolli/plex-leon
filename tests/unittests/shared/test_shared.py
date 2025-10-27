import importlib
import sys

import pytest
from plex_leon import shared


MEDIA_ENTRIES = [
    {
        "name": "John Wick (2014) {tvdb-155}",
        "title": "John Wick",
        "title_year": "John Wick (2014)",
        "year": "2014",
        "tvdbid": "155",
    },
    {
        "name": "300 - Rise of an Empire (2014) {tvdb-459}",
        "title": "300 - Rise of an Empire",
        "title_year": "300 - Rise of an Empire (2014)",
        "year": "2014",
        "tvdbid": "459",
    },
    {
        "name": "The Chronicles of Narnia - The Lion, the Witch and the Wardrobe (2005) {tvdb-232}",
        "title": "The Chronicles of Narnia - The Lion, the Witch and the Wardrobe",
        "title_year": "The Chronicles of Narnia - The Lion, the Witch and the Wardrobe (2005)",
        "year": "2005",
        "tvdbid": "232",
    },
    {
        "name": "[REC] (2007) {tvdb-3331}",
        "title": "[REC]",
        "title_year": "[REC] (2007)",
        "year": "2007",
        "tvdbid": "3331",
    },
    {
        "name": "The Lord of the Rings - The Rings of Power (2022) {tvdb-367506}",
        "title": "The Lord of the Rings - The Rings of Power",
        "title_year": "The Lord of the Rings - The Rings of Power (2022)",
        "year": "2022",
        "tvdbid": "367506",
    },
    {
        "name": "Game of Thrones (2011) {tvdb-121361}",
        "title": "Game of Thrones",
        "title_year": "Game of Thrones (2011)",
        "year": "2011",
        "tvdbid": "121361",
    },
    {
        "name": "The Terminal List - Dark Wolf (2025) {tvdb-464185}",
        "title": "The Terminal List - Dark Wolf",
        "title_year": "The Terminal List - Dark Wolf (2025)",
        "year": "2025",
        "tvdbid": "464185",
    },
]


@pytest.mark.parametrize(
    "entry",
    MEDIA_ENTRIES,
    ids=[media["name"] for media in MEDIA_ENTRIES],
)
def test_tvdb_regex_extracts_identifier(entry: dict[str, str]) -> None:
    match = shared.TVDB_REGEX.search(entry["name"])
    assert match
    assert match.group(1) == entry["tvdbid"]


@pytest.mark.parametrize(
    "entry",
    MEDIA_ENTRIES,
    ids=[media["name"] for media in MEDIA_ENTRIES],
)
def test_tvdb_suffix_regex_removes_wrapped_suffix(entry: dict[str, str]) -> None:
    stripped = shared.TVDB_SUFFIX_REGEX.sub("", entry["name"]).strip()
    assert stripped == entry["title_year"]


def test_dir_lists_exported_helpers() -> None:
    """Check that key helpers are present in the shared package's dir().
    Ensures the lazy export mechanism and __all__ are working as intended.
    """
    exported = dir(shared)
    assert "format_bytes" in exported
    assert "EPISODE_TAG_REGEX" in exported


def test_getattr_lazy_imports_and_caches_exports() -> None:
    """Test that __getattr__ lazily loads and caches exported helpers.
    Verifies that the shared module does not eagerly import submodules, and that
    after attribute access, the helper is cached in the module dict.
    """
    module_name = "plex_leon.shared"
    original_main = sys.modules[module_name]
    original_submodules = {
        name: sys.modules[name]
        for name in list(sys.modules)
        if name.startswith(f"{module_name}.")
    }

    try:
        for name in list(sys.modules):
            if name == module_name or name.startswith(f"{module_name}."):
                sys.modules.pop(name)

        fresh = importlib.import_module(module_name)
        assert "format_bytes" not in fresh.__dict__

        func = fresh.format_bytes
        assert callable(func)
        assert fresh.__dict__["format_bytes"] is func
    finally:
        for name in list(sys.modules):
            if name == module_name or name.startswith(f"{module_name}."):
                sys.modules.pop(name)
        sys.modules[module_name] = original_main
        sys.modules.update(original_submodules)
