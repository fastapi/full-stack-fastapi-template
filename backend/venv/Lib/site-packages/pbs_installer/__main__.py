from __future__ import annotations

import logging
from argparse import SUPPRESS, Action, ArgumentParser, Namespace
from collections.abc import Sequence
from typing import Any

from ._install import install
from ._utils import get_available_arch_platforms


def _setup_logger(verbose: bool) -> None:
    logger = logging.getLogger("pbs_installer")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)


class ListAction(Action):
    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str = SUPPRESS,
        default: Any = SUPPRESS,
        help: str | None = None,
    ) -> None:
        super().__init__(
            option_strings=option_strings, dest=dest, nargs=0, default=default, help=help
        )

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        self.list_versions()
        parser.exit()

    def list_versions(self) -> None:
        from ._versions import PYTHON_VERSIONS

        for version in PYTHON_VERSIONS:
            print(f"- {version}")


def main() -> None:
    archs, platforms = get_available_arch_platforms()
    parser = ArgumentParser("pbs-install", description="Installer for Python Build Standalone")
    install_group = parser.add_argument_group("Install Arguments")
    install_group.add_argument(
        "version", help="The version of Python to install, e.g. 3.8, 3.10.4, pypy@3.10"
    )
    install_group.add_argument(
        "--version-dir", help="Install to a subdirectory named by the version", action="store_true"
    )
    install_group.add_argument(
        "--build-dir", help="Include the build directory", action="store_true"
    )
    install_group.add_argument(
        "-d", "--destination", help="The directory to install to", required=True
    )
    install_group.add_argument("--arch", choices=archs, help="Override the architecture to install")
    install_group.add_argument(
        "--platform", choices=platforms, help="Override the platform to install"
    )
    parser.add_argument("-v", "--verbose", help="Enable verbose logging", action="store_true")
    parser.add_argument("-l", "--list", action=ListAction, help="List installable versions")

    args = parser.parse_args()
    _setup_logger(args.verbose)
    impl, has_amp, version = args.version.rpartition("@")
    if not has_amp:
        impl = "cpython"
    install(
        version,
        args.destination,
        version_dir=args.version_dir,
        arch=args.arch,
        platform=args.platform,
        implementation=impl,
        build_dir=args.build_dir,
    )
    print("Done!")


if __name__ == "__main__":
    main()
