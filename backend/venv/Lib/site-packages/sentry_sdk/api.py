import inspect

from sentry_sdk._types import TYPE_CHECKING
from sentry_sdk.hub import Hub
from sentry_sdk.scope import Scope
from sentry_sdk.tracing import NoOpSpan, Transaction

if TYPE_CHECKING:
    from typing import Any
    from typing import Dict
    from typing import Optional
    from typing import overload
    from typing import Callable
    from typing import TypeVar
    from typing import ContextManager
    from typing import Union

    from sentry_sdk._types import (
        Event,
        Hint,
        Breadcrumb,
        BreadcrumbHint,
        ExcInfo,
        MeasurementUnit,
        LogLevelStr,
    )
    from sentry_sdk.tracing import Span

    T = TypeVar("T")
    F = TypeVar("F", bound=Callable[..., Any])
else:

    def overload(x):
        # type: (T) -> T
        return x


# When changing this, update __all__ in __init__.py too
__all__ = [
    "capture_event",
    "capture_message",
    "capture_exception",
    "add_breadcrumb",
    "configure_scope",
    "push_scope",
    "flush",
    "last_event_id",
    "start_span",
    "start_transaction",
    "set_tag",
    "set_context",
    "set_extra",
    "set_user",
    "set_level",
    "set_measurement",
    "get_current_span",
    "get_traceparent",
    "get_baggage",
    "continue_trace",
]


def hubmethod(f):
    # type: (F) -> F
    f.__doc__ = "%s\n\n%s" % (
        "Alias for :py:meth:`sentry_sdk.Hub.%s`" % f.__name__,
        inspect.getdoc(getattr(Hub, f.__name__)),
    )
    return f


def scopemethod(f):
    # type: (F) -> F
    f.__doc__ = "%s\n\n%s" % (
        "Alias for :py:meth:`sentry_sdk.Scope.%s`" % f.__name__,
        inspect.getdoc(getattr(Scope, f.__name__)),
    )
    return f


@hubmethod
def capture_event(
    event,  # type: Event
    hint=None,  # type: Optional[Hint]
    scope=None,  # type: Optional[Any]
    **scope_kwargs  # type: Any
):
    # type: (...) -> Optional[str]
    return Hub.current.capture_event(event, hint, scope=scope, **scope_kwargs)


@hubmethod
def capture_message(
    message,  # type: str
    level=None,  # type: Optional[LogLevelStr]
    scope=None,  # type: Optional[Any]
    **scope_kwargs  # type: Any
):
    # type: (...) -> Optional[str]
    return Hub.current.capture_message(message, level, scope=scope, **scope_kwargs)


@hubmethod
def capture_exception(
    error=None,  # type: Optional[Union[BaseException, ExcInfo]]
    scope=None,  # type: Optional[Any]
    **scope_kwargs  # type: Any
):
    # type: (...) -> Optional[str]
    return Hub.current.capture_exception(error, scope=scope, **scope_kwargs)


@hubmethod
def add_breadcrumb(
    crumb=None,  # type: Optional[Breadcrumb]
    hint=None,  # type: Optional[BreadcrumbHint]
    **kwargs  # type: Any
):
    # type: (...) -> None
    return Hub.current.add_breadcrumb(crumb, hint, **kwargs)


@overload
def configure_scope():
    # type: () -> ContextManager[Scope]
    pass


@overload
def configure_scope(  # noqa: F811
    callback,  # type: Callable[[Scope], None]
):
    # type: (...) -> None
    pass


@hubmethod
def configure_scope(  # noqa: F811
    callback=None,  # type: Optional[Callable[[Scope], None]]
):
    # type: (...) -> Optional[ContextManager[Scope]]
    return Hub.current.configure_scope(callback)


@overload
def push_scope():
    # type: () -> ContextManager[Scope]
    pass


@overload
def push_scope(  # noqa: F811
    callback,  # type: Callable[[Scope], None]
):
    # type: (...) -> None
    pass


@hubmethod
def push_scope(  # noqa: F811
    callback=None,  # type: Optional[Callable[[Scope], None]]
):
    # type: (...) -> Optional[ContextManager[Scope]]
    return Hub.current.push_scope(callback)


@scopemethod
def set_tag(key, value):
    # type: (str, Any) -> None
    return Hub.current.scope.set_tag(key, value)


@scopemethod
def set_context(key, value):
    # type: (str, Dict[str, Any]) -> None
    return Hub.current.scope.set_context(key, value)


@scopemethod
def set_extra(key, value):
    # type: (str, Any) -> None
    return Hub.current.scope.set_extra(key, value)


@scopemethod
def set_user(value):
    # type: (Optional[Dict[str, Any]]) -> None
    return Hub.current.scope.set_user(value)


@scopemethod
def set_level(value):
    # type: (LogLevelStr) -> None
    return Hub.current.scope.set_level(value)


@hubmethod
def flush(
    timeout=None,  # type: Optional[float]
    callback=None,  # type: Optional[Callable[[int, float], None]]
):
    # type: (...) -> None
    return Hub.current.flush(timeout=timeout, callback=callback)


@hubmethod
def last_event_id():
    # type: () -> Optional[str]

    return Hub.current.last_event_id()


@hubmethod
def start_span(
    span=None,  # type: Optional[Span]
    **kwargs  # type: Any
):
    # type: (...) -> Span
    return Hub.current.start_span(span=span, **kwargs)


@hubmethod
def start_transaction(
    transaction=None,  # type: Optional[Transaction]
    **kwargs  # type: Any
):
    # type: (...) -> Union[Transaction, NoOpSpan]
    return Hub.current.start_transaction(transaction, **kwargs)


def set_measurement(name, value, unit=""):
    # type: (str, float, MeasurementUnit) -> None
    transaction = Hub.current.scope.transaction
    if transaction is not None:
        transaction.set_measurement(name, value, unit)


def get_current_span(hub=None):
    # type: (Optional[Hub]) -> Optional[Span]
    """
    Returns the currently active span if there is one running, otherwise `None`
    """
    if hub is None:
        hub = Hub.current

    current_span = hub.scope.span
    return current_span


def get_traceparent():
    # type: () -> Optional[str]
    """
    Returns the traceparent either from the active span or from the scope.
    """
    return Hub.current.get_traceparent()


def get_baggage():
    # type: () -> Optional[str]
    """
    Returns Baggage either from the active span or from the scope.
    """
    return Hub.current.get_baggage()


def continue_trace(environ_or_headers, op=None, name=None, source=None):
    # type: (Dict[str, Any], Optional[str], Optional[str], Optional[str]) -> Transaction
    """
    Sets the propagation context from environment or headers and returns a transaction.
    """
    return Hub.current.continue_trace(environ_or_headers, op, name, source)
