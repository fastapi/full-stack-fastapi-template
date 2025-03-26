from __future__ import annotations

import shlex

from typing import TYPE_CHECKING

import shellingham

from poetry.console.commands.env_command import EnvCommand
from poetry.utils._compat import WINDOWS


if TYPE_CHECKING:
    from poetry.utils.env import Env


class ShellNotSupportedError(Exception):
    """Raised when a shell doesn't have an activator in virtual environment"""


class EnvActivateCommand(EnvCommand):
    name = "env activate"
    description = "Print the command to activate a virtual environment."

    def handle(self) -> int:
        from poetry.utils.env import EnvManager

        env = EnvManager(self.poetry).get()

        if command := self._get_activate_command(env):
            self.line(command)
            return 0
        else:
            raise ShellNotSupportedError(
                "Discovered shell doesn't have an activator in virtual environment"
            )

    def _get_activate_command(self, env: Env) -> str:
        try:
            shell, _ = shellingham.detect_shell()
        except shellingham.ShellDetectionFailure:
            shell = ""
        if shell == "fish":
            command, filename = "source", "activate.fish"
        elif shell == "nu":
            command, filename = "overlay use", "activate.nu"
        elif shell == "csh":
            command, filename = "source", "activate.csh"
        elif shell in ["powershell", "pwsh"]:
            command, filename = ".", "Activate.ps1"
        elif shell == "cmd":
            command, filename = ".", "activate.bat"
        else:
            command, filename = "source", "activate"

        if (activation_script := env.bin_dir / filename).exists():
            if WINDOWS:
                return f"{self._quote(str(activation_script), shell)}"
            return f"{command} {self._quote(str(activation_script), shell)}"
        return ""

    @staticmethod
    def _quote(command: str, shell: str) -> str:
        if WINDOWS:
            if shell == "cmd":
                return f'"{command}"'
            if shell in ["powershell", "pwsh"]:
                return f'& "{command}"'
        return shlex.quote(command)
