"""
Entity Definition entity for individual entities (tables) in ERD.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldDefinition:
    """Definition of a field in an entity."""

    name: str
    type: str
    constraints: list[str] = field(default_factory=list)
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_nullable: bool = True
    default_value: str | None = None
    description: str | None = None

    def __post_init__(self):
        if self.is_primary_key:
            self.constraints.append("PK")
        if self.is_foreign_key:
            self.constraints.append("FK")
        if not self.is_nullable:
            self.constraints.append("NOT NULL")

    def to_mermaid_field(self) -> str:
        """Convert field to Mermaid ERD field syntax."""
        field_parts = [self.type, self.name]

        if self.constraints:
            constraint_str = " ".join(self.constraints)
            field_parts.append(constraint_str)

        return " ".join(field_parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert field definition to dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "constraints": self.constraints,
            "is_primary_key": self.is_primary_key,
            "is_foreign_key": self.is_foreign_key,
            "is_nullable": self.is_nullable,
            "default_value": self.default_value,
            "description": self.description,
        }


@dataclass
class EntityDefinition:
    """Individual entity (table) definition in ERD."""

    name: str
    fields: list[FieldDefinition]
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Ensure entity name is uppercase for ERD
        self.name = self.name.upper()

    @property
    def primary_key_fields(self) -> list[FieldDefinition]:
        """Get all primary key fields."""
        return [field for field in self.fields if field.is_primary_key]

    @property
    def foreign_key_fields(self) -> list[FieldDefinition]:
        """Get all foreign key fields."""
        return [field for field in self.fields if field.is_foreign_key]

    @property
    def has_relationships(self) -> bool:
        """Check if entity has foreign key relationships."""
        return len(self.foreign_key_fields) > 0

    def get_field_by_name(self, field_name: str) -> FieldDefinition | None:
        """Get a field by its name."""
        for field_def in self.fields:
            if field_def.name == field_name:
                return field_def
        return None

    def add_field(self, field: FieldDefinition) -> None:
        """Add a field to the entity."""
        self.fields.append(field)

    def to_mermaid_entity(self) -> str:
        """Convert entity to Mermaid ERD entity syntax."""
        lines = [f"{self.name} {{"]

        for field_def in self.fields:
            lines.append(f"    {field_def.to_mermaid_field()}")

        lines.append("}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert entity definition to dictionary."""
        return {
            "name": self.name,
            "fields": [field.to_dict() for field in self.fields],
            "description": self.description,
            "metadata": self.metadata,
        }

    @classmethod
    def from_model_metadata(cls, model_metadata) -> "EntityDefinition":
        """Create EntityDefinition from ModelMetadata."""
        fields = []

        for field_meta in model_metadata.fields:
            # Convert type hint to Mermaid type
            mermaid_type = cls._convert_type_to_mermaid(field_meta.type_hint)

            field_def = FieldDefinition(
                name=field_meta.name,
                type=mermaid_type,
                constraints=[],  # Will be set in __post_init__
                is_primary_key=field_meta.is_primary_key,
                is_foreign_key=field_meta.is_foreign_key,
                is_nullable=field_meta.is_nullable,
                default_value=(
                    str(field_meta.default_value)
                    if field_meta.default_value is not None
                    else None
                ),
            )
            fields.append(field_def)

        return cls(
            name=model_metadata.table_name,
            fields=fields,
            description=f"Table for {model_metadata.class_name} model",
            metadata={
                "class_name": model_metadata.class_name,
                "file_path": str(model_metadata.file_path),
                "line_number": model_metadata.line_number,
            },
        )

    @staticmethod
    def _convert_type_to_mermaid(type_hint: str) -> str:
        """Convert Python type hint to Mermaid ERD type."""
        type_hint = type_hint.lower()

        # Common type mappings
        type_mappings = {
            "str": "string",
            "string": "string",
            "int": "int",
            "integer": "int",
            "float": "float",
            "bool": "boolean",
            "boolean": "boolean",
            "datetime": "datetime",
            "date": "date",
            "time": "time",
            "uuid": "uuid",
            "json": "json",
            "text": "text",
            "bytes": "bytes",
            "bytea": "bytes",
        }

        # Handle Optional types
        if "optional" in type_hint or "union" in type_hint:
            # Extract the inner type
            for key in type_mappings:
                if key in type_hint:
                    return type_mappings[key]

        # Handle List types
        if "list" in type_hint or "array" in type_hint:
            return "array"

        # Direct mapping
        for key, value in type_mappings.items():
            if key in type_hint:
                return value

        # Default fallback
        if "uuid" in type_hint:
            return "uuid"
        elif "datetime" in type_hint:
            return "datetime"
        elif "int" in type_hint:
            return "int"
        elif "str" in type_hint:
            return "string"
        else:
            return "string"  # Safe fallback
