from typing import (
    Tuple,
    TypeVar,
    Union,
)

from sqlalchemy.sql._typing import (
    _ColumnExpressionArgument,
)
from sqlalchemy.sql.expression import Select as _Select
from typing_extensions import Self

_T = TypeVar("_T")


# Separate this class in SelectBase, Select, and SelectOfScalar so that they can share
# where and having without having type overlap incompatibility in session.exec().
class SelectBase(_Select[Tuple[_T]]):
    inherit_cache = True

    def where(self, *whereclause: Union[_ColumnExpressionArgument[bool], bool]) -> Self:
        """Return a new `Select` construct with the given expression added to
        its `WHERE` clause, joined to the existing clause via `AND`, if any.
        """
        return super().where(*whereclause)  # type: ignore[arg-type]

    def having(self, *having: Union[_ColumnExpressionArgument[bool], bool]) -> Self:
        """Return a new `Select` construct with the given expression added to
        its `HAVING` clause, joined to the existing clause via `AND`, if any.
        """
        return super().having(*having)  # type: ignore[arg-type]


class Select(SelectBase[_T]):
    inherit_cache = True


# This is not comparable to sqlalchemy.sql.selectable.ScalarSelect, that has a different
# purpose. This is the same as a normal SQLAlchemy Select class where there's only one
# entity, so the result will be converted to a scalar by default. This way writing
# for loops on the results will feel natural.
class SelectOfScalar(SelectBase[_T]):
    inherit_cache = True
