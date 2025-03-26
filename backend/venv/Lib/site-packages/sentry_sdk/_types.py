try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False


# Re-exported for compat, since code out there in the wild might use this variable.
MYPY = TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import MutableMapping

    from datetime import datetime

    from types import TracebackType
    from typing import Any
    from typing import Callable
    from typing import Dict
    from typing import List
    from typing import Mapping
    from typing import Optional
    from typing import Tuple
    from typing import Type
    from typing import Union
    from typing_extensions import Literal, TypedDict

    # "critical" is an alias of "fatal" recognized by Relay
    LogLevelStr = Literal["fatal", "critical", "error", "warning", "info", "debug"]

    Event = TypedDict(
        "Event",
        {
            "breadcrumbs": dict[
                Literal["values"], list[dict[str, Any]]
            ],  # TODO: We can expand on this type
            "check_in_id": str,
            "contexts": dict[str, dict[str, object]],
            "dist": str,
            "duration": Optional[float],
            "environment": str,
            "errors": list[dict[str, Any]],  # TODO: We can expand on this type
            "event_id": str,
            "exception": dict[
                Literal["values"], list[dict[str, Any]]
            ],  # TODO: We can expand on this type
            "extra": MutableMapping[str, object],
            "fingerprint": list[str],
            "level": LogLevelStr,
            "logentry": Mapping[str, object],
            "logger": str,
            "measurements": dict[str, object],
            "message": str,
            "modules": dict[str, str],
            "monitor_config": Mapping[str, object],
            "monitor_slug": Optional[str],
            "platform": Literal["python"],
            "profile": object,  # Should be sentry_sdk.profiler.Profile, but we can't import that here due to circular imports
            "release": str,
            "request": dict[str, object],
            "sdk": Mapping[str, object],
            "server_name": str,
            "spans": list[dict[str, object]],
            "stacktrace": dict[
                str, object
            ],  # We access this key in the code, but I am unsure whether we ever set it
            "start_timestamp": datetime,
            "status": Optional[str],
            "tags": MutableMapping[
                str, str
            ],  # Tags must be less than 200 characters each
            "threads": dict[
                Literal["values"], list[dict[str, Any]]
            ],  # TODO: We can expand on this type
            "timestamp": Optional[datetime],  # Must be set before sending the event
            "transaction": str,
            "transaction_info": Mapping[str, Any],  # TODO: We can expand on this type
            "type": Literal["check_in", "transaction"],
            "user": dict[str, object],
            "_metrics_summary": dict[str, object],
        },
        total=False,
    )

    ExcInfo = Tuple[
        Optional[Type[BaseException]], Optional[BaseException], Optional[TracebackType]
    ]

    Hint = Dict[str, Any]

    Breadcrumb = Dict[str, Any]
    BreadcrumbHint = Dict[str, Any]

    SamplingContext = Dict[str, Any]

    EventProcessor = Callable[[Event, Hint], Optional[Event]]
    ErrorProcessor = Callable[[Event, ExcInfo], Optional[Event]]
    BreadcrumbProcessor = Callable[[Breadcrumb, BreadcrumbHint], Optional[Breadcrumb]]
    TransactionProcessor = Callable[[Event, Hint], Optional[Event]]

    TracesSampler = Callable[[SamplingContext], Union[float, int, bool]]

    # https://github.com/python/mypy/issues/5710
    NotImplementedType = Any

    EventDataCategory = Literal[
        "default",
        "error",
        "crash",
        "transaction",
        "security",
        "attachment",
        "session",
        "internal",
        "profile",
        "metric_bucket",
        "monitor",
    ]
    SessionStatus = Literal["ok", "exited", "crashed", "abnormal"]
    EndpointType = Literal["store", "envelope"]

    DurationUnit = Literal[
        "nanosecond",
        "microsecond",
        "millisecond",
        "second",
        "minute",
        "hour",
        "day",
        "week",
    ]

    InformationUnit = Literal[
        "bit",
        "byte",
        "kilobyte",
        "kibibyte",
        "megabyte",
        "mebibyte",
        "gigabyte",
        "gibibyte",
        "terabyte",
        "tebibyte",
        "petabyte",
        "pebibyte",
        "exabyte",
        "exbibyte",
    ]

    FractionUnit = Literal["ratio", "percent"]
    MeasurementUnit = Union[DurationUnit, InformationUnit, FractionUnit, str]

    ProfilerMode = Literal["sleep", "thread", "gevent", "unknown"]

    # Type of the metric.
    MetricType = Literal["d", "s", "g", "c"]

    # Value of the metric.
    MetricValue = Union[int, float, str]

    # Internal representation of tags as a tuple of tuples (this is done in order to allow for the same key to exist
    # multiple times).
    MetricTagsInternal = Tuple[Tuple[str, str], ...]

    # External representation of tags as a dictionary.
    MetricTagValue = Union[
        str,
        int,
        float,
        None,
        List[Union[int, str, float, None]],
        Tuple[Union[int, str, float, None], ...],
    ]
    MetricTags = Mapping[str, MetricTagValue]

    # Value inside the generator for the metric value.
    FlushedMetricValue = Union[int, float]

    BucketKey = Tuple[MetricType, str, MeasurementUnit, MetricTagsInternal]
    MetricMetaKey = Tuple[MetricType, str, MeasurementUnit]

    MonitorConfigScheduleType = Literal["crontab", "interval"]
    MonitorConfigScheduleUnit = Literal[
        "year",
        "month",
        "week",
        "day",
        "hour",
        "minute",
        "second",  # not supported in Sentry and will result in a warning
    ]

    MonitorConfigSchedule = TypedDict(
        "MonitorConfigSchedule",
        {
            "type": MonitorConfigScheduleType,
            "value": Union[int, str],
            "unit": MonitorConfigScheduleUnit,
        },
        total=False,
    )

    MonitorConfig = TypedDict(
        "MonitorConfig",
        {
            "schedule": MonitorConfigSchedule,
            "timezone": str,
            "checkin_margin": int,
            "max_runtime": int,
            "failure_issue_threshold": int,
            "recovery_threshold": int,
        },
        total=False,
    )
