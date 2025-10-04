"""
Relationship Definition entity for relationships between entities in ERD.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RelationshipType(Enum):
    """Enumeration of relationship types."""

    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_ONE = "N:1"
    MANY_TO_MANY = "N:N"


class Cardinality(Enum):
    """Enumeration of cardinality symbols for Mermaid ERD."""

    ONE = "||"
    ZERO_OR_ONE = "|o"
    ZERO_OR_MORE = "}o"
    ONE_OR_MORE = "}|"


@dataclass
class RelationshipDefinition:
    """Definition of relationships between entities in ERD."""

    from_entity: str
    to_entity: str
    relationship_type: RelationshipType
    from_cardinality: Cardinality
    to_cardinality: Cardinality
    label: str | None = None
    foreign_key_field: str | None = None
    foreign_key_target_field: str | None = None
    cascade_delete: bool = False
    cascade_update: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure entity names are uppercase."""
        self.from_entity = self.from_entity.upper()
        self.to_entity = self.to_entity.upper()

        # Generate label if not provided
        if not self.label:
            self.label = f"{self.from_entity} -> {self.to_entity}"

    @property
    def mermaid_cardinality(self) -> str:
        """Get Mermaid cardinality representation."""
        return f"{self.from_cardinality.value}--{self.to_cardinality.value}"

    def to_mermaid_relationship(self) -> str:
        """Convert relationship to Mermaid ERD relationship syntax."""
        # Build relationship line with proper cardinality symbols
        cardinality_map = {
            Cardinality.ONE: "||",
            Cardinality.ZERO_OR_ONE: "|o", 
            Cardinality.ZERO_OR_MORE: "o{",
            Cardinality.ONE_OR_MORE: "}|",
        }
        
        from_symbol = cardinality_map.get(self.from_cardinality, "||")
        to_symbol = cardinality_map.get(self.to_cardinality, "||")
        
        # Create relationship line
        relationship_line = f"{self.from_entity} {from_symbol}--{to_symbol} {self.to_entity}"
        
        # Add label if present
        if self.label:
            relationship_line += f" : {self.label}"
        
        return relationship_line

    def is_bidirectional(self) -> bool:
        """Check if this is a bidirectional relationship."""
        # Check if there's a corresponding reverse relationship
        # This would be determined by the metadata or by analyzing the model
        return self.metadata.get("is_bidirectional", False)

    def get_foreign_key_info(self) -> dict[str, str]:
        """Get foreign key information."""
        return {
            "field": self.foreign_key_field or "",
            "target_field": self.foreign_key_target_field or "",
            "target_table": self.to_entity,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert relationship definition to dictionary."""
        return {
            "from_entity": self.from_entity,
            "to_entity": self.to_entity,
            "relationship_type": self.relationship_type.value,
            "from_cardinality": self.from_cardinality.value,
            "to_cardinality": self.to_cardinality.value,
            "label": self.label,
            "foreign_key_field": self.foreign_key_field,
            "foreign_key_target_field": self.foreign_key_target_field,
            "cascade_delete": self.cascade_delete,
            "cascade_update": self.cascade_update,
            "metadata": self.metadata,
        }

    @classmethod
    def from_model_relationship(
        cls, relationship_metadata, from_model, to_model
    ) -> "RelationshipDefinition":
        """Create RelationshipDefinition from ModelMetadata relationship."""

        # Determine relationship type based on metadata
        rel_type_str = relationship_metadata.relationship_type.lower()

        if rel_type_str == "one-to-one":
            relationship_type = RelationshipType.ONE_TO_ONE
            from_cardinality = Cardinality.ONE
            to_cardinality = Cardinality.ONE
        elif rel_type_str == "one-to-many":
            relationship_type = RelationshipType.ONE_TO_MANY
            from_cardinality = Cardinality.ONE
            to_cardinality = Cardinality.ZERO_OR_MORE
        elif rel_type_str == "many-to-one":
            relationship_type = RelationshipType.MANY_TO_ONE
            from_cardinality = Cardinality.ZERO_OR_MORE
            to_cardinality = Cardinality.ONE
        elif rel_type_str == "many-to-many":
            relationship_type = RelationshipType.MANY_TO_MANY
            from_cardinality = Cardinality.ZERO_OR_MORE
            to_cardinality = Cardinality.ZERO_OR_MORE
        else:
            # Default to one-to-many
            relationship_type = RelationshipType.ONE_TO_MANY
            from_cardinality = Cardinality.ONE
            to_cardinality = Cardinality.ZERO_OR_MORE

        # Create a simple label (just the field name)
        label = relationship_metadata.field_name

        return cls(
            from_entity=from_model.table_name,
            to_entity=to_model.table_name,
            relationship_type=relationship_type,
            from_cardinality=from_cardinality,
            to_cardinality=to_cardinality,
            label=label,
            foreign_key_field=relationship_metadata.foreign_key_field,
            cascade_delete=relationship_metadata.cascade,
            metadata={
                "field_name": relationship_metadata.field_name,
                "target_model": relationship_metadata.target_model,
                "back_populates": relationship_metadata.back_populates,
                "cascade": relationship_metadata.cascade,
                "is_bidirectional": relationship_metadata.back_populates is not None,
            },
        )

    @classmethod
    def from_foreign_key(
        cls, from_model, to_model, foreign_key_field
    ) -> "RelationshipDefinition":
        """Create RelationshipDefinition from foreign key relationship."""

        # This is typically a many-to-one relationship
        relationship_type = RelationshipType.MANY_TO_ONE
        from_cardinality = Cardinality.ZERO_OR_MORE
        to_cardinality = Cardinality.ONE

        return cls(
            from_entity=from_model.table_name,
            to_entity=to_model.table_name,
            relationship_type=relationship_type,
            from_cardinality=from_cardinality,
            to_cardinality=to_cardinality,
            label=foreign_key_field.name,
            foreign_key_field=foreign_key_field.name,
            foreign_key_target_field=to_model.primary_key,
            metadata={
                "inferred_from_fk": True,
                "field_name": foreign_key_field.name,
            },
        )


@dataclass
class RelationshipManager:
    """Manager for handling relationships between entities."""

    relationships: list[RelationshipDefinition] = field(default_factory=list)

    def add_relationship(self, relationship: RelationshipDefinition) -> None:
        """Add a relationship to the manager."""
        self.relationships.append(relationship)

    def get_relationships_for_entity(
        self, entity_name: str
    ) -> list[RelationshipDefinition]:
        """Get all relationships involving a specific entity."""
        entity_name = entity_name.upper()
        return [
            rel
            for rel in self.relationships
            if rel.from_entity == entity_name or rel.to_entity == entity_name
        ]

    def get_outgoing_relationships(
        self, entity_name: str
    ) -> list[RelationshipDefinition]:
        """Get relationships where the entity is the source."""
        entity_name = entity_name.upper()
        return [rel for rel in self.relationships if rel.from_entity == entity_name]

    def get_incoming_relationships(
        self, entity_name: str
    ) -> list[RelationshipDefinition]:
        """Get relationships where the entity is the target."""
        entity_name = entity_name.upper()
        return [rel for rel in self.relationships if rel.to_entity == entity_name]

    def has_relationship(self, from_entity: str, to_entity: str) -> bool:
        """Check if there's a relationship between two entities."""
        from_entity = from_entity.upper()
        to_entity = to_entity.upper()
        return any(
            (rel.from_entity == from_entity and rel.to_entity == to_entity)
            or (rel.from_entity == to_entity and rel.to_entity == from_entity)
            for rel in self.relationships
        )

    def to_mermaid_relationships(self) -> list[str]:
        """Convert all relationships to Mermaid ERD syntax."""
        return [rel.to_mermaid_relationship() for rel in self.relationships]

    def to_dict(self) -> dict[str, Any]:
        """Convert relationship manager to dictionary."""
        return {
            "relationships": [rel.to_dict() for rel in self.relationships],
        }
