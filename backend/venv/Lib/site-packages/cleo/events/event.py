from __future__ import annotations


class Event:
    """
    Event
    """

    def __init__(self) -> None:
        self._propagation_stopped = False

    def is_propagation_stopped(self) -> bool:
        return self._propagation_stopped

    def stop_propagation(self) -> None:
        self._propagation_stopped = True
