from __future__ import annotations

import subprocess

from typing import TYPE_CHECKING

from poetry.core.vcs.git import Git


if TYPE_CHECKING:
    from pathlib import Path


def get_vcs(directory: Path) -> Git | None:
    directory = directory.resolve(strict=True)
    vcs: Git | None

    try:
        from poetry.core.vcs.git import executable

        check_ignore = subprocess.run(
            [executable(), "check-ignore", "."],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            cwd=directory,
        ).returncode

        if check_ignore == 0:
            vcs = None
        else:
            rel_path_to_git_dir = subprocess.check_output(
                [executable(), "rev-parse", "--show-cdup"],
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                cwd=directory,
            ).strip()

            vcs = Git((directory / rel_path_to_git_dir).resolve())

    except (subprocess.CalledProcessError, OSError, RuntimeError):
        vcs = None

    return vcs
