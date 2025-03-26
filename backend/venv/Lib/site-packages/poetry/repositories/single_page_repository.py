from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.repositories.exceptions import PackageNotFoundError
from poetry.repositories.legacy_repository import LegacyRepository
from poetry.repositories.link_sources.html import HTMLPage


if TYPE_CHECKING:
    from packaging.utils import NormalizedName


class SinglePageRepository(LegacyRepository):
    def _get_page(self, name: NormalizedName) -> HTMLPage:
        """
        Single page repositories only have one page irrespective of endpoint.
        """
        response = self._get_response("")
        if not response:
            raise PackageNotFoundError(f"Package [{name}] not found.")
        return HTMLPage(response.url, response.text)
