from __future__ import annotations

import json

from importlib.resources import files
from typing import Any

import fastjsonschema

from fastjsonschema.exceptions import JsonSchemaValueException


def validate_object(obj: dict[str, Any]) -> list[str]:
    schema = json.loads(
        (files(__package__) / "schemas" / "poetry.json").read_text(encoding="utf-8")
    )

    validate = fastjsonschema.compile(schema)

    errors = []
    try:
        validate(obj)
    except JsonSchemaValueException as e:
        errors = [e.message]

    core_schema = json.loads(
        (files("poetry.core") / "json" / "schemas" / "poetry-schema.json").read_text(
            encoding="utf-8"
        )
    )

    properties = schema["properties"].keys() | core_schema["properties"].keys()
    additional_properties = obj.keys() - properties
    for key in additional_properties:
        errors.append(f"Additional properties are not allowed ('{key}' was unexpected)")

    return errors
