from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from poetry.core.packages.dependency_group import MAIN_GROUP

from poetry.console.commands.install import InstallCommand
from poetry.console.commands.self.self_command import SelfCommand


if TYPE_CHECKING:
    from cleo.io.inputs.option import Option


class SelfInstallCommand(SelfCommand, InstallCommand):
    name = "self install"
    description = (
        "Install locked packages (incl. addons) required by this Poetry installation."
    )
    options: ClassVar[list[Option]] = [
        o for o in InstallCommand.options if o.name in {"sync", "dry-run"}
    ]
    help = f"""\
The <c1>self install</c1> command ensures all additional packages specified are \
installed in the current runtime environment.

This is managed in the <comment>{SelfCommand.get_default_system_pyproject_file()}</> \
file.

You can add more packages using the <c1>self add</c1> command and remove them using \
the <c1>self remove</c1> command.
"""

    @property
    def activated_groups(self) -> set[str]:
        return {MAIN_GROUP, self.default_group}

    @property
    def _alternative_sync_command(self) -> str:
        return "poetry self sync"
