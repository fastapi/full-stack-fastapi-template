import sys

__all__ = ['files']


if sys.version_info < (3, 9):
    from importlib_resources import files
else:
    from importlib.resources import files
