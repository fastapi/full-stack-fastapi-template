from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from poetry.core.packages.dependency import Dependency
    from poetry.core.packages.package import Package


class DependencyPackage:
    def __init__(self, dependency: Dependency, package: Package) -> None:
        self._dependency = dependency
        self._package = package

    @property
    def dependency(self) -> Dependency:
        return self._dependency

    @property
    def package(self) -> Package:
        return self._package

    def clone(self) -> DependencyPackage:
        return self.__class__(self._dependency, self._package.clone())

    def with_features(self, features: list[str]) -> DependencyPackage:
        return self.__class__(self._dependency, self._package.with_features(features))

    def without_features(self) -> DependencyPackage:
        return self.with_features([])

    def __str__(self) -> str:
        return str(self._package)

    def __repr__(self) -> str:
        return repr(self._package)

    def __hash__(self) -> int:
        return hash(self._package)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DependencyPackage):
            other = other.package

        equal: bool = self._package == other
        return equal
