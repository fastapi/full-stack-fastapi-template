from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option
from cleo.io.null_io import NullIO
from tomlkit import table
from tomlkit.items import AoT

from poetry.config.source import Source
from poetry.console.commands.command import Command
from poetry.repositories.repository_pool import Priority


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option


class SourceAddCommand(Command):
    name = "source add"
    description = "Add source configuration for project."

    arguments: ClassVar[list[Argument]] = [
        argument(
            "name",
            "Source repository name.",
        ),
        argument(
            "url",
            "Source repository URL."
            " Required, except for PyPI, for which it is not allowed.",
            optional=True,
        ),
    ]

    options: ClassVar[list[Option]] = [
        option(
            "priority",
            "p",
            "Set the priority of this source. One of:"
            f" {', '.join(p.name.lower() for p in Priority)}. Defaults to"
            f" {Priority.PRIMARY.name.lower()}, but will switch to "
            f"{Priority.SUPPLEMENTAL.name.lower()} in a later release.",
            flag=False,
        ),
    ]

    def handle(self) -> int:
        from poetry.factory import Factory

        name: str = self.argument("name")
        lower_name = name.lower()
        url: str = self.argument("url")
        priority_str: str | None = self.option("priority", None)

        if lower_name == "pypi":
            name = "PyPI"
            if url:
                self.line_error(
                    "<error>The URL of PyPI is fixed and cannot be set.</error>"
                )
                return 1
        elif not url:
            self.line_error(
                "<error>A custom source cannot be added without a URL.</error>"
            )
            return 1

        if priority_str is None:
            self.io.write_error_line(
                f"<warning>The default priority will change to <b>{Priority.SUPPLEMENTAL.name.lower()}</> "
                f"in a future release.</>"
            )
            priority = Priority.PRIMARY
        else:
            priority = Priority[priority_str.upper()]

        sources = AoT([])
        new_source = Source(name=name, url=url, priority=priority)
        is_new_source = True

        for source in self.poetry.get_sources():
            if source.name.lower() == lower_name:
                source = new_source
                is_new_source = False

            sources.append(source.to_toml_table())

        if is_new_source:
            self.line(f"Adding source with name <c1>{name}</c1>.")
            sources.append(new_source.to_toml_table())
        else:
            self.line(f"Source with name <c1>{name}</c1> already exists. Updating.")

        # ensure new source is valid. eg: invalid name etc.
        try:
            pool = Factory.create_pool(self.poetry.config, sources, NullIO())
            pool.repository(name)
        except ValueError as e:
            self.line_error(
                f"<error>Failed to validate addition of <c1>{name}</c1>: {e}</error>"
            )
            return 1

        # tomlkit types are awkward to work with, treat content as a mostly untyped
        # dictionary.
        content: dict[str, Any] = self.poetry.pyproject.data
        if "tool" not in content:
            content["tool"] = table()
        if "poetry" not in content["tool"]:
            content["tool"]["poetry"] = table()
        self.poetry.pyproject.poetry_config["source"] = sources
        self.poetry.pyproject.save()

        return 0
