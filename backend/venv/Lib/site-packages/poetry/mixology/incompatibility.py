from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.mixology.incompatibility_cause import ConflictCauseError
from poetry.mixology.incompatibility_cause import DependencyCauseError
from poetry.mixology.incompatibility_cause import NoVersionsCauseError
from poetry.mixology.incompatibility_cause import PlatformCauseError
from poetry.mixology.incompatibility_cause import PythonCauseError
from poetry.mixology.incompatibility_cause import RootCauseError


if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterator

    from poetry.mixology.incompatibility_cause import IncompatibilityCauseError
    from poetry.mixology.term import Term


class Incompatibility:
    def __init__(self, terms: list[Term], cause: IncompatibilityCauseError) -> None:
        # Remove the root package from generated incompatibilities, since it will
        # always be satisfied. This makes error reporting clearer, and may also
        # make solving more efficient.
        if (
            len(terms) != 1
            and isinstance(cause, ConflictCauseError)
            and any(term.is_positive() and term.dependency.is_root for term in terms)
        ):
            terms = [
                term
                for term in terms
                if not term.is_positive() or not term.dependency.is_root
            ]

        if len(terms) != 1 and (
            # Short-circuit in the common case of a two-term incompatibility with
            # two different packages (for example, a dependency).
            len(terms) != 2
            or terms[0].dependency.complete_name == terms[-1].dependency.complete_name
        ):
            # Coalesce multiple terms about the same package if possible.
            by_name: dict[str, dict[str, Term]] = {}
            for term in terms:
                by_ref = by_name.setdefault(term.dependency.complete_name, {})
                ref = term.dependency.complete_name

                if ref in by_ref:
                    value = by_ref[ref].intersect(term)

                    # If we have two terms that refer to the same package but have a
                    # null intersection, they're mutually exclusive, making this
                    # incompatibility irrelevant, since we already know that mutually
                    # exclusive version ranges are incompatible. We should never derive
                    # an irrelevant incompatibility.
                    err_msg = f"Package '{ref}' is listed as a dependency of itself."
                    assert value is not None, err_msg
                    by_ref[ref] = value
                else:
                    by_ref[ref] = term

            new_terms = []
            for by_ref in by_name.values():
                positive_terms = [
                    term for term in by_ref.values() if term.is_positive()
                ]
                if positive_terms:
                    new_terms += positive_terms
                    continue

                new_terms += list(by_ref.values())

            terms = new_terms

        self._terms = terms
        self._cause = cause

    @property
    def terms(self) -> list[Term]:
        return self._terms

    @property
    def cause(self) -> IncompatibilityCauseError:
        return self._cause

    @property
    def external_incompatibilities(
        self,
    ) -> Iterator[Incompatibility]:
        """
        Returns all external incompatibilities in this incompatibility's
        derivation graph.
        """
        if isinstance(self._cause, ConflictCauseError):
            cause: ConflictCauseError = self._cause
            yield from cause.conflict.external_incompatibilities

            yield from cause.other.external_incompatibilities
        else:
            yield self

    def is_failure(self) -> bool:
        return len(self._terms) == 0 or (
            len(self._terms) == 1 and self._terms[0].dependency.is_root
        )

    def __str__(self) -> str:
        if isinstance(self._cause, DependencyCauseError):
            assert len(self._terms) == 2

            depender = self._terms[0]
            dependee = self._terms[1]
            assert depender.is_positive()
            assert not dependee.is_positive()

            return (
                f"{self._terse(depender, allow_every=True)} depends on"
                f" {self._terse(dependee)}"
            )
        elif isinstance(self._cause, PythonCauseError):
            assert len(self._terms) == 1
            assert self._terms[0].is_positive()

            text = f"{self._terse(self._terms[0], allow_every=True)} requires "
            text += f"Python {self._cause.python_version}"

            return text
        elif isinstance(self._cause, PlatformCauseError):
            assert len(self._terms) == 1
            assert self._terms[0].is_positive()

            text = f"{self._terse(self._terms[0], allow_every=True)} requires "
            text += f"platform {self._cause.platform}"

            return text
        elif isinstance(self._cause, NoVersionsCauseError):
            assert len(self._terms) == 1
            assert self._terms[0].is_positive()

            return (
                f"no versions of {self._terms[0].dependency.name} match"
                f" {self._terms[0].constraint}"
            )
        elif isinstance(self._cause, RootCauseError):
            assert len(self._terms) == 1
            assert not self._terms[0].is_positive()
            assert self._terms[0].dependency.is_root

            return (
                f"{self._terms[0].dependency.name} is"
                f" {self._terms[0].dependency.constraint}"
            )
        elif self.is_failure():
            return "version solving failed"

        if len(self._terms) == 1:
            term = self._terms[0]
            verb = "forbidden" if term.is_positive() else "required"
            return f"{term.dependency.name} is {verb}"

        if len(self._terms) == 2:
            term1 = self._terms[0]
            term2 = self._terms[1]

            if term1.is_positive() == term2.is_positive():
                if not term1.is_positive():
                    return f"either {self._terse(term1)} or {self._terse(term2)}"

                package1 = (
                    term1.dependency.name
                    if term1.constraint.is_any()
                    else self._terse(term1)
                )
                package2 = (
                    term2.dependency.name
                    if term2.constraint.is_any()
                    else self._terse(term2)
                )

                return f"{package1} is incompatible with {package2}"

        positive = []
        negative = []

        for term in self._terms:
            if term.is_positive():
                positive.append(self._terse(term))
            else:
                negative.append(self._terse(term))

        if positive and negative:
            if len(positive) != 1:
                return f"if {' and '.join(positive)} then {' or '.join(negative)}"

            positive_term = next(term for term in self._terms if term.is_positive())
            return (
                f"{self._terse(positive_term, allow_every=True)} requires"
                f" {' or '.join(negative)}"
            )
        elif positive:
            return f"one of {' or '.join(positive)} must be false"
        else:
            return f"one of {' or '.join(negative)} must be true"

    def and_to_string(
        self,
        other: Incompatibility,
        this_line: int | None,
        other_line: int | None,
    ) -> str:
        requires_both = self._try_requires_both(other, this_line, other_line)
        if requires_both is not None:
            return requires_both

        requires_through = self._try_requires_through(other, this_line, other_line)
        if requires_through is not None:
            return requires_through

        requires_forbidden = self._try_requires_forbidden(other, this_line, other_line)
        if requires_forbidden is not None:
            return requires_forbidden

        buffer = [str(self)]
        if this_line is not None:
            buffer.append(f" {this_line!s}")

        buffer.append(f" and {other!s}")

        if other_line is not None:
            buffer.append(f" {other_line!s}")

        return "\n".join(buffer)

    def _try_requires_both(
        self,
        other: Incompatibility,
        this_line: int | None,
        other_line: int | None,
    ) -> str | None:
        if len(self._terms) == 1 or len(other.terms) == 1:
            return None

        this_positive = self._single_term_where(lambda term: term.is_positive())
        if this_positive is None:
            return None

        other_positive = other._single_term_where(lambda term: term.is_positive())
        if other_positive is None:
            return None

        if this_positive.dependency != other_positive.dependency:
            return None

        this_negatives = " or ".join(
            [self._terse(term) for term in self._terms if not term.is_positive()]
        )

        other_negatives = " or ".join(
            [self._terse(term) for term in other.terms if not term.is_positive()]
        )

        buffer = [self._terse(this_positive, allow_every=True) + " "]
        is_dependency = isinstance(self.cause, DependencyCauseError) and isinstance(
            other.cause, DependencyCauseError
        )

        if is_dependency:
            buffer.append("depends on")
        else:
            buffer.append("requires")

        buffer.append(f" both {this_negatives}")
        if this_line is not None:
            buffer.append(f" ({this_line})")

        buffer.append(f" and {other_negatives}")

        if other_line is not None:
            buffer.append(f" ({other_line})")

        return "".join(buffer)

    def _try_requires_through(
        self,
        other: Incompatibility,
        this_line: int | None,
        other_line: int | None,
    ) -> str | None:
        if len(self._terms) == 1 or len(other.terms) == 1:
            return None

        this_negative = self._single_term_where(lambda term: not term.is_positive())
        other_negative = other._single_term_where(lambda term: not term.is_positive())

        if this_negative is None and other_negative is None:
            return None

        this_positive = self._single_term_where(lambda term: term.is_positive())
        other_positive = self._single_term_where(lambda term: term.is_positive())

        if (
            this_negative is not None
            and other_positive is not None
            and this_negative.dependency.name == other_positive.dependency.name
            and this_negative.inverse.satisfies(other_positive)
        ):
            prior = self
            prior_negative = this_negative
            prior_line = this_line
            latter = other
            latter_line = other_line
        elif (
            other_negative is not None
            and this_positive is not None
            and other_negative.dependency.name == this_positive.dependency.name
            and other_negative.inverse.satisfies(this_positive)
        ):
            prior = other
            prior_negative = other_negative
            prior_line = other_line
            latter = self
            latter_line = this_line
        else:
            return None

        prior_positives = [term for term in prior.terms if term.is_positive()]

        buffer = []
        if len(prior_positives) > 1:
            prior_string = " or ".join([self._terse(term) for term in prior_positives])
            buffer.append(f"if {prior_string} then ")
        else:
            if isinstance(prior.cause, DependencyCauseError):
                verb = "depends on"
            else:
                verb = "requires"

            buffer.append(
                f"{self._terse(prior_positives[0], allow_every=True)} {verb} "
            )

        buffer.append(self._terse(prior_negative))
        if prior_line is not None:
            buffer.append(f" ({prior_line})")

        buffer.append(" which ")

        if isinstance(latter.cause, DependencyCauseError):
            buffer.append("depends on ")
        else:
            buffer.append("requires ")

        buffer.append(
            " or ".join(
                [self._terse(term) for term in latter.terms if not term.is_positive()]
            )
        )

        if latter_line is not None:
            buffer.append(f" ({latter_line})")

        return "".join(buffer)

    def _try_requires_forbidden(
        self,
        other: Incompatibility,
        this_line: int | None,
        other_line: int | None,
    ) -> str | None:
        if len(self._terms) != 1 and len(other.terms) != 1:
            return None

        if len(self.terms) == 1:
            prior = other
            latter = self
            prior_line = other_line
            latter_line = this_line
        else:
            prior = self
            latter = other
            prior_line = this_line
            latter_line = other_line

        negative = prior._single_term_where(lambda term: not term.is_positive())
        if negative is None:
            return None

        if not negative.inverse.satisfies(latter.terms[0]):
            return None

        positives = [t for t in prior.terms if t.is_positive()]

        buffer = []
        if len(positives) > 1:
            prior_string = " or ".join([self._terse(term) for term in positives])
            buffer.append(f"if {prior_string} then ")
        else:
            buffer.append(self._terse(positives[0], allow_every=True))
            if isinstance(prior.cause, DependencyCauseError):
                buffer.append(" depends on ")
            else:
                buffer.append(" requires ")

        buffer.append(self._terse(latter.terms[0]) + " ")
        if prior_line is not None:
            buffer.append(f"({prior_line}) ")

        if isinstance(latter.cause, PythonCauseError):
            cause: PythonCauseError = latter.cause
            buffer.append(f"which requires Python {cause.python_version}")
        elif isinstance(latter.cause, NoVersionsCauseError):
            buffer.append("which doesn't match any versions")
        else:
            buffer.append("which is forbidden")

        if latter_line is not None:
            buffer.append(f" ({latter_line})")

        return "".join(buffer)

    def _terse(self, term: Term, allow_every: bool = False) -> str:
        if allow_every and term.constraint.is_any():
            return f"every version of {term.dependency.complete_name}"

        if term.dependency.is_root:
            pretty_name: str = term.dependency.pretty_name
            return pretty_name

        if term.dependency.source_type:
            return str(term.dependency)
        pretty_name = term.dependency.complete_pretty_name
        return f"{pretty_name} ({term.dependency.pretty_constraint})"

    def _single_term_where(self, callable: Callable[[Term], bool]) -> Term | None:
        found = None
        for term in self._terms:
            if not callable(term):
                continue

            if found is not None:
                return None

            found = term

        return found

    def __repr__(self) -> str:
        return f"<Incompatibility {self!s}>"
