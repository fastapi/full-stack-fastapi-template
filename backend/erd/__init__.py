"""
ERD Package - Entity Relationship Diagram generation from SQLModel definitions.

This package provides functionality to automatically generate Mermaid ERD diagrams
from SQLModel class definitions, including validation and output formatting.

Main Components:
- generator: Main ERD generation logic
- models: Data structures for model metadata
- validation: ERD validation and error checking
- discovery: SQLModel introspection and parsing
- output: ERD output formatting and file handling
- entities: Entity definition structures
- fields: Field definition structures
- relationships: Relationship definition and management
- mermaid_validator: Mermaid syntax validation

Usage:
    from erd import ERDGenerator
    
    generator = ERDGenerator()
    mermaid_code = generator.generate_erd()
"""

from .generator import ERDGenerator
from .models import (
    FieldMetadata,
    ModelMetadata, 
    RelationshipMetadata,
    ConstraintMetadata
)
from .validation import (
    ERDValidator,
    ValidationResult,
    ValidationError,
    ErrorSeverity,
    ValidationMode
)
from .output import ERDOutput
from .entities import EntityDefinition
from .relationships import RelationshipDefinition, RelationshipManager
from .discovery import ModelDiscovery
from .mermaid_validator import MermaidValidator

__version__ = "1.0.0"
__all__ = [
    "ERDGenerator",
    "FieldMetadata",
    "ModelMetadata", 
    "RelationshipMetadata",
    "ConstraintMetadata",
    "ERDValidator",
    "ValidationResult",
    "ValidationError",
    "ErrorSeverity",
    "ValidationMode",
    "ERDOutput",
    "EntityDefinition",
    "RelationshipDefinition",
    "RelationshipManager",
    "ModelDiscovery",
    "MermaidValidator",
]
