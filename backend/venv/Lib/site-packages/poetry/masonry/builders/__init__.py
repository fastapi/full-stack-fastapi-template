from __future__ import annotations

from poetry.core.masonry.builders.sdist import SdistBuilder
from poetry.core.masonry.builders.wheel import WheelBuilder

from poetry.masonry.builders.editable import EditableBuilder


__all__ = ["BUILD_FORMATS", "EditableBuilder"]


# might be extended by plugins
BUILD_FORMATS = {
    "sdist": SdistBuilder,
    "wheel": WheelBuilder,
}
