
"""Top-level package for plex_leon.

Keep the package __init__ intentionally minimal to avoid circular import
issues when submodules (like ``plex_leon.shared``) are imported. Heavy
imports should be performed by callers from submodules directly, e.g.
``from plex_leon.shared import parse_episode_tag`` or
``from plex_leon.cli import main``.
"""

__all__ = []
