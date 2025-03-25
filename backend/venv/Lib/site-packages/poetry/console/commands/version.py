from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option
from poetry.core.version.exceptions import InvalidVersionError
from tomlkit.toml_document import TOMLDocument

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option
    from poetry.core.constraints.version import Version


class VersionCommand(Command):
    name = "version"
    description = (
        "Shows the version of the project or bumps it when a valid "
        "bump rule is provided."
    )

    arguments: ClassVar[list[Argument]] = [
        argument(
            "version",
            "The version number or the rule to update the version.",
            optional=True,
        ),
    ]
    options: ClassVar[list[Option]] = [
        option("short", "s", "Output the version number only"),
        option(
            "dry-run",
            None,
            "Do not update pyproject.toml file",
        ),
        option("next-phase", None, "Increment the phase of the current version"),
    ]

    help = """\
The version command shows the current version of the project or bumps the version of
the project and writes the new version back to <comment>pyproject.toml</> if a valid
bump rule is provided.

The new version should ideally be a valid semver string or a valid bump rule:
patch, minor, major, prepatch, preminor, premajor, prerelease.
"""

    def handle(self) -> int:
        version = self.argument("version")

        if version:
            version = self.increment_version(
                self.poetry.package.pretty_version, version, self.option("next-phase")
            )

            if self.option("short"):
                self.line(version.to_string())
            else:
                self.line(
                    f"Bumping version from <b>{self.poetry.package.pretty_version}</>"
                    f" to <fg=green>{version}</>"
                )

            if not self.option("dry-run"):
                content: dict[str, Any] = self.poetry.file.read()
                project_content = content.get("project", {})
                if "version" in project_content:
                    project_content["version"] = version.text
                poetry_content = content.get("tool", {}).get("poetry", {})
                if "version" in poetry_content:
                    poetry_content["version"] = version.text

                assert isinstance(content, TOMLDocument)
                self.poetry.file.write(content)
        else:
            if self.option("short"):
                self.line(self.poetry.package.pretty_version)
            else:
                self.line(
                    f"<comment>{self.poetry.package.pretty_name}</>"
                    f" <info>{self.poetry.package.pretty_version}</>"
                )

        return 0

    def increment_version(
        self, version: str, rule: str, next_phase: bool = False
    ) -> Version:
        from poetry.core.constraints.version import Version

        try:
            parsed = Version.parse(version)
        except InvalidVersionError:
            raise ValueError("The project's version doesn't seem to follow semver")

        if rule in {"major", "premajor"}:
            new = parsed.next_major()
            if rule == "premajor":
                new = new.first_prerelease()
        elif rule in {"minor", "preminor"}:
            new = parsed.next_minor()
            if rule == "preminor":
                new = new.first_prerelease()
        elif rule in {"patch", "prepatch"}:
            new = parsed.next_patch()
            if rule == "prepatch":
                new = new.first_prerelease()
        elif rule == "prerelease":
            if parsed.is_unstable():
                pre = parsed.pre
                assert pre is not None
                pre = pre.next_phase() if next_phase else pre.next()
                new = Version(parsed.epoch, parsed.release, pre)
            else:
                new = parsed.next_patch().first_prerelease()
        else:
            new = Version.parse(rule)

        return new
