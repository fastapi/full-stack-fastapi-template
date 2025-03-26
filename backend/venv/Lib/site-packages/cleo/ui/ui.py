from __future__ import annotations

from cleo.exceptions import CleoValueError
from cleo.ui.component import Component


class UI:
    def __init__(self, components: list[Component] | None = None) -> None:
        self._components: dict[str, Component] = {}

        for component in components or []:
            self.register(component)

    def register(self, component: Component) -> None:
        if not isinstance(component, Component):
            raise CleoValueError(
                "A UI component must inherit from the Component class."
            )

        if not component.name:
            raise CleoValueError("A UI component cannot be anonymous.")

        self._components[component.name] = component

    def component(self, name: str) -> Component:
        if name not in self._components:
            raise CleoValueError(f'UI component "{name}" does not exist.')

        return self._components[name]
