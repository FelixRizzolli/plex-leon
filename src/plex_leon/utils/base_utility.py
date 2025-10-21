from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import sys
from typing import Any


@dataclass
class BaseOptions:
    dry_run: bool = False
    forced: bool = False
    log_level: int = 20  # similar to logging.INFO


class BaseUtility(ABC):
    """Base class for utilities.

    Provides simple logging helpers and a run() entrypoint that calls the
    concrete implementation's process() method.
    """

    def __init__(self, *, dry_run: bool = False, forced: bool = False, log_level: int = 20) -> None:
        self.opts = BaseOptions(
            dry_run=dry_run, forced=forced, log_level=log_level)

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

    # Logging helpers. log_level semantics: lower number = more verbose
    def _should_log(self, level: int) -> bool:
        return level >= self.log_level

    def log_error(self, msg: str, /) -> None:
        # always print errors to stderr
        print(f"❌ ERROR: {msg}", file=sys.stderr)

    def log_warning(self, msg: str, /) -> None:
        if self._should_log(30):
            print(f"⚠️ WARN: {msg}")

    def log_info(self, msg: str, /) -> None:
        if self._should_log(20):
            print(f"ℹ️ {msg}")

    def log_debug(self, msg: str, /) -> None:
        if self._should_log(10):
            print(f"🐛 DEBUG: {msg}")

    def log_verbose(self, msg: str, /) -> None:
        if self._should_log(5):
            print(f"🔍 VERBOSE: {msg}")

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
