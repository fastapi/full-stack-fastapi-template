from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from poetry.core.constraints.version import parse_constraint


if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Sequence

    from poetry.core.constraints.version import Version
    from poetry.core.packages.dependency import Dependency

from poetry.core.packages.package import Package


class ProjectPackage(Package):
    def __init__(
        self,
        name: str,
        version: str | Version,
    ) -> None:
        super().__init__(name, version)

        # Attributes must be immutable for clone() to be safe!
        # (For performance reasons, clone only creates a copy instead of a deep copy).

        self.build_config: Mapping[str, Any] = {}
        self.packages: Sequence[Mapping[str, Any]] = []
        self.include: Sequence[Mapping[str, Any]] = []
        self.exclude: Sequence[Mapping[str, Any]] = []
        self.custom_urls: Mapping[str, str] = {}
        self._requires_python: str = "*"
        self.dynamic_classifiers = True

        self.entry_points: Mapping[str, dict[str, str]] = {}

        if self._python_versions == "*":
            self._python_constraint = parse_constraint("~2.7 || >=3.4")

    @property
    def build_script(self) -> str | None:
        return self.build_config.get("script")

    def is_root(self) -> bool:
        return True

    def to_dependency(self) -> Dependency:
        dependency = super().to_dependency()

        dependency.is_root = True

        return dependency

    @property
    def requires_python(self) -> str:
        return self._requires_python

    @requires_python.setter
    def requires_python(self, value: str) -> None:
        self._requires_python = value
        self.python_versions = value

    @property
    def python_versions(self) -> str:
        return self._python_versions

    @python_versions.setter
    def python_versions(self, value: str) -> None:
        self._python_versions = value

        if value == "*":
            if self._requires_python != "*":
                raise ValueError(
                    f'The Python constraint in [tool.poetry.dependencies] "{value}"'
                    ' is not a subset of "requires-python" in [project]'
                    f' "{self._requires_python}"'
                )
            value = "~2.7 || >=3.4"

        self._python_constraint = parse_constraint(value)
        if not parse_constraint(self._requires_python).allows_all(
            self._python_constraint
        ):
            raise ValueError(
                f'The Python constraint in [tool.poetry.dependencies] "{value}"'
                ' is not a subset of "requires-python" in [project]'
                f' "{self._requires_python}"'
            )

    @property
    def version(self) -> Version:
        # override version to make it settable
        return super().version

    @version.setter
    def version(self, value: str | Version) -> None:
        self._set_version(value)

    @property
    def all_classifiers(self) -> list[str]:
        if self.dynamic_classifiers:
            return super().all_classifiers

        return list(self.classifiers)

    @property
    def urls(self) -> dict[str, str]:
        urls = super().urls

        urls.update(self.custom_urls)

        return urls

    def __hash__(self) -> int:
        # The parent Package class's __hash__ incorporates the version because
        # a Package's version is immutable. But a ProjectPackage's version is
        # mutable. So call Package's parent hash function.
        return super(Package, self).__hash__()

    def build_should_generate_setup(self) -> bool:
        value: bool = self.build_config.get("generate-setup-file", False)
        return value
