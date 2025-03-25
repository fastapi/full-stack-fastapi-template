from __future__ import annotations

import contextlib
import os
import re
import subprocess
import sys
import sysconfig

from abc import ABC
from abc import abstractmethod
from functools import cached_property
from pathlib import Path
from subprocess import CalledProcessError
from typing import TYPE_CHECKING
from typing import Any

from installer.utils import SCHEME_NAMES
from virtualenv.seed.wheels.embed import get_embed_wheel

from poetry.utils.env.exceptions import EnvCommandError
from poetry.utils.env.site_packages import SitePackages
from poetry.utils.helpers import get_real_windows_path
from poetry.utils.helpers import is_dir_writable


if TYPE_CHECKING:
    from packaging.tags import Tag
    from poetry.core.version.markers import BaseMarker
    from virtualenv.seed.wheels.util import Wheel

    from poetry.utils.env.generic_env import GenericEnv

    PythonVersion = tuple[int, int, int, str, int]


class Env(ABC):
    """
    An abstract Python environment.
    """

    def __init__(self, path: Path, base: Path | None = None) -> None:
        self._is_windows = sys.platform == "win32"
        self._is_mingw = sysconfig.get_platform().startswith("mingw")
        self._is_conda = bool(os.environ.get("CONDA_DEFAULT_ENV"))

        if self._is_windows:
            path = get_real_windows_path(path)
            base = get_real_windows_path(base) if base else None

        bin_dir = "bin" if not self._is_windows or self._is_mingw else "Scripts"
        self._path = path
        self._bin_dir = self._path / bin_dir

        self._executable = "python"
        self._pip_executable = "pip"

        self.find_executables()

        self._base = base or path

        self._site_packages: SitePackages | None = None
        self._supported_tags: list[Tag] | None = None
        self._purelib: Path | None = None
        self._platlib: Path | None = None
        self._script_dirs: list[Path] | None = None

        self._embedded_pip_path: Path | None = None

    @property
    def bin_dir(self) -> Path:
        return self._bin_dir

    @property
    def path(self) -> Path:
        return self._path

    @property
    def base(self) -> Path:
        return self._base

    @property
    def version_info(self) -> PythonVersion:
        version_info: PythonVersion = self.marker_env["version_info"]
        return version_info

    @property
    def python_implementation(self) -> str:
        implementation: str = self.marker_env["platform_python_implementation"]
        return implementation

    @property
    def python(self) -> Path:
        """
        Path to current python executable
        """
        return Path(self._bin(self._executable))

    @cached_property
    def marker_env(self) -> dict[str, Any]:
        return self.get_marker_env()

    @property
    def parent_env(self) -> GenericEnv:
        from poetry.utils.env.generic_env import GenericEnv

        return GenericEnv(self.base, child_env=self)

    def _find_python_executable(self) -> None:
        bin_dir = self._bin_dir

        if self._is_windows and self._is_conda:
            bin_dir = self._path

        python_executables = sorted(
            p.name
            for p in bin_dir.glob("python*")
            if re.match(r"python(?:\d+(?:\.\d+)?)?(?:\.exe)?$", p.name)
        )
        if python_executables:
            executable = python_executables[0]
            if executable.endswith(".exe"):
                executable = executable[:-4]

            self._executable = executable

    def _find_pip_executable(self) -> None:
        pip_executables = sorted(
            p.name
            for p in self._bin_dir.glob("pip*")
            if re.match(r"pip(?:\d+(?:\.\d+)?)?(?:\.exe)?$", p.name)
        )
        if pip_executables:
            pip_executable = pip_executables[0]
            if pip_executable.endswith(".exe"):
                pip_executable = pip_executable[:-4]

            self._pip_executable = pip_executable

    def find_executables(self) -> None:
        self._find_python_executable()
        self._find_pip_executable()

    def get_embedded_wheel(self, distribution: str) -> Path:
        wheel: Wheel = get_embed_wheel(
            distribution, f"{self.version_info[0]}.{self.version_info[1]}"
        )
        path: Path = wheel.path
        return path

    @property
    def pip_embedded(self) -> Path:
        if self._embedded_pip_path is None:
            self._embedded_pip_path = self.get_embedded_wheel("pip") / "pip"
        return self._embedded_pip_path

    @property
    def pip(self) -> Path:
        """
        Path to current pip executable
        """
        # we do not use as_posix() here due to issues with windows pathlib2
        # implementation
        path = Path(self._bin(self._pip_executable))
        if not path.exists():
            return self.pip_embedded
        return path

    @property
    def platform(self) -> str:
        return sys.platform

    @property
    def os(self) -> str:
        return os.name

    @property
    def site_packages(self) -> SitePackages:
        if self._site_packages is None:
            self._site_packages = SitePackages(
                self.purelib,
                self.platlib,
                self.fallbacks,
            )
        return self._site_packages

    @property
    def usersite(self) -> Path | None:
        if "usersite" in self.paths:
            return Path(self.paths["usersite"])
        return None

    @property
    def userbase(self) -> Path | None:
        if "userbase" in self.paths:
            return Path(self.paths["userbase"])
        return None

    @property
    def purelib(self) -> Path:
        if self._purelib is None:
            self._purelib = Path(self.paths["purelib"])

        return self._purelib

    @property
    def platlib(self) -> Path:
        if self._platlib is None:
            if "platlib" in self.paths:
                self._platlib = Path(self.paths["platlib"])
            else:
                self._platlib = self.purelib

        return self._platlib

    @cached_property
    def fallbacks(self) -> list[Path]:
        paths = [Path(path) for path in self.paths.get("fallbacks", [])]
        paths += [self.usersite] if self.usersite else []
        return paths

    def set_paths(
        self,
        purelib: str | Path | None = None,
        platlib: str | Path | None = None,
        userbase: str | Path | None = None,
        usersite: str | Path | None = None,
    ) -> None:
        """
        A cached property aware way to set environment paths during runtime.

        In some cases, like in `PluginManager._install()` method, paths are modified during execution. Direct
        modification of `self.paths` is not safe as caches relying on are not invalidated. This helper method
        ensures that we clear the relevant caches why paths are modified.
        """
        if purelib:
            self.paths["purelib"] = str(purelib)

        if platlib:
            self.paths["platlib"] = str(platlib)

        if userbase:
            self.paths["userbase"] = str(userbase)

        if usersite:
            self.paths["usersite"] = str(usersite)

        # clear cached properties using the env paths
        self.__dict__.pop("fallbacks", None)
        self.__dict__.pop("scheme_dict", None)

    @cached_property
    def scheme_dict(self) -> dict[str, str]:
        """
        This property exists to allow cases where system environment paths are not writable and
        user site is enabled. This enables us to ensure packages (wheels) are correctly installed
        into directories where the current user can write to.

        If all candidates in `self.paths` is writable, no modification is made. If at least one path is not writable
        and all generated writable candidates are indeed writable, these are used instead. If any candidate is not
        writable, the original paths are returned.

        Alternative writable candidates are generated by replacing discovered prefix, with "userbase"
        if available. The original prefix is computed as the common path prefix of "scripts" and "purelib".
        For example, given `{ "purelib": "/usr/local/lib/python3.13/site-packages", "scripts": "/usr/local/bin",
        "userbase": "/home/user/.local" }`; the candidate "purelib" path would be
        `/home/user/.local/lib/python3.13/site-packages`.
        """
        paths = self.paths.copy()

        if (
            not self.is_venv()
            and paths.get("userbase")
            and ("scripts" in paths and "purelib" in paths)
        ):
            overrides: dict[str, str] = {}

            try:
                base_path = os.path.commonpath([paths["scripts"], paths["purelib"]])
            except ValueError:
                return paths

            scheme_names = [key for key in SCHEME_NAMES if key in self.paths]

            for key in scheme_names:
                if not is_dir_writable(path=Path(paths[key]), create=True):
                    # there is at least one path that is not writable
                    break
            else:
                # all paths are writable, return early
                return paths

            for key in scheme_names:
                candidate = paths[key].replace(base_path, paths["userbase"])
                if not is_dir_writable(path=Path(candidate), create=True):
                    # at least one candidate is not writable, we cannot do much here
                    return paths

                overrides[key] = candidate

            paths.update(overrides)

        return paths

    def _get_lib_dirs(self) -> list[Path]:
        return [self.purelib, self.platlib, *self.fallbacks]

    def is_path_relative_to_lib(self, path: Path) -> bool:
        for lib_path in self._get_lib_dirs():
            with contextlib.suppress(ValueError):
                path.relative_to(lib_path)
                return True

        return False

    @property
    @abstractmethod
    def sys_path(self) -> list[str]: ...

    @cached_property
    def paths(self) -> dict[str, str]:
        paths = self.get_paths()

        if self.is_venv():
            # We copy pip's logic here for the `include` path
            paths["include"] = str(
                self.path.joinpath(
                    "include",
                    "site",
                    f"python{self.version_info[0]}.{self.version_info[1]}",
                )
            )
        return paths

    @property
    def supported_tags(self) -> list[Tag]:
        if self._supported_tags is None:
            self._supported_tags = self.get_supported_tags()

        return self._supported_tags

    @classmethod
    def get_base_prefix(cls) -> Path:
        real_prefix = getattr(sys, "real_prefix", None)
        if real_prefix is not None:
            return Path(real_prefix)

        base_prefix = getattr(sys, "base_prefix", None)
        if base_prefix is not None:
            return Path(base_prefix)

        return Path(sys.prefix)

    @abstractmethod
    def get_marker_env(self) -> dict[str, Any]: ...

    def get_pip_command(self, embedded: bool = False) -> list[str]:
        if embedded or not Path(self._bin(self._pip_executable)).exists():
            return [str(self.python), str(self.pip_embedded)]
        # run as module so that pip can update itself on Windows
        return [str(self.python), "-m", "pip"]

    @abstractmethod
    def get_supported_tags(self) -> list[Tag]: ...

    @abstractmethod
    def get_paths(self) -> dict[str, str]: ...

    def is_valid_for_marker(self, marker: BaseMarker) -> bool:
        valid: bool = marker.validate(self.marker_env)
        return valid

    def is_sane(self) -> bool:
        """
        Checks whether the current environment is sane or not.
        """
        return True

    def get_command_from_bin(self, bin: str) -> list[str]:
        if bin == "pip":
            # when pip is required we need to ensure that we fall back to
            # embedded pip when pip is not available in the environment
            return self.get_pip_command()

        return [self._bin(bin)]

    def run(self, bin: str, *args: str, **kwargs: Any) -> str:
        cmd = self.get_command_from_bin(bin) + list(args)
        return self._run(cmd, **kwargs)

    def run_pip(self, *args: str, **kwargs: Any) -> str:
        pip = self.get_pip_command()
        cmd = pip + list(args)
        return self._run(cmd, **kwargs)

    def run_python_script(self, content: str, **kwargs: Any) -> str:
        # Options Used:
        #     -I        : Run Python in isolated mode. (#6627)
        #     -W ignore : Suppress warnings.
        #
        # TODO: Consider replacing (-I) with (-EP) once support for managing Python <3.11 environments dropped.
        # This is useful to prevent user site being disabled over zealously.

        return self.run(
            self._executable,
            "-I",
            "-W",
            "ignore",
            "-c",
            content,
            stderr=subprocess.PIPE,
            **kwargs,
        )

    def _run(self, cmd: list[str], **kwargs: Any) -> str:
        """
        Run a command inside the Python environment.
        """
        call = kwargs.pop("call", False)
        env = kwargs.pop("env", dict(os.environ))
        stderr = kwargs.pop("stderr", subprocess.STDOUT)

        try:
            if call:
                assert stderr != subprocess.PIPE
                subprocess.check_call(cmd, stderr=stderr, env=env, **kwargs)
                output = ""
            else:
                encoding = "locale" if sys.version_info >= (3, 10) else None
                output = subprocess.check_output(
                    cmd, stderr=stderr, env=env, text=True, encoding=encoding, **kwargs
                )
        except CalledProcessError as e:
            raise EnvCommandError(e)

        return output

    def execute(self, bin: str, *args: str, **kwargs: Any) -> int:
        command = self.get_command_from_bin(bin) + list(args)
        env = kwargs.pop("env", dict(os.environ))

        if not self._is_windows:
            return os.execvpe(command[0], command, env=env)

        kwargs["shell"] = True
        exe = subprocess.Popen(command, env=env, **kwargs)
        exe.communicate()
        return exe.returncode

    @abstractmethod
    def is_venv(self) -> bool: ...

    @property
    def script_dirs(self) -> list[Path]:
        if self._script_dirs is None:
            scripts = self.paths.get("scripts")
            self._script_dirs = [
                Path(scripts) if scripts is not None else self._bin_dir
            ]
            if self.userbase:
                self._script_dirs.append(self.userbase / self._script_dirs[0].name)
        return self._script_dirs

    def _bin(self, bin: str) -> str:
        """
        Return path to the given executable.
        """
        if self._is_windows and not bin.endswith(".exe"):
            bin_path = self._bin_dir / (bin + ".exe")
        else:
            bin_path = self._bin_dir / bin

        if not bin_path.exists():
            # On Windows, some executables can be in the base path
            # This is especially true when installing Python with
            # the official installer, where python.exe will be at
            # the root of the env path.
            if self._is_windows:
                if not bin.endswith(".exe"):
                    bin_path = self._path / (bin + ".exe")
                else:
                    bin_path = self._path / bin

                if bin_path.exists():
                    return str(bin_path)

            return bin

        return str(bin_path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Env):
            return False

        return other.__class__ == self.__class__ and other.path == self.path

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self._path}")'
