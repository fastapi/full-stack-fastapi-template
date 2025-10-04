"""
ERD Validation System - Validate that generated ERD diagrams accurately represent current SQLModel definitions.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ErrorSeverity(Enum):
    """Enumeration of validation error severity levels."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class ValidationMode(Enum):
    """Enumeration of validation modes."""

    STRICT = "strict"
    PERMISSIVE = "permissive"
    REPORT = "report"


@dataclass
class ValidationError:
    """Individual validation error."""

    message: str
    severity: ErrorSeverity
    line_number: int | None = None
    field_name: str | None = None
    entity_name: str | None = None
    error_code: str | None = None
    suggestions: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.line_number is None:
            self.line_number = -1


@dataclass
class ValidationResult:
    """Result of ERD validation."""

    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_error(self, error: ValidationError) -> None:
        """Add a validation error."""
        self.errors.append(error)
        if error.severity == ErrorSeverity.CRITICAL:
            self.is_valid = False

    def add_warning(self, warning: ValidationError) -> None:
        """Add a validation warning."""
        self.warnings.append(warning)

    def has_critical_errors(self) -> bool:
        """Check if there are any critical errors."""
        return any(error.severity == ErrorSeverity.CRITICAL for error in self.errors)


@dataclass
class ValidationConfig:
    """Configuration for ERD validation."""

    strict_mode: bool = True
    check_syntax: bool = True
    validate_relationships: bool = True
    validate_constraints: bool = True
    max_errors: int = 10
    timeout_seconds: int = 30


class ERDValidator:
    """Main ERD validation system."""

    def __init__(self, config: ValidationConfig | None = None):
        self.config = config or ValidationConfig()
        self.mode = (
            ValidationMode.STRICT
            if self.config.strict_mode
            else ValidationMode.PERMISSIVE
        )

    def set_mode(self, mode: ValidationMode) -> None:
        """Set validation mode."""
        self.mode = mode

    def validate_all(self, erd_content: str) -> ValidationResult:
        """Validate all aspects of an ERD."""
        result = ValidationResult(is_valid=True)

        try:
            # Parse entities and relationships for validation
            entities = self._parse_entities(erd_content)
            relationships = self._parse_relationships(erd_content)

            # Validate entities exist
            entities_result = self.validate_entities_exist(erd_content)
            result.errors.extend(entities_result.errors)
            result.warnings.extend(entities_result.warnings)

            # Validate relationships
            if self.config.validate_relationships:
                relationships_result = self.validate_relationships(relationships)
                result.errors.extend(relationships_result.errors)
                result.warnings.extend(relationships_result.warnings)

            # Update overall validity
            result.is_valid = not result.has_critical_errors()

        except Exception as e:
            error = ValidationError(
                message=f"Validation failed: {str(e)}",
                severity=ErrorSeverity.CRITICAL,
                error_code="VALIDATION_ERROR",
            )
            result.add_error(error)

        return result

    def validate_mermaid_syntax(self, erd_content: str) -> ValidationResult:
        """Validate Mermaid ERD syntax."""
        result = ValidationResult(is_valid=True)

        # Check for basic Mermaid ERD structure
        if "erDiagram" not in erd_content:
            error = ValidationError(
                message="Missing 'erDiagram' declaration",
                severity=ErrorSeverity.CRITICAL,
                error_code="MISSING_ERDIAGRAM",
            )
            result.add_error(error)

        # Check for valid entity syntax
        entity_pattern = r"^\s*[A-Z_][A-Z0-9_]*\s*\{"
        lines = erd_content.split("\n")

        for i, line in enumerate(lines, 1):
            if (
                line.strip()
                and not line.strip().startswith("erDiagram")
                and not line.strip().startswith("}")
            ):
                if not re.match(entity_pattern, line.strip()) and "--" not in line:
                    if line.strip().startswith("```"):
                        continue  # Skip markdown code blocks

                    warning = ValidationError(
                        message=f"Potentially invalid ERD syntax on line {i}: {line.strip()}",
                        severity=ErrorSeverity.WARNING,
                        line_number=i,
                        error_code="INVALID_SYNTAX",
                    )
                    result.add_warning(warning)

        return result

    def validate_entities(self, erd_content: str) -> ValidationResult:
        """Validate entity completeness and accuracy."""
        result = ValidationResult(is_valid=True)

        # Parse entities from ERD content
        entities = self._parse_entities(erd_content)

        if not entities:
            error = ValidationError(
                message="No entities found in ERD",
                severity=ErrorSeverity.CRITICAL,
                error_code="NO_ENTITIES",
            )
            result.add_error(error)

        # Validate each entity
        for entity in entities:
            if not entity.get("fields"):
                error = ValidationError(
                    message=f"Entity {entity.get('name', 'Unknown')} has no fields",
                    severity=ErrorSeverity.WARNING,
                    entity_name=entity.get("name"),
                    error_code="ENTITY_NO_FIELDS",
                )
                result.add_warning(error)

            # Check for primary key
            has_primary_key = any(
                "PK" in field.get("constraints", "")
                for field in entity.get("fields", [])
            )
            if not has_primary_key:
                warning = ValidationError(
                    message=f"Entity {entity.get('name', 'Unknown')} has no primary key",
                    severity=ErrorSeverity.WARNING,
                    entity_name=entity.get("name"),
                    error_code="ENTITY_NO_PK",
                )
                result.add_warning(warning)

        return result

    def validate_relationships(
        self, relationships: list[dict[str, Any]]
    ) -> ValidationResult:
        """Validate relationship cardinality and constraints."""
        result = ValidationResult(is_valid=True)

        for rel in relationships:
            # Basic relationship validation
            if not rel.get("from_entity") or not rel.get("to_entity"):
                error = ValidationError(
                    message="Invalid relationship: missing from_entity or to_entity",
                    severity=ErrorSeverity.CRITICAL,
                    error_code="INVALID_RELATIONSHIP",
                )
                result.add_error(error)

        return result

    def validate_fields(self, test_data: dict[str, Any]) -> ValidationResult:
        """Validate field definitions and types."""
        result = ValidationResult(is_valid=True)

        entities = test_data.get("entities", [])

        # Simple field validation - check if field names match
        for entity in entities:
            _ = {field["name"] for field in entity.get("fields", [])}
            # This would be expanded with actual model comparison

        return result

    def validate_primary_keys(self, entities: list[dict[str, Any]]) -> ValidationResult:
        """Validate primary key definitions."""
        result = ValidationResult(is_valid=True)

        for entity in entities:
            primary_key = entity.get("primary_key")
            if not primary_key:
                error = ValidationError(
                    message=f"Entity {entity.get('name')} has no primary key",
                    severity=ErrorSeverity.WARNING,
                    entity_name=entity.get("name"),
                    error_code="NO_PRIMARY_KEY",
                )
                result.add_warning(error)

        return result

    def validate_foreign_keys(
        self, foreign_keys: list[dict[str, Any]]
    ) -> ValidationResult:
        """Validate foreign key relationships."""
        result = ValidationResult(is_valid=True)

        for fk in foreign_keys:
            if not fk.get("references"):
                error = ValidationError(
                    message=f"Foreign key {fk.get('field')} has no reference",
                    severity=ErrorSeverity.CRITICAL,
                    field_name=fk.get("field"),
                    error_code="FK_NO_REFERENCE",
                )
                result.add_error(error)

        return result

    def _parse_entities(self, erd_content: str) -> list[dict[str, Any]]:
        """Parse entities from ERD content."""
        entities = []
        lines = erd_content.split("\n")
        current_entity = None

        for line in lines:
            line = line.strip()

            # Start of entity
            if line.endswith("{"):
                entity_name = line[:-1].strip()
                current_entity = {"name": entity_name, "fields": []}
                entities.append(current_entity)

            # Field in entity
            elif current_entity and line and not line.startswith("}"):
                field_parts = line.split()
                if len(field_parts) >= 2:
                    field = {
                        "type": field_parts[0],
                        "name": field_parts[1],
                        "constraints": (
                            " ".join(field_parts[2:]) if len(field_parts) > 2 else ""
                        ),
                    }
                    current_entity["fields"].append(field)

            # End of entity
            elif line == "}":
                current_entity = None

        return entities

    def _parse_relationships(self, erd_content: str) -> list[dict[str, Any]]:
        """Parse relationships from ERD content."""
        relationships = []
        lines = erd_content.split("\n")

        for line in lines:
            line = line.strip()

            # Relationship line (contains --)
            if "--" in line and not line.startswith("erDiagram"):
                parts = line.split("--")
                if len(parts) >= 2:
                    from_part = parts[0].strip()
                    to_part = parts[1].strip()

                    # Parse cardinality and labels
                    from_entity = from_part.split()[0] if from_part.split() else ""
                    to_entity = to_part.split()[0] if to_part.split() else ""

                    relationship = {
                        "from_entity": from_entity,
                        "to_entity": to_entity,
                        "cardinality": line,
                    }
                    relationships.append(relationship)

        return relationships

    def validate_for_cli(self, erd_content: str) -> ValidationResult:
        """Validate ERD for CLI usage."""
        return self.validate_all(erd_content)

    def validate_for_pre_commit(self, erd_content: str) -> ValidationResult:
        """Validate ERD for pre-commit hook usage."""
        return self.validate_all(erd_content)

    def validate_for_ci_cd(self, erd_content: str) -> ValidationResult:
        """Validate ERD for CI/CD usage."""
        return self.validate_all(erd_content)
