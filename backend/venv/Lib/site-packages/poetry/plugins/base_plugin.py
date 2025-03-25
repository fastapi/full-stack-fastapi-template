from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class BasePlugin(ABC):
    """
    Base class for all plugin types

    The `activate()` method must be implemented and receives the Poetry instance.
    """

    PLUGIN_API_VERSION = "1.0.0"

    @property
    @abstractmethod
    def group(self) -> str:
        """
        Name of entrypoint group the plugin belongs to.
        """
