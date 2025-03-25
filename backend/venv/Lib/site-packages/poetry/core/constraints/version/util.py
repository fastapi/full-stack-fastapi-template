from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.core.constraints.version.version_range import VersionRange


if TYPE_CHECKING:
    from poetry.core.constraints.version.version_constraint import VersionConstraint


def constraint_regions(constraints: list[VersionConstraint]) -> list[VersionRange]:
    """
    Transform a list of VersionConstraints into a list of VersionRanges that mark out
    the distinct regions of version-space.

    eg input >=3.6 and >=2.7,<3.0.0 || >=3.4.0
    output <2.7, >=2.7,<3.0.0, >=3.0.0,<3.4.0, >=3.4.0,<3.6, >=3.6.
    """
    flattened = []
    for constraint in constraints:
        flattened += constraint.flatten()

    mins = {
        (constraint.min, not constraint.include_min)
        for constraint in flattened
        if constraint.min is not None
    }
    maxs = {
        (constraint.max, constraint.include_max)
        for constraint in flattened
        if constraint.max is not None
    }

    edges = sorted(mins | maxs)
    if not edges:
        return [VersionRange(None, None)]

    start = edges[0]
    regions = [
        VersionRange(None, start[0], include_max=start[1]),
    ]

    for low, high in zip(edges, edges[1:]):
        version_range = VersionRange(
            low[0],
            high[0],
            include_min=not low[1],
            include_max=high[1],
        )
        regions.append(version_range)

    end = edges[-1]
    regions.append(
        VersionRange(end[0], None, include_min=not end[1]),
    )

    return regions
