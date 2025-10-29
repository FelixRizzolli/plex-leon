"""
Script to extract the current version from pyproject.toml.
"""

import re
import sys
from pathlib import Path


def get_current_version(pyproject_path: Path | None = None) -> str:
    """
    Extract the current version from pyproject.toml.

    Args:
        pyproject_path: Optional path to pyproject.toml. If None, uses the default location.

    Returns:
        The version string (e.g., "3.0.1").

    Raises:
        FileNotFoundError: If the pyproject.toml file doesn't exist.
        ValueError: If the version field is not found in pyproject.toml.
    """
    if pyproject_path is None:
        # Default to the workspace root's pyproject.toml
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

    if not pyproject_path.exists():
        raise FileNotFoundError(
            f"pyproject.toml not found at {pyproject_path}")

    content = pyproject_path.read_text(encoding="utf-8")

    # Pattern to match version = "3.0.1" in the [project] section
    version_pattern = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)

    match = version_pattern.search(content)
    if not match:
        raise ValueError("Version field not found in pyproject.toml")

    return match.group(1)


def main():
    """CLI entry point for the get_current_version script."""
    try:
        version = get_current_version()
        print(version)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
