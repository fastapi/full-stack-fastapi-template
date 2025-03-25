from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import option

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.option import Option

    from poetry.utils.env import Env


class EnvInfoCommand(Command):
    name = "env info"
    description = "Displays information about the current environment."

    options: ClassVar[list[Option]] = [
        option("path", "p", "Only display the environment's path."),
        option(
            "executable", "e", "Only display the environment's python executable path."
        ),
    ]

    def handle(self) -> int:
        from poetry.utils.env import EnvManager

        env = EnvManager(self.poetry).get()

        if self.option("path"):
            if not env.is_venv():
                return 1

            self.line(str(env.path))

            return 0

        if self.option("executable"):
            if not env.is_venv():
                return 1

            self.line(str(env.python))

            return 0

        self._display_complete_info(env)
        return 0

    def _display_complete_info(self, env: Env) -> None:
        env_python_version = ".".join(str(s) for s in env.version_info[:3])
        self.line("")
        self.line("<b>Virtualenv</b>")
        listing = [
            f"<info>Python</info>:         <comment>{env_python_version}</>",
            f"<info>Implementation</info>: <comment>{env.python_implementation}</>",
            (
                "<info>Path</info>:          "
                f" <comment>{env.path if env.is_venv() else 'NA'}</>"
            ),
            (
                "<info>Executable</info>:    "
                f" <comment>{env.python if env.is_venv() else 'NA'}</>"
            ),
        ]
        if env.is_venv():
            listing.append(
                "<info>Valid</info>:         "
                f" <{'comment' if env.is_sane() else 'error'}>{env.is_sane()}</>"
            )
        self.line("\n".join(listing))

        self.line("")

        base_env = env.parent_env
        python = ".".join(str(v) for v in base_env.version_info[:3])
        self.line("<b>Base</b>")
        self.line(
            "\n".join(
                [
                    f"<info>Platform</info>:   <comment>{env.platform}</>",
                    f"<info>OS</info>:         <comment>{env.os}</>",
                    f"<info>Python</info>:     <comment>{python}</>",
                    f"<info>Path</info>:       <comment>{base_env.path}</>",
                    f"<info>Executable</info>: <comment>{base_env.python}</>",
                ]
            )
        )
