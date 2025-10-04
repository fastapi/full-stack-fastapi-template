"""
ERD Output entity for generated Mermaid ERD diagram structure.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ERDOutput:
    """Generated Mermaid ERD diagram structure."""

    mermaid_code: str
    entities: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)
    validation_status: str = "pending"  # "pending", "valid", "invalid", "error"
    generation_timestamp: datetime | None = None
    version: str = "1.0"

    def __post_init__(self):
        if self.generation_timestamp is None:
            self.generation_timestamp = datetime.now()

        # Initialize metadata if empty
        if not self.metadata:
            self.metadata = {
                "generated_at": self.generation_timestamp.isoformat(),
                "version": self.version,
                "entity_count": len(self.entities),
                "relationship_count": len(self.relationships),
            }

    @property
    def is_valid(self) -> bool:
        """Check if the ERD output is valid."""
        return self.validation_status == "valid"

    @property
    def has_errors(self) -> bool:
        """Check if the ERD output has errors."""
        return self.validation_status in ["invalid", "error"]

    def mark_as_valid(self) -> None:
        """Mark the ERD output as valid."""
        self.validation_status = "valid"

    def mark_as_invalid(self, reason: str = None) -> None:
        """Mark the ERD output as invalid."""
        self.validation_status = "invalid"
        if reason:
            self.metadata["validation_error"] = reason

    def mark_as_error(self, error_message: str) -> None:
        """Mark the ERD output as having an error."""
        self.validation_status = "error"
        self.metadata["error_message"] = error_message

    def add_entity(self, entity: dict[str, Any]) -> None:
        """Add an entity to the ERD output."""
        self.entities.append(entity)
        self.metadata["entity_count"] = len(self.entities)

    def add_relationship(self, relationship: dict[str, Any]) -> None:
        """Add a relationship to the ERD output."""
        self.relationships.append(relationship)
        self.metadata["relationship_count"] = len(self.relationships)

    def get_entity_by_name(self, entity_name: str) -> dict[str, Any] | None:
        """Get an entity by its name."""
        for entity in self.entities:
            if entity.get("name") == entity_name:
                return entity
        return None

    def get_relationships_for_entity(self, entity_name: str) -> list[dict[str, Any]]:
        """Get all relationships involving a specific entity."""
        relationships = []
        for rel in self.relationships:
            if (
                rel.get("from_entity") == entity_name
                or rel.get("to_entity") == entity_name
            ):
                relationships.append(rel)
        return relationships

    def to_markdown(self, include_metadata: bool = True) -> str:
        """Convert ERD output to Markdown format."""
        lines = ["# Database ERD Diagram", ""]

        if include_metadata:
            lines.extend(
                [
                    "## Metadata",
                    f"- **Generated**: {self.metadata.get('generated_at', 'Unknown')}",
                    f"- **Version**: {self.metadata.get('version', 'Unknown')}",
                    f"- **Entities**: {self.metadata.get('entity_count', 0)}",
                    f"- **Relationships**: {self.metadata.get('relationship_count', 0)}",
                    f"- **Status**: {self.validation_status}",
                    "",
                ]
            )

        lines.extend(
            [
                "## Entity Relationship Diagram",
                "",
                "```mermaid",
                self.mermaid_code,
                "```",
                "",
                "*This diagram is automatically generated from SQLModel definitions*",
            ]
        )

        if self.has_errors and "error_message" in self.metadata:
            lines.extend(
                [
                    "",
                    "## Errors",
                    "",
                    f"⚠️ **Error**: {self.metadata['error_message']}",
                ]
            )

        return "\n".join(lines)

    def to_mermaid_format(self, include_metadata: bool = True) -> str:
        """Convert ERD output to pure Mermaid format with metadata as comments."""
        lines = []
        
        if include_metadata:
               lines.extend([
                   "%% Database ERD Diagram",
                   f"%% Generated: {self.metadata.get('generated_at', 'Unknown')}",
                   f"%% Version: {self.metadata.get('version', 'Unknown')}",
                   f"%% Entities: {len(self.entities)}",
                   f"%% Relationships: {len(self.relationships)}",
                   f"%% Status: {self.validation_status}",
                   ""
               ])
            
               if self.has_errors and "error_message" in self.metadata:
                   lines.extend([
                       f"%% Error: {self.metadata['error_message']}",
                       ""
                   ])
               
               lines.extend([
                   "%% This diagram is automatically generated from SQLModel definitions",
                   ""
               ])
        
        # Add the actual Mermaid diagram
        lines.append(self.mermaid_code)
        
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert ERD output to dictionary for serialization."""
        return {
            "mermaid_code": self.mermaid_code,
            "entities": self.entities,
            "relationships": self.relationships,
            "metadata": self.metadata,
            "validation_status": self.validation_status,
            "generation_timestamp": (
                self.generation_timestamp.isoformat()
                if self.generation_timestamp
                else None
            ),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ERDOutput":
        """Create ERDOutput from dictionary."""
        timestamp = None
        if data.get("generation_timestamp"):
            timestamp = datetime.fromisoformat(data["generation_timestamp"])

        return cls(
            mermaid_code=data["mermaid_code"],
            entities=data["entities"],
            relationships=data["relationships"],
            metadata=data.get("metadata", {}),
            validation_status=data.get("validation_status", "pending"),
            generation_timestamp=timestamp,
            version=data.get("version", "1.0"),
        )
