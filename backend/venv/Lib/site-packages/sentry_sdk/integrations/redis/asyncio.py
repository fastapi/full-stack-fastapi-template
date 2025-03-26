from __future__ import absolute_import

from sentry_sdk import Hub
from sentry_sdk.consts import OP
from sentry_sdk.integrations.redis import (
    RedisIntegration,
    _get_span_description,
    _set_client_data,
    _set_pipeline_data,
)
from sentry_sdk._types import TYPE_CHECKING
from sentry_sdk.tracing import Span
from sentry_sdk.utils import capture_internal_exceptions

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, Union
    from redis.asyncio.client import Pipeline, StrictRedis
    from redis.asyncio.cluster import ClusterPipeline, RedisCluster


def patch_redis_async_pipeline(
    pipeline_cls, is_cluster, get_command_args_fn, set_db_data_fn
):
    # type: (Union[type[Pipeline[Any]], type[ClusterPipeline[Any]]], bool, Any, Callable[[Span, Any], None]) -> None
    old_execute = pipeline_cls.execute

    async def _sentry_execute(self, *args, **kwargs):
        # type: (Any, *Any, **Any) -> Any
        hub = Hub.current

        if hub.get_integration(RedisIntegration) is None:
            return await old_execute(self, *args, **kwargs)

        with hub.start_span(
            op=OP.DB_REDIS, description="redis.pipeline.execute"
        ) as span:
            with capture_internal_exceptions():
                set_db_data_fn(span, self)
                _set_pipeline_data(
                    span,
                    is_cluster,
                    get_command_args_fn,
                    False if is_cluster else self.is_transaction,
                    self._command_stack if is_cluster else self.command_stack,
                )

            return await old_execute(self, *args, **kwargs)

    pipeline_cls.execute = _sentry_execute  # type: ignore[method-assign]


def patch_redis_async_client(cls, is_cluster, set_db_data_fn):
    # type: (Union[type[StrictRedis[Any]], type[RedisCluster[Any]]], bool, Callable[[Span, Any], None]) -> None
    old_execute_command = cls.execute_command

    async def _sentry_execute_command(self, name, *args, **kwargs):
        # type: (Any, str, *Any, **Any) -> Any
        hub = Hub.current

        if hub.get_integration(RedisIntegration) is None:
            return await old_execute_command(self, name, *args, **kwargs)

        description = _get_span_description(name, *args)

        with hub.start_span(op=OP.DB_REDIS, description=description) as span:
            set_db_data_fn(span, self)
            _set_client_data(span, is_cluster, name, *args)

            return await old_execute_command(self, name, *args, **kwargs)

    cls.execute_command = _sentry_execute_command  # type: ignore[method-assign]
