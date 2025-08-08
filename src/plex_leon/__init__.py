from .core import (
    TVDB_REGEX,
    collect_tvdb_ids,
    extract_tvdb_id,
    move_file,
    process_libraries,
)

# Maintain backward compatibility: expose a CLI-compatible main that delegates to cli.main
from .cli import main

__all__ = [
    "TVDB_REGEX",
    "extract_tvdb_id",
    "collect_tvdb_ids",
    "move_file",
    "process_libraries",
    "main",
]
