from __future__ import annotations

from typing import TYPE_CHECKING

from cleo.io.inputs.string_input import StringInput
from cleo.io.io import IO
from cleo.io.outputs.null_output import NullOutput


if TYPE_CHECKING:
    from cleo.io.inputs.input import Input


class NullIO(IO):
    def __init__(self, input: Input | None = None) -> None:
        super().__init__(input or StringInput(""), NullOutput(), NullOutput())
