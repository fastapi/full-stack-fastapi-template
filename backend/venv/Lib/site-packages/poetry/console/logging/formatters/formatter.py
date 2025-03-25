from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class Formatter(ABC):
    @abstractmethod
    def format(self, msg: str) -> str: ...
