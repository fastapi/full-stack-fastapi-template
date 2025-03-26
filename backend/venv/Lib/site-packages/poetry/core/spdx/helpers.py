from __future__ import annotations

import functools
import json

from importlib.resources import files
from typing import TYPE_CHECKING

from poetry.core.spdx.license import License


if TYPE_CHECKING:
    from importlib.abc import Traversable


def _get_license_file() -> Traversable:
    return files(__package__) / "data" / "licenses.json"


def license_by_id(identifier: str) -> License:
    if not identifier:
        raise ValueError("A license identifier is required")

    licenses = _load_licenses()
    return licenses.get(
        identifier.lower(), License(identifier, identifier, False, False)
    )


@functools.lru_cache
def _load_licenses() -> dict[str, License]:
    licenses = {}
    licenses_file = _get_license_file()

    with licenses_file.open(encoding="utf-8") as f:
        data = json.load(f)

    for name, license_info in data.items():
        license = License(name, license_info[0], license_info[1], license_info[2])
        licenses[name.lower()] = license

        full_name = license_info[0].lower()
        if full_name in licenses:
            existing_license = licenses[full_name]
            if not existing_license.is_deprecated:
                continue

        licenses[full_name] = license

    # Add a Proprietary license for non-standard licenses
    licenses["proprietary"] = License("Proprietary", "Proprietary", False, False)

    return licenses


if __name__ == "__main__":
    from poetry.core.spdx.updater import Updater

    updater = Updater()
    updater.dump()
