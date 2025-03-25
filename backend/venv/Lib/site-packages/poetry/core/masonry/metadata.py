from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.core.utils.helpers import readme_content_type


if TYPE_CHECKING:
    from packaging.utils import NormalizedName

    from poetry.core.packages.project_package import ProjectPackage


class Metadata:
    metadata_version = "2.3"
    # version 1.0
    name: str | None = None
    version: str
    platforms: tuple[str, ...] = ()
    supported_platforms: tuple[str, ...] = ()
    summary: str | None = None
    description: str | None = None
    keywords: str | None = None
    home_page: str | None = None
    download_url: str | None = None
    author: str | None = None
    author_email: str | None = None
    license: str | None = None
    # version 1.1
    classifiers: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()
    obsoletes: tuple[str, ...] = ()
    # version 1.2
    maintainer: str | None = None
    maintainer_email: str | None = None
    requires_python: str | None = None
    requires_external: tuple[str, ...] = ()
    requires_dist: list[str] = []  # noqa: RUF012
    provides_dist: tuple[str, ...] = ()
    obsoletes_dist: tuple[str, ...] = ()
    project_urls: tuple[str, ...] = ()

    # Version 2.1
    description_content_type: str | None = None
    provides_extra: list[NormalizedName] = []  # noqa: RUF012

    @classmethod
    def from_package(cls, package: ProjectPackage) -> Metadata:
        from poetry.core.version.helpers import format_python_constraint

        meta = cls()

        meta.name = package.pretty_name
        meta.version = package.version.to_string()
        meta.summary = package.description
        if package.readme_content:
            meta.description = package.readme_content
        elif package.readmes:
            descriptions = []
            for readme in package.readmes:
                try:
                    descriptions.append(readme.read_text(encoding="utf-8"))
                except FileNotFoundError as e:
                    raise FileNotFoundError(
                        f"Readme path `{readme}` does not exist."
                    ) from e
                except IsADirectoryError as e:
                    raise IsADirectoryError(
                        f"Readme path `{readme}` is a directory."
                    ) from e
                except PermissionError as e:
                    raise PermissionError(
                        f"Readme path `{readme}` is not readable."
                    ) from e
            meta.description = "\n".join(descriptions)

        meta.keywords = ",".join(package.keywords)
        meta.home_page = package.homepage or package.repository_url
        meta.author = package.author_name
        meta.author_email = package.author_email

        if package.license:
            meta.license = package.license.id

        meta.classifiers = tuple(package.all_classifiers)

        # Version 1.2
        meta.maintainer = package.maintainer_name
        meta.maintainer_email = package.maintainer_email

        # Requires python
        if package.requires_python != "*":
            meta.requires_python = package.requires_python
        elif package.python_versions != "*":
            meta.requires_python = format_python_constraint(package.python_constraint)

        meta.requires_dist = [
            d.to_pep_508()
            for d in package.requires
            if not d.is_optional() or d.in_extras
        ]

        # Version 2.1
        if package.readme_content_type:
            meta.description_content_type = package.readme_content_type
        elif package.readmes:
            meta.description_content_type = readme_content_type(package.readmes[0])

        meta.provides_extra = list(package.extras)

        meta.project_urls = tuple(
            f"{name}, {url}" for name, url in package.urls.items()
        )

        return meta
