"""Test package setup for src/ layout.

Ensures that the project `src` directory is on sys.path so tests can
import the `plex_leon` package without installing it.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))
