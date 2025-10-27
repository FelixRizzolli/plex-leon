import os
import sys
from pathlib import Path


def main(argv=None):
    """Run pytest with coverage to generate html, xml, json and lcov reports under data/coverage.

    This function is intended to be installed as a console script entry point in Poetry.
    """
    argv = list(argv or sys.argv[1:])

    # Ensure output directory exists
    out_dir = Path("data/coverage")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build pytest args. Allow passing extra pytest args via argv.
    # We'll run tests under the default test paths; if user passes args, append them.
    base_args = [
        "--cov=src",
        "--cov-report=html:data/coverage/html",
        "--cov-report=xml:data/coverage/coverage.xml",
        "--cov-report=json:data/coverage/coverage.json",
        "--cov-report=lcov:data/coverage/coverage.lcov",
    ]

    # If user provided paths/args, use them after our options, otherwise default to running pytest normally
    if argv:
        final_args = base_args + argv
    else:
        final_args = base_args + ["tests"]

    # Import here to avoid bringing pytest into module import time if not needed
    try:
        import pytest
    except Exception as exc:  # pragma: no cover - runtime/environmental
        print("Error: pytest is not available in the environment:",
              exc, file=sys.stderr)
        return 2

    print("Running pytest with coverage. Output directory:", out_dir)
    return pytest.main(final_args)


if __name__ == "__main__":
    raise SystemExit(main())
