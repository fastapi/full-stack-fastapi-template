from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.mixology.assignment import Assignment
from poetry.mixology.set_relation import SetRelation


if TYPE_CHECKING:
    from poetry.core.packages.dependency import Dependency
    from poetry.core.packages.package import Package

    from poetry.mixology.incompatibility import Incompatibility
    from poetry.mixology.term import Term


class PartialSolution:
    """
    # A list of Assignments that represent the solver's current best guess about
    # what's true for the eventual set of package versions that will comprise the
    # total solution.
    #
    # See:
    # https://github.com/dart-lang/mixology/tree/master/doc/solver.md#partial-solution.
    """

    def __init__(self) -> None:
        # The assignments that have been made so far, in the order they were
        # assigned.
        self._assignments: list[Assignment] = []

        # The decisions made for each package.
        self._decisions: dict[str, Package] = {}

        # The intersection of all positive Assignments for each package, minus any
        # negative Assignments that refer to that package.
        #
        # This is derived from self._assignments.
        self._positive: dict[str, Term] = {}

        # The union of all negative Assignments for each package.
        #
        # If a package has any positive Assignments, it doesn't appear in this
        # map.
        #
        # This is derived from self._assignments.
        self._negative: dict[str, Term] = {}

        # The number of distinct solutions that have been attempted so far.
        self._attempted_solutions = 1

        # Whether the solver is currently backtracking.
        self._backtracking = False

    @property
    def decisions(self) -> list[Package]:
        return list(self._decisions.values())

    @property
    def decision_level(self) -> int:
        return len(self._decisions)

    @property
    def attempted_solutions(self) -> int:
        return self._attempted_solutions

    @property
    def unsatisfied(self) -> list[Dependency]:
        return [
            term.dependency
            for term in self._positive.values()
            if term.dependency.complete_name not in self._decisions
        ]

    def decide(self, package: Package) -> None:
        """
        Adds an assignment of package as a decision
        and increments the decision level.
        """
        # When we make a new decision after backtracking, count an additional
        # attempted solution. If we backtrack multiple times in a row, though, we
        # only want to count one, since we haven't actually started attempting a
        # new solution.
        if self._backtracking:
            self._attempted_solutions += 1

        self._backtracking = False
        self._decisions[package.complete_name] = package

        self._assign(
            Assignment.decision(package, self.decision_level, len(self._assignments))
        )

    def derive(
        self, dependency: Dependency, is_positive: bool, cause: Incompatibility
    ) -> None:
        """
        Adds an assignment of package as a derivation.
        """
        self._assign(
            Assignment.derivation(
                dependency,
                is_positive,
                cause,
                self.decision_level,
                len(self._assignments),
            )
        )

    def _assign(self, assignment: Assignment) -> None:
        """
        Adds an Assignment to _assignments and _positive or _negative.
        """
        self._assignments.append(assignment)
        self._register(assignment)

    def backtrack(self, decision_level: int) -> None:
        """
        Resets the current decision level to decision_level, and removes all
        assignments made after that level.
        """
        self._backtracking = True

        packages = set()
        while self._assignments[-1].decision_level > decision_level:
            removed = self._assignments.pop(-1)
            packages.add(removed.dependency.complete_name)
            if removed.is_decision():
                del self._decisions[removed.dependency.complete_name]

        # Re-compute _positive and _negative for the packages that were removed.
        for package in packages:
            if package in self._positive:
                del self._positive[package]

            if package in self._negative:
                del self._negative[package]

        for assignment in self._assignments:
            if assignment.dependency.complete_name in packages:
                self._register(assignment)

    def _register(self, assignment: Assignment) -> None:
        """
        Registers an Assignment in _positive or _negative.
        """
        name = assignment.dependency.complete_name
        old_positive = self._positive.get(name)
        if old_positive is not None:
            value = old_positive.intersect(assignment)
            assert value is not None
            self._positive[name] = value

            return

        old_negative = self._negative.get(name)
        term = (
            assignment if old_negative is None else assignment.intersect(old_negative)
        )
        assert term is not None

        if term.is_positive():
            if name in self._negative:
                del self._negative[name]

            self._positive[name] = term
        else:
            self._negative[name] = term

    def satisfier(self, term: Term) -> Assignment:
        """
        Returns the first Assignment in this solution such that the sublist of
        assignments up to and including that entry collectively satisfies term.
        """
        assigned_term: Term | None = None

        for assignment in self._assignments:
            if assignment.dependency.complete_name != term.dependency.complete_name:
                continue

            if (
                not assignment.dependency.is_root
                and not assignment.dependency.is_same_package_as(term.dependency)
            ):
                if not assignment.is_positive():
                    continue

                assert not term.is_positive()

                return assignment

            if assigned_term is None:
                assigned_term = assignment
            else:
                assigned_term = assigned_term.intersect(assignment)

            # As soon as we have enough assignments to satisfy term, return them.
            assert assigned_term is not None
            if assigned_term.satisfies(term):
                return assignment

        raise RuntimeError(f"[BUG] {term} is not satisfied.")

    def satisfies(self, term: Term) -> bool:
        return self.relation(term) == SetRelation.SUBSET

    def relation(self, term: Term) -> str:
        positive = self._positive.get(term.dependency.complete_name)
        if positive is not None:
            return positive.relation(term)

        negative = self._negative.get(term.dependency.complete_name)
        if negative is None:
            return SetRelation.OVERLAPPING

        return negative.relation(term)
