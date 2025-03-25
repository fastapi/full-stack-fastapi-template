from __future__ import annotations

from typing import Iterable

from cleo.io.outputs.output import Output
from cleo.io.outputs.output import Type
from cleo.io.outputs.output import Verbosity


class NullOutput(Output):
    @property
    def verbosity(self) -> Verbosity:
        return Verbosity.QUIET

    def is_decorated(self) -> bool:
        return False

    def decorated(self, decorated: bool = True) -> None:
        pass

    def supports_utf8(self) -> bool:
        return True

    def set_verbosity(self, verbosity: Verbosity) -> None:
        pass

    def is_quiet(self) -> bool:
        return True

    def is_verbose(self) -> bool:
        return False

    def is_very_verbose(self) -> bool:
        return False

    def is_debug(self) -> bool:
        return False

    def write_line(
        self,
        messages: str | Iterable[str],
        verbosity: Verbosity = Verbosity.NORMAL,
        type: Type = Type.NORMAL,
    ) -> None:
        pass

    def write(
        self,
        messages: str | Iterable[str],
        new_line: bool = False,
        verbosity: Verbosity = Verbosity.NORMAL,
        type: Type = Type.NORMAL,
    ) -> None:
        pass

    def flush(self) -> None:
        pass

    def _write(self, message: str, new_line: bool = False) -> None:
        pass
