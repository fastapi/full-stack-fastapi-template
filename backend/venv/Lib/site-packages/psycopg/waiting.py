"""
Code concerned with waiting in different contexts (blocking, async, etc).

These functions are designed to consume the generators returned by the
`generators` module function and to return their final value.

"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import os
import sys
import select
import logging
import selectors
from asyncio import Event, TimeoutError, get_event_loop, wait_for
from selectors import DefaultSelector

from . import errors as e
from .abc import RV, PQGen, PQGenConn, WaitFunc
from ._enums import Ready as Ready
from ._enums import Wait as Wait  # re-exported
from ._cmodule import _psycopg

WAIT_R = Wait.R
WAIT_W = Wait.W
WAIT_RW = Wait.RW
READY_NONE = Ready.NONE
READY_R = Ready.R
READY_W = Ready.W
READY_RW = Ready.RW

logger = logging.getLogger(__name__)


def wait_selector(gen: PQGen[RV], fileno: int, interval: float | None = None) -> RV:
    """
    Wait for a generator using the best strategy available.

    :param gen: a generator performing database operations and yielding
        `Ready` values when it would block.
    :param fileno: the file descriptor to wait on.
    :param interval: interval (in seconds) to check for other interrupt, e.g.
        to allow Ctrl-C. If zero or None, wait indefinitely.
    :return: whatever `!gen` returns on completion.

    Consume `!gen`, scheduling `fileno` for completion when it is reported to
    block. Once ready again send the ready state back to `!gen`.
    """
    try:
        s = next(gen)
        with DefaultSelector() as sel:
            sel.register(fileno, s)
            while True:
                rlist = sel.select(timeout=interval)
                if not rlist:
                    gen.send(READY_NONE)
                    continue

                sel.unregister(fileno)
                ready = rlist[0][1]
                s = gen.send(ready)
                sel.register(fileno, s)

    except StopIteration as ex:
        rv: RV = ex.value
        return rv


def wait_conn(gen: PQGenConn[RV], interval: float | None = None) -> RV:
    """
    Wait for a connection generator using the best strategy available.

    :param gen: a generator performing database operations and yielding
        (fd, `Ready`) pairs when it would block.
    :param interval: interval (in seconds) to check for other interrupt, e.g.
        to allow Ctrl-C. If zero or None, wait indefinitely.
    :return: whatever `!gen` returns on completion.

    Behave like in `wait()`, but take the fileno to wait from the generator
    itself, which might change during processing.
    """
    try:
        fileno, s = next(gen)
        if not interval:
            interval = None
        with DefaultSelector() as sel:
            sel.register(fileno, s)
            while True:
                rlist = sel.select(timeout=interval)
                if not rlist:
                    gen.send(READY_NONE)
                    continue

                sel.unregister(fileno)
                ready = rlist[0][1]
                fileno, s = gen.send(ready)
                sel.register(fileno, s)

    except StopIteration as ex:
        rv: RV = ex.value
        return rv


async def wait_async(gen: PQGen[RV], fileno: int, interval: float | None = None) -> RV:
    """
    Coroutine waiting for a generator to complete.

    :param gen: a generator performing database operations and yielding
        `Ready` values when it would block.
    :param fileno: the file descriptor to wait on.
    :param interval: interval (in seconds) to check for other interrupt, e.g.
        to allow Ctrl-C. If None, wait indefinitely.
    :return: whatever `!gen` returns on completion.

    Behave like in `wait()`, but exposing an `asyncio` interface.
    """
    # Use an event to block and restart after the fd state changes.
    # Not sure this is the best implementation but it's a start.
    ev = Event()
    loop = get_event_loop()
    ready: int
    s: Wait

    def wakeup(state: Ready) -> None:
        nonlocal ready
        ready |= state
        ev.set()

    try:
        s = next(gen)
        while True:
            reader = s & WAIT_R
            writer = s & WAIT_W
            if not reader and not writer:
                raise e.InternalError(f"bad poll status: {s}")
            ev.clear()
            ready = 0
            if reader:
                loop.add_reader(fileno, wakeup, READY_R)
            if writer:
                loop.add_writer(fileno, wakeup, READY_W)
            try:
                if interval is not None:
                    try:
                        await wait_for(ev.wait(), interval)
                    except TimeoutError:
                        pass
                else:
                    await ev.wait()
            finally:
                if reader:
                    loop.remove_reader(fileno)
                if writer:
                    loop.remove_writer(fileno)
            s = gen.send(ready)

    except OSError as ex:
        # Assume the connection was closed
        raise e.OperationalError(str(ex))
    except StopIteration as ex:
        rv: RV = ex.value
        return rv


async def wait_conn_async(gen: PQGenConn[RV], interval: float | None = None) -> RV:
    """
    Coroutine waiting for a connection generator to complete.

    :param gen: a generator performing database operations and yielding
        (fd, `Ready`) pairs when it would block.
    :param interval: interval (in seconds) to check for other interrupt, e.g.
        to allow Ctrl-C. If zero or None, wait indefinitely.
    :return: whatever `!gen` returns on completion.

    Behave like in `wait()`, but take the fileno to wait from the generator
    itself, which might change during processing.
    """
    # Use an event to block and restart after the fd state changes.
    # Not sure this is the best implementation but it's a start.
    ev = Event()
    loop = get_event_loop()
    ready: Ready
    s: Wait

    def wakeup(state: Ready) -> None:
        nonlocal ready
        ready = state
        ev.set()

    try:
        fileno, s = next(gen)
        while True:
            reader = s & WAIT_R
            writer = s & WAIT_W
            if not reader and not writer:
                raise e.InternalError(f"bad poll status: {s}")
            ev.clear()
            ready = 0  # type: ignore[assignment]
            if reader:
                loop.add_reader(fileno, wakeup, READY_R)
            if writer:
                loop.add_writer(fileno, wakeup, READY_W)
            try:
                if interval:
                    try:
                        await wait_for(ev.wait(), interval)
                    except TimeoutError:
                        pass
                else:
                    await ev.wait()
            finally:
                if reader:
                    loop.remove_reader(fileno)
                if writer:
                    loop.remove_writer(fileno)
            fileno, s = gen.send(ready)

    except StopIteration as ex:
        rv: RV = ex.value
        return rv


# Specialised implementation of wait functions.


def wait_select(gen: PQGen[RV], fileno: int, interval: float | None = None) -> RV:
    """
    Wait for a generator using select where supported.

    BUG: on Linux, can't select on FD >= 1024. On Windows it's fine.
    """
    try:
        s = next(gen)

        empty = ()
        fnlist = (fileno,)
        while True:
            rl, wl, xl = select.select(
                fnlist if s & WAIT_R else empty,
                fnlist if s & WAIT_W else empty,
                fnlist,
                interval,
            )
            ready = 0
            if rl:
                ready = READY_R
            if wl:
                ready |= READY_W
            if not ready:
                gen.send(READY_NONE)
                continue

            s = gen.send(ready)

    except StopIteration as ex:
        rv: RV = ex.value
        return rv


if hasattr(selectors, "EpollSelector"):
    _epoll_evmasks = {
        WAIT_R: select.EPOLLONESHOT | select.EPOLLIN | select.EPOLLERR,
        WAIT_W: select.EPOLLONESHOT | select.EPOLLOUT | select.EPOLLERR,
        WAIT_RW: select.EPOLLONESHOT
        | (select.EPOLLIN | select.EPOLLOUT | select.EPOLLERR),
    }
else:
    _epoll_evmasks = {}


def wait_epoll(gen: PQGen[RV], fileno: int, interval: float | None = None) -> RV:
    """
    Wait for a generator using epoll where supported.

    Parameters are like for `wait()`. If it is detected that the best selector
    strategy is `epoll` then this function will be used instead of `wait`.

    See also: https://linux.die.net/man/2/epoll_ctl

    BUG: if the connection FD is closed, `epoll.poll()` hangs. Same for
    EpollSelector. For this reason, wait_poll() is currently preferable.
    To reproduce the bug:

        export PSYCOPG_WAIT_FUNC=wait_epoll
        pytest tests/test_concurrency.py::test_concurrent_close
    """
    try:
        s = next(gen)

        if interval is None or interval < 0:
            interval = 0.0

        with select.epoll() as epoll:
            evmask = _epoll_evmasks[s]
            epoll.register(fileno, evmask)
            while True:
                fileevs = epoll.poll(interval)
                if not fileevs:
                    gen.send(READY_NONE)
                    continue
                ev = fileevs[0][1]
                ready = 0
                if ev & ~select.EPOLLOUT:
                    ready = READY_R
                if ev & ~select.EPOLLIN:
                    ready |= READY_W
                s = gen.send(ready)
                evmask = _epoll_evmasks[s]
                epoll.modify(fileno, evmask)

    except StopIteration as ex:
        rv: RV = ex.value
        return rv


if hasattr(selectors, "PollSelector"):
    _poll_evmasks = {
        WAIT_R: select.POLLIN,
        WAIT_W: select.POLLOUT,
        WAIT_RW: select.POLLIN | select.POLLOUT,
    }
else:
    _poll_evmasks = {}


def wait_poll(gen: PQGen[RV], fileno: int, interval: float | None = None) -> RV:
    """
    Wait for a generator using poll where supported.

    Parameters are like for `wait()`.
    """
    try:
        s = next(gen)

        if interval is None or interval < 0:
            interval = 0
        else:
            interval = int(interval * 1000.0)

        poll = select.poll()
        evmask = _poll_evmasks[s]
        poll.register(fileno, evmask)
        while True:
            fileevs = poll.poll(interval)
            if not fileevs:
                gen.send(READY_NONE)
                continue

            ev = fileevs[0][1]
            ready = 0
            if ev & ~select.POLLOUT:
                ready = READY_R
            if ev & ~select.POLLIN:
                ready |= READY_W
            s = gen.send(ready)
            evmask = _poll_evmasks[s]
            poll.modify(fileno, evmask)

    except StopIteration as ex:
        rv: RV = ex.value
        return rv


def _is_select_patched() -> bool:
    """
    Detect if some greenlet library has patched the select library.

    If this is the case, avoid to use the wait_c function as it doesn't behave
    in a collaborative way.

    Currently supported: gevent.
    """
    # If not imported, don't import it.
    m = sys.modules.get("gevent.monkey")
    if m:
        try:
            if m.is_module_patched("select"):
                return True
        except Exception as ex:
            logger.warning("failed to detect gevent monkey-patching: %s", ex)

    return False


if _psycopg:
    wait_c = _psycopg.wait_c


# Choose the best wait strategy for the platform.
#
# the selectors objects have a generic interface but come with some overhead,
# so we also offer more finely tuned implementations.

wait: WaitFunc

# Allow the user to choose a specific function for testing
if "PSYCOPG_WAIT_FUNC" in os.environ:
    fname = os.environ["PSYCOPG_WAIT_FUNC"]
    if not fname.startswith("wait_") or fname not in globals():
        raise ImportError(
            "PSYCOPG_WAIT_FUNC should be the name of an available wait function;"
            f" got {fname!r}"
        )
    wait = globals()[fname]

# On Windows, for the moment, avoid using wait_c, because it was reported to
# use excessive CPU (see #645).
# TODO: investigate why.
elif _psycopg and sys.platform != "win32" and not _is_select_patched():
    wait = wait_c

elif selectors.DefaultSelector is getattr(selectors, "SelectSelector", None):
    # On Windows, SelectSelector should be the default.
    wait = wait_select

elif hasattr(selectors, "PollSelector"):
    # On linux, EpollSelector is the default. However, it hangs if the fd is
    # closed while polling.
    wait = wait_poll

else:
    wait = wait_selector
