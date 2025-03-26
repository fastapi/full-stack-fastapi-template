from __future__ import annotations

import dataclasses

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Literal

from cleo.helpers import option
from poetry.core.constraints.version import Version

from poetry.console.commands.env_command import EnvCommand
from poetry.masonry.builders import BUILD_FORMATS
from poetry.utils._compat import metadata
from poetry.utils.helpers import remove_directory
from poetry.utils.isolated_build import isolated_builder


if TYPE_CHECKING:
    from collections.abc import Callable

    from cleo.io.inputs.option import Option
    from cleo.io.io import IO

    from poetry.poetry import Poetry
    from poetry.utils.env import Env

DistributionType = Literal["sdist", "wheel"]


@dataclasses.dataclass(frozen=True)
class BuildOptions:
    clean: bool
    formats: list[DistributionType]
    output: str
    config_settings: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        for fmt in self.formats:
            if fmt not in BUILD_FORMATS:
                raise ValueError(f"Invalid format: {fmt}")


class BuildHandler:
    def __init__(self, poetry: Poetry, env: Env, io: IO) -> None:
        self.poetry = poetry
        self.env = env
        self.io = io

    def _build(
        self,
        fmt: DistributionType,
        executable: Path,
        target_dir: Path,
        config_settings: dict[str, Any],
    ) -> None:
        builder = BUILD_FORMATS[fmt]

        builder(
            self.poetry,
            executable=executable,
            config_settings=config_settings,
        ).build(target_dir)

    def _isolated_build(
        self,
        fmt: DistributionType,
        executable: Path,
        target_dir: Path,
        config_settings: dict[str, Any],
    ) -> None:
        with isolated_builder(
            source=self.poetry.file.path.parent,
            distribution=fmt,
            python_executable=executable,
        ) as builder:
            builder.build(fmt, target_dir, config_settings=config_settings)

    def _requires_isolated_build(self) -> bool:
        """
        Determines if an isolated build is required.

        An isolated build is required if:
        - The package has a build script.
        - There are multiple build system dependencies.
        - The build dependency is not `poetry-core`.
        - The installed `poetry-core` version does not satisfy the build dependency constraints.
        - The build dependency has a source type (e.g. is a VcsDependency).

        :returns: True if an isolated build is required, False otherwise.
        """
        if not self._has_build_backend_defined():
            self.io.write_error_line(
                "<warning><b>WARNING</>: No build backend defined. Please define one in the <c1>pyproject.toml</>.\n"
                "Falling back to using the built-in `poetry-core` version.\n"
                "In a future release Poetry will fallback to `setuptools` as defined by PEP 517.\n"
                "More details can be found at https://python-poetry.org/docs/libraries/#packaging</>"
            )
            return False

        if (
            self.poetry.package.build_script
            or len(self.poetry.build_system_dependencies) != 1
        ):
            return True

        build_dependency = self.poetry.build_system_dependencies[0]
        if build_dependency.name != "poetry-core":
            return True

        poetry_core_version = Version.parse(metadata.version("poetry-core"))

        return bool(
            not build_dependency.constraint.allows(poetry_core_version)
            or build_dependency.source_type
        )

    def _get_builder(self) -> Callable[..., None]:
        if self._requires_isolated_build():
            return self._isolated_build

        return self._build

    def _has_build_backend_defined(self) -> bool:
        return "build-backend" in self.poetry.pyproject.data.get("build-system", {})

    def build(self, options: BuildOptions) -> int:
        if not self.poetry.is_package_mode:
            self.io.write_error_line(
                "Building a package is not possible in non-package mode."
            )
            return 1

        dist_dir = Path(options.output)
        package = self.poetry.package
        self.io.write_line(
            f"Building <c1>{package.pretty_name}</c1> (<c2>{package.version}</c2>)"
        )

        if not dist_dir.is_absolute():
            dist_dir = self.poetry.pyproject_path.parent / dist_dir

        if options.clean:
            remove_directory(path=dist_dir, force=True)

        build = self._get_builder()

        for fmt in options.formats:
            self.io.write_line(f"Building <info>{fmt}</info>")
            build(
                fmt,
                executable=self.env.python,
                target_dir=dist_dir,
                config_settings=options.config_settings,
            )

        return 0


class BuildCommand(EnvCommand):
    name = "build"
    description = "Builds a package, as a tarball and a wheel by default."

    options: ClassVar[list[Option]] = [
        option("format", "f", "Limit the format to either sdist or wheel.", flag=False),
        option(
            "clean",
            description="Clean output directory before building.",
            flag=True,
        ),
        option(
            "local-version",
            "l",
            "Add or replace a local version label to the build. (<warning>Deprecated</warning>)",
            flag=False,
        ),
        option(
            "output",
            "o",
            "Set output directory for build artifacts. Default is `dist`.",
            default="dist",
            flag=False,
        ),
        option(
            "config-settings",
            "c",
            description="Provide config settings that should be passed to backend in <key>=<value> format.",
            flag=False,
            multiple=True,
        ),
    ]

    loggers: ClassVar[list[str]] = [
        "poetry.core.masonry.builders.builder",
        "poetry.core.masonry.builders.sdist",
        "poetry.core.masonry.builders.wheel",
    ]

    @staticmethod
    def _prepare_config_settings(
        local_version: str | None, config_settings: list[str] | None, io: IO
    ) -> dict[str, str]:
        config_settings = config_settings or []
        result = {}

        if local_version:
            io.write_error_line(
                f"<warning>`<fg=yellow;options=bold>--local-version</>` is deprecated."
                f" Use `<fg=yellow;options=bold>--config-settings local-version={local_version}</>`"
                f" instead.</warning>"
            )
            result["local-version"] = local_version

        for config_setting in config_settings:
            if "=" not in config_setting:
                raise ValueError(
                    f"Invalid config setting format: {config_setting}. "
                    "Config settings must be in the format 'key=value'"
                )

            key, _, value = config_setting.partition("=")
            result[key] = value

        return result

    @staticmethod
    def _prepare_formats(fmt: str | None) -> list[str]:
        fmt = fmt or "all"

        return ["sdist", "wheel"] if fmt == "all" else [fmt]

    def handle(self) -> int:
        build_handler = BuildHandler(
            poetry=self.poetry,
            env=self.env,
            io=self.io,
        )
        build_options = BuildOptions(
            clean=self.option("clean"),
            formats=self._prepare_formats(self.option("format")),  # type: ignore[arg-type]
            output=self.option("output"),
            config_settings=self._prepare_config_settings(
                local_version=self.option("local-version"),
                config_settings=self.option("config-settings"),
                io=self.io,
            ),
        )

        return build_handler.build(options=build_options)
