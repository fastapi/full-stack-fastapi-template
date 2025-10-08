"""The main point for importing pytest-asyncio items."""
from ._version import version as __version__  # noqa
from .plugin import fixture

__all__ = ("fixture",)
