from __future__ import annotations

from poetry.layouts.layout import Layout
from poetry.layouts.src import SrcLayout


_LAYOUTS = {"src": SrcLayout, "standard": Layout}


def layout(name: str) -> type[Layout]:
    if name not in _LAYOUTS:
        raise ValueError("Invalid layout")

    return _LAYOUTS[name]
