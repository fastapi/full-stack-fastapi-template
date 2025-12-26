from abc import ABC, abstractmethod

from starlette.requests import Request


class KeyStrategy(ABC):
    """Base interface for rate-limit key generation."""

    @abstractmethod
    def get_key(self, request: Request, route_path: str) -> str:
        """Return unique identifier string (e.g., 'ip:127.0.0.1')"""
        raise NotImplementedError
