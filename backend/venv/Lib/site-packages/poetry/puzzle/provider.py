from __future__ import annotations

import functools
import itertools
import logging
import re
import time

from collections import defaultdict
from contextlib import contextmanager
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import cast

from cleo.ui.progress_indicator import ProgressIndicator
from poetry.core.constraints.version import EmptyConstraint
from poetry.core.constraints.version import Version
from poetry.core.constraints.version import VersionRange
from poetry.core.packages.utils.utils import get_python_constraint_from_marker
from poetry.core.version.markers import AnyMarker
from poetry.core.version.markers import parse_marker
from poetry.core.version.markers import union as marker_union

from poetry.mixology.incompatibility import Incompatibility
from poetry.mixology.incompatibility_cause import DependencyCauseError
from poetry.mixology.incompatibility_cause import PythonCauseError
from poetry.mixology.term import Term
from poetry.packages import DependencyPackage
from poetry.packages.direct_origin import DirectOrigin
from poetry.packages.package_collection import PackageCollection
from poetry.puzzle.exceptions import OverrideNeededError
from poetry.utils.helpers import get_file_hash


if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Collection
    from collections.abc import Iterable
    from collections.abc import Iterator
    from pathlib import Path

    from cleo.io.io import IO
    from packaging.utils import NormalizedName
    from poetry.core.constraints.version import VersionConstraint
    from poetry.core.packages.dependency import Dependency
    from poetry.core.packages.directory_dependency import DirectoryDependency
    from poetry.core.packages.file_dependency import FileDependency
    from poetry.core.packages.package import Package
    from poetry.core.packages.url_dependency import URLDependency
    from poetry.core.packages.vcs_dependency import VCSDependency
    from poetry.core.version.markers import BaseMarker

    from poetry.repositories import RepositoryPool
    from poetry.utils.env import Env


logger = logging.getLogger(__name__)


class IncompatibleConstraintsError(Exception):
    """
    Exception when there are duplicate dependencies with incompatible constraints.
    """

    def __init__(
        self, package: Package, *dependencies: Dependency, with_sources: bool = False
    ) -> None:
        constraints = []
        for dep in dependencies:
            constraint = dep.to_pep_508()
            if dep.is_direct_origin():
                # add version info because issue might be a version conflict
                # with a version constraint
                constraint += f" ({dep.constraint})"
            if with_sources and dep.source_name:
                constraint += f" ; source={dep.source_name}"
            constraints.append(constraint)
        super().__init__(
            f"Incompatible constraints in requirements of {package}:\n"
            + "\n".join(constraints)
        )


class Indicator(ProgressIndicator):
    CONTEXT: str | None = None

    @staticmethod
    @contextmanager
    def context() -> Iterator[Callable[[str | None], None]]:
        def _set_context(context: str | None) -> None:
            Indicator.CONTEXT = context

        yield _set_context

        _set_context(None)

    def _formatter_context(self) -> str:
        if Indicator.CONTEXT is None:
            return " "
        else:
            return f" <c1>{Indicator.CONTEXT}</> "

    def _formatter_elapsed(self) -> str:
        assert self._start_time is not None
        elapsed = time.time() - self._start_time

        return f"{elapsed:.1f}s"


class Provider:
    UNSAFE_PACKAGES: ClassVar[set[str]] = set()

    def __init__(
        self,
        package: Package,
        pool: RepositoryPool,
        io: IO,
        *,
        locked: list[Package] | None = None,
        active_root_extras: Collection[NormalizedName] | None = None,
    ) -> None:
        self._package = package
        self._pool = pool
        self._direct_origin = DirectOrigin(self._pool.artifact_cache)
        self._io = io
        self._env: Env | None = None
        self._package_python_constraint = package.python_constraint
        self._is_debugging: bool = self._io.is_debug() or self._io.is_very_verbose()
        self._overrides: dict[Package, dict[str, Dependency]] = {}
        self._deferred_cache: dict[Dependency, Package] = {}
        self._load_deferred = True
        self._source_root: Path | None = None
        self._direct_origin_packages: dict[str, Package] = {}
        self._locked: dict[NormalizedName, list[DependencyPackage]] = defaultdict(list)
        self._use_latest: Collection[NormalizedName] = []
        self._active_root_extras = (
            frozenset(active_root_extras) if active_root_extras is not None else None
        )

        self._explicit_sources: dict[str, str] = {}
        for package in locked or []:
            self._locked[package.name].append(
                DependencyPackage(package.to_dependency(), package)
            )
        for dependency_packages in self._locked.values():
            dependency_packages.sort(
                key=lambda p: p.package.version,
                reverse=True,
            )

        self.get_package_from_pool = functools.cache(self._pool.package)

    @property
    def pool(self) -> RepositoryPool:
        return self._pool

    @property
    def use_latest(self) -> Collection[NormalizedName]:
        return self._use_latest

    @functools.cached_property
    def _overrides_marker_intersection(self) -> BaseMarker:
        overrides_marker_intersection: BaseMarker = AnyMarker()
        for dep_overrides in self._overrides.values():
            for dep in dep_overrides.values():
                overrides_marker_intersection = overrides_marker_intersection.intersect(
                    dep.marker
                )
        return overrides_marker_intersection

    @functools.cached_property
    def _python_constraint(self) -> VersionConstraint:
        return self._package_python_constraint.intersect(
            get_python_constraint_from_marker(self._overrides_marker_intersection)
        )

    def is_debugging(self) -> bool:
        return self._is_debugging

    def set_overrides(self, overrides: dict[Package, dict[str, Dependency]]) -> None:
        self._overrides = overrides
        self.__dict__.pop("_python_constraint", None)
        self.__dict__.pop("_overrides_marker_intersection", None)

    def load_deferred(self, load_deferred: bool) -> None:
        self._load_deferred = load_deferred

    @contextmanager
    def use_source_root(self, source_root: Path) -> Iterator[Provider]:
        original_source_root = self._source_root
        self._source_root = source_root

        try:
            yield self
        finally:
            self._source_root = original_source_root

    @contextmanager
    def use_environment(self, env: Env) -> Iterator[Provider]:
        original_python_constraint = self._package_python_constraint

        self._env = env
        self._package_python_constraint = Version.parse(
            env.marker_env["python_full_version"]
        )

        try:
            yield self
        finally:
            self._env = None
            self._package_python_constraint = original_python_constraint

    @contextmanager
    def use_latest_for(self, names: Collection[NormalizedName]) -> Iterator[Provider]:
        self._use_latest = names

        try:
            yield self
        finally:
            self._use_latest = []

    @staticmethod
    def validate_package_for_dependency(
        dependency: Dependency, package: Package
    ) -> None:
        if dependency.name != package.name:
            # For now, the dependency's name must match the actual package's name
            raise RuntimeError(
                f"The dependency name for {dependency.name} does not match the actual"
                f" package's name: {package.name}"
            )

    def search_for_direct_origin_dependency(self, dependency: Dependency) -> Package:
        package = self._deferred_cache.get(dependency)
        if package is not None:
            pass

        elif dependency.is_vcs():
            dependency = cast("VCSDependency", dependency)
            package = self._search_for_vcs(dependency)

        elif dependency.is_file():
            dependency = cast("FileDependency", dependency)
            package = self._search_for_file(dependency)

        elif dependency.is_directory():
            dependency = cast("DirectoryDependency", dependency)
            package = self._search_for_directory(dependency)

        elif dependency.is_url():
            dependency = cast("URLDependency", dependency)
            package = self._search_for_url(dependency)

        else:
            raise RuntimeError(
                f"{dependency}: unknown direct dependency type {dependency.source_type}"
            )

        if dependency.is_vcs():
            dependency._source_reference = package.source_reference
            dependency._source_resolved_reference = package.source_resolved_reference
            dependency._source_subdirectory = package.source_subdirectory

        dependency._constraint = package.version
        dependency._pretty_constraint = package.version.text

        self._deferred_cache[dependency] = package

        return package

    def search_for(self, dependency: Dependency) -> list[DependencyPackage]:
        """
        Search for the specifications that match the given dependency.

        The specifications in the returned list will be considered in reverse
        order, so the latest version ought to be last.
        """
        if dependency.is_root:
            return PackageCollection(dependency, [self._package])

        if dependency.is_direct_origin():
            package = self.search_for_direct_origin_dependency(dependency)
            self._direct_origin_packages[dependency.name] = package
            return PackageCollection(dependency, [package])

        # If we've previously found a direct-origin package that meets this dependency,
        # use it.
        #
        # We rely on the VersionSolver resolving direct-origin dependencies first.
        direct_origin_package = self._direct_origin_packages.get(dependency.name)
        if direct_origin_package and direct_origin_package.satisfies(dependency):
            packages = [direct_origin_package]
            return PackageCollection(dependency, packages)

        packages = self._pool.find_packages(dependency)

        packages.sort(
            key=lambda p: (
                not p.yanked,
                not p.is_prerelease() and not dependency.allows_prereleases(),
                p.version,
            ),
            reverse=True,
        )

        return PackageCollection(dependency, packages)

    def _search_for_vcs(self, dependency: VCSDependency) -> Package:
        """
        Search for the specifications that match the given VCS dependency.

        Basically, we clone the repository in a temporary directory
        and get the information we need by checking out the specified reference.
        """
        package = self._direct_origin.get_package_from_vcs(
            dependency.vcs,
            dependency.source,
            branch=dependency.branch,
            tag=dependency.tag,
            rev=dependency.rev,
            subdirectory=dependency.source_subdirectory,
            source_root=self._source_root
            or (self._env.path.joinpath("src") if self._env else None),
        )

        self.validate_package_for_dependency(dependency=dependency, package=package)

        package.develop = dependency.develop

        return package

    def _search_for_file(self, dependency: FileDependency) -> Package:
        dependency.validate(raise_error=True)
        package = self._direct_origin.get_package_from_file(dependency.full_path)

        self.validate_package_for_dependency(dependency=dependency, package=package)

        if dependency.base is not None:
            package.root_dir = dependency.base

        package.files = [
            {
                "file": dependency.path.name,
                "hash": "sha256:" + get_file_hash(dependency.full_path),
            }
        ]

        return package

    def _search_for_directory(self, dependency: DirectoryDependency) -> Package:
        dependency.validate(raise_error=True)
        package = self._direct_origin.get_package_from_directory(dependency.full_path)

        self.validate_package_for_dependency(dependency=dependency, package=package)

        package.develop = dependency.develop

        if dependency.base is not None:
            package.root_dir = dependency.base

        return package

    def _search_for_url(self, dependency: URLDependency) -> Package:
        package = self._direct_origin.get_package_from_url(dependency.url)

        self.validate_package_for_dependency(dependency=dependency, package=package)

        for extra in dependency.extras:
            if extra in package.extras:
                for dep in package.extras[extra]:
                    dep.activate()

                for extra_dep in package.extras[extra]:
                    package.add_dependency(extra_dep)

        return package

    def _get_dependencies_with_overrides(
        self, dependencies: list[Dependency], package: Package
    ) -> list[Dependency]:
        overrides = self._overrides.get(package, {})
        _dependencies = []
        overridden = []
        for dep in dependencies:
            if dep.name in overrides:
                if dep.name in overridden:
                    continue

                # empty constraint is used in overrides to mark that the package has
                # already been handled and is not required for the attached markers
                if not overrides[dep.name].constraint.is_empty():
                    _dependencies.append(overrides[dep.name])
                overridden.append(dep.name)

                continue

            _dependencies.append(dep)
        return _dependencies

    def incompatibilities_for(
        self, dependency_package: DependencyPackage
    ) -> list[Incompatibility]:
        """
        Returns incompatibilities that encapsulate a given package's dependencies,
        or that it can't be safely selected.

        If multiple subsequent versions of this package have the same
        dependencies, this will return incompatibilities that reflect that. It
        won't return incompatibilities that have already been returned by a
        previous call to _incompatibilities_for().
        """
        package = dependency_package.package
        if package.is_root():
            dependencies = package.all_requires
        else:
            dependencies = package.requires

            if not package.python_constraint.allows_all(self._python_constraint):
                transitive_python_constraint = get_python_constraint_from_marker(
                    dependency_package.dependency.transitive_marker
                )
                intersection = package.python_constraint.intersect(
                    transitive_python_constraint
                )
                difference = transitive_python_constraint.difference(intersection)

                # The difference is only relevant if it intersects
                # the root package python constraint
                difference = difference.intersect(self._python_constraint)
                if (
                    transitive_python_constraint.is_any()
                    or self._python_constraint.intersect(
                        dependency_package.dependency.python_constraint
                    ).is_empty()
                    or intersection.is_empty()
                    or not difference.is_empty()
                ):
                    return [
                        Incompatibility(
                            [Term(package.to_dependency(), True)],
                            PythonCauseError(
                                package.python_versions, str(self._python_constraint)
                            ),
                        )
                    ]

        return [
            Incompatibility(
                [Term(package.to_dependency(), True), Term(dep, False)],
                DependencyCauseError(),
            )
            for dep in self._get_dependencies_with_overrides(dependencies, package)
        ]

    def complete_package(
        self, dependency_package: DependencyPackage
    ) -> DependencyPackage:
        package = dependency_package.package
        dependency = dependency_package.dependency

        if package.is_root():
            dependency_package = dependency_package.clone()
            package = dependency_package.package
            dependency = dependency_package.dependency
            requires = package.all_requires
        elif package.is_direct_origin():
            requires = package.requires
        else:
            dependency_package = DependencyPackage(
                dependency,
                self.get_package_from_pool(
                    package.pretty_name,
                    package.version,
                    repository_name=dependency.source_name,
                ),
            )

            package = dependency_package.package
            dependency = dependency_package.dependency
            requires = package.requires

        found_extras = set()
        optional_dependencies = set()
        _dependencies = []

        if dependency.extras:
            # Find all the optional dependencies that are wanted - taking care to allow
            # for self-referential extras.
            stack = list(dependency.extras)
            while stack:
                extra = stack.pop()
                if extra in found_extras:
                    continue
                found_extras.add(extra)

                extra_dependencies = package.extras.get(extra, [])
                for extra_dependency in extra_dependencies:
                    if extra_dependency.name == dependency.name:
                        stack += list(extra_dependency.extras)
                    else:
                        optional_dependencies.add(extra_dependency.name)

            # If some extras/features were required, we need to add a special dependency
            # representing the base package to the current package.

            dependency_package = dependency_package.with_features(
                list(dependency.extras)
            )
            package = dependency_package.package
            dependency = dependency_package.dependency
            new_dependency = package.without_features().to_dependency()
            new_dependency.marker = dependency.marker

            # When adding dependency foo[extra] -> foo, preserve foo's source, if it's
            # specified. This prevents us from trying to get foo from PyPI
            # when user explicitly set repo for foo[extra].
            if not new_dependency.source_name and dependency.source_name:
                new_dependency.source_name = dependency.source_name

            _dependencies.append(new_dependency)

        for dep in requires:
            if not self._python_constraint.allows_any(dep.python_constraint):
                continue

            if dep.name in self.UNSAFE_PACKAGES:
                continue

            if self._env:
                marker_values = (
                    self._marker_values(self._active_root_extras)
                    if package.is_root()
                    else self._env.marker_env
                )
                if not dep.marker.validate(marker_values):
                    continue

            if not package.is_root() and (
                (dep.is_optional() and dep.name not in optional_dependencies)
                or (dep.in_extras and not set(dep.in_extras).intersection(found_extras))
            ):
                continue

            # For normal dependency resolution, we have to make sure that root extras
            # are represented in the markers. This is required to identify mutually
            # exclusive markers in cases like 'extra == "foo"' and 'extra != "foo"'.
            # However, for installation with re-resolving (installer.re-resolve=true,
            # which results in self._env being not None), this spoils the result
            # because we have to keep extras so that they are uninstalled
            # when calculating the operations of the transaction.
            if self._env is None and package.is_root() and dep.in_extras:
                # The clone is required for installation with re-resolving
                # without an existing lock file because the root package is used
                # once for solving and a second time for re-resolving for installation.
                dep = dep.clone()
                dep.marker = dep.marker.intersect(
                    parse_marker(
                        " or ".join(f'extra == "{extra}"' for extra in dep.in_extras)
                    )
                )

            _dependencies.append(dep)

        if self._load_deferred:
            # Retrieving constraints for deferred dependencies
            for dep in _dependencies:
                if dep.is_direct_origin():
                    locked = self.get_locked(dep)
                    # If lock file contains exactly the same URL and reference
                    # (commit hash) of dependency as is requested,
                    # do not analyze it again: nothing could have changed.
                    if locked is not None and locked.package.is_same_package_as(dep):
                        continue
                    self.search_for_direct_origin_dependency(dep)

        dependencies = self._get_dependencies_with_overrides(_dependencies, package)

        # Searching for duplicate dependencies
        #
        # If the duplicate dependencies have the same constraint,
        # the requirements will be merged.
        #
        # For instance:
        #   • enum34; python_version=="2.7"
        #   • enum34; python_version=="3.3"
        #
        # will become:
        #   • enum34; python_version=="2.7" or python_version=="3.3"
        #
        # If the duplicate dependencies have different constraints
        # we have to split the dependency graph.
        #
        # An example of this is:
        #   • pypiwin32 (220); sys_platform == "win32" and python_version >= "3.6"
        #   • pypiwin32 (219); sys_platform == "win32" and python_version < "3.6"
        duplicates: dict[str, list[Dependency]] = defaultdict(list)
        for dep in dependencies:
            duplicates[dep.name].append(dep)

        dependencies = []
        for dep_name, deps in duplicates.items():
            if len(deps) == 1:
                dependencies.append(deps[0])
                continue

            self.debug(f"<debug>Duplicate dependencies for {dep_name}</debug>")

            # For dependency resolution, markers of duplicate dependencies must be
            # mutually exclusive. However, we have to take care about duplicates
            # with differing extras.
            duplicates_by_extras: dict[str, list[Dependency]] = defaultdict(list)
            for dep in deps:
                duplicates_by_extras[dep.complete_name].append(dep)

            if len(duplicates_by_extras) == 1:
                active_extras = (
                    self._active_root_extras if package.is_root() else dependency.extras
                )
                deps = self._resolve_overlapping_markers(package, deps, active_extras)
            else:
                # There are duplicates with different extras.
                for complete_dep_name, deps_by_extra in duplicates_by_extras.items():
                    if len(deps_by_extra) > 1:
                        duplicates_by_extras[complete_dep_name] = (
                            self._resolve_overlapping_markers(
                                package, deps_by_extra, None
                            )
                        )
                if all(len(d) == 1 for d in duplicates_by_extras.values()) and all(
                    d1[0].marker.intersect(d2[0].marker).is_empty()
                    for d1, d2 in itertools.combinations(
                        duplicates_by_extras.values(), 2
                    )
                ):
                    # Since all markers are mutually exclusive,
                    # we can trigger overrides.
                    deps = list(itertools.chain(*duplicates_by_extras.values()))
                else:
                    # Too complicated to handle with overrides,
                    # fallback to basic handling without overrides.
                    for d in duplicates_by_extras.values():
                        dependencies.extend(d)
                    continue

            if len(deps) == 1:
                self.debug(f"<debug>Merging requirements for {dep_name}</debug>")
                dependencies.append(deps[0])
                continue

            # Sort out irrelevant requirements
            deps = [
                dep
                for dep in deps
                if not self._overrides_marker_intersection.intersect(
                    dep.marker
                ).is_empty()
            ]
            if len(deps) < 2:
                if not deps or (len(deps) == 1 and deps[0].constraint.is_empty()):
                    msg = f"<debug>No relevant requirements for {dep_name}</debug>"
                else:
                    msg = f"<debug>Only one relevant requirement for {dep_name}</debug>"
                    dependencies.append(deps[0])
                self.debug(msg)
                continue

            # At this point, we raise an exception that will
            # tell the solver to make new resolutions with specific overrides.
            #
            # For instance, if the foo (1.2.3) package has the following dependencies:
            #   • bar (>=2.0) ; python_version >= "3.6"
            #   • bar (<2.0) ; python_version < "3.6"
            #
            # then the solver will need to make two new resolutions
            # with the following overrides:
            #   • {<Package foo (1.2.3): {"bar": <Dependency bar (>=2.0)>}
            #   • {<Package foo (1.2.3): {"bar": <Dependency bar (<2.0)>}

            def fmt_warning(d: Dependency) -> str:
                dependency_marker = d.marker if not d.marker.is_any() else "*"
                return (
                    f"<c1>{d.name}</c1> <fg=default>(<c2>{d.pretty_constraint}</c2>)</>"
                    f" with markers <b>{dependency_marker}</b>"
                )

            warnings = ", ".join(fmt_warning(d) for d in deps[:-1])
            warnings += f" and {fmt_warning(deps[-1])}"
            self.debug(
                f"<warning>Different requirements found for {warnings}.</warning>"
            )

            overrides = []
            for dep in deps:
                current_overrides = self._overrides.copy()
                package_overrides = current_overrides.get(package, {}).copy()
                package_overrides.update({dep.name: dep})
                current_overrides.update({package: package_overrides})
                overrides.append(current_overrides)

            raise OverrideNeededError(*overrides)

        # Modifying dependencies as needed
        clean_dependencies = []
        for dep in dependencies:
            if not dependency.transitive_marker.without_extras().is_any():
                transitive_marker_intersection = (
                    dependency.transitive_marker.without_extras().intersect(
                        dep.marker.without_extras()
                    )
                )
                if transitive_marker_intersection.is_empty():
                    # The dependency is not needed, since the markers specified
                    # for the current package selection are not compatible with
                    # the markers for the current dependency, so we skip it
                    continue

                dep.transitive_marker = transitive_marker_intersection

            if not dependency.python_constraint.is_any():
                python_constraint_intersection = dep.python_constraint.intersect(
                    dependency.python_constraint
                )
                if python_constraint_intersection.is_empty():
                    # This dependency is not needed under current python constraint.
                    continue

            clean_dependencies.append(dep)

        package = package.with_dependency_groups([], only=True)
        dependency_package = DependencyPackage(dependency, package)

        for dep in clean_dependencies:
            package.add_dependency(dep)

        if self._locked and package.is_root():
            # At this point all duplicates have been eliminated via overrides
            # so that explicit sources are unambiguous.
            # Clear _explicit_sources because it might be filled
            # from a previous override.
            self._explicit_sources.clear()
            for dep in clean_dependencies:
                if dep.source_name:
                    self._explicit_sources[dep.name] = dep.source_name

        return dependency_package

    def get_locked(self, dependency: Dependency) -> DependencyPackage | None:
        if dependency.name in self._use_latest:
            return None

        locked = self._locked.get(dependency.name, [])
        for dependency_package in locked:
            package = dependency_package.package
            if package.satisfies(dependency):
                if explicit_source := self._explicit_sources.get(dependency.name):
                    dependency.source_name = explicit_source
                return DependencyPackage(dependency, package)
        return None

    def debug(self, message: str, depth: int = 0) -> None:
        if not (self._io.is_very_verbose() or self._io.is_debug()):
            return

        if message.startswith("fact:"):
            if "depends on" in message:
                m = re.match(r"fact: (.+?) depends on (.+?) \((.+?)\)", message)
                if m is None:
                    raise ValueError(f"Unable to parse fact: {message}")
                m2 = re.match(r"(.+?) \((.+?)\)", m.group(1))
                if m2:
                    name = m2.group(1)
                    version = f" (<c2>{m2.group(2)}</c2>)"
                else:
                    name = m.group(1)
                    version = ""

                message = (
                    f"<fg=blue>fact</>: <c1>{name}</c1>{version} "
                    f"depends on <c1>{m.group(2)}</c1> (<c2>{m.group(3)}</c2>)"
                )
            elif " is " in message:
                message = re.sub(
                    "fact: (.+) is (.+)",
                    "<fg=blue>fact</>: <c1>\\1</c1> is <c2>\\2</c2>",
                    message,
                )
            else:
                message = re.sub(
                    r"(?<=: )(.+?) \((.+?)\)", "<c1>\\1</c1> (<c2>\\2</c2>)", message
                )
                message = f"<fg=blue>fact</>: {message.split('fact: ')[1]}"
        elif message.startswith("selecting "):
            message = re.sub(
                r"selecting (.+?) \((.+?)\)",
                "<fg=blue>selecting</> <c1>\\1</c1> (<c2>\\2</c2>)",
                message,
            )
        elif message.startswith("derived:"):
            m = re.match(r"derived: (.+?) \((.+?)\)$", message)
            if m:
                message = (
                    f"<fg=blue>derived</>: <c1>{m.group(1)}</c1>"
                    f" (<c2>{m.group(2)}</c2>)"
                )
            else:
                message = (
                    f"<fg=blue>derived</>: <c1>{message.split('derived: ')[1]}</c1>"
                )
        elif message.startswith("conflict:"):
            m = re.match(r"conflict: (.+?) depends on (.+?) \((.+?)\)", message)
            if m:
                m2 = re.match(r"(.+?) \((.+?)\)", m.group(1))
                if m2:
                    name = m2.group(1)
                    version = f" (<c2>{m2.group(2)}</c2>)"
                else:
                    name = m.group(1)
                    version = ""

                message = (
                    f"<fg=red;options=bold>conflict</>: <c1>{name}</c1>{version} "
                    f"depends on <c1>{m.group(2)}</c1> (<c2>{m.group(3)}</c2>)"
                )
            else:
                message = (
                    "<fg=red;options=bold>conflict</>:"
                    f" {message.split('conflict: ')[1]}"
                )

        message = message.replace("! ", "<error>!</error> ")

        if self.is_debugging():
            debug_info = str(message)
            debug_info = (
                "\n".join(
                    [
                        f"<debug>{str(depth).rjust(4)}:</debug> {s}"
                        for s in debug_info.split("\n")
                    ]
                )
                + "\n"
            )

            self._io.write(debug_info)

    def _group_by_source(
        self, dependencies: Iterable[Dependency]
    ) -> list[list[Dependency]]:
        """
        Takes a list of dependencies and returns a list of groups of dependencies,
        each group containing all dependencies from the same source.
        """
        groups: list[list[Dependency]] = []
        for dep in dependencies:
            for group in groups:
                if (
                    dep.is_same_source_as(group[0])
                    and dep.source_name == group[0].source_name
                ):
                    group.append(dep)
                    break
            else:
                groups.append([dep])
        return groups

    def _merge_dependencies_by_constraint(
        self, dependencies: Iterable[Dependency]
    ) -> list[Dependency]:
        """
        Merge dependencies with the same constraint
        by building a union of their markers.

        For instance, if we have:
           - foo (>=2.0) ; python_version >= "3.6" and python_version < "3.7"
           - foo (>=2.0) ; python_version >= "3.7"
        we can avoid two overrides by merging them to:
           - foo (>=2.0) ; python_version >= "3.6"
        """
        dep_groups = self._group_by_source(dependencies)
        merged_dependencies = []
        for group in dep_groups:
            by_constraint: dict[VersionConstraint, list[Dependency]] = defaultdict(list)
            for dep in group:
                by_constraint[dep.constraint].append(dep)
            for deps in by_constraint.values():
                dep = deps[0]
                if len(deps) > 1:
                    new_markers = (dep.marker for dep in deps)
                    dep.marker = marker_union(*new_markers)
                merged_dependencies.append(dep)

        return merged_dependencies

    def _is_relevant_marker(
        self, marker: BaseMarker, active_extras: Collection[NormalizedName] | None
    ) -> bool:
        """
        A marker is relevant if
        - it is not empty
        - allowed by the project's python constraint
        - allowed by active extras of the dependency (not relevant for root package)
        - allowed by the environment (only during installation)
        """
        return (
            not marker.is_empty()
            and self._python_constraint.allows_any(
                get_python_constraint_from_marker(marker)
            )
            and (active_extras is None or marker.validate({"extra": active_extras}))
            and (not self._env or marker.validate(self._env.marker_env))
        )

    def _resolve_overlapping_markers(
        self,
        package: Package,
        dependencies: list[Dependency],
        active_extras: Collection[NormalizedName] | None,
    ) -> list[Dependency]:
        """
        Convert duplicate dependencies with potentially overlapping markers
        into duplicate dependencies with mutually exclusive markers.

        Therefore, the intersections of all combinations of markers and inverted markers
        have to be calculated. If such an intersection is relevant (not empty, etc.),
        the intersection of all constraints, whose markers were not inverted is built
        and a new dependency with the calculated version constraint and marker is added.
        (The marker of such a dependency does not overlap with the marker
        of any other new dependency.)
        """
        # In order to reduce the number of intersections,
        # we merge duplicate dependencies by constraint.
        dependencies = self._merge_dependencies_by_constraint(dependencies)

        new_dependencies = []
        for uses in itertools.product([True, False], repeat=len(dependencies)):
            # intersection of markers
            # For performance optimization, we don't just intersect all markers at once,
            # but intersect them one after the other to get empty markers early.
            # Further, we intersect the inverted markers at last because
            # they are more likely to overlap than the non-inverted ones.
            markers = (
                dep.marker if use else dep.marker.invert()
                for use, dep in sorted(
                    zip(uses, dependencies), key=lambda ud: ud[0], reverse=True
                )
            )
            used_marker_intersection: BaseMarker = AnyMarker()
            for m in markers:
                used_marker_intersection = used_marker_intersection.intersect(m)
            if not self._is_relevant_marker(used_marker_intersection, active_extras):
                continue

            # intersection of constraints
            constraint: VersionConstraint = VersionRange()
            specific_source_dependency = None
            used_dependencies = list(itertools.compress(dependencies, uses))
            for dep in used_dependencies:
                if dep.is_direct_origin() or dep.source_name:
                    # if direct origin or specific source:
                    # conflict if specific source already set and not the same
                    if specific_source_dependency and (
                        not dep.is_same_source_as(specific_source_dependency)
                        or dep.source_name != specific_source_dependency.source_name
                    ):
                        raise IncompatibleConstraintsError(
                            package, dep, specific_source_dependency, with_sources=True
                        )
                    specific_source_dependency = dep
                constraint = constraint.intersect(dep.constraint)
            if constraint.is_empty():
                # conflict in overlapping area
                raise IncompatibleConstraintsError(package, *used_dependencies)

            if not any(uses):
                # This is an edge case where the dependency is not required
                # for the resulting marker. However, we have to consider it anyway
                #  in order to not miss other dependencies later, for instance:
                #   • foo (1.0) ; python == 3.7
                #   • foo (2.0) ; python == 3.8
                #   • bar (2.0) ; python == 3.8
                #   • bar (3.0) ; python == 3.9
                # the last dependency would be missed without this,
                # because the intersection with both foo dependencies is empty.

                # Set constraint to empty to mark dependency as "not required".
                constraint = EmptyConstraint()
                used_dependencies = dependencies

            # build new dependency with intersected constraint and marker
            # (and correct source)
            new_dep = (
                specific_source_dependency
                if specific_source_dependency
                else used_dependencies[0]
            ).with_constraint(constraint)
            new_dep.marker = used_marker_intersection
            new_dependencies.append(new_dep)

        # In order to reduce the number of overrides we merge duplicate
        # dependencies by constraint again. After overlapping markers were
        # resolved, there might be new dependencies with the same constraint.
        return self._merge_dependencies_by_constraint(new_dependencies)

    def _marker_values(
        self, extras: Collection[NormalizedName] | None = None
    ) -> dict[str, Any]:
        """
        Marker values, from `self._env` if present plus the supplied extras

        :param extras: the values to add to the 'extra' marker value
        """
        result = self._env.marker_env.copy() if self._env is not None else {}
        if extras is not None:
            assert "extra" not in result, (
                "'extra' marker key is already present in environment"
            )
            result["extra"] = set(extras)
        return result
