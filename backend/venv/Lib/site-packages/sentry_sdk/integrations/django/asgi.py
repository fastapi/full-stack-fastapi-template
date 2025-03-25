"""
Instrumentation for Django 3.0

Since this file contains `async def` it is conditionally imported in
`sentry_sdk.integrations.django` (depending on the existence of
`django.core.handlers.asgi`.
"""

import asyncio

from django.core.handlers.wsgi import WSGIRequest

from sentry_sdk import Hub, _functools
from sentry_sdk._types import TYPE_CHECKING
from sentry_sdk.consts import OP
from sentry_sdk.hub import _should_send_default_pii

from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.utils import capture_internal_exceptions


if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, Union

    from django.core.handlers.asgi import ASGIRequest
    from django.http.response import HttpResponse

    from sentry_sdk._types import Event, EventProcessor


def _make_asgi_request_event_processor(request):
    # type: (ASGIRequest) -> EventProcessor
    def asgi_request_event_processor(event, hint):
        # type: (Event, dict[str, Any]) -> Event
        # if the request is gone we are fine not logging the data from
        # it.  This might happen if the processor is pushed away to
        # another thread.
        from sentry_sdk.integrations.django import (
            DjangoRequestExtractor,
            _set_user_info,
        )

        if request is None:
            return event

        if type(request) == WSGIRequest:
            return event

        with capture_internal_exceptions():
            DjangoRequestExtractor(request).extract_into_event(event)

        if _should_send_default_pii():
            with capture_internal_exceptions():
                _set_user_info(request, event)

        return event

    return asgi_request_event_processor


def patch_django_asgi_handler_impl(cls):
    # type: (Any) -> None

    from sentry_sdk.integrations.django import DjangoIntegration

    old_app = cls.__call__

    async def sentry_patched_asgi_handler(self, scope, receive, send):
        # type: (Any, Any, Any, Any) -> Any
        hub = Hub.current
        integration = hub.get_integration(DjangoIntegration)
        if integration is None:
            return await old_app(self, scope, receive, send)

        middleware = SentryAsgiMiddleware(
            old_app.__get__(self, cls), unsafe_context_data=True
        )._run_asgi3

        return await middleware(scope, receive, send)

    cls.__call__ = sentry_patched_asgi_handler

    modern_django_asgi_support = hasattr(cls, "create_request")
    if modern_django_asgi_support:
        old_create_request = cls.create_request

        def sentry_patched_create_request(self, *args, **kwargs):
            # type: (Any, *Any, **Any) -> Any
            hub = Hub.current
            integration = hub.get_integration(DjangoIntegration)
            if integration is None:
                return old_create_request(self, *args, **kwargs)

            with hub.configure_scope() as scope:
                request, error_response = old_create_request(self, *args, **kwargs)
                scope.add_event_processor(_make_asgi_request_event_processor(request))

                return request, error_response

        cls.create_request = sentry_patched_create_request


def patch_get_response_async(cls, _before_get_response):
    # type: (Any, Any) -> None
    old_get_response_async = cls.get_response_async

    async def sentry_patched_get_response_async(self, request):
        # type: (Any, Any) -> Union[HttpResponse, BaseException]
        _before_get_response(request)
        return await old_get_response_async(self, request)

    cls.get_response_async = sentry_patched_get_response_async


def patch_channels_asgi_handler_impl(cls):
    # type: (Any) -> None

    import channels  # type: ignore
    from sentry_sdk.integrations.django import DjangoIntegration

    if channels.__version__ < "3.0.0":
        old_app = cls.__call__

        async def sentry_patched_asgi_handler(self, receive, send):
            # type: (Any, Any, Any) -> Any
            if Hub.current.get_integration(DjangoIntegration) is None:
                return await old_app(self, receive, send)

            middleware = SentryAsgiMiddleware(
                lambda _scope: old_app.__get__(self, cls), unsafe_context_data=True
            )

            return await middleware(self.scope)(receive, send)

        cls.__call__ = sentry_patched_asgi_handler

    else:
        # The ASGI handler in Channels >= 3 has the same signature as
        # the Django handler.
        patch_django_asgi_handler_impl(cls)


def wrap_async_view(hub, callback):
    # type: (Hub, Any) -> Any
    @_functools.wraps(callback)
    async def sentry_wrapped_callback(request, *args, **kwargs):
        # type: (Any, *Any, **Any) -> Any

        with hub.configure_scope() as sentry_scope:
            if sentry_scope.profile is not None:
                sentry_scope.profile.update_active_thread_id()

            with hub.start_span(
                op=OP.VIEW_RENDER, description=request.resolver_match.view_name
            ):
                return await callback(request, *args, **kwargs)

    return sentry_wrapped_callback


def _asgi_middleware_mixin_factory(_check_middleware_span):
    # type: (Callable[..., Any]) -> Any
    """
    Mixin class factory that generates a middleware mixin for handling requests
    in async mode.
    """

    class SentryASGIMixin:
        if TYPE_CHECKING:
            _inner = None

        def __init__(self, get_response):
            # type: (Callable[..., Any]) -> None
            self.get_response = get_response
            self._acall_method = None
            self._async_check()

        def _async_check(self):
            # type: () -> None
            """
            If get_response is a coroutine function, turns us into async mode so
            a thread is not consumed during a whole request.
            Taken from django.utils.deprecation::MiddlewareMixin._async_check
            """
            if asyncio.iscoroutinefunction(self.get_response):
                self._is_coroutine = asyncio.coroutines._is_coroutine  # type: ignore

        def async_route_check(self):
            # type: () -> bool
            """
            Function that checks if we are in async mode,
            and if we are forwards the handling of requests to __acall__
            """
            return asyncio.iscoroutinefunction(self.get_response)

        async def __acall__(self, *args, **kwargs):
            # type: (*Any, **Any) -> Any
            f = self._acall_method
            if f is None:
                if hasattr(self._inner, "__acall__"):
                    self._acall_method = f = self._inner.__acall__  # type: ignore
                else:
                    self._acall_method = f = self._inner

            middleware_span = _check_middleware_span(old_method=f)

            if middleware_span is None:
                return await f(*args, **kwargs)

            with middleware_span:
                return await f(*args, **kwargs)

    return SentryASGIMixin
