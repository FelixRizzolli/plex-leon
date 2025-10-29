"""
Script to extract changelog entries for a specific version from CHANGELOG.md.
"""

import re
import sys
from pathlib import Path


def get_changes(version: str, changelog_path: Path | None = None) -> str:
    """
    Extract the changelog entry for a specific version from CHANGELOG.md.

    Args:
        version: The version to extract (e.g., "3.0.0")
        changelog_path: Optional path to CHANGELOG.md. If None, uses the default location.

    Returns:
        The changelog content for the specified version, including the version header.
        Returns an empty string if the version is not found.

    Raises:
        FileNotFoundError: If the CHANGELOG.md file doesn't exist.
    """
    if changelog_path is None:
        # Default to the workspace root's CHANGELOG.md
        changelog_path = Path(__file__).parent.parent.parent / "CHANGELOG.md"

    if not changelog_path.exists():
        raise FileNotFoundError(f"CHANGELOG.md not found at {changelog_path}")

    content = changelog_path.read_text(encoding="utf-8")

    # Pattern to match version headers like ## [3.0.0] - 2025-10-28
    version_pattern = re.compile(
        rf"^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$",
        re.MULTILINE
    )

    match = version_pattern.search(content)
    if not match:
        return ""

    # Start after the version header line (skip the headline)
    start_pos = match.end() + 1  # +1 to skip the newline after the header

    # Find the next version header (or end of file)
    next_version_pattern = re.compile(r"^## \[\d+\.\d+\.\d+\]", re.MULTILINE)
    next_match = next_version_pattern.search(content, match.end())

    if next_match:
        end_pos = next_match.start()
    else:
        end_pos = len(content)

    # Extract the section and strip leading/trailing whitespace
    section = content[start_pos:end_pos].strip()

    return section


def main():
    """CLI entry point for the get_changes script."""
    if len(sys.argv) != 2:
        print("Usage: python get_changes.py <version>", file=sys.stderr)
        print("Example: python get_changes.py 3.0.0", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]

    try:
        changes = get_changes(version)
        if changes:
            print(changes)
        else:
            print(
                f"Version {version} not found in CHANGELOG.md", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
