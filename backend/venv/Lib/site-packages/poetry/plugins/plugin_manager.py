from __future__ import annotations

import hashlib
import json
import logging
import shutil
import sys

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

import tomlkit

from poetry.core.packages.project_package import ProjectPackage

from poetry.__version__ import __version__
from poetry.installation import Installer
from poetry.packages import Locker
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.plugins.plugin import Plugin
from poetry.repositories.installed_repository import InstalledRepository
from poetry.toml import TOMLFile
from poetry.utils._compat import metadata
from poetry.utils._compat import tomllib
from poetry.utils.env import Env
from poetry.utils.env import EnvManager


if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from cleo.io.io import IO
    from poetry.core.packages.dependency import Dependency
    from poetry.core.packages.package import Package

    from poetry.poetry import Poetry


logger = logging.getLogger(__name__)


class PluginManager:
    """
    This class registers and activates plugins.
    """

    def __init__(self, group: str) -> None:
        self._group = group
        self._plugins: list[Plugin] = []

    @staticmethod
    def add_project_plugin_path(directory: Path) -> None:
        from poetry.factory import Factory

        try:
            pyproject_toml = Factory.locate(directory)
        except RuntimeError:
            # no pyproject.toml -> no project plugins
            return

        plugin_path = pyproject_toml.parent / ProjectPluginCache.PATH
        if plugin_path.exists():
            EnvManager.get_system_env(naive=True).sys_path.insert(0, str(plugin_path))

    @classmethod
    def ensure_project_plugins(cls, poetry: Poetry, io: IO) -> None:
        ProjectPluginCache(poetry, io).ensure_plugins()

    def load_plugins(self) -> None:
        plugin_entrypoints = self.get_plugin_entry_points()

        for ep in plugin_entrypoints:
            self._load_plugin_entry_point(ep)

    def get_plugin_entry_points(self) -> list[metadata.EntryPoint]:
        return list(metadata.entry_points(group=self._group))

    def activate(self, *args: Any, **kwargs: Any) -> None:
        for plugin in self._plugins:
            plugin.activate(*args, **kwargs)

    def _add_plugin(self, plugin: Plugin) -> None:
        if not isinstance(plugin, (Plugin, ApplicationPlugin)):
            raise ValueError(
                "The Poetry plugin must be an instance of Plugin or ApplicationPlugin"
            )

        self._plugins.append(plugin)

    def _load_plugin_entry_point(self, ep: metadata.EntryPoint) -> None:
        logger.debug("Loading the %s plugin", ep.name)

        plugin = ep.load()

        if not issubclass(plugin, (Plugin, ApplicationPlugin)):
            raise ValueError(
                "The Poetry plugin must be an instance of Plugin or ApplicationPlugin"
            )

        self._add_plugin(plugin())


class ProjectPluginCache:
    PATH = Path(".poetry") / "plugins"

    def __init__(self, poetry: Poetry, io: IO) -> None:
        self._poetry = poetry
        self._io = io
        self._path = poetry.pyproject_path.parent / self.PATH
        self._config_file = self._path / "config.toml"
        self._gitignore_file = self._path.parent / ".gitignore"

    @property
    def _plugin_section(self) -> dict[str, Any]:
        plugins = self._poetry.local_config.get("requires-plugins", {})
        assert isinstance(plugins, dict)
        return plugins

    @cached_property
    def _config(self) -> dict[str, Any]:
        return {
            "python": sys.version,
            "poetry": __version__,
            "plugins-hash": hashlib.sha256(
                json.dumps(self._plugin_section, sort_keys=True).encode()
            ).hexdigest(),
        }

    def ensure_plugins(self) -> None:
        from poetry.factory import Factory

        # parse project plugins
        plugins = []
        for name, constraints in self._plugin_section.items():
            _constraints = (
                constraints if isinstance(constraints, list) else [constraints]
            )
            for _constraint in _constraints:
                plugins.append(Factory.create_dependency(name, _constraint))

        if not plugins:
            if self._path.exists():
                self._io.write_line(
                    "<info>No project plugins defined."
                    " Removing the project's plugin cache</info>"
                )
                self._io.write_line("")
                shutil.rmtree(self._path)
            return

        if self._is_fresh():
            if self._io.is_debug():
                self._io.write_line("The project's plugin cache is up to date.")
                self._io.write_line("")
            return
        elif self._path.exists():
            self._io.write_line(
                "Removing the project's plugin cache because it is outdated"
            )
            # Just remove the cache for two reasons:
            # 1. Since the path of the cache has already been added to sys.path
            #    at this point, we had to distinguish between packages installed
            #    directly into Poetry's env and packages installed in the project cache.
            # 2. Updating packages in the cache does not work out of the box,
            #    probably, because we use pip to uninstall and pip does not know
            #    about the cache so that we end up with just overwriting installed
            #    packages and multiple dist-info folders per package.
            # In sum, we keep it simple by always starting from an empty cache
            # if something has changed.
            shutil.rmtree(self._path)

        # determine plugins relevant for Poetry's environment
        poetry_env = EnvManager.get_system_env(naive=True)
        relevant_plugins = {
            plugin.name: plugin
            for plugin in plugins
            if plugin.marker.validate(poetry_env.marker_env)
        }
        if not relevant_plugins:
            if self._io.is_debug():
                self._io.write_line(
                    "No relevant project plugins for Poetry's environment defined."
                )
                self._io.write_line("")
            self._write_config()
            return

        self._io.write_line(
            "<info>Ensuring that the Poetry plugins required"
            " by the project are available...</info>"
        )

        # check if required plugins are already available
        missing_plugin_count = len(relevant_plugins)
        satisfied_plugins = set()
        insufficient_plugins = []
        installed_packages = []
        installed_repo = InstalledRepository.load(poetry_env)
        for package in installed_repo.packages:
            if required_plugin := relevant_plugins.get(package.name):
                if package.satisfies(required_plugin):
                    satisfied_plugins.add(package.name)
                    installed_packages.append(package)
                else:
                    insufficient_plugins.append((package, required_plugin))
                    # Do not add the package to installed_packages so that
                    # the solver does not consider it.
                missing_plugin_count -= 1
                if missing_plugin_count == 0:
                    break
            else:
                installed_packages.append(package)

        if missing_plugin_count == 0 and not insufficient_plugins:
            # all required plugins are installed and satisfy the requirements
            self._write_config()
            self._io.write_line(
                "All required plugins have already been installed"
                " in Poetry's environment."
            )
            self._io.write_line("")
            return

        if insufficient_plugins and self._io.is_debug():
            plugins_str = "\n".join(
                f"  - {req}\n    installed: {p}" for p, req in insufficient_plugins
            )
            self._io.write_line(
                "The following Poetry plugins are required by the project"
                f" but are not satisfied by the installed versions:\n{plugins_str}"
            )

        # install missing plugins
        missing_plugins = [
            plugin
            for name, plugin in relevant_plugins.items()
            if name not in satisfied_plugins
        ]
        plugins_str = "\n".join(f"  - {p}" for p in missing_plugins)
        self._io.write_line(
            "The following Poetry plugins are required by the project"
            f" but are not installed in Poetry's environment:\n{plugins_str}\n"
            f"Installing Poetry plugins only for the current project..."
        )
        self._install(missing_plugins, poetry_env, installed_packages)
        self._io.write_line("")
        self._write_config()

    def _is_fresh(self) -> bool:
        if not self._config_file.exists():
            return False

        with self._config_file.open("rb") as f:
            stored_config = tomllib.load(f)

        return stored_config == self._config

    def _install(
        self,
        plugins: Sequence[Dependency],
        poetry_env: Env,
        locked_packages: Sequence[Package],
    ) -> None:
        project = ProjectPackage(name="poetry-project-instance", version="0")
        project.python_versions = ".".join(str(v) for v in poetry_env.version_info[:3])
        # consider all packages in Poetry's environment pinned
        for package in locked_packages:
            project.add_dependency(package.to_dependency())
        # add missing plugin dependencies
        for dependency in plugins:
            project.add_dependency(dependency)

        # force new package to be installed in the project cache instead of Poetry's env
        poetry_env.set_paths(purelib=self._path, platlib=self._path)

        self._ensure_cache_directory()

        installer = Installer(
            self._io,
            poetry_env,
            project,
            Locker(self._path / "poetry.lock", {}),
            self._poetry.pool,
            self._poetry.config,
            # Build installed repository from locked packages so that plugins
            # that may be overwritten are not included.
            InstalledRepository(locked_packages),
        )
        installer.update(True)

        if installer.run() != 0:
            raise RuntimeError("Failed to install required Poetry plugins")

    def _write_config(self) -> None:
        self._ensure_cache_directory()

        document = tomlkit.document()

        for key, value in self._config.items():
            document[key] = value

        TOMLFile(self._config_file).write(data=document)

    def _ensure_cache_directory(self) -> None:
        if self._path.exists():
            return

        self._path.mkdir(parents=True, exist_ok=True)
        # only write .gitignore if path did not exist before
        self._gitignore_file.write_text("*", encoding="utf-8")
