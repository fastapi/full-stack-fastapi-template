"""
Field Definition entity for detailed field information in ERD.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FieldType(Enum):
    """Enumeration of supported field types."""

    STRING = "string"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    UUID = "uuid"
    JSON = "json"
    TEXT = "text"
    BYTES = "bytes"
    ARRAY = "array"
    ENUM = "enum"


class ConstraintType(Enum):
    """Enumeration of constraint types."""

    PRIMARY_KEY = "PK"
    FOREIGN_KEY = "FK"
    NOT_NULL = "NOT NULL"
    UNIQUE = "UNIQUE"
    CHECK = "CHECK"
    DEFAULT = "DEFAULT"


@dataclass
class Constraint:
    """Database constraint definition."""

    type: ConstraintType
    value: str | None = None
    referenced_table: str | None = None
    referenced_column: str | None = None

    def to_string(self) -> str:
        """Convert constraint to string representation."""
        if self.type == ConstraintType.DEFAULT and self.value:
            return f"DEFAULT {self.value}"
        elif self.type == ConstraintType.CHECK and self.value:
            return f"CHECK {self.value}"
        elif self.type == ConstraintType.FOREIGN_KEY and self.referenced_table:
            ref = f"{self.referenced_table}"
            if self.referenced_column:
                ref += f".{self.referenced_column}"
            return f"FK -> {ref}"
        else:
            return self.type.value


@dataclass
class FieldDefinition:
    """Detailed field definition for ERD generation."""

    name: str
    type: FieldType
    constraints: list[Constraint] = field(default_factory=list)
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_nullable: bool = True
    is_unique: bool = False
    default_value: str | int | float | bool | None = None
    max_length: int | None = None
    precision: int | None = None
    scale: int | None = None
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize constraints based on field properties."""
        if self.is_primary_key:
            self.constraints.append(Constraint(ConstraintType.PRIMARY_KEY))
        if self.is_foreign_key:
            self.constraints.append(Constraint(ConstraintType.FOREIGN_KEY))
        if not self.is_nullable:
            self.constraints.append(Constraint(ConstraintType.NOT_NULL))
        if self.is_unique:
            self.constraints.append(Constraint(ConstraintType.UNIQUE))
        if self.default_value is not None:
            self.constraints.append(
                Constraint(ConstraintType.DEFAULT, str(self.default_value))
            )

    @property
    def mermaid_type(self) -> str:
        """Get the Mermaid ERD type representation."""
        type_str = self.type.value

        # Add size information for string types
        if self.type == FieldType.STRING and self.max_length:
            type_str = f"{type_str}({self.max_length})"

        # Add precision/scale for numeric types
        if self.type in [FieldType.FLOAT] and self.precision:
            if self.scale:
                type_str = f"{type_str}({self.precision},{self.scale})"
            else:
                type_str = f"{type_str}({self.precision})"

        return type_str

    @property
    def constraint_strings(self) -> list[str]:
        """Get list of constraint strings."""
        return [constraint.to_string() for constraint in self.constraints]

    def to_mermaid_field(self) -> str:
        """Convert field to Mermaid ERD field syntax."""
        field_parts = [self.mermaid_type, self.name]

        if self.constraints:
            constraint_str = " ".join(self.constraint_strings)
            field_parts.append(constraint_str)

        return " ".join(field_parts)

    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the field."""
        self.constraints.append(constraint)

    def remove_constraint(self, constraint_type: ConstraintType) -> None:
        """Remove constraints of a specific type."""
        self.constraints = [c for c in self.constraints if c.type != constraint_type]

    def has_constraint(self, constraint_type: ConstraintType) -> bool:
        """Check if field has a specific constraint type."""
        return any(c.type == constraint_type for c in self.constraints)

    def set_foreign_key_reference(
        self, referenced_table: str, referenced_column: str = None
    ) -> None:
        """Set foreign key reference information."""
        # Remove existing FK constraint
        self.remove_constraint(ConstraintType.FOREIGN_KEY)

        # Add new FK constraint with reference
        fk_constraint = Constraint(
            ConstraintType.FOREIGN_KEY,
            referenced_table=referenced_table,
            referenced_column=referenced_column,
        )
        self.constraints.append(fk_constraint)
        self.is_foreign_key = True

    def to_dict(self) -> dict[str, Any]:
        """Convert field definition to dictionary."""
        return {
            "name": self.name,
            "type": self.type.value,
            "constraints": [c.to_string() for c in self.constraints],
            "is_primary_key": self.is_primary_key,
            "is_foreign_key": self.is_foreign_key,
            "is_nullable": self.is_nullable,
            "is_unique": self.is_unique,
            "default_value": self.default_value,
            "max_length": self.max_length,
            "precision": self.precision,
            "scale": self.scale,
            "description": self.description,
            "metadata": self.metadata,
        }

    @classmethod
    def from_model_field(cls, field_metadata) -> "FieldDefinition":
        """Create FieldDefinition from ModelMetadata field."""
        # Convert type hint to FieldType
        field_type = cls._convert_type_to_field_type(field_metadata.type_hint)

        # Create field definition
        field_def = cls(
            name=field_metadata.name,
            type=field_type,
            is_primary_key=field_metadata.is_primary_key,
            is_foreign_key=field_metadata.is_foreign_key,
            is_nullable=field_metadata.is_nullable,
            default_value=field_metadata.default_value,
        )

        # Set foreign key reference if available
        if field_metadata.foreign_key_reference:
            parts = field_metadata.foreign_key_reference.split(".")
            if len(parts) >= 2:
                field_def.set_foreign_key_reference(parts[0], parts[1])
            else:
                field_def.set_foreign_key_reference(parts[0])

        return field_def

    @staticmethod
    def _convert_type_to_field_type(type_hint: str) -> FieldType:
        """Convert Python type hint to FieldType enum."""
        type_hint = type_hint.lower()

        # Handle Optional and Union types
        if "optional" in type_hint or "union" in type_hint:
            # Extract the inner type
            for field_type in FieldType:
                if field_type.value in type_hint:
                    return field_type

        # Handle List types
        if "list" in type_hint or "array" in type_hint:
            return FieldType.ARRAY

        # Direct mappings
        type_mappings = {
            "str": FieldType.STRING,
            "string": FieldType.STRING,
            "int": FieldType.INTEGER,
            "integer": FieldType.INTEGER,
            "float": FieldType.FLOAT,
            "bool": FieldType.BOOLEAN,
            "boolean": FieldType.BOOLEAN,
            "datetime": FieldType.DATETIME,
            "date": FieldType.DATE,
            "time": FieldType.TIME,
            "uuid": FieldType.UUID,
            "json": FieldType.JSON,
            "text": FieldType.TEXT,
            "bytes": FieldType.BYTES,
            "bytea": FieldType.BYTES,
        }

        for key, value in type_mappings.items():
            if key in type_hint:
                return value

        # Default fallback
        return FieldType.STRING
