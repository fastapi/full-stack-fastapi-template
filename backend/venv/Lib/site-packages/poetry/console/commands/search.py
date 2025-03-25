from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import argument

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument


class SearchCommand(Command):
    name = "search"
    description = "Searches for packages on remote repositories."

    arguments: ClassVar[list[Argument]] = [
        argument("tokens", "The tokens to search for.", multiple=True)
    ]

    def handle(self) -> int:
        seen = set()

        table = self.table(style="compact")
        table.set_headers(
            ["<b>Package</>", "<b>Version</>", "<b>Source</>", "<b>Description</>"]
        )

        rows = []

        for repository in self.poetry.pool.repositories:
            for result in repository.search(self.argument("tokens")):
                key = f"{repository.name}::{result.pretty_string}"
                if key in seen:
                    continue
                seen.add(key)
                rows.append((result, repository.name))

        if not rows:
            self.line("<info>No matching packages were found.</>")
            return 0

        for package, source in sorted(
            rows, key=lambda x: (x[0].name, x[0].version, x[1])
        ):
            table.add_row(
                [
                    f"<c1>{package.name}</>",
                    f"<b>{package.version}</b>",
                    f"<fg=yellow;options=bold>{source}</>",
                    str(package.description),
                ]
            )

        table.render()

        return 0
