import types
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    AbstractSet,
    Any,
    Callable,
    Dict,
    ForwardRef,
    Generator,
    Mapping,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)

from pydantic import VERSION as P_VERSION
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from typing_extensions import Annotated, get_args, get_origin

# Reassign variable to make it reexported for mypy
PYDANTIC_VERSION = P_VERSION
PYDANTIC_MINOR_VERSION = tuple(int(i) for i in P_VERSION.split(".")[:2])
IS_PYDANTIC_V2 = PYDANTIC_MINOR_VERSION[0] == 2


if TYPE_CHECKING:
    from .main import RelationshipInfo, SQLModel

UnionType = getattr(types, "UnionType", Union)
NoneType = type(None)
T = TypeVar("T")
InstanceOrType = Union[T, Type[T]]
_TSQLModel = TypeVar("_TSQLModel", bound="SQLModel")


class FakeMetadata:
    max_length: Optional[int] = None
    max_digits: Optional[int] = None
    decimal_places: Optional[int] = None


@dataclass
class ObjectWithUpdateWrapper:
    obj: Any
    update: Dict[str, Any]

    def __getattribute__(self, __name: str) -> Any:
        update = super().__getattribute__("update")
        obj = super().__getattribute__("obj")
        if __name in update:
            return update[__name]
        return getattr(obj, __name)


def _is_union_type(t: Any) -> bool:
    return t is UnionType or t is Union


finish_init: ContextVar[bool] = ContextVar("finish_init", default=True)


@contextmanager
def partial_init() -> Generator[None, None, None]:
    token = finish_init.set(False)
    yield
    finish_init.reset(token)


if IS_PYDANTIC_V2:
    from annotated_types import MaxLen
    from pydantic import ConfigDict as BaseConfig
    from pydantic._internal._fields import PydanticMetadata
    from pydantic._internal._model_construction import ModelMetaclass
    from pydantic._internal._repr import Representation as Representation
    from pydantic_core import PydanticUndefined as Undefined
    from pydantic_core import PydanticUndefinedType as UndefinedType

    # Dummy for types, to make it importable
    class ModelField:
        pass

    class SQLModelConfig(BaseConfig, total=False):
        table: Optional[bool]
        registry: Optional[Any]

    def get_config_value(
        *, model: InstanceOrType["SQLModel"], parameter: str, default: Any = None
    ) -> Any:
        return model.model_config.get(parameter, default)

    def set_config_value(
        *,
        model: InstanceOrType["SQLModel"],
        parameter: str,
        value: Any,
    ) -> None:
        model.model_config[parameter] = value  # type: ignore[literal-required]

    def get_model_fields(model: InstanceOrType[BaseModel]) -> Dict[str, "FieldInfo"]:
        # TODO: refactor the usage of this function to always pass the class
        # not the instance, and then remove this extra check
        # this is for compatibility with Pydantic v3
        if isinstance(model, type):
            use_model = model
        else:
            use_model = model.__class__
        return use_model.model_fields

    def get_fields_set(
        object: InstanceOrType["SQLModel"],
    ) -> Union[Set[str], Callable[[BaseModel], Set[str]]]:
        return object.model_fields_set

    def init_pydantic_private_attrs(new_object: InstanceOrType["SQLModel"]) -> None:
        object.__setattr__(new_object, "__pydantic_fields_set__", set())
        object.__setattr__(new_object, "__pydantic_extra__", None)
        object.__setattr__(new_object, "__pydantic_private__", None)

    def get_annotations(class_dict: Dict[str, Any]) -> Dict[str, Any]:
        return class_dict.get("__annotations__", {})

    def is_table_model_class(cls: Type[Any]) -> bool:
        config = getattr(cls, "model_config", {})
        if config:
            return config.get("table", False) or False
        return False

    def get_relationship_to(
        name: str,
        rel_info: "RelationshipInfo",
        annotation: Any,
    ) -> Any:
        origin = get_origin(annotation)
        use_annotation = annotation
        # Direct relationships (e.g. 'Team' or Team) have None as an origin
        if origin is None:
            if isinstance(use_annotation, ForwardRef):
                use_annotation = use_annotation.__forward_arg__
            else:
                return use_annotation
        # If Union (e.g. Optional), get the real field
        elif _is_union_type(origin):
            use_annotation = get_args(annotation)
            if len(use_annotation) > 2:
                raise ValueError(
                    "Cannot have a (non-optional) union as a SQLAlchemy field"
                )
            arg1, arg2 = use_annotation
            if arg1 is NoneType and arg2 is not NoneType:
                use_annotation = arg2
            elif arg2 is NoneType and arg1 is not NoneType:
                use_annotation = arg1
            else:
                raise ValueError(
                    "Cannot have a Union of None and None as a SQLAlchemy field"
                )

        # If a list, then also get the real field
        elif origin is list:
            use_annotation = get_args(annotation)[0]

        return get_relationship_to(
            name=name, rel_info=rel_info, annotation=use_annotation
        )

    def is_field_noneable(field: "FieldInfo") -> bool:
        if getattr(field, "nullable", Undefined) is not Undefined:
            return field.nullable  # type: ignore
        origin = get_origin(field.annotation)
        if origin is not None and _is_union_type(origin):
            args = get_args(field.annotation)
            if any(arg is NoneType for arg in args):
                return True
        if not field.is_required():
            if field.default is Undefined:
                return False
            if field.annotation is None or field.annotation is NoneType:  # type: ignore[comparison-overlap]
                return True
            return False
        return False

    def get_sa_type_from_type_annotation(annotation: Any) -> Any:
        # Resolve Optional fields
        if annotation is None:
            raise ValueError("Missing field type")
        origin = get_origin(annotation)
        if origin is None:
            return annotation
        elif origin is Annotated:
            return get_sa_type_from_type_annotation(get_args(annotation)[0])
        if _is_union_type(origin):
            bases = get_args(annotation)
            if len(bases) > 2:
                raise ValueError(
                    "Cannot have a (non-optional) union as a SQLAlchemy field"
                )
            # Non optional unions are not allowed
            if bases[0] is not NoneType and bases[1] is not NoneType:
                raise ValueError(
                    "Cannot have a (non-optional) union as a SQLAlchemy field"
                )
            # Optional unions are allowed
            use_type = bases[0] if bases[0] is not NoneType else bases[1]
            return get_sa_type_from_type_annotation(use_type)
        return origin

    def get_sa_type_from_field(field: Any) -> Any:
        type_: Any = field.annotation
        return get_sa_type_from_type_annotation(type_)

    def get_field_metadata(field: Any) -> Any:
        for meta in field.metadata:
            if isinstance(meta, (PydanticMetadata, MaxLen)):
                return meta
        return FakeMetadata()

    def post_init_field_info(field_info: FieldInfo) -> None:
        return None

    # Dummy to make it importable
    def _calculate_keys(
        self: "SQLModel",
        include: Optional[Mapping[Union[int, str], Any]],
        exclude: Optional[Mapping[Union[int, str], Any]],
        exclude_unset: bool,
        update: Optional[Dict[str, Any]] = None,
    ) -> Optional[AbstractSet[str]]:  # pragma: no cover
        return None

    def sqlmodel_table_construct(
        *,
        self_instance: _TSQLModel,
        values: Dict[str, Any],
        _fields_set: Union[Set[str], None] = None,
    ) -> _TSQLModel:
        # Copy from Pydantic's BaseModel.construct()
        # Ref: https://github.com/pydantic/pydantic/blob/v2.5.2/pydantic/main.py#L198
        # Modified to not include everything, only the model fields, and to
        # set relationships
        # SQLModel override to get class SQLAlchemy __dict__ attributes and
        # set them back in after creating the object
        # new_obj = cls.__new__(cls)
        cls = type(self_instance)
        old_dict = self_instance.__dict__.copy()
        # End SQLModel override

        fields_values: Dict[str, Any] = {}
        defaults: Dict[
            str, Any
        ] = {}  # keeping this separate from `fields_values` helps us compute `_fields_set`
        for name, field in cls.model_fields.items():
            if field.alias and field.alias in values:
                fields_values[name] = values.pop(field.alias)
            elif name in values:
                fields_values[name] = values.pop(name)
            elif not field.is_required():
                defaults[name] = field.get_default(call_default_factory=True)
        if _fields_set is None:
            _fields_set = set(fields_values.keys())
        fields_values.update(defaults)

        _extra: Union[Dict[str, Any], None] = None
        if cls.model_config.get("extra") == "allow":
            _extra = {}
            for k, v in values.items():
                _extra[k] = v
        # SQLModel override, do not include everything, only the model fields
        # else:
        #     fields_values.update(values)
        # End SQLModel override
        # SQLModel override
        # Do not set __dict__, instead use setattr to trigger SQLAlchemy
        # object.__setattr__(new_obj, "__dict__", fields_values)
        # instrumentation
        for key, value in {**old_dict, **fields_values}.items():
            setattr(self_instance, key, value)
        # End SQLModel override
        object.__setattr__(self_instance, "__pydantic_fields_set__", _fields_set)
        if not cls.__pydantic_root_model__:
            object.__setattr__(self_instance, "__pydantic_extra__", _extra)

        if cls.__pydantic_post_init__:
            self_instance.model_post_init(None)
        elif not cls.__pydantic_root_model__:
            # Note: if there are any private attributes, cls.__pydantic_post_init__ would exist
            # Since it doesn't, that means that `__pydantic_private__` should be set to None
            object.__setattr__(self_instance, "__pydantic_private__", None)
        # SQLModel override, set relationships
        # Get and set any relationship objects
        for key in self_instance.__sqlmodel_relationships__:
            value = values.get(key, Undefined)
            if value is not Undefined:
                setattr(self_instance, key, value)
        # End SQLModel override
        return self_instance

    def sqlmodel_validate(
        cls: Type[_TSQLModel],
        obj: Any,
        *,
        strict: Union[bool, None] = None,
        from_attributes: Union[bool, None] = None,
        context: Union[Dict[str, Any], None] = None,
        update: Union[Dict[str, Any], None] = None,
    ) -> _TSQLModel:
        if not is_table_model_class(cls):
            new_obj: _TSQLModel = cls.__new__(cls)
        else:
            # If table, create the new instance normally to make SQLAlchemy create
            # the _sa_instance_state attribute
            # The wrapper of this function should use with _partial_init()
            with partial_init():
                new_obj = cls()
        # SQLModel Override to get class SQLAlchemy __dict__ attributes and
        # set them back in after creating the object
        old_dict = new_obj.__dict__.copy()
        use_obj = obj
        if isinstance(obj, dict) and update:
            use_obj = {**obj, **update}
        elif update:
            use_obj = ObjectWithUpdateWrapper(obj=obj, update=update)
        cls.__pydantic_validator__.validate_python(
            use_obj,
            strict=strict,
            from_attributes=from_attributes,
            context=context,
            self_instance=new_obj,
        )
        # Capture fields set to restore it later
        fields_set = new_obj.__pydantic_fields_set__.copy()
        if not is_table_model_class(cls):
            # If not table, normal Pydantic code, set __dict__
            new_obj.__dict__ = {**old_dict, **new_obj.__dict__}
        else:
            # Do not set __dict__, instead use setattr to trigger SQLAlchemy
            # instrumentation
            for key, value in {**old_dict, **new_obj.__dict__}.items():
                setattr(new_obj, key, value)
        # Restore fields set
        object.__setattr__(new_obj, "__pydantic_fields_set__", fields_set)
        # Get and set any relationship objects
        if is_table_model_class(cls):
            for key in new_obj.__sqlmodel_relationships__:
                value = getattr(use_obj, key, Undefined)
                if value is not Undefined:
                    setattr(new_obj, key, value)
        return new_obj

    def sqlmodel_init(*, self: "SQLModel", data: Dict[str, Any]) -> None:
        old_dict = self.__dict__.copy()
        if not is_table_model_class(self.__class__):
            self.__pydantic_validator__.validate_python(
                data,
                self_instance=self,
            )
        else:
            sqlmodel_table_construct(
                self_instance=self,
                values=data,
            )
        object.__setattr__(
            self,
            "__dict__",
            {**old_dict, **self.__dict__},
        )

else:
    from pydantic import BaseConfig as BaseConfig  # type: ignore[assignment]
    from pydantic.errors import ConfigError
    from pydantic.fields import (  # type: ignore[attr-defined, no-redef]
        SHAPE_SINGLETON,
        ModelField,
    )
    from pydantic.fields import (  # type: ignore[attr-defined, no-redef]
        Undefined as Undefined,  # noqa
    )
    from pydantic.fields import (  # type: ignore[attr-defined, no-redef]
        UndefinedType as UndefinedType,
    )
    from pydantic.main import (  # type: ignore[no-redef]
        ModelMetaclass as ModelMetaclass,
    )
    from pydantic.main import validate_model
    from pydantic.typing import resolve_annotations
    from pydantic.utils import ROOT_KEY, ValueItems
    from pydantic.utils import (  # type: ignore[no-redef]
        Representation as Representation,
    )

    class SQLModelConfig(BaseConfig):  # type: ignore[no-redef]
        table: Optional[bool] = None  # type: ignore[misc]
        registry: Optional[Any] = None  # type: ignore[misc]

    def get_config_value(
        *, model: InstanceOrType["SQLModel"], parameter: str, default: Any = None
    ) -> Any:
        return getattr(model.__config__, parameter, default)  # type: ignore[union-attr]

    def set_config_value(
        *,
        model: InstanceOrType["SQLModel"],
        parameter: str,
        value: Any,
    ) -> None:
        setattr(model.__config__, parameter, value)  # type: ignore

    def get_model_fields(model: InstanceOrType[BaseModel]) -> Dict[str, "FieldInfo"]:
        return model.__fields__  # type: ignore

    def get_fields_set(
        object: InstanceOrType["SQLModel"],
    ) -> Union[Set[str], Callable[[BaseModel], Set[str]]]:
        return object.__fields_set__

    def init_pydantic_private_attrs(new_object: InstanceOrType["SQLModel"]) -> None:
        object.__setattr__(new_object, "__fields_set__", set())

    def get_annotations(class_dict: Dict[str, Any]) -> Dict[str, Any]:
        return resolve_annotations(  # type: ignore[no-any-return]
            class_dict.get("__annotations__", {}),
            class_dict.get("__module__", None),
        )

    def is_table_model_class(cls: Type[Any]) -> bool:
        config = getattr(cls, "__config__", None)
        if config:
            return getattr(config, "table", False)
        return False

    def get_relationship_to(
        name: str,
        rel_info: "RelationshipInfo",
        annotation: Any,
    ) -> Any:
        temp_field = ModelField.infer(  # type: ignore[attr-defined]
            name=name,
            value=rel_info,
            annotation=annotation,
            class_validators=None,
            config=SQLModelConfig,
        )
        relationship_to = temp_field.type_
        if isinstance(temp_field.type_, ForwardRef):
            relationship_to = temp_field.type_.__forward_arg__
        return relationship_to

    def is_field_noneable(field: "FieldInfo") -> bool:
        if not field.required:  # type: ignore[attr-defined]
            # Taken from [Pydantic](https://github.com/samuelcolvin/pydantic/blob/v1.8.2/pydantic/fields.py#L946-L947)
            return field.allow_none and (  # type: ignore[attr-defined]
                field.shape != SHAPE_SINGLETON or not field.sub_fields  # type: ignore[attr-defined]
            )
        return field.allow_none  # type: ignore[no-any-return, attr-defined]

    def get_sa_type_from_field(field: Any) -> Any:
        if isinstance(field.type_, type) and field.shape == SHAPE_SINGLETON:
            return field.type_
        raise ValueError(f"The field {field.name} has no matching SQLAlchemy type")

    def get_field_metadata(field: Any) -> Any:
        metadata = FakeMetadata()
        metadata.max_length = field.field_info.max_length
        metadata.max_digits = getattr(field.type_, "max_digits", None)
        metadata.decimal_places = getattr(field.type_, "decimal_places", None)
        return metadata

    def post_init_field_info(field_info: FieldInfo) -> None:
        field_info._validate()  # type: ignore[attr-defined]

    def _calculate_keys(
        self: "SQLModel",
        include: Optional[Mapping[Union[int, str], Any]],
        exclude: Optional[Mapping[Union[int, str], Any]],
        exclude_unset: bool,
        update: Optional[Dict[str, Any]] = None,
    ) -> Optional[AbstractSet[str]]:
        if include is None and exclude is None and not exclude_unset:
            # Original in Pydantic:
            # return None
            # Updated to not return SQLAlchemy attributes
            # Do not include relationships as that would easily lead to infinite
            # recursion, or traversing the whole database
            return (
                self.__fields__.keys()  # noqa
            )  # | self.__sqlmodel_relationships__.keys()

        keys: AbstractSet[str]
        if exclude_unset:
            keys = self.__fields_set__.copy()  # noqa
        else:
            # Original in Pydantic:
            # keys = self.__dict__.keys()
            # Updated to not return SQLAlchemy attributes
            # Do not include relationships as that would easily lead to infinite
            # recursion, or traversing the whole database
            keys = (
                self.__fields__.keys()  # noqa
            )  # | self.__sqlmodel_relationships__.keys()
        if include is not None:
            keys &= include.keys()

        if update:
            keys -= update.keys()

        if exclude:
            keys -= {k for k, v in exclude.items() if ValueItems.is_true(v)}

        return keys

    def sqlmodel_validate(
        cls: Type[_TSQLModel],
        obj: Any,
        *,
        strict: Union[bool, None] = None,
        from_attributes: Union[bool, None] = None,
        context: Union[Dict[str, Any], None] = None,
        update: Union[Dict[str, Any], None] = None,
    ) -> _TSQLModel:
        # This was SQLModel's original from_orm() for Pydantic v1
        # Duplicated from Pydantic
        if not cls.__config__.orm_mode:  # type: ignore[attr-defined] # noqa
            raise ConfigError(
                "You must have the config attribute orm_mode=True to use from_orm"
            )
        if not isinstance(obj, Mapping):
            obj = (
                {ROOT_KEY: obj}
                if cls.__custom_root_type__  # type: ignore[attr-defined] # noqa
                else cls._decompose_class(obj)  # type: ignore[attr-defined] # noqa
            )
        # SQLModel, support update dict
        if update is not None:
            obj = {**obj, **update}
        # End SQLModel support dict
        if not getattr(cls.__config__, "table", False):  # noqa
            # If not table, normal Pydantic code
            m: _TSQLModel = cls.__new__(cls)
        else:
            # If table, create the new instance normally to make SQLAlchemy create
            # the _sa_instance_state attribute
            m = cls()
        values, fields_set, validation_error = validate_model(cls, obj)
        if validation_error:
            raise validation_error
        # Updated to trigger SQLAlchemy internal handling
        if not getattr(cls.__config__, "table", False):  # noqa
            object.__setattr__(m, "__dict__", values)
        else:
            for key, value in values.items():
                setattr(m, key, value)
        # Continue with standard Pydantic logic
        object.__setattr__(m, "__fields_set__", fields_set)
        m._init_private_attributes()  # type: ignore[attr-defined] # noqa
        return m

    def sqlmodel_init(*, self: "SQLModel", data: Dict[str, Any]) -> None:
        values, fields_set, validation_error = validate_model(self.__class__, data)
        # Only raise errors if not a SQLModel model
        if (
            not is_table_model_class(self.__class__)  # noqa
            and validation_error
        ):
            raise validation_error
        if not is_table_model_class(self.__class__):
            object.__setattr__(self, "__dict__", values)
        else:
            # Do not set values as in Pydantic, pass them through setattr, so
            # SQLAlchemy can handle them
            for key, value in values.items():
                setattr(self, key, value)
        object.__setattr__(self, "__fields_set__", fields_set)
        non_pydantic_keys = data.keys() - values.keys()

        if is_table_model_class(self.__class__):
            for key in non_pydantic_keys:
                if key in self.__sqlmodel_relationships__:
                    setattr(self, key, data[key])
