from typing import (
    Any,
    Dict,
    Mapping,
    Optional,
    Sequence,
    TypeVar,
    Union,
    overload,
)

from sqlalchemy import util
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.engine.interfaces import _CoreAnyExecuteParams
from sqlalchemy.engine.result import Result, ScalarResult, TupleResult
from sqlalchemy.orm import Query as _Query
from sqlalchemy.orm import Session as _Session
from sqlalchemy.orm._typing import OrmExecuteOptionsParameter
from sqlalchemy.sql._typing import _ColumnsClauseArgument
from sqlalchemy.sql.base import Executable as _Executable
from sqlalchemy.sql.dml import UpdateBase
from sqlmodel.sql.base import Executable
from sqlmodel.sql.expression import Select, SelectOfScalar
from typing_extensions import deprecated

_TSelectParam = TypeVar("_TSelectParam", bound=Any)


class Session(_Session):
    @overload
    def exec(
        self,
        statement: Select[_TSelectParam],
        *,
        params: Optional[Union[Mapping[str, Any], Sequence[Mapping[str, Any]]]] = None,
        execution_options: Mapping[str, Any] = util.EMPTY_DICT,
        bind_arguments: Optional[Dict[str, Any]] = None,
        _parent_execute_state: Optional[Any] = None,
        _add_event: Optional[Any] = None,
    ) -> TupleResult[_TSelectParam]: ...

    @overload
    def exec(
        self,
        statement: SelectOfScalar[_TSelectParam],
        *,
        params: Optional[Union[Mapping[str, Any], Sequence[Mapping[str, Any]]]] = None,
        execution_options: Mapping[str, Any] = util.EMPTY_DICT,
        bind_arguments: Optional[Dict[str, Any]] = None,
        _parent_execute_state: Optional[Any] = None,
        _add_event: Optional[Any] = None,
    ) -> ScalarResult[_TSelectParam]: ...

    @overload
    def exec(
        self,
        statement: UpdateBase,
        *,
        params: Optional[Union[Mapping[str, Any], Sequence[Mapping[str, Any]]]] = None,
        execution_options: Mapping[str, Any] = util.EMPTY_DICT,
        bind_arguments: Optional[Dict[str, Any]] = None,
        _parent_execute_state: Optional[Any] = None,
        _add_event: Optional[Any] = None,
    ) -> CursorResult[Any]: ...

    def exec(
        self,
        statement: Union[
            Select[_TSelectParam],
            SelectOfScalar[_TSelectParam],
            Executable[_TSelectParam],
            UpdateBase,
        ],
        *,
        params: Optional[Union[Mapping[str, Any], Sequence[Mapping[str, Any]]]] = None,
        execution_options: Mapping[str, Any] = util.EMPTY_DICT,
        bind_arguments: Optional[Dict[str, Any]] = None,
        _parent_execute_state: Optional[Any] = None,
        _add_event: Optional[Any] = None,
    ) -> Union[
        TupleResult[_TSelectParam], ScalarResult[_TSelectParam], CursorResult[Any]
    ]:
        results = super().execute(
            statement,
            params=params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            _parent_execute_state=_parent_execute_state,
            _add_event=_add_event,
        )
        if isinstance(statement, SelectOfScalar):
            return results.scalars()
        return results  # type: ignore

    @deprecated(
        """
        🚨 You probably want to use `session.exec()` instead of `session.execute()`.

        This is the original SQLAlchemy `session.execute()` method that returns objects
        of type `Row`, and that you have to call `scalars()` to get the model objects.

        For example:

        ```Python
        heroes = session.execute(select(Hero)).scalars().all()
        ```

        instead you could use `exec()`:

        ```Python
        heroes = session.exec(select(Hero)).all()
        ```
        """,
        category=None,
    )
    def execute(  # type: ignore
        self,
        statement: _Executable,
        params: Optional[_CoreAnyExecuteParams] = None,
        *,
        execution_options: OrmExecuteOptionsParameter = util.EMPTY_DICT,
        bind_arguments: Optional[Dict[str, Any]] = None,
        _parent_execute_state: Optional[Any] = None,
        _add_event: Optional[Any] = None,
    ) -> Result[Any]:
        """
        🚨 You probably want to use `session.exec()` instead of `session.execute()`.

        This is the original SQLAlchemy `session.execute()` method that returns objects
        of type `Row`, and that you have to call `scalars()` to get the model objects.

        For example:

        ```Python
        heroes = session.execute(select(Hero)).scalars().all()
        ```

        instead you could use `exec()`:

        ```Python
        heroes = session.exec(select(Hero)).all()
        ```
        """
        return super().execute(
            statement,
            params=params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            _parent_execute_state=_parent_execute_state,
            _add_event=_add_event,
        )

    @deprecated(
        """
        🚨 You probably want to use `session.exec()` instead of `session.query()`.

        `session.exec()` is SQLModel's own short version with increased type
        annotations.

        Or otherwise you might want to use `session.execute()` instead of
        `session.query()`.
        """
    )
    def query(  # type: ignore
        self, *entities: _ColumnsClauseArgument[Any], **kwargs: Any
    ) -> _Query[Any]:
        """
        🚨 You probably want to use `session.exec()` instead of `session.query()`.

        `session.exec()` is SQLModel's own short version with increased type
        annotations.

        Or otherwise you might want to use `session.execute()` instead of
        `session.query()`.
        """
        return super().query(*entities, **kwargs)
