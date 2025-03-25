from __future__ import annotations

import json
import re

from typing import TYPE_CHECKING
from typing import Any
from typing import Sequence

from cleo.commands.command import Command
from cleo.descriptors.descriptor import Descriptor
from cleo.formatters.formatter import Formatter
from cleo.io.inputs.definition import Definition


if TYPE_CHECKING:
    from cleo.application import Application
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option


class TextDescriptor(Descriptor):
    def _describe_argument(self, argument: Argument, **options: Any) -> None:
        if argument.default is not None and (
            not isinstance(argument.default, list) or argument.default
        ):
            default = (
                f"<comment> [default: {self._format_default_value(argument.default)}]"
                "</comment>"
            )
        else:
            default = ""

        total_width = options.get("total_width", len(argument.name))

        spacing_width = total_width - len(argument.name)
        sub_argument_description = re.sub(
            r"\s*[\r\n]\s*",
            "\n" + " " * (total_width + 4),
            argument.description,
        )
        self._write(
            f"  <c1>{argument.name}</c1>  {' ' * spacing_width}"
            f"{sub_argument_description}{default}"
        )

    def _describe_option(self, option: Option, **options: Any) -> None:
        if (
            option.accepts_value()
            and option.default is not None
            and (not isinstance(option.default, list) or option.default)
        ):
            default = (
                "<comment> [default: "
                f"{self._format_default_value(option.default)}]</comment>"
            )
        else:
            default = ""

        value = ""
        if option.accepts_value():
            value = "=" + option.name.upper()

            if not option.requires_value():
                value = "[" + value + "]"

        total_width = options.get(
            "total_width", self._calculate_total_width_for_options([option])
        )

        option_shortcut = f"-{option.shortcut}, " if option.shortcut else "    "
        synopsis = f"{option_shortcut}--{option.name}{value}"

        spacing_width = total_width - len(synopsis)
        sub_option_description = re.sub(
            r"\s*[\r\n]\s*",
            "\n" + " " * (total_width + 4),
            option.description,
        )
        are_multiple_values_allowed = (
            "<comment> (multiple values allowed)</comment>" if option.is_list() else ""
        )
        self._write(
            f"  <c1>{synopsis}</c1>  "
            f"{' ' * spacing_width}{sub_option_description}"
            f"{default}"
            f"{are_multiple_values_allowed}"
        )

    def _describe_definition(self, definition: Definition, **options: Any) -> None:
        arguments = definition.arguments
        definition_options = definition.options
        total_width = self._calculate_total_width_for_options(definition_options)

        for argument in arguments:
            total_width = max(total_width, len(argument.name))

        if arguments:
            self._write("<b>Arguments:</b>")
            self._write("\n")

            for argument in arguments:
                self._describe_argument(argument, total_width=total_width)
                self._write("\n")

        if arguments and definition_options:
            self._write("\n")

        if definition_options:
            later_options = []

            self._write("<b>Options:</b>")

            for option in definition_options:
                if option.shortcut and len(option.shortcut) > 1:
                    later_options.append(option)
                    continue

                self._write("\n")
                self._describe_option(option, total_width=total_width)

            for option in later_options:
                self._write("\n")
                self._describe_option(option, total_width=total_width)

    def _describe_command(self, command: Command, **options: Any) -> None:
        command.merge_application_definition(False)

        description = command.description
        if description:
            self._write("<b>Description:</b>")
            self._write("\n")
            self._write("  " + description)
            self._write("\n\n")

        self._write("<b>Usage:</b>")
        for usage in [command.synopsis(True), *command.aliases, *command.usages]:
            self._write("\n")
            self._write("  " + Formatter.escape(usage))

        self._write("\n")

        definition = command.definition
        if definition.options or definition.arguments:
            self._write("\n")
            self._describe_definition(definition, **options)
            self._write("\n")

        help_text = command.processed_help
        if help_text and help_text != description:
            self._write("\n")
            self._write("<b>Help:</b>")
            self._write("\n")
            self._write("  " + help_text.replace("\n", "\n  "))
            self._write("\n")

    def _describe_application(self, application: Application, **options: Any) -> None:
        from cleo.descriptors.application_description import ApplicationDescription

        described_namespace = options.get("namespace")
        description = ApplicationDescription(application, namespace=described_namespace)

        help_text = application.help
        if help_text:
            self._write(f"{help_text}\n\n")

        self._write("<b>Usage:</b>\n")
        self._write("  command [options] [arguments]\n\n")

        self._describe_definition(Definition(application.definition.options), **options)

        self._write("\n\n")

        commands = description.commands
        namespaces = description.namespaces

        if described_namespace and namespaces:
            described_namespace_info = next(iter(namespaces.values()))
            for name in described_namespace_info["commands"]:
                commands[name] = description.command(name)

        # calculate max width based on available commands per namespace
        all_commands = list(commands)
        for namespace in namespaces.values():
            all_commands += namespace["commands"]

        width = self._get_column_width(all_commands)
        if described_namespace:
            self._write(
                f'<b>Available commands for the "{described_namespace}" namespace:</b>'
            )
        else:
            self._write("<b>Available commands:</b>")

        for namespace in namespaces.values():
            namespace["commands"] = [c for c in namespace["commands"] if c in commands]

            if not namespace["commands"]:
                continue

            if not (
                described_namespace
                or namespace["id"] == ApplicationDescription.GLOBAL_NAMESPACE
            ):
                self._write("\n")
                self._write(f" <comment>{namespace['id']}</comment>")

            for name in namespace["commands"]:
                self._write("\n")
                spacing_width = width - len(name)
                command = commands[name]
                command_aliases = (
                    self._get_command_aliases_text(command)
                    if command.name == name
                    else ""
                )
                self._write(
                    f"  <c1>{name}</c1>{' ' * spacing_width}"
                    f"{command_aliases + command.description}"
                )

            self._write("\n")

    def _format_default_value(self, default: Any) -> str:
        if isinstance(default, str):
            default = Formatter.escape(default)
        elif isinstance(default, list):
            default = [
                Formatter.escape(value) for value in default if isinstance(value, str)
            ]
        elif isinstance(default, dict):
            default = {
                key: Formatter.escape(value)
                for key, value in default.items()
                if isinstance(value, str)
            }

        return json.dumps(default).replace("\\\\", "\\")

    def _calculate_total_width_for_options(self, options: list[Option]) -> int:
        total_width = 0

        for option in options:
            name_length = 1 + max(len(option.shortcut or ""), 1) + 4 + len(option.name)

            if option.accepts_value():
                value_length = 1 + len(option.name)
                if not option.requires_value():
                    value_length += 2

                name_length += value_length

            total_width = max(total_width, name_length)

        return total_width

    def _get_column_width(self, commands: Sequence[Command | str]) -> int:
        widths: list[int] = []

        for command in commands:
            if isinstance(command, Command):
                assert command.name is not None
                widths.append(len(command.name))
                for alias in command.aliases:
                    widths.append(len(alias))
            else:
                widths.append(len(command))

        if not widths:
            return 0

        return max(widths) + 2

    def _get_command_aliases_text(self, command: Command) -> str:
        aliases = command.aliases

        if aliases:
            return f"[{ '|'.join(aliases) }] "

        return ""
