from __future__ import annotations

import os
import platform
import site
import sys
import sysconfig

from pathlib import Path
from typing import Any

from packaging.tags import Tag
from packaging.tags import interpreter_name
from packaging.tags import interpreter_version
from packaging.tags import sys_tags

from poetry.utils.env.base_env import Env


class SystemEnv(Env):
    """
    A system (i.e. not a virtualenv) Python environment.
    """

    @property
    def python(self) -> Path:
        return Path(sys.executable)

    @property
    def sys_path(self) -> list[str]:
        return sys.path

    def get_paths(self) -> dict[str, str]:
        import site

        paths = sysconfig.get_paths().copy()

        if site.check_enableusersite():
            paths["usersite"] = site.getusersitepackages()
            paths["userbase"] = site.getuserbase()

        return paths

    def get_supported_tags(self) -> list[Tag]:
        return list(sys_tags())

    def get_marker_env(self) -> dict[str, Any]:
        if hasattr(sys, "implementation"):
            info = sys.implementation.version
            iver = f"{info.major}.{info.minor}.{info.micro}"
            kind = info.releaselevel
            if kind != "final":
                iver += kind[0] + str(info.serial)

            implementation_name = sys.implementation.name
        else:
            iver = "0"
            implementation_name = ""

        return {
            "implementation_name": implementation_name,
            "implementation_version": iver,
            "os_name": os.name,
            "platform_machine": platform.machine(),
            "platform_release": platform.release(),
            "platform_system": platform.system(),
            "platform_version": platform.version(),
            # Workaround for https://github.com/python/cpython/issues/99968
            "python_full_version": platform.python_version().rstrip("+"),
            "platform_python_implementation": platform.python_implementation(),
            "python_version": ".".join(platform.python_version().split(".")[:2]),
            "sys_platform": sys.platform,
            "version_info": sys.version_info,
            "interpreter_name": interpreter_name(),
            "interpreter_version": interpreter_version(),
        }

    def is_venv(self) -> bool:
        return self._path != self._base

    def _get_lib_dirs(self) -> list[Path]:
        return super()._get_lib_dirs() + [Path(d) for d in site.getsitepackages()]
