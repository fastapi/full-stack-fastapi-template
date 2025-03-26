import inspect
from functools import wraps

import sentry_sdk
from sentry_sdk import get_current_span
from sentry_sdk._types import TYPE_CHECKING
from sentry_sdk.consts import OP
from sentry_sdk.utils import logger, qualname_from_function


if TYPE_CHECKING:
    from typing import Any


def start_child_span_decorator(func):
    # type: (Any) -> Any
    """
    Decorator to add child spans for functions.

    This is the Python 3 compatible version of the decorator.
    For Python 2 there is duplicated code here: ``sentry_sdk.tracing_utils_python2.start_child_span_decorator()``.

    See also ``sentry_sdk.tracing.trace()``.
    """

    # Asynchronous case
    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def func_with_tracing(*args, **kwargs):
            # type: (*Any, **Any) -> Any

            span = get_current_span(sentry_sdk.Hub.current)

            if span is None:
                logger.warning(
                    "Can not create a child span for %s. "
                    "Please start a Sentry transaction before calling this function.",
                    qualname_from_function(func),
                )
                return await func(*args, **kwargs)

            with span.start_child(
                op=OP.FUNCTION,
                description=qualname_from_function(func),
            ):
                return await func(*args, **kwargs)

    # Synchronous case
    else:

        @wraps(func)
        def func_with_tracing(*args, **kwargs):
            # type: (*Any, **Any) -> Any

            span = get_current_span(sentry_sdk.Hub.current)

            if span is None:
                logger.warning(
                    "Can not create a child span for %s. "
                    "Please start a Sentry transaction before calling this function.",
                    qualname_from_function(func),
                )
                return func(*args, **kwargs)

            with span.start_child(
                op=OP.FUNCTION,
                description=qualname_from_function(func),
            ):
                return func(*args, **kwargs)

    return func_with_tracing
