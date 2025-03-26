# mypy: allow-untyped-defs, allow-incomplete-defs, allow-untyped-calls
# mypy: no-warn-return-any, allow-any-generics

from __future__ import annotations

import contextlib
import re
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import Optional
from typing import Protocol
from typing import Set
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

from sqlalchemy import __version__
from sqlalchemy import schema
from sqlalchemy import sql
from sqlalchemy import types as sqltypes
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.sql import visitors
from sqlalchemy.sql.base import DialectKWArgs
from sqlalchemy.sql.elements import BindParameter
from sqlalchemy.sql.elements import ColumnClause
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.sql.visitors import traverse
from typing_extensions import TypeGuard

if True:
    from sqlalchemy.sql.naming import _NONE_NAME as _NONE_NAME  # type: ignore[attr-defined] # noqa: E501

if TYPE_CHECKING:
    from sqlalchemy import ClauseElement
    from sqlalchemy import Identity
    from sqlalchemy import Index
    from sqlalchemy import Table
    from sqlalchemy.engine import Connection
    from sqlalchemy.engine import Dialect
    from sqlalchemy.engine import Transaction
    from sqlalchemy.sql.base import ColumnCollection
    from sqlalchemy.sql.compiler import SQLCompiler
    from sqlalchemy.sql.elements import ColumnElement
    from sqlalchemy.sql.schema import Constraint
    from sqlalchemy.sql.schema import SchemaItem

_CE = TypeVar("_CE", bound=Union["ColumnElement[Any]", "SchemaItem"])


class _CompilerProtocol(Protocol):
    def __call__(self, element: Any, compiler: Any, **kw: Any) -> str: ...


def _safe_int(value: str) -> Union[int, str]:
    try:
        return int(value)
    except:
        return value


_vers = tuple(
    [_safe_int(x) for x in re.findall(r"(\d+|[abc]\d)", __version__)]
)
# https://docs.sqlalchemy.org/en/latest/changelog/changelog_14.html#change-0c6e0cc67dfe6fac5164720e57ef307d
sqla_14_18 = _vers >= (1, 4, 18)
sqla_14_26 = _vers >= (1, 4, 26)
sqla_2 = _vers >= (2,)
sqlalchemy_version = __version__

if TYPE_CHECKING:

    def compiles(
        element: Type[ClauseElement], *dialects: str
    ) -> Callable[[_CompilerProtocol], _CompilerProtocol]: ...

else:
    from sqlalchemy.ext.compiler import compiles


identity_has_dialect_kwargs = issubclass(schema.Identity, DialectKWArgs)


def _get_identity_options_dict(
    identity: Union[Identity, schema.Sequence, None],
    dialect_kwargs: bool = False,
) -> Dict[str, Any]:
    if identity is None:
        return {}
    elif identity_has_dialect_kwargs:
        assert hasattr(identity, "_as_dict")
        as_dict = identity._as_dict()
        if dialect_kwargs:
            assert isinstance(identity, DialectKWArgs)
            as_dict.update(identity.dialect_kwargs)
    else:
        as_dict = {}
        if isinstance(identity, schema.Identity):
            # always=None means something different than always=False
            as_dict["always"] = identity.always
            if identity.on_null is not None:
                as_dict["on_null"] = identity.on_null
        # attributes common to Identity and Sequence
        attrs = (
            "start",
            "increment",
            "minvalue",
            "maxvalue",
            "nominvalue",
            "nomaxvalue",
            "cycle",
            "cache",
            "order",
        )
        as_dict.update(
            {
                key: getattr(identity, key, None)
                for key in attrs
                if getattr(identity, key, None) is not None
            }
        )
    return as_dict


if sqla_2:
    from sqlalchemy.sql.base import _NoneName
else:
    from sqlalchemy.util import symbol as _NoneName  # type: ignore[assignment]


_ConstraintName = Union[None, str, _NoneName]
_ConstraintNameDefined = Union[str, _NoneName]


def constraint_name_defined(
    name: _ConstraintName,
) -> TypeGuard[_ConstraintNameDefined]:
    return name is _NONE_NAME or isinstance(name, (str, _NoneName))


def constraint_name_string(name: _ConstraintName) -> TypeGuard[str]:
    return isinstance(name, str)


def constraint_name_or_none(name: _ConstraintName) -> Optional[str]:
    return name if constraint_name_string(name) else None


AUTOINCREMENT_DEFAULT = "auto"


@contextlib.contextmanager
def _ensure_scope_for_ddl(
    connection: Optional[Connection],
) -> Iterator[None]:
    try:
        in_transaction = connection.in_transaction  # type: ignore[union-attr]
    except AttributeError:
        # catch for MockConnection, None
        in_transaction = None
        pass

    # yield outside the catch
    if in_transaction is None:
        yield
    else:
        if not in_transaction():
            assert connection is not None
            with connection.begin():
                yield
        else:
            yield


def _safe_begin_connection_transaction(
    connection: Connection,
) -> Transaction:
    transaction = connection.get_transaction()
    if transaction:
        return transaction
    else:
        return connection.begin()


def _safe_commit_connection_transaction(
    connection: Connection,
) -> None:
    transaction = connection.get_transaction()
    if transaction:
        transaction.commit()


def _safe_rollback_connection_transaction(
    connection: Connection,
) -> None:
    transaction = connection.get_transaction()
    if transaction:
        transaction.rollback()


def _get_connection_in_transaction(connection: Optional[Connection]) -> bool:
    try:
        in_transaction = connection.in_transaction  # type: ignore
    except AttributeError:
        # catch for MockConnection
        return False
    else:
        return in_transaction()


def _idx_table_bound_expressions(idx: Index) -> Iterable[ColumnElement[Any]]:
    return idx.expressions  # type: ignore


def _copy(schema_item: _CE, **kw) -> _CE:
    if hasattr(schema_item, "_copy"):
        return schema_item._copy(**kw)
    else:
        return schema_item.copy(**kw)  # type: ignore[union-attr]


def _connectable_has_table(
    connectable: Connection, tablename: str, schemaname: Union[str, None]
) -> bool:
    return connectable.dialect.has_table(connectable, tablename, schemaname)


def _exec_on_inspector(inspector, statement, **params):
    with inspector._operation_context() as conn:
        return conn.execute(statement, params)


def _nullability_might_be_unset(metadata_column):
    from sqlalchemy.sql import schema

    return metadata_column._user_defined_nullable is schema.NULL_UNSPECIFIED


def _server_default_is_computed(*server_default) -> bool:
    return any(isinstance(sd, schema.Computed) for sd in server_default)


def _server_default_is_identity(*server_default) -> bool:
    return any(isinstance(sd, schema.Identity) for sd in server_default)


def _table_for_constraint(constraint: Constraint) -> Table:
    if isinstance(constraint, ForeignKeyConstraint):
        table = constraint.parent
        assert table is not None
        return table  # type: ignore[return-value]
    else:
        return constraint.table


def _columns_for_constraint(constraint):
    if isinstance(constraint, ForeignKeyConstraint):
        return [fk.parent for fk in constraint.elements]
    elif isinstance(constraint, CheckConstraint):
        return _find_columns(constraint.sqltext)
    else:
        return list(constraint.columns)


def _resolve_for_variant(type_, dialect):
    if _type_has_variants(type_):
        base_type, mapping = _get_variant_mapping(type_)
        return mapping.get(dialect.name, base_type)
    else:
        return type_


if hasattr(sqltypes.TypeEngine, "_variant_mapping"):  # 2.0

    def _type_has_variants(type_):
        return bool(type_._variant_mapping)

    def _get_variant_mapping(type_):
        return type_, type_._variant_mapping

else:

    def _type_has_variants(type_):
        return type(type_) is sqltypes.Variant

    def _get_variant_mapping(type_):
        return type_.impl, type_.mapping


def _fk_spec(constraint: ForeignKeyConstraint) -> Any:
    if TYPE_CHECKING:
        assert constraint.columns is not None
        assert constraint.elements is not None
        assert isinstance(constraint.parent, Table)

    source_columns = [
        constraint.columns[key].name for key in constraint.column_keys
    ]

    source_table = constraint.parent.name
    source_schema = constraint.parent.schema
    target_schema = constraint.elements[0].column.table.schema
    target_table = constraint.elements[0].column.table.name
    target_columns = [element.column.name for element in constraint.elements]
    ondelete = constraint.ondelete
    onupdate = constraint.onupdate
    deferrable = constraint.deferrable
    initially = constraint.initially
    return (
        source_schema,
        source_table,
        source_columns,
        target_schema,
        target_table,
        target_columns,
        onupdate,
        ondelete,
        deferrable,
        initially,
    )


def _fk_is_self_referential(constraint: ForeignKeyConstraint) -> bool:
    spec = constraint.elements[0]._get_colspec()
    tokens = spec.split(".")
    tokens.pop(-1)  # colname
    tablekey = ".".join(tokens)
    assert constraint.parent is not None
    return tablekey == constraint.parent.key


def _is_type_bound(constraint: Constraint) -> bool:
    # this deals with SQLAlchemy #3260, don't copy CHECK constraints
    # that will be generated by the type.
    # new feature added for #3260
    return constraint._type_bound


def _find_columns(clause):
    """locate Column objects within the given expression."""

    cols: Set[ColumnElement[Any]] = set()
    traverse(clause, {}, {"column": cols.add})
    return cols


def _remove_column_from_collection(
    collection: ColumnCollection, column: Union[Column[Any], ColumnClause[Any]]
) -> None:
    """remove a column from a ColumnCollection."""

    # workaround for older SQLAlchemy, remove the
    # same object that's present
    assert column.key is not None
    to_remove = collection[column.key]

    # SQLAlchemy 2.0 will use more ReadOnlyColumnCollection
    # (renamed from ImmutableColumnCollection)
    if hasattr(collection, "_immutable") or hasattr(collection, "_readonly"):
        collection._parent.remove(to_remove)
    else:
        collection.remove(to_remove)


def _textual_index_column(
    table: Table, text_: Union[str, TextClause, ColumnElement[Any]]
) -> Union[ColumnElement[Any], Column[Any]]:
    """a workaround for the Index construct's severe lack of flexibility"""
    if isinstance(text_, str):
        c = Column(text_, sqltypes.NULLTYPE)
        table.append_column(c)
        return c
    elif isinstance(text_, TextClause):
        return _textual_index_element(table, text_)
    elif isinstance(text_, _textual_index_element):
        return _textual_index_column(table, text_.text)
    elif isinstance(text_, sql.ColumnElement):
        return _copy_expression(text_, table)
    else:
        raise ValueError("String or text() construct expected")


def _copy_expression(expression: _CE, target_table: Table) -> _CE:
    def replace(col):
        if (
            isinstance(col, Column)
            and col.table is not None
            and col.table is not target_table
        ):
            if col.name in target_table.c:
                return target_table.c[col.name]
            else:
                c = _copy(col)
                target_table.append_column(c)
                return c
        else:
            return None

    return visitors.replacement_traverse(  # type: ignore[call-overload]
        expression, {}, replace
    )


class _textual_index_element(sql.ColumnElement):
    """Wrap around a sqlalchemy text() construct in such a way that
    we appear like a column-oriented SQL expression to an Index
    construct.

    The issue here is that currently the Postgresql dialect, the biggest
    recipient of functional indexes, keys all the index expressions to
    the corresponding column expressions when rendering CREATE INDEX,
    so the Index we create here needs to have a .columns collection that
    is the same length as the .expressions collection.  Ultimately
    SQLAlchemy should support text() expressions in indexes.

    See SQLAlchemy issue 3174.

    """

    __visit_name__ = "_textual_idx_element"

    def __init__(self, table: Table, text: TextClause) -> None:
        self.table = table
        self.text = text
        self.key = text.text
        self.fake_column = schema.Column(self.text.text, sqltypes.NULLTYPE)
        table.append_column(self.fake_column)

    def get_children(self, **kw):
        return [self.fake_column]


@compiles(_textual_index_element)
def _render_textual_index_column(
    element: _textual_index_element, compiler: SQLCompiler, **kw
) -> str:
    return compiler.process(element.text, **kw)


class _literal_bindparam(BindParameter):
    pass


@compiles(_literal_bindparam)
def _render_literal_bindparam(
    element: _literal_bindparam, compiler: SQLCompiler, **kw
) -> str:
    return compiler.render_literal_bindparam(element, **kw)


def _get_constraint_final_name(
    constraint: Union[Index, Constraint], dialect: Optional[Dialect]
) -> Optional[str]:
    if constraint.name is None:
        return None
    assert dialect is not None
    # for SQLAlchemy 1.4 we would like to have the option to expand
    # the use of "deferred" names for constraints as well as to have
    # some flexibility with "None" name and similar; make use of new
    # SQLAlchemy API to return what would be the final compiled form of
    # the name for this dialect.
    return dialect.identifier_preparer.format_constraint(
        constraint, _alembic_quote=False
    )


def _constraint_is_named(
    constraint: Union[Constraint, Index], dialect: Optional[Dialect]
) -> bool:
    if constraint.name is None:
        return False
    assert dialect is not None
    name = dialect.identifier_preparer.format_constraint(
        constraint, _alembic_quote=False
    )
    return name is not None


def is_expression_index(index: Index) -> bool:
    for expr in index.expressions:
        if is_expression(expr):
            return True
    return False


def is_expression(expr: Any) -> bool:
    while isinstance(expr, UnaryExpression):
        expr = expr.element
    if not isinstance(expr, ColumnClause) or expr.is_literal:
        return True
    return False
