from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.packages.dependency_package import DependencyPackage


if TYPE_CHECKING:
    from collections.abc import Iterable

    from poetry.core.packages.dependency import Dependency
    from poetry.core.packages.package import Package


class PackageCollection(list[DependencyPackage]):
    def __init__(
        self,
        dependency: Dependency,
        packages: Iterable[Package | DependencyPackage] = (),
    ) -> None:
        self._dependency = dependency

        super().__init__()

        for package in packages:
            self.append(package)

    def append(self, package: Package | DependencyPackage) -> None:
        if isinstance(package, DependencyPackage):
            package = package.package

        package = DependencyPackage(self._dependency, package)

        return super().append(package)
