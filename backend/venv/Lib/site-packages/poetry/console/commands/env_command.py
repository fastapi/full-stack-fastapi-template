from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from poetry.utils.env import Env


class EnvCommand(Command):
    def __init__(self) -> None:
        # Set in poetry.console.application.Application.configure_env
        self._env: Env | None = None

        super().__init__()

    @property
    def env(self) -> Env:
        assert self._env is not None
        return self._env

    def set_env(self, env: Env) -> None:
        self._env = env
