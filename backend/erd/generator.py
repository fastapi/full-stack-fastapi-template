"""
ERD Generator Module - Main entity responsible for generating Mermaid ERD diagrams from SQLModel definitions.
"""

from datetime import datetime
from pathlib import Path

from .entities import EntityDefinition
from .discovery import ModelDiscovery
from .models import FieldMetadata, ModelMetadata, RelationshipMetadata
from .output import ERDOutput
from .relationships import RelationshipDefinition, RelationshipManager
from .validation import ERDValidator
from .mermaid_validator import MermaidValidator


class ERDGenerator:
    """Main entity responsible for generating Mermaid ERD diagrams from SQLModel definitions."""

    def __init__(
        self,
        models_path: str = "app/models.py",
        output_path: str = "../docs/database/erd.mmd",
    ):
        self.models_path = models_path
        self.output_path = output_path
        self.mermaid_syntax = {}
        self.validation_rules = {}
        self.model_discovery = ModelDiscovery()
        self.generated_models: dict[str, ModelMetadata] = {}
        self.relationship_manager = RelationshipManager()
        self.validator = ERDValidator()
        self.mermaid_validator = MermaidValidator()

    def generate_erd(self) -> str:
        """Generate Mermaid ERD diagram from SQLModel definitions."""
        try:
            # Step 1: Discover and parse models
            self._discover_models()

            # Step 2: Extract metadata from models
            self._extract_model_metadata()

            # Step 3: Generate entities
            entities = self._generate_entities()

            # Step 4: Generate relationships
            relationships = self._generate_relationships()

            # Step 5: Generate Mermaid code
            mermaid_code = self._generate_mermaid_code(entities, relationships)

            # Step 6: Create ERD output
            erd_output = ERDOutput(
                mermaid_code=mermaid_code,
                entities=[entity.to_dict() for entity in entities],
                relationships=[rel.to_dict() for rel in relationships],
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "models_processed": len(self.generated_models),
                    "entities_count": len(entities),
                    "relationships_count": len(relationships),
                },
            )

            # Step 7: Validate the generated ERD
            validation_result = self.validator.validate_all(mermaid_code)
            
            # Step 8: Validate Mermaid syntax
            mermaid_validation = self.mermaid_validator.validate_complete(mermaid_code)
            validation_result.errors.extend(mermaid_validation.errors)
            validation_result.warnings.extend(mermaid_validation.warnings)
            if not mermaid_validation.is_valid:
                validation_result.is_valid = False

            # Update ERD output with validation results
            if validation_result.is_valid:
                erd_output.mark_as_valid()
            else:
                erd_output.mark_as_invalid()
                erd_output.metadata["validation_errors"] = [
                    {
                        "message": error.message,
                        "severity": error.severity.value,
                        "line_number": error.line_number,
                        "error_code": error.error_code,
                    }
                    for error in validation_result.errors
                ]
                erd_output.metadata["validation_warnings"] = [
                    {
                        "message": warning.message,
                        "severity": warning.severity.value,
                        "line_number": warning.line_number,
                        "error_code": warning.error_code,
                    }
                    for warning in validation_result.warnings
                ]

            # Step 9: Write output to file
            self._write_output(erd_output)

            return mermaid_code

        except Exception as e:
            error_msg = f"ERD generation failed: {str(e)}"
            # Create error output
            error_output = ERDOutput(
                mermaid_code="erDiagram\n    ERROR {\n        string message\n    }",
                entities=[],
                relationships=[],
                validation_status="error",
            )
            error_output.mark_as_error(error_msg)
            self._write_output(error_output)
            raise Exception(error_msg) from e

    def validate_models(self) -> bool:
        """Validate SQLModel definitions for ERD generation."""
        try:
            # Discover models first
            self._discover_models()

            # Extract metadata
            self._extract_model_metadata()

            # Basic validation checks
            if not self.generated_models:
                raise ValueError("No SQLModel classes found")

            validation_errors = []

            for model_name, model_metadata in self.generated_models.items():
                if not model_metadata.primary_key:
                    validation_errors.append(f"Model {model_name} has no primary key")

                if not model_metadata.fields:
                    validation_errors.append(f"Model {model_name} has no fields")

                # Validate field types and constraints
                for field in model_metadata.fields:
                    if not field.type_hint or field.type_hint == "Any":
                        validation_errors.append(f"Model {model_name}.{field.name} has no type hint")

            if validation_errors:
                print("Validation errors found:")
                for error in validation_errors:
                    print(f"  - {error}")
                return False

            return True

        except Exception as e:
            print(f"Validation failed: {e}")
            return False

    def _discover_models(self) -> None:
        """Discover SQLModel files and classes."""
        # Use the model discovery to find all model files
        model_files = self.model_discovery.discover_model_files(self.models_path)

        if not model_files:
            # Fallback to the specified models path
            models_path = Path(self.models_path)
            if models_path.exists():
                model_files = {models_path}
            else:
                raise FileNotFoundError(f"Models file not found: {self.models_path}")

        # Extract models from all discovered files
        for file_path in model_files:
            models = self.model_discovery.extract_model_classes(file_path)
            for model_info in models:
                self.generated_models[model_info["name"]] = model_info

    def _extract_model_metadata(self) -> None:
        """Extract detailed metadata from discovered models."""
        for model_name, model_info in self.generated_models.items():
            # Convert basic model info to ModelMetadata with enhanced introspection
            fields = []
            relationships = []
            constraints = []

            # Enhanced field extraction with type hints and constraints
            for field_name in model_info.get("fields", []):
                field_meta = self._create_field_metadata(model_info, field_name)
                
                # Skip relationship fields - they're not database columns
                if not self._is_relationship_field(field_meta, model_info):
                    fields.append(field_meta)

            # Extract relationships from the model
            relationships = self._extract_relationships(model_info)

            # Extract constraints (empty for now)
            constraints = []

            model_metadata = ModelMetadata(
                class_name=model_info["name"],
                table_name=model_info["name"].lower(),
                file_path=Path(model_info["file_path"]),
                line_number=model_info["line_number"],
                fields=fields,
                relationships=relationships,
                constraints=constraints,
            )

            self.generated_models[model_name] = model_metadata

    def _is_relationship_field(self, field_meta: FieldMetadata, model_info: dict) -> bool:
        """Check if a field is a relationship field (not a database column)."""
        # Check if this field is defined as a Relationship() in the model
        for rel_info in model_info.get("relationships", []):
            if rel_info["field_name"] == field_meta.name:
                return True
        
        # Check field type for relationship indicators
        field_type = field_meta.type_hint.lower()
        
        # List types are usually relationships (e.g., list["Item"])
        if "list[" in field_type or "List[" in field_type:
            return True
        
        # Union types with None might be relationships (e.g., User | None)
        if "| None" in field_type and not field_meta.is_foreign_key:
            return True
        
        return False

    def _is_bidirectional_relationship(self, rel_meta: RelationshipMetadata, target_model: ModelMetadata) -> bool:
        """Check if a relationship is bidirectional (has back_populates)."""
        # Check if this relationship has back_populates
        if not rel_meta.back_populates:
            return False
        
        # Check if the target model has a corresponding relationship with back_populates pointing back
        for target_rel in target_model.relationships:
            # The target relationship should have back_populates pointing to our field_name
            # and should point to our source model
            if (target_rel.back_populates == rel_meta.field_name):
                return True
        
        return False

    def _generate_entities(self) -> list[EntityDefinition]:
        """Generate entity definitions from model metadata."""
        entities = []

        for _model_name, model_metadata in self.generated_models.items():
            entity = EntityDefinition.from_model_metadata(model_metadata)
            entities.append(entity)

        return entities

    def _generate_relationships(self) -> list[RelationshipDefinition]:
        """Generate relationship definitions, avoiding redundant bidirectional relationships."""
        relationships = []
        processed_pairs = set()  # Track which entity pairs we've already handled

        # Generate relationships from relationship metadata
        for model_name, model_metadata in self.generated_models.items():
            for rel_meta in model_metadata.relationships:
                # Find target model
                target_model_name = rel_meta.target_model
                if target_model_name in self.generated_models:
                    target_model = self.generated_models[target_model_name]
                    
                    # Create relationship key for bidirectional detection
                    pair_key = tuple(sorted([model_name, target_model_name]))
                    
                    if pair_key not in processed_pairs:
                        # Check if this is bidirectional
                        if self._is_bidirectional_relationship(rel_meta, target_model):
                            # Always prefer the one-to-many direction
                            if rel_meta.relationship_type == "one-to-many":
                                relationship = RelationshipDefinition.from_model_relationship(
                                    rel_meta, model_metadata, target_model
                                )
                                relationships.append(relationship)
                                processed_pairs.add(pair_key)
                        else:
                            # Non-bidirectional, render normally
                            relationship = RelationshipDefinition.from_model_relationship(
                                rel_meta, model_metadata, target_model
                            )
                            relationships.append(relationship)

        # Also generate relationships from foreign key fields (fallback)
        for _model_name, model_metadata in self.generated_models.items():
            for field in model_metadata.foreign_key_fields:
                # Find target model (simple heuristic)
                target_model_name = self._find_target_model(field.name)
                if target_model_name and target_model_name in self.generated_models:
                    target_model = self.generated_models[target_model_name]
                    
                    # Create relationship key for bidirectional detection
                    pair_key = tuple(sorted([_model_name, target_model_name]))
                    
                    if pair_key not in processed_pairs:
                        relationship = RelationshipDefinition.from_foreign_key(
                            model_metadata, target_model, field
                        )
                        relationships.append(relationship)
                        processed_pairs.add(pair_key)

        return relationships

    def _find_target_model(self, field_name: str) -> str | None:
        """Find target model for a foreign key field."""
        # Simple heuristic: remove _id suffix and capitalize
        if field_name.endswith("_id"):
            model_name = field_name[:-3].title()
            return model_name
        return None

    def _generate_mermaid_code(
        self,
        entities: list[EntityDefinition],
        relationships: list[RelationshipDefinition],
    ) -> str:
        """Generate Mermaid ERD code from entities and relationships."""
        lines = ["erDiagram"]

        # Add entities
        for entity in entities:
            lines.append("")
            lines.append(entity.to_mermaid_entity())

        # Add relationships
        if relationships:
            lines.append("")
            for relationship in relationships:
                lines.append(relationship.to_mermaid_relationship())

        return "\n".join(lines)

    def _write_output(self, erd_output: ERDOutput) -> None:
        """Write ERD output to file."""
        output_path = Path(self.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        mermaid_content = erd_output.to_mermaid_format()
        output_path.write_text(mermaid_content, encoding="utf-8")

    def _create_field_metadata(self, model_info: dict, field_name: str) -> FieldMetadata:
        """Create enhanced field metadata with type hints and constraints."""
        # Parse the actual model file to get detailed field information
        file_path = Path(model_info["file_path"])
        field_meta = self._parse_field_from_source(file_path, model_info["name"], field_name)

        # If parsing failed, use basic heuristics
        if not field_meta:
            field_meta = FieldMetadata(
                name=field_name,
                type_hint=self._infer_field_type(field_name),
                is_primary_key=field_name == "id",
                is_foreign_key=field_name.endswith("_id"),
                is_nullable=True,
            )

        return field_meta

    def _parse_field_from_source(self, file_path: Path, class_name: str, field_name: str) -> FieldMetadata | None:
        """Parse field information from the source file using AST."""
        try:
            import ast

            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            if item.target.id == field_name:
                                # Extract type hint
                                type_hint = ast.unparse(item.annotation) if item.annotation else "Any"

                                # Check for Field() call
                                is_primary_key = False
                                is_foreign_key = False
                                is_nullable = True
                                foreign_key_ref = None

                                if isinstance(item.value, ast.Call):
                                    # Parse Field() arguments
                                    for keyword in item.value.keywords:
                                        if keyword.arg == "primary_key" and isinstance(keyword.value, ast.Constant):
                                            is_primary_key = keyword.value.value
                                        elif keyword.arg == "foreign_key" and isinstance(keyword.value, ast.Constant):
                                            foreign_key_ref = keyword.value.value
                                            is_foreign_key = True
                                        elif keyword.arg == "nullable" and isinstance(keyword.value, ast.Constant):
                                            is_nullable = keyword.value.value

                                return FieldMetadata(
                                    name=field_name,
                                    type_hint=type_hint,
                                    is_primary_key=is_primary_key,
                                    is_foreign_key=is_foreign_key,
                                    is_nullable=is_nullable,
                                    foreign_key_reference=foreign_key_ref,
                                )
        except Exception:
            pass

        return None

    def _infer_field_type(self, field_name: str) -> str:
        """Infer field type from field name."""
        if field_name == "id":
            return "UUID"
        elif field_name.endswith("_id"):
            return "UUID"
        elif field_name in ["email", "name", "title", "description"]:
            return "str"
        elif field_name in ["created_at", "updated_at", "timestamp"]:
            return "datetime"
        elif field_name in ["is_active", "is_superuser", "enabled"]:
            return "bool"
        else:
            return "str"

    def _extract_relationships(self, model_info: dict) -> list[RelationshipMetadata]:
        """Extract relationships from model info."""
        relationships = []
        
        # Extract relationships from the discovered relationship data
        for rel_info in model_info.get("relationships", []):
            rel_meta = RelationshipMetadata(
                field_name=rel_info["field_name"],
                target_model=rel_info["target_model"],
                relationship_type=rel_info["relationship_type"],
                back_populates=rel_info.get("back_populates"),
                cascade=rel_info.get("cascade_delete", False),
            )
            relationships.append(rel_meta)
        
        # Also extract foreign key relationships from field names (fallback)
        for field_name in model_info.get("fields", []):
            if field_name.endswith("_id") and field_name != "id":
                # Check if we already have a relationship for this field
                existing_rel = any(
                    rel.field_name == field_name or rel.foreign_key_field == field_name
                    for rel in relationships
                )
                
                if not existing_rel:
                    # This looks like a foreign key relationship
                    target_model = field_name[:-3].title()  # Remove _id and capitalize
                    rel_meta = RelationshipMetadata(
                        field_name=field_name,
                        target_model=target_model,
                        relationship_type="many-to-one",
                        foreign_key_field=field_name,
                    )
                    relationships.append(rel_meta)
        
        return relationships

