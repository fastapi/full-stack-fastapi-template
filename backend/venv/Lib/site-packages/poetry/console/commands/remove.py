from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option
from packaging.utils import canonicalize_name
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.dependency_group import MAIN_GROUP
from tomlkit.toml_document import TOMLDocument

from poetry.console.commands.installer_command import InstallerCommand


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option


class RemoveCommand(InstallerCommand):
    name = "remove"
    description = "Removes a package from the project dependencies."

    arguments: ClassVar[list[Argument]] = [
        argument("packages", "The packages to remove.", multiple=True)
    ]
    options: ClassVar[list[Option]] = [
        option("group", "G", "The group to remove the dependency from.", flag=False),
        option(
            "dev",
            "D",
            "Remove a package from the development dependencies."
            " (shortcut for '-G dev')",
        ),
        option(
            "dry-run",
            None,
            "Output the operations but do not execute anything "
            "(implicitly enables --verbose).",
        ),
        option("lock", None, "Do not perform operations (only update the lockfile)."),
    ]

    help = """The <info>remove</info> command removes a package from the current
list of installed packages

<info>poetry remove</info>"""

    loggers: ClassVar[list[str]] = [
        "poetry.repositories.pypi_repository",
        "poetry.inspection.info",
    ]

    def handle(self) -> int:
        packages = self.argument("packages")

        if self.option("dev"):
            group = "dev"
        else:
            group = self.option("group", self.default_group)

        content: dict[str, Any] = self.poetry.file.read()
        project_content = content.get("project", {})
        poetry_content = content.get("tool", {}).get("poetry", {})

        if group is None:
            # remove from all groups
            removed = set()
            group_sections = []
            project_dependencies = project_content.get("dependencies", [])
            poetry_dependencies = poetry_content.get("dependencies", {})
            if project_dependencies or poetry_dependencies:
                group_sections.append(
                    (MAIN_GROUP, project_dependencies, poetry_dependencies)
                )
            group_sections.extend(
                (group_name, [], group_section.get("dependencies", {}))
                for group_name, group_section in poetry_content.get("group", {}).items()
            )

            for group_name, project_section, poetry_section in group_sections:
                removed |= self._remove_packages(
                    packages, project_section, poetry_section, group_name
                )
                if group_name != MAIN_GROUP and not poetry_section:
                    del poetry_content["group"][group_name]
        elif group == "dev" and "dev-dependencies" in poetry_content:
            # We need to account for the old `dev-dependencies` section
            removed = self._remove_packages(
                packages, [], poetry_content["dev-dependencies"], "dev"
            )

            if not poetry_content["dev-dependencies"]:
                del poetry_content["dev-dependencies"]
        else:
            removed = set()
            if "group" in poetry_content:
                if group in poetry_content["group"]:
                    removed = self._remove_packages(
                        packages,
                        [],
                        poetry_content["group"][group].get("dependencies", {}),
                        group,
                    )

                if not poetry_content["group"][group]:
                    del poetry_content["group"][group]

        if "group" in poetry_content and not poetry_content["group"]:
            del poetry_content["group"]

        not_found = set(packages).difference(removed)
        if not_found:
            raise ValueError(
                "The following packages were not found: " + ", ".join(sorted(not_found))
            )

        # Refresh the locker
        self.poetry.locker.set_pyproject_data(content)
        self.installer.set_locker(self.poetry.locker)
        self.installer.set_package(self.poetry.package)
        self.installer.dry_run(self.option("dry-run", False))
        self.installer.verbose(self.io.is_verbose())
        self.installer.update(True)
        self.installer.execute_operations(not self.option("lock"))
        self.installer.whitelist(removed)

        status = self.installer.run()

        if not self.option("dry-run") and status == 0:
            assert isinstance(content, TOMLDocument)
            self.poetry.file.write(content)

        return status

    def _remove_packages(
        self,
        packages: list[str],
        project_section: list[str],
        poetry_section: dict[str, Any],
        group_name: str,
    ) -> set[str]:
        removed = set()
        group = self.poetry.package.dependency_group(group_name)

        for package in packages:
            normalized_name = canonicalize_name(package)
            for requirement in project_section.copy():
                if Dependency.create_from_pep_508(requirement).name == normalized_name:
                    project_section.remove(requirement)
                    removed.add(package)
            for existing_package in list(poetry_section):
                if canonicalize_name(existing_package) == normalized_name:
                    del poetry_section[existing_package]
                    removed.add(package)

        for package in removed:
            group.remove_dependency(package)

        return removed
