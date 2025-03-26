from __future__ import annotations

from typing import ClassVar

from cleo.commands.command import Command
from cleo.io.inputs.argument import Argument


class ListCommand(Command):
    name = "list"

    description = "Lists commands."

    help = """\
The <info>{command_name}</info> command lists all commands:

  <info>{command_full_name}</info>

You can also display the commands for a specific namespace:

  <info>{command_full_name} test</info>
"""

    arguments: ClassVar[list[Argument]] = [
        Argument("namespace", required=False, description="The namespace name")
    ]

    def handle(self) -> int:
        from cleo.descriptors.text_descriptor import TextDescriptor

        TextDescriptor().describe(
            self._io, self.application, namespace=self.argument("namespace")
        )

        return 0
