from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import process_libraries
from .utils import assert_required_tools_installed


def _add_migrate_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "migrate",
        help="Move items from library-a to library-c when their TVDB ID exists in library-b.",
        description="Move files and folders from library-a to library-c if their tvdb-id exists in library-b.",
    )
    p.add_argument(
        "--lib-a", type=Path, default=Path("./data/library-a"), help="Path to library-a (default: ./data/library-a)"
    )
    p.add_argument(
        "--lib-b", type=Path, default=Path("./data/library-b"), help="Path to library-b (default: ./data/library-b)"
    )
    p.add_argument(
        "--lib-c", type=Path, default=Path("./data/library-c"), help="Path to library-c (default: ./data/library-c)"
    )
    p.add_argument("--overwrite", action="store_true",
                   help="Overwrite existing files in library-c")
    p.add_argument(
        "--dry-run", action="store_true", help="Show what would be moved, but do not actually move files."
    )
    return p


def _add_stub_parser(subparsers: argparse._SubParsersAction, name: str, help_text: str) -> None:
    subparsers.add_parser(name, help=help_text, description=help_text)


def main(argv: list[str] | None = None) -> int:
    # Build top-level parser with subcommands
    parser = argparse.ArgumentParser(
        prog="plex-leon",
        description="Utilities for managing media libraries based on TVDB IDs.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Subcommands
    _add_migrate_parser(subparsers)
    _add_stub_parser(subparsers, "season-renamer",
                     "Rename seasons (not implemented yet)")
    _add_stub_parser(subparsers, "episode-renamer",
                     "Rename episodes (not implemented yet)")
    _add_stub_parser(subparsers, "episode-check",
                     "Check episodes (not implemented yet)")

    # Prepare argv with backward compatibility:
    # - If argv is provided and its first element is a program name, drop it.
    # - If no subcommand is provided (first token starts with '-'), default to 'migrate'.
    if argv is None:
        parsed_argv = sys.argv[1:]
    else:
        parsed_argv = list(argv)

    if parsed_argv and not parsed_argv[0].startswith("-") and parsed_argv[0] not in {
        "migrate",
        "season-renamer",
        "episode-renamer",
        "episode-check",
    }:
        # Drop program name
        parsed_argv = parsed_argv[1:]

    if not parsed_argv or parsed_argv[0].startswith("-"):
        # Default to migrate subcommand for backward compatibility
        parsed_argv = ["migrate", *parsed_argv]

    args = parser.parse_args(parsed_argv)

    # Route to subcommands
    if args.command == "migrate":
        # Preflight: ensure required external tools are available
        try:
            assert_required_tools_installed()
        except RuntimeError as exc:
            print(f"ERROR: {exc}")
            return 2

        moved, skipped = process_libraries(
            lib_a=args.lib_a,
            lib_b=args.lib_b,
            lib_c=args.lib_c,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        if moved or skipped:
            print(
                f"Done. Eligible files/folders moved: {moved}; skipped: {skipped}.")
        return 0

    if args.command in {"season-renamer", "episode-renamer", "episode-check"}:
        print(f"'{args.command}' is not implemented yet.")
        return 0

    # Unknown or missing command (shouldn't happen due to defaulting)
    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
