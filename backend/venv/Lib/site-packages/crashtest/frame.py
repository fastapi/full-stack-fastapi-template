from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import inspect

    from types import FrameType


class Frame:
    _content_cache: dict[str, str] = {}

    def __init__(self, frame_info: inspect.FrameInfo) -> None:
        self._frame = frame_info.frame
        self._frame_info = frame_info
        self._lineno = frame_info.lineno
        self._filename = frame_info.filename
        self._function = frame_info.function
        self._lines = None
        self._file_content: str | None = None

    @property
    def frame(self) -> FrameType:
        return self._frame

    @property
    def lineno(self) -> int:
        return self._lineno

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def function(self) -> str:
        return self._function

    @property
    def line(self) -> str:
        if not self._frame_info.code_context:
            return ""

        return self._frame_info.code_context[0]

    @property
    def file_content(self) -> str:
        if self._file_content is None:
            if not self._filename:
                file_content = ""
            else:
                if self._filename not in self.__class__._content_cache:
                    try:
                        with open(self._filename, encoding="utf-8") as f:
                            file_content = f.read()
                    except OSError:
                        file_content = ""

                    self.__class__._content_cache[self._filename] = file_content

                file_content = self.__class__._content_cache[self._filename]

            self._file_content = file_content

        return self._file_content

    def __hash__(self) -> int:
        return hash(self._filename) ^ hash(self._function) ^ hash(self._lineno)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Frame):
            raise NotImplementedError
        return (
            self._filename == other.filename
            and self._function == other.function
            and self._lineno == other.lineno
        )

    def __repr__(self) -> str:
        return f"<Frame {self._filename}, {self._function}, {self._lineno}>"
