from __future__ import annotations

import importlib.util
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import urllib.request


@dataclass(frozen=True)
class DownloadSpec:
    resolution: str
    size: str
    url: str


class BaseTestLibraryGenerator(ABC):
    """Base class for generator scripts.

    Child classes must implement `execute(...)`. Callers should invoke
    `run(...)` which ensures sample videos are downloaded into `temp_dir`
    before delegating to `execute`.
    """

    def __init__(self, *, repo_root: Path | None = None, temp_dir: Path | None = None, logger: logging.Logger | None = None):
        self.repo_root = Path(repo_root) if repo_root is not None else Path(
            __file__).resolve().parents[2]
        self.temp_dir = Path(temp_dir) if temp_dir is not None else (
            self.repo_root / "data" / "temp")
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def run(self, *args, **kwargs):
        """Top-level runner.

        Ensures sample videos are present in `temp_dir` then calls
        the concrete `execute` implementation.
        """
        # Ensure the temp directory exists and contains sample clips
        try:
            self.download_sample_videos()
        except Exception:
            # Log the exception but proceed to execute so callers can still
            # create directories/placeholders as needed.
            self.logger.exception(
                "download_sample_videos failed; continuing to execute")

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
            self.logger.warning("downloads.py not found at %s", p)
            return []

        spec = importlib.util.spec_from_file_location("_gen_downloads", str(p))
        if spec is None:
            self.logger.error("Unable to create spec for downloads.py")
            return []
        mod = importlib.util.module_from_spec(spec)
        # spec.loader may be None in static checkers, guard accordingly
        loader = getattr(spec, "loader", None)
        if loader is None:
            self.logger.error("Unable to load downloads.py (no loader)")
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
                    "invalid download entry in downloads.py: %r", entry)
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
            self.logger.debug(
                "temp dir exists and contains files; skipping downloads: %s", self.temp_dir)
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
                self.logger.info("skip download (exists): %s", dest)
                downloaded.append(dest)
                continue

            tmp = dest.with_suffix(dest.suffix + ".part")
            try:
                self.logger.info("downloading: %s -> %s", spec.url, dest)
                with urllib.request.urlopen(spec.url, timeout=60) as resp, open(tmp, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                tmp.replace(dest)
                downloaded.append(dest)
            except Exception:
                self.logger.exception("failed to download %s", spec.url)
                # create a small placeholder so subsequent steps can proceed
                if not dest.exists():
                    try:
                        dest.write_bytes(b"")
                        downloaded.append(dest)
                    except Exception:
                        self.logger.exception(
                            "failed to write placeholder for %s", dest)

        return downloaded
