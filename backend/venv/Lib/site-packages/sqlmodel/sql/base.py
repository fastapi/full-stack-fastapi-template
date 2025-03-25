from typing import Generic, TypeVar

from sqlalchemy.sql.base import Executable as _Executable

_T = TypeVar("_T")


class Executable(_Executable, Generic[_T]):
    pass
