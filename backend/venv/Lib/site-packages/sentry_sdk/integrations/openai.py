from sentry_sdk import consts
from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Iterable, List, Optional, Callable, Iterator
    from sentry_sdk.tracing import Span

import sentry_sdk
from sentry_sdk._functools import wraps
from sentry_sdk.hub import Hub, _should_send_default_pii
from sentry_sdk.integrations import DidNotEnable, Integration
from sentry_sdk.utils import logger, capture_internal_exceptions, event_from_exception

try:
    from openai.resources.chat.completions import Completions
    from openai.resources import Embeddings

    if TYPE_CHECKING:
        from openai.types.chat import ChatCompletionMessageParam, ChatCompletionChunk
except ImportError:
    raise DidNotEnable("OpenAI not installed")

try:
    import tiktoken  # type: ignore

    enc = tiktoken.get_encoding("cl100k_base")

    def count_tokens(s):
        # type: (str) -> int
        return len(enc.encode_ordinary(s))

    logger.debug("[OpenAI] using tiktoken to count tokens")
except ImportError:
    logger.info(
        "The Sentry Python SDK requires 'tiktoken' in order to measure token usage from some OpenAI APIs"
        "Please install 'tiktoken' if you aren't receiving token usage in Sentry."
        "See https://docs.sentry.io/platforms/python/integrations/openai/ for more information."
    )

    def count_tokens(s):
        # type: (str) -> int
        return 0


COMPLETION_TOKENS_USED = "ai.completion_tоkens.used"
PROMPT_TOKENS_USED = "ai.prompt_tоkens.used"
TOTAL_TOKENS_USED = "ai.total_tоkens.used"


class OpenAIIntegration(Integration):
    identifier = "openai"

    def __init__(self, include_prompts=True):
        # type: (OpenAIIntegration, bool) -> None
        self.include_prompts = include_prompts

    @staticmethod
    def setup_once():
        # type: () -> None
        Completions.create = _wrap_chat_completion_create(Completions.create)
        Embeddings.create = _wrap_embeddings_create(Embeddings.create)


def _capture_exception(hub, exc):
    # type: (Hub, Any) -> None

    if hub.client is not None:
        event, hint = event_from_exception(
            exc,
            client_options=hub.client.options,
            mechanism={"type": "openai", "handled": False},
        )
        hub.capture_event(event, hint=hint)


def _normalize_data(data):
    # type: (Any) -> Any

    # convert pydantic data (e.g. OpenAI v1+) to json compatible format
    if hasattr(data, "model_dump"):
        try:
            return data.model_dump()
        except Exception as e:
            logger.warning("Could not convert pydantic data to JSON: %s", e)
            return data
    if isinstance(data, list):
        return list(_normalize_data(x) for x in data)
    if isinstance(data, dict):
        return {k: _normalize_data(v) for (k, v) in data.items()}
    return data


def set_data_normalized(span, key, value):
    # type: (Span, str, Any) -> None
    span.set_data(key, _normalize_data(value))


def _calculate_chat_completion_usage(
    messages, response, span, streaming_message_responses=None
):
    # type: (Iterable[ChatCompletionMessageParam], Any, Span, Optional[List[str]]) -> None
    completion_tokens = 0
    prompt_tokens = 0
    total_tokens = 0
    if hasattr(response, "usage"):
        if hasattr(response.usage, "completion_tokens") and isinstance(
            response.usage.completion_tokens, int
        ):
            completion_tokens = response.usage.completion_tokens
        if hasattr(response.usage, "prompt_tokens") and isinstance(
            response.usage.prompt_tokens, int
        ):
            prompt_tokens = response.usage.prompt_tokens
        if hasattr(response.usage, "total_tokens") and isinstance(
            response.usage.total_tokens, int
        ):
            total_tokens = response.usage.total_tokens

    if prompt_tokens == 0:
        for message in messages:
            if "content" in message:
                prompt_tokens += count_tokens(message["content"])

    if completion_tokens == 0:
        if streaming_message_responses is not None:
            for message in streaming_message_responses:
                completion_tokens += count_tokens(message)
        elif hasattr(response, "choices"):
            for choice in response.choices:
                if hasattr(choice, "message"):
                    completion_tokens += count_tokens(choice.message)

    if total_tokens == 0:
        total_tokens = prompt_tokens + completion_tokens

    if completion_tokens != 0:
        set_data_normalized(span, COMPLETION_TOKENS_USED, completion_tokens)
    if prompt_tokens != 0:
        set_data_normalized(span, PROMPT_TOKENS_USED, prompt_tokens)
    if total_tokens != 0:
        set_data_normalized(span, TOTAL_TOKENS_USED, total_tokens)


def _wrap_chat_completion_create(f):
    # type: (Callable[..., Any]) -> Callable[..., Any]
    @wraps(f)
    def new_chat_completion(*args, **kwargs):
        # type: (*Any, **Any) -> Any
        hub = Hub.current
        if not hub:
            return f(*args, **kwargs)

        integration = hub.get_integration(OpenAIIntegration)  # type: OpenAIIntegration
        if not integration:
            return f(*args, **kwargs)

        if "messages" not in kwargs:
            # invalid call (in all versions of openai), let it return error
            return f(*args, **kwargs)

        try:
            iter(kwargs["messages"])
        except TypeError:
            # invalid call (in all versions), messages must be iterable
            return f(*args, **kwargs)

        kwargs["messages"] = list(kwargs["messages"])
        messages = kwargs["messages"]
        model = kwargs.get("model")
        streaming = kwargs.get("stream")

        span = sentry_sdk.start_span(
            op=consts.OP.OPENAI_CHAT_COMPLETIONS_CREATE, description="Chat Completion"
        )
        span.__enter__()
        try:
            res = f(*args, **kwargs)
        except Exception as e:
            _capture_exception(Hub.current, e)
            span.__exit__(None, None, None)
            raise e from None

        with capture_internal_exceptions():
            if _should_send_default_pii() and integration.include_prompts:
                set_data_normalized(span, "ai.input_messages", messages)

            set_data_normalized(span, "ai.model_id", model)
            set_data_normalized(span, "ai.streaming", streaming)

            if hasattr(res, "choices"):
                if _should_send_default_pii() and integration.include_prompts:
                    set_data_normalized(
                        span,
                        "ai.responses",
                        list(map(lambda x: x.message, res.choices)),
                    )
                _calculate_chat_completion_usage(messages, res, span)
                span.__exit__(None, None, None)
            elif hasattr(res, "_iterator"):
                data_buf: list[list[str]] = []  # one for each choice

                old_iterator = res._iterator  # type: Iterator[ChatCompletionChunk]

                def new_iterator():
                    # type: () -> Iterator[ChatCompletionChunk]
                    with capture_internal_exceptions():
                        for x in old_iterator:
                            if hasattr(x, "choices"):
                                choice_index = 0
                                for choice in x.choices:
                                    if hasattr(choice, "delta") and hasattr(
                                        choice.delta, "content"
                                    ):
                                        content = choice.delta.content
                                        if len(data_buf) <= choice_index:
                                            data_buf.append([])
                                        data_buf[choice_index].append(content or "")
                                    choice_index += 1
                            yield x
                        if len(data_buf) > 0:
                            all_responses = list(
                                map(lambda chunk: "".join(chunk), data_buf)
                            )
                            if (
                                _should_send_default_pii()
                                and integration.include_prompts
                            ):
                                set_data_normalized(span, "ai.responses", all_responses)
                            _calculate_chat_completion_usage(
                                messages, res, span, all_responses
                            )
                    span.__exit__(None, None, None)

                res._iterator = new_iterator()
            else:
                set_data_normalized(span, "unknown_response", True)
                span.__exit__(None, None, None)
            return res

    return new_chat_completion


def _wrap_embeddings_create(f):
    # type: (Callable[..., Any]) -> Callable[..., Any]

    @wraps(f)
    def new_embeddings_create(*args, **kwargs):
        # type: (*Any, **Any) -> Any

        hub = Hub.current
        if not hub:
            return f(*args, **kwargs)

        integration = hub.get_integration(OpenAIIntegration)  # type: OpenAIIntegration
        if not integration:
            return f(*args, **kwargs)

        with sentry_sdk.start_span(
            op=consts.OP.OPENAI_EMBEDDINGS_CREATE,
            description="OpenAI Embedding Creation",
        ) as span:
            if "input" in kwargs and (
                _should_send_default_pii() and integration.include_prompts
            ):
                if isinstance(kwargs["input"], str):
                    set_data_normalized(span, "ai.input_messages", [kwargs["input"]])
                elif (
                    isinstance(kwargs["input"], list)
                    and len(kwargs["input"]) > 0
                    and isinstance(kwargs["input"][0], str)
                ):
                    set_data_normalized(span, "ai.input_messages", kwargs["input"])
            if "model" in kwargs:
                set_data_normalized(span, "ai.model_id", kwargs["model"])
            try:
                response = f(*args, **kwargs)
            except Exception as e:
                _capture_exception(Hub.current, e)
                raise e from None

            prompt_tokens = 0
            total_tokens = 0
            if hasattr(response, "usage"):
                if hasattr(response.usage, "prompt_tokens") and isinstance(
                    response.usage.prompt_tokens, int
                ):
                    prompt_tokens = response.usage.prompt_tokens
                if hasattr(response.usage, "total_tokens") and isinstance(
                    response.usage.total_tokens, int
                ):
                    total_tokens = response.usage.total_tokens

            if prompt_tokens == 0:
                prompt_tokens = count_tokens(kwargs["input"] or "")

            if total_tokens == 0:
                total_tokens = prompt_tokens

            set_data_normalized(span, PROMPT_TOKENS_USED, prompt_tokens)
            set_data_normalized(span, TOTAL_TOKENS_USED, total_tokens)

            return response

    return new_embeddings_create
