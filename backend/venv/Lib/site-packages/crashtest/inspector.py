from __future__ import annotations

import inspect

from crashtest.frame import Frame
from crashtest.frame_collection import FrameCollection


class Inspector:
    def __init__(self, exception: BaseException):
        self._exception = exception
        self._frames: FrameCollection | None = None
        self._outer_frames = None
        self._inner_frames = None
        self._previous_exception = exception.__context__

    @property
    def exception(self) -> BaseException:
        return self._exception

    @property
    def exception_name(self) -> str:
        return self._exception.__class__.__name__

    @property
    def exception_message(self) -> str:
        return str(self._exception)

    @property
    def frames(self) -> FrameCollection:
        if self._frames is not None:
            return self._frames

        self._frames = FrameCollection()

        tb = self._exception.__traceback__

        while tb:
            frame_info = inspect.getframeinfo(tb)
            self._frames.append(Frame(inspect.FrameInfo(tb.tb_frame, *frame_info)))
            tb = tb.tb_next

        return self._frames

    @property
    def previous_exception(self) -> BaseException | None:
        return self._previous_exception

    def has_previous_exception(self) -> bool:
        return self._previous_exception is not None
