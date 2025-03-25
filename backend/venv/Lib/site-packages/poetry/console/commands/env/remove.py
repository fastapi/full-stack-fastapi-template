from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option


class EnvRemoveCommand(Command):
    name = "env remove"
    description = "Remove virtual environments associated with the project."

    arguments: ClassVar[list[Argument]] = [
        argument(
            "python",
            "The python executables associated with, or names of the virtual"
            " environments which are to be removed.",
            optional=True,
            multiple=True,
        )
    ]
    options: ClassVar[list[Option]] = [
        option(
            "all",
            description=(
                "Remove all managed virtual environments associated with the project."
            ),
        ),
    ]

    def handle(self) -> int:
        from poetry.utils.env import EnvManager

        is_in_project = self.poetry.config.get("virtualenvs.in-project")

        pythons = self.argument("python")
        remove_all_envs = self.option("all")

        if not (pythons or remove_all_envs or is_in_project):
            self.line("No virtualenv provided.")

        manager = EnvManager(self.poetry)
        # TODO: refactor env.py to allow removal with one loop
        for python in pythons:
            venv = manager.remove(python)
            self.line(f"Deleted virtualenv: <comment>{venv.path}</comment>")
        if remove_all_envs or is_in_project:
            for venv in manager.list():
                if not is_in_project or venv.path.is_relative_to(
                    self.poetry.pyproject_path.parent
                ):
                    manager.remove_venv(venv.path)
                    self.line(f"Deleted virtualenv: <comment>{venv.path}</comment>")
            # Since we remove all the virtualenvs, we can also remove the entry
            # in the envs file. (Strictly speaking, we should do this explicitly,
            # in case it points to a virtualenv that had been removed manually before.)
            if remove_all_envs and manager.envs_file.exists():
                manager.envs_file.remove_section(manager.base_env_name)

        return 0
