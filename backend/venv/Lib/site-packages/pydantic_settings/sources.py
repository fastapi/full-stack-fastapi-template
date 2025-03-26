from __future__ import annotations as _annotations

import json
import os
import re
import shlex
import sys
import typing
import warnings
from abc import ABC, abstractmethod

if sys.version_info >= (3, 9):
    from argparse import BooleanOptionalAction
from argparse import SUPPRESS, ArgumentParser, Namespace, RawDescriptionHelpFormatter, _SubParsersAction
from collections import defaultdict, deque
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from textwrap import dedent
from types import BuiltinFunctionType, FunctionType, SimpleNamespace
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    Mapping,
    NoReturn,
    Optional,
    Sequence,
    TypeVar,
    Union,
    cast,
    overload,
)

import typing_extensions
from dotenv import dotenv_values
from pydantic import AliasChoices, AliasPath, BaseModel, Json, RootModel, Secret, TypeAdapter
from pydantic._internal._repr import Representation
from pydantic._internal._typing_extra import WithArgsTypes, origin_is_union, typing_base
from pydantic._internal._utils import deep_update, is_model_class, lenient_issubclass
from pydantic.dataclasses import is_pydantic_dataclass
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from typing_extensions import Annotated, _AnnotatedAlias, get_args, get_origin

from pydantic_settings.utils import path_type_label

if TYPE_CHECKING:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        tomllib = None
    import tomli
    import yaml
    from pydantic._internal._dataclasses import PydanticDataclass

    from pydantic_settings.main import BaseSettings

    PydanticModel = TypeVar('PydanticModel', bound=PydanticDataclass | BaseModel)
else:
    yaml = None
    tomllib = None
    tomli = None
    PydanticModel = Any


def import_yaml() -> None:
    global yaml
    if yaml is not None:
        return
    try:
        import yaml
    except ImportError as e:
        raise ImportError('PyYAML is not installed, run `pip install pydantic-settings[yaml]`') from e


def import_toml() -> None:
    global tomli
    global tomllib
    if sys.version_info < (3, 11):
        if tomli is not None:
            return
        try:
            import tomli
        except ImportError as e:
            raise ImportError('tomli is not installed, run `pip install pydantic-settings[toml]`') from e
    else:
        if tomllib is not None:
            return
        import tomllib


def import_azure_key_vault() -> None:
    global TokenCredential
    global SecretClient
    global ResourceNotFoundError

    try:
        from azure.core.credentials import TokenCredential
        from azure.core.exceptions import ResourceNotFoundError
        from azure.keyvault.secrets import SecretClient
    except ImportError as e:
        raise ImportError(
            'Azure Key Vault dependencies are not installed, run `pip install pydantic-settings[azure-key-vault]`'
        ) from e


DotenvType = Union[Path, str, Sequence[Union[Path, str]]]
PathType = Union[Path, str, Sequence[Union[Path, str]]]
DEFAULT_PATH: PathType = Path('')

# This is used as default value for `_env_file` in the `BaseSettings` class and
# `env_file` in `DotEnvSettingsSource` so the default can be distinguished from `None`.
# See the docstring of `BaseSettings` for more details.
ENV_FILE_SENTINEL: DotenvType = Path('')


class NoDecode:
    """Annotation to prevent decoding of a field value."""

    pass


class ForceDecode:
    """Annotation to force decoding of a field value."""

    pass


class SettingsError(ValueError):
    pass


class _CliSubCommand:
    pass


class _CliPositionalArg:
    pass


class _CliImplicitFlag:
    pass


class _CliExplicitFlag:
    pass


class _CliInternalArgParser(ArgumentParser):
    def __init__(self, cli_exit_on_error: bool = True, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._cli_exit_on_error = cli_exit_on_error

    def error(self, message: str) -> NoReturn:
        if not self._cli_exit_on_error:
            raise SettingsError(f'error parsing CLI: {message}')
        super().error(message)


class CliMutuallyExclusiveGroup(BaseModel):
    pass


T = TypeVar('T')
CliSubCommand = Annotated[Union[T, None], _CliSubCommand]
CliPositionalArg = Annotated[T, _CliPositionalArg]
_CliBoolFlag = TypeVar('_CliBoolFlag', bound=bool)
CliImplicitFlag = Annotated[_CliBoolFlag, _CliImplicitFlag]
CliExplicitFlag = Annotated[_CliBoolFlag, _CliExplicitFlag]
CLI_SUPPRESS = SUPPRESS
CliSuppress = Annotated[T, CLI_SUPPRESS]


def get_subcommand(
    model: PydanticModel, is_required: bool = True, cli_exit_on_error: bool | None = None
) -> Optional[PydanticModel]:
    """
    Get the subcommand from a model.

    Args:
        model: The model to get the subcommand from.
        is_required: Determines whether a model must have subcommand set and raises error if not
            found. Defaults to `True`.
        cli_exit_on_error: Determines whether this function exits with error if no subcommand is found.
            Defaults to model_config `cli_exit_on_error` value if set. Otherwise, defaults to `True`.

    Returns:
        The subcommand model if found, otherwise `None`.

    Raises:
        SystemExit: When no subcommand is found and is_required=`True` and cli_exit_on_error=`True`
            (the default).
        SettingsError: When no subcommand is found and is_required=`True` and
            cli_exit_on_error=`False`.
    """

    model_cls = type(model)
    if cli_exit_on_error is None and is_model_class(model_cls):
        model_default = model_cls.model_config.get('cli_exit_on_error')
        if isinstance(model_default, bool):
            cli_exit_on_error = model_default
    if cli_exit_on_error is None:
        cli_exit_on_error = True

    subcommands: list[str] = []
    for field_name, field_info in _get_model_fields(model_cls).items():
        if _CliSubCommand in field_info.metadata:
            if getattr(model, field_name) is not None:
                return getattr(model, field_name)
            subcommands.append(field_name)

    if is_required:
        error_message = (
            f'Error: CLI subcommand is required {{{", ".join(subcommands)}}}'
            if subcommands
            else 'Error: CLI subcommand is required but no subcommands were found.'
        )
        raise SystemExit(error_message) if cli_exit_on_error else SettingsError(error_message)

    return None


class EnvNoneType(str):
    pass


class PydanticBaseSettingsSource(ABC):
    """
    Abstract base class for settings sources, every settings source classes should inherit from it.
    """

    def __init__(self, settings_cls: type[BaseSettings]):
        self.settings_cls = settings_cls
        self.config = settings_cls.model_config
        self._current_state: dict[str, Any] = {}
        self._settings_sources_data: dict[str, dict[str, Any]] = {}

    def _set_current_state(self, state: dict[str, Any]) -> None:
        """
        Record the state of settings from the previous settings sources. This should
        be called right before __call__.
        """
        self._current_state = state

    def _set_settings_sources_data(self, states: dict[str, dict[str, Any]]) -> None:
        """
        Record the state of settings from all previous settings sources. This should
        be called right before __call__.
        """
        self._settings_sources_data = states

    @property
    def current_state(self) -> dict[str, Any]:
        """
        The current state of the settings, populated by the previous settings sources.
        """
        return self._current_state

    @property
    def settings_sources_data(self) -> dict[str, dict[str, Any]]:
        """
        The state of all previous settings sources.
        """
        return self._settings_sources_data

    @abstractmethod
    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        """
        Gets the value, the key for model creation, and a flag to determine whether value is complex.

        This is an abstract method that should be overridden in every settings source classes.

        Args:
            field: The field.
            field_name: The field name.

        Returns:
            A tuple that contains the value, key and a flag to determine whether value is complex.
        """
        pass

    def field_is_complex(self, field: FieldInfo) -> bool:
        """
        Checks whether a field is complex, in which case it will attempt to be parsed as JSON.

        Args:
            field: The field.

        Returns:
            Whether the field is complex.
        """
        return _annotation_is_complex(field.annotation, field.metadata)

    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        """
        Prepares the value of a field.

        Args:
            field_name: The field name.
            field: The field.
            value: The value of the field that has to be prepared.
            value_is_complex: A flag to determine whether value is complex.

        Returns:
            The prepared value.
        """
        if value is not None and (self.field_is_complex(field) or value_is_complex):
            return self.decode_complex_value(field_name, field, value)
        return value

    def decode_complex_value(self, field_name: str, field: FieldInfo, value: Any) -> Any:
        """
        Decode the value for a complex field

        Args:
            field_name: The field name.
            field: The field.
            value: The value of the field that has to be prepared.

        Returns:
            The decoded value for further preparation
        """
        if field and (
            NoDecode in field.metadata
            or (self.config.get('enable_decoding') is False and ForceDecode not in field.metadata)
        ):
            return value

        return json.loads(value)

    @abstractmethod
    def __call__(self) -> dict[str, Any]:
        pass


class DefaultSettingsSource(PydanticBaseSettingsSource):
    """
    Source class for loading default object values.

    Args:
        settings_cls: The Settings class.
        nested_model_default_partial_update: Whether to allow partial updates on nested model default object fields.
            Defaults to `False`.
    """

    def __init__(self, settings_cls: type[BaseSettings], nested_model_default_partial_update: bool | None = None):
        super().__init__(settings_cls)
        self.defaults: dict[str, Any] = {}
        self.nested_model_default_partial_update = (
            nested_model_default_partial_update
            if nested_model_default_partial_update is not None
            else self.config.get('nested_model_default_partial_update', False)
        )
        if self.nested_model_default_partial_update:
            for field_name, field_info in settings_cls.model_fields.items():
                alias_names, *_ = _get_alias_names(field_name, field_info)
                preferred_alias = alias_names[0]
                if is_dataclass(type(field_info.default)):
                    self.defaults[preferred_alias] = asdict(field_info.default)
                elif is_model_class(type(field_info.default)):
                    self.defaults[preferred_alias] = field_info.default.model_dump()

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        # Nothing to do here. Only implement the return statement to make mypy happy
        return None, '', False

    def __call__(self) -> dict[str, Any]:
        return self.defaults

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(nested_model_default_partial_update={self.nested_model_default_partial_update})'
        )


class InitSettingsSource(PydanticBaseSettingsSource):
    """
    Source class for loading values provided during settings class initialization.
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        init_kwargs: dict[str, Any],
        nested_model_default_partial_update: bool | None = None,
    ):
        self.init_kwargs = {}
        init_kwarg_names = set(init_kwargs.keys())
        for field_name, field_info in settings_cls.model_fields.items():
            alias_names, *_ = _get_alias_names(field_name, field_info)
            init_kwarg_name = init_kwarg_names & set(alias_names)
            if init_kwarg_name:
                preferred_alias = alias_names[0]
                init_kwarg_names -= init_kwarg_name
                self.init_kwargs[preferred_alias] = init_kwargs[init_kwarg_name.pop()]
        self.init_kwargs.update({key: val for key, val in init_kwargs.items() if key in init_kwarg_names})

        super().__init__(settings_cls)
        self.nested_model_default_partial_update = (
            nested_model_default_partial_update
            if nested_model_default_partial_update is not None
            else self.config.get('nested_model_default_partial_update', False)
        )

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        # Nothing to do here. Only implement the return statement to make mypy happy
        return None, '', False

    def __call__(self) -> dict[str, Any]:
        return (
            TypeAdapter(Dict[str, Any]).dump_python(self.init_kwargs)
            if self.nested_model_default_partial_update
            else self.init_kwargs
        )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(init_kwargs={self.init_kwargs!r})'


class PydanticBaseEnvSettingsSource(PydanticBaseSettingsSource):
    def __init__(
        self,
        settings_cls: type[BaseSettings],
        case_sensitive: bool | None = None,
        env_prefix: str | None = None,
        env_ignore_empty: bool | None = None,
        env_parse_none_str: str | None = None,
        env_parse_enums: bool | None = None,
    ) -> None:
        super().__init__(settings_cls)
        self.case_sensitive = case_sensitive if case_sensitive is not None else self.config.get('case_sensitive', False)
        self.env_prefix = env_prefix if env_prefix is not None else self.config.get('env_prefix', '')
        self.env_ignore_empty = (
            env_ignore_empty if env_ignore_empty is not None else self.config.get('env_ignore_empty', False)
        )
        self.env_parse_none_str = (
            env_parse_none_str if env_parse_none_str is not None else self.config.get('env_parse_none_str')
        )
        self.env_parse_enums = env_parse_enums if env_parse_enums is not None else self.config.get('env_parse_enums')

    def _apply_case_sensitive(self, value: str) -> str:
        return value.lower() if not self.case_sensitive else value

    def _extract_field_info(self, field: FieldInfo, field_name: str) -> list[tuple[str, str, bool]]:
        """
        Extracts field info. This info is used to get the value of field from environment variables.

        It returns a list of tuples, each tuple contains:
            * field_key: The key of field that has to be used in model creation.
            * env_name: The environment variable name of the field.
            * value_is_complex: A flag to determine whether the value from environment variable
              is complex and has to be parsed.

        Args:
            field (FieldInfo): The field.
            field_name (str): The field name.

        Returns:
            list[tuple[str, str, bool]]: List of tuples, each tuple contains field_key, env_name, and value_is_complex.
        """
        field_info: list[tuple[str, str, bool]] = []
        if isinstance(field.validation_alias, (AliasChoices, AliasPath)):
            v_alias: str | list[str | int] | list[list[str | int]] | None = field.validation_alias.convert_to_aliases()
        else:
            v_alias = field.validation_alias

        if v_alias:
            if isinstance(v_alias, list):  # AliasChoices, AliasPath
                for alias in v_alias:
                    if isinstance(alias, str):  # AliasPath
                        field_info.append((alias, self._apply_case_sensitive(alias), True if len(alias) > 1 else False))
                    elif isinstance(alias, list):  # AliasChoices
                        first_arg = cast(str, alias[0])  # first item of an AliasChoices must be a str
                        field_info.append(
                            (first_arg, self._apply_case_sensitive(first_arg), True if len(alias) > 1 else False)
                        )
            else:  # string validation alias
                field_info.append((v_alias, self._apply_case_sensitive(v_alias), False))

        if not v_alias or self.config.get('populate_by_name', False):
            if origin_is_union(get_origin(field.annotation)) and _union_is_complex(field.annotation, field.metadata):
                field_info.append((field_name, self._apply_case_sensitive(self.env_prefix + field_name), True))
            else:
                field_info.append((field_name, self._apply_case_sensitive(self.env_prefix + field_name), False))

        return field_info

    def _replace_field_names_case_insensitively(self, field: FieldInfo, field_values: dict[str, Any]) -> dict[str, Any]:
        """
        Replace field names in values dict by looking in models fields insensitively.

        By having the following models:

            ```py
            class SubSubSub(BaseModel):
                VaL3: str

            class SubSub(BaseModel):
                Val2: str
                SUB_sub_SuB: SubSubSub

            class Sub(BaseModel):
                VAL1: str
                SUB_sub: SubSub

            class Settings(BaseSettings):
                nested: Sub

                model_config = SettingsConfigDict(env_nested_delimiter='__')
            ```

        Then:
            _replace_field_names_case_insensitively(
                field,
                {"val1": "v1", "sub_SUB": {"VAL2": "v2", "sub_SUB_sUb": {"vAl3": "v3"}}}
            )
            Returns {'VAL1': 'v1', 'SUB_sub': {'Val2': 'v2', 'SUB_sub_SuB': {'VaL3': 'v3'}}}
        """
        values: dict[str, Any] = {}

        for name, value in field_values.items():
            sub_model_field: FieldInfo | None = None

            annotation = field.annotation

            # If field is Optional, we need to find the actual type
            args = get_args(annotation)
            if origin_is_union(get_origin(field.annotation)) and len(args) == 2 and type(None) in args:
                for arg in args:
                    if arg is not None:
                        annotation = arg
                        break

            # This is here to make mypy happy
            # Item "None" of "Optional[Type[Any]]" has no attribute "model_fields"
            if not annotation or not hasattr(annotation, 'model_fields'):
                values[name] = value
                continue

            # Find field in sub model by looking in fields case insensitively
            for sub_model_field_name, f in annotation.model_fields.items():
                if not f.validation_alias and sub_model_field_name.lower() == name.lower():
                    sub_model_field = f
                    break

            if not sub_model_field:
                values[name] = value
                continue

            if lenient_issubclass(sub_model_field.annotation, BaseModel) and isinstance(value, dict):
                values[sub_model_field_name] = self._replace_field_names_case_insensitively(sub_model_field, value)
            else:
                values[sub_model_field_name] = value

        return values

    def _replace_env_none_type_values(self, field_value: dict[str, Any]) -> dict[str, Any]:
        """
        Recursively parse values that are of "None" type(EnvNoneType) to `None` type(None).
        """
        values: dict[str, Any] = {}

        for key, value in field_value.items():
            if not isinstance(value, EnvNoneType):
                values[key] = value if not isinstance(value, dict) else self._replace_env_none_type_values(value)
            else:
                values[key] = None

        return values

    def _get_resolved_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        """
        Gets the value, the preferred alias key for model creation, and a flag to determine whether value
        is complex.

        Note:
            In V3, this method should either be made public, or, this method should be removed and the
            abstract method get_field_value should be updated to include a "use_preferred_alias" flag.

        Args:
            field: The field.
            field_name: The field name.

        Returns:
            A tuple that contains the value, preferred key and a flag to determine whether value is complex.
        """
        field_value, field_key, value_is_complex = self.get_field_value(field, field_name)
        if not (value_is_complex or (self.config.get('populate_by_name', False) and (field_key == field_name))):
            field_infos = self._extract_field_info(field, field_name)
            preferred_key, *_ = field_infos[0]
            return field_value, preferred_key, value_is_complex
        return field_value, field_key, value_is_complex

    def __call__(self) -> dict[str, Any]:
        data: dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            try:
                field_value, field_key, value_is_complex = self._get_resolved_field_value(field, field_name)
            except Exception as e:
                raise SettingsError(
                    f'error getting value for field "{field_name}" from source "{self.__class__.__name__}"'
                ) from e

            try:
                field_value = self.prepare_field_value(field_name, field, field_value, value_is_complex)
            except ValueError as e:
                raise SettingsError(
                    f'error parsing value for field "{field_name}" from source "{self.__class__.__name__}"'
                ) from e

            if field_value is not None:
                if self.env_parse_none_str is not None:
                    if isinstance(field_value, dict):
                        field_value = self._replace_env_none_type_values(field_value)
                    elif isinstance(field_value, EnvNoneType):
                        field_value = None
                if (
                    not self.case_sensitive
                    # and lenient_issubclass(field.annotation, BaseModel)
                    and isinstance(field_value, dict)
                ):
                    data[field_key] = self._replace_field_names_case_insensitively(field, field_value)
                else:
                    data[field_key] = field_value

        return data


class SecretsSettingsSource(PydanticBaseEnvSettingsSource):
    """
    Source class for loading settings values from secret files.
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        secrets_dir: PathType | None = None,
        case_sensitive: bool | None = None,
        env_prefix: str | None = None,
        env_ignore_empty: bool | None = None,
        env_parse_none_str: str | None = None,
        env_parse_enums: bool | None = None,
    ) -> None:
        super().__init__(
            settings_cls, case_sensitive, env_prefix, env_ignore_empty, env_parse_none_str, env_parse_enums
        )
        self.secrets_dir = secrets_dir if secrets_dir is not None else self.config.get('secrets_dir')

    def __call__(self) -> dict[str, Any]:
        """
        Build fields from "secrets" files.
        """
        secrets: dict[str, str | None] = {}

        if self.secrets_dir is None:
            return secrets

        secrets_dirs = [self.secrets_dir] if isinstance(self.secrets_dir, (str, os.PathLike)) else self.secrets_dir
        secrets_paths = [Path(p).expanduser() for p in secrets_dirs]
        self.secrets_paths = []

        for path in secrets_paths:
            if not path.exists():
                warnings.warn(f'directory "{path}" does not exist')
            else:
                self.secrets_paths.append(path)

        if not len(self.secrets_paths):
            return secrets

        for path in self.secrets_paths:
            if not path.is_dir():
                raise SettingsError(f'secrets_dir must reference a directory, not a {path_type_label(path)}')

        return super().__call__()

    @classmethod
    def find_case_path(cls, dir_path: Path, file_name: str, case_sensitive: bool) -> Path | None:
        """
        Find a file within path's directory matching filename, optionally ignoring case.

        Args:
            dir_path: Directory path.
            file_name: File name.
            case_sensitive: Whether to search for file name case sensitively.

        Returns:
            Whether file path or `None` if file does not exist in directory.
        """
        for f in dir_path.iterdir():
            if f.name == file_name:
                return f
            elif not case_sensitive and f.name.lower() == file_name.lower():
                return f
        return None

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        """
        Gets the value for field from secret file and a flag to determine whether value is complex.

        Args:
            field: The field.
            field_name: The field name.

        Returns:
            A tuple that contains the value (`None` if the file does not exist), key, and
                a flag to determine whether value is complex.
        """

        for field_key, env_name, value_is_complex in self._extract_field_info(field, field_name):
            # paths reversed to match the last-wins behaviour of `env_file`
            for secrets_path in reversed(self.secrets_paths):
                path = self.find_case_path(secrets_path, env_name, self.case_sensitive)
                if not path:
                    # path does not exist, we currently don't return a warning for this
                    continue

                if path.is_file():
                    return path.read_text().strip(), field_key, value_is_complex
                else:
                    warnings.warn(
                        f'attempted to load secret file "{path}" but found a {path_type_label(path)} instead.',
                        stacklevel=4,
                    )

        return None, field_key, value_is_complex

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(secrets_dir={self.secrets_dir!r})'


class EnvSettingsSource(PydanticBaseEnvSettingsSource):
    """
    Source class for loading settings values from environment variables.
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        case_sensitive: bool | None = None,
        env_prefix: str | None = None,
        env_nested_delimiter: str | None = None,
        env_nested_max_split: int | None = None,
        env_ignore_empty: bool | None = None,
        env_parse_none_str: str | None = None,
        env_parse_enums: bool | None = None,
    ) -> None:
        super().__init__(
            settings_cls, case_sensitive, env_prefix, env_ignore_empty, env_parse_none_str, env_parse_enums
        )
        self.env_nested_delimiter = (
            env_nested_delimiter if env_nested_delimiter is not None else self.config.get('env_nested_delimiter')
        )
        self.env_nested_max_split = (
            env_nested_max_split if env_nested_max_split is not None else self.config.get('env_nested_max_split')
        )
        self.maxsplit = (self.env_nested_max_split or 0) - 1
        self.env_prefix_len = len(self.env_prefix)

        self.env_vars = self._load_env_vars()

    def _load_env_vars(self) -> Mapping[str, str | None]:
        return parse_env_vars(os.environ, self.case_sensitive, self.env_ignore_empty, self.env_parse_none_str)

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        """
        Gets the value for field from environment variables and a flag to determine whether value is complex.

        Args:
            field: The field.
            field_name: The field name.

        Returns:
            A tuple that contains the value (`None` if not found), key, and
                a flag to determine whether value is complex.
        """

        env_val: str | None = None
        for field_key, env_name, value_is_complex in self._extract_field_info(field, field_name):
            env_val = self.env_vars.get(env_name)
            if env_val is not None:
                break

        return env_val, field_key, value_is_complex

    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        """
        Prepare value for the field.

        * Extract value for nested field.
        * Deserialize value to python object for complex field.

        Args:
            field: The field.
            field_name: The field name.

        Returns:
            A tuple contains prepared value for the field.

        Raises:
            ValuesError: When There is an error in deserializing value for complex field.
        """
        is_complex, allow_parse_failure = self._field_is_complex(field)
        if self.env_parse_enums:
            enum_val = _annotation_enum_name_to_val(field.annotation, value)
            value = value if enum_val is None else enum_val

        if is_complex or value_is_complex:
            if isinstance(value, EnvNoneType):
                return value
            elif value is None:
                # field is complex but no value found so far, try explode_env_vars
                env_val_built = self.explode_env_vars(field_name, field, self.env_vars)
                if env_val_built:
                    return env_val_built
            else:
                # field is complex and there's a value, decode that as JSON, then add explode_env_vars
                try:
                    value = self.decode_complex_value(field_name, field, value)
                except ValueError as e:
                    if not allow_parse_failure:
                        raise e

                if isinstance(value, dict):
                    return deep_update(value, self.explode_env_vars(field_name, field, self.env_vars))
                else:
                    return value
        elif value is not None:
            # simplest case, field is not complex, we only need to add the value if it was found
            return value

    def _field_is_complex(self, field: FieldInfo) -> tuple[bool, bool]:
        """
        Find out if a field is complex, and if so whether JSON errors should be ignored
        """
        if self.field_is_complex(field):
            allow_parse_failure = False
        elif origin_is_union(get_origin(field.annotation)) and _union_is_complex(field.annotation, field.metadata):
            allow_parse_failure = True
        else:
            return False, False

        return True, allow_parse_failure

    # Default value of `case_sensitive` is `None`, because we don't want to break existing behavior.
    # We have to change the method to a non-static method and use
    # `self.case_sensitive` instead in V3.
    def next_field(
        self, field: FieldInfo | Any | None, key: str, case_sensitive: bool | None = None
    ) -> FieldInfo | None:
        """
        Find the field in a sub model by key(env name)

        By having the following models:

            ```py
            class SubSubModel(BaseSettings):
                dvals: Dict

            class SubModel(BaseSettings):
                vals: list[str]
                sub_sub_model: SubSubModel

            class Cfg(BaseSettings):
                sub_model: SubModel
            ```

        Then:
            next_field(sub_model, 'vals') Returns the `vals` field of `SubModel` class
            next_field(sub_model, 'sub_sub_model') Returns `sub_sub_model` field of `SubModel` class

        Args:
            field: The field.
            key: The key (env name).
            case_sensitive: Whether to search for key case sensitively.

        Returns:
            Field if it finds the next field otherwise `None`.
        """
        if not field:
            return None

        annotation = field.annotation if isinstance(field, FieldInfo) else field
        if origin_is_union(get_origin(annotation)) or isinstance(annotation, WithArgsTypes):
            for type_ in get_args(annotation):
                type_has_key = self.next_field(type_, key, case_sensitive)
                if type_has_key:
                    return type_has_key
        elif is_model_class(annotation) or is_pydantic_dataclass(annotation):
            fields = _get_model_fields(annotation)
            # `case_sensitive is None` is here to be compatible with the old behavior.
            # Has to be removed in V3.
            for field_name, f in fields.items():
                for _, env_name, _ in self._extract_field_info(f, field_name):
                    if case_sensitive is None or case_sensitive:
                        if field_name == key or env_name == key:
                            return f
                    elif field_name.lower() == key.lower() or env_name.lower() == key.lower():
                        return f
        return None

    def explode_env_vars(self, field_name: str, field: FieldInfo, env_vars: Mapping[str, str | None]) -> dict[str, Any]:
        """
        Process env_vars and extract the values of keys containing env_nested_delimiter into nested dictionaries.

        This is applied to a single field, hence filtering by env_var prefix.

        Args:
            field_name: The field name.
            field: The field.
            env_vars: Environment variables.

        Returns:
            A dictionary contains extracted values from nested env values.
        """
        if not self.env_nested_delimiter:
            return {}

        is_dict = lenient_issubclass(get_origin(field.annotation), dict)

        prefixes = [
            f'{env_name}{self.env_nested_delimiter}' for _, env_name, _ in self._extract_field_info(field, field_name)
        ]
        result: dict[str, Any] = {}
        for env_name, env_val in env_vars.items():
            try:
                prefix = next(prefix for prefix in prefixes if env_name.startswith(prefix))
            except StopIteration:
                continue
            # we remove the prefix before splitting in case the prefix has characters in common with the delimiter
            env_name_without_prefix = env_name[len(prefix) :]
            *keys, last_key = env_name_without_prefix.split(self.env_nested_delimiter, self.maxsplit)
            env_var = result
            target_field: FieldInfo | None = field
            for key in keys:
                target_field = self.next_field(target_field, key, self.case_sensitive)
                if isinstance(env_var, dict):
                    env_var = env_var.setdefault(key, {})

            # get proper field with last_key
            target_field = self.next_field(target_field, last_key, self.case_sensitive)

            # check if env_val maps to a complex field and if so, parse the env_val
            if (target_field or is_dict) and env_val:
                if target_field:
                    is_complex, allow_json_failure = self._field_is_complex(target_field)
                else:
                    # nested field type is dict
                    is_complex, allow_json_failure = True, True
                if is_complex:
                    try:
                        env_val = self.decode_complex_value(last_key, target_field, env_val)  # type: ignore
                    except ValueError as e:
                        if not allow_json_failure:
                            raise e
            if isinstance(env_var, dict):
                if last_key not in env_var or not isinstance(env_val, EnvNoneType) or env_var[last_key] == {}:
                    env_var[last_key] = env_val

        return result

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(env_nested_delimiter={self.env_nested_delimiter!r}, '
            f'env_prefix_len={self.env_prefix_len!r})'
        )


class DotEnvSettingsSource(EnvSettingsSource):
    """
    Source class for loading settings values from env files.
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        env_file: DotenvType | None = ENV_FILE_SENTINEL,
        env_file_encoding: str | None = None,
        case_sensitive: bool | None = None,
        env_prefix: str | None = None,
        env_nested_delimiter: str | None = None,
        env_nested_max_split: int | None = None,
        env_ignore_empty: bool | None = None,
        env_parse_none_str: str | None = None,
        env_parse_enums: bool | None = None,
    ) -> None:
        self.env_file = env_file if env_file != ENV_FILE_SENTINEL else settings_cls.model_config.get('env_file')
        self.env_file_encoding = (
            env_file_encoding if env_file_encoding is not None else settings_cls.model_config.get('env_file_encoding')
        )
        super().__init__(
            settings_cls,
            case_sensitive,
            env_prefix,
            env_nested_delimiter,
            env_nested_max_split,
            env_ignore_empty,
            env_parse_none_str,
            env_parse_enums,
        )

    def _load_env_vars(self) -> Mapping[str, str | None]:
        return self._read_env_files()

    @staticmethod
    def _static_read_env_file(
        file_path: Path,
        *,
        encoding: str | None = None,
        case_sensitive: bool = False,
        ignore_empty: bool = False,
        parse_none_str: str | None = None,
    ) -> Mapping[str, str | None]:
        file_vars: dict[str, str | None] = dotenv_values(file_path, encoding=encoding or 'utf8')
        return parse_env_vars(file_vars, case_sensitive, ignore_empty, parse_none_str)

    def _read_env_file(
        self,
        file_path: Path,
    ) -> Mapping[str, str | None]:
        return self._static_read_env_file(
            file_path,
            encoding=self.env_file_encoding,
            case_sensitive=self.case_sensitive,
            ignore_empty=self.env_ignore_empty,
            parse_none_str=self.env_parse_none_str,
        )

    def _read_env_files(self) -> Mapping[str, str | None]:
        env_files = self.env_file
        if env_files is None:
            return {}

        if isinstance(env_files, (str, os.PathLike)):
            env_files = [env_files]

        dotenv_vars: dict[str, str | None] = {}
        for env_file in env_files:
            env_path = Path(env_file).expanduser()
            if env_path.is_file():
                dotenv_vars.update(self._read_env_file(env_path))

        return dotenv_vars

    def __call__(self) -> dict[str, Any]:
        data: dict[str, Any] = super().__call__()
        is_extra_allowed = self.config.get('extra') != 'forbid'

        # As `extra` config is allowed in dotenv settings source, We have to
        # update data with extra env variables from dotenv file.
        for env_name, env_value in self.env_vars.items():
            if not env_value or env_name in data:
                continue
            env_used = False
            for field_name, field in self.settings_cls.model_fields.items():
                for _, field_env_name, _ in self._extract_field_info(field, field_name):
                    if env_name == field_env_name or (
                        (
                            _annotation_is_complex(field.annotation, field.metadata)
                            or (
                                origin_is_union(get_origin(field.annotation))
                                and _union_is_complex(field.annotation, field.metadata)
                            )
                        )
                        and env_name.startswith(field_env_name)
                    ):
                        env_used = True
                        break
                if env_used:
                    break
            if not env_used:
                if is_extra_allowed and env_name.startswith(self.env_prefix):
                    # env_prefix should be respected and removed from the env_name
                    normalized_env_name = env_name[len(self.env_prefix) :]
                    data[normalized_env_name] = env_value
                else:
                    data[env_name] = env_value
        return data

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(env_file={self.env_file!r}, env_file_encoding={self.env_file_encoding!r}, '
            f'env_nested_delimiter={self.env_nested_delimiter!r}, env_prefix_len={self.env_prefix_len!r})'
        )


class CliSettingsSource(EnvSettingsSource, Generic[T]):
    """
    Source class for loading settings values from CLI.

    Note:
        A `CliSettingsSource` connects with a `root_parser` object by using the parser methods to add
        `settings_cls` fields as command line arguments. The `CliSettingsSource` internal parser representation
        is based upon the `argparse` parsing library, and therefore, requires the parser methods to support
        the same attributes as their `argparse` library counterparts.

    Args:
        cli_prog_name: The CLI program name to display in help text. Defaults to `None` if cli_parse_args is `None`.
            Otherwse, defaults to sys.argv[0].
        cli_parse_args: The list of CLI arguments to parse. Defaults to None.
            If set to `True`, defaults to sys.argv[1:].
        cli_parse_none_str: The CLI string value that should be parsed (e.g. "null", "void", "None", etc.) into `None`
            type(None). Defaults to "null" if cli_avoid_json is `False`, and "None" if cli_avoid_json is `True`.
        cli_hide_none_type: Hide `None` values in CLI help text. Defaults to `False`.
        cli_avoid_json: Avoid complex JSON objects in CLI help text. Defaults to `False`.
        cli_enforce_required: Enforce required fields at the CLI. Defaults to `False`.
        cli_use_class_docs_for_groups: Use class docstrings in CLI group help text instead of field descriptions.
            Defaults to `False`.
        cli_exit_on_error: Determines whether or not the internal parser exits with error info when an error occurs.
            Defaults to `True`.
        cli_prefix: Prefix for command line arguments added under the root parser. Defaults to "".
        cli_flag_prefix_char: The flag prefix character to use for CLI optional arguments. Defaults to '-'.
        cli_implicit_flags: Whether `bool` fields should be implicitly converted into CLI boolean flags.
            (e.g. --flag, --no-flag). Defaults to `False`.
        cli_ignore_unknown_args: Whether to ignore unknown CLI args and parse only known ones. Defaults to `False`.
        cli_kebab_case: CLI args use kebab case. Defaults to `False`.
        case_sensitive: Whether CLI "--arg" names should be read with case-sensitivity. Defaults to `True`.
            Note: Case-insensitive matching is only supported on the internal root parser and does not apply to CLI
            subcommands.
        root_parser: The root parser object.
        parse_args_method: The root parser parse args method. Defaults to `argparse.ArgumentParser.parse_args`.
        add_argument_method: The root parser add argument method. Defaults to `argparse.ArgumentParser.add_argument`.
        add_argument_group_method: The root parser add argument group method.
            Defaults to `argparse.ArgumentParser.add_argument_group`.
        add_parser_method: The root parser add new parser (sub-command) method.
            Defaults to `argparse._SubParsersAction.add_parser`.
        add_subparsers_method: The root parser add subparsers (sub-commands) method.
            Defaults to `argparse.ArgumentParser.add_subparsers`.
        formatter_class: A class for customizing the root parser help text. Defaults to `argparse.RawDescriptionHelpFormatter`.
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        cli_prog_name: str | None = None,
        cli_parse_args: bool | list[str] | tuple[str, ...] | None = None,
        cli_parse_none_str: str | None = None,
        cli_hide_none_type: bool | None = None,
        cli_avoid_json: bool | None = None,
        cli_enforce_required: bool | None = None,
        cli_use_class_docs_for_groups: bool | None = None,
        cli_exit_on_error: bool | None = None,
        cli_prefix: str | None = None,
        cli_flag_prefix_char: str | None = None,
        cli_implicit_flags: bool | None = None,
        cli_ignore_unknown_args: bool | None = None,
        cli_kebab_case: bool | None = None,
        case_sensitive: bool | None = True,
        root_parser: Any = None,
        parse_args_method: Callable[..., Any] | None = None,
        add_argument_method: Callable[..., Any] | None = ArgumentParser.add_argument,
        add_argument_group_method: Callable[..., Any] | None = ArgumentParser.add_argument_group,
        add_parser_method: Callable[..., Any] | None = _SubParsersAction.add_parser,
        add_subparsers_method: Callable[..., Any] | None = ArgumentParser.add_subparsers,
        formatter_class: Any = RawDescriptionHelpFormatter,
    ) -> None:
        self.cli_prog_name = (
            cli_prog_name if cli_prog_name is not None else settings_cls.model_config.get('cli_prog_name', sys.argv[0])
        )
        self.cli_hide_none_type = (
            cli_hide_none_type
            if cli_hide_none_type is not None
            else settings_cls.model_config.get('cli_hide_none_type', False)
        )
        self.cli_avoid_json = (
            cli_avoid_json if cli_avoid_json is not None else settings_cls.model_config.get('cli_avoid_json', False)
        )
        if not cli_parse_none_str:
            cli_parse_none_str = 'None' if self.cli_avoid_json is True else 'null'
        self.cli_parse_none_str = cli_parse_none_str
        self.cli_enforce_required = (
            cli_enforce_required
            if cli_enforce_required is not None
            else settings_cls.model_config.get('cli_enforce_required', False)
        )
        self.cli_use_class_docs_for_groups = (
            cli_use_class_docs_for_groups
            if cli_use_class_docs_for_groups is not None
            else settings_cls.model_config.get('cli_use_class_docs_for_groups', False)
        )
        self.cli_exit_on_error = (
            cli_exit_on_error
            if cli_exit_on_error is not None
            else settings_cls.model_config.get('cli_exit_on_error', True)
        )
        self.cli_prefix = cli_prefix if cli_prefix is not None else settings_cls.model_config.get('cli_prefix', '')
        self.cli_flag_prefix_char = (
            cli_flag_prefix_char
            if cli_flag_prefix_char is not None
            else settings_cls.model_config.get('cli_flag_prefix_char', '-')
        )
        self._cli_flag_prefix = self.cli_flag_prefix_char * 2
        if self.cli_prefix:
            if cli_prefix.startswith('.') or cli_prefix.endswith('.') or not cli_prefix.replace('.', '').isidentifier():  # type: ignore
                raise SettingsError(f'CLI settings source prefix is invalid: {cli_prefix}')
            self.cli_prefix += '.'
        self.cli_implicit_flags = (
            cli_implicit_flags
            if cli_implicit_flags is not None
            else settings_cls.model_config.get('cli_implicit_flags', False)
        )
        self.cli_ignore_unknown_args = (
            cli_ignore_unknown_args
            if cli_ignore_unknown_args is not None
            else settings_cls.model_config.get('cli_ignore_unknown_args', False)
        )
        self.cli_kebab_case = (
            cli_kebab_case if cli_kebab_case is not None else settings_cls.model_config.get('cli_kebab_case', False)
        )

        case_sensitive = case_sensitive if case_sensitive is not None else True
        if not case_sensitive and root_parser is not None:
            raise SettingsError('Case-insensitive matching is only supported on the internal root parser')

        super().__init__(
            settings_cls,
            env_nested_delimiter='.',
            env_parse_none_str=self.cli_parse_none_str,
            env_parse_enums=True,
            env_prefix=self.cli_prefix,
            case_sensitive=case_sensitive,
        )

        root_parser = (
            _CliInternalArgParser(
                cli_exit_on_error=self.cli_exit_on_error,
                prog=self.cli_prog_name,
                description=None if settings_cls.__doc__ is None else dedent(settings_cls.__doc__),
                formatter_class=formatter_class,
                prefix_chars=self.cli_flag_prefix_char,
                allow_abbrev=False,
            )
            if root_parser is None
            else root_parser
        )
        self._connect_root_parser(
            root_parser=root_parser,
            parse_args_method=parse_args_method,
            add_argument_method=add_argument_method,
            add_argument_group_method=add_argument_group_method,
            add_parser_method=add_parser_method,
            add_subparsers_method=add_subparsers_method,
            formatter_class=formatter_class,
        )

        if cli_parse_args not in (None, False):
            if cli_parse_args is True:
                cli_parse_args = sys.argv[1:]
            elif not isinstance(cli_parse_args, (list, tuple)):
                raise SettingsError(
                    f'cli_parse_args must be List[str] or Tuple[str, ...], recieved {type(cli_parse_args)}'
                )
            self._load_env_vars(parsed_args=self._parse_args(self.root_parser, cli_parse_args))

    @overload
    def __call__(self) -> dict[str, Any]: ...

    @overload
    def __call__(self, *, args: list[str] | tuple[str, ...] | bool) -> CliSettingsSource[T]:
        """
        Parse and load the command line arguments list into the CLI settings source.

        Args:
            args:
                The command line arguments to parse and load. Defaults to `None`, which means do not parse
                command line arguments. If set to `True`, defaults to sys.argv[1:]. If set to `False`, does
                not parse command line arguments.

        Returns:
            CliSettingsSource: The object instance itself.
        """
        ...

    @overload
    def __call__(self, *, parsed_args: Namespace | SimpleNamespace | dict[str, Any]) -> CliSettingsSource[T]:
        """
        Loads parsed command line arguments into the CLI settings source.

        Note:
            The parsed args must be in `argparse.Namespace`, `SimpleNamespace`, or vars dictionary
            (e.g., vars(argparse.Namespace)) format.

        Args:
            parsed_args: The parsed args to load.

        Returns:
            CliSettingsSource: The object instance itself.
        """
        ...

    def __call__(
        self,
        *,
        args: list[str] | tuple[str, ...] | bool | None = None,
        parsed_args: Namespace | SimpleNamespace | dict[str, list[str] | str] | None = None,
    ) -> dict[str, Any] | CliSettingsSource[T]:
        if args is not None and parsed_args is not None:
            raise SettingsError('`args` and `parsed_args` are mutually exclusive')
        elif args is not None:
            if args is False:
                return self._load_env_vars(parsed_args={})
            if args is True:
                args = sys.argv[1:]
            return self._load_env_vars(parsed_args=self._parse_args(self.root_parser, args))
        elif parsed_args is not None:
            return self._load_env_vars(parsed_args=parsed_args)
        else:
            return super().__call__()

    @overload
    def _load_env_vars(self) -> Mapping[str, str | None]: ...

    @overload
    def _load_env_vars(self, *, parsed_args: Namespace | SimpleNamespace | dict[str, Any]) -> CliSettingsSource[T]:
        """
        Loads the parsed command line arguments into the CLI environment settings variables.

        Note:
            The parsed args must be in `argparse.Namespace`, `SimpleNamespace`, or vars dictionary
            (e.g., vars(argparse.Namespace)) format.

        Args:
            parsed_args: The parsed args to load.

        Returns:
            CliSettingsSource: The object instance itself.
        """
        ...

    def _load_env_vars(
        self, *, parsed_args: Namespace | SimpleNamespace | dict[str, list[str] | str] | None = None
    ) -> Mapping[str, str | None] | CliSettingsSource[T]:
        if parsed_args is None:
            return {}

        if isinstance(parsed_args, (Namespace, SimpleNamespace)):
            parsed_args = vars(parsed_args)

        selected_subcommands: list[str] = []
        for field_name, val in parsed_args.items():
            if isinstance(val, list):
                parsed_args[field_name] = self._merge_parsed_list(val, field_name)
            elif field_name.endswith(':subcommand') and val is not None:
                subcommand_name = field_name.split(':')[0] + val
                subcommand_dest = self._cli_subcommands[field_name][subcommand_name]
                selected_subcommands.append(subcommand_dest)

        for subcommands in self._cli_subcommands.values():
            for subcommand_dest in subcommands.values():
                if subcommand_dest not in selected_subcommands:
                    parsed_args[subcommand_dest] = self.cli_parse_none_str

        parsed_args = {
            key: val
            for key, val in parsed_args.items()
            if not key.endswith(':subcommand') and val is not PydanticUndefined
        }
        if selected_subcommands:
            last_selected_subcommand = max(selected_subcommands, key=len)
            if not any(field_name for field_name in parsed_args.keys() if f'{last_selected_subcommand}.' in field_name):
                parsed_args[last_selected_subcommand] = '{}'

        self.env_vars = parse_env_vars(
            cast(Mapping[str, str], parsed_args),
            self.case_sensitive,
            self.env_ignore_empty,
            self.cli_parse_none_str,
        )

        return self

    def _get_merge_parsed_list_types(
        self, parsed_list: list[str], field_name: str
    ) -> tuple[Optional[type], Optional[type]]:
        merge_type = self._cli_dict_args.get(field_name, list)
        if (
            merge_type is list
            or not origin_is_union(get_origin(merge_type))
            or not any(
                type_
                for type_ in get_args(merge_type)
                if type_ is not type(None) and get_origin(type_) not in (dict, Mapping)
            )
        ):
            inferred_type = merge_type
        else:
            inferred_type = list if parsed_list and (len(parsed_list) > 1 or parsed_list[0].startswith('[')) else str

        return merge_type, inferred_type

    def _merge_parsed_list(self, parsed_list: list[str], field_name: str) -> str:
        try:
            merged_list: list[str] = []
            is_last_consumed_a_value = False
            merge_type, inferred_type = self._get_merge_parsed_list_types(parsed_list, field_name)
            for val in parsed_list:
                if not isinstance(val, str):
                    # If val is not a string, it's from an external parser and we can ignore parsing the rest of the
                    # list.
                    break
                val = val.strip()
                if val.startswith('[') and val.endswith(']'):
                    val = val[1:-1].strip()
                while val:
                    val = val.strip()
                    if val.startswith(','):
                        val = self._consume_comma(val, merged_list, is_last_consumed_a_value)
                        is_last_consumed_a_value = False
                    else:
                        if val.startswith('{') or val.startswith('['):
                            val = self._consume_object_or_array(val, merged_list)
                        else:
                            try:
                                val = self._consume_string_or_number(val, merged_list, merge_type)
                            except ValueError as e:
                                if merge_type is inferred_type:
                                    raise e
                                merge_type = inferred_type
                                val = self._consume_string_or_number(val, merged_list, merge_type)
                        is_last_consumed_a_value = True
                if not is_last_consumed_a_value:
                    val = self._consume_comma(val, merged_list, is_last_consumed_a_value)

            if merge_type is str:
                return merged_list[0]
            elif merge_type is list:
                return f'[{",".join(merged_list)}]'
            else:
                merged_dict: dict[str, str] = {}
                for item in merged_list:
                    merged_dict.update(json.loads(item))
                return json.dumps(merged_dict)
        except Exception as e:
            raise SettingsError(f'Parsing error encountered for {field_name}: {e}')

    def _consume_comma(self, item: str, merged_list: list[str], is_last_consumed_a_value: bool) -> str:
        if not is_last_consumed_a_value:
            merged_list.append('""')
        return item[1:]

    def _consume_object_or_array(self, item: str, merged_list: list[str]) -> str:
        count = 1
        close_delim = '}' if item.startswith('{') else ']'
        for consumed in range(1, len(item)):
            if item[consumed] in ('{', '['):
                count += 1
            elif item[consumed] in ('}', ']'):
                count -= 1
                if item[consumed] == close_delim and count == 0:
                    merged_list.append(item[: consumed + 1])
                    return item[consumed + 1 :]
        raise SettingsError(f'Missing end delimiter "{close_delim}"')

    def _consume_string_or_number(self, item: str, merged_list: list[str], merge_type: type[Any] | None) -> str:
        consumed = 0 if merge_type is not str else len(item)
        is_find_end_quote = False
        while consumed < len(item):
            if item[consumed] == '"' and (consumed == 0 or item[consumed - 1] != '\\'):
                is_find_end_quote = not is_find_end_quote
            if not is_find_end_quote and item[consumed] == ',':
                break
            consumed += 1
        if is_find_end_quote:
            raise SettingsError('Mismatched quotes')
        val_string = item[:consumed].strip()
        if merge_type in (list, str):
            try:
                float(val_string)
            except ValueError:
                if val_string == self.cli_parse_none_str:
                    val_string = 'null'
                if val_string not in ('true', 'false', 'null') and not val_string.startswith('"'):
                    val_string = f'"{val_string}"'
            merged_list.append(val_string)
        else:
            key, val = (kv for kv in val_string.split('=', 1))
            if key.startswith('"') and not key.endswith('"') and not val.startswith('"') and val.endswith('"'):
                raise ValueError(f'Dictionary key=val parameter is a quoted string: {val_string}')
            key, val = key.strip('"'), val.strip('"')
            merged_list.append(json.dumps({key: val}))
        return item[consumed:]

    def _get_sub_models(self, model: type[BaseModel], field_name: str, field_info: FieldInfo) -> list[type[BaseModel]]:
        field_types: tuple[Any, ...] = (
            (field_info.annotation,) if not get_args(field_info.annotation) else get_args(field_info.annotation)
        )
        if self.cli_hide_none_type:
            field_types = tuple([type_ for type_ in field_types if type_ is not type(None)])

        sub_models: list[type[BaseModel]] = []
        for type_ in field_types:
            if _annotation_contains_types(type_, (_CliSubCommand,), is_include_origin=False):
                raise SettingsError(f'CliSubCommand is not outermost annotation for {model.__name__}.{field_name}')
            elif _annotation_contains_types(type_, (_CliPositionalArg,), is_include_origin=False):
                raise SettingsError(f'CliPositionalArg is not outermost annotation for {model.__name__}.{field_name}')
            if is_model_class(_strip_annotated(type_)) or is_pydantic_dataclass(_strip_annotated(type_)):
                sub_models.append(_strip_annotated(type_))
        return sub_models

    def _verify_cli_flag_annotations(self, model: type[BaseModel], field_name: str, field_info: FieldInfo) -> None:
        if _CliImplicitFlag in field_info.metadata:
            cli_flag_name = 'CliImplicitFlag'
        elif _CliExplicitFlag in field_info.metadata:
            cli_flag_name = 'CliExplicitFlag'
        else:
            return

        if field_info.annotation is not bool:
            raise SettingsError(f'{cli_flag_name} argument {model.__name__}.{field_name} is not of type bool')
        elif sys.version_info < (3, 9) and (
            field_info.default is PydanticUndefined and field_info.default_factory is None
        ):
            raise SettingsError(
                f'{cli_flag_name} argument {model.__name__}.{field_name} must have default for python versions < 3.9'
            )

    def _sort_arg_fields(self, model: type[BaseModel]) -> list[tuple[str, FieldInfo]]:
        positional_variadic_arg = []
        positional_args, subcommand_args, optional_args = [], [], []
        for field_name, field_info in _get_model_fields(model).items():
            if _CliSubCommand in field_info.metadata:
                if not field_info.is_required():
                    raise SettingsError(f'subcommand argument {model.__name__}.{field_name} has a default value')
                else:
                    alias_names, *_ = _get_alias_names(field_name, field_info)
                    if len(alias_names) > 1:
                        raise SettingsError(f'subcommand argument {model.__name__}.{field_name} has multiple aliases')
                    field_types = [type_ for type_ in get_args(field_info.annotation) if type_ is not type(None)]
                    for field_type in field_types:
                        if not (is_model_class(field_type) or is_pydantic_dataclass(field_type)):
                            raise SettingsError(
                                f'subcommand argument {model.__name__}.{field_name} has type not derived from BaseModel'
                            )
                subcommand_args.append((field_name, field_info))
            elif _CliPositionalArg in field_info.metadata:
                alias_names, *_ = _get_alias_names(field_name, field_info)
                if len(alias_names) > 1:
                    raise SettingsError(f'positional argument {model.__name__}.{field_name} has multiple aliases')
                is_append_action = _annotation_contains_types(
                    field_info.annotation, (list, set, dict, Sequence, Mapping), is_strip_annotated=True
                )
                if not is_append_action:
                    positional_args.append((field_name, field_info))
                else:
                    positional_variadic_arg.append((field_name, field_info))
            else:
                self._verify_cli_flag_annotations(model, field_name, field_info)
                optional_args.append((field_name, field_info))

        if positional_variadic_arg:
            if len(positional_variadic_arg) > 1:
                field_names = ', '.join([name for name, info in positional_variadic_arg])
                raise SettingsError(f'{model.__name__} has multiple variadic positonal arguments: {field_names}')
            elif subcommand_args:
                field_names = ', '.join([name for name, info in positional_variadic_arg + subcommand_args])
                raise SettingsError(
                    f'{model.__name__} has variadic positonal arguments and subcommand arguments: {field_names}'
                )

        return positional_args + positional_variadic_arg + subcommand_args + optional_args

    @property
    def root_parser(self) -> T:
        """The connected root parser instance."""
        return self._root_parser

    def _connect_parser_method(
        self, parser_method: Callable[..., Any] | None, method_name: str, *args: Any, **kwargs: Any
    ) -> Callable[..., Any]:
        if (
            parser_method is not None
            and self.case_sensitive is False
            and method_name == 'parse_args_method'
            and isinstance(self._root_parser, _CliInternalArgParser)
        ):

            def parse_args_insensitive_method(
                root_parser: _CliInternalArgParser,
                args: list[str] | tuple[str, ...] | None = None,
                namespace: Namespace | None = None,
            ) -> Any:
                insensitive_args = []
                for arg in shlex.split(shlex.join(args)) if args else []:
                    flag_prefix = rf'\{self.cli_flag_prefix_char}{{1,2}}'
                    matched = re.match(rf'^({flag_prefix}[^\s=]+)(.*)', arg)
                    if matched:
                        arg = matched.group(1).lower() + matched.group(2)
                    insensitive_args.append(arg)
                return parser_method(root_parser, insensitive_args, namespace)  # type: ignore

            return parse_args_insensitive_method

        elif parser_method is None:

            def none_parser_method(*args: Any, **kwargs: Any) -> Any:
                raise SettingsError(
                    f'cannot connect CLI settings source root parser: {method_name} is set to `None` but is needed for connecting'
                )

            return none_parser_method

        else:
            return parser_method

    def _connect_group_method(self, add_argument_group_method: Callable[..., Any] | None) -> Callable[..., Any]:
        add_argument_group = self._connect_parser_method(add_argument_group_method, 'add_argument_group_method')

        def add_group_method(parser: Any, **kwargs: Any) -> Any:
            if not kwargs.pop('_is_cli_mutually_exclusive_group'):
                kwargs.pop('required')
                return add_argument_group(parser, **kwargs)
            else:
                main_group_kwargs = {arg: kwargs.pop(arg) for arg in ['title', 'description'] if arg in kwargs}
                main_group_kwargs['title'] += ' (mutually exclusive)'
                group = add_argument_group(parser, **main_group_kwargs)
                if not hasattr(group, 'add_mutually_exclusive_group'):
                    raise SettingsError(
                        'cannot connect CLI settings source root parser: '
                        'group object is missing add_mutually_exclusive_group but is needed for connecting'
                    )
                return group.add_mutually_exclusive_group(**kwargs)

        return add_group_method

    def _connect_root_parser(
        self,
        root_parser: T,
        parse_args_method: Callable[..., Any] | None,
        add_argument_method: Callable[..., Any] | None = ArgumentParser.add_argument,
        add_argument_group_method: Callable[..., Any] | None = ArgumentParser.add_argument_group,
        add_parser_method: Callable[..., Any] | None = _SubParsersAction.add_parser,
        add_subparsers_method: Callable[..., Any] | None = ArgumentParser.add_subparsers,
        formatter_class: Any = RawDescriptionHelpFormatter,
    ) -> None:
        def _parse_known_args(*args: Any, **kwargs: Any) -> Namespace:
            return ArgumentParser.parse_known_args(*args, **kwargs)[0]

        self._root_parser = root_parser
        if parse_args_method is None:
            parse_args_method = _parse_known_args if self.cli_ignore_unknown_args else ArgumentParser.parse_args
        self._parse_args = self._connect_parser_method(parse_args_method, 'parse_args_method')
        self._add_argument = self._connect_parser_method(add_argument_method, 'add_argument_method')
        self._add_group = self._connect_group_method(add_argument_group_method)
        self._add_parser = self._connect_parser_method(add_parser_method, 'add_parser_method')
        self._add_subparsers = self._connect_parser_method(add_subparsers_method, 'add_subparsers_method')
        self._formatter_class = formatter_class
        self._cli_dict_args: dict[str, type[Any] | None] = {}
        self._cli_subcommands: defaultdict[str, dict[str, str]] = defaultdict(dict)
        self._add_parser_args(
            parser=self.root_parser,
            model=self.settings_cls,
            added_args=[],
            arg_prefix=self.env_prefix,
            subcommand_prefix=self.env_prefix,
            group=None,
            alias_prefixes=[],
            model_default=PydanticUndefined,
        )

    def _add_parser_args(
        self,
        parser: Any,
        model: type[BaseModel],
        added_args: list[str],
        arg_prefix: str,
        subcommand_prefix: str,
        group: Any,
        alias_prefixes: list[str],
        model_default: Any,
    ) -> ArgumentParser:
        subparsers: Any = None
        alias_path_args: dict[str, str] = {}
        # Ignore model default if the default is a model and not a subclass of the current model.
        model_default = (
            None
            if (
                (is_model_class(type(model_default)) or is_pydantic_dataclass(type(model_default)))
                and not issubclass(type(model_default), model)
            )
            else model_default
        )
        for field_name, field_info in self._sort_arg_fields(model):
            sub_models: list[type[BaseModel]] = self._get_sub_models(model, field_name, field_info)
            alias_names, is_alias_path_only = _get_alias_names(
                field_name, field_info, alias_path_args=alias_path_args, case_sensitive=self.case_sensitive
            )
            preferred_alias = alias_names[0]
            if _CliSubCommand in field_info.metadata:
                for model in sub_models:
                    subcommand_alias = self._check_kebab_name(
                        model.__name__ if len(sub_models) > 1 else preferred_alias
                    )
                    subcommand_name = f'{arg_prefix}{subcommand_alias}'
                    subcommand_dest = f'{arg_prefix}{preferred_alias}'
                    self._cli_subcommands[f'{arg_prefix}:subcommand'][subcommand_name] = subcommand_dest

                    subcommand_help = None if len(sub_models) > 1 else field_info.description
                    if self.cli_use_class_docs_for_groups:
                        subcommand_help = None if model.__doc__ is None else dedent(model.__doc__)

                    subparsers = (
                        self._add_subparsers(
                            parser,
                            title='subcommands',
                            dest=f'{arg_prefix}:subcommand',
                            description=field_info.description if len(sub_models) > 1 else None,
                        )
                        if subparsers is None
                        else subparsers
                    )

                    if hasattr(subparsers, 'metavar'):
                        subparsers.metavar = (
                            f'{subparsers.metavar[:-1]},{subcommand_alias}}}'
                            if subparsers.metavar
                            else f'{{{subcommand_alias}}}'
                        )

                    self._add_parser_args(
                        parser=self._add_parser(
                            subparsers,
                            subcommand_alias,
                            help=subcommand_help,
                            formatter_class=self._formatter_class,
                            description=None if model.__doc__ is None else dedent(model.__doc__),
                        ),
                        model=model,
                        added_args=[],
                        arg_prefix=f'{arg_prefix}{preferred_alias}.',
                        subcommand_prefix=f'{subcommand_prefix}{preferred_alias}.',
                        group=None,
                        alias_prefixes=[],
                        model_default=PydanticUndefined,
                    )
            else:
                flag_prefix: str = self._cli_flag_prefix
                is_append_action = _annotation_contains_types(
                    field_info.annotation, (list, set, dict, Sequence, Mapping), is_strip_annotated=True
                )
                is_parser_submodel = sub_models and not is_append_action
                kwargs: dict[str, Any] = {}
                kwargs['default'] = CLI_SUPPRESS
                kwargs['help'] = self._help_format(field_name, field_info, model_default)
                kwargs['metavar'] = self._metavar_format(field_info.annotation)
                kwargs['required'] = (
                    self.cli_enforce_required and field_info.is_required() and model_default is PydanticUndefined
                )
                kwargs['dest'] = (
                    # Strip prefix if validation alias is set and value is not complex.
                    # Related https://github.com/pydantic/pydantic-settings/pull/25
                    f'{arg_prefix}{preferred_alias}'[self.env_prefix_len :]
                    if arg_prefix and field_info.validation_alias is not None and not is_parser_submodel
                    else f'{arg_prefix}{preferred_alias}'
                )

                arg_names = self._get_arg_names(arg_prefix, subcommand_prefix, alias_prefixes, alias_names, added_args)
                if not arg_names or (kwargs['dest'] in added_args):
                    continue

                if is_append_action:
                    kwargs['action'] = 'append'
                    if _annotation_contains_types(field_info.annotation, (dict, Mapping), is_strip_annotated=True):
                        self._cli_dict_args[kwargs['dest']] = field_info.annotation

                if _CliPositionalArg in field_info.metadata:
                    arg_names, flag_prefix = self._convert_positional_arg(
                        kwargs, field_info, preferred_alias, model_default
                    )

                self._convert_bool_flag(kwargs, field_info, model_default)

                if is_parser_submodel:
                    self._add_parser_submodels(
                        parser,
                        model,
                        sub_models,
                        added_args,
                        arg_prefix,
                        subcommand_prefix,
                        flag_prefix,
                        arg_names,
                        kwargs,
                        field_name,
                        field_info,
                        alias_names,
                        model_default=model_default,
                    )
                elif not is_alias_path_only:
                    if group is not None:
                        if isinstance(group, dict):
                            group = self._add_group(parser, **group)
                        added_args += list(arg_names)
                        self._add_argument(group, *(f'{flag_prefix[:len(name)]}{name}' for name in arg_names), **kwargs)
                    else:
                        added_args += list(arg_names)
                        self._add_argument(
                            parser, *(f'{flag_prefix[:len(name)]}{name}' for name in arg_names), **kwargs
                        )

        self._add_parser_alias_paths(parser, alias_path_args, added_args, arg_prefix, subcommand_prefix, group)
        return parser

    def _check_kebab_name(self, name: str) -> str:
        if self.cli_kebab_case:
            return name.replace('_', '-')
        return name

    def _convert_bool_flag(self, kwargs: dict[str, Any], field_info: FieldInfo, model_default: Any) -> None:
        if kwargs['metavar'] == 'bool':
            default = None
            if field_info.default is not PydanticUndefined:
                default = field_info.default
            if model_default is not PydanticUndefined:
                default = model_default
            if sys.version_info >= (3, 9) or isinstance(default, bool):
                if (self.cli_implicit_flags or _CliImplicitFlag in field_info.metadata) and (
                    _CliExplicitFlag not in field_info.metadata
                ):
                    del kwargs['metavar']
                    kwargs['action'] = (
                        BooleanOptionalAction if sys.version_info >= (3, 9) else f'store_{str(not default).lower()}'
                    )

    def _convert_positional_arg(
        self, kwargs: dict[str, Any], field_info: FieldInfo, preferred_alias: str, model_default: Any
    ) -> tuple[list[str], str]:
        flag_prefix = ''
        arg_names = [kwargs['dest']]
        kwargs['default'] = PydanticUndefined
        kwargs['metavar'] = self._check_kebab_name(preferred_alias.upper())

        # Note: CLI positional args are always strictly required at the CLI. Therefore, use field_info.is_required in
        # conjunction with model_default instead of the derived kwargs['required'].
        is_required = field_info.is_required() and model_default is PydanticUndefined
        if kwargs.get('action') == 'append':
            del kwargs['action']
            kwargs['nargs'] = '+' if is_required else '*'
        elif not is_required:
            kwargs['nargs'] = '?'

        del kwargs['dest']
        del kwargs['required']
        return arg_names, flag_prefix

    def _get_arg_names(
        self,
        arg_prefix: str,
        subcommand_prefix: str,
        alias_prefixes: list[str],
        alias_names: tuple[str, ...],
        added_args: list[str],
    ) -> list[str]:
        arg_names: list[str] = []
        for prefix in [arg_prefix] + alias_prefixes:
            for name in alias_names:
                arg_name = self._check_kebab_name(
                    f'{prefix}{name}'
                    if subcommand_prefix == self.env_prefix
                    else f'{prefix.replace(subcommand_prefix, "", 1)}{name}'
                )
                if arg_name not in added_args:
                    arg_names.append(arg_name)
        return arg_names

    def _add_parser_submodels(
        self,
        parser: Any,
        model: type[BaseModel],
        sub_models: list[type[BaseModel]],
        added_args: list[str],
        arg_prefix: str,
        subcommand_prefix: str,
        flag_prefix: str,
        arg_names: list[str],
        kwargs: dict[str, Any],
        field_name: str,
        field_info: FieldInfo,
        alias_names: tuple[str, ...],
        model_default: Any,
    ) -> None:
        if issubclass(model, CliMutuallyExclusiveGroup):
            # Argparse has deprecated "calling add_argument_group() or add_mutually_exclusive_group() on a
            # mutually exclusive group" (https://docs.python.org/3/library/argparse.html#mutual-exclusion).
            # Since nested models result in a group add, raise an exception for nested models in a mutually
            # exclusive group.
            raise SettingsError('cannot have nested models in a CliMutuallyExclusiveGroup')

        model_group: Any = None
        model_group_kwargs: dict[str, Any] = {}
        model_group_kwargs['title'] = f'{arg_names[0]} options'
        model_group_kwargs['description'] = field_info.description
        model_group_kwargs['required'] = kwargs['required']
        model_group_kwargs['_is_cli_mutually_exclusive_group'] = any(
            issubclass(model, CliMutuallyExclusiveGroup) for model in sub_models
        )
        if model_group_kwargs['_is_cli_mutually_exclusive_group'] and len(sub_models) > 1:
            raise SettingsError('cannot use union with CliMutuallyExclusiveGroup')
        if self.cli_use_class_docs_for_groups and len(sub_models) == 1:
            model_group_kwargs['description'] = None if sub_models[0].__doc__ is None else dedent(sub_models[0].__doc__)

        if model_default is not PydanticUndefined:
            if is_model_class(type(model_default)) or is_pydantic_dataclass(type(model_default)):
                model_default = getattr(model_default, field_name)
        else:
            if field_info.default is not PydanticUndefined:
                model_default = field_info.default
            elif field_info.default_factory is not None:
                model_default = field_info.default_factory
        if model_default is None:
            desc_header = f'default: {self.cli_parse_none_str} (undefined)'
            if model_group_kwargs['description'] is not None:
                model_group_kwargs['description'] = dedent(f'{desc_header}\n{model_group_kwargs["description"]}')
            else:
                model_group_kwargs['description'] = desc_header

        preferred_alias = alias_names[0]
        if not self.cli_avoid_json:
            added_args.append(arg_names[0])
            kwargs['help'] = f'set {arg_names[0]} from JSON string'
            model_group = self._add_group(parser, **model_group_kwargs)
            self._add_argument(model_group, *(f'{flag_prefix}{name}' for name in arg_names), **kwargs)
        for model in sub_models:
            self._add_parser_args(
                parser=parser,
                model=model,
                added_args=added_args,
                arg_prefix=f'{arg_prefix}{preferred_alias}.',
                subcommand_prefix=subcommand_prefix,
                group=model_group if model_group else model_group_kwargs,
                alias_prefixes=[f'{arg_prefix}{name}.' for name in alias_names[1:]],
                model_default=model_default,
            )

    def _add_parser_alias_paths(
        self,
        parser: Any,
        alias_path_args: dict[str, str],
        added_args: list[str],
        arg_prefix: str,
        subcommand_prefix: str,
        group: Any,
    ) -> None:
        if alias_path_args:
            context = parser
            if group is not None:
                context = self._add_group(parser, **group) if isinstance(group, dict) else group
            is_nested_alias_path = arg_prefix.endswith('.')
            arg_prefix = arg_prefix[:-1] if is_nested_alias_path else arg_prefix
            for name, metavar in alias_path_args.items():
                name = '' if is_nested_alias_path else name
                arg_name = (
                    f'{arg_prefix}{name}'
                    if subcommand_prefix == self.env_prefix
                    else f'{arg_prefix.replace(subcommand_prefix, "", 1)}{name}'
                )
                kwargs: dict[str, Any] = {}
                kwargs['default'] = CLI_SUPPRESS
                kwargs['help'] = 'pydantic alias path'
                kwargs['dest'] = f'{arg_prefix}{name}'
                if metavar == 'dict' or is_nested_alias_path:
                    kwargs['metavar'] = 'dict'
                else:
                    kwargs['action'] = 'append'
                    kwargs['metavar'] = 'list'
                if arg_name not in added_args:
                    added_args.append(arg_name)
                    self._add_argument(context, f'{self._cli_flag_prefix}{arg_name}', **kwargs)

    def _get_modified_args(self, obj: Any) -> tuple[str, ...]:
        if not self.cli_hide_none_type:
            return get_args(obj)
        else:
            return tuple([type_ for type_ in get_args(obj) if type_ is not type(None)])

    def _metavar_format_choices(self, args: list[str], obj_qualname: str | None = None) -> str:
        if 'JSON' in args:
            args = args[: args.index('JSON') + 1] + [arg for arg in args[args.index('JSON') + 1 :] if arg != 'JSON']
        metavar = ','.join(args)
        if obj_qualname:
            return f'{obj_qualname}[{metavar}]'
        else:
            return metavar if len(args) == 1 else f'{{{metavar}}}'

    def _metavar_format_recurse(self, obj: Any) -> str:
        """Pretty metavar representation of a type. Adapts logic from `pydantic._repr.display_as_type`."""
        obj = _strip_annotated(obj)
        if _is_function(obj):
            # If function is locally defined use __name__ instead of __qualname__
            return obj.__name__ if '<locals>' in obj.__qualname__ else obj.__qualname__
        elif obj is ...:
            return '...'
        elif isinstance(obj, Representation):
            return repr(obj)
        elif isinstance(obj, typing_extensions.TypeAliasType):
            return str(obj)

        if not isinstance(obj, (typing_base, WithArgsTypes, type)):
            obj = obj.__class__

        if origin_is_union(get_origin(obj)):
            return self._metavar_format_choices(list(map(self._metavar_format_recurse, self._get_modified_args(obj))))
        elif get_origin(obj) in (typing_extensions.Literal, typing.Literal):
            return self._metavar_format_choices(list(map(str, self._get_modified_args(obj))))
        elif lenient_issubclass(obj, Enum):
            return self._metavar_format_choices([val.name for val in obj])
        elif isinstance(obj, WithArgsTypes):
            return self._metavar_format_choices(
                list(map(self._metavar_format_recurse, self._get_modified_args(obj))),
                obj_qualname=obj.__qualname__ if hasattr(obj, '__qualname__') else str(obj),
            )
        elif obj is type(None):
            return self.cli_parse_none_str
        elif is_model_class(obj):
            return 'JSON'
        elif isinstance(obj, type):
            return obj.__qualname__
        else:
            return repr(obj).replace('typing.', '').replace('typing_extensions.', '')

    def _metavar_format(self, obj: Any) -> str:
        return self._metavar_format_recurse(obj).replace(', ', ',')

    def _help_format(self, field_name: str, field_info: FieldInfo, model_default: Any) -> str:
        _help = field_info.description if field_info.description else ''
        if _help == CLI_SUPPRESS or CLI_SUPPRESS in field_info.metadata:
            return CLI_SUPPRESS

        if field_info.is_required() and model_default in (PydanticUndefined, None):
            if _CliPositionalArg not in field_info.metadata:
                ifdef = 'ifdef: ' if model_default is None else ''
                _help += f' ({ifdef}required)' if _help else f'({ifdef}required)'
        else:
            default = f'(default: {self.cli_parse_none_str})'
            if is_model_class(type(model_default)) or is_pydantic_dataclass(type(model_default)):
                default = f'(default: {getattr(model_default, field_name)})'
            elif model_default not in (PydanticUndefined, None) and _is_function(model_default):
                default = f'(default factory: {self._metavar_format(model_default)})'
            elif field_info.default not in (PydanticUndefined, None):
                enum_name = _annotation_enum_val_to_name(field_info.annotation, field_info.default)
                default = f'(default: {field_info.default if enum_name is None else enum_name})'
            elif field_info.default_factory is not None:
                default = f'(default factory: {self._metavar_format(field_info.default_factory)})'
            _help += f' {default}' if _help else default
        return _help.replace('%', '%%') if issubclass(type(self._root_parser), ArgumentParser) else _help


class ConfigFileSourceMixin(ABC):
    def _read_files(self, files: PathType | None) -> dict[str, Any]:
        if files is None:
            return {}
        if isinstance(files, (str, os.PathLike)):
            files = [files]
        vars: dict[str, Any] = {}
        for file in files:
            file_path = Path(file).expanduser()
            if file_path.is_file():
                vars.update(self._read_file(file_path))
        return vars

    @abstractmethod
    def _read_file(self, path: Path) -> dict[str, Any]:
        pass


class JsonConfigSettingsSource(InitSettingsSource, ConfigFileSourceMixin):
    """
    A source class that loads variables from a JSON file
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        json_file: PathType | None = DEFAULT_PATH,
        json_file_encoding: str | None = None,
    ):
        self.json_file_path = json_file if json_file != DEFAULT_PATH else settings_cls.model_config.get('json_file')
        self.json_file_encoding = (
            json_file_encoding
            if json_file_encoding is not None
            else settings_cls.model_config.get('json_file_encoding')
        )
        self.json_data = self._read_files(self.json_file_path)
        super().__init__(settings_cls, self.json_data)

    def _read_file(self, file_path: Path) -> dict[str, Any]:
        with open(file_path, encoding=self.json_file_encoding) as json_file:
            return json.load(json_file)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(json_file={self.json_file_path})'


class TomlConfigSettingsSource(InitSettingsSource, ConfigFileSourceMixin):
    """
    A source class that loads variables from a TOML file
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        toml_file: PathType | None = DEFAULT_PATH,
    ):
        self.toml_file_path = toml_file if toml_file != DEFAULT_PATH else settings_cls.model_config.get('toml_file')
        self.toml_data = self._read_files(self.toml_file_path)
        super().__init__(settings_cls, self.toml_data)

    def _read_file(self, file_path: Path) -> dict[str, Any]:
        import_toml()
        with open(file_path, mode='rb') as toml_file:
            if sys.version_info < (3, 11):
                return tomli.load(toml_file)
            return tomllib.load(toml_file)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(toml_file={self.toml_file_path})'


class PyprojectTomlConfigSettingsSource(TomlConfigSettingsSource):
    """
    A source class that loads variables from a `pyproject.toml` file.
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        toml_file: Path | None = None,
    ) -> None:
        self.toml_file_path = self._pick_pyproject_toml_file(
            toml_file, settings_cls.model_config.get('pyproject_toml_depth', 0)
        )
        self.toml_table_header: tuple[str, ...] = settings_cls.model_config.get(
            'pyproject_toml_table_header', ('tool', 'pydantic-settings')
        )
        self.toml_data = self._read_files(self.toml_file_path)
        for key in self.toml_table_header:
            self.toml_data = self.toml_data.get(key, {})
        super(TomlConfigSettingsSource, self).__init__(settings_cls, self.toml_data)

    @staticmethod
    def _pick_pyproject_toml_file(provided: Path | None, depth: int) -> Path:
        """Pick a `pyproject.toml` file path to use.

        Args:
            provided: Explicit path provided when instantiating this class.
            depth: Number of directories up the tree to check of a pyproject.toml.

        """
        if provided:
            return provided.resolve()
        rv = Path.cwd() / 'pyproject.toml'
        count = 0
        if not rv.is_file():
            child = rv.parent.parent / 'pyproject.toml'
            while count < depth:
                if child.is_file():
                    return child
                if str(child.parent) == rv.root:
                    break  # end discovery after checking system root once
                child = child.parent.parent / 'pyproject.toml'
                count += 1
        return rv


class YamlConfigSettingsSource(InitSettingsSource, ConfigFileSourceMixin):
    """
    A source class that loads variables from a yaml file
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        yaml_file: PathType | None = DEFAULT_PATH,
        yaml_file_encoding: str | None = None,
    ):
        self.yaml_file_path = yaml_file if yaml_file != DEFAULT_PATH else settings_cls.model_config.get('yaml_file')
        self.yaml_file_encoding = (
            yaml_file_encoding
            if yaml_file_encoding is not None
            else settings_cls.model_config.get('yaml_file_encoding')
        )
        self.yaml_data = self._read_files(self.yaml_file_path)
        super().__init__(settings_cls, self.yaml_data)

    def _read_file(self, file_path: Path) -> dict[str, Any]:
        import_yaml()
        with open(file_path, encoding=self.yaml_file_encoding) as yaml_file:
            return yaml.safe_load(yaml_file) or {}

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(yaml_file={self.yaml_file_path})'


class AzureKeyVaultMapping(Mapping[str, Optional[str]]):
    _loaded_secrets: dict[str, str | None]
    _secret_client: SecretClient  # type: ignore
    _secret_names: list[str]

    def __init__(
        self,
        secret_client: SecretClient,  # type: ignore
    ) -> None:
        self._loaded_secrets = {}
        self._secret_client = secret_client
        self._secret_names: list[str] = [secret.name for secret in self._secret_client.list_properties_of_secrets()]

    def __getitem__(self, key: str) -> str | None:
        if key not in self._loaded_secrets:
            try:
                self._loaded_secrets[key] = self._secret_client.get_secret(key).value
            except Exception:
                raise KeyError(key)

        return self._loaded_secrets[key]

    def __len__(self) -> int:
        return len(self._secret_names)

    def __iter__(self) -> Iterator[str]:
        return iter(self._secret_names)


class AzureKeyVaultSettingsSource(EnvSettingsSource):
    _url: str
    _credential: TokenCredential  # type: ignore
    _secret_client: SecretClient  # type: ignore

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        url: str,
        credential: TokenCredential,  # type: ignore
        env_prefix: str | None = None,
        env_parse_none_str: str | None = None,
        env_parse_enums: bool | None = None,
    ) -> None:
        import_azure_key_vault()
        self._url = url
        self._credential = credential
        super().__init__(
            settings_cls,
            case_sensitive=True,
            env_prefix=env_prefix,
            env_nested_delimiter='--',
            env_ignore_empty=False,
            env_parse_none_str=env_parse_none_str,
            env_parse_enums=env_parse_enums,
        )

    def _load_env_vars(self) -> Mapping[str, Optional[str]]:
        secret_client = SecretClient(vault_url=self._url, credential=self._credential)  # type: ignore
        return AzureKeyVaultMapping(secret_client)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(url={self._url!r}, ' f'env_nested_delimiter={self.env_nested_delimiter!r})'


def _get_env_var_key(key: str, case_sensitive: bool = False) -> str:
    return key if case_sensitive else key.lower()


def _parse_env_none_str(value: str | None, parse_none_str: str | None = None) -> str | None | EnvNoneType:
    return value if not (value == parse_none_str and parse_none_str is not None) else EnvNoneType(value)


def parse_env_vars(
    env_vars: Mapping[str, str | None],
    case_sensitive: bool = False,
    ignore_empty: bool = False,
    parse_none_str: str | None = None,
) -> Mapping[str, str | None]:
    return {
        _get_env_var_key(k, case_sensitive): _parse_env_none_str(v, parse_none_str)
        for k, v in env_vars.items()
        if not (ignore_empty and v == '')
    }


def read_env_file(
    file_path: Path,
    *,
    encoding: str | None = None,
    case_sensitive: bool = False,
    ignore_empty: bool = False,
    parse_none_str: str | None = None,
) -> Mapping[str, str | None]:
    warnings.warn(
        'read_env_file will be removed in the next version, use DotEnvSettingsSource._static_read_env_file if you must',
        DeprecationWarning,
    )
    return DotEnvSettingsSource._static_read_env_file(
        file_path,
        encoding=encoding,
        case_sensitive=case_sensitive,
        ignore_empty=ignore_empty,
        parse_none_str=parse_none_str,
    )


def _annotation_is_complex(annotation: type[Any] | None, metadata: list[Any]) -> bool:
    # If the model is a root model, the root annotation should be used to
    # evaluate the complexity.
    try:
        if annotation is not None and issubclass(annotation, RootModel):
            # In some rare cases (see test_root_model_as_field),
            # the root attribute is not available. For these cases, python 3.8 and 3.9
            # return 'RootModelRootType'.
            root_annotation = annotation.__annotations__.get('root', None)
            if root_annotation is not None and root_annotation != 'RootModelRootType':
                annotation = root_annotation
    except TypeError:
        pass

    if any(isinstance(md, Json) for md in metadata):  # type: ignore[misc]
        return False
    # Check if annotation is of the form Annotated[type, metadata].
    if isinstance(annotation, _AnnotatedAlias):
        # Return result of recursive call on inner type.
        inner, *meta = get_args(annotation)
        return _annotation_is_complex(inner, meta)
    origin = get_origin(annotation)

    if origin is Secret:
        return False

    return (
        _annotation_is_complex_inner(annotation)
        or _annotation_is_complex_inner(origin)
        or hasattr(origin, '__pydantic_core_schema__')
        or hasattr(origin, '__get_pydantic_core_schema__')
    )


def _annotation_is_complex_inner(annotation: type[Any] | None) -> bool:
    if lenient_issubclass(annotation, (str, bytes)):
        return False

    return lenient_issubclass(annotation, (BaseModel, Mapping, Sequence, tuple, set, frozenset, deque)) or is_dataclass(
        annotation
    )


def _union_is_complex(annotation: type[Any] | None, metadata: list[Any]) -> bool:
    return any(_annotation_is_complex(arg, metadata) for arg in get_args(annotation))


def _annotation_contains_types(
    annotation: type[Any] | None,
    types: tuple[Any, ...],
    is_include_origin: bool = True,
    is_strip_annotated: bool = False,
) -> bool:
    if is_strip_annotated:
        annotation = _strip_annotated(annotation)
    if is_include_origin is True and get_origin(annotation) in types:
        return True
    for type_ in get_args(annotation):
        if _annotation_contains_types(type_, types, is_include_origin=True, is_strip_annotated=is_strip_annotated):
            return True
    return annotation in types


def _strip_annotated(annotation: Any) -> Any:
    while get_origin(annotation) == Annotated:
        annotation = get_args(annotation)[0]
    return annotation


def _annotation_enum_val_to_name(annotation: type[Any] | None, value: Any) -> Optional[str]:
    for type_ in (annotation, get_origin(annotation), *get_args(annotation)):
        if lenient_issubclass(type_, Enum):
            if value in tuple(val.value for val in type_):
                return type_(value).name
    return None


def _annotation_enum_name_to_val(annotation: type[Any] | None, name: Any) -> Any:
    for type_ in (annotation, get_origin(annotation), *get_args(annotation)):
        if lenient_issubclass(type_, Enum):
            if name in tuple(val.name for val in type_):
                return type_[name]
    return None


def _get_model_fields(model_cls: type[Any]) -> dict[str, FieldInfo]:
    if is_pydantic_dataclass(model_cls) and hasattr(model_cls, '__pydantic_fields__'):
        return model_cls.__pydantic_fields__
    if is_model_class(model_cls):
        return model_cls.model_fields
    raise SettingsError(f'Error: {model_cls.__name__} is not subclass of BaseModel or pydantic.dataclasses.dataclass')


def _get_alias_names(
    field_name: str, field_info: FieldInfo, alias_path_args: dict[str, str] = {}, case_sensitive: bool = True
) -> tuple[tuple[str, ...], bool]:
    alias_names: list[str] = []
    is_alias_path_only: bool = True
    if not any((field_info.alias, field_info.validation_alias)):
        alias_names += [field_name]
        is_alias_path_only = False
    else:
        new_alias_paths: list[AliasPath] = []
        for alias in (field_info.alias, field_info.validation_alias):
            if alias is None:
                continue
            elif isinstance(alias, str):
                alias_names.append(alias)
                is_alias_path_only = False
            elif isinstance(alias, AliasChoices):
                for name in alias.choices:
                    if isinstance(name, str):
                        alias_names.append(name)
                        is_alias_path_only = False
                    else:
                        new_alias_paths.append(name)
            else:
                new_alias_paths.append(alias)
        for alias_path in new_alias_paths:
            name = cast(str, alias_path.path[0])
            name = name.lower() if not case_sensitive else name
            alias_path_args[name] = 'dict' if len(alias_path.path) > 2 else 'list'
            if not alias_names and is_alias_path_only:
                alias_names.append(name)
    if not case_sensitive:
        alias_names = [alias_name.lower() for alias_name in alias_names]
    return tuple(dict.fromkeys(alias_names)), is_alias_path_only


def _is_function(obj: Any) -> bool:
    return isinstance(obj, (FunctionType, BuiltinFunctionType))
