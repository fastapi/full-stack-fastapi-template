from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import argument

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.ui.table import Rows


class SourceShowCommand(Command):
    name = "source show"
    description = "Show information about sources configured for the project."

    arguments: ClassVar[list[Argument]] = [
        argument(
            "source",
            "Source(s) to show information for. Defaults to showing all sources.",
            optional=True,
            multiple=True,
        ),
    ]

    def notify_implicit_pypi(self) -> None:
        if not self.poetry.pool.has_repository("pypi"):
            return

        self.line(
            "<c1><b>PyPI</> is implicitly enabled as a <b>primary</> source. "
            "If you wish to disable it, or alter its priority please refer to "
            "<b>https://python-poetry.org/docs/repositories/#package-sources</>.</>"
        )
        self.line("")

    def handle(self) -> int:
        sources = self.poetry.get_sources()
        names = self.argument("source")
        lower_names = [name.lower() for name in names]

        if not sources:
            self.line("No sources configured for this project.\n")
            self.notify_implicit_pypi()
            return 0

        if names and not any(s.name.lower() in lower_names for s in sources):
            self.line_error(
                f"No source found with name(s): {', '.join(names)}",
                style="error",
            )
            return 1

        is_pypi_implicit = True

        for source in sources:
            if names and source.name.lower() not in lower_names:
                continue

            if source.name.lower() == "pypi":
                is_pypi_implicit = False

            table = self.table(style="compact")
            rows: Rows = [["<info>name</>", f" : <c1>{source.name}</>"]]
            if source.url:
                rows.append(["<info>url</>", f" : {source.url}"])
            rows.append(["<info>priority</>", f" : {source.priority.name.lower()}"])
            table.add_rows(rows)
            table.render()
            self.line("")

        if not names and is_pypi_implicit:
            self.notify_implicit_pypi()

        return 0
