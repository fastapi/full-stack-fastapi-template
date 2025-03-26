from functools import wraps
from inspect import iscoroutinefunction

from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Any, cast, overload, ParamSpec, TypeVar, Union

    P = ParamSpec("P")
    R = TypeVar("R")


class MonitorMixin:
    if TYPE_CHECKING:

        @overload
        def __call__(self, fn):
            # type: (Callable[P, Awaitable[Any]]) -> Callable[P, Awaitable[Any]]
            # Unfortunately, mypy does not give us any reliable way to type check the
            # return value of an Awaitable (i.e. async function) for this overload,
            # since calling iscouroutinefunction narrows the type to Callable[P, Awaitable[Any]].
            ...

        @overload
        def __call__(self, fn):
            # type: (Callable[P, R]) -> Callable[P, R]
            ...

    def __call__(
        self,
        fn,  # type: Union[Callable[P, R], Callable[P, Awaitable[Any]]]
    ):
        # type: (...) -> Union[Callable[P, R], Callable[P, Awaitable[Any]]]
        if iscoroutinefunction(fn):
            return self._async_wrapper(fn)

        else:
            if TYPE_CHECKING:
                fn = cast("Callable[P, R]", fn)
            return self._sync_wrapper(fn)

    def _async_wrapper(self, fn):
        # type: (Callable[P, Awaitable[Any]]) -> Callable[P, Awaitable[Any]]
        @wraps(fn)
        async def inner(*args: "P.args", **kwargs: "P.kwargs"):
            # type: (...) -> R
            with self:  # type: ignore[attr-defined]
                return await fn(*args, **kwargs)

        return inner

    def _sync_wrapper(self, fn):
        # type: (Callable[P, R]) -> Callable[P, R]
        @wraps(fn)
        def inner(*args: "P.args", **kwargs: "P.kwargs"):
            # type: (...) -> R
            with self:  # type: ignore[attr-defined]
                return fn(*args, **kwargs)

        return inner
