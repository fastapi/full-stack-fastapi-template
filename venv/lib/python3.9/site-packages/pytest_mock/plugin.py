import asyncio
import builtins
import functools
import inspect
import sys
import unittest.mock
import warnings
from typing import Any
from typing import Callable
from typing import cast
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional
from typing import overload
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

import pytest

from ._util import get_mock_module
from ._util import parse_ini_boolean

_T = TypeVar("_T")

if sys.version_info >= (3, 8):
    AsyncMockType = unittest.mock.AsyncMock
    MockType = Union[
        unittest.mock.MagicMock,
        unittest.mock.AsyncMock,
        unittest.mock.NonCallableMagicMock,
    ]
else:
    AsyncMockType = Any
    MockType = Union[unittest.mock.MagicMock, unittest.mock.NonCallableMagicMock]


class PytestMockWarning(UserWarning):
    """Base class for all warnings emitted by pytest-mock."""


class MockerFixture:
    """
    Fixture that provides the same interface to functions in the mock module,
    ensuring that they are uninstalled at the end of each test.
    """

    def __init__(self, config: Any) -> None:
        self._patches_and_mocks: List[Tuple[Any, unittest.mock.MagicMock]] = []
        self.mock_module = mock_module = get_mock_module(config)
        self.patch = self._Patcher(
            self._patches_and_mocks, mock_module
        )  # type: MockerFixture._Patcher
        # aliases for convenience
        self.Mock = mock_module.Mock
        self.MagicMock = mock_module.MagicMock
        self.NonCallableMock = mock_module.NonCallableMock
        self.NonCallableMagicMock = mock_module.NonCallableMagicMock
        self.PropertyMock = mock_module.PropertyMock
        if hasattr(mock_module, "AsyncMock"):
            self.AsyncMock = mock_module.AsyncMock
        self.call = mock_module.call
        self.ANY = mock_module.ANY
        self.DEFAULT = mock_module.DEFAULT
        self.sentinel = mock_module.sentinel
        self.mock_open = mock_module.mock_open
        if hasattr(mock_module, "seal"):
            self.seal = mock_module.seal

    def create_autospec(
        self, spec: Any, spec_set: bool = False, instance: bool = False, **kwargs: Any
    ) -> MockType:
        m: MockType = self.mock_module.create_autospec(
            spec, spec_set, instance, **kwargs
        )
        self._patches_and_mocks.append((None, m))
        return m

    def resetall(
        self, *, return_value: bool = False, side_effect: bool = False
    ) -> None:
        """
        Call reset_mock() on all patchers started by this fixture.

        :param bool return_value: Reset the return_value of mocks.
        :param bool side_effect: Reset the side_effect of mocks.
        """
        supports_reset_mock_with_args: Tuple[Type[Any], ...]
        if hasattr(self, "AsyncMock"):
            supports_reset_mock_with_args = (self.Mock, self.AsyncMock)
        else:
            supports_reset_mock_with_args = (self.Mock,)

        for p, m in self._patches_and_mocks:
            # See issue #237.
            if not hasattr(m, "reset_mock"):
                continue
            if isinstance(m, supports_reset_mock_with_args):
                m.reset_mock(return_value=return_value, side_effect=side_effect)
            else:
                m.reset_mock()

    def stopall(self) -> None:
        """
        Stop all patchers started by this fixture. Can be safely called multiple
        times.
        """
        for p, m in reversed(self._patches_and_mocks):
            if p is not None:
                p.stop()
        self._patches_and_mocks.clear()

    def stop(self, mock: unittest.mock.MagicMock) -> None:
        """
        Stops a previous patch or spy call by passing the ``MagicMock`` object
        returned by it.
        """
        for index, (p, m) in enumerate(self._patches_and_mocks):
            if mock is m:
                p.stop()
                del self._patches_and_mocks[index]
                break
        else:
            raise ValueError("This mock object is not registered")

    def spy(self, obj: object, name: str) -> MockType:
        """
        Create a spy of method. It will run method normally, but it is now
        possible to use `mock` call features with it, like call count.

        :param obj: An object.
        :param name: A method in object.
        :return: Spy object.
        """
        method = getattr(obj, name)
        if inspect.isclass(obj) and isinstance(
            inspect.getattr_static(obj, name), (classmethod, staticmethod)
        ):
            # Can't use autospec classmethod or staticmethod objects before 3.7
            # see: https://bugs.python.org/issue23078
            autospec = False
        else:
            autospec = inspect.ismethod(method) or inspect.isfunction(method)

        def wrapper(*args, **kwargs):
            spy_obj.spy_return = None
            spy_obj.spy_exception = None
            try:
                r = method(*args, **kwargs)
            except BaseException as e:
                spy_obj.spy_exception = e
                raise
            else:
                spy_obj.spy_return = r
            return r

        async def async_wrapper(*args, **kwargs):
            spy_obj.spy_return = None
            spy_obj.spy_exception = None
            try:
                r = await method(*args, **kwargs)
            except BaseException as e:
                spy_obj.spy_exception = e
                raise
            else:
                spy_obj.spy_return = r
            return r

        if asyncio.iscoroutinefunction(method):
            wrapped = functools.update_wrapper(async_wrapper, method)
        else:
            wrapped = functools.update_wrapper(wrapper, method)

        spy_obj = self.patch.object(obj, name, side_effect=wrapped, autospec=autospec)
        spy_obj.spy_return = None
        spy_obj.spy_exception = None
        return spy_obj

    def stub(self, name: Optional[str] = None) -> unittest.mock.MagicMock:
        """
        Create a stub method. It accepts any arguments. Ideal to register to
        callbacks in tests.

        :param name: the constructed stub's name as used in repr
        :return: Stub object.
        """
        return cast(
            unittest.mock.MagicMock,
            self.mock_module.MagicMock(spec=lambda *args, **kwargs: None, name=name),
        )

    def async_stub(self, name: Optional[str] = None) -> AsyncMockType:
        """
        Create a async stub method. It accepts any arguments. Ideal to register to
        callbacks in tests.

        :param name: the constructed stub's name as used in repr
        :return: Stub object.
        """
        return cast(
            AsyncMockType,
            self.mock_module.AsyncMock(spec=lambda *args, **kwargs: None, name=name),
        )

    class _Patcher:
        """
        Object to provide the same interface as mock.patch, mock.patch.object,
        etc. We need this indirection to keep the same API of the mock package.
        """

        DEFAULT = object()

        def __init__(self, patches_and_mocks, mock_module):
            self.__patches_and_mocks = patches_and_mocks
            self.mock_module = mock_module

        def _start_patch(
            self, mock_func: Any, warn_on_mock_enter: bool, *args: Any, **kwargs: Any
        ) -> MockType:
            """Patches something by calling the given function from the mock
            module, registering the patch to stop it later and returns the
            mock object resulting from the mock call.
            """
            p = mock_func(*args, **kwargs)
            mocked: MockType = p.start()
            self.__patches_and_mocks.append((p, mocked))
            if hasattr(mocked, "reset_mock"):
                # check if `mocked` is actually a mock object, as depending on autospec or target
                # parameters `mocked` can be anything
                if hasattr(mocked, "__enter__") and warn_on_mock_enter:
                    if sys.version_info >= (3, 8):
                        depth = 5
                    else:
                        depth = 4
                    mocked.__enter__.side_effect = lambda: warnings.warn(
                        "Mocks returned by pytest-mock do not need to be used as context managers. "
                        "The mocker fixture automatically undoes mocking at the end of a test. "
                        "This warning can be ignored if it was triggered by mocking a context manager. "
                        "https://pytest-mock.readthedocs.io/en/latest/remarks.html#usage-as-context-manager",
                        PytestMockWarning,
                        stacklevel=depth,
                    )
            return mocked

        def object(
            self,
            target: object,
            attribute: str,
            new: object = DEFAULT,
            spec: Optional[object] = None,
            create: bool = False,
            spec_set: Optional[object] = None,
            autospec: Optional[object] = None,
            new_callable: object = None,
            **kwargs: Any
        ) -> MockType:
            """API to mock.patch.object"""
            if new is self.DEFAULT:
                new = self.mock_module.DEFAULT
            return self._start_patch(
                self.mock_module.patch.object,
                True,
                target,
                attribute,
                new=new,
                spec=spec,
                create=create,
                spec_set=spec_set,
                autospec=autospec,
                new_callable=new_callable,
                **kwargs
            )

        def context_manager(
            self,
            target: builtins.object,
            attribute: str,
            new: builtins.object = DEFAULT,
            spec: Optional[builtins.object] = None,
            create: bool = False,
            spec_set: Optional[builtins.object] = None,
            autospec: Optional[builtins.object] = None,
            new_callable: builtins.object = None,
            **kwargs: Any
        ) -> MockType:
            """This is equivalent to mock.patch.object except that the returned mock
            does not issue a warning when used as a context manager."""
            if new is self.DEFAULT:
                new = self.mock_module.DEFAULT
            return self._start_patch(
                self.mock_module.patch.object,
                False,
                target,
                attribute,
                new=new,
                spec=spec,
                create=create,
                spec_set=spec_set,
                autospec=autospec,
                new_callable=new_callable,
                **kwargs
            )

        def multiple(
            self,
            target: builtins.object,
            spec: Optional[builtins.object] = None,
            create: bool = False,
            spec_set: Optional[builtins.object] = None,
            autospec: Optional[builtins.object] = None,
            new_callable: Optional[builtins.object] = None,
            **kwargs: Any
        ) -> Dict[str, MockType]:
            """API to mock.patch.multiple"""
            return self._start_patch(
                self.mock_module.patch.multiple,
                True,
                target,
                spec=spec,
                create=create,
                spec_set=spec_set,
                autospec=autospec,
                new_callable=new_callable,
                **kwargs
            )

        def dict(
            self,
            in_dict: Union[Mapping[Any, Any], str],
            values: Union[Mapping[Any, Any], Iterable[Tuple[Any, Any]]] = (),
            clear: bool = False,
            **kwargs: Any
        ) -> Any:
            """API to mock.patch.dict"""
            return self._start_patch(
                self.mock_module.patch.dict,
                True,
                in_dict,
                values=values,
                clear=clear,
                **kwargs
            )

        @overload
        def __call__(
            self,
            target: str,
            new: None = ...,
            spec: Optional[builtins.object] = ...,
            create: bool = ...,
            spec_set: Optional[builtins.object] = ...,
            autospec: Optional[builtins.object] = ...,
            new_callable: None = ...,
            **kwargs: Any
        ) -> MockType:
            ...

        @overload
        def __call__(
            self,
            target: str,
            new: _T,
            spec: Optional[builtins.object] = ...,
            create: bool = ...,
            spec_set: Optional[builtins.object] = ...,
            autospec: Optional[builtins.object] = ...,
            new_callable: None = ...,
            **kwargs: Any
        ) -> _T:
            ...

        @overload
        def __call__(
            self,
            target: str,
            new: None,
            spec: Optional[builtins.object],
            create: bool,
            spec_set: Optional[builtins.object],
            autospec: Optional[builtins.object],
            new_callable: Callable[[], _T],
            **kwargs: Any
        ) -> _T:
            ...

        @overload
        def __call__(
            self,
            target: str,
            new: None = ...,
            spec: Optional[builtins.object] = ...,
            create: bool = ...,
            spec_set: Optional[builtins.object] = ...,
            autospec: Optional[builtins.object] = ...,
            *,
            new_callable: Callable[[], _T],
            **kwargs: Any
        ) -> _T:
            ...

        def __call__(
            self,
            target: str,
            new: builtins.object = DEFAULT,
            spec: Optional[builtins.object] = None,
            create: bool = False,
            spec_set: Optional[builtins.object] = None,
            autospec: Optional[builtins.object] = None,
            new_callable: Optional[Callable[[], Any]] = None,
            **kwargs: Any
        ) -> Any:
            """API to mock.patch"""
            if new is self.DEFAULT:
                new = self.mock_module.DEFAULT
            return self._start_patch(
                self.mock_module.patch,
                True,
                target,
                new=new,
                spec=spec,
                create=create,
                spec_set=spec_set,
                autospec=autospec,
                new_callable=new_callable,
                **kwargs
            )


def _mocker(pytestconfig: Any) -> Generator[MockerFixture, None, None]:
    """
    Return an object that has the same interface to the `mock` module, but
    takes care of automatically undoing all patches after each test method.
    """
    result = MockerFixture(pytestconfig)
    yield result
    result.stopall()


mocker = pytest.fixture()(_mocker)  # default scope is function
class_mocker = pytest.fixture(scope="class")(_mocker)
module_mocker = pytest.fixture(scope="module")(_mocker)
package_mocker = pytest.fixture(scope="package")(_mocker)
session_mocker = pytest.fixture(scope="session")(_mocker)


_mock_module_patches = []  # type: List[Any]
_mock_module_originals = {}  # type: Dict[str, Any]


def assert_wrapper(
    __wrapped_mock_method__: Callable[..., Any], *args: Any, **kwargs: Any
) -> None:
    __tracebackhide__ = True
    try:
        __wrapped_mock_method__(*args, **kwargs)
        return
    except AssertionError as e:
        if getattr(e, "_mock_introspection_applied", 0):
            msg = str(e)
        else:
            __mock_self = args[0]
            msg = str(e)
            if __mock_self.call_args is not None:
                actual_args, actual_kwargs = __mock_self.call_args
                introspection = ""
                try:
                    assert actual_args == args[1:]
                except AssertionError as e_args:
                    introspection += "\nArgs:\n" + str(e_args)
                try:
                    assert actual_kwargs == kwargs
                except AssertionError as e_kwargs:
                    introspection += "\nKwargs:\n" + str(e_kwargs)
                if introspection:
                    msg += "\n\npytest introspection follows:\n" + introspection
        e = AssertionError(msg)
        e._mock_introspection_applied = True  # type:ignore[attr-defined]
        raise e


def assert_has_calls_wrapper(
    __wrapped_mock_method__: Callable[..., Any], *args: Any, **kwargs: Any
) -> None:
    __tracebackhide__ = True
    try:
        __wrapped_mock_method__(*args, **kwargs)
        return
    except AssertionError as e:
        any_order = kwargs.get("any_order", False)
        if getattr(e, "_mock_introspection_applied", 0) or any_order:
            msg = str(e)
        else:
            __mock_self = args[0]
            msg = str(e)
            if __mock_self.call_args_list is not None:
                actual_calls = list(__mock_self.call_args_list)
                expect_calls = args[1]
                introspection = ""
                from itertools import zip_longest

                for actual_call, expect_call in zip_longest(actual_calls, expect_calls):
                    if actual_call is not None:
                        actual_args, actual_kwargs = actual_call
                    else:
                        actual_args = tuple()
                        actual_kwargs = {}

                    if expect_call is not None:
                        _, expect_args, expect_kwargs = expect_call
                    else:
                        expect_args = tuple()
                        expect_kwargs = {}

                    try:
                        assert actual_args == expect_args
                    except AssertionError as e_args:
                        introspection += "\nArgs:\n" + str(e_args)
                    try:
                        assert actual_kwargs == expect_kwargs
                    except AssertionError as e_kwargs:
                        introspection += "\nKwargs:\n" + str(e_kwargs)
                if introspection:
                    msg += "\n\npytest introspection follows:\n" + introspection
        e = AssertionError(msg)
        e._mock_introspection_applied = True  # type:ignore[attr-defined]
        raise e


def wrap_assert_not_called(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_not_called"], *args, **kwargs)


def wrap_assert_called_with(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called_with"], *args, **kwargs)


def wrap_assert_called_once(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called_once"], *args, **kwargs)


def wrap_assert_called_once_with(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called_once_with"], *args, **kwargs)


def wrap_assert_has_calls(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_has_calls_wrapper(
        _mock_module_originals["assert_has_calls"], *args, **kwargs
    )


def wrap_assert_any_call(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_any_call"], *args, **kwargs)


def wrap_assert_called(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_called"], *args, **kwargs)


def wrap_assert_not_awaited(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_not_awaited"], *args, **kwargs)


def wrap_assert_awaited_with(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited_with"], *args, **kwargs)


def wrap_assert_awaited_once(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited_once"], *args, **kwargs)


def wrap_assert_awaited_once_with(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited_once_with"], *args, **kwargs)


def wrap_assert_has_awaits(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_has_awaits"], *args, **kwargs)


def wrap_assert_any_await(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_any_await"], *args, **kwargs)


def wrap_assert_awaited(*args: Any, **kwargs: Any) -> None:
    __tracebackhide__ = True
    assert_wrapper(_mock_module_originals["assert_awaited"], *args, **kwargs)


def wrap_assert_methods(config: Any) -> None:
    """
    Wrap assert methods of mock module so we can hide their traceback and
    add introspection information to specified argument asserts.
    """
    # Make sure we only do this once
    if _mock_module_originals:
        return

    mock_module = get_mock_module(config)

    wrappers = {
        "assert_called": wrap_assert_called,
        "assert_called_once": wrap_assert_called_once,
        "assert_called_with": wrap_assert_called_with,
        "assert_called_once_with": wrap_assert_called_once_with,
        "assert_any_call": wrap_assert_any_call,
        "assert_has_calls": wrap_assert_has_calls,
        "assert_not_called": wrap_assert_not_called,
    }
    for method, wrapper in wrappers.items():
        try:
            original = getattr(mock_module.NonCallableMock, method)
        except AttributeError:  # pragma: no cover
            continue
        _mock_module_originals[method] = original
        patcher = mock_module.patch.object(mock_module.NonCallableMock, method, wrapper)
        patcher.start()
        _mock_module_patches.append(patcher)

    if hasattr(mock_module, "AsyncMock"):
        async_wrappers = {
            "assert_awaited": wrap_assert_awaited,
            "assert_awaited_once": wrap_assert_awaited_once,
            "assert_awaited_with": wrap_assert_awaited_with,
            "assert_awaited_once_with": wrap_assert_awaited_once_with,
            "assert_any_await": wrap_assert_any_await,
            "assert_has_awaits": wrap_assert_has_awaits,
            "assert_not_awaited": wrap_assert_not_awaited,
        }
        for method, wrapper in async_wrappers.items():
            try:
                original = getattr(mock_module.AsyncMock, method)
            except AttributeError:  # pragma: no cover
                continue
            _mock_module_originals[method] = original
            patcher = mock_module.patch.object(mock_module.AsyncMock, method, wrapper)
            patcher.start()
            _mock_module_patches.append(patcher)

    config.add_cleanup(unwrap_assert_methods)


def unwrap_assert_methods() -> None:
    for patcher in _mock_module_patches:
        try:
            patcher.stop()
        except RuntimeError as e:
            # a patcher might have been stopped by user code (#137)
            # so we need to catch this error here and ignore it;
            # unfortunately there's no public API to check if a patch
            # has been started, so catching the error it is
            if str(e) == "stop called on unstarted patcher":
                pass
            else:
                raise
    _mock_module_patches[:] = []
    _mock_module_originals.clear()


def pytest_addoption(parser: Any) -> None:
    parser.addini(
        "mock_traceback_monkeypatch",
        "Monkeypatch the mock library to improve reporting of the "
        "assert_called_... methods",
        default=True,
    )
    parser.addini(
        "mock_use_standalone_module",
        'Use standalone "mock" (from PyPI) instead of builtin "unittest.mock" '
        "on Python 3",
        default=False,
    )


def pytest_configure(config: Any) -> None:
    tb = config.getoption("--tb", default="auto")
    if (
        parse_ini_boolean(config.getini("mock_traceback_monkeypatch"))
        and tb != "native"
    ):
        wrap_assert_methods(config)
