import sys

from sentry_sdk.hub import Hub
from sentry_sdk.utils import event_from_exception
from sentry_sdk._compat import reraise
from sentry_sdk._functools import wraps


from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    from typing import Callable
    from typing import TypeVar
    from typing import Union
    from typing import Optional

    from typing import overload

    F = TypeVar("F", bound=Callable[..., Any])

else:

    def overload(x):
        # type: (F) -> F
        return x


@overload
def serverless_function(f, flush=True):
    # type: (F, bool) -> F
    pass


@overload
def serverless_function(f=None, flush=True):  # noqa: F811
    # type: (None, bool) -> Callable[[F], F]
    pass


def serverless_function(f=None, flush=True):  # noqa
    # type: (Optional[F], bool) -> Union[F, Callable[[F], F]]
    def wrapper(f):
        # type: (F) -> F
        @wraps(f)
        def inner(*args, **kwargs):
            # type: (*Any, **Any) -> Any
            with Hub(Hub.current) as hub:
                with hub.configure_scope() as scope:
                    scope.clear_breadcrumbs()

                try:
                    return f(*args, **kwargs)
                except Exception:
                    _capture_and_reraise()
                finally:
                    if flush:
                        _flush_client()

        return inner  # type: ignore

    if f is None:
        return wrapper
    else:
        return wrapper(f)


def _capture_and_reraise():
    # type: () -> None
    exc_info = sys.exc_info()
    hub = Hub.current
    if hub.client is not None:
        event, hint = event_from_exception(
            exc_info,
            client_options=hub.client.options,
            mechanism={"type": "serverless", "handled": False},
        )
        hub.capture_event(event, hint=hint)

    reraise(*exc_info)


def _flush_client():
    # type: () -> None
    return Hub.current.flush()
