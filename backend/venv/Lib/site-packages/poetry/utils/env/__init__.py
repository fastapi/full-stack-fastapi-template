from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from poetry.core.utils.helpers import temporary_directory

from poetry.utils.env.base_env import Env
from poetry.utils.env.env_manager import EnvManager
from poetry.utils.env.exceptions import EnvCommandError
from poetry.utils.env.exceptions import EnvError
from poetry.utils.env.exceptions import IncorrectEnvError
from poetry.utils.env.generic_env import GenericEnv
from poetry.utils.env.mock_env import MockEnv
from poetry.utils.env.null_env import NullEnv
from poetry.utils.env.script_strings import GET_BASE_PREFIX
from poetry.utils.env.script_strings import GET_ENV_PATH_ONELINER
from poetry.utils.env.script_strings import GET_ENVIRONMENT_INFO
from poetry.utils.env.script_strings import GET_PATHS
from poetry.utils.env.script_strings import GET_PYTHON_VERSION_ONELINER
from poetry.utils.env.script_strings import GET_SYS_PATH
from poetry.utils.env.site_packages import SitePackages
from poetry.utils.env.system_env import SystemEnv
from poetry.utils.env.virtual_env import VirtualEnv


if TYPE_CHECKING:
    from collections.abc import Iterator

    from cleo.io.io import IO

    from poetry.poetry import Poetry


@contextmanager
def ephemeral_environment(
    executable: Path | None = None,
    flags: dict[str, str | bool] | None = None,
) -> Iterator[VirtualEnv]:
    with temporary_directory() as tmp_dir:
        # TODO: cache PEP 517 build environment corresponding to each project venv
        venv_dir = Path(tmp_dir) / ".venv"
        EnvManager.build_venv(
            path=venv_dir,
            executable=executable,
            flags=flags,
        )
        yield VirtualEnv(venv_dir, venv_dir)


@contextmanager
def build_environment(
    poetry: Poetry, env: Env | None = None, io: IO | None = None
) -> Iterator[Env]:
    """
    If a build script is specified for the project, there could be additional build
    time dependencies, eg: cython, setuptools etc. In these cases, we create an
    ephemeral build environment with all requirements specified under
    `build-system.requires` and return this. Otherwise, the given default project
    environment is returned.
    """
    if not env or poetry.package.build_script:
        with ephemeral_environment(
            executable=env.python if env else None,
            flags={"no-pip": True},
        ) as venv:
            if io:
                requires = [
                    f"<c1>{requirement}</c1>"
                    for requirement in poetry.pyproject.build_system.requires
                ]

                io.write_error_line(
                    "<b>Preparing</b> build environment with build-system requirements"
                    f" {', '.join(requires)}"
                )

            from poetry.utils.isolated_build import IsolatedEnv

            isolated_env = IsolatedEnv(venv, poetry.pool)
            isolated_env.install(poetry.pyproject.build_system.requires)

            yield venv
    else:
        yield env


__all__ = [
    "GET_BASE_PREFIX",
    "GET_ENVIRONMENT_INFO",
    "GET_ENV_PATH_ONELINER",
    "GET_PATHS",
    "GET_PYTHON_VERSION_ONELINER",
    "GET_SYS_PATH",
    "Env",
    "EnvCommandError",
    "EnvError",
    "EnvManager",
    "GenericEnv",
    "IncorrectEnvError",
    "MockEnv",
    "NullEnv",
    "SitePackages",
    "SystemEnv",
    "VirtualEnv",
    "build_environment",
    "ephemeral_environment",
]
