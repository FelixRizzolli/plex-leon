
from .shared.utils import TVDB_REGEX, collect_tvdb_ids, extract_tvdb_id, move_file, file_size, read_video_resolution
from .utils.migrate import process_libraries

# Maintain backward compatibility: expose a CLI-compatible main that delegates to cli.main
from .cli import main

__all__ = [
    "TVDB_REGEX",
    "extract_tvdb_id",
    "collect_tvdb_ids",
    "move_file",
    "file_size",
    "read_video_resolution",
    "process_libraries",
    "main",
]
