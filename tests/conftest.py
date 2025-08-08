"""Pytest configuration.

Ensures the tests directory is on sys.path so imports like
`from utils import make_files` resolve correctly during test collection.
"""
from __future__ import annotations

import sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent.resolve()
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
