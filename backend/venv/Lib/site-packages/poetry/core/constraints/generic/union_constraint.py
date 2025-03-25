from __future__ import annotations

import itertools

from poetry.core.constraints.generic import AnyConstraint
from poetry.core.constraints.generic.base_constraint import BaseConstraint
from poetry.core.constraints.generic.constraint import Constraint
from poetry.core.constraints.generic.constraint import ExtraConstraint
from poetry.core.constraints.generic.empty_constraint import EmptyConstraint
from poetry.core.constraints.generic.multi_constraint import ExtraMultiConstraint
from poetry.core.constraints.generic.multi_constraint import MultiConstraint


class UnionConstraint(BaseConstraint):
    def __init__(self, *constraints: BaseConstraint) -> None:
        self._constraints = constraints

    @property
    def constraints(self) -> tuple[BaseConstraint, ...]:
        return self._constraints

    def allows(
        self,
        other: BaseConstraint,
    ) -> bool:
        return any(constraint.allows(other) for constraint in self._constraints)

    def allows_any(self, other: BaseConstraint) -> bool:
        if isinstance(other, UnionConstraint):
            return any(
                c1.allows_any(c2)
                for c1 in self._constraints
                for c2 in other.constraints
            )

        return any(c.allows_any(other) for c in self._constraints)

    def allows_all(self, other: BaseConstraint) -> bool:
        if isinstance(other, UnionConstraint):
            return all(
                any(c1.allows_all(c2) for c1 in self._constraints)
                for c2 in other.constraints
            )

        return any(c.allows_all(other) for c in self._constraints)

    def invert(self) -> MultiConstraint:
        inverted_constraints = [c.invert() for c in self._constraints]
        if any(not isinstance(c, Constraint) for c in inverted_constraints):
            raise NotImplementedError(
                "Inversion of complex union constraints not implemented"
            )
        if any(isinstance(c, ExtraConstraint) for c in inverted_constraints):
            multi_type: type[MultiConstraint] = ExtraMultiConstraint
        else:
            multi_type = MultiConstraint
        return multi_type(*inverted_constraints)  # type: ignore[arg-type]

    def intersect(self, other: BaseConstraint) -> BaseConstraint:
        if other.is_any():
            return self

        if other.is_empty():
            return other

        if isinstance(other, UnionConstraint) and set(other.constraints) == set(
            self._constraints
        ):
            return self

        if isinstance(other, ExtraConstraint) and other in self._constraints:
            return other

        if isinstance(other, Constraint):
            # (A or B) and C => (A and C) or (B and C)
            # just a special case of UnionConstraint
            other = UnionConstraint(other)

        new_constraints = []
        if isinstance(other, UnionConstraint):
            # (A or B) and (C or D) => (A and C) or (A and D) or (B and C) or (B and D)
            for our_constraint in self._constraints:
                for their_constraint in other.constraints:
                    intersection = our_constraint.intersect(their_constraint)

                    if not (intersection.is_empty() or intersection in new_constraints):
                        new_constraints.append(intersection)

        else:
            assert isinstance(other, MultiConstraint)
            # (A or B) and (C and D) => (A and C and D) or (B and C and D)

            for our_constraint in self._constraints:
                intersection = our_constraint
                for their_constraint in other.constraints:
                    intersection = intersection.intersect(their_constraint)

                if not (intersection.is_empty() or intersection in new_constraints):
                    new_constraints.append(intersection)

        if not new_constraints:
            return EmptyConstraint()

        if len(new_constraints) == 1:
            return new_constraints[0]

        return UnionConstraint(*new_constraints)

    def union(self, other: BaseConstraint) -> BaseConstraint:
        if other.is_any():
            return other

        if other.is_empty():
            return self

        if other == self:
            return self

        if isinstance(other, Constraint):
            # (A or B) or C => A or B or C
            # just a special case of UnionConstraint
            other = UnionConstraint(other)

        new_constraints: list[BaseConstraint] = []
        if isinstance(other, UnionConstraint):
            # (A or B) or (C or D) => A or B or C or D
            our_new_constraints: list[BaseConstraint] = []
            their_new_constraints: list[BaseConstraint] = []
            merged_new_constraints: list[BaseConstraint] = []
            for their_constraint in other.constraints:
                for our_constraint in self._constraints:
                    union = our_constraint.union(their_constraint)
                    if union.is_any():
                        return AnyConstraint()
                    if isinstance(union, Constraint):
                        if union == our_constraint:
                            if union not in our_new_constraints:
                                our_new_constraints.append(union)
                        elif union == their_constraint:
                            if union not in their_new_constraints:
                                their_new_constraints.append(their_constraint)
                        elif union not in merged_new_constraints:
                            merged_new_constraints.append(union)
                    else:
                        if our_constraint not in our_new_constraints:
                            our_new_constraints.append(our_constraint)
                        if their_constraint not in their_new_constraints:
                            their_new_constraints.append(their_constraint)
            new_constraints = our_new_constraints
            for constraint in itertools.chain(
                their_new_constraints, merged_new_constraints
            ):
                if constraint not in new_constraints:
                    new_constraints.append(constraint)

        else:
            assert isinstance(other, MultiConstraint)
            # (A or B) or (C and D) => nothing to do

            new_constraints = [*self._constraints, other]

        if len(new_constraints) == 1:
            return new_constraints[0]

        return UnionConstraint(*new_constraints)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnionConstraint):
            return False

        return self._constraints == other._constraints

    def __hash__(self) -> int:
        return hash(("union", *self._constraints))

    def __str__(self) -> str:
        constraints = [str(constraint) for constraint in self._constraints]
        return " || ".join(constraints)
