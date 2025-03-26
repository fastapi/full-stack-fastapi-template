from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import option

from poetry.console.commands.self.self_command import SelfCommand
from poetry.console.commands.show import ShowCommand


if TYPE_CHECKING:
    from cleo.io.inputs.option import Option


class SelfShowCommand(SelfCommand, ShowCommand):
    name = "self show"
    options: ClassVar[list[Option]] = [
        option("addons", None, "List only add-on packages installed."),
        *[o for o in ShowCommand.options if o.name in {"tree", "latest", "outdated"}],
    ]
    description = "Show packages from Poetry's runtime environment."
    help = f"""\
The <c1>self show</c1> command behaves similar to the <c1>show</c1> command, but
working within Poetry's runtime environment. This lists all packages installed within
the Poetry install environment.

To show only additional packages that have been added via <c1>self add</c1> and their
dependencies use <c1>self show --addons</c1>.

This is managed in the <comment>{SelfCommand.get_default_system_pyproject_file()}</> \
file.
"""

    @property
    def activated_groups(self) -> set[str]:
        if self.option("addons", False):
            return {SelfCommand.ADDITIONAL_PACKAGE_GROUP}

        groups: set[str] = super(ShowCommand, self).activated_groups
        return groups
