from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.core.constraints.version.version_constraint import VersionConstraint


if TYPE_CHECKING:
    from poetry.core.constraints.version.version import Version
    from poetry.core.constraints.version.version_range_constraint import (
        VersionRangeConstraint,
    )


class EmptyConstraint(VersionConstraint):
    def is_empty(self) -> bool:
        return True

    def is_any(self) -> bool:
        return False

    def is_simple(self) -> bool:
        return True

    def has_upper_bound(self) -> bool:
        # Rationale:
        # 1. If no version can satisfy the constraint,
        #    this is like an upper bound of 0 (not included).
        # 2. The opposite of an empty constraint, which is *, has no upper bound
        #    and the two extremes often behave the other way around.
        return True

    def allows(self, version: Version) -> bool:
        return False

    def allows_all(self, other: VersionConstraint) -> bool:
        return other.is_empty()

    def allows_any(self, other: VersionConstraint) -> bool:
        return False

    def intersect(self, other: VersionConstraint) -> EmptyConstraint:
        return self

    def union(self, other: VersionConstraint) -> VersionConstraint:
        return other

    def difference(self, other: VersionConstraint) -> EmptyConstraint:
        return self

    def flatten(self) -> list[VersionRangeConstraint]:
        return []

    def __str__(self) -> str:
        return "<empty>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VersionConstraint):
            return False

        return other.is_empty()

    def __hash__(self) -> int:
        return hash("empty")
