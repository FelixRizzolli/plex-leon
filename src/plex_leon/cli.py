from __future__ import annotations

import argparse
from pathlib import Path

from .core import process_libraries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Move files and folders from library-a to library-c if their tvdb-id exists in library-b.",
    )
    parser.add_argument(
        "--lib-a", type=Path, default=Path("./data/library-a"), help="Path to library-a (default: ./data/library-a)"
    )
    parser.add_argument(
        "--lib-b", type=Path, default=Path("./data/library-b"), help="Path to library-b (default: ./data/library-b)"
    )
    parser.add_argument(
        "--lib-c", type=Path, default=Path("./data/library-c"), help="Path to library-c (default: ./data/library-c)"
    )
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing files in library-c")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be moved, but do not actually move files."
    )

    # Accept either None (use sys.argv) or an explicit list. If a list is provided
    # and the first element looks like a program name (doesn't start with '-'),
    # strip it to match argparse expectations.
    if argv is None:
        args = parser.parse_args()
    else:
        if argv and not argv[0].startswith("-"):
            argv = argv[1:]
        args = parser.parse_args(argv)

    moved, skipped = process_libraries(
        lib_a=args.lib_a, lib_b=args.lib_b, lib_c=args.lib_c, overwrite=args.overwrite, dry_run=args.dry_run
    )

    if moved or skipped:
        print(
            f"Done. Eligible files/folders moved: {moved}; skipped: {skipped}.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
