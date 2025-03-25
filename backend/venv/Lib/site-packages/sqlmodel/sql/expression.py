from typing import (
    Any,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import sqlalchemy
from sqlalchemy import (
    Column,
    ColumnElement,
    Extract,
    FunctionElement,
    FunctionFilter,
    Label,
    Over,
    TypeCoerce,
    WithinGroup,
)
from sqlalchemy.orm import InstrumentedAttribute, Mapped
from sqlalchemy.sql._typing import (
    _ColumnExpressionArgument,
    _ColumnExpressionOrLiteralArgument,
    _ColumnExpressionOrStrLabelArgument,
)
from sqlalchemy.sql.elements import (
    BinaryExpression,
    Case,
    Cast,
    CollectionAggregate,
    ColumnClause,
    TryCast,
    UnaryExpression,
)
from sqlalchemy.sql.type_api import TypeEngine
from typing_extensions import Literal

from ._expression_select_cls import Select as Select
from ._expression_select_cls import SelectOfScalar as SelectOfScalar
from ._expression_select_gen import select as select

_T = TypeVar("_T")

_TypeEngineArgument = Union[Type[TypeEngine[_T]], TypeEngine[_T]]

# Redefine operatos that would only take a column expresion to also take the (virtual)
# types of Pydantic models, e.g. str instead of only Mapped[str].


def all_(expr: Union[_ColumnExpressionArgument[_T], _T]) -> CollectionAggregate[bool]:
    return sqlalchemy.all_(expr)  # type: ignore[arg-type]


def and_(
    initial_clause: Union[Literal[True], _ColumnExpressionArgument[bool], bool],
    *clauses: Union[_ColumnExpressionArgument[bool], bool],
) -> ColumnElement[bool]:
    return sqlalchemy.and_(initial_clause, *clauses)  # type: ignore[arg-type]


def any_(expr: Union[_ColumnExpressionArgument[_T], _T]) -> CollectionAggregate[bool]:
    return sqlalchemy.any_(expr)  # type: ignore[arg-type]


def asc(
    column: Union[_ColumnExpressionOrStrLabelArgument[_T], _T],
) -> UnaryExpression[_T]:
    return sqlalchemy.asc(column)  # type: ignore[arg-type]


def collate(
    expression: Union[_ColumnExpressionArgument[str], str], collation: str
) -> BinaryExpression[str]:
    return sqlalchemy.collate(expression, collation)  # type: ignore[arg-type]


def between(
    expr: Union[_ColumnExpressionOrLiteralArgument[_T], _T],
    lower_bound: Any,
    upper_bound: Any,
    symmetric: bool = False,
) -> BinaryExpression[bool]:
    return sqlalchemy.between(expr, lower_bound, upper_bound, symmetric=symmetric)


def not_(clause: Union[_ColumnExpressionArgument[_T], _T]) -> ColumnElement[_T]:
    return sqlalchemy.not_(clause)  # type: ignore[arg-type]


def case(
    *whens: Union[
        Tuple[Union[_ColumnExpressionArgument[bool], bool], Any], Mapping[Any, Any]
    ],
    value: Optional[Any] = None,
    else_: Optional[Any] = None,
) -> Case[Any]:
    return sqlalchemy.case(*whens, value=value, else_=else_)  # type: ignore[arg-type]


def cast(
    expression: Union[_ColumnExpressionOrLiteralArgument[Any], Any],
    type_: "_TypeEngineArgument[_T]",
) -> Cast[_T]:
    return sqlalchemy.cast(expression, type_)


def try_cast(
    expression: Union[_ColumnExpressionOrLiteralArgument[Any], Any],
    type_: "_TypeEngineArgument[_T]",
) -> TryCast[_T]:
    return sqlalchemy.try_cast(expression, type_)


def desc(
    column: Union[_ColumnExpressionOrStrLabelArgument[_T], _T],
) -> UnaryExpression[_T]:
    return sqlalchemy.desc(column)  # type: ignore[arg-type]


def distinct(expr: Union[_ColumnExpressionArgument[_T], _T]) -> UnaryExpression[_T]:
    return sqlalchemy.distinct(expr)  # type: ignore[arg-type]


def bitwise_not(expr: Union[_ColumnExpressionArgument[_T], _T]) -> UnaryExpression[_T]:
    return sqlalchemy.bitwise_not(expr)  # type: ignore[arg-type]


def extract(field: str, expr: Union[_ColumnExpressionArgument[Any], Any]) -> Extract:
    return sqlalchemy.extract(field, expr)


def funcfilter(
    func: FunctionElement[_T], *criterion: Union[_ColumnExpressionArgument[bool], bool]
) -> FunctionFilter[_T]:
    return sqlalchemy.funcfilter(func, *criterion)  # type: ignore[arg-type]


def label(
    name: str,
    element: Union[_ColumnExpressionArgument[_T], _T],
    type_: Optional["_TypeEngineArgument[_T]"] = None,
) -> Label[_T]:
    return sqlalchemy.label(name, element, type_=type_)  # type: ignore[arg-type]


def nulls_first(
    column: Union[_ColumnExpressionArgument[_T], _T],
) -> UnaryExpression[_T]:
    return sqlalchemy.nulls_first(column)  # type: ignore[arg-type]


def nulls_last(column: Union[_ColumnExpressionArgument[_T], _T]) -> UnaryExpression[_T]:
    return sqlalchemy.nulls_last(column)  # type: ignore[arg-type]


def or_(
    initial_clause: Union[Literal[False], _ColumnExpressionArgument[bool], bool],
    *clauses: Union[_ColumnExpressionArgument[bool], bool],
) -> ColumnElement[bool]:
    return sqlalchemy.or_(initial_clause, *clauses)  # type: ignore[arg-type]


def over(
    element: FunctionElement[_T],
    partition_by: Optional[
        Union[
            Iterable[Union[_ColumnExpressionArgument[Any], Any]],
            _ColumnExpressionArgument[Any],
            Any,
        ]
    ] = None,
    order_by: Optional[
        Union[
            Iterable[Union[_ColumnExpressionArgument[Any], Any]],
            _ColumnExpressionArgument[Any],
            Any,
        ]
    ] = None,
    range_: Optional[Tuple[Optional[int], Optional[int]]] = None,
    rows: Optional[Tuple[Optional[int], Optional[int]]] = None,
) -> Over[_T]:
    return sqlalchemy.over(
        element, partition_by=partition_by, order_by=order_by, range_=range_, rows=rows
    )


def tuple_(
    *clauses: Union[_ColumnExpressionArgument[Any], Any],
    types: Optional[Sequence["_TypeEngineArgument[Any]"]] = None,
) -> Tuple[Any, ...]:
    return sqlalchemy.tuple_(*clauses, types=types)  # type: ignore[return-value]


def type_coerce(
    expression: Union[_ColumnExpressionOrLiteralArgument[Any], Any],
    type_: "_TypeEngineArgument[_T]",
) -> TypeCoerce[_T]:
    return sqlalchemy.type_coerce(expression, type_)


def within_group(
    element: FunctionElement[_T], *order_by: Union[_ColumnExpressionArgument[Any], Any]
) -> WithinGroup[_T]:
    return sqlalchemy.within_group(element, *order_by)


def col(column_expression: _T) -> Mapped[_T]:
    if not isinstance(column_expression, (ColumnClause, Column, InstrumentedAttribute)):
        raise RuntimeError(f"Not a SQLAlchemy column: {column_expression}")
    return column_expression  # type: ignore
