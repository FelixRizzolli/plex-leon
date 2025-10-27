from __future__ import annotations

import importlib.util
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import urllib.request

from loguru import logger as loguru_logger


@dataclass(frozen=True)
class DownloadSpec:
    resolution: str
    size: str
    url: str


@dataclass
class GeneratorOptions:
    log_level: int | str = 20


class BaseTestLibraryGenerator(ABC):
    """Base class for generator scripts.

    Child classes must implement `execute(...)`. Callers should invoke
    `run(...)` which ensures sample videos are downloaded into `temp_dir`
    before delegating to `execute`.
    """

    def __init__(
        self,
        *,
        repo_root: Path | None = None,
        temp_dir: Path | None = None,
        logger=None,
        log_level: int | str = 20,
    ):
        default_root = Path(__file__).resolve().parents[3]
        self.repo_root = Path(
            repo_root) if repo_root is not None else default_root
        self.temp_dir = Path(temp_dir) if temp_dir is not None else (
            self.repo_root / "data" / "temp")
        self.opts = GeneratorOptions(log_level=log_level)

        if logger is not None:
            self.logger = logger
        else:
            self.logger = loguru_logger
            if not getattr(self.logger, "_plex_leon_configured", False):
                self.logger.remove()
                level = self._normalize_level(self.log_level)
                fmt = (
                    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                    "<level>{level: <8}</level> | {message}"
                )
                self.logger.add(sys.stderr, level=level, format=fmt)
                setattr(self.logger, "_plex_leon_configured", True)

    @property
    def log_level(self) -> int | str:
        return self.opts.log_level

    def _normalize_level(self, level: int | str) -> int | str:
        if isinstance(level, int):
            return level
        if not isinstance(level, str):
            raise TypeError("log_level must be int or str")
        name = level.strip().upper()
        mapping = {
            "TRACE": "TRACE",
            "DEBUG": "DEBUG",
            "INFO": "INFO",
            "SUCCESS": "SUCCESS",
            "WARNING": "WARNING",
            "WARN": "WARNING",
            "ERROR": "ERROR",
            "CRITICAL": "CRITICAL",
            "FATAL": "CRITICAL",
        }
        return mapping.get(name, name)

    def log_error(self, msg: str, /) -> None:
        self.logger.error(f"❌ ERROR: {msg}")

    def log_warning(self, msg: str, /) -> None:
        self.logger.warning(f"⚠️ WARN: {msg}")

    def log_info(self, msg: str, /) -> None:
        self.logger.info(f"ℹ️ {msg}")

    def log_debug(self, msg: str, /) -> None:
        self.logger.debug(f"🐛 DEBUG: {msg}")

    def log_verbose(self, msg: str, /) -> None:
        self.logger.trace(f"🔍 VERBOSE: {msg}")

    def run(self, *args, **kwargs):
        """Top-level runner.

        Ensures sample videos are present in `temp_dir` then calls
        the concrete `execute` implementation.
        """
        # Ensure the temp directory exists and contains sample clips
        try:
            self.download_sample_videos()
        except Exception:
            # Log the exception but proceed so callers can still create
            # directories/placeholders as needed.
            self.logger.exception(
                "❌ ERROR: download_sample_videos failed; continuing to execute")

        return self.execute(*args, **kwargs)

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Override in subclasses to perform the generator work.

        Should return an int (exit code) or any meaningful result for the
        specific generator.
        """

    # -- download helpers -------------------------------------------------
    def _downloads_py_path(self) -> Path:
        """Return path to the shared downloads.py used by the generators."""
        # scripts/generators -> repo_root/scripts/shared/downloads.py
        return self.repo_root / "scripts" / "shared" / "downloads.py"

    def _load_downloads(self) -> list[DownloadSpec]:
        p = self._downloads_py_path()
        if not p.exists():
            self.log_warning(f"downloads.py not found at {p}")
            return []

        spec = importlib.util.spec_from_file_location("_gen_downloads", str(p))
        if spec is None:
            self.log_error("Unable to create spec for downloads.py")
            return []
        mod = importlib.util.module_from_spec(spec)
        # spec.loader may be None in static checkers, guard accordingly
        loader = getattr(spec, "loader", None)
        if loader is None:
            self.log_error("Unable to load downloads.py (no loader)")
            return []
        loader.exec_module(mod)  # type: ignore[attr-defined]
        raw = getattr(mod, "downloads", [])
        out: list[DownloadSpec] = []
        for entry in raw:
            try:
                out.append(DownloadSpec(str(entry.get("resolution")),
                           str(entry.get("size")), str(entry.get("url"))))
            except Exception:
                self.logger.exception(
                    f"❌ ERROR: invalid download entry in downloads.py: {entry!r}")
        return out

    def download_sample_videos(self, specs: Iterable[DownloadSpec] | None = None, *, overwrite: bool = False) -> List[Path]:
        """Ensure sample videos exist in `self.temp_dir`.

        If `self.temp_dir` already exists and contains any files, the method
        does nothing (returns the existing file list). Otherwise it downloads
        the sample files described by `specs` (or those from shared
        `downloads.py`) into `self.temp_dir` and returns the list of file
        Paths.
        """
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        existing = [p for p in self.temp_dir.iterdir() if p.is_file()]
        if existing and not overwrite:
            self.log_debug(
                f"temp dir exists and contains files; skipping downloads: {self.temp_dir}")
            return existing

        if specs is None:
            specs = self._load_downloads()

        downloaded: List[Path] = []
        for spec in specs:
            # make a stable filename
            ext = ".mp4"
            url_path = spec.url.split("?")[0]
            if "." in url_path.rsplit("/", 1)[-1]:
                ext = "." + url_path.rsplit('.', 1)[-1]
            dest = self.temp_dir / f"sample_{spec.resolution}_{spec.size}{ext}"
            if dest.exists() and dest.stat().st_size > 0 and not overwrite:
                self.log_info(f"skip download (exists): {dest}")
                downloaded.append(dest)
                continue

            tmp = dest.with_suffix(dest.suffix + ".part")
            try:
                self.log_info(f"downloading: {spec.url} -> {dest}")
                with urllib.request.urlopen(spec.url, timeout=60) as resp, open(tmp, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                tmp.replace(dest)
                downloaded.append(dest)
            except Exception:
                self.logger.exception(
                    f"❌ ERROR: failed to download {spec.url}")
                # create a small placeholder so subsequent steps can proceed
                if not dest.exists():
                    try:
                        dest.write_bytes(b"")
                        downloaded.append(dest)
                    except Exception:
                        self.logger.exception(
                            f"❌ ERROR: failed to write placeholder for {dest}")

        return downloaded
