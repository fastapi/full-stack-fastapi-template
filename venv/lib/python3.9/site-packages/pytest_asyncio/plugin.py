"""pytest-asyncio implementation."""
import asyncio
import contextlib
import enum
import functools
import inspect
import socket
import sys
import warnings
from textwrap import dedent
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    TypeVar,
    Union,
    cast,
    overload,
)

import pytest
from pytest import (
    Config,
    FixtureRequest,
    Function,
    Item,
    Parser,
    PytestPluginManager,
    Session,
)

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

_R = TypeVar("_R")

_ScopeName = Literal["session", "package", "module", "class", "function"]
_T = TypeVar("_T")

SimpleFixtureFunction = TypeVar(
    "SimpleFixtureFunction", bound=Callable[..., Awaitable[_R]]
)
FactoryFixtureFunction = TypeVar(
    "FactoryFixtureFunction", bound=Callable[..., AsyncIterator[_R]]
)
FixtureFunction = Union[SimpleFixtureFunction, FactoryFixtureFunction]
FixtureFunctionMarker = Callable[[FixtureFunction], FixtureFunction]

# https://github.com/pytest-dev/pytest/pull/9510
FixtureDef = Any
SubRequest = Any


class Mode(str, enum.Enum):
    AUTO = "auto"
    STRICT = "strict"


ASYNCIO_MODE_HELP = """\
'auto' - for automatically handling all async functions by the plugin
'strict' - for autoprocessing disabling (useful if different async frameworks \
should be tested together, e.g. \
both pytest-asyncio and pytest-trio are used in the same project)
"""


def pytest_addoption(parser: Parser, pluginmanager: PytestPluginManager) -> None:
    group = parser.getgroup("asyncio")
    group.addoption(
        "--asyncio-mode",
        dest="asyncio_mode",
        default=None,
        metavar="MODE",
        help=ASYNCIO_MODE_HELP,
    )
    parser.addini(
        "asyncio_mode",
        help="default value for --asyncio-mode",
        default="strict",
    )


@overload
def fixture(
    fixture_function: FixtureFunction,
    *,
    scope: "Union[_ScopeName, Callable[[str, Config], _ScopeName]]" = ...,
    params: Optional[Iterable[object]] = ...,
    autouse: bool = ...,
    ids: Union[
        Iterable[Union[str, float, int, bool, None]],
        Callable[[Any], Optional[object]],
        None,
    ] = ...,
    name: Optional[str] = ...,
) -> FixtureFunction:
    ...


@overload
def fixture(
    fixture_function: None = ...,
    *,
    scope: "Union[_ScopeName, Callable[[str, Config], _ScopeName]]" = ...,
    params: Optional[Iterable[object]] = ...,
    autouse: bool = ...,
    ids: Union[
        Iterable[Union[str, float, int, bool, None]],
        Callable[[Any], Optional[object]],
        None,
    ] = ...,
    name: Optional[str] = None,
) -> FixtureFunctionMarker:
    ...


def fixture(
    fixture_function: Optional[FixtureFunction] = None, **kwargs: Any
) -> Union[FixtureFunction, FixtureFunctionMarker]:
    if fixture_function is not None:
        _make_asyncio_fixture_function(fixture_function)
        return pytest.fixture(fixture_function, **kwargs)

    else:

        @functools.wraps(fixture)
        def inner(fixture_function: FixtureFunction) -> FixtureFunction:
            return fixture(fixture_function, **kwargs)

        return inner


def _is_asyncio_fixture_function(obj: Any) -> bool:
    obj = getattr(obj, "__func__", obj)  # instance method maybe?
    return getattr(obj, "_force_asyncio_fixture", False)


def _make_asyncio_fixture_function(obj: Any) -> None:
    if hasattr(obj, "__func__"):
        # instance method, check the function object
        obj = obj.__func__
    obj._force_asyncio_fixture = True


def _is_coroutine(obj: Any) -> bool:
    """Check to see if an object is really an asyncio coroutine."""
    return asyncio.iscoroutinefunction(obj)


def _is_coroutine_or_asyncgen(obj: Any) -> bool:
    return _is_coroutine(obj) or inspect.isasyncgenfunction(obj)


def _get_asyncio_mode(config: Config) -> Mode:
    val = config.getoption("asyncio_mode")
    if val is None:
        val = config.getini("asyncio_mode")
    try:
        return Mode(val)
    except ValueError:
        modes = ", ".join(m.value for m in Mode)
        raise pytest.UsageError(
            f"{val!r} is not a valid asyncio_mode. Valid modes: {modes}."
        )


def pytest_configure(config: Config) -> None:
    """Inject documentation."""
    config.addinivalue_line(
        "markers",
        "asyncio: "
        "mark the test as a coroutine, it will be "
        "run using an asyncio event loop",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_report_header(config: Config) -> List[str]:
    """Add asyncio config to pytest header."""
    mode = _get_asyncio_mode(config)
    return [f"asyncio: mode={mode}"]


def _preprocess_async_fixtures(
    config: Config,
    processed_fixturedefs: Set[FixtureDef],
) -> None:
    asyncio_mode = _get_asyncio_mode(config)
    fixturemanager = config.pluginmanager.get_plugin("funcmanage")
    for fixtures in fixturemanager._arg2fixturedefs.values():
        for fixturedef in fixtures:
            func = fixturedef.func
            if fixturedef in processed_fixturedefs or not _is_coroutine_or_asyncgen(
                func
            ):
                continue
            if not _is_asyncio_fixture_function(func) and asyncio_mode == Mode.STRICT:
                # Ignore async fixtures without explicit asyncio mark in strict mode
                # This applies to pytest_trio fixtures, for example
                continue
            _make_asyncio_fixture_function(func)
            _inject_fixture_argnames(fixturedef)
            _synchronize_async_fixture(fixturedef)
            assert _is_asyncio_fixture_function(fixturedef.func)
            processed_fixturedefs.add(fixturedef)


def _inject_fixture_argnames(fixturedef: FixtureDef) -> None:
    """
    Ensures that `request` and `event_loop` are arguments of the specified fixture.
    """
    to_add = []
    for name in ("request", "event_loop"):
        if name not in fixturedef.argnames:
            to_add.append(name)
    if to_add:
        fixturedef.argnames += tuple(to_add)


def _synchronize_async_fixture(fixturedef: FixtureDef) -> None:
    """
    Wraps the fixture function of an async fixture in a synchronous function.
    """
    if inspect.isasyncgenfunction(fixturedef.func):
        _wrap_asyncgen_fixture(fixturedef)
    elif inspect.iscoroutinefunction(fixturedef.func):
        _wrap_async_fixture(fixturedef)


def _add_kwargs(
    func: Callable[..., Any],
    kwargs: Dict[str, Any],
    event_loop: asyncio.AbstractEventLoop,
    request: SubRequest,
) -> Dict[str, Any]:
    sig = inspect.signature(func)
    ret = kwargs.copy()
    if "request" in sig.parameters:
        ret["request"] = request
    if "event_loop" in sig.parameters:
        ret["event_loop"] = event_loop
    return ret


def _perhaps_rebind_fixture_func(
    func: _T, instance: Optional[Any], unittest: bool
) -> _T:
    if instance is not None:
        # The fixture needs to be bound to the actual request.instance
        # so it is bound to the same object as the test method.
        unbound, cls = func, None
        try:
            unbound, cls = func.__func__, type(func.__self__)  # type: ignore
        except AttributeError:
            pass
        # If unittest is true, the fixture is bound unconditionally.
        # otherwise, only if the fixture was bound before to an instance of
        # the same type.
        if unittest or (cls is not None and isinstance(instance, cls)):
            func = unbound.__get__(instance)  # type: ignore
    return func


def _wrap_asyncgen_fixture(fixturedef: FixtureDef) -> None:
    fixture = fixturedef.func

    @functools.wraps(fixture)
    def _asyncgen_fixture_wrapper(
        event_loop: asyncio.AbstractEventLoop, request: SubRequest, **kwargs: Any
    ):
        func = _perhaps_rebind_fixture_func(
            fixture, request.instance, fixturedef.unittest
        )
        gen_obj = func(**_add_kwargs(func, kwargs, event_loop, request))

        async def setup():
            res = await gen_obj.__anext__()
            return res

        def finalizer() -> None:
            """Yield again, to finalize."""

            async def async_finalizer() -> None:
                try:
                    await gen_obj.__anext__()
                except StopAsyncIteration:
                    pass
                else:
                    msg = "Async generator fixture didn't stop."
                    msg += "Yield only once."
                    raise ValueError(msg)

            event_loop.run_until_complete(async_finalizer())

        result = event_loop.run_until_complete(setup())
        request.addfinalizer(finalizer)
        return result

    fixturedef.func = _asyncgen_fixture_wrapper


def _wrap_async_fixture(fixturedef: FixtureDef) -> None:
    fixture = fixturedef.func

    @functools.wraps(fixture)
    def _async_fixture_wrapper(
        event_loop: asyncio.AbstractEventLoop, request: SubRequest, **kwargs: Any
    ):
        func = _perhaps_rebind_fixture_func(
            fixture, request.instance, fixturedef.unittest
        )

        async def setup():
            res = await func(**_add_kwargs(func, kwargs, event_loop, request))
            return res

        return event_loop.run_until_complete(setup())

    fixturedef.func = _async_fixture_wrapper


_HOLDER: Set[FixtureDef] = set()


@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makeitem(
    collector: Union[pytest.Module, pytest.Class], name: str, obj: object
) -> Union[
    pytest.Item, pytest.Collector, List[Union[pytest.Item, pytest.Collector]], None
]:
    """A pytest hook to collect asyncio coroutines."""
    if not collector.funcnamefilter(name):
        return None
    _preprocess_async_fixtures(collector.config, _HOLDER)
    return None


def pytest_collection_modifyitems(
    session: Session, config: Config, items: List[Item]
) -> None:
    """
    Marks collected async test items as `asyncio` tests.

    The mark is only applied in `AUTO` mode. It is applied to:

      - coroutines
      - staticmethods wrapping coroutines
      - Hypothesis tests wrapping coroutines

    """
    if _get_asyncio_mode(config) != Mode.AUTO:
        return
    function_items = (item for item in items if isinstance(item, Function))
    for function_item in function_items:
        function = function_item.obj
        if isinstance(function, staticmethod):
            # staticmethods need to be unwrapped.
            function = function.__func__
        if (
            _is_coroutine(function)
            or _is_hypothesis_test(function)
            and _hypothesis_test_wraps_coroutine(function)
        ):
            function_item.add_marker("asyncio")


def _hypothesis_test_wraps_coroutine(function: Any) -> bool:
    return _is_coroutine(function.hypothesis.inner_test)


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(
    fixturedef: FixtureDef, request: SubRequest
) -> Optional[object]:
    """Adjust the event loop policy when an event loop is produced."""
    if fixturedef.argname == "event_loop":
        # The use of a fixture finalizer is preferred over the
        # pytest_fixture_post_finalizer hook. The fixture finalizer is invoked once
        # for each fixture, whereas the hook may be invoked multiple times for
        # any specific fixture.
        # see https://github.com/pytest-dev/pytest/issues/5848
        _add_finalizers(
            fixturedef,
            _close_event_loop,
            _provide_clean_event_loop,
        )
        outcome = yield
        loop = outcome.get_result()
        policy = asyncio.get_event_loop_policy()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                old_loop = policy.get_event_loop()
            if old_loop is not loop:
                old_loop.close()
        except RuntimeError:
            # Either the current event loop has been set to None
            # or the loop policy doesn't specify to create new loops
            # or we're not in the main thread
            pass
        policy.set_event_loop(loop)
        return

    yield


def _add_finalizers(fixturedef: FixtureDef, *finalizers: Callable[[], object]) -> None:
    """
    Regsiters the specified fixture finalizers in the fixture.

    Finalizers need to specified in the exact order in which they should be invoked.

    :param fixturedef: Fixture definition which finalizers should be added to
    :param finalizers: Finalizers to be added
    """
    for finalizer in reversed(finalizers):
        fixturedef.addfinalizer(finalizer)


_UNCLOSED_EVENT_LOOP_WARNING = dedent(
    """\
    pytest-asyncio detected an unclosed event loop when tearing down the event_loop
    fixture: %r
    pytest-asyncio will close the event loop for you, but future versions of the
    library will no longer do so. In order to ensure compatibility with future
    versions, please make sure that:
        1. Any custom "event_loop" fixture properly closes the loop after yielding it
        2. The scopes of your custom "event_loop" fixtures do not overlap
        3. Your code does not modify the event loop in async fixtures or tests
    """
)


def _close_event_loop() -> None:
    policy = asyncio.get_event_loop_policy()
    try:
        loop = policy.get_event_loop()
    except RuntimeError:
        loop = None
    if loop is not None:
        if not loop.is_closed():
            warnings.warn(
                _UNCLOSED_EVENT_LOOP_WARNING % loop,
                DeprecationWarning,
            )
        loop.close()


def _provide_clean_event_loop() -> None:
    # At this point, the event loop for the current thread is closed.
    # When a user calls asyncio.get_event_loop(), they will get a closed loop.
    # In order to avoid this side effect from pytest-asyncio, we need to replace
    # the current loop with a fresh one.
    # Note that we cannot set the loop to None, because get_event_loop only creates
    # a new loop, when set_event_loop has not been called.
    policy = asyncio.get_event_loop_policy()
    new_loop = policy.new_event_loop()
    policy.set_event_loop(new_loop)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> Optional[object]:
    """
    Pytest hook called before a test case is run.

    Wraps marked tests in a synchronous function
    where the wrapped test coroutine is executed in an event loop.
    """
    marker = pyfuncitem.get_closest_marker("asyncio")
    if marker is not None:
        funcargs: Dict[str, object] = pyfuncitem.funcargs  # type: ignore[name-defined]
        loop = cast(asyncio.AbstractEventLoop, funcargs["event_loop"])
        if _is_hypothesis_test(pyfuncitem.obj):
            pyfuncitem.obj.hypothesis.inner_test = wrap_in_sync(
                pyfuncitem,
                pyfuncitem.obj.hypothesis.inner_test,
                _loop=loop,
            )
        else:
            pyfuncitem.obj = wrap_in_sync(
                pyfuncitem,
                pyfuncitem.obj,
                _loop=loop,
            )
    yield


def _is_hypothesis_test(function: Any) -> bool:
    return getattr(function, "is_hypothesis_test", False)


def wrap_in_sync(
    pyfuncitem: pytest.Function,
    func: Callable[..., Awaitable[Any]],
    _loop: asyncio.AbstractEventLoop,
):
    """Return a sync wrapper around an async function executing it in the
    current event loop."""

    # if the function is already wrapped, we rewrap using the original one
    # not using __wrapped__ because the original function may already be
    # a wrapped one
    raw_func = getattr(func, "_raw_test_func", None)
    if raw_func is not None:
        func = raw_func

    @functools.wraps(func)
    def inner(*args, **kwargs):
        coro = func(*args, **kwargs)
        if not inspect.isawaitable(coro):
            pyfuncitem.warn(
                pytest.PytestWarning(
                    f"The test {pyfuncitem} is marked with '@pytest.mark.asyncio' "
                    "but it is not an async function. "
                    "Please remove asyncio marker. "
                    "If the test is not marked explicitly, "
                    "check for global markers applied via 'pytestmark'."
                )
            )
            return
        task = asyncio.ensure_future(coro, loop=_loop)
        try:
            _loop.run_until_complete(task)
        except BaseException:
            # run_until_complete doesn't get the result from exceptions
            # that are not subclasses of `Exception`. Consume all
            # exceptions to prevent asyncio's warning from logging.
            if task.done() and not task.cancelled():
                task.exception()
            raise

    inner._raw_test_func = func  # type: ignore[attr-defined]
    return inner


def pytest_runtest_setup(item: pytest.Item) -> None:
    marker = item.get_closest_marker("asyncio")
    if marker is None:
        return
    fixturenames = item.fixturenames  # type: ignore[attr-defined]
    # inject an event loop fixture for all async tests
    if "event_loop" in fixturenames:
        fixturenames.remove("event_loop")
    fixturenames.insert(0, "event_loop")
    obj = getattr(item, "obj", None)
    if not getattr(obj, "hypothesis", False) and getattr(
        obj, "is_hypothesis_test", False
    ):
        pytest.fail(
            "test function `%r` is using Hypothesis, but pytest-asyncio "
            "only works with Hypothesis 3.64.0 or later." % item
        )


@pytest.fixture
def event_loop(request: FixtureRequest) -> Iterator[asyncio.AbstractEventLoop]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def _unused_port(socket_type: int) -> int:
    """Find an unused localhost port from 1024-65535 and return it."""
    with contextlib.closing(socket.socket(type=socket_type)) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
def unused_tcp_port() -> int:
    return _unused_port(socket.SOCK_STREAM)


@pytest.fixture
def unused_udp_port() -> int:
    return _unused_port(socket.SOCK_DGRAM)


@pytest.fixture(scope="session")
def unused_tcp_port_factory() -> Callable[[], int]:
    """A factory function, producing different unused TCP ports."""
    produced = set()

    def factory():
        """Return an unused port."""
        port = _unused_port(socket.SOCK_STREAM)

        while port in produced:
            port = _unused_port(socket.SOCK_STREAM)

        produced.add(port)

        return port

    return factory


@pytest.fixture(scope="session")
def unused_udp_port_factory() -> Callable[[], int]:
    """A factory function, producing different unused UDP ports."""
    produced = set()

    def factory():
        """Return an unused port."""
        port = _unused_port(socket.SOCK_DGRAM)

        while port in produced:
            port = _unused_port(socket.SOCK_DGRAM)

        produced.add(port)

        return port

    return factory
