from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

# Compiled regex used to extract TVDB ids like "{tvdb-12345}" from filenames
TVDB_REGEX = re.compile(r"\{tvdb-(\d+)\}", re.IGNORECASE)


def extract_tvdb_id(name: str) -> str | None:
    """Return the TVDB id embedded in a filename/folder name or None.

    Example: "John Wick (2014) {tvdb-155}.mp4" -> "155"
    """
    media = TVDB_REGEX.search(name)
    return media.group(1) if media else None


def collect_tvdb_ids(path: Path) -> set[str]:
    """Collect TVDB ids from the immediate children of a directory.

    Hidden entries (starting with a dot) are ignored. Both files and folders
    are considered.
    """
    ids: set[str] = set()
    for entry in path.iterdir():
        if not entry.name.startswith("."):
            tvdb = extract_tvdb_id(entry.name)
            if tvdb:
                ids.add(tvdb)
    return ids


def move_file(src: Path, dst: Path, *, overwrite: bool, dry_run: bool) -> None:
    """Move a file/folder from src to dst.

    - Creates destination parent directories as needed.
    - Prints an action message (or a skip message when not overwriting).
    - If dry_run=True, only prints without modifying the filesystem.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        print(f"SKIP exists: {dst}")
        return
    print(f"MOVE: {src} -> {dst}")
    if dry_run:
        return
    if dst.exists():
        if dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)
    shutil.move(src.as_posix(), dst.as_posix())


def file_size(path: Path) -> int:
    """Return the size of a file in bytes.

    - If the path doesn't exist or isn't a regular file, returns 0.
    - Never raises for missing files; use path.exists() if you need strict checks.
    """
    try:
        return path.stat().st_size if path.is_file() else 0
    except FileNotFoundError:
        return 0


def read_video_resolution(path: Path) -> tuple[int, int] | None:
    """Return (width, height) of the primary video stream from file metadata.

    Tries the following probes in order and returns the first successful result:
    1) ffprobe (from FFmpeg): fast and reliable
    2) mediainfo: common CLI tool on many systems

    Returns None if metadata cannot be read.
    """
    if not path.exists() or not path.is_file():
        return None

    def _num(val) -> int | None:
        """Best-effort convert width/height values to int.

        Accepts ints, floats, and strings like "1920", "1 920", "1920.0",
        or "1920 pixels". Returns None when parsing fails or value <= 0.
        """
        if isinstance(val, int):
            return val if val > 0 else None
        if isinstance(val, float):
            ival = int(val)
            return ival if ival > 0 else None
        if isinstance(val, str):
            m = re.search(r"(\d+)", val.replace("\u00a0", " "))
            if m:
                try:
                    ival = int(m.group(1))
                    return ival if ival > 0 else None
                except ValueError:
                    return None
        return None

    # Try ffprobe
    try:
        proc = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "json",
                path.as_posix(),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
        )
        if proc.returncode == 0 and proc.stdout:
            data = json.loads(proc.stdout)
            streams = data.get("streams") or []
            if streams:
                s0 = streams[0]
                w = _num(s0.get("width"))
                h = _num(s0.get("height"))
                if w and h:
                    return (w, h)
    except FileNotFoundError:
        # ffprobe not installed
        pass
    except json.JSONDecodeError:
        pass

    # ffprobe fallback with simple text output
    try:
        proc = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                path.as_posix(),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
        )
        if proc.returncode == 0 and proc.stdout:
            lines = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
            if len(lines) >= 2:
                w = _num(lines[0])
                h = _num(lines[1])
                if w and h:
                    return (w, h)
    except FileNotFoundError:
        pass

    # Try mediainfo
    try:
        proc = subprocess.run(
            ["mediainfo", "--Output=JSON", path.as_posix()],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
        )
        if proc.returncode == 0 and proc.stdout:
            data = json.loads(proc.stdout)
            media = data.get("media", {})
            tracks = media.get("track", [])
            for tr in tracks:
                if tr.get("@type") == "Video":
                    # mediainfo may provide width/height as strings
                    w = _num(tr.get("Width"))
                    h = _num(tr.get("Height"))
                    if w and h:
                        return (w, h)
    except FileNotFoundError:
        # mediainfo not installed
        pass
    except json.JSONDecodeError:
        pass

    return None
