from __future__ import annotations

from poetry.console.commands.command import Command


class AboutCommand(Command):
    name = "about"

    description = "Shows information about Poetry."

    def handle(self) -> int:
        from poetry.utils._compat import metadata

        self.line(
            f"""\
<info>Poetry - Package Management for Python

Version: {metadata.version("poetry")}
Poetry-Core Version: {metadata.version("poetry-core")}</info>

<comment>Poetry is a dependency manager tracking local dependencies of your projects\
 and libraries.
See <fg=blue>https://github.com/python-poetry/poetry</> for more information.</comment>\
"""
        )

        return 0
