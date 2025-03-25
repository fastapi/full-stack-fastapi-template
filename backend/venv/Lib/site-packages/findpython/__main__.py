from __future__ import annotations

import logging
import sys
from argparse import ArgumentParser

from findpython import Finder
from findpython.__version__ import __version__

logger = logging.getLogger("findpython")


def setup_logger(level: int = logging.DEBUG) -> None:
    """
    Setup the logger.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(name)s-%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level)


def split_str(value: str) -> list[str]:
    return value.split(",")


def cli(argv: list[str] | None = None) -> int:
    """
    Command line interface for findpython.
    """
    parser = ArgumentParser(
        "findpython", description="A utility to find python versions on your system"
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-a", "--all", action="store_true", help="Show all matching python versions"
    )
    parser.add_argument(
        "--resolve-symlink", action="store_true", help="Resolve all symlinks"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--no-same-file",
        action="store_true",
        help="Eliminate the duplicated results with the same file contents",
    )
    parser.add_argument(
        "--no-same-python",
        action="store_true",
        help="Eliminate the duplicated results with the same sys.executable",
    )
    parser.add_argument(
        "--pre", "--prereleases", action="store_true", help="Allow prereleases"
    )
    parser.add_argument("--providers", type=split_str, help="Select provider(s) to use")
    parser.add_argument("version_spec", nargs="?", help="Python version spec or name")

    args = parser.parse_args(argv)
    if args.verbose:
        setup_logger()

    finder = Finder(
        resolve_symlinks=args.resolve_symlink,
        no_same_file=args.no_same_file,
        selected_providers=args.providers,
    )
    if args.all:
        find_func = finder.find_all
    else:
        find_func = finder.find  # type: ignore[assignment]

    python_versions = find_func(args.version_spec, allow_prereleases=args.pre)
    if not python_versions:
        print("No matching python version found", file=sys.stderr)
        return 1
    if not isinstance(python_versions, list):
        python_versions = [python_versions]
    print("Found matching python versions:", file=sys.stderr)
    for python_version in python_versions:
        print(python_version)
    return 0


def main() -> None:
    """
    Main function.
    """
    sys.exit(cli())


if __name__ == "__main__":
    main()
