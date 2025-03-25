from __future__ import absolute_import
import sys

from sentry_sdk._compat import reraise
from sentry_sdk.consts import OP
from sentry_sdk.hub import Hub
from sentry_sdk.integrations import Integration, DidNotEnable
from sentry_sdk._types import TYPE_CHECKING
from sentry_sdk.utils import event_from_exception

try:
    import asyncio
    from asyncio.tasks import Task
except ImportError:
    raise DidNotEnable("asyncio not available")


if TYPE_CHECKING:
    from typing import Any
    from collections.abc import Coroutine

    from sentry_sdk._types import ExcInfo


def get_name(coro):
    # type: (Any) -> str
    return (
        getattr(coro, "__qualname__", None)
        or getattr(coro, "__name__", None)
        or "coroutine without __name__"
    )


def patch_asyncio():
    # type: () -> None
    orig_task_factory = None
    try:
        loop = asyncio.get_running_loop()
        orig_task_factory = loop.get_task_factory()

        def _sentry_task_factory(loop, coro, **kwargs):
            # type: (asyncio.AbstractEventLoop, Coroutine[Any, Any, Any], Any) -> asyncio.Future[Any]

            async def _coro_creating_hub_and_span():
                # type: () -> Any
                hub = Hub(Hub.current)
                result = None

                with hub:
                    with hub.start_span(op=OP.FUNCTION, description=get_name(coro)):
                        try:
                            result = await coro
                        except Exception:
                            reraise(*_capture_exception(hub))

                return result

            # Trying to use user set task factory (if there is one)
            if orig_task_factory:
                return orig_task_factory(loop, _coro_creating_hub_and_span(), **kwargs)

            # The default task factory in `asyncio` does not have its own function
            # but is just a couple of lines in `asyncio.base_events.create_task()`
            # Those lines are copied here.

            # WARNING:
            # If the default behavior of the task creation in asyncio changes,
            # this will break!
            task = Task(_coro_creating_hub_and_span(), loop=loop, **kwargs)
            if task._source_traceback:  # type: ignore
                del task._source_traceback[-1]  # type: ignore

            return task

        loop.set_task_factory(_sentry_task_factory)  # type: ignore
    except RuntimeError:
        # When there is no running loop, we have nothing to patch.
        pass


def _capture_exception(hub):
    # type: (Hub) -> ExcInfo
    exc_info = sys.exc_info()

    integration = hub.get_integration(AsyncioIntegration)
    if integration is not None:
        # If an integration is there, a client has to be there.
        client = hub.client  # type: Any

        event, hint = event_from_exception(
            exc_info,
            client_options=client.options,
            mechanism={"type": "asyncio", "handled": False},
        )
        hub.capture_event(event, hint=hint)

    return exc_info


class AsyncioIntegration(Integration):
    identifier = "asyncio"

    @staticmethod
    def setup_once():
        # type: () -> None
        patch_asyncio()
