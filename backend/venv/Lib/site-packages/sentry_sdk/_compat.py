import sys
import contextlib
from datetime import datetime, timedelta
from functools import wraps

from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from typing import Tuple
    from typing import Any
    from typing import Type
    from typing import TypeVar
    from typing import Callable

    T = TypeVar("T")


PY2 = sys.version_info[0] == 2
PY33 = sys.version_info[0] == 3 and sys.version_info[1] >= 3
PY37 = sys.version_info[0] == 3 and sys.version_info[1] >= 7
PY310 = sys.version_info[0] == 3 and sys.version_info[1] >= 10
PY311 = sys.version_info[0] == 3 and sys.version_info[1] >= 11

if PY2:
    import urlparse

    text_type = unicode  # noqa

    string_types = (str, text_type)
    number_types = (int, long, float)  # noqa
    int_types = (int, long)  # noqa
    iteritems = lambda x: x.iteritems()  # noqa: B301
    binary_sequence_types = (bytearray, memoryview)

    def datetime_utcnow():
        # type: () -> datetime
        return datetime.utcnow()

    def utc_from_timestamp(timestamp):
        # type: (float) -> datetime
        return datetime.utcfromtimestamp(timestamp)

    def duration_in_milliseconds(delta):
        # type: (timedelta) -> float
        seconds = delta.days * 24 * 60 * 60 + delta.seconds
        milliseconds = seconds * 1000 + float(delta.microseconds) / 1000
        return milliseconds

    def implements_str(cls):
        # type: (T) -> T
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: unicode(x).encode("utf-8")  # noqa
        return cls

    # The line below is written as an "exec" because it triggers a syntax error in Python 3
    exec("def reraise(tp, value, tb=None):\n raise tp, value, tb")

    def contextmanager(func):
        # type: (Callable) -> Callable
        """
        Decorator which creates a contextmanager that can also be used as a
        decorator, similar to how the built-in contextlib.contextmanager
        function works in Python 3.2+.
        """
        contextmanager_func = contextlib.contextmanager(func)

        @wraps(func)
        class DecoratorContextManager:
            def __init__(self, *args, **kwargs):
                # type: (...) -> None
                self.the_contextmanager = contextmanager_func(*args, **kwargs)

            def __enter__(self):
                # type: () -> None
                self.the_contextmanager.__enter__()

            def __exit__(self, *args, **kwargs):
                # type: (...) -> None
                self.the_contextmanager.__exit__(*args, **kwargs)

            def __call__(self, decorated_func):
                # type: (Callable) -> Callable[...]
                @wraps(decorated_func)
                def when_called(*args, **kwargs):
                    # type: (...) -> Any
                    with self.the_contextmanager:
                        return_val = decorated_func(*args, **kwargs)
                    return return_val

                return when_called

        return DecoratorContextManager

else:
    from datetime import timezone
    import urllib.parse as urlparse  # noqa

    text_type = str
    string_types = (text_type,)  # type: Tuple[type]
    number_types = (int, float)  # type: Tuple[type, type]
    int_types = (int,)
    iteritems = lambda x: x.items()
    binary_sequence_types = (bytes, bytearray, memoryview)

    def datetime_utcnow():
        # type: () -> datetime
        return datetime.now(timezone.utc)

    def utc_from_timestamp(timestamp):
        # type: (float) -> datetime
        return datetime.fromtimestamp(timestamp, timezone.utc)

    def duration_in_milliseconds(delta):
        # type: (timedelta) -> float
        return delta / timedelta(milliseconds=1)

    def implements_str(x):
        # type: (T) -> T
        return x

    def reraise(tp, value, tb=None):
        # type: (Optional[Type[BaseException]], Optional[BaseException], Optional[Any]) -> None
        assert value is not None
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    # contextlib.contextmanager already can be used as decorator in Python 3.2+
    contextmanager = contextlib.contextmanager


def with_metaclass(meta, *bases):
    # type: (Any, *Any) -> Any
    class MetaClass(type):
        def __new__(metacls, name, this_bases, d):
            # type: (Any, Any, Any, Any) -> Any
            return meta(name, bases, d)

    return type.__new__(MetaClass, "temporary_class", (), {})


def check_uwsgi_thread_support():
    # type: () -> bool
    # We check two things here:
    #
    # 1. uWSGI doesn't run in threaded mode by default -- issue a warning if
    #    that's the case.
    #
    # 2. Additionally, if uWSGI is running in preforking mode (default), it needs
    #    the --py-call-uwsgi-fork-hooks option for the SDK to work properly. This
    #    is because any background threads spawned before the main process is
    #    forked are NOT CLEANED UP IN THE CHILDREN BY DEFAULT even if
    #    --enable-threads is on. One has to explicitly provide
    #    --py-call-uwsgi-fork-hooks to force uWSGI to run regular cpython
    #    after-fork hooks that take care of cleaning up stale thread data.
    try:
        from uwsgi import opt  # type: ignore
    except ImportError:
        return True

    from sentry_sdk.consts import FALSE_VALUES

    def enabled(option):
        # type: (str) -> bool
        value = opt.get(option, False)
        if isinstance(value, bool):
            return value

        if isinstance(value, bytes):
            try:
                value = value.decode()
            except Exception:
                pass

        return value and str(value).lower() not in FALSE_VALUES

    # When `threads` is passed in as a uwsgi option,
    # `enable-threads` is implied on.
    threads_enabled = "threads" in opt or enabled("enable-threads")
    fork_hooks_on = enabled("py-call-uwsgi-fork-hooks")
    lazy_mode = enabled("lazy-apps") or enabled("lazy")

    if lazy_mode and not threads_enabled:
        from warnings import warn

        warn(
            Warning(
                "IMPORTANT: "
                "We detected the use of uWSGI without thread support. "
                "This might lead to unexpected issues. "
                'Please run uWSGI with "--enable-threads" for full support.'
            )
        )

        return False

    elif not lazy_mode and (not threads_enabled or not fork_hooks_on):
        from warnings import warn

        warn(
            Warning(
                "IMPORTANT: "
                "We detected the use of uWSGI in preforking mode without "
                "thread support. This might lead to crashing workers. "
                'Please run uWSGI with both "--enable-threads" and '
                '"--py-call-uwsgi-fork-hooks" for full support.'
            )
        )

        return False

    return True
