from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from cleo.io.null_io import NullIO
from packaging.utils import canonicalize_name

from poetry.installation.executor import Executor
from poetry.puzzle.transaction import Transaction
from poetry.repositories import Repository
from poetry.repositories import RepositoryPool
from poetry.repositories.installed_repository import InstalledRepository
from poetry.repositories.lockfile_repository import LockfileRepository


if TYPE_CHECKING:
    from collections.abc import Iterable

    from cleo.io.io import IO
    from packaging.utils import NormalizedName
    from poetry.core.packages.package import Package
    from poetry.core.packages.path_dependency import PathDependency
    from poetry.core.packages.project_package import ProjectPackage

    from poetry.config.config import Config
    from poetry.installation.operations.operation import Operation
    from poetry.packages import Locker
    from poetry.packages.transitive_package_info import TransitivePackageInfo
    from poetry.utils.env import Env


class Installer:
    def __init__(
        self,
        io: IO,
        env: Env,
        package: ProjectPackage,
        locker: Locker,
        pool: RepositoryPool,
        config: Config,
        installed: InstalledRepository | None = None,
        executor: Executor | None = None,
        disable_cache: bool = False,
    ) -> None:
        self._io = io
        self._env = env
        self._package = package
        self._locker = locker
        self._pool = pool
        self._config = config

        self._dry_run = False
        self._requires_synchronization = False
        self._update = False
        self._verbose = False
        self._groups: Iterable[str] | None = None
        self._skip_directory = False
        self._lock = False

        self._whitelist: list[NormalizedName] = []

        self._extras: list[NormalizedName] = []

        if executor is None:
            executor = Executor(
                self._env, self._pool, config, self._io, disable_cache=disable_cache
            )

        self._executor = executor

        if installed is None:
            installed = self._get_installed()

        self._installed_repository = installed

    @property
    def executor(self) -> Executor:
        return self._executor

    def set_package(self, package: ProjectPackage) -> Installer:
        self._package = package

        return self

    def set_locker(self, locker: Locker) -> Installer:
        self._locker = locker

        return self

    def run(self) -> int:
        # Check if refresh
        if not self._update and self._lock and self._locker.is_locked():
            return self._do_refresh()

        # Force update if there is no lock file present
        if not self._update and not self._locker.is_locked():
            self._update = True

        if self.is_dry_run():
            self.verbose(True)

        return self._do_install()

    def dry_run(self, dry_run: bool = True) -> Installer:
        self._dry_run = dry_run
        self._executor.dry_run(dry_run)

        return self

    def is_dry_run(self) -> bool:
        return self._dry_run

    def requires_synchronization(
        self, requires_synchronization: bool = True
    ) -> Installer:
        self._requires_synchronization = requires_synchronization

        return self

    def verbose(self, verbose: bool = True) -> Installer:
        self._verbose = verbose
        self._executor.verbose(verbose)

        return self

    def is_verbose(self) -> bool:
        return self._verbose

    def only_groups(self, groups: Iterable[str]) -> Installer:
        self._groups = groups

        return self

    def update(self, update: bool = True) -> Installer:
        self._update = update

        return self

    def skip_directory(self, skip_directory: bool = False) -> Installer:
        self._skip_directory = skip_directory

        return self

    def lock(self, update: bool = True) -> Installer:
        """
        Prepare the installer for locking only.
        """
        self.update(update=update)
        self.execute_operations(False)
        self._lock = True

        return self

    def is_updating(self) -> bool:
        return self._update

    def execute_operations(self, execute: bool = True) -> Installer:
        if not execute:
            self._executor.disable()

        return self

    def whitelist(self, packages: Iterable[str]) -> Installer:
        self._whitelist = [canonicalize_name(p) for p in packages]

        return self

    def extras(self, extras: list[str]) -> Installer:
        self._extras = [canonicalize_name(extra) for extra in extras]

        return self

    def _do_refresh(self) -> int:
        from poetry.puzzle.solver import Solver

        # Checking extras
        for extra in self._extras:
            if extra not in self._package.extras:
                raise ValueError(f"Extra [{extra}] is not specified.")

        locked_repository = self._locker.locked_repository()
        solver = Solver(
            self._package,
            self._pool,
            locked_repository.packages,
            locked_repository.packages,
            self._io,
        )

        # Always re-solve directory dependencies, otherwise we can't determine
        # if anything has changed (and the lock file contains an invalid version).
        use_latest = [
            p.name for p in locked_repository.packages if p.source_type == "directory"
        ]

        with solver.provider.use_source_root(
            source_root=self._env.path.joinpath("src")
        ):
            solved_packages = solver.solve(use_latest=use_latest).get_solved_packages()

        self._write_lock_file(solved_packages, force=True)

        return 0

    def _do_install(self) -> int:
        from poetry.puzzle.solver import Solver

        locked_repository = Repository("poetry-locked")
        reresolve = self._config.get("installer.re-resolve", True)
        solved_packages: dict[Package, TransitivePackageInfo] = {}
        lockfile_repo = LockfileRepository()

        if self._update:
            if not self._lock and self._locker.is_locked():
                locked_repository = self._locker.locked_repository()

                # If no packages have been whitelisted (The ones we want to update),
                # we whitelist every package in the lock file.
                if not self._whitelist:
                    for pkg in locked_repository.packages:
                        self._whitelist.append(pkg.name)

            # Checking extras
            for extra in self._extras:
                if extra not in self._package.extras:
                    raise ValueError(f"Extra [{extra}] is not specified.")

            self._io.write_line("<info>Updating dependencies</>")
            solver = Solver(
                self._package,
                self._pool,
                self._installed_repository.packages,
                locked_repository.packages,
                self._io,
            )

            with solver.provider.use_source_root(
                source_root=self._env.path.joinpath("src")
            ):
                solved_packages = solver.solve(
                    use_latest=self._whitelist
                ).get_solved_packages()

            if not self.executor.enabled:
                # If we are only in lock mode, no need to go any further
                self._write_lock_file(solved_packages)
                return 0

            for package in solved_packages:
                if not lockfile_repo.has_package(package):
                    lockfile_repo.add_package(package)

        else:
            self._io.write_line("<info>Installing dependencies from lock file</>")

            if not self._locker.is_fresh():
                raise ValueError(
                    "pyproject.toml changed significantly since poetry.lock was last"
                    " generated. Run `poetry lock` to fix the lock file."
                )
            if not (reresolve or self._locker.is_locked_groups_and_markers()):
                if self._io.is_verbose():
                    self._io.write_line(
                        "<info>Cannot install without re-resolving"
                        " because the lock file is not at least version 2.1</>"
                    )
                reresolve = True

            locker_extras = {
                canonicalize_name(extra)
                for extra in self._locker.lock_data.get("extras", {})
            }
            for extra in self._extras:
                if extra not in locker_extras:
                    raise ValueError(f"Extra [{extra}] is not specified.")

            locked_repository = self._locker.locked_repository()
            if reresolve:
                lockfile_repo = locked_repository
            else:
                solved_packages = self._locker.locked_packages()

        if self._io.is_verbose():
            self._io.write_line("")
            self._io.write_line(
                "<info>Finding the necessary packages for the current system</>"
            )

        if reresolve:
            if self._groups is not None:
                root = self._package.with_dependency_groups(
                    list(self._groups), only=True
                )
            else:
                root = self._package.without_optional_dependency_groups()

            # We resolve again by only using the lock file
            packages = lockfile_repo.packages + locked_repository.packages
            pool = RepositoryPool.from_packages(packages, self._config)

            solver = Solver(
                root,
                pool,
                self._installed_repository.packages,
                locked_repository.packages,
                NullIO(),
                active_root_extras=self._extras,
            )
            # Everything is resolved at this point, so we no longer need
            # to load deferred dependencies (i.e. VCS, URL and path dependencies)
            solver.provider.load_deferred(False)

            with solver.use_environment(self._env):
                transaction = solver.solve(use_latest=self._whitelist)

        else:
            if self._groups is None:
                groups = self._package.dependency_group_names()
            else:
                groups = set(self._groups)
            transaction = Transaction(
                locked_repository.packages,
                solved_packages,
                self._installed_repository.packages,
                self._package,
                self._env.marker_env,
                groups,
            )

        ops = transaction.calculate_operations(
            with_uninstalls=(
                self._requires_synchronization or (self._update and not reresolve)
            ),
            synchronize=self._requires_synchronization,
            skip_directory=self._skip_directory,
            extras=set(self._extras),
            system_site_packages={
                p.name for p in self._installed_repository.system_site_packages
            },
        )
        if reresolve and not self._requires_synchronization:
            # If no packages synchronisation has been requested we need
            # to calculate the uninstall operations
            transaction = Transaction(
                locked_repository.packages,
                lockfile_repo.packages,
                installed_packages=self._installed_repository.packages,
                root_package=root,
            )

            ops = [
                op
                for op in transaction.calculate_operations(with_uninstalls=True)
                if op.job_type == "uninstall"
            ] + ops

        # Validate the dependencies
        for op in ops:
            dep = op.package.to_dependency()
            if dep.is_file() or dep.is_directory():
                dep = cast("PathDependency", dep)
                dep.validate(raise_error=not op.skipped)

        # Execute operations
        status = self._execute(ops)

        if status == 0 and self._update:
            # Only write lock file when installation is success
            self._write_lock_file(solved_packages)

        return status

    def _write_lock_file(
        self,
        packages: dict[Package, TransitivePackageInfo],
        force: bool = False,
    ) -> None:
        if not self.is_dry_run() and (force or self._update):
            updated_lock = self._locker.set_lock_data(self._package, packages)

            if updated_lock:
                self._io.write_line("")
                self._io.write_line("<info>Writing lock file</>")

    def _execute(self, operations: list[Operation]) -> int:
        return self._executor.execute(operations)

    def _get_installed(self) -> InstalledRepository:
        return InstalledRepository.load(self._env)
