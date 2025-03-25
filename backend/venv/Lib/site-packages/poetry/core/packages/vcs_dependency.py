from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.core.packages.dependency import Dependency


if TYPE_CHECKING:
    from collections.abc import Iterable


class VCSDependency(Dependency):
    """
    Represents a VCS dependency
    """

    def __init__(
        self,
        name: str,
        vcs: str,
        source: str,
        branch: str | None = None,
        tag: str | None = None,
        rev: str | None = None,
        resolved_rev: str | None = None,
        directory: str | None = None,
        groups: Iterable[str] | None = None,
        optional: bool = False,
        develop: bool = False,
        extras: Iterable[str] | None = None,
    ) -> None:
        # Attributes must be immutable for clone() to be safe!
        # (For performance reasons, clone only creates a copy instead of a deep copy).
        self._vcs = vcs

        self._branch = branch
        self._tag = tag
        self._rev = rev
        self._directory = directory

        super().__init__(
            name,
            "*",
            groups=groups,
            optional=optional,
            allows_prereleases=True,
            source_type=self._vcs.lower(),
            source_url=source,
            source_reference=branch or tag or rev or "HEAD",
            source_resolved_reference=resolved_rev,
            source_subdirectory=directory,
            extras=extras,
        )

        self._source = self.source_url or source
        self._develop = develop

    @property
    def vcs(self) -> str:
        return self._vcs

    @property
    def source(self) -> str:
        return self._source

    @property
    def branch(self) -> str | None:
        return self._branch

    @property
    def tag(self) -> str | None:
        return self._tag

    @property
    def rev(self) -> str | None:
        return self._rev

    @property
    def directory(self) -> str | None:
        return self._directory

    @property
    def develop(self) -> bool:
        return self._develop

    @property
    def reference(self) -> str:
        reference = self._branch or self._tag or self._rev or ""
        return reference

    @property
    def pretty_constraint(self) -> str:
        if self._branch:
            what = "branch"
            version = self._branch
        elif self._tag:
            what = "tag"
            version = self._tag
        elif self._rev:
            what = "rev"
            version = self._rev
        else:
            return ""

        return f"{what} {version}"

    def _base_pep_508_name(self, *, resolved: bool = False) -> str:
        from poetry.core.vcs import git

        requirement = self.complete_pretty_name

        parsed_url = git.ParsedUrl.parse(self._source)
        if parsed_url.protocol is not None:
            requirement += f" @ {self._vcs}+{self._source}"
        else:
            requirement += f" @ {self._vcs}+ssh://{parsed_url.format()}"

        if resolved and self.source_resolved_reference:
            requirement += f"@{self.source_resolved_reference}"
        elif self.reference:
            requirement += f"@{self.reference}"

        if self._directory:
            requirement += f"#subdirectory={self._directory}"

        return requirement

    @property
    def base_pep_508_name(self) -> str:
        requirement = self._base_pep_508_name()
        return requirement

    @property
    def base_pep_508_name_resolved(self) -> str:
        requirement = self._base_pep_508_name(resolved=True)
        return requirement

    def is_vcs(self) -> bool:
        return True
