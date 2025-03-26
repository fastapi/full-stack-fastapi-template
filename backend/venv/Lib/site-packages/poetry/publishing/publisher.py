from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from poetry.publishing.uploader import Uploader
from poetry.utils.authenticator import Authenticator


if TYPE_CHECKING:
    from pathlib import Path

    from cleo.io.io import IO

    from poetry.poetry import Poetry

logger = logging.getLogger(__name__)


class Publisher:
    """
    Registers and publishes packages to remote repositories.
    """

    def __init__(self, poetry: Poetry, io: IO, dist_dir: Path | None = None) -> None:
        self._poetry = poetry
        self._package = poetry.package
        self._io = io
        self._uploader = Uploader(poetry, io, dist_dir)
        self._authenticator = Authenticator(poetry.config, self._io)

    @property
    def files(self) -> list[Path]:
        return self._uploader.files

    def publish(
        self,
        repository_name: str | None,
        username: str | None,
        password: str | None,
        cert: Path | None = None,
        client_cert: Path | None = None,
        dry_run: bool = False,
        skip_existing: bool = False,
    ) -> None:
        if not repository_name:
            url = "https://upload.pypi.org/legacy/"
            repository_name = "pypi"
        else:
            # Retrieving config information
            url = self._poetry.config.get(f"repositories.{repository_name}.url")
            if url is None:
                raise RuntimeError(f"Repository {repository_name} is not defined")

        if not (username and password):
            # Check if we have a token first
            token = self._authenticator.get_pypi_token(repository_name)
            if token:
                logger.debug("Found an API token for %s.", repository_name)
                username = "__token__"
                password = token
            else:
                auth = self._authenticator.get_http_auth(repository_name)
                if auth:
                    logger.debug(
                        "Found authentication information for %s.", repository_name
                    )
                    username = auth.username
                    password = auth.password

        certificates = self._authenticator.get_certs_for_repository(repository_name)
        resolved_cert = cert or certificates.cert or certificates.verify
        resolved_client_cert = client_cert or certificates.client_cert

        self._uploader.auth(username, password)

        if repository_name == "pypi":
            repository_name = "PyPI"
        self._io.write_line(
            f"Publishing <c1>{self._package.pretty_name}</c1>"
            f" (<c2>{self._package.pretty_version}</c2>) to"
            f" <info>{repository_name}</info>"
        )

        self._uploader.upload(
            url,
            cert=resolved_cert,
            client_cert=resolved_client_cert,
            dry_run=dry_run,
            skip_existing=skip_existing,
        )
