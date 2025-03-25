from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from poetry.console.commands.remove import RemoveCommand
from poetry.console.commands.self.self_command import SelfCommand


if TYPE_CHECKING:
    from cleo.io.inputs.option import Option


class SelfRemoveCommand(SelfCommand, RemoveCommand):
    name = "self remove"
    description = "Remove additional packages from Poetry's runtime environment."
    options: ClassVar[list[Option]] = [
        o for o in RemoveCommand.options if o.name in {"dry-run"}
    ]
    help = f"""\
The <c1>self remove</c1> command removes additional package's to Poetry's runtime \
environment.

This is managed in the <comment>{SelfCommand.get_default_system_pyproject_file()}</> \
file.
"""
