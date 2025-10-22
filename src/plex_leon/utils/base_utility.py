from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import sys
from typing import Any
from typing import Union

from loguru import logger


@dataclass
class BaseOptions:
    dry_run: bool = False
    forced: bool = False
    # Accept numeric or human-readable log level (e.g. 20 or "info")
    log_level: Union[int, str] = 20  # similar to logging.INFO


class BaseUtility(ABC):
    """Base class for utilities.

    Provides simple logging helpers and a run() entrypoint that calls the
    concrete implementation's process() method.
    """

    def __init__(self, *, dry_run: bool = False, forced: bool = False, log_level: Union[int, str] = 20) -> None:
        self.opts = BaseOptions(
            dry_run=dry_run, forced=forced, log_level=log_level)

        # Configure loguru once per process. The first BaseUtility created
        # will set a stderr sink with the provided level. Subsequent
        # instances won't add duplicate sinks.
        if not getattr(logger, "_plex_leon_configured", False):
            logger.remove()
            # normalize the level (accept strings like "debug", "INFO", or numeric values)
            level = self._normalize_level(self.log_level)
            logger.add(sys.stderr, level=level)
            setattr(logger, "_plex_leon_configured", True)

    # Convenience properties
    @property
    def dry_run(self) -> bool:
        return self.opts.dry_run

    @property
    def forced(self) -> bool:
        return self.opts.forced

    @property
    def log_level(self) -> int:
        return self.opts.log_level

    def _normalize_level(self, level: int | str) -> int | str:
        """Normalize a human-friendly level to something loguru accepts.

        Accepts numeric levels (passed through) or common strings like
        'debug', 'INFO', 'Trace', etc. Returns either an int or upper-case
        level name string that loguru accepts.
        """
        if isinstance(level, int):
            return level
        if not isinstance(level, str):
            raise TypeError("log_level must be int or str")
        name = level.strip().upper()
        # Allow common synonyms and lowercase inputs
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
        # always print errors to stderr
        # keep the existing visual prefix; loguru emits to stderr by default
        logger.error(f"❌ ERROR: {msg}")

    def log_warning(self, msg: str, /) -> None:
        logger.warning(f"⚠️ WARN: {msg}")

    def log_info(self, msg: str, /) -> None:
        logger.info(f"ℹ️ {msg}")

    def log_debug(self, msg: str, /) -> None:
        logger.debug(f"🐛 DEBUG: {msg}")

    def log_verbose(self, msg: str, /) -> None:
        # use trace for very low-level verbose output (loguru level 5)
        logger.trace(f"🔍 VERBOSE: {msg}")

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the utility.

        Delegates to the concrete process() implementation. Subclasses must
        implement process(). The run method provides a stable entrypoint and
        ensures dry-run option is available on the instance.
        """
        try:
            return self.process(*args, **kwargs)
        except Exception as e:
            # surface exceptions as logged errors and re-raise
            self.log_error(str(e))
            raise

    @abstractmethod
    def process(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()
