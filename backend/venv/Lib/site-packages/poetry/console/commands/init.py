from __future__ import annotations

import re

from collections.abc import Mapping
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Union

from cleo.helpers import option
from packaging.utils import canonicalize_name
from tomlkit import inline_table

from poetry.console.commands.command import Command
from poetry.console.commands.env_command import EnvCommand
from poetry.utils.dependency_specification import RequirementsParser
from poetry.utils.env.python import Python


if TYPE_CHECKING:
    from cleo.io.inputs.option import Option
    from packaging.utils import NormalizedName
    from poetry.core.packages.package import Package
    from tomlkit.items import InlineTable

    from poetry.repositories import RepositoryPool

Requirements = dict[str, Union[str, Mapping[str, Any]]]


class InitCommand(Command):
    name = "init"
    description = (
        "Creates a basic <comment>pyproject.toml</> file in the current directory."
    )

    options: ClassVar[list[Option]] = [
        option("name", None, "Name of the package.", flag=False),
        option("description", None, "Description of the package.", flag=False),
        option("author", None, "Author name of the package.", flag=False),
        option("python", None, "Compatible Python versions.", flag=False),
        option(
            "dependency",
            None,
            "Package to require, with an optional version constraint, "
            "e.g. requests:^2.10.0 or requests=2.11.1.",
            flag=False,
            multiple=True,
        ),
        option(
            "dev-dependency",
            None,
            "Package to require for development, with an optional version"
            " constraint, e.g. requests:^2.10.0 or requests=2.11.1.",
            flag=False,
            multiple=True,
        ),
        option("license", "l", "License of the package.", flag=False),
    ]

    help = """\
The <c1>init</c1> command creates a basic <comment>pyproject.toml</> file in the\
 current directory.
"""

    def __init__(self) -> None:
        super().__init__()

        self._pool: RepositoryPool | None = None

    def handle(self) -> int:
        from pathlib import Path

        project_path = Path.cwd()

        if self.io.input.option("project"):
            project_path = Path(self.io.input.option("project"))
            if not project_path.exists() or not project_path.is_dir():
                self.line_error("<error>The --project path is not a directory.</error>")
                return 1

        return self._init_pyproject(project_path=project_path)

    def _init_pyproject(
        self,
        project_path: Path,
        allow_interactive: bool = True,
        layout_name: str = "standard",
        readme_format: str = "md",
    ) -> int:
        from poetry.core.vcs.git import GitConfig

        from poetry.config.config import Config
        from poetry.layouts import layout
        from poetry.pyproject.toml import PyProjectTOML

        is_interactive = self.io.is_interactive() and allow_interactive

        pyproject = PyProjectTOML(project_path / "pyproject.toml")

        if pyproject.file.exists():
            if pyproject.is_poetry_project():
                self.line_error(
                    "<error>A pyproject.toml file with a project and/or"
                    " a poetry section already exists.</error>"
                )
                return 1

            if pyproject.data.get("build-system"):
                self.line_error(
                    "<error>A pyproject.toml file with a defined build-system already"
                    " exists.</error>"
                )
                return 1

        vcs_config = GitConfig()

        if is_interactive:
            self.line("")
            self.line(
                "This command will guide you through creating your"
                " <info>pyproject.toml</> config."
            )
            self.line("")

        name = self.option("name")
        if not name:
            name = project_path.name.lower()

            if is_interactive:
                question = self.create_question(
                    f"Package name [<comment>{name}</comment>]: ", default=name
                )
                name = self.ask(question)

        version = "0.1.0"

        if is_interactive:
            question = self.create_question(
                f"Version [<comment>{version}</comment>]: ", default=version
            )
            version = self.ask(question)

        description = self.option("description") or ""
        if not description and is_interactive:
            description = self.ask(self.create_question("Description []: ", default=""))

        author = self.option("author")
        if not author and vcs_config.get("user.name"):
            author = vcs_config["user.name"]
            author_email = vcs_config.get("user.email")
            if author_email:
                author += f" <{author_email}>"

        if is_interactive:
            question = self.create_question(
                f"Author [<comment>{author}</comment>, n to skip]: ", default=author
            )
            question.set_validator(lambda v: self._validate_author(v, author))
            author = self.ask(question)

        authors = [author] if author else []

        license_name = self.option("license")
        if not license_name and is_interactive:
            license_name = self.ask(self.create_question("License []: ", default=""))

        python = self.option("python")
        if not python:
            config = Config.create()
            python = (
                ">="
                + Python.get_preferred_python(config, self.io).minor_version.to_string()
            )

            if is_interactive:
                question = self.create_question(
                    f"Compatible Python versions [<comment>{python}</comment>]: ",
                    default=python,
                )
                python = self.ask(question)

        if is_interactive:
            self.line("")

        requirements: Requirements = {}
        if self.option("dependency"):
            requirements = self._format_requirements(
                self._determine_requirements(self.option("dependency"))
            )

        question_text = "Would you like to define your main dependencies interactively?"
        help_message = """\
        You can specify a package in the following forms:
          - A single name (<b>requests</b>): this will search for matches on PyPI
          - A name and a constraint (<b>requests@^2.23.0</b>)
          - A git url (<b>git+https://github.com/python-poetry/poetry.git</b>)
          - A git url with a revision\
         (<b>git+https://github.com/python-poetry/poetry.git#develop</b>)
          - A file path (<b>../my-package/my-package.whl</b>)
          - A directory (<b>../my-package/</b>)
          - A url (<b>https://example.com/packages/my-package-0.1.0.tar.gz</b>)
        """

        help_displayed = False
        if is_interactive and self.confirm(question_text, True):
            self.line(help_message)
            help_displayed = True
            requirements.update(
                self._format_requirements(self._determine_requirements([]))
            )
            self.line("")

        dev_requirements: Requirements = {}
        if self.option("dev-dependency"):
            dev_requirements = self._format_requirements(
                self._determine_requirements(self.option("dev-dependency"))
            )

        question_text = (
            "Would you like to define your development dependencies interactively?"
        )
        if is_interactive and self.confirm(question_text, True):
            if not help_displayed:
                self.line(help_message)

            dev_requirements.update(
                self._format_requirements(self._determine_requirements([]))
            )

            self.line("")

        layout_ = layout(layout_name)(
            name,
            version,
            description=description,
            author=authors[0] if authors else None,
            readme_format=readme_format,
            license=license_name,
            python=python,
            dependencies=requirements,
            dev_dependencies=dev_requirements,
        )

        create_layout = not project_path.exists()

        if create_layout:
            layout_.create(project_path, with_pyproject=False)

        content = layout_.generate_project_content()
        for section, item in content.items():
            pyproject.data.append(section, item)

        if is_interactive:
            self.line("<info>Generated file</info>")
            self.line("")
            self.line(pyproject.data.as_string().replace("\r\n", "\n"))
            self.line("")

        if is_interactive and not self.confirm("Do you confirm generation?", True):
            self.line_error("<error>Command aborted</error>")

            return 1

        pyproject.save()

        if create_layout:
            path = project_path.resolve()

            with suppress(ValueError):
                path = path.relative_to(Path.cwd())

            self.line(
                f"Created package <info>{layout_._package_name}</> in"
                f" <fg=blue>{path.as_posix()}</>"
            )

        return 0

    def _generate_choice_list(
        self, matches: list[Package], canonicalized_name: NormalizedName
    ) -> list[str]:
        choices = []
        matches_names = [p.name for p in matches]
        exact_match = canonicalized_name in matches_names
        if exact_match:
            choices.append(matches[matches_names.index(canonicalized_name)].pretty_name)

        for found_package in matches:
            if len(choices) >= 10:
                break

            if found_package.name == canonicalized_name:
                continue

            choices.append(found_package.pretty_name)

        return choices

    def _determine_requirements(
        self,
        requires: list[str],
        allow_prereleases: bool | None = None,
        source: str | None = None,
        is_interactive: bool | None = None,
    ) -> list[dict[str, Any]]:
        if is_interactive is None:
            is_interactive = self.io.is_interactive()

        if not requires:
            result = []

            question = self.create_question(
                "Package to add or search for (leave blank to skip):"
            )
            question.set_validator(self._validate_package)

            follow_up_question = self.create_question(
                "\nAdd a package (leave blank to skip):"
            )
            follow_up_question.set_validator(self._validate_package)

            package = self.ask(question)
            while package:
                constraint = self._parse_requirements([package])[0]
                if (
                    "git" in constraint
                    or "url" in constraint
                    or "path" in constraint
                    or "version" in constraint
                ):
                    self.line(f"Adding <info>{package}</info>")
                    result.append(constraint)
                    package = self.ask(follow_up_question)
                    continue

                canonicalized_name = canonicalize_name(constraint["name"])
                matches = self._get_pool().search(canonicalized_name)
                if not matches:
                    self.line_error("<error>Unable to find package</error>")
                    package = False
                else:
                    choices = self._generate_choice_list(matches, canonicalized_name)

                    info_string = (
                        f"Found <info>{len(matches)}</info> packages matching"
                        f" <c1>{package}</c1>"
                    )

                    if len(matches) > 10:
                        info_string += "\nShowing the first 10 matches"

                    self.line(info_string)

                    # Default to an empty value to signal no package was selected
                    choices.append("")

                    package = self.choice(
                        "\nEnter package # to add, or the complete package name if"
                        " it is not listed",
                        choices,
                        attempts=3,
                        default=len(choices) - 1,
                    )

                    if not package:
                        self.line("<warning>No package selected</warning>")

                    # package selected by user, set constraint name to package name
                    if package:
                        constraint["name"] = package

                # no constraint yet, determine the best version automatically
                if package and "version" not in constraint:
                    question = self.create_question(
                        "Enter the version constraint to require "
                        "(or leave blank to use the latest version):"
                    )
                    question.set_max_attempts(3)
                    question.set_validator(lambda x: (x or "").strip() or None)

                    package_constraint = self.ask(question)

                    if package_constraint is None:
                        _, package_constraint = self._find_best_version_for_package(
                            package
                        )

                        self.line(
                            f"Using version <b>{package_constraint}</b> for"
                            f" <c1>{package}</c1>"
                        )

                    constraint["version"] = package_constraint

                if package:
                    result.append(constraint)

                if is_interactive:
                    package = self.ask(follow_up_question)

            return result

        result = []
        for requirement in self._parse_requirements(requires):
            if "git" in requirement or "url" in requirement or "path" in requirement:
                result.append(requirement)
                continue
            elif "version" not in requirement:
                # determine the best version automatically
                name, version = self._find_best_version_for_package(
                    requirement["name"],
                    allow_prereleases=allow_prereleases,
                    source=source,
                )
                requirement["version"] = version
                requirement["name"] = name

                self.line(f"Using version <b>{version}</b> for <c1>{name}</c1>")
            else:
                # check that the specified version/constraint exists
                # before we proceed
                name, _ = self._find_best_version_for_package(
                    requirement["name"],
                    requirement["version"],
                    allow_prereleases=allow_prereleases,
                    source=source,
                )

                requirement["name"] = name

            result.append(requirement)

        return result

    def _find_best_version_for_package(
        self,
        name: str,
        required_version: str | None = None,
        allow_prereleases: bool | None = None,
        source: str | None = None,
    ) -> tuple[str, str]:
        from poetry.version.version_selector import VersionSelector

        selector = VersionSelector(self._get_pool())
        package = selector.find_best_candidate(
            name, required_version, allow_prereleases=allow_prereleases, source=source
        )

        if not package:
            # TODO: find similar
            raise ValueError(f"Could not find a matching version of package {name}")

        version = package.version.without_local()
        return package.pretty_name, f"^{version.to_string()}"

    def _parse_requirements(self, requirements: list[str]) -> list[dict[str, Any]]:
        from poetry.core.pyproject.exceptions import PyProjectError

        try:
            cwd = self.poetry.file.path.parent
            artifact_cache = self.poetry.pool.artifact_cache
        except (PyProjectError, RuntimeError):
            cwd = Path.cwd()
            artifact_cache = self._get_pool().artifact_cache

        parser = RequirementsParser(
            artifact_cache=artifact_cache,
            env=self.env if isinstance(self, EnvCommand) else None,
            cwd=cwd,
        )
        return [
            parser.parse(re.sub(r"@\s*latest$", "", requirement, flags=re.I))
            for requirement in requirements
        ]

    def _format_requirements(self, requirements: list[dict[str, str]]) -> Requirements:
        requires: Requirements = {}
        for requirement in requirements:
            name = requirement.pop("name")
            constraint: str | InlineTable
            if "version" in requirement and len(requirement) == 1:
                constraint = requirement["version"]
            else:
                constraint = inline_table()
                constraint.trivia.trail = "\n"
                constraint.update(requirement)

            requires[name] = constraint

        return requires

    @staticmethod
    def _validate_author(author: str, default: str) -> str | None:
        from poetry.core.utils.helpers import combine_unicode
        from poetry.core.utils.patterns import AUTHOR_REGEX

        author = combine_unicode(author or default)

        if author in ["n", "no"]:
            return None

        m = AUTHOR_REGEX.match(author)
        if not m:
            raise ValueError(
                "Invalid author string. Must be in the format: "
                "John Smith <john@example.com>"
            )

        return author

    @staticmethod
    def _validate_package(package: str | None) -> str | None:
        if package and len(package.split()) > 2:
            raise ValueError("Invalid package definition.")

        return package

    def _get_pool(self) -> RepositoryPool:
        from poetry.config.config import Config
        from poetry.repositories import RepositoryPool
        from poetry.repositories.pypi_repository import PyPiRepository

        if isinstance(self, EnvCommand):
            return self.poetry.pool

        if self._pool is None:
            self._pool = RepositoryPool()
            pool_size = Config.create().installer_max_workers
            self._pool.add_repository(PyPiRepository(pool_size=pool_size))

        return self._pool
