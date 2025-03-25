from __future__ import annotations

import json
import os
import re
import subprocess

from typing import TYPE_CHECKING
from typing import Any

from poetry.utils.env.script_strings import GET_PATHS
from poetry.utils.env.virtual_env import VirtualEnv


if TYPE_CHECKING:
    from pathlib import Path

    from poetry.utils.env.base_env import Env


class GenericEnv(VirtualEnv):
    def __init__(
        self, path: Path, base: Path | None = None, child_env: Env | None = None
    ) -> None:
        self._child_env = child_env

        super().__init__(path, base=base)

    def find_executables(self) -> None:
        patterns = [("python*", "pip*")]

        if self._child_env:
            minor_version = (
                f"{self._child_env.version_info[0]}.{self._child_env.version_info[1]}"
            )
            major_version = f"{self._child_env.version_info[0]}"
            patterns = [
                (f"python{minor_version}", f"pip{minor_version}"),
                (f"python{major_version}", f"pip{major_version}"),
            ]

        python_executable = None
        pip_executable = None

        for python_pattern, pip_pattern in patterns:
            if python_executable and pip_executable:
                break

            if not python_executable:
                python_executables = sorted(
                    p.name
                    for p in self._bin_dir.glob(python_pattern)
                    if re.match(r"python(?:\d+(?:\.\d+)?)?(?:\.exe)?$", p.name)
                )

                if python_executables:
                    executable = python_executables[0]
                    if executable.endswith(".exe"):
                        executable = executable[:-4]

                    python_executable = executable

            if not pip_executable:
                pip_executables = sorted(
                    p.name
                    for p in self._bin_dir.glob(pip_pattern)
                    if re.match(r"pip(?:\d+(?:\.\d+)?)?(?:\.exe)?$", p.name)
                )
                if pip_executables:
                    pip_executable = pip_executables[0]
                    if pip_executable.endswith(".exe"):
                        pip_executable = pip_executable[:-4]

            if python_executable:
                self._executable = python_executable

            if pip_executable:
                self._pip_executable = pip_executable

    def get_paths(self) -> dict[str, str]:
        output = self.run_python_script(GET_PATHS)

        paths: dict[str, str] = json.loads(output)
        return paths

    def execute(self, bin: str, *args: str, **kwargs: Any) -> int:
        command = self.get_command_from_bin(bin) + list(args)
        env = kwargs.pop("env", dict(os.environ))

        if not self._is_windows:
            return os.execvpe(command[0], command, env=env)

        exe = subprocess.Popen(command, env=env, **kwargs)
        exe.communicate()

        return exe.returncode

    def _run(self, cmd: list[str], **kwargs: Any) -> str:
        return super(VirtualEnv, self)._run(cmd, **kwargs)

    def is_venv(self) -> bool:
        return self._path != self._base
