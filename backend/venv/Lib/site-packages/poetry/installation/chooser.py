from __future__ import annotations

import logging
import re

from typing import TYPE_CHECKING
from typing import Any

from poetry.config.config import Config
from poetry.config.config import PackageFilterPolicy
from poetry.console.exceptions import ConsoleMessage
from poetry.console.exceptions import PoetryRuntimeError
from poetry.repositories.http_repository import HTTPRepository
from poetry.utils.helpers import get_highest_priority_hash_type
from poetry.utils.wheel import Wheel


if TYPE_CHECKING:
    from poetry.core.constraints.version import Version
    from poetry.core.packages.package import Package
    from poetry.core.packages.utils.link import Link

    from poetry.repositories.repository_pool import RepositoryPool
    from poetry.utils.env import Env


logger = logging.getLogger(__name__)


class Chooser:
    """
    A Chooser chooses an appropriate release archive for packages.
    """

    def __init__(
        self, pool: RepositoryPool, env: Env, config: Config | None = None
    ) -> None:
        self._pool = pool
        self._env = env
        self._config = config or Config.create()
        self._no_binary_policy: PackageFilterPolicy = PackageFilterPolicy(
            self._config.get("installer.no-binary", [])
        )
        self._only_binary_policy: PackageFilterPolicy = PackageFilterPolicy(
            self._config.get("installer.only-binary", [])
        )

    def choose_for(self, package: Package) -> Link:
        """
        Return the url of the selected archive for a given package.
        """
        links = []

        # these are used only for providing insightful errors to the user
        unsupported_wheels = set()
        links_seen = 0
        wheels_skipped = 0
        sdists_skipped = 0

        for link in self._get_links(package):
            links_seen += 1

            if link.is_wheel:
                if not self._no_binary_policy.allows(package.name):
                    logger.debug(
                        "Skipping wheel for %s as requested in no binary policy for"
                        " package (%s)",
                        link.filename,
                        package.name,
                    )
                    wheels_skipped += 1
                    continue

                if not Wheel(link.filename).is_supported_by_environment(self._env):
                    logger.debug(
                        "Skipping wheel %s as this is not supported by the current"
                        " environment",
                        link.filename,
                    )
                    unsupported_wheels.add(link.filename)
                    continue

            if link.ext in {".egg", ".exe", ".msi", ".rpm", ".srpm"}:
                logger.debug("Skipping unsupported distribution %s", link.filename)
                continue

            if link.is_sdist and not self._only_binary_policy.allows(package.name):
                logger.debug(
                    "Skipping source distribution for %s as requested in only binary policy for"
                    " package (%s)",
                    link.filename,
                    package.name,
                )
                sdists_skipped += 1
                continue

            links.append(link)

        if not links:
            raise self._no_links_found_error(
                package, links_seen, wheels_skipped, sdists_skipped, unsupported_wheels
            )

        # Get the best link
        chosen = max(links, key=lambda link: self._sort_key(package, link))

        return chosen

    def _no_links_found_error(
        self,
        package: Package,
        links_seen: int,
        wheels_skipped: int,
        sdists_skipped: int,
        unsupported_wheels: set[str],
    ) -> PoetryRuntimeError:
        messages = []
        info = (
            f"This is likely not a Poetry issue.\n\n"
            f"  - {links_seen} candidate(s) were identified for the package\n"
        )

        if wheels_skipped > 0:
            info += f"  - {wheels_skipped} wheel(s) were skipped due to your <c1>installer.no-binary</> policy\n"

        if sdists_skipped > 0:
            info += f"  - {sdists_skipped} source distribution(s) were skipped due to your <c1>installer.only-binary</> policy\n"

        if unsupported_wheels:
            info += (
                f"  - {len(unsupported_wheels)} wheel(s) were skipped as your project's environment does not support "
                f"the identified abi tags\n"
            )

        messages.append(ConsoleMessage(info.strip()))

        if unsupported_wheels:
            messages += [
                ConsoleMessage(
                    "The following wheel(s) were skipped as the current project environment does not support them "
                    "due to abi compatibility issues.",
                    debug=True,
                ),
                ConsoleMessage("\n".join(unsupported_wheels), debug=True)
                .indent("  - ")
                .wrap("warning"),
                ConsoleMessage(
                    "If you would like to see the supported tags in your project environment, you can execute "
                    "the following command:\n\n"
                    "    <c1>poetry debug tags</>",
                    debug=True,
                ),
            ]

        source_hint = ""
        if package.source_type and package.source_reference:
            source_hint += f" ({package.source_reference})"

        messages.append(
            ConsoleMessage(
                f"Make sure the lockfile is up-to-date. You can try one of the following;\n\n"
                f"    1. <b>Regenerate lockfile: </><fg=yellow>poetry lock --no-cache --regenerate</>\n"
                f"    2. <b>Update package     : </><fg=yellow>poetry update --no-cache {package.name}</>\n\n"
                f"If neither works, please first check to verify that the {package.name} has published wheels "
                f"available from your configured source{source_hint} that are compatible with your environment"
                f"- ie. operating system, architecture (x86_64, arm64 etc.), python interpreter."
            )
            .make_section("Solutions")
            .wrap("info")
        )

        return PoetryRuntimeError(
            reason=f"Unable to find installation candidates for {package}",
            messages=messages,
        )

    def _get_links(self, package: Package) -> list[Link]:
        if package.source_type:
            assert package.source_reference is not None
            repository = self._pool.repository(package.source_reference)

        elif not self._pool.has_repository("pypi"):
            repository = self._pool.repositories[0]
        else:
            repository = self._pool.repository("pypi")
        links = repository.find_links_for_package(package)

        locked_hashes = {f["hash"] for f in package.files}
        if not locked_hashes:
            return links

        selected_links = []
        skipped = []
        locked_hash_names = {h.split(":")[0] for h in locked_hashes}
        for link in links:
            if not link.hashes:
                selected_links.append(link)
                continue

            link_hash: str | None = None
            if (candidates := locked_hash_names.intersection(link.hashes.keys())) and (
                hash_name := get_highest_priority_hash_type(candidates, link.filename)
            ):
                link_hash = f"{hash_name}:{link.hashes[hash_name]}"

            elif isinstance(repository, HTTPRepository):
                link_hash = repository.calculate_sha256(link)

            if link_hash not in locked_hashes:
                skipped.append((link.filename, link_hash))
                logger.debug(
                    "Skipping %s as %s checksum does not match expected value",
                    link.filename,
                    link_hash,
                )
                continue

            selected_links.append(link)

        if links and not selected_links:
            reason = f"Downloaded distributions for <b>{package.pretty_name} ({package.pretty_version})</> did not match any known checksums in your lock file."
            link_hashes = "\n".join(f"  - {link}({h})" for link, h in skipped)
            known_hashes = "\n".join(f"  - {h}" for h in locked_hashes)
            messages = [
                ConsoleMessage(
                    "<options=bold>Causes:</>\n"
                    "  - invalid or corrupt cache either during locking or installation\n"
                    "  - network interruptions or errors causing corrupted downloads\n\n"
                    "<b>Solutions:</>\n"
                    "  1. Try running your command again using the <c1>--no-cache</> global option enabled.\n"
                    "  2. Try regenerating your lock file using (<c1>poetry lock --no-cache --regenerate</>).\n\n"
                    "If any of those solutions worked, you will have to clear your caches using (<c1>poetry cache clear --all CACHE_NAME</>)."
                ),
                ConsoleMessage(
                    f"Poetry retrieved the following links:\n"
                    f"{link_hashes}\n\n"
                    f"The lockfile contained only the following hashes:\n"
                    f"{known_hashes}",
                    debug=True,
                ),
            ]
            raise PoetryRuntimeError(reason, messages)

        return selected_links

    def _sort_key(
        self, package: Package, link: Link
    ) -> tuple[int, int, int, Version, tuple[Any, ...], int]:
        """
        Function to pass as the `key` argument to a call to sorted() to sort
        InstallationCandidates by preference.
        Returns a tuple such that tuples sorting as greater using Python's
        default comparison operator are more preferred.
        The preference is as follows:
        First and foremost, candidates with allowed (matching) hashes are
        always preferred over candidates without matching hashes. This is
        because e.g. if the only candidate with an allowed hash is yanked,
        we still want to use that candidate.
        Second, excepting hash considerations, candidates that have been
        yanked (in the sense of PEP 592) are always less preferred than
        candidates that haven't been yanked. Then:
        If not finding wheels, they are sorted by version only.
        If finding wheels, then the sort order is by version, then:
          1. existing installs
          2. wheels ordered via Wheel.support_index_min(self._supported_tags)
          3. source archives
        If prefer_binary was set, then all wheels are sorted above sources.
        Note: it was considered to embed this logic into the Link
              comparison operators, but then different sdist links
              with the same version, would have to be considered equal
        """
        build_tag: tuple[Any, ...] = ()
        binary_preference = 0
        if link.is_wheel:
            wheel = Wheel(link.filename)
            if not wheel.is_supported_by_environment(self._env):
                raise RuntimeError(
                    f"{wheel.filename} is not a supported wheel for this platform. It "
                    "can't be sorted."
                )

            # TODO: Binary preference
            pri = -(wheel.get_minimum_supported_index(self._env.supported_tags) or 0)
            if wheel.build_tag is not None:
                match = re.match(r"^(\d+)(.*)$", wheel.build_tag)
                if not match:
                    raise ValueError(f"Unable to parse build tag: {wheel.build_tag}")
                build_tag_groups = match.groups()
                build_tag = (int(build_tag_groups[0]), build_tag_groups[1])
        else:  # sdist
            support_num = len(self._env.supported_tags)
            pri = -support_num

        has_allowed_hash = int(self._is_link_hash_allowed_for_package(link, package))

        yank_value = int(not link.yanked)

        return (
            has_allowed_hash,
            yank_value,
            binary_preference,
            package.version,
            build_tag,
            pri,
        )

    def _is_link_hash_allowed_for_package(self, link: Link, package: Package) -> bool:
        if not link.hashes:
            return True

        link_hashes = {f"{name}:{h}" for name, h in link.hashes.items()}
        locked_hashes = {f["hash"] for f in package.files}

        return bool(link_hashes & locked_hashes)
