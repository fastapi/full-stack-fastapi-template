from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import option

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.option import Option


class PublishCommand(Command):
    name = "publish"
    description = "Publishes a package to a remote repository."

    options: ClassVar[list[Option]] = [
        option(
            "repository", "r", "The repository to publish the package to.", flag=False
        ),
        option("username", "u", "The username to access the repository.", flag=False),
        option("password", "p", "The password to access the repository.", flag=False),
        option(
            "cert", None, "Certificate authority to access the repository.", flag=False
        ),
        option(
            "client-cert",
            None,
            "Client certificate to access the repository.",
            flag=False,
        ),
        option(
            "dist-dir",
            None,
            "Dist directory where built artifact are stored. Default is `dist`.",
            default="dist",
            flag=False,
        ),
        option("build", None, "Build the package before publishing."),
        option("dry-run", None, "Perform all actions except upload the package."),
        option(
            "skip-existing",
            None,
            "Ignore errors from files already existing in the repository.",
        ),
    ]

    help = """The publish command builds and uploads the package to a remote repository.

By default, it will upload to PyPI but if you pass the --repository option it will
upload to it instead.

The --repository option should match the name of a configured repository using
the config command.
"""

    loggers: ClassVar[list[str]] = ["poetry.publishing.publisher"]

    def handle(self) -> int:
        from poetry.publishing.publisher import Publisher

        if not self.poetry.is_package_mode:
            self.line_error("Publishing a package is not possible in non-package mode.")
            return 1

        dist_dir = self.option("dist-dir")

        publisher = Publisher(self.poetry, self.io, Path(dist_dir))

        # Building package first, if told
        if self.option("build"):
            if publisher.files and not self.confirm(
                f"There are <info>{len(publisher.files)}</info> files ready for"
                " publishing. Build anyway?"
            ):
                self.line_error("<error>Aborted!</error>")

                return 1

            self.call("build", args=f"--output {dist_dir}")

        files = publisher.files
        if not files:
            self.line_error(
                "<error>No files to publish. "
                "Run poetry build first or use the --build option.</error>"
            )

            return 1

        self.line("")

        cert = Path(self.option("cert")) if self.option("cert") else None
        client_cert = (
            Path(self.option("client-cert")) if self.option("client-cert") else None
        )

        publisher.publish(
            self.option("repository"),
            self.option("username"),
            self.option("password"),
            cert,
            client_cert,
            self.option("dry-run"),
            self.option("skip-existing"),
        )

        return 0
