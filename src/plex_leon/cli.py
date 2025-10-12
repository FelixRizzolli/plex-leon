from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .utils.migrate import process_libraries
from .shared import assert_required_tools_installed
from .utils.season_renamer import process_library as season_process_library
from .utils.episode_renamer import process_library as episode_process_library
from .utils.prepare import process as prepare_process


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
    p.add_argument(
        "--threads", type=int, default=None, help="Optional thread count for metadata reads (I/O bound)."
    )
    p.add_argument(
        "--no-resolution", action="store_true", help="Skip resolution comparisons to speed up large runs."
    )
    return p


def _add_stub_parser(subparsers: argparse._SubParsersAction, name: str, help_text: str) -> None:
    subparsers.add_parser(name, help=help_text, description=help_text)


def _add_season_renamer_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "season-renamer",
        help="Rename season folders like 'season 01' or 'Staffel 01' to 'Season 01'",
        description=(
            "Rename season folders in a library to the canonical 'Season NN' form. "
            "Matches any folder name with exactly one number (e.g., typos like 'Satffel 01')."
        ),
    )
    p.add_argument(
        "--lib", type=Path, default=Path("./data/library-s"), help="Path to the library to process (default: ./data/library-s)"
    )
    p.add_argument(
        "--dry-run", action="store_true", help="Show planned renames without changing the filesystem."
    )
    return p


def _add_episode_renamer_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "episode-renamer",
        help="Rename episode files to '<Show (Year)> - sNNeMM[ -ePP].ext' using the show folder name.",
        description=(
            "Rename episode files under a library so the basename is derived from the show folder title "
            "and the episode id extracted from the file (supports SxxExx and double episodes)."
        ),
    )
    p.add_argument(
        "--lib", type=Path, default=Path("./data/library-e"), help="Path to the library to process (default: ./data/library-e)"
    )
    p.add_argument(
        "--dry-run", action="store_true", help="Show planned renames without changing the filesystem."
    )
    return p


def _add_prepare_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "prepare",
        help="Prepare a library by moving loose episode files into Season folders and renaming them",
        description=(
            "Scan a root folder for TV show folders named 'Title (YYYY) {tvdb-#}' and "
            "move/rename loose episode files into 'Season NN' folders."
        ),
    )
    p.add_argument(
        "--lib",
        type=Path,
        default=Path("./data/library-p"),
        help="Path to the library to process (default: ./data/library-p)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned moves/renames without changing the filesystem.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    # Build top-level parser with subcommands
    parser = argparse.ArgumentParser(
        prog="plex-leon",
        description="Utilities for managing media libraries based on TVDB IDs.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Subcommands
    _add_migrate_parser(subparsers)
    _add_season_renamer_parser(subparsers)
    _add_episode_renamer_parser(subparsers)
    _add_prepare_parser(subparsers)
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
        "prepare",
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
            print(f"❌ ERROR: {exc}")
            return 2

        t0 = time.perf_counter()
        moved, skipped = process_libraries(
            lib_a=args.lib_a,
            lib_b=args.lib_b,
            lib_c=args.lib_c,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            prefer_resolution=not args.no_resolution,
            threads=args.threads,
        )
        dt = time.perf_counter() - t0
        if moved or skipped:
            print(
                f"Done. Eligible files/folders moved: {moved}; skipped: {skipped}. Took {dt:.2f}s."
            )
        return 0

    if args.command == "season-renamer":
        t0 = time.perf_counter()
        renamed_count, = season_process_library(args.lib, args.dry_run)
        dt = time.perf_counter() - t0
        print(
            f"Done. Season folders renamed: {renamed_count}. Took {dt:.2f}s.")
        return 0

    if args.command == "prepare":
        t0 = time.perf_counter()
        renamed_count, = prepare_process(args.lib, args.dry_run)
        dt = time.perf_counter() - t0
        print(f"Done. Episodes processed: {renamed_count}. Took {dt:.2f}s.")
        return 0

    if args.command == "episode-renamer":
        t0 = time.perf_counter()
        renamed_count, = episode_process_library(args.lib, args.dry_run)
        dt = time.perf_counter() - t0
        print(f"Done. Episode files renamed: {renamed_count}. Took {dt:.2f}s.")
        return 0

    if args.command in {"episode-check"}:
        print(f"'{args.command}' is not implemented yet.")
        return 0

    # Unknown or missing command (shouldn't happen due to defaulting)
    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
