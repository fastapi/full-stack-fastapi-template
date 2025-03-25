from __future__ import annotations

import functools
import time

from collections import defaultdict
from contextlib import contextmanager
from typing import TYPE_CHECKING

from poetry.core.version.markers import AnyMarker
from poetry.core.version.markers import EmptyMarker
from poetry.core.version.markers import MultiMarker
from poetry.core.version.markers import SingleMarker
from poetry.core.version.markers import parse_marker

from poetry.mixology import resolve_version
from poetry.mixology.failure import SolveFailureError
from poetry.packages.transitive_package_info import TransitivePackageInfo
from poetry.puzzle.exceptions import OverrideNeededError
from poetry.puzzle.exceptions import SolverProblemError
from poetry.puzzle.provider import Indicator
from poetry.puzzle.provider import Provider


if TYPE_CHECKING:
    from collections.abc import Collection
    from collections.abc import Iterator
    from collections.abc import Sequence

    from cleo.io.io import IO
    from packaging.utils import NormalizedName
    from poetry.core.constraints.version import VersionConstraint
    from poetry.core.packages.dependency import Dependency
    from poetry.core.packages.package import Package
    from poetry.core.packages.project_package import ProjectPackage
    from poetry.core.version.markers import BaseMarker
    from typing_extensions import Self

    from poetry.puzzle.transaction import Transaction
    from poetry.repositories import RepositoryPool
    from poetry.utils.env import Env

    MarkerOriginDict = defaultdict[Package, defaultdict[Package, BaseMarker]]


class Solver:
    def __init__(
        self,
        package: ProjectPackage,
        pool: RepositoryPool,
        installed: list[Package],
        locked: list[Package],
        io: IO,
        active_root_extras: Collection[NormalizedName] | None = None,
    ) -> None:
        self._package = package
        self._pool = pool
        self._installed_packages = installed
        self._locked_packages = locked
        self._io = io

        self._provider = Provider(
            self._package,
            self._pool,
            self._io,
            locked=locked,
            active_root_extras=active_root_extras,
        )
        self._overrides: list[dict[Package, dict[str, Dependency]]] = []

    @property
    def provider(self) -> Provider:
        return self._provider

    @contextmanager
    def use_environment(self, env: Env) -> Iterator[None]:
        with self.provider.use_environment(env):
            yield

    def solve(
        self, use_latest: Collection[NormalizedName] | None = None
    ) -> Transaction:
        from poetry.puzzle.transaction import Transaction

        with self._progress(), self._provider.use_latest_for(use_latest or []):
            start = time.time()
            packages = self._solve()
            # simplify markers by removing redundant information
            for transitive_info in packages.values():
                for group, marker in transitive_info.markers.items():
                    transitive_info.markers[group] = simplify_marker(
                        marker, self._package.python_constraint
                    )
            end = time.time()

            if len(self._overrides) > 1:
                self._provider.debug(
                    # ignore the warning as provider does not do interpolation
                    f"Complete version solving took {end - start:.3f}"
                    f" seconds with {len(self._overrides)} overrides"
                )
                self._provider.debug(
                    # ignore the warning as provider does not do interpolation
                    "Resolved with overrides:"
                    f" {', '.join(f'({b})' for b in self._overrides)}"
                )

        for p in packages:
            if p.yanked:
                message = (
                    f"The locked version {p.pretty_version} for {p.pretty_name} is a"
                    " yanked version."
                )
                if p.yanked_reason:
                    message += f" Reason for being yanked: {p.yanked_reason}"
                self._io.write_error_line(f"<warning>Warning: {message}</warning>")

        return Transaction(
            self._locked_packages,
            packages,
            installed_packages=self._installed_packages,
            root_package=self._package,
        )

    @contextmanager
    def _progress(self) -> Iterator[None]:
        if not self._io.output.is_decorated() or self._provider.is_debugging():
            self._io.write_line("Resolving dependencies...")
            yield
        else:
            indicator = Indicator(
                self._io, "{message}{context}<debug>({elapsed:2s})</debug>"
            )

            with indicator.auto(
                "<info>Resolving dependencies...</info>",
                "<info>Resolving dependencies...</info>",
            ):
                yield

    def _solve_in_compatibility_mode(
        self,
        overrides: tuple[dict[Package, dict[str, Dependency]], ...],
    ) -> dict[Package, TransitivePackageInfo]:
        override_packages: list[
            tuple[
                dict[Package, dict[str, Dependency]],
                dict[Package, TransitivePackageInfo],
            ]
        ] = []
        for override in overrides:
            self._provider.debug(
                # ignore the warning as provider does not do interpolation
                "<comment>Retrying dependency resolution "
                f"with the following overrides ({override}).</comment>"
            )
            self._provider.set_overrides(override)
            new_packages = self._solve()
            override_packages.append((override, new_packages))

        return merge_override_packages(override_packages)

    def _solve(self) -> dict[Package, TransitivePackageInfo]:
        if self._provider._overrides:
            self._overrides.append(self._provider._overrides)

        try:
            result = resolve_version(self._package, self._provider)

            packages = result.packages
        except OverrideNeededError as e:
            return self._solve_in_compatibility_mode(e.overrides)
        except SolveFailureError as e:
            raise SolverProblemError(e)

        return self._aggregate_solved_packages(packages)

    def _aggregate_solved_packages(
        self, packages: list[Package]
    ) -> dict[Package, TransitivePackageInfo]:
        combined_nodes, markers = depth_first_search(
            PackageNode(self._package, packages)
        )
        results = dict(aggregate_package_nodes(nodes) for nodes in combined_nodes)
        calculate_markers(results, markers)

        # Merging feature packages with base packages
        solved_packages = {}
        for package in packages:
            if package.features:
                for _package in packages:
                    if (
                        not _package.features
                        and _package.name == package.name
                        and _package.version == package.version
                    ):
                        for dep in package.requires:
                            # Prevent adding base package as a dependency to itself
                            if _package.name == dep.name:
                                continue

                            # Avoid duplication.
                            if any(
                                _dep == dep and _dep.marker == dep.marker
                                for _dep in _package.requires
                            ):
                                continue

                            _package.add_dependency(dep)
            else:
                solved_packages[package] = results[package]

        return solved_packages


DFSNodeID = tuple[str, frozenset[str], bool]


class DFSNode:
    def __init__(self, id: DFSNodeID, name: str, base_name: str) -> None:
        self.id = id
        self.name = name
        self.base_name = base_name

    def reachable(self) -> Sequence[Self]:
        return []

    def visit(self, parents: list[PackageNode]) -> None:
        pass

    def __str__(self) -> str:
        return str(self.id)


def depth_first_search(
    source: PackageNode,
) -> tuple[list[list[PackageNode]], MarkerOriginDict]:
    back_edges: dict[DFSNodeID, list[PackageNode]] = defaultdict(list)
    markers: MarkerOriginDict = defaultdict(lambda: defaultdict(EmptyMarker))
    visited: set[DFSNodeID] = set()
    topo_sorted_nodes: list[PackageNode] = []

    dfs_visit(source, back_edges, visited, topo_sorted_nodes, markers)

    # Combine the nodes by name
    combined_nodes: dict[str, list[PackageNode]] = defaultdict(list)
    for node in topo_sorted_nodes:
        node.visit(back_edges[node.id])
        combined_nodes[node.name].append(node)

    combined_topo_sorted_nodes: list[list[PackageNode]] = [
        combined_nodes.pop(node.name)
        for node in topo_sorted_nodes
        if node.name in combined_nodes
    ]

    return combined_topo_sorted_nodes, markers


def dfs_visit(
    node: PackageNode,
    back_edges: dict[DFSNodeID, list[PackageNode]],
    visited: set[DFSNodeID],
    sorted_nodes: list[PackageNode],
    markers: MarkerOriginDict,
) -> None:
    if node.id in visited:
        return
    visited.add(node.id)

    for out_neighbor in node.reachable():
        back_edges[out_neighbor.id].append(node)
        marker = markers[out_neighbor.package][node.package]
        markers[out_neighbor.package][node.package] = marker.union(
            out_neighbor.marker
            if node.package.is_root()
            else out_neighbor.marker.without_extras()
        )
        dfs_visit(out_neighbor, back_edges, visited, sorted_nodes, markers)
    sorted_nodes.insert(0, node)


class PackageNode(DFSNode):
    def __init__(
        self,
        package: Package,
        packages: list[Package],
        previous: PackageNode | None = None,
        dep: Dependency | None = None,
        marker: BaseMarker | None = None,
    ) -> None:
        self.package = package
        self.packages = packages

        self.dep = dep
        self.marker = marker or AnyMarker()
        self.depth = -1

        if not previous:
            self.groups: frozenset[str] = frozenset()
            self.optional = True
        elif dep:
            self.groups = dep.groups
            self.optional = dep.is_optional()
        else:
            raise ValueError("Both previous and dep must be passed")

        package_repr = repr(package)
        super().__init__(
            (package_repr, self.groups, self.optional),
            package_repr,
            package.name,
        )

    def reachable(self) -> Sequence[PackageNode]:
        children: list[PackageNode] = []

        for dependency in self.package.all_requires:
            for pkg in self.packages:
                if pkg.complete_name == dependency.complete_name and pkg.satisfies(
                    dependency
                ):
                    marker = dependency.marker
                    if self.package.is_root() and dependency.in_extras:
                        marker = marker.intersect(
                            parse_marker(
                                " or ".join(
                                    f'extra == "{extra}"'
                                    for extra in dependency.in_extras
                                )
                            )
                        )
                    children.append(
                        PackageNode(
                            pkg,
                            self.packages,
                            self,
                            self.dep or dependency,
                            marker,
                        )
                    )

        return children

    def visit(self, parents: list[PackageNode]) -> None:
        # The root package, which has no parents, is defined as having depth -1
        # So that the root package's top-level dependencies have depth 0.
        self.depth = 1 + max(
            [
                parent.depth if parent.base_name != self.base_name else parent.depth - 1
                for parent in parents
            ]
            + [-2]
        )


def aggregate_package_nodes(
    nodes: list[PackageNode],
) -> tuple[Package, TransitivePackageInfo]:
    package = nodes[0].package
    depth = max(node.depth for node in nodes)
    groups: set[str] = set()
    for node in nodes:
        groups.update(node.groups)

    optional = all(node.optional for node in nodes)
    for node in nodes:
        node.depth = depth
        node.optional = optional

    package.optional = optional

    # TransitivePackageInfo.markers is updated later,
    # because the nodes of all packages have to be aggregated first.
    return package, TransitivePackageInfo(depth, groups, {})


def calculate_markers(
    packages: dict[Package, TransitivePackageInfo], markers: MarkerOriginDict
) -> None:
    # group packages by depth
    packages_by_depth: dict[int, list[Package]] = defaultdict(list)
    max_depth = -1
    for package, info in packages.items():
        max_depth = max(max_depth, info.depth)
        packages_by_depth[info.depth].append(package)

    # calculate markers from lowest to highest depth
    # (start with depth 0 because the root package has depth -1)
    has_incomplete_markers = True
    while has_incomplete_markers:
        has_incomplete_markers = False
        for depth in range(max_depth + 1):
            for package in packages_by_depth[depth]:
                transitive_info = packages[package]
                transitive_marker: dict[str, BaseMarker] = {
                    group: EmptyMarker() for group in transitive_info.groups
                }
                for parent, m in markers[package].items():
                    parent_info = packages[parent]
                    if parent_info.groups:
                        if parent_info.groups != set(parent_info.markers):
                            # there is a cycle -> we need one more iteration
                            has_incomplete_markers = True
                            continue
                        for group in parent_info.groups:
                            transitive_marker[group] = transitive_marker[group].union(
                                parent_info.markers[group].intersect(m)
                            )
                    else:
                        for group in transitive_info.groups:
                            transitive_marker[group] = transitive_marker[group].union(m)
                transitive_info.markers = transitive_marker


def merge_override_packages(
    override_packages: list[
        tuple[
            dict[Package, dict[str, Dependency]], dict[Package, TransitivePackageInfo]
        ]
    ],
) -> dict[Package, TransitivePackageInfo]:
    result: dict[Package, TransitivePackageInfo] = {}
    all_packages: dict[
        Package, list[tuple[Package, TransitivePackageInfo, BaseMarker]]
    ] = {}
    for override, o_packages in override_packages:
        override_marker: BaseMarker = AnyMarker()
        for deps in override.values():
            for dep in deps.values():
                override_marker = override_marker.intersect(dep.marker.without_extras())
        for package, info in o_packages.items():
            for group, marker in info.markers.items():
                # `override_marker` is often a SingleMarker or a MultiMarker,
                # `marker` often is a MultiMarker that contains `override_marker`.
                # We can "remove" `override_marker` from `marker`
                # because we will do an intersection later anyway.
                # By removing it now, it is more likely that we hit
                # the performance shortcut instead of the fallback algorithm.
                info.markers[group] = remove_other_from_marker(marker, override_marker)
            all_packages.setdefault(package, []).append(
                (package, info, override_marker)
            )
    for package_duplicates in all_packages.values():
        base = package_duplicates[0]
        remaining = package_duplicates[1:]
        package = base[0]
        package_info = base[1]
        first_override_marker = base[2]
        result[package] = package_info
        package_info.depth = max(info.depth for _, info, _ in package_duplicates)
        package_info.groups = {
            g for _, info, _ in package_duplicates for g in info.groups
        }
        if all(info.markers == package_info.markers for _, info, _ in remaining):
            # performance shortcut:
            # if markers are the same for all overrides,
            # we can use less expensive marker operations
            override_marker = EmptyMarker()
            for _, _, marker in package_duplicates:
                override_marker = override_marker.union(marker)
            package_info.markers = {
                group: override_marker.intersect(marker)
                for group, marker in package_info.markers.items()
            }
        else:
            # fallback / general algorithm with performance issues
            for group, marker in package_info.markers.items():
                package_info.markers[group] = first_override_marker.intersect(marker)
            for _, info, override_marker in remaining:
                for group, marker in info.markers.items():
                    package_info.markers[group] = package_info.markers.get(
                        group, EmptyMarker()
                    ).union(override_marker.intersect(marker))
        for duplicate_package, _, _ in remaining:
            for dep in duplicate_package.requires:
                if dep not in package.requires:
                    package.add_dependency(dep)
    return result


def remove_other_from_marker(marker: BaseMarker, other: BaseMarker) -> BaseMarker:
    if isinstance(other, SingleMarker):
        other_markers: set[BaseMarker] = {other}
    elif isinstance(other, MultiMarker):
        other_markers = set(other.markers)
    else:
        return marker
    if isinstance(marker, MultiMarker) and other_markers.issubset(marker.markers):
        return MultiMarker.of(*(m for m in marker.markers if m not in other_markers))
    return marker


@functools.cache
def simplify_marker(
    marker: BaseMarker, python_constraint: VersionConstraint
) -> BaseMarker:
    """
    Remove constraints from markers that are covered by the projects Python constraint.

    Use cache because we call this function often for the same markers.
    """
    return marker.reduce_by_python_constraint(python_constraint)
