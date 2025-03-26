from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from poetry.console.commands.self.install import SelfInstallCommand


if TYPE_CHECKING:
    from cleo.io.inputs.option import Option


class SelfSyncCommand(SelfInstallCommand):
    name = "self sync"
    description = (
        "Sync Poetry's own environment according to the locked packages (incl. addons)"
        " required by this Poetry installation."
    )
    options: ClassVar[list[Option]] = [
        opt for opt in SelfInstallCommand.options if opt.name != "sync"
    ]
    help = f"""\
The <c1>self sync</c1> command ensures all additional (and no other) packages \
specified are installed in the current runtime environment.

This is managed in the \
<comment>{SelfInstallCommand.get_default_system_pyproject_file()}</> file.

You can add more packages using the <c1>self add</c1> command and remove them using \
the <c1>self remove</c1> command.
"""

    @property
    def _with_synchronization(self) -> bool:
        return True
