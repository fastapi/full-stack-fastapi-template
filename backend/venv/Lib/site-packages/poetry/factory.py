from __future__ import annotations

import contextlib
import logging
import re

from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from cleo.io.null_io import NullIO
from packaging.utils import canonicalize_name
from poetry.core.constraints.version import Version
from poetry.core.constraints.version import parse_constraint
from poetry.core.factory import Factory as BaseFactory
from poetry.core.packages.dependency_group import MAIN_GROUP

from poetry.__version__ import __version__
from poetry.config.config import Config
from poetry.exceptions import PoetryError
from poetry.json import validate_object
from poetry.packages.locker import Locker
from poetry.plugins.plugin import Plugin
from poetry.plugins.plugin_manager import PluginManager
from poetry.poetry import Poetry
from poetry.toml.file import TOMLFile


if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from cleo.io.io import IO
    from poetry.core.packages.package import Package
    from tomlkit.toml_document import TOMLDocument

    from poetry.repositories import RepositoryPool
    from poetry.repositories.http_repository import HTTPRepository
    from poetry.utils.dependency_specification import DependencySpec

logger = logging.getLogger(__name__)


class Factory(BaseFactory):
    """
    Factory class to create various elements needed by Poetry.
    """

    def create_poetry(
        self,
        cwd: Path | None = None,
        with_groups: bool = True,
        io: IO | None = None,
        disable_plugins: bool = False,
        disable_cache: bool = False,
    ) -> Poetry:
        if io is None:
            io = NullIO()

        base_poetry = super().create_poetry(cwd=cwd, with_groups=with_groups)

        if version_str := base_poetry.local_config.get("requires-poetry"):
            version_constraint = parse_constraint(version_str)
            version = Version.parse(__version__)
            if not version_constraint.allows(version):
                raise PoetryError(
                    f"This project requires Poetry {version_constraint},"
                    f" but you are using Poetry {version}"
                )

        poetry_file = base_poetry.pyproject_path
        locker = Locker(poetry_file.parent / "poetry.lock", base_poetry.pyproject.data)

        # Loading global configuration
        config = Config.create()

        # Loading local configuration
        local_config_file = TOMLFile(poetry_file.parent / "poetry.toml")
        if local_config_file.exists():
            if io.is_debug():
                io.write_line(f"Loading configuration file {local_config_file.path}")

            config.merge(local_config_file.read())

        # Load local sources
        repositories = {}
        existing_repositories = config.get("repositories", {})
        for source in base_poetry.local_config.get("source", []):
            name = source.get("name")
            url = source.get("url")
            if name and url and name not in existing_repositories:
                repositories[name] = {"url": url}

        config.merge({"repositories": repositories})

        poetry = Poetry(
            poetry_file,
            base_poetry.local_config,
            base_poetry.package,
            locker,
            config,
            disable_cache,
        )

        poetry.set_pool(
            self.create_pool(
                config,
                poetry.local_config.get("source", []),
                io,
                disable_cache=disable_cache,
            )
        )

        if not disable_plugins:
            plugin_manager = PluginManager(Plugin.group)
            plugin_manager.load_plugins()
            plugin_manager.activate(poetry, io)

        return poetry

    @classmethod
    def create_pool(
        cls,
        config: Config,
        sources: Iterable[dict[str, Any]] = (),
        io: IO | None = None,
        disable_cache: bool = False,
    ) -> RepositoryPool:
        from poetry.repositories import RepositoryPool
        from poetry.repositories.repository_pool import Priority

        if io is None:
            io = NullIO()

        if disable_cache:
            logger.debug("Disabling source caches")

        pool = RepositoryPool(config=config)

        explicit_pypi = False
        for source in sources:
            repository = cls.create_package_source(
                source, config, disable_cache=disable_cache
            )
            priority = Priority[source.get("priority", Priority.PRIMARY.name).upper()]

            if io.is_debug():
                io.write_line(
                    f"Adding repository {repository.name} ({repository.url})"
                    f" and setting it as {priority.name.lower()}"
                )

            pool.add_repository(repository, priority=priority)
            if repository.name.lower() == "pypi":
                explicit_pypi = True

        # Only add PyPI if no primary repository is configured
        if not explicit_pypi:
            if pool.has_primary_repositories():
                if io.is_debug():
                    io.write_line("Deactivating the PyPI repository")
            else:
                pool.add_repository(
                    cls.create_package_source(
                        {"name": "pypi"}, config, disable_cache=disable_cache
                    ),
                    priority=Priority.PRIMARY,
                )

        if not pool.repositories:
            raise PoetryError(
                "At least one source must not be configured as 'explicit'."
            )

        return pool

    @classmethod
    def create_package_source(
        cls, source: dict[str, str], config: Config, disable_cache: bool = False
    ) -> HTTPRepository:
        from poetry.repositories.exceptions import InvalidSourceError
        from poetry.repositories.legacy_repository import LegacyRepository
        from poetry.repositories.pypi_repository import PyPiRepository
        from poetry.repositories.single_page_repository import SinglePageRepository

        try:
            name = source["name"]
        except KeyError:
            raise InvalidSourceError("Missing [name] in source.")

        pool_size = config.installer_max_workers

        if name.lower() == "pypi":
            if "url" in source:
                raise InvalidSourceError(
                    "The PyPI repository cannot be configured with a custom url."
                )
            return PyPiRepository(
                config=config,
                disable_cache=disable_cache,
                pool_size=pool_size,
            )

        try:
            url = source["url"]
        except KeyError:
            raise InvalidSourceError(f"Missing [url] in source {name!r}.")

        repository_class = LegacyRepository

        if re.match(r".*\.(htm|html)$", url):
            repository_class = SinglePageRepository

        return repository_class(
            name,
            url,
            config=config,
            disable_cache=disable_cache,
            pool_size=pool_size,
        )

    @classmethod
    def create_pyproject_from_package(cls, package: Package) -> TOMLDocument:
        import tomlkit

        from poetry.utils.dependency_specification import dependency_to_specification

        pyproject: dict[str, Any] = tomlkit.document()

        pyproject["tool"] = tomlkit.table(is_super_table=True)

        content: dict[str, Any] = tomlkit.table()
        pyproject["tool"]["poetry"] = content

        content["name"] = package.name
        content["version"] = package.version.text
        content["description"] = package.description
        content["authors"] = package.authors
        content["license"] = package.license.id if package.license else ""

        if package.classifiers:
            content["classifiers"] = package.classifiers

        if package.documentation_url:
            content["documentation"] = package.documentation_url

        if package.repository_url:
            content["repository"] = package.repository_url

        if package.homepage:
            content["homepage"] = package.homepage

        if package.maintainers:
            content["maintainers"] = package.maintainers

        if package.keywords:
            content["keywords"] = package.keywords

        readmes = []

        for readme in package.readmes:
            readme_posix_path = readme.as_posix()

            with contextlib.suppress(ValueError):
                if package.root_dir:
                    readme_posix_path = readme.relative_to(package.root_dir).as_posix()

            readmes.append(readme_posix_path)

        if readmes:
            content["readme"] = readmes

        optional_dependencies = set()
        extras_section = None

        if package.extras:
            extras_section = tomlkit.table()

            for extra in package.extras:
                _dependencies = []
                for dependency in package.extras[extra]:
                    _dependencies.append(dependency.name)
                    optional_dependencies.add(dependency.name)

                extras_section[extra] = _dependencies

        optional_dependencies = set(optional_dependencies)
        dependency_section = content["dependencies"] = tomlkit.table()
        dependency_section["python"] = package.python_versions

        for dep in package.all_requires:
            constraint: DependencySpec | str = dependency_to_specification(
                dep, tomlkit.inline_table()
            )

            if not isinstance(constraint, str):
                if dep.name in optional_dependencies:
                    constraint["optional"] = True

                if len(constraint) == 1 and "version" in constraint:
                    assert isinstance(constraint["version"], str)
                    constraint = constraint["version"]
                elif not constraint:
                    constraint = "*"

            for group in dep.groups:
                if group == MAIN_GROUP:
                    dependency_section[dep.name] = constraint
                else:
                    if "group" not in content:
                        content["group"] = tomlkit.table(is_super_table=True)

                    if group not in content["group"]:
                        content["group"][group] = tomlkit.table(is_super_table=True)

                    if "dependencies" not in content["group"][group]:
                        content["group"][group]["dependencies"] = tomlkit.table()

                    content["group"][group]["dependencies"][dep.name] = constraint

        if extras_section:
            content["extras"] = extras_section

        pyproject = cast("TOMLDocument", pyproject)

        return pyproject

    @classmethod
    def validate(
        cls, toml_data: dict[str, Any], strict: bool = False
    ) -> dict[str, list[str]]:
        results = super().validate(toml_data, strict)
        poetry_config = toml_data["tool"]["poetry"]

        results["errors"].extend(validate_object(poetry_config))

        # A project should not depend on itself.
        # TODO: consider [project.dependencies] and [project.optional-dependencies]
        dependencies = set(poetry_config.get("dependencies", {}).keys())
        dependencies.update(poetry_config.get("dev-dependencies", {}).keys())
        groups = poetry_config.get("group", {}).values()
        for group in groups:
            dependencies.update(group.get("dependencies", {}).keys())

        dependencies = {canonicalize_name(d) for d in dependencies}

        project_name = toml_data.get("project", {}).get("name") or poetry_config.get(
            "name"
        )
        if project_name is not None and canonicalize_name(project_name) in dependencies:
            results["errors"].append(
                f"Project name ({project_name}) is same as one of its dependencies"
            )

        return results
