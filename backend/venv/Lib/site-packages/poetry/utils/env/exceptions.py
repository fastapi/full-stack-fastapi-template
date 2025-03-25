from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.utils._compat import decode


if TYPE_CHECKING:
    from subprocess import CalledProcessError


class EnvError(Exception):
    pass


class IncorrectEnvError(EnvError):
    def __init__(self, env_name: str) -> None:
        message = f"Env {env_name} doesn't belong to this project."
        super().__init__(message)


class EnvCommandError(EnvError):
    def __init__(self, e: CalledProcessError) -> None:
        self.e = e

        message_parts = [
            f"Command {e.cmd} errored with the following return code {e.returncode}"
        ]
        if e.output:
            message_parts.append(f"Output:\n{decode(e.output)}")
        if e.stderr:
            message_parts.append(f"Error output:\n{decode(e.stderr)}")
        super().__init__("\n\n".join(message_parts))
