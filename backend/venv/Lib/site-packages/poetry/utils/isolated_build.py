from __future__ import annotations

import os
import subprocess

from contextlib import contextmanager
from contextlib import redirect_stdout
from io import StringIO
from typing import TYPE_CHECKING

from build import BuildBackendException
from build.env import IsolatedEnv as BaseIsolatedEnv

from poetry.utils._compat import decode
from poetry.utils.env import Env
from poetry.utils.env import EnvManager
from poetry.utils.env import ephemeral_environment


if TYPE_CHECKING:
    from collections.abc import Collection
    from collections.abc import Iterator
    from pathlib import Path

    from build import DistributionType
    from build import ProjectBuilder

    from poetry.repositories import RepositoryPool


class IsolatedBuildBaseError(Exception): ...


class IsolatedBuildBackendError(IsolatedBuildBaseError):
    def __init__(self, source: Path, exception: BuildBackendException) -> None:
        super().__init__()
        self.source = source
        self.exception = exception

    def generate_message(
        self, source_string: str | None = None, build_command: str | None = None
    ) -> str:
        e = self.exception.exception
        source_string = source_string or self.source.as_posix()
        build_command = (
            build_command
            or f'pip wheel --no-cache-dir --use-pep517 "{self.source.as_posix()}"'
        )

        reasons = ["PEP517 build of a dependency failed", str(self.exception)]

        if isinstance(e, subprocess.CalledProcessError):
            inner_traceback = decode(e.stderr or e.stdout or e.output).strip()
            inner_reason = "\n    | ".join(
                ["", str(e), "", *inner_traceback.split("\n")]
            ).lstrip("\n")
            reasons.append(f"<warning>{inner_reason}</warning>")

        reasons.append(
            "<info>"
            "<options=bold>Note:</> This error originates from the build backend, and is likely not a "
            f"problem with poetry but one of the following issues with {source_string}\n\n"
            "  - not supporting PEP 517 builds\n"
            "  - not specifying PEP 517 build requirements correctly\n"
            "  - the build requirements are incompatible with your operating system or Python version\n"
            "  - the build requirements are missing system dependencies (eg: compilers, libraries, headers).\n\n"
            f"You can verify this by running <c1>{build_command}</c1>."
            "</info>"
        )

        return "\n\n".join(reasons)

    def __str__(self) -> str:
        return self.generate_message()


class IsolatedBuildInstallError(IsolatedBuildBaseError):
    def __init__(self, requirements: Collection[str], output: str, error: str) -> None:
        message = "\n\n".join(
            (
                f"Failed to install {', '.join(requirements)}.",
                f"Output:\n{output}",
                f"Error:\n{error}",
            )
        )
        super().__init__(message)
        self._requirements = requirements

    @property
    def requirements(self) -> Collection[str]:
        return self._requirements


class IsolatedEnv(BaseIsolatedEnv):
    def __init__(self, env: Env, pool: RepositoryPool) -> None:
        self._env = env
        self._pool = pool

    @property
    def python_executable(self) -> str:
        return str(self._env.python)

    def make_extra_environ(self) -> dict[str, str]:
        path = os.environ.get("PATH")
        scripts_dir = str(self._env._bin_dir)
        return {
            "PATH": (
                os.pathsep.join([scripts_dir, path])
                if path is not None
                else scripts_dir
            )
        }

    def install(self, requirements: Collection[str]) -> None:
        from cleo.io.buffered_io import BufferedIO
        from poetry.core.packages.dependency import Dependency
        from poetry.core.packages.project_package import ProjectPackage

        from poetry.config.config import Config
        from poetry.installation.installer import Installer
        from poetry.packages.locker import Locker
        from poetry.repositories.installed_repository import InstalledRepository

        # We build Poetry dependencies from the requirements
        package = ProjectPackage("__root__", "0.0.0")
        package.python_versions = ".".join(str(v) for v in self._env.version_info[:3])
        env_markers = self._env.get_marker_env()

        for requirement in requirements:
            dependency = Dependency.create_from_pep_508(requirement)

            if dependency.marker.is_empty() or dependency.marker.validate(env_markers):
                # we ignore dependencies that are not valid for this environment
                # this ensures that we do not end up with unnecessary constraint
                # errors when solving build system requirements; this is assumed
                # safe as this environment is ephemeral
                package.add_dependency(dependency)

        io = BufferedIO()

        installer = Installer(
            io,
            self._env,
            package,
            Locker(self._env.path.joinpath("poetry.lock"), {}),
            self._pool,
            Config.create(),
            InstalledRepository.load(self._env),
        )
        installer.update(True)

        if installer.run() != 0:
            raise IsolatedBuildInstallError(
                requirements, io.fetch_output(), io.fetch_error()
            )


@contextmanager
def isolated_builder(
    source: Path,
    distribution: DistributionType = "wheel",
    python_executable: Path | None = None,
    pool: RepositoryPool | None = None,
) -> Iterator[ProjectBuilder]:
    from build import ProjectBuilder
    from pyproject_hooks import quiet_subprocess_runner

    from poetry.factory import Factory

    try:
        # we recreate the project's Poetry instance in order to retrieve the correct repository pool
        # when a pool is not provided
        pool = pool or Factory().create_poetry().pool
    except RuntimeError:
        # the context manager is not being called within a Poetry project context
        # fallback to a default pool using only PyPI as source
        from poetry.repositories import RepositoryPool
        from poetry.repositories.pypi_repository import PyPiRepository

        # fallback to using only PyPI
        pool = RepositoryPool(repositories=[PyPiRepository()])

    python_executable = (
        python_executable or EnvManager.get_system_env(naive=True).python
    )

    with ephemeral_environment(
        executable=python_executable,
        flags={"no-pip": True},
    ) as venv:
        env = IsolatedEnv(venv, pool)
        stdout = StringIO()
        try:
            builder = ProjectBuilder.from_isolated_env(
                env, source, runner=quiet_subprocess_runner
            )

            with redirect_stdout(stdout):
                env.install(builder.build_system_requires)

                # we repeat the build system requirements to avoid poetry installer from removing them
                env.install(
                    builder.build_system_requires
                    | builder.get_requires_for_build(distribution)
                )

                yield builder
        except BuildBackendException as e:
            raise IsolatedBuildBackendError(source, e) from None
