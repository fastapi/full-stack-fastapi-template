from __future__ import annotations

import sys

from poetry.console.commands.command import Command


class DebugInfoCommand(Command):
    name = "debug info"
    description = "Shows debug information."

    def handle(self) -> int:
        poetry_python_version = ".".join(str(s) for s in sys.version_info[:3])

        self.line("")
        self.line("<b>Poetry</b>")
        self.line(
            "\n".join(
                [
                    f"<info>Version</info>: <comment>{self.poetry.VERSION}</>",
                    f"<info>Python</info>:  <comment>{poetry_python_version}</>",
                ]
            )
        )
        command = self.get_application().get("env info")

        exit_code: int = command.run(self.io)
        return exit_code
