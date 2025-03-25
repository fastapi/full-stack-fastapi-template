from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import argument
from tomlkit.items import AoT

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument


class SourceRemoveCommand(Command):
    name = "source remove"
    description = "Remove source configured for the project."

    arguments: ClassVar[list[Argument]] = [
        argument(
            "name",
            "Source repository name.",
        ),
    ]

    def handle(self) -> int:
        name = self.argument("name")
        lower_name = name.lower()

        sources = AoT([])
        removed = False

        for source in self.poetry.get_sources():
            if source.name.lower() == lower_name:
                self.line(f"Removing source with name <c1>{source.name}</c1>.")
                removed = True
                continue
            sources.append(source.to_toml_table())

        if not removed:
            self.line_error(
                f"<error>Source with name <c1>{name}</c1> was not found.</error>"
            )
            return 1

        self.poetry.pyproject.poetry_config["source"] = sources
        self.poetry.pyproject.save()

        return 0
