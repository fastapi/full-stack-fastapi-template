from __future__ import annotations

import base64
import hashlib
import os
import plistlib
import re
import subprocess
import sys

from functools import cached_property
from pathlib import Path
from subprocess import CalledProcessError
from typing import TYPE_CHECKING

import tomlkit
import virtualenv

from cleo.io.null_io import NullIO
from poetry.core.constraints.version import Version

from poetry.toml.file import TOMLFile
from poetry.utils._compat import WINDOWS
from poetry.utils._compat import encode
from poetry.utils.env.exceptions import EnvCommandError
from poetry.utils.env.exceptions import IncorrectEnvError
from poetry.utils.env.generic_env import GenericEnv
from poetry.utils.env.python import Python
from poetry.utils.env.python.exceptions import InvalidCurrentPythonVersionError
from poetry.utils.env.python.exceptions import NoCompatiblePythonVersionFoundError
from poetry.utils.env.python.exceptions import PythonVersionNotFoundError
from poetry.utils.env.script_strings import GET_ENV_PATH_ONELINER
from poetry.utils.env.script_strings import GET_PYTHON_VERSION_ONELINER
from poetry.utils.env.system_env import SystemEnv
from poetry.utils.env.virtual_env import VirtualEnv
from poetry.utils.helpers import get_real_windows_path
from poetry.utils.helpers import remove_directory


if TYPE_CHECKING:
    from cleo.io.io import IO

    from poetry.poetry import Poetry
    from poetry.utils.env.base_env import Env


class EnvsFile(TOMLFile):
    """
    This file contains one section per project with the project's base env name
    as section name. Each section contains the minor and patch version of the
    python executable used to create the currently active virtualenv.

    Example:

    [poetry-QRErDmmj]
    minor = "3.9"
    patch = "3.9.13"

    [poetry-core-m5r7DkRA]
    minor = "3.11"
    patch = "3.11.6"
    """

    def remove_section(self, name: str, minor: str | None = None) -> str | None:
        """
        Remove a section from the envs file.

        If "minor" is given, the section is only removed if its minor value
        matches "minor".

        Returns the "minor" value of the removed section.
        """
        envs = self.read()
        current_env = envs.get(name)
        if current_env is not None and (not minor or current_env["minor"] == minor):
            del envs[name]
            self.write(envs)
            minor = current_env["minor"]
            assert isinstance(minor, str)
            return minor

        return None


class EnvManager:
    """
    Environments manager
    """

    _env = None

    ENVS_FILE = "envs.toml"

    def __init__(self, poetry: Poetry, io: None | IO = None) -> None:
        self._poetry = poetry
        self._io = io or NullIO()

    @property
    def in_project_venv(self) -> Path:
        venv: Path = self._poetry.file.path.parent / ".venv"
        return venv

    @cached_property
    def envs_file(self) -> EnvsFile:
        return EnvsFile(self._poetry.config.virtualenvs_path / self.ENVS_FILE)

    @cached_property
    def base_env_name(self) -> str:
        return self.generate_env_name(
            self._poetry.package.name,
            str(self._poetry.file.path.parent),
        )

    def activate(self, python: str) -> Env:
        venv_path = self._poetry.config.virtualenvs_path

        python_instance = Python.get_by_name(python)
        if python_instance is None:
            raise PythonVersionNotFoundError(python)

        create = False
        # If we are required to create the virtual environment in the project directory,
        # create or recreate it if needed
        if self.use_in_project_venv():
            create = False
            venv = self.in_project_venv
            if venv.exists():
                # We need to check if the patch version is correct
                _venv = VirtualEnv(venv)
                current_patch = ".".join(str(v) for v in _venv.version_info[:3])

                if python_instance.patch_version.to_string() != current_patch:
                    create = True

            self.create_venv(python=python_instance, force=create)

            return self.get(reload=True)

        envs = tomlkit.document()
        if self.envs_file.exists():
            envs = self.envs_file.read()
            current_env = envs.get(self.base_env_name)
            if current_env is not None:
                current_minor = current_env["minor"]
                current_patch = current_env["patch"]

                if (
                    current_minor == python_instance.minor_version.to_string()
                    and current_patch != python_instance.patch_version.to_string()
                ):
                    # We need to recreate
                    create = True

        venv = (
            venv_path
            / f"{self.base_env_name}-py{python_instance.minor_version.to_string()}"
        )

        # Create if needed
        if not venv.exists() or create:
            in_venv = os.environ.get("VIRTUAL_ENV") is not None
            if in_venv or not venv.exists():
                create = True

            if venv.exists():
                # We need to check if the patch version is correct
                _venv = VirtualEnv(venv)
                current_patch = ".".join(str(v) for v in _venv.version_info[:3])

                if python_instance.patch_version.to_string() != current_patch:
                    create = True

            self.create_venv(python=python_instance, force=create)

        # Activate
        envs[self.base_env_name] = {
            "minor": python_instance.minor_version.to_string(),
            "patch": python_instance.patch_version.to_string(),
        }
        self.envs_file.write(envs)

        return self.get(reload=True)

    def deactivate(self) -> None:
        venv_path = self._poetry.config.virtualenvs_path

        if self.envs_file.exists() and (
            minor := self.envs_file.remove_section(self.base_env_name)
        ):
            venv = venv_path / f"{self.base_env_name}-py{minor}"
            self._io.write_error_line(
                f"Deactivating virtualenv: <comment>{venv}</comment>"
            )

    def get(self, reload: bool = False) -> Env:
        if self._env is not None and not reload:
            return self._env

        python_minor: str | None = None

        env = None
        envs = None
        if self.envs_file.exists():
            envs = self.envs_file.read()
            env = envs.get(self.base_env_name)
            if env:
                python_minor = env["minor"]

        # Check if we are inside a virtualenv or not
        # Conda sets CONDA_PREFIX in its envs, see
        # https://github.com/conda/conda/issues/2764
        env_prefix = os.environ.get("VIRTUAL_ENV", os.environ.get("CONDA_PREFIX"))
        conda_env_name = os.environ.get("CONDA_DEFAULT_ENV")
        # It's probably not a good idea to pollute Conda's global "base" env, since
        # most users have it activated all the time.
        in_venv = env_prefix is not None and conda_env_name != "base"

        if not in_venv or env is not None:
            # Checking if a local virtualenv exists
            if self.in_project_venv_exists():
                venv = self.in_project_venv

                return VirtualEnv(venv)

            create_venv = self._poetry.config.get("virtualenvs.create", True)

            if not create_venv:
                return self.get_system_env()

            venv_path = self._poetry.config.virtualenvs_path

            if python_minor is None:
                # we only need to discover python version in this case
                python = Python.get_preferred_python(
                    config=self._poetry.config, io=self._io
                )
                python_minor = python.minor_version.to_string()

            name = f"{self.base_env_name}-py{python_minor.strip()}"

            venv = venv_path / name

            if not venv.exists():
                if env and envs:
                    del envs[self.base_env_name]
                    self.envs_file.write(envs)
                return self.get_system_env()

            return VirtualEnv(venv)

        if env_prefix is not None:
            prefix = Path(env_prefix)
            base_prefix = None
        else:
            prefix = Path(sys.prefix)
            base_prefix = self.get_base_prefix()

        return VirtualEnv(prefix, base_prefix)

    def list(self, name: str | None = None) -> list[VirtualEnv]:
        if name is None:
            name = self._poetry.package.name

        venv_name = self.generate_env_name(name, str(self._poetry.file.path.parent))
        venv_path = self._poetry.config.virtualenvs_path
        env_list = [VirtualEnv(p) for p in sorted(venv_path.glob(f"{venv_name}-py*"))]

        if self.in_project_venv_exists():
            venv = self.in_project_venv
            env_list.insert(0, VirtualEnv(venv))
        return env_list

    @staticmethod
    def check_env_is_for_current_project(env: str, base_env_name: str) -> bool:
        """
        Check if env name starts with projects name.

        This is done to prevent action on other project's envs.
        """
        return env.startswith(base_env_name)

    def remove(self, python: str) -> Env:
        python_path = Path(python)
        if python_path.is_file():
            # Validate env name if provided env is a full path to python
            try:
                encoding = "locale" if sys.version_info >= (3, 10) else None
                env_dir = subprocess.check_output(
                    [python, "-c", GET_ENV_PATH_ONELINER], text=True, encoding=encoding
                ).strip("\n")
                env_name = Path(env_dir).name
                if not self.check_env_is_for_current_project(
                    env_name, self.base_env_name
                ):
                    raise IncorrectEnvError(env_name)
            except CalledProcessError as e:
                raise EnvCommandError(e)

        if self.check_env_is_for_current_project(python, self.base_env_name):
            venvs = self.list()
            for venv in venvs:
                if venv.path.name == python:
                    # Exact virtualenv name
                    if self.envs_file.exists():
                        venv_minor = ".".join(str(v) for v in venv.version_info[:2])
                        self.envs_file.remove_section(self.base_env_name, venv_minor)

                    self.remove_venv(venv.path)

                    return venv

            raise ValueError(
                f'<warning>Environment "{python}" does not exist.</warning>'
            )
        else:
            venv_path = self._poetry.config.virtualenvs_path
            # Get all the poetry envs, even for other projects
            env_names = [p.name for p in sorted(venv_path.glob("*-*-py*"))]
            if python in env_names:
                raise IncorrectEnvError(python)

        try:
            python_version = Version.parse(python)
            python = f"python{python_version.major}"
            if python_version.precision > 1:
                python += f".{python_version.minor}"
        except ValueError:
            # Executable in PATH or full executable path
            pass

        try:
            encoding = "locale" if sys.version_info >= (3, 10) else None
            python_version_string = subprocess.check_output(
                [python, "-c", GET_PYTHON_VERSION_ONELINER],
                text=True,
                encoding=encoding,
            )
        except CalledProcessError as e:
            raise EnvCommandError(e)

        python_version = Version.parse(python_version_string.strip())
        minor = f"{python_version.major}.{python_version.minor}"

        name = f"{self.base_env_name}-py{minor}"
        venv_path = venv_path / name

        if not venv_path.exists():
            raise ValueError(f'<warning>Environment "{name}" does not exist.</warning>')

        if self.envs_file.exists():
            self.envs_file.remove_section(self.base_env_name, minor)

        self.remove_venv(venv_path)

        return VirtualEnv(venv_path, venv_path)

    def use_in_project_venv(self) -> bool:
        in_project: bool | None = self._poetry.config.get("virtualenvs.in-project")
        if in_project is not None:
            return in_project

        return self.in_project_venv.is_dir()

    def in_project_venv_exists(self) -> bool:
        in_project: bool | None = self._poetry.config.get("virtualenvs.in-project")
        if in_project is False:
            return False

        return self.in_project_venv.is_dir()

    def create_venv(
        self,
        name: str | None = None,
        python: Python | None = None,
        force: bool = False,
    ) -> Env:
        if self._env is not None and not force:
            return self._env

        cwd = self._poetry.file.path.parent
        env = self.get(reload=True)

        if not env.is_sane():
            force = True

        if env.is_venv() and not force:
            # Already inside a virtualenv.
            current_python = Version.parse(
                ".".join(str(c) for c in env.version_info[:3])
            )
            if not self._poetry.package.python_constraint.allows(current_python):
                raise InvalidCurrentPythonVersionError(
                    self._poetry.package.python_versions, str(current_python)
                )
            return env

        create_venv = self._poetry.config.get("virtualenvs.create")
        in_project_venv = self.use_in_project_venv()
        use_poetry_python = self._poetry.config.get("virtualenvs.use-poetry-python")
        venv_prompt = self._poetry.config.get("virtualenvs.prompt")

        specific_python_requested = python is not None
        if not python:
            python = Python.get_preferred_python(
                config=self._poetry.config, io=self._io
            )

        venv_path = (
            self.in_project_venv
            if in_project_venv
            else self._poetry.config.virtualenvs_path
        )
        if not name:
            name = self._poetry.package.name

        supported_python = self._poetry.package.python_constraint
        if not supported_python.allows(python.patch_version):
            # The currently activated or chosen Python version
            # is not compatible with the Python constraint specified
            # for the project.
            # If an executable has been specified, we stop there
            # and notify the user of the incompatibility.
            # Otherwise, we try to find a compatible Python version.
            if specific_python_requested and use_poetry_python:
                raise NoCompatiblePythonVersionFoundError(
                    self._poetry.package.python_versions,
                    python.patch_version.to_string(),
                )

            self._io.write_error_line(
                f"<warning>The currently activated Python version {python.patch_version.to_string()} is not"
                f" supported by the project ({self._poetry.package.python_versions}).\n"
                "Trying to find and use a compatible version.</warning> "
            )

            python = Python.get_compatible_python(poetry=self._poetry, io=self._io)

        if in_project_venv:
            venv = venv_path
        else:
            name = self.generate_env_name(name, str(cwd))
            name = f"{name}-py{python.minor_version.to_string()}"
            venv = venv_path / name

        if venv_prompt is not None:
            venv_prompt = venv_prompt.format(
                project_name=self._poetry.package.name or "virtualenv",
                python_version=python.minor_version.to_string(),
            )

        if not venv.exists():
            if create_venv is False:
                self._io.write_error_line(
                    "<fg=black;bg=yellow>"
                    "Skipping virtualenv creation, "
                    "as specified in config file."
                    "</>"
                )

                return self.get_system_env()

            self._io.write_error_line(
                f"Creating virtualenv <c1>{name}</> in"
                f" {venv_path if not WINDOWS else get_real_windows_path(venv_path)!s}"
            )
        else:
            create_venv = False
            if force:
                if not env.is_sane():
                    self._io.write_error_line(
                        f"<warning>The virtual environment found in {env.path} seems to"
                        " be broken.</warning>"
                    )
                self._io.write_error_line(
                    f"Recreating virtualenv <c1>{name}</> in {venv!s}"
                )
                self.remove_venv(venv)
                create_venv = True
            elif self._io.is_very_verbose():
                self._io.write_error_line(f"Virtualenv <c1>{name}</> already exists.")

        if create_venv:
            self.build_venv(
                venv,
                executable=python.executable,
                flags=self._poetry.config.get("virtualenvs.options"),
                prompt=venv_prompt,
            )

        # venv detection:
        # stdlib venv may symlink sys.executable, so we can't use realpath.
        # but others can symlink *to* the venv Python,
        # so we can't just use sys.executable.
        # So we just check every item in the symlink tree (generally <= 3)
        p = os.path.normcase(sys.executable)
        paths = [p]
        while os.path.islink(p):
            p = os.path.normcase(os.path.join(os.path.dirname(p), os.readlink(p)))
            paths.append(p)

        p_venv = os.path.normcase(str(venv))
        if any(p.startswith(p_venv) for p in paths):
            # Running properly in the virtualenv, don't need to do anything
            return self.get_system_env()

        return VirtualEnv(venv)

    @classmethod
    def build_venv(
        cls,
        path: Path,
        executable: Path | None = None,
        flags: dict[str, str | bool] | None = None,
        with_pip: bool | None = None,
        prompt: str | None = None,
    ) -> virtualenv.run.session.Session:
        flags = flags or {}

        if with_pip is not None:
            flags["no-pip"] = not with_pip

        flags.setdefault("no-pip", True)
        flags.setdefault("no-setuptools", True)
        flags.setdefault("no-wheel", True)

        if WINDOWS:
            path = get_real_windows_path(path)
            executable = get_real_windows_path(executable) if executable else None

        executable_str = None if executable is None else executable.resolve().as_posix()

        args = [
            "--no-download",
            "--no-periodic-update",
            "--try-first-with",
            executable_str or sys.executable,
        ]

        if prompt is not None:
            args.extend(["--prompt", prompt])

        for flag, value in flags.items():
            if value is True:
                args.append(f"--{flag}")

            elif value is not False:
                args.append(f"--{flag}={value}")

        args.append(str(path))

        cli_result = virtualenv.cli_run(args, setup_logging=False)

        # Exclude the venv folder from from macOS Time Machine backups
        # TODO: Add backup-ignore markers for other platforms too
        if sys.platform == "darwin":
            import xattr

            xattr.setxattr(
                str(path),
                "com.apple.metadata:com_apple_backup_excludeItem",
                plistlib.dumps("com.apple.backupd", fmt=plistlib.FMT_BINARY),
            )

        return cli_result

    @classmethod
    def remove_venv(cls, path: Path) -> None:
        assert path.is_dir()
        try:
            remove_directory(path)
            return
        except OSError as e:
            # Continue only if e.errno == 16
            if e.errno != 16:  # ERRNO 16: Device or resource busy
                raise e

        # Delete all files and folders but the toplevel one. This is because sometimes
        # the venv folder is mounted by the OS, such as in a docker volume. In such
        # cases, an attempt to delete the folder itself will result in an `OSError`.
        # See https://github.com/python-poetry/poetry/pull/2064
        for file_path in path.iterdir():
            if file_path.is_file() or file_path.is_symlink():
                file_path.unlink()
            elif file_path.is_dir():
                remove_directory(file_path, force=True)

    @classmethod
    def get_system_env(cls, naive: bool = False) -> Env:
        """
        Retrieve the current Python environment.

        This can be the base Python environment or an activated virtual environment.

        This method also workaround the issue that the virtual environment
        used by Poetry internally (when installed via the custom installer)
        is incorrectly detected as the system environment. Note that this workaround
        happens only when `naive` is False since there are times where we actually
        want to retrieve Poetry's custom virtual environment
        (e.g. plugin installation or self update).
        """
        prefix, base_prefix = Path(sys.prefix), Path(cls.get_base_prefix())
        env: Env = SystemEnv(prefix)
        if not naive:
            env = GenericEnv(base_prefix, child_env=env)

        return env

    @classmethod
    def get_base_prefix(cls) -> Path:
        real_prefix = getattr(sys, "real_prefix", None)
        if real_prefix is not None:
            return Path(real_prefix)

        base_prefix = getattr(sys, "base_prefix", None)
        if base_prefix is not None:
            return Path(base_prefix)

        return Path(sys.prefix)

    @classmethod
    def generate_env_name(cls, name: str, cwd: str) -> str:
        name = name.lower()
        sanitized_name = re.sub(r'[ $`!*@"\\\r\n\t]', "_", name)[:42]
        normalized_cwd = os.path.normcase(os.path.realpath(cwd))
        h_bytes = hashlib.sha256(encode(normalized_cwd)).digest()
        h_str = base64.urlsafe_b64encode(h_bytes).decode()[:8]

        return f"{sanitized_name}-{h_str}"
