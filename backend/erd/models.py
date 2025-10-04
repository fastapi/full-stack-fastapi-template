"""
Model Metadata entity for ERD generation.
Extracted metadata from SQLModel classes for ERD generation.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FieldMetadata:
    """Metadata for a single field in a SQLModel."""

    name: str
    type_hint: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_nullable: bool = True
    default_value: Any | None = None
    constraints: list[str] = None
    foreign_key_reference: str | None = None

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []


@dataclass
class RelationshipMetadata:
    """Metadata for relationships between SQLModel classes."""

    field_name: str
    target_model: str
    relationship_type: str  # "one-to-one", "one-to-many", "many-to-many"
    foreign_key_field: str | None = None
    back_populates: str | None = None
    cascade: str | None = None


@dataclass
class ConstraintMetadata:
    """Metadata for database constraints."""

    name: str
    type: str  # "primary_key", "foreign_key", "unique", "check"
    fields: list[str]
    target_table: str | None = None
    target_fields: list[str] | None = None


@dataclass
class ModelMetadata:
    """Extracted metadata from SQLModel classes for ERD generation."""

    class_name: str
    table_name: str
    file_path: Path
    line_number: int
    fields: list[FieldMetadata]
    relationships: list[RelationshipMetadata]
    constraints: list[ConstraintMetadata]
    primary_key: str | None = None
    imports: list[str] = None

    def __post_init__(self):
        if self.imports is None:
            self.imports = []

        # Auto-detect primary key from fields
        if not self.primary_key:
            for field in self.fields:
                if field.is_primary_key:
                    self.primary_key = field.name
                    break

    @property
    def has_foreign_keys(self) -> bool:
        """Check if this model has any foreign key relationships."""
        return any(field.is_foreign_key for field in self.fields)

    @property
    def foreign_key_fields(self) -> list[FieldMetadata]:
        """Get all foreign key fields in this model."""
        return [field for field in self.fields if field.is_foreign_key]

    @property
    def entity_name(self) -> str:
        """Get the entity name for ERD (uppercase table name)."""
        return self.table_name.upper()

    def get_field_by_name(self, field_name: str) -> FieldMetadata | None:
        """Get a field by its name."""
        for field in self.fields:
            if field.name == field_name:
                return field
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert model metadata to dictionary for serialization."""
        return {
            "class_name": self.class_name,
            "table_name": self.table_name,
            "file_path": str(self.file_path),
            "line_number": self.line_number,
            "fields": [
                {
                    "name": f.name,
                    "type_hint": f.type_hint,
                    "is_primary_key": f.is_primary_key,
                    "is_foreign_key": f.is_foreign_key,
                    "is_nullable": f.is_nullable,
                    "default_value": (
                        str(f.default_value) if f.default_value is not None else None
                    ),
                    "constraints": f.constraints,
                    "foreign_key_reference": f.foreign_key_reference,
                }
                for f in self.fields
            ],
            "relationships": [
                {
                    "field_name": r.field_name,
                    "target_model": r.target_model,
                    "relationship_type": r.relationship_type,
                    "foreign_key_field": r.foreign_key_field,
                    "back_populates": r.back_populates,
                    "cascade": r.cascade,
                }
                for r in self.relationships
            ],
            "constraints": [
                {
                    "name": c.name,
                    "type": c.type,
                    "fields": c.fields,
                    "target_table": c.target_table,
                    "target_fields": c.target_fields,
                }
                for c in self.constraints
            ],
            "primary_key": self.primary_key,
            "imports": self.imports,
        }
