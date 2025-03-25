from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from poetry.console.commands.install import InstallCommand


if TYPE_CHECKING:
    from cleo.io.inputs.option import Option


class SyncCommand(InstallCommand):
    name = "sync"
    description = "Update the project's environment according to the lockfile."

    options: ClassVar[list[Option]] = [
        opt for opt in InstallCommand.options if opt.name != "sync"
    ]

    help = """\
The <info>sync</info> command makes sure that the project's environment is in sync with
the <comment>poetry.lock</> file.
It is equivalent to running <info>poetry install --sync</info>.

<info>poetry sync</info>

By default, the above command will also install the current project. To install only the
dependencies and not including the current project, run the command with the
<info>--no-root</info> option like below:

<info> poetry sync --no-root</info>

If you want to use Poetry only for dependency management but not for packaging,
you can set the "package-mode" to false in your pyproject.toml file.
"""

    @property
    def _with_synchronization(self) -> bool:
        return True
