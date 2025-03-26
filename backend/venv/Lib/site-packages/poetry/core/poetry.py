from __future__ import annotations

import logging

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from packaging.utils import canonicalize_name

from poetry.core.packages.dependency import Dependency
from poetry.core.packages.directory_dependency import DirectoryDependency
from poetry.core.packages.file_dependency import FileDependency
from poetry.core.pyproject.toml import PyProjectTOML


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from poetry.core.packages.project_package import ProjectPackage


class Poetry:
    def __init__(
        self,
        file: Path,
        local_config: dict[str, Any],
        package: ProjectPackage,
        pyproject_type: type[PyProjectTOML] = PyProjectTOML,
    ) -> None:
        self._pyproject = pyproject_type(file)
        self._package = package
        self._local_config = local_config
        self._build_system_dependencies: list[Dependency] | None = None

    @property
    def pyproject(self) -> PyProjectTOML:
        return self._pyproject

    @property
    def pyproject_path(self) -> Path:
        return self._pyproject.path

    @property
    def package(self) -> ProjectPackage:
        return self._package

    @property
    def is_package_mode(self) -> bool:
        package_mode = self._local_config["package-mode"]
        assert isinstance(package_mode, bool)
        return package_mode

    @property
    def local_config(self) -> dict[str, Any]:
        return self._local_config

    def get_project_config(self, config: str, default: Any = None) -> Any:
        return self._local_config.get("config", {}).get(config, default)

    @property
    def build_system_dependencies(self) -> list[Dependency]:
        if self._build_system_dependencies is None:
            build_system = self.pyproject.build_system
            self._build_system_dependencies = []

            for requirement in build_system.requires:
                dependency = None
                try:
                    dependency = Dependency.create_from_pep_508(requirement)
                except ValueError:
                    # PEP 517 requires can be path if not PEP 508
                    path = Path(requirement)

                    if path.is_file():
                        dependency = FileDependency(
                            name=canonicalize_name(path.name), path=path
                        )
                    elif path.is_dir():
                        dependency = DirectoryDependency(
                            name=canonicalize_name(path.name), path=path
                        )

                # skip since we could not determine requirement
                if dependency:
                    self._build_system_dependencies.append(dependency)
                else:
                    logger.debug(
                        "Skipping build system dependency - could not determine requirement type: %s",
                        requirement,
                    )

        return self._build_system_dependencies
