import contextlib
import os
import re
import sys

import sentry_sdk
from sentry_sdk.consts import OP, SPANDATA
from sentry_sdk.utils import (
    capture_internal_exceptions,
    filename_for_module,
    Dsn,
    match_regex_list,
    to_string,
    is_sentry_url,
    _is_external_source,
    _module_in_list,
)
from sentry_sdk._compat import PY2, duration_in_milliseconds, iteritems
from sentry_sdk._types import TYPE_CHECKING

if PY2:
    from collections import Mapping
    from urllib import quote, unquote
else:
    from collections.abc import Mapping
    from urllib.parse import quote, unquote

if TYPE_CHECKING:
    import typing

    from typing import Any
    from typing import Dict
    from typing import Generator
    from typing import Optional
    from typing import Union

    from types import FrameType


SENTRY_TRACE_REGEX = re.compile(
    "^[ \t]*"  # whitespace
    "([0-9a-f]{32})?"  # trace_id
    "-?([0-9a-f]{16})?"  # span_id
    "-?([01])?"  # sampled
    "[ \t]*$"  # whitespace
)

# This is a normal base64 regex, modified to reflect that fact that we strip the
# trailing = or == off
base64_stripped = (
    # any of the characters in the base64 "alphabet", in multiples of 4
    "([a-zA-Z0-9+/]{4})*"
    # either nothing or 2 or 3 base64-alphabet characters (see
    # https://en.wikipedia.org/wiki/Base64#Decoding_Base64_without_padding for
    # why there's never only 1 extra character)
    "([a-zA-Z0-9+/]{2,3})?"
)


class EnvironHeaders(Mapping):  # type: ignore
    def __init__(
        self,
        environ,  # type: typing.Mapping[str, str]
        prefix="HTTP_",  # type: str
    ):
        # type: (...) -> None
        self.environ = environ
        self.prefix = prefix

    def __getitem__(self, key):
        # type: (str) -> Optional[Any]
        return self.environ[self.prefix + key.replace("-", "_").upper()]

    def __len__(self):
        # type: () -> int
        return sum(1 for _ in iter(self))

    def __iter__(self):
        # type: () -> Generator[str, None, None]
        for k in self.environ:
            if not isinstance(k, str):
                continue

            k = k.replace("-", "_").upper()
            if not k.startswith(self.prefix):
                continue

            yield k[len(self.prefix) :]


def has_tracing_enabled(options):
    # type: (Optional[Dict[str, Any]]) -> bool
    """
    Returns True if either traces_sample_rate or traces_sampler is
    defined and enable_tracing is set and not false.
    """
    if options is None:
        return False

    return bool(
        options.get("enable_tracing") is not False
        and (
            options.get("traces_sample_rate") is not None
            or options.get("traces_sampler") is not None
        )
    )


@contextlib.contextmanager
def record_sql_queries(
    hub,  # type: sentry_sdk.Hub
    cursor,  # type: Any
    query,  # type: Any
    params_list,  # type:  Any
    paramstyle,  # type: Optional[str]
    executemany,  # type: bool
    record_cursor_repr=False,  # type: bool
):
    # type: (...) -> Generator[sentry_sdk.tracing.Span, None, None]

    # TODO: Bring back capturing of params by default
    if hub.client and hub.client.options["_experiments"].get(
        "record_sql_params", False
    ):
        if not params_list or params_list == [None]:
            params_list = None

        if paramstyle == "pyformat":
            paramstyle = "format"
    else:
        params_list = None
        paramstyle = None

    query = _format_sql(cursor, query)

    data = {}
    if params_list is not None:
        data["db.params"] = params_list
    if paramstyle is not None:
        data["db.paramstyle"] = paramstyle
    if executemany:
        data["db.executemany"] = True
    if record_cursor_repr and cursor is not None:
        data["db.cursor"] = cursor

    with capture_internal_exceptions():
        hub.add_breadcrumb(message=query, category="query", data=data)

    with hub.start_span(op=OP.DB, description=query) as span:
        for k, v in data.items():
            span.set_data(k, v)
        yield span


def maybe_create_breadcrumbs_from_span(hub, span):
    # type: (sentry_sdk.Hub, sentry_sdk.tracing.Span) -> None
    if span.op == OP.DB_REDIS:
        hub.add_breadcrumb(
            message=span.description, type="redis", category="redis", data=span._tags
        )
    elif span.op == OP.HTTP_CLIENT:
        hub.add_breadcrumb(type="http", category="httplib", data=span._data)
    elif span.op == "subprocess":
        hub.add_breadcrumb(
            type="subprocess",
            category="subprocess",
            message=span.description,
            data=span._data,
        )


def add_query_source(hub, span):
    # type: (sentry_sdk.Hub, sentry_sdk.tracing.Span) -> None
    """
    Adds OTel compatible source code information to the span
    """
    client = hub.client
    if client is None:
        return

    if span.timestamp is None or span.start_timestamp is None:
        return

    should_add_query_source = client.options.get("enable_db_query_source", True)
    if not should_add_query_source:
        return

    duration = span.timestamp - span.start_timestamp
    threshold = client.options.get("db_query_source_threshold_ms", 0)
    slow_query = duration_in_milliseconds(duration) > threshold

    if not slow_query:
        return

    project_root = client.options["project_root"]
    in_app_include = client.options.get("in_app_include")
    in_app_exclude = client.options.get("in_app_exclude")

    # Find the correct frame
    frame = sys._getframe()  # type: Union[FrameType, None]
    while frame is not None:
        try:
            abs_path = frame.f_code.co_filename
            if abs_path and PY2:
                abs_path = os.path.abspath(abs_path)
        except Exception:
            abs_path = ""

        try:
            namespace = frame.f_globals.get("__name__")  # type: Optional[str]
        except Exception:
            namespace = None

        is_sentry_sdk_frame = namespace is not None and namespace.startswith(
            "sentry_sdk."
        )

        should_be_included = not _is_external_source(abs_path)
        if namespace is not None:
            if in_app_exclude and _module_in_list(namespace, in_app_exclude):
                should_be_included = False
            if in_app_include and _module_in_list(namespace, in_app_include):
                # in_app_include takes precedence over in_app_exclude, so doing it
                # at the end
                should_be_included = True

        if (
            abs_path.startswith(project_root)
            and should_be_included
            and not is_sentry_sdk_frame
        ):
            break

        frame = frame.f_back
    else:
        frame = None

    # Set the data
    if frame is not None:
        try:
            lineno = frame.f_lineno
        except Exception:
            lineno = None
        if lineno is not None:
            span.set_data(SPANDATA.CODE_LINENO, frame.f_lineno)

        try:
            namespace = frame.f_globals.get("__name__")
        except Exception:
            namespace = None
        if namespace is not None:
            span.set_data(SPANDATA.CODE_NAMESPACE, namespace)

        try:
            filepath = frame.f_code.co_filename
        except Exception:
            filepath = None
        if filepath is not None:
            if namespace is not None and not PY2:
                in_app_path = filename_for_module(namespace, filepath)
            elif project_root is not None and filepath.startswith(project_root):
                in_app_path = filepath.replace(project_root, "").lstrip(os.sep)
            else:
                in_app_path = filepath
            span.set_data(SPANDATA.CODE_FILEPATH, in_app_path)

        try:
            code_function = frame.f_code.co_name
        except Exception:
            code_function = None

        if code_function is not None:
            span.set_data(SPANDATA.CODE_FUNCTION, frame.f_code.co_name)


def extract_sentrytrace_data(header):
    # type: (Optional[str]) -> Optional[Dict[str, Union[str, bool, None]]]
    """
    Given a `sentry-trace` header string, return a dictionary of data.
    """
    if not header:
        return None

    if header.startswith("00-") and header.endswith("-00"):
        header = header[3:-3]

    match = SENTRY_TRACE_REGEX.match(header)
    if not match:
        return None

    trace_id, parent_span_id, sampled_str = match.groups()
    parent_sampled = None

    if trace_id:
        trace_id = "{:032x}".format(int(trace_id, 16))
    if parent_span_id:
        parent_span_id = "{:016x}".format(int(parent_span_id, 16))
    if sampled_str:
        parent_sampled = sampled_str != "0"

    return {
        "trace_id": trace_id,
        "parent_span_id": parent_span_id,
        "parent_sampled": parent_sampled,
    }


def _format_sql(cursor, sql):
    # type: (Any, str) -> Optional[str]

    real_sql = None

    # If we're using psycopg2, it could be that we're
    # looking at a query that uses Composed objects. Use psycopg2's mogrify
    # function to format the query. We lose per-parameter trimming but gain
    # accuracy in formatting.
    try:
        if hasattr(cursor, "mogrify"):
            real_sql = cursor.mogrify(sql)
            if isinstance(real_sql, bytes):
                real_sql = real_sql.decode(cursor.connection.encoding)
    except Exception:
        real_sql = None

    return real_sql or to_string(sql)


class Baggage(object):
    """
    The W3C Baggage header information (see https://www.w3.org/TR/baggage/).
    """

    __slots__ = ("sentry_items", "third_party_items", "mutable")

    SENTRY_PREFIX = "sentry-"
    SENTRY_PREFIX_REGEX = re.compile("^sentry-")

    def __init__(
        self,
        sentry_items,  # type: Dict[str, str]
        third_party_items="",  # type: str
        mutable=True,  # type: bool
    ):
        self.sentry_items = sentry_items
        self.third_party_items = third_party_items
        self.mutable = mutable

    @classmethod
    def from_incoming_header(cls, header):
        # type: (Optional[str]) -> Baggage
        """
        freeze if incoming header already has sentry baggage
        """
        sentry_items = {}
        third_party_items = ""
        mutable = True

        if header:
            for item in header.split(","):
                if "=" not in item:
                    continue

                with capture_internal_exceptions():
                    item = item.strip()
                    key, val = item.split("=")
                    if Baggage.SENTRY_PREFIX_REGEX.match(key):
                        baggage_key = unquote(key.split("-")[1])
                        sentry_items[baggage_key] = unquote(val)
                        mutable = False
                    else:
                        third_party_items += ("," if third_party_items else "") + item

        return Baggage(sentry_items, third_party_items, mutable)

    @classmethod
    def from_options(cls, scope):
        # type: (sentry_sdk.scope.Scope) -> Optional[Baggage]

        sentry_items = {}  # type: Dict[str, str]
        third_party_items = ""
        mutable = False

        client = sentry_sdk.Hub.current.client

        if client is None or scope._propagation_context is None:
            return Baggage(sentry_items)

        options = client.options
        propagation_context = scope._propagation_context

        if propagation_context is not None and "trace_id" in propagation_context:
            sentry_items["trace_id"] = propagation_context["trace_id"]

        if options.get("environment"):
            sentry_items["environment"] = options["environment"]

        if options.get("release"):
            sentry_items["release"] = options["release"]

        if options.get("dsn"):
            sentry_items["public_key"] = Dsn(options["dsn"]).public_key

        if options.get("traces_sample_rate"):
            sentry_items["sample_rate"] = options["traces_sample_rate"]

        user = (scope and scope._user) or {}
        if user.get("segment"):
            sentry_items["user_segment"] = user["segment"]

        return Baggage(sentry_items, third_party_items, mutable)

    @classmethod
    def populate_from_transaction(cls, transaction):
        # type: (sentry_sdk.tracing.Transaction) -> Baggage
        """
        Populate fresh baggage entry with sentry_items and make it immutable
        if this is the head SDK which originates traces.
        """
        hub = transaction.hub or sentry_sdk.Hub.current
        client = hub.client
        sentry_items = {}  # type: Dict[str, str]

        if not client:
            return Baggage(sentry_items)

        options = client.options or {}
        user = (hub.scope and hub.scope._user) or {}

        sentry_items["trace_id"] = transaction.trace_id

        if options.get("environment"):
            sentry_items["environment"] = options["environment"]

        if options.get("release"):
            sentry_items["release"] = options["release"]

        if options.get("dsn"):
            sentry_items["public_key"] = Dsn(options["dsn"]).public_key

        if (
            transaction.name
            and transaction.source not in LOW_QUALITY_TRANSACTION_SOURCES
        ):
            sentry_items["transaction"] = transaction.name

        if user.get("segment"):
            sentry_items["user_segment"] = user["segment"]

        if transaction.sample_rate is not None:
            sentry_items["sample_rate"] = str(transaction.sample_rate)

        if transaction.sampled is not None:
            sentry_items["sampled"] = "true" if transaction.sampled else "false"

        # there's an existing baggage but it was mutable,
        # which is why we are creating this new baggage.
        # However, if by chance the user put some sentry items in there, give them precedence.
        if transaction._baggage and transaction._baggage.sentry_items:
            sentry_items.update(transaction._baggage.sentry_items)

        return Baggage(sentry_items, mutable=False)

    def freeze(self):
        # type: () -> None
        self.mutable = False

    def dynamic_sampling_context(self):
        # type: () -> Dict[str, str]
        header = {}

        for key, item in iteritems(self.sentry_items):
            header[key] = item

        return header

    def serialize(self, include_third_party=False):
        # type: (bool) -> str
        items = []

        for key, val in iteritems(self.sentry_items):
            with capture_internal_exceptions():
                item = Baggage.SENTRY_PREFIX + quote(key) + "=" + quote(str(val))
                items.append(item)

        if include_third_party:
            items.append(self.third_party_items)

        return ",".join(items)


def should_propagate_trace(hub, url):
    # type: (sentry_sdk.Hub, str) -> bool
    """
    Returns True if url matches trace_propagation_targets configured in the given hub. Otherwise, returns False.
    """
    client = hub.client  # type: Any
    trace_propagation_targets = client.options["trace_propagation_targets"]

    if is_sentry_url(hub, url):
        return False

    return match_regex_list(url, trace_propagation_targets, substring_matching=True)


def normalize_incoming_data(incoming_data):
    # type: (Dict[str, Any]) -> Dict[str, Any]
    """
    Normalizes incoming data so the keys are all lowercase with dashes instead of underscores and stripped from known prefixes.
    """
    data = {}
    for key, value in incoming_data.items():
        if key.startswith("HTTP_"):
            key = key[5:]

        key = key.replace("_", "-").lower()
        data[key] = value

    return data


# Circular imports
from sentry_sdk.tracing import LOW_QUALITY_TRANSACTION_SOURCES
