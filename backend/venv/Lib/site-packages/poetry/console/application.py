from __future__ import annotations

import argparse
import logging

from contextlib import suppress
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING
from typing import cast

from cleo._utils import find_similar_names
from cleo.application import Application as BaseApplication
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_events import COMMAND
from cleo.events.event_dispatcher import EventDispatcher
from cleo.exceptions import CleoCommandNotFoundError
from cleo.exceptions import CleoError
from cleo.formatters.style import Style
from cleo.io.inputs.argv_input import ArgvInput

from poetry.__version__ import __version__
from poetry.console.command_loader import CommandLoader
from poetry.console.commands.command import Command
from poetry.console.exceptions import PoetryRuntimeError
from poetry.utils.helpers import directory
from poetry.utils.helpers import ensure_path


if TYPE_CHECKING:
    from collections.abc import Callable

    from cleo.events.event import Event
    from cleo.io.inputs.definition import Definition
    from cleo.io.inputs.input import Input
    from cleo.io.io import IO
    from cleo.io.outputs.output import Output

    from poetry.console.commands.installer_command import InstallerCommand
    from poetry.poetry import Poetry


def load_command(name: str) -> Callable[[], Command]:
    def _load() -> Command:
        words = name.split(" ")
        module = import_module("poetry.console.commands." + ".".join(words))
        command_class = getattr(module, "".join(c.title() for c in words) + "Command")
        command: Command = command_class()
        return command

    return _load


COMMANDS = [
    "about",
    "add",
    "build",
    "check",
    "config",
    "init",
    "install",
    "lock",
    "new",
    "publish",
    "remove",
    "run",
    "search",
    "show",
    "sync",
    "update",
    "version",
    # Cache commands
    "cache clear",
    "cache list",
    # Debug commands
    "debug info",
    "debug resolve",
    "debug tags",
    # Env commands
    "env activate",
    "env info",
    "env list",
    "env remove",
    "env use",
    # Python commands,
    "python install",
    "python list",
    "python remove",
    # Self commands
    "self add",
    "self install",
    "self lock",
    "self remove",
    "self update",
    "self show",
    "self show plugins",
    "self sync",
    # Source commands
    "source add",
    "source remove",
    "source show",
]

# these are special messages to override the default message when a command is not found
# in cases where a previously existing command has been moved to a plugin or outright
# removed for various reasons
COMMAND_NOT_FOUND_PREFIX_MESSAGE = (
    "Looks like you're trying to use a Poetry command that is not available."
)
COMMAND_NOT_FOUND_MESSAGES = {
    "shell": """
Since <info>Poetry (<b>2.0.0</>)</>, the <c1>shell</> command is not installed by default. You can use,

  - the new <c1>env activate</> command (<b>recommended</>); or
  - the <c1>shell plugin</> to install the <c1>shell</> command

<b>Documentation:</> https://python-poetry.org/docs/managing-environments/#activating-the-environment

<warning>Note that the <c1>env activate</> command is not a direct replacement for <c1>shell</> command.
"""
}


class Application(BaseApplication):
    def __init__(self) -> None:
        super().__init__("poetry", __version__)

        self._poetry: Poetry | None = None
        self._io: IO | None = None
        self._disable_plugins = False
        self._disable_cache = False
        self._plugins_loaded = False
        self._working_directory = Path.cwd()
        self._project_directory: Path | None = None

        dispatcher = EventDispatcher()
        dispatcher.add_listener(COMMAND, self.register_command_loggers)
        dispatcher.add_listener(COMMAND, self.configure_env)
        dispatcher.add_listener(COMMAND, self.configure_installer_for_event)
        self.set_event_dispatcher(dispatcher)

        command_loader = CommandLoader({name: load_command(name) for name in COMMANDS})
        self.set_command_loader(command_loader)

    @property
    def _default_definition(self) -> Definition:
        from cleo.io.inputs.option import Option

        definition = super()._default_definition

        definition.add_option(
            Option("--no-plugins", flag=True, description="Disables plugins.")
        )

        definition.add_option(
            Option(
                "--no-cache", flag=True, description="Disables Poetry source caches."
            )
        )

        definition.add_option(
            Option(
                "--project",
                "-P",
                flag=False,
                description=(
                    "Specify another path as the project root."
                    " All command-line arguments will be resolved relative to the current working directory."
                ),
            )
        )

        definition.add_option(
            Option(
                "--directory",
                "-C",
                flag=False,
                description=(
                    "The working directory for the Poetry command (defaults to the"
                    " current working directory). All command-line arguments will be"
                    " resolved relative to the given directory."
                ),
            )
        )

        return definition

    @property
    def project_directory(self) -> Path:
        return self._project_directory or self._working_directory

    @property
    def poetry(self) -> Poetry:
        from poetry.factory import Factory

        if self._poetry is not None:
            return self._poetry

        self._poetry = Factory().create_poetry(
            cwd=self.project_directory,
            io=self._io,
            disable_plugins=self._disable_plugins,
            disable_cache=self._disable_cache,
        )

        return self._poetry

    @property
    def command_loader(self) -> CommandLoader:
        command_loader = self._command_loader
        assert isinstance(command_loader, CommandLoader)
        return command_loader

    def reset_poetry(self) -> None:
        self._poetry = None

    def create_io(
        self,
        input: Input | None = None,
        output: Output | None = None,
        error_output: Output | None = None,
    ) -> IO:
        io = super().create_io(input, output, error_output)

        # Set our own CLI styles
        formatter = io.output.formatter
        formatter.set_style("c1", Style("cyan"))
        formatter.set_style("c2", Style("default", options=["bold"]))
        formatter.set_style("info", Style("blue"))
        formatter.set_style("comment", Style("green"))
        formatter.set_style("warning", Style("yellow"))
        formatter.set_style("debug", Style("default", options=["dark"]))
        formatter.set_style("success", Style("green"))

        # Dark variants
        formatter.set_style("c1_dark", Style("cyan", options=["dark"]))
        formatter.set_style("c2_dark", Style("default", options=["bold", "dark"]))
        formatter.set_style("success_dark", Style("green", options=["dark"]))

        io.output.set_formatter(formatter)
        io.error_output.set_formatter(formatter)

        self._io = io

        return io

    def _run(self, io: IO) -> int:
        # we do this here and not inside the _configure_io implementation in order
        # to ensure the users are not exposed to a stack trace for providing invalid values to
        # the options --directory or --project, configuring the options here allow cleo to trap and
        # display the error cleanly unless the user uses verbose or debug
        self._configure_global_options(io)

        self._load_plugins(io)

        exit_code: int = 1

        with directory(self._working_directory):
            try:
                exit_code = super()._run(io)
            except PoetryRuntimeError as e:
                io.write_error_line("")
                e.write(io)
                io.write_error_line("")
            except CleoCommandNotFoundError as e:
                command = self._get_command_name(io)

                if command is not None and (
                    message := COMMAND_NOT_FOUND_MESSAGES.get(command)
                ):
                    io.write_error_line("")
                    io.write_error_line(COMMAND_NOT_FOUND_PREFIX_MESSAGE)
                    io.write_error_line(message)
                    return 1

                if command is not None and command in self.get_namespaces():
                    sub_commands = []

                    for key in self._commands:
                        if key.startswith(f"{command} "):
                            sub_commands.append(key)

                    io.write_error_line(
                        f"The requested command does not exist in the <c1>{command}</> namespace."
                    )
                    suggested_names = find_similar_names(command, sub_commands)
                    self._error_write_command_suggestions(
                        io, suggested_names, f"#{command}"
                    )
                    return 1

                if command is not None:
                    suggested_names = find_similar_names(
                        command, list(self._commands.keys())
                    )
                    io.write_error_line(
                        f"The requested command <c1>{command}</> does not exist."
                    )
                    self._error_write_command_suggestions(io, suggested_names)
                    return 1

                raise e

        return exit_code

    def _error_write_command_suggestions(
        self, io: IO, suggested_names: list[str], doc_tag: str | None = None
    ) -> None:
        if suggested_names:
            suggestion_lines = [
                f"<c1>{name.replace(' ', '</> <b>', 1)}</>: {self._commands[name].description}"
                for name in suggested_names
            ]
            suggestions = "\n    ".join(["", *sorted(suggestion_lines)])
            io.write_error_line(
                f"\n<error>Did you mean one of these perhaps?</>{suggestions}"
            )

        io.write_error_line(
            "\n<b>Documentation: </>"
            f"<info>https://python-poetry.org/docs/cli/{doc_tag or ''}</>"
        )

    def _configure_global_options(self, io: IO) -> None:
        """
        Configures global options for the application by setting up the relevant
        directories, disabling plugins or cache, and managing the working and
        project directories. This method ensures that all directories are valid
        paths and handles the resolution of the project directory relative to the
        working directory if necessary.

        :param io: The IO instance whose input and options are being read.
        :return: Nothing.
        """
        self._disable_plugins = io.input.option("no-plugins")
        self._disable_cache = io.input.option("no-cache")

        # we use ensure_path for the directories to make sure these are valid paths
        # this will raise an exception if the path is invalid
        self._working_directory = ensure_path(
            io.input.option("directory") or Path.cwd(), is_directory=True
        )

        self._project_directory = io.input.option("project")
        if self._project_directory is not None:
            self._project_directory = Path(self._project_directory)
            self._project_directory = ensure_path(
                self._project_directory
                if self._project_directory.is_absolute()
                else self._working_directory.joinpath(self._project_directory).resolve(
                    strict=False
                ),
                is_directory=True,
            )

    def _sort_global_options(self, io: IO) -> None:
        """
        Sorts global options of the provided IO instance according to the
        definition of the available options, reordering and parsing arguments
        to ensure consistency in input handling.

        The function interprets the options and their corresponding values
        using an argument parser, constructs a sorted list of tokens, and
        recreates the input with the rearranged sequence while maintaining
        compatibility with the initially provided input stream.

        If using in conjunction with `_configure_run_command`, it is recommended that
        it be called first in order to correctly handling cases like
        `poetry run -V python -V`.

        :param io: The IO instance whose input and options are being processed
                   and reordered.
        :return: Nothing.
        """
        original_input = cast(ArgvInput, io.input)
        tokens: list[str] = original_input._tokens

        parser = argparse.ArgumentParser(add_help=False)

        for option in self.definition.options:
            parser.add_argument(
                f"--{option.name}",
                *([f"-{option.shortcut}"] if option.shortcut else []),
                action="store_true" if option.is_flag() else "store",
            )

        args, remaining_args = parser.parse_known_args(tokens)

        tokens = []
        for option in self.definition.options:
            key = option.name.replace("-", "_")
            value = getattr(args, key, None)

            if value is not None:
                if value:  # is truthy
                    tokens.append(f"--{option.name}")

                if option.accepts_value():
                    tokens.append(str(value))

        sorted_input = ArgvInput([self._name or "", *tokens, *remaining_args])

        # this is required to ensure stdin is transferred
        sorted_input.set_stream(original_input.stream)

        # this is required as cleo internally checks for `io.input._interactive`
        # when configuring io, and cleo's test applications overrides this attribute
        # explicitly causing test setups to fail
        sorted_input.interactive(io.input.is_interactive())

        with suppress(CleoError):
            sorted_input.bind(self.definition)

        io.set_input(sorted_input)

    def _configure_run_command(self, io: IO) -> None:
        """
        Configures the input for the "run" command to properly handle cases where the user
        executes commands such as "poetry run -- <subcommand>". This involves reorganizing
        input tokens to ensure correct parsing and execution of the run command.
        """
        with suppress(CleoError):
            io.input.bind(self.definition)

        command_name = io.input.first_argument

        if command_name == "run":
            original_input = cast(ArgvInput, io.input)
            tokens: list[str] = original_input._tokens

            if "--" in tokens:
                # this means the user has done the right thing and used "poetry run -- echo hello"
                # in this case there is not much we need to do, we can skip the rest
                return

            # find the correct command index, in some cases this might not be first occurrence
            # eg: poetry -C run run echo
            command_index = tokens.index(command_name)

            while command_index < (len(tokens) - 1):
                try:
                    # try parsing the tokens so far
                    _ = ArgvInput(
                        [self._name or "", *tokens[: command_index + 1]],
                        definition=self.definition,
                    )
                    break
                except CleoError:
                    # parsing failed, try finding the next "run" token
                    try:
                        command_index += (
                            tokens[command_index + 1 :].index(command_name) + 1
                        )
                    except ValueError:
                        command_index = len(tokens)
            else:
                # looks like we reached the end of the road, let cleo deal with it
                return

            # fetch tokens after the "run" command
            tokens_without_command = tokens[command_index + 1 :]

            # we create a new input for parsing the subcommand pretending
            # it is poetry command
            without_command = ArgvInput(
                [self._name or "", *tokens_without_command], None
            )

            with suppress(CleoError):
                # we want to bind the definition here so that cleo knows what should be
                # parsed, and how
                without_command.bind(self.definition)

            # the first argument here is the subcommand
            subcommand = without_command.first_argument
            subcommand_index = (
                (tokens_without_command.index(subcommand) if subcommand else 0)
                + command_index
                + 1
            )

            # recreate the original input reordering in the following order
            #   - all tokens before "run" command
            #   - all tokens after "run" command but before the subcommand
            #   - the "run" command token
            #   - the "--" token to normalise the form
            #   - all remaining tokens starting with the subcommand
            run_input = ArgvInput(
                [
                    self._name or "",
                    *tokens[:command_index],
                    *tokens[command_index + 1 : subcommand_index],
                    command_name,
                    "--",
                    *tokens[subcommand_index:],
                ]
            )
            run_input.set_stream(original_input.stream)

            with suppress(CleoError):
                run_input.bind(self.definition)

            # reset the input to our constructed form
            io.set_input(run_input)

    def _configure_io(self, io: IO) -> None:
        self._configure_run_command(io)
        self._sort_global_options(io)
        super()._configure_io(io)

    def register_command_loggers(
        self, event: Event, event_name: str, _: EventDispatcher
    ) -> None:
        from poetry.console.logging.filters import POETRY_FILTER
        from poetry.console.logging.io_formatter import IOFormatter
        from poetry.console.logging.io_handler import IOHandler

        assert isinstance(event, ConsoleCommandEvent)
        command = event.command
        if not isinstance(command, Command):
            return

        io = event.io

        loggers = [
            "poetry.packages.locker",
            "poetry.packages.package",
            "poetry.utils.password_manager",
        ]

        loggers += command.loggers

        handler = IOHandler(io)
        handler.setFormatter(IOFormatter())

        level = logging.WARNING

        if io.is_debug():
            level = logging.DEBUG
        elif io.is_very_verbose() or io.is_verbose():
            level = logging.INFO

        logging.basicConfig(level=level, handlers=[handler])

        # only log third-party packages when very verbose
        if not io.is_very_verbose():
            handler.addFilter(POETRY_FILTER)

        for name in loggers:
            logger = logging.getLogger(name)

            _level = level
            # The builders loggers are special and we can actually
            # start at the INFO level.
            if (
                logger.name.startswith("poetry.core.masonry.builders")
                and _level > logging.INFO
            ):
                _level = logging.INFO

            logger.setLevel(_level)

    def configure_env(self, event: Event, event_name: str, _: EventDispatcher) -> None:
        from poetry.console.commands.env_command import EnvCommand
        from poetry.console.commands.self.self_command import SelfCommand

        assert isinstance(event, ConsoleCommandEvent)
        command = event.command
        if not isinstance(command, EnvCommand) or isinstance(command, SelfCommand):
            return

        if command._env is not None:
            return

        from poetry.utils.env import EnvManager

        io = event.io
        poetry = command.poetry

        env_manager = EnvManager(poetry, io=io)
        env = env_manager.create_venv()

        if env.is_venv() and io.is_verbose():
            io.write_line(f"Using virtualenv: <comment>{env.path}</>")

        command.set_env(env)

    @classmethod
    def configure_installer_for_event(
        cls, event: Event, event_name: str, _: EventDispatcher
    ) -> None:
        from poetry.console.commands.installer_command import InstallerCommand

        assert isinstance(event, ConsoleCommandEvent)
        command = event.command
        if not isinstance(command, InstallerCommand):
            return

        # If the command already has an installer
        # we skip this step
        if command._installer is not None:
            return

        cls.configure_installer_for_command(command, event.io)

    @staticmethod
    def configure_installer_for_command(command: InstallerCommand, io: IO) -> None:
        from poetry.installation.installer import Installer

        poetry = command.poetry
        installer = Installer(
            io,
            command.env,
            poetry.package,
            poetry.locker,
            poetry.pool,
            poetry.config,
            disable_cache=poetry.disable_cache,
        )
        command.set_installer(installer)

    def _load_plugins(self, io: IO) -> None:
        if self._plugins_loaded:
            return

        self._disable_plugins = io.input.has_parameter_option("--no-plugins")

        if not self._disable_plugins:
            from poetry.plugins.application_plugin import ApplicationPlugin
            from poetry.plugins.plugin_manager import PluginManager

            PluginManager.add_project_plugin_path(self.project_directory)
            manager = PluginManager(ApplicationPlugin.group)
            manager.load_plugins()
            manager.activate(self)

        self._plugins_loaded = True


def main() -> int:
    exit_code: int = Application().run()
    return exit_code


if __name__ == "__main__":
    main()
